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
