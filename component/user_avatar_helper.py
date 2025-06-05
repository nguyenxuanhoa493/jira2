"""
User Avatar Helper - Helper class để quản lý avatar và user data
"""

from typing import Dict, List, Optional
import streamlit as st


class UserAvatarHelper:
    """Helper class để quản lý avatar và user data"""

    # Constants
    AVATAR_SIZE = 48
    DEFAULT_AVATAR_STYLE = "vertical-align: middle; margin-right: 8px;"

    def __init__(self, jira_client):
        self.jira = jira_client
        self._user_cache = {}
        self._init_user_cache()

    def _init_user_cache(self):
        """Khởi tạo cache cho user data"""
        try:
            self._user_cache = {
                user.get("displayName"): user for user in self.jira.users
            }
        except AttributeError:
            # Fallback nếu không có jira.users
            self._user_cache = {}

    def get_user_data(self, display_name: str) -> Dict:
        """Lấy user data với cache"""
        if display_name in self._user_cache:
            return self._user_cache[display_name]

        # Fallback to API call
        try:
            user_data = self.jira.user_service.get_user_by_display_name(display_name)
            self._user_cache[display_name] = user_data  # Cache for next time
            return user_data
        except Exception:
            return {}

    def get_avatar_url(self, display_name: str) -> str:
        """Lấy avatar URL cho user"""
        user_data = self.get_user_data(display_name)
        return user_data.get("avatar", "")

    def get_short_name(self, display_name: str) -> str:
        """Lấy short name cho user"""
        user_data = self.get_user_data(display_name)
        return user_data.get("shortName", display_name)

    def render_user_avatar_html(
        self, display_name: str, size: Optional[int] = None
    ) -> str:
        """Render HTML cho avatar của user"""
        avatar_url = self.get_avatar_url(display_name)
        if not avatar_url:
            return ""

        size = size or self.AVATAR_SIZE
        return f'<img src="{avatar_url}?s={size}" class="custom-img" style="{self.DEFAULT_AVATAR_STYLE}">'

    def render_user_display_with_avatar(
        self, display_name: str, additional_info: str = "", use_short_name: bool = True
    ) -> str:
        """Render complete user display với avatar và thông tin bổ sung"""
        avatar_html = self.render_user_avatar_html(display_name)
        name_to_show = (
            self.get_short_name(display_name) if use_short_name else display_name
        )

        if avatar_html:
            return f"{avatar_html}**{name_to_show}**{additional_info}"
        else:
            return f"**{name_to_show}**{additional_info}"

    def render_avatar_list_for_day(self, users_off: List[Dict]) -> str:
        """Render danh sách avatar cho một ngày"""
        avatar_list = []
        for user_data in users_off:
            display_name = user_data["user_name"]
            avatar_url = self.get_avatar_url(display_name)
            if avatar_url:
                avatar_list.append(f"![Ảnh]({avatar_url}?s={self.AVATAR_SIZE})")

        # Loại bỏ duplicates và giữ thứ tự
        unique_avatars = list(dict.fromkeys(avatar_list))
        return " ".join(unique_avatars)
