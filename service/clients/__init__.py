"""
Clients package - External service integrations
"""

# Expose main clients for easy import
from .jira.jira_client import JiraClient
from .supabase.supabase_client import SupabaseHybridClient

__all__ = ["JiraClient", "SupabaseHybridClient"]
