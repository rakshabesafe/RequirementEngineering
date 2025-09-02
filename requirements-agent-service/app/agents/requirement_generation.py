import logging
import requests
import uuid
from typing import TypedDict, List, Dict, Any
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama

from langgraph.graph import StateGraph, END, ConditionalEdge

from ..vector_store import vector_store_manager
from ..config import settings

logger = logging.getLogger(__name__)

#--------------------------------------------------------------------------
# 1. Define the State for the Graph
#--------------------------------------------------------------------------
class GraphState(TypedDict):
    project_id: int
    jira_project_key: str
    initial_prompt: str
    retrieved_docs: List[str]
    generated_stories: List[Dict[str, Any]]
    jira_results: List[Dict[str, Any]]
    error: str | None

#--------------------------------------------------------------------------
# 2. Define Pydantic Models for LLM Output (Function Calling)
#--------------------------------------------------------------------------
class UserStory(BaseModel):
    """A single, well-defined user story with a title, description, and acceptance criteria."""
    title: str = Field(..., description="A short, descriptive title for the user story.")
    description: str = Field(..., description="The user story, following the 'As a [user], I want [feature], so that [benefit]' format.")
    acceptance_criteria: List[str] = Field(..., description="A list of conditions that must be met for the story to be considered complete.")

class UserStoryList(BaseModel):
    """A list of user stories generated from the provided context."""
    stories: List[UserStory]

#--------------------------------------------------------------------------
# 3. Define the Nodes of the Graph
#--------------------------------------------------------------------------

def retrieve_documents_node(state: GraphState) -> GraphState:
    """
    Retrieves relevant document chunks from the vector store based on the initial prompt.
    """
    logger.info("Node: retrieve_documents")
    try:
        documents = vector_store_manager.search(
            project_id=state['project_id'],
            query=state['initial_prompt'],
            limit=5  # Retrieve top 5 most relevant chunks
        )
        retrieved_docs_content = [doc.page_content for doc in documents]
        return {"retrieved_docs": retrieved_docs_content, "error": None}
    except Exception as e:
        logger.error(f"Error in retrieve_documents_node: {e}")
        return {"error": f"Failed to retrieve documents: {e}"}

def generate_user_stories_node(state: GraphState) -> GraphState:
    """
    Uses a configured LLM (OpenAI or Ollama) to generate user stories
    based on the retrieved documents.
    """
    logger.info("Node: generate_user_stories")
    if state.get("error"): return {}

    context_str = "\n\n".join(state['retrieved_docs'])

    try:
        if settings.LLM_PROVIDER == "ollama":
            logger.info("Using Ollama to generate user stories.")
            # Setup for Ollama with JSON output
            parser = JsonOutputParser(pydantic_object=UserStoryList)
            prompt = ChatPromptTemplate.from_template(
                "You are an expert agile business analyst. Based on the provided context, generate a list of user stories.\n"
                "CONTEXT:\n{context}\n\nPROMPT: {prompt}\n\n"
                "Format your response as a JSON object that strictly adheres to the following JSON schema:\n"
                "```json\n{format_instructions}\n```"
            )
            llm = ChatOllama(
                base_url=settings.OLLAMA_BASE_URL,
                model=settings.OLLAMA_MODEL_NAME,
                temperature=0,
                format="json"  # Enable JSON mode in Ollama
            )
            chain = prompt | llm | parser
            result_dict = chain.invoke({
                "context": context_str,
                "prompt": state['initial_prompt'],
                "format_instructions": parser.get_format_instructions()
            })
            generated_stories = result_dict.get('stories', [])

        else: # Default to OpenAI
            logger.info("Using OpenAI to generate user stories.")
            # Setup for OpenAI with structured output (function calling)
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert agile business analyst. Your task is to analyze the provided technical documentation and generate a list of clear, concise, and actionable user stories. Use the provided function `UserStoryList` to structure your output."),
                ("user", "Based on the following context, please generate the user stories:\n\nCONTEXT:\n---\n{context}\n\n---\nPROMPT: {prompt}")
            ])
            llm = ChatOpenAI(model=settings.OPENAI_MODEL_NAME, temperature=0, api_key=settings.OPENAI_API_KEY)
            structured_llm = llm.with_structured_output(UserStoryList)
            chain = prompt | structured_llm
            result = chain.invoke({
                "context": context_str,
                "prompt": state['initial_prompt']
            })
            generated_stories = [story.dict() for story in result.stories]

        logger.info(f"Generated {len(generated_stories)} user stories using {settings.LLM_PROVIDER}.")
        return {"generated_stories": generated_stories, "error": None}

    except Exception as e:
        logger.error(f"Error in generate_user_stories_node: {e}")
        return {"error": f"Failed to generate user stories with {settings.LLM_PROVIDER}: {e}"}

def push_to_jira_node(state: GraphState) -> GraphState:
    """
    Pushes the generated user stories to Jira via the integration service.
    """
    logger.info("Node: push_to_jira")
    if state.get("error"): return {}

    stories_to_push = state.get("generated_stories", [])
    if not stories_to_push:
        logger.warning("No stories to push to Jira.")
        return {"jira_results": []}

    jira_results = []
    integration_url = f"{settings.INTEGRATION_SERVICE_URL}/integrations/jira/issues"

    for story in stories_to_push:
        # Create a unique internal ID for traceability
        internal_id = f"req-{uuid.uuid4()}"

        # Format the description for Jira
        jira_description = f"{story['description']}\n\n*Acceptance Criteria:*\n"
        for i, criteria in enumerate(story['acceptance_criteria'], 1):
            jira_description += f"- {criteria}\n"

        payload = {
            "internal_id": internal_id,
            "source_service": "requirements-agent-service",
            "project_key": state['jira_project_key'],
            "title": story['title'],
            "description": jira_description,
            "issue_type": "Story"
        }

        try:
            response = requests.post(integration_url, json=payload, timeout=15)
            response.raise_for_status()
            result_data = response.json()
            jira_results.append(result_data)
            logger.info(f"Successfully pushed story '{story['title']}' to Jira as {result_data['jira_key']}.")
        except requests.RequestException as e:
            error_message = f"Failed to push story '{story['title']}' to Jira. Error: {e}"
            logger.error(error_message)
            # Continue to the next story, but record the error
            jira_results.append({"error": error_message, "story": story})

    return {"jira_results": jira_results, "error": None}

#--------------------------------------------------------------------------
# 4. Define the Graph and conditional edges
#--------------------------------------------------------------------------

def should_continue(state: GraphState) -> ConditionalEdge:
    """Conditional edge to check for errors and decide the next step."""
    if state.get("error"):
        logger.error(f"Error detected in graph state: {state['error']}")
        return END

    # If stories were generated, push them. Otherwise, end.
    if state.get("generated_stories"):
        return "push_to_jira"
    else:
        logger.warning("No stories were generated, ending graph execution.")
        return END

# Initialize the graph
workflow = StateGraph(GraphState)

# Add nodes
workflow.add_node("retrieve_documents", retrieve_documents_node)
workflow.add_node("generate_user_stories", generate_user_stories_node)
workflow.add_node("push_to_jira", push_to_jira_node)

# Set the entry point
workflow.set_entry_point("retrieve_documents")

# Add edges
workflow.add_edge("retrieve_documents", "generate_user_stories")
workflow.add_conditional_edges(
    "generate_user_stories",
    should_continue,
)
workflow.add_edge("push_to_jira", END)

# Compile the graph into a runnable
agent_graph = workflow.compile()
logger.info("Requirement generation agent graph compiled successfully.")
