import logging
from atlassian import Jira
from typing import Dict, Any

from .base import BaseAdapter
from ..config import settings

logger = logging.getLogger(__name__)

class JiraAdapter(BaseAdapter):
    """
    Adapter for interacting with the Atlassian Jira API.
    """

    def __init__(self):
        try:
            self.jira = Jira(
                url=settings.JIRA_URL,
                username=settings.JIRA_USERNAME,
                password=settings.JIRA_API_TOKEN,
                cloud=True  # Important for Atlassian Cloud instances
            )
            # Verify connection
            self.jira.get_server_info()
            logger.info("Successfully connected to Jira.")
        except Exception as e:
            logger.error(f"Failed to connect to Jira at {settings.JIRA_URL}. Error: {e}")
            # In a real app, you might want a more robust way to handle this,
            # but for now, we'll let it raise an exception on use.
            self.jira = None

    def create_issue(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates an issue in Jira.

        :param issue_data: A dictionary containing:
                           - 'project_key': The Jira project key (e.g., "PROJ").
                           - 'title': The summary/title of the issue.
                           - 'description': The body of the issue.
                           - 'issue_type': The type of issue (e.g., "Task", "Story").
        :return: A dictionary with details of the created issue from Jira.
        """
        if not self.jira:
            raise ConnectionError("Jira client not initialized. Check credentials and URL.")

        try:
            # Prepare the fields for the Jira API call
            fields = {
                "project": {"key": issue_data["project_key"]},
                "summary": issue_data["title"],
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": issue_data["description"]
                                }
                            ]
                        }
                    ]
                },
                "issuetype": {"name": issue_data["issue_type"]},
            }

            created_issue = self.jira.issue_create(fields=fields)
            logger.info(f"Successfully created Jira issue {created_issue['key']}.")

            # The response from jira.issue_create is already a dict
            # It looks like: {'id': '10002', 'key': 'PROJ-3', 'self': '...'}
            return created_issue

        except Exception as e:
            logger.error(f"Failed to create issue in Jira. Error: {e}")
            # Re-raise the exception to be handled by the API endpoint
            raise
