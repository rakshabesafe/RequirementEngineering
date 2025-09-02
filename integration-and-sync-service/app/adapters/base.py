from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAdapter(ABC):
    """
    Abstract Base Class for all external tool integration adapters.
    Defines the common interface for creating and managing issues.
    """

    @abstractmethod
    def create_issue(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates an issue in the external system.

        :param issue_data: A dictionary containing the necessary information
                           to create the issue (e.g., title, description, project_key).
        :return: A dictionary containing the details of the created issue,
                 including its ID and key.
        """
        pass

    # In future phases, we would add more methods here:
    # @abstractmethod
    # def update_issue(self, issue_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
    #     pass
    #
    # @abstractmethod
    # def get_issue(self, issue_id: str) -> Dict[str, Any]:
    #     pass
