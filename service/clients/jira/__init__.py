"""
JIRA services package - All JIRA-related functionality
"""

# Main hybrid client + backward compatibility
from .jira_client import (
    JiraHybridClient,
    JiraClient,  # Backward compatibility alias
    get_jira_client,  # Backward compatibility
    get_jira_hybrid_client,
    get_jira_hybrid_client_lite,
    get_jira_hybrid_info,
    reset_jira_hybrid,
)

# Domain services
from .project_service import ProjectService
from .user_service import UserService
from .sprint_service import SprintService
from .worklog_service import WorklogService

__all__ = [
    # Main clients
    "JiraHybridClient",
    "JiraClient",  # Backward compatibility
    # Getter functions
    "get_jira_client",  # Backward compatibility
    "get_jira_hybrid_client",
    "get_jira_hybrid_client_lite",
    # Utility functions
    "get_jira_hybrid_info",
    "reset_jira_hybrid",
    # Domain services
    "ProjectService",
    "UserService",
    "SprintService",
    "WorklogService",
]
