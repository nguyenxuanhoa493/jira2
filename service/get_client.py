"""
Service Cache Manager - Quản lý tất cả clients một cách đơn giản
Thay thế hybrid_singleton pattern bằng approach đơn giản và reliable
"""

import streamlit as st
from typing import Optional, Union
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class CacheManager:
    """
    Quản lý cache cho tất cả clients trong ứng dụng
    Sử dụng Streamlit cache_resource native để đảm bảo performance và reliability
    """

    @staticmethod
    @st.cache_resource(show_spinner="🔧 Đang khởi tạo JIRA client...")
    def get_jira_client():
        """
        Tạo và cache JIRA client
        Returns: JiraHybridClient instance hoặc None nếu failed
        """
        try:
            from service.clients.jira.jira_client import JiraHybridClient

            client = JiraHybridClient()
            print("✅ JIRA client initialized successfully")
            return client
        except Exception as e:
            print(f"❌ JIRA client initialization failed: {str(e)}")
            if hasattr(st, "error"):
                st.error(f"❌ JIRA client initialization failed: {str(e)}")
            return None

    @staticmethod
    @st.cache_resource(show_spinner="🔧 Đang khởi tạo Supabase client...")
    def get_supabase_client():
        """
        Tạo và cache Supabase client
        Returns: SupabaseHybridClient instance hoặc None nếu failed
        """
        try:
            from service.clients.supabase.supabase_client import SupabaseHybridClient

            client = SupabaseHybridClient()
            print("✅ Supabase client initialized successfully")
            return client
        except Exception as e:
            print(f"❌ Supabase client initialization failed: {str(e)}")
            if hasattr(st, "error"):
                st.error(f"❌ Supabase client initialization failed: {str(e)}")
            return None

    @staticmethod
    def reset_all_caches():
        """
        Reset tất cả cache và session state
        """
        # Clear Streamlit cache
        st.cache_resource.clear()

        # Clear session state cache keys
        keys_to_clear = [
            k
            for k in st.session_state.keys()
            if any(
                cache_key in k.lower()
                for cache_key in ["client", "hybrid", "cache", "demo", "connection"]
            )
        ]
        for key in keys_to_clear:
            del st.session_state[key]

        print("🔄 All caches cleared by CacheManager")

    @staticmethod
    def get_client_info(client) -> dict:
        """
        Lấy thông tin chi tiết về client
        """
        if client is None:
            return {"status": "Not initialized", "type": None, "id": None}

        return {
            "status": "Initialized",
            "type": client.__class__.__name__,
            "id": id(client),
            "is_connected": getattr(client, "is_connected", False),
            "has_test_connection": hasattr(client, "test_connection"),
        }

    @staticmethod
    def test_client_connection(client) -> tuple[bool, str]:
        """
        Test connection của client
        Returns: (is_connected, message)
        """
        if client is None:
            return False, "Client is not initialized"

        if not hasattr(client, "test_connection"):
            return False, "Client does not support connection testing"

        try:
            return client.test_connection()
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"

    @staticmethod
    def get_all_clients_status() -> dict:
        """
        Lấy status của tất cả clients
        """
        jira = CacheManager.get_jira_client()
        supabase = CacheManager.get_supabase_client()

        return {
            "jira": {
                "info": CacheManager.get_client_info(jira),
                "connection": CacheManager.test_client_connection(jira),
            },
            "supabase": {
                "info": CacheManager.get_client_info(supabase),
                "connection": CacheManager.test_client_connection(supabase),
            },
        }

    @staticmethod
    def diagnose_issues() -> list[str]:
        """
        Tự động phát hiện các vấn đề với clients
        Returns: List of issues found
        """
        issues = []

        jira = CacheManager.get_jira_client()
        supabase = CacheManager.get_supabase_client()

        # Check for None clients
        if jira is None:
            issues.append("❌ JIRA client không khởi tạo được")

        if supabase is None:
            issues.append("❌ Supabase client không khởi tạo được")

        # Check for type confusion
        if supabase is not None and type(supabase).__name__ == "JiraHybridClient":
            issues.append("❌ Supabase client bị cache nhầm thành JIRA client")

        # Check connections
        if jira is not None:
            is_connected, _ = CacheManager.test_client_connection(jira)
            if not is_connected:
                issues.append("❌ JIRA client không kết nối được")

        if supabase is not None:
            is_connected, _ = CacheManager.test_client_connection(supabase)
            if not is_connected:
                issues.append("❌ Supabase client không kết nối được")

        return issues


# Convenience functions for easy import
def get_jira() -> Optional[object]:
    """Convenience function to get JIRA client"""
    return CacheManager.get_jira_client()


def get_supabase() -> Optional[object]:
    """Convenience function to get Supabase client"""
    return CacheManager.get_supabase_client()


def reset_cache():
    """Convenience function to reset all caches"""
    CacheManager.reset_all_caches()


def check_clients_health() -> dict:
    """Convenience function to check all clients health"""
    return CacheManager.get_all_clients_status()


def auto_fix_issues() -> bool:
    """
    Tự động phát hiện và khắc phục issues
    Returns: True nếu có issues được fix
    """
    issues = CacheManager.diagnose_issues()

    if issues:
        print("🚨 Issues detected:", issues)

        # Auto-fix by resetting cache
        CacheManager.reset_all_caches()

        if hasattr(st, "error") and hasattr(st, "success"):
            st.error("🚨 **Phát hiện vấn đề cache:**")
            for issue in issues:
                st.write(issue)

            st.info("🔧 **Đang tự động khắc phục...**")
            st.success("✅ Đã khắc phục tự động! Vui lòng refresh trang.")

        return True

    return False


# Export main interface
__all__ = [
    "CacheManager",
    "get_jira",
    "get_supabase",
    "reset_cache",
    "check_clients_health",
    "auto_fix_issues",
]
