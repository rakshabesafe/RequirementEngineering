# AI-Driven Software Development Lifecycle Platform

This project is a comprehensive, microservices-based platform designed to leverage AI agents to assist and automate various stages of the software development lifecycle (SDLC). From ingesting requirement documents to generating user stories, creating architectural models, and ensuring traceability, this platform provides a robust foundation for building AI-powered engineering tools.

## Architectural Principles

The platform is built on a set of modern architectural principles:

- **AI-First Design:** Core business logic is encapsulated within AI agents, which are treated as first-class citizens.
- **Microservices Ecosystem:** Each service is aligned with a specific Domain-Driven Design (DDD) Bounded Context, promoting separation of concerns and scalability.
- **Event-Driven & Asynchronous:** Inter-service communication defaults to being asynchronous via a message broker (RabbitMQ), ensuring loose coupling and resilience. Synchronous REST APIs are primarily used for client-to-gateway interactions.
- **Immutability:** Key artifacts, such as architectural models, are immutable. Changes result in new versions, providing a complete and auditable history.

## Technology Stack

| Category              | Technology                                   |
|-----------------------|----------------------------------------------|
| Backend               | FastAPI (Python)                             |
| Frontend              | ReactJS                                      |
| API Gateway           | Kong                                         |
| Databases             | PostgreSQL, Neo4j (Graph), Qdrant (Vector)   |
| Storage               | MinIO (S3-compatible object storage)         |
| AI Frameworks         | LangChain, LangGraph                         |
| LLM Providers         | OpenAI, Ollama (configurable)                |
| Messaging             | RabbitMQ                                     |
| Containerization      | Docker, Docker Compose                       |

## Services Overview

The platform consists of the following microservices:

- **`frontend-gateway`**: The single entry point for all UI clients, handled by Kong.
- **`project-input-service`**: Manages projects and ingests user documents into MinIO.
- **`architecture-adr-service`**: The source of truth for versioned architectural models and ADRs.
- **`integration-and-sync-service`**: Manages communication with external tools like Jira.
- **`requirements-agent-service`**: Hosts AI agents for generating user stories from documents.
- **`architecture-agent-service`**: (Phase 2) Hosts AI agents for generating architecture from requirements.
- **`traceability-service`**: (Phase 2) Manages the Neo4j graph of relationships between all artifacts.
- **`diagram-generation-service`**: (Phase 2) Renders textual diagrams (PlantUML, Mermaid) into images.
- **`notification-service`**: (Phase 3) Manages user notifications.

## Getting Started

### Prerequisites

1.  **Docker & Docker Compose:** Ensure you have Docker and Docker Compose (V2 syntax, `docker compose`) installed and running.
2.  **API Keys:** You will need API keys and credentials for the external services you wish to use.
3.  **(Optional) Ollama:** If you intend to use local models, you must have [Ollama](https://ollama.com/) installed and running on your host machine.

### Configuration

Before running the platform, you must configure the necessary credentials in the `docker-compose.yml` file at the root of this project.

Find the following service definitions and add your credentials:

1.  **`integration-and-sync-service`**:
    ```yaml
    environment:
      - JIRA_URL=https://your-jira-instance.atlassian.net
      - JIRA_USERNAME=your-email@example.com
      - JIRA_API_TOKEN=your-api-token
    ```

2.  **`requirements-agent-service`**:
    ```yaml
    environment:
      - LLM_PROVIDER=openai # or 'ollama'
      # --- OpenAI Credentials ---
      - OPENAI_API_KEY=your-openai-api-key
      # --- Ollama Configuration ---
      - OLLAMA_BASE_URL=http://host.docker.internal:11434 # Default for Docker Desktop
      - OLLAMA_MODEL_NAME=llama3
    ```

### Running the Platform

Once configured, you can start the entire platform with a single command from the project root:

```bash
# The 'sudo' may be required depending on your Docker installation
sudo docker compose up --build -d
```

This command will build the images for all custom services and start all containers in detached mode.

## Accessing the Services

- **Frontend Application:** `http://localhost:3000`
- **API Gateway (Kong):** `http://localhost` (or `http://localhost:80`)
- **Kong Admin API:** `http://localhost:8001`
- **MinIO Console:** `http://localhost:9001`
- **RabbitMQ Management:** `http://localhost:15672`
- **Neo4j Browser:** `http://localhost:7474`