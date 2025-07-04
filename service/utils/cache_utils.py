"""
Cache utilities for file-based persistence
"""

import pickle
import os
import streamlit as st
from datetime import datetime
from typing import Any, Optional
import hashlib


class FileCache:
    """File-based cache system cho Streamlit - Persistent cache không expire tự động"""

    def __init__(self, cache_dir: str = ".streamlit_cache"):
        self.cache_dir = cache_dir
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        """Tạo cache directory nếu chưa có"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_file_path(self, cache_key: str) -> str:
        """Tạo đường dẫn file cache từ cache key"""
        # Hash cache key để tránh tên file quá dài
        hashed_key = hashlib.md5(cache_key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{hashed_key}.pkl")

    def save_cache(self, cache_key: str, data: Any):
        """
        Lưu data vào cache file (persistent - không expire)

        Args:
            cache_key: Unique key cho cache
            data: Dữ liệu cần cache
        """
        try:
            cache_file = self._get_cache_file_path(cache_key)

            cache_data = {
                "data": data,
                "timestamp": datetime.now(),
                "cache_key": cache_key,  # For debugging
            }

            with open(cache_file, "wb") as f:
                pickle.dump(cache_data, f)

            print(f"💾 Cache saved: {cache_key}")

        except Exception as e:
            print(f"❌ Error saving cache {cache_key}: {str(e)}")

    def load_cache(self, cache_key: str) -> Optional[Any]:
        """
        Load data từ cache file (persistent - không check TTL)

        Args:
            cache_key: Cache key để tìm

        Returns:
            Cached data hoặc None nếu không có
        """
        try:
            cache_file = self._get_cache_file_path(cache_key)

            if not os.path.exists(cache_file):
                return None

            with open(cache_file, "rb") as f:
                cache_data = pickle.load(f)

            print(f"⚡ Cache hit: {cache_key}")
            return cache_data["data"]

        except Exception as e:
            print(f"❌ Error loading cache {cache_key}: {str(e)}")
            return None

    def get_cache_metadata(self, cache_key: str) -> Optional[dict]:
        """
        Lấy metadata của cache (timestamp, cache_key) mà không load data

        Args:
            cache_key: Cache key để tìm

        Returns:
            Cache metadata dict hoặc None nếu không có
        """
        try:
            cache_file = self._get_cache_file_path(cache_key)

            if not os.path.exists(cache_file):
                return None

            with open(cache_file, "rb") as f:
                cache_data = pickle.load(f)

            return {
                "timestamp": cache_data.get("timestamp"),
                "cache_key": cache_data.get("cache_key"),
                "file_path": cache_file,
            }

        except Exception as e:
            print(f"❌ Error getting cache metadata {cache_key}: {str(e)}")
            return None

    def load_cache_with_metadata(
        self, cache_key: str
    ) -> tuple[Optional[Any], Optional[dict]]:
        """
        Load data và metadata từ cache

        Args:
            cache_key: Cache key để tìm

        Returns:
            Tuple (data, metadata) hoặc (None, None) nếu không có
        """
        try:
            cache_file = self._get_cache_file_path(cache_key)

            if not os.path.exists(cache_file):
                return None, None

            with open(cache_file, "rb") as f:
                cache_data = pickle.load(f)

            data = cache_data["data"]
            metadata = {
                "timestamp": cache_data.get("timestamp"),
                "cache_key": cache_data.get("cache_key"),
                "file_path": cache_file,
            }

            print(f"⚡ Cache hit with metadata: {cache_key}")
            return data, metadata

        except Exception as e:
            print(f"❌ Error loading cache with metadata {cache_key}: {str(e)}")
            return None, None

    def clear_cache(self, cache_key: Optional[str] = None):
        """
        Xóa cache

        Args:
            cache_key: Specific key để xóa, hoặc None để xóa tất cả
        """
        try:
            if cache_key:
                # Xóa cache cụ thể
                cache_file = self._get_cache_file_path(cache_key)
                if os.path.exists(cache_file):
                    os.remove(cache_file)
                    print(f"🗑️ Cache cleared: {cache_key}")
            else:
                # Xóa tất cả cache
                if os.path.exists(self.cache_dir):
                    for file in os.listdir(self.cache_dir):
                        if file.endswith(".pkl"):
                            os.remove(os.path.join(self.cache_dir, file))
                    print("🗑️ All cache cleared")

        except Exception as e:
            print(f"❌ Error clearing cache: {str(e)}")

    def get_cache_info(self) -> dict:
        """Lấy thông tin về cache hiện có"""
        try:
            info = {
                "cache_dir": self.cache_dir,
                "total_files": 0,
                "total_size_mb": 0,
                "files": [],
            }

            if not os.path.exists(self.cache_dir):
                return info

            for file in os.listdir(self.cache_dir):
                if file.endswith(".pkl"):
                    file_path = os.path.join(self.cache_dir, file)
                    file_size = os.path.getsize(file_path)
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))

                    info["files"].append(
                        {
                            "file": file,
                            "size_kb": round(file_size / 1024, 2),
                            "modified": file_mtime.strftime("%Y-%m-%d %H:%M:%S"),
                        }
                    )

                    info["total_files"] += 1
                    info["total_size_mb"] += file_size

            info["total_size_mb"] = round(info["total_size_mb"] / (1024 * 1024), 2)
            return info

        except Exception as e:
            print(f"❌ Error getting cache info: {str(e)}")
            return {"error": str(e)}


# Global instance
file_cache = FileCache()


def cache_with_file(cache_key: str):
    """
    Decorator để cache function result vào file (persistent)

    Args:
        cache_key: Cache key prefix
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Tạo unique cache key từ function args
            args_str = str(args) + str(sorted(kwargs.items()))
            full_cache_key = f"{cache_key}_{hashlib.md5(args_str.encode()).hexdigest()}"

            # Try load từ cache
            cached_result = file_cache.load_cache(full_cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function và cache result
            result = func(*args, **kwargs)
            file_cache.save_cache(full_cache_key, result)

            return result

        return wrapper

    return decorator
