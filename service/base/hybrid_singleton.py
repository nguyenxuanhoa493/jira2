import threading
import streamlit as st
from abc import ABC, abstractmethod, ABCMeta
from typing import Any, Optional
import time


class HybridSingletonMeta(ABCMeta):
    """
    Metaclass cho Hybrid Singleton pattern
    Đảm bảo thread-safe và performance tối ưu
    Inherit từ ABCMeta để tương thích với ABC
    """

    _instances = {}
    _locks = {}

    def __call__(cls, *args, **kwargs):
        # Tạo lock cho từng class nếu chưa có
        if cls not in cls._locks:
            cls._locks[cls] = threading.Lock()

        # Thread-safe instance creation
        if cls not in cls._instances:
            with cls._locks[cls]:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
                    print(f"🔧 {cls.__name__} Hybrid Singleton created: {id(instance)}")

        return cls._instances[cls]


class HybridSingletonBase(ABC, metaclass=HybridSingletonMeta):
    """
    Base class cho Hybrid Singleton pattern

    3 Layers:
    1. Classic Singleton (thread-safe với metaclass)
    2. Streamlit Cache Resource
    3. Session State fallback (optional)
    """

    def __init__(self):
        if hasattr(self, "_initialized"):
            return

        self._initialized = False
        self._creation_time = time.time()
        self._access_count = 0

        # Call child class initialization
        self._initialize()
        self._initialized = True

    @abstractmethod
    def _initialize(self):
        """Override this method in child classes"""
        pass

    def _track_access(self):
        """Track access for monitoring"""
        self._access_count += 1

    def get_stats(self) -> dict:
        """Get singleton statistics"""
        return {
            "class_name": self.__class__.__name__,
            "instance_id": id(self),
            "initialized": self._initialized,
            "creation_time": self._creation_time,
            "access_count": self._access_count,
            "uptime_seconds": time.time() - self._creation_time,
        }

    @classmethod
    def reset_instance(cls):
        """Reset singleton instance (for testing/debugging)"""
        if cls in cls._instances:
            with cls._locks.get(cls, threading.Lock()):
                if cls in cls._instances:
                    del cls._instances[cls]
                    print(f"🔄 {cls.__name__} Hybrid Singleton reset")

    @classmethod
    def get_instance_info(cls) -> dict:
        """Get information about current instance"""
        if cls in cls._instances:
            instance = cls._instances[cls]
            return instance.get_stats()
        return {"status": "No instance created yet"}


def create_hybrid_getter(
    client_class, cache_key: str, session_key: Optional[str] = None
):
    """
    Factory function to create hybrid getter functions

    Args:
        client_class: The singleton class to instantiate
        cache_key: Key for Streamlit cache
        session_key: Optional key for session state fallback
    """

    @st.cache_resource(show_spinner=False)
    def _cached_getter(*args, **kwargs):
        """Layer 2: Streamlit Cache Resource"""
        return client_class(*args, **kwargs)

    def hybrid_getter(*args, **kwargs):
        """
        Hybrid getter with 3 layers:
        1. Session State (fastest)
        2. Streamlit Cache (fast)
        3. Singleton Creation (thread-safe)
        """

        # Layer 3: Optional Session State check
        if session_key and session_key in st.session_state:
            instance = st.session_state[session_key]
            instance._track_access()
            return instance

        # Layer 2: Streamlit Cache Resource
        instance = _cached_getter(*args, **kwargs)
        instance._track_access()

        # Store in session state for faster next access
        if session_key:
            st.session_state[session_key] = instance

        return instance

    return hybrid_getter


# Utility functions for monitoring all hybrid singletons
def get_all_hybrid_instances() -> dict:
    """Get info about all hybrid singleton instances"""
    result = {}
    for cls, instance in HybridSingletonMeta._instances.items():
        result[cls.__name__] = instance.get_stats()
    return result


def reset_all_hybrid_instances():
    """Reset all hybrid singleton instances"""
    for cls in list(HybridSingletonMeta._instances.keys()):
        cls.reset_instance()
    st.cache_resource.clear()
    print("🔄 All Hybrid Singletons reset")
