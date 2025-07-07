import os
from dotenv import load_dotenv

# Đọc file .env
load_dotenv()

# JIRA Configuration
JIRA_SERVER = os.getenv("JIRA_URL")
JIRA_USER = os.getenv("EMAIL")
JIRA_API_TOKEN = os.getenv("API_TOKEN")
DEFAULT_PROJECT = os.getenv("DEFAULT_PROJECT")

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

DEFAULT_FIELDS_ISSUE = [
    "summary",
    "status",
    "assignee",
    "creator",
    "reporter",
    "issuetype",
    "priority",
    "timeoriginalestimate",
    "customfield_10060",
    "customfield_10160",
    "customfield_10159",
    "customfield_10192",
    "customfield_10132",
    "customfield_10130",
    "customfield_10031",
    "customfield_10191",
    "customfield_10092",
    "subtasks",
    "reporter",
    "worklog",
    "closedSprints",
    "created",
    "updated",
    "timetracking",
    "duedate",
]

KEY_ISSUE_DEBUG = "1571"
DEFAULT_MAX_ISSUE_PER_PAGE = 100
STATUS_IS_DEV_DONE = ["Done", "Dev Done"]

STATUS_ORDER = {
    "Reopen": {"name": "Reopen", "color": "#e74c3c"},
    "To Do": {"name": "To Do", "color": "#95a5a6"},
    "In Progress": {"name": "In Progress", "color": "#3498db"},
    "Wait for review": {"name": "Wait for review", "color": "#f1c40f"},
    "Dev Done": {"name": "Dev Done", "color": "#4ade80"},
    "Test Done": {"name": "Test Done", "color": "#22c55e"},
    "Deployed": {"name": "Deployed", "color": "#16a34a"},
    "Done": {"name": "Done", "color": "#15803d"},
    "Close": {"name": "Close", "color": "#34495e"},
}


def validate_supabase_config():
    """Kiểm tra cấu hình Supabase có hợp lệ không"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return False, "Vui lòng cấu hình SUPABASE_URL và SUPABASE_KEY trong file .env"

    if (
        SUPABASE_URL == "https://your-project.supabase.co"
        or SUPABASE_KEY == "your-anon-key-here"
    ):
        return (
            False,
            "Vui lòng thay thế SUPABASE_URL và SUPABASE_KEY bằng giá trị thực tế",
        )

    return True, "Cấu hình Supabase hợp lệ"


def validate_jira_config():
    """Kiểm tra cấu hình JIRA có hợp lệ không"""
    if not JIRA_SERVER or not JIRA_USER or not JIRA_API_TOKEN:
        return False, "Vui lòng cấu hình JIRA_URL, EMAIL và API_TOKEN trong file .env"

    return True, "Cấu hình JIRA hợp lệ"
