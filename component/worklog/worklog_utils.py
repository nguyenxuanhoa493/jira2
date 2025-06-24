"""Utility functions cho worklog components"""

from service.clients.jira.user_service import UserService


def _get_user_avatar(username):
    """Lấy avatar URL của user từ Jira"""
    try:
        user_service = UserService()
        users = user_service.get_list_users()

        for user in users:
            # Safe access to user attributes - could be JIRA User object or dict
            user_display_name = ""
            user_avatar = ""

            if hasattr(user, "displayName"):
                # JIRA User object
                user_display_name = getattr(user, "displayName", "")
                user_avatar = getattr(user, "avatar", "")
            elif isinstance(user, dict):
                # Dictionary
                user_display_name = user.get("displayName", "")
                user_avatar = user.get("avatar", "")

            if user_display_name == username:
                return user_avatar
        return ""
    except Exception as e:
        print(f"Warning: Could not get user avatar: {e}")
        return ""


def _truncate_comment(comment):
    """Cắt ngắn comment nếu quá dài"""
    if len(comment) > 100:
        return comment[:100] + "..."
    return comment


def _break_long_text(text, max_chars=50):
    """Chia text dài thành nhiều dòng"""
    if not text or len(text) <= max_chars:
        return text

    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        if len(current_line + " " + word) <= max_chars:
            current_line += (" " + word) if current_line else word
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return "\n".join(lines)
