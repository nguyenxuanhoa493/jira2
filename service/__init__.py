"""
Service package cho Jira integration
Bao gồm CacheManager mới thay thế hybrid_singleton
"""

# Import từ CacheManager mới
from .get_client import (
    CacheManager,
    get_jira,
    get_supabase,
    reset_cache,
    check_clients_health,
    auto_fix_issues,
)

# Import từ cấu trúc cũ để backward compatibility
from .clients.jira.jira_client import (
    JiraHybridClient,
    JiraClient,  # Backward compatibility
    get_jira_client,  # Backward compatibility
    get_jira_hybrid_client,
    get_jira_hybrid_client_lite,
)

# Main exports - CacheManager approach (recommended)
__all__ = [
    # New CacheManager approach (RECOMMENDED)
    "CacheManager",
    "get_jira",
    "get_supabase",
    "reset_cache",
    "check_clients_health",
    "auto_fix_issues",
    # Backward compatibility - hybrid singleton approach (DEPRECATED)
    "JiraHybridClient",
    "JiraClient",  # Backward compatibility
    "get_jira_client",  # Backward compatibility
    "get_jira_hybrid_client",
    "get_jira_hybrid_client_lite",
]
