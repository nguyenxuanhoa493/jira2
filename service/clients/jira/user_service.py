import json
import os
from service.base.jira_base import JiraBase
from conf import DEFAULT_PROJECT


class UserService(JiraBase):
    """Service quản lý user trong Jira"""

    def __init__(self):
        super().__init__()
        # Load users từ file JSON
        try:
            with open("./service/utils/user.json", "r", encoding="utf-8") as f:
                self.users = json.load(f)
        except FileNotFoundError:
            self.users = []

        # Tạo dict mapping để query user data nhanh hơn - O(1) complexity
        self._users_by_display_name = {}
        self._users_by_account_id = {}

        # Build mapping dictionaries
        for user in self.users:
            display_name = user.get("displayName")
            account_id = user.get("accountId")

            if display_name:
                self._users_by_display_name[display_name] = user
            if account_id:
                self._users_by_account_id[account_id] = user

    def get_list_users(self, limit=200):
        """Lấy danh sách user từ Jira Cloud, chỉ lấy user có accountType là 'atlassian'"""
        params = {"maxResults": limit}
        users = self.jira._get_json("users/search", params)
        result = []
        for user in users:
            user_is_active_and_human = user.get(
                "accountType"
            ) == "atlassian" and user.get("active")
            if not user_is_active_and_human:
                continue
            user["avatar"] = user["avatarUrls"]["48x48"]
            del user["avatarUrls"]
            result.append(user)
        return result

    def search_users(self):
        """Tìm kiếm user có thể assign cho project"""
        return self.jira.search_assignable_users_for_projects(
            maxResults=200, projectKeys=DEFAULT_PROJECT, username=""
        )

    def get_user_by_display_name(self, display_name: str):
        """Lấy user data theo displayName - O(1) complexity"""
        return self._users_by_display_name.get(display_name)

    def get_user_by_account_id(self, account_id: str):
        """Lấy user data theo accountId - O(1) complexity"""
        return self._users_by_account_id.get(account_id)

    def get_avatar_url_by_display_name(self, display_name: str) -> str:
        """Lấy avatar URL theo displayName - O(1) complexity"""
        user = self.get_user_by_display_name(display_name)
        return user.get("avatar", "") if user else ""

    def get_short_name_by_display_name(self, display_name: str) -> str:
        """Lấy shortName (avatar markdown) theo displayName - O(1) complexity"""
        user = self.get_user_by_display_name(display_name)
        if user:
            shortName = user.get("shortName", display_name)
            return shortName

    def get_all_display_names(self) -> list:
        """Lấy danh sách tất cả displayName"""
        return list(self._users_by_display_name.keys())

    def get_all_account_ids(self) -> list:
        """Lấy danh sách tất cả accountId"""
        return list(self._users_by_account_id.keys())
