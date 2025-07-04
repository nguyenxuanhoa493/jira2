"""Utilities cho xử lý ngày tháng trong ứng dụng"""

from datetime import datetime, timedelta
from typing import Tuple, Optional

# Constants
DEFAULT_DAYS_BACK = 7


def get_date_range(option: str) -> Tuple[datetime.date, datetime.date]:
    """Tính toán khoảng ngày dựa trên lựa chọn nhanh"""
    today = datetime.now().date()

    date_ranges = {
        "Hôm nay": (today, today),
        "Hôm qua": (today - timedelta(days=1), today - timedelta(days=1)),
        "Tuần này": _get_current_week_range(today),
        "Tuần trước": _get_last_week_range(today),
    }

    return date_ranges.get(option, _get_default_range(today))


def _get_current_week_range(
    today: datetime.date,
) -> Tuple[datetime.date, datetime.date]:
    """Tính khoảng ngày từ thứ 2 đến chủ nhật của tuần hiện tại"""
    days_since_monday = today.weekday()
    monday = today - timedelta(days=days_since_monday)
    sunday = monday + timedelta(days=6)
    return monday, sunday


def _get_last_week_range(today: datetime.date) -> Tuple[datetime.date, datetime.date]:
    """Tính khoảng ngày từ thứ 2 đến chủ nhật của tuần trước"""
    days_since_monday = today.weekday()
    this_monday = today - timedelta(days=days_since_monday)
    last_monday = this_monday - timedelta(days=7)
    last_sunday = last_monday + timedelta(days=6)
    return last_monday, last_sunday


def _get_default_range(today: datetime.date) -> Tuple[datetime.date, datetime.date]:
    """Khoảng ngày mặc định cho tùy chỉnh"""
    return today - timedelta(days=DEFAULT_DAYS_BACK), today


def get_default_dates() -> Tuple[datetime.date, datetime.date]:
    """Lấy ngày mặc định cho khởi tạo"""
    today = datetime.now().date()
    return today, today  # Mặc định là hôm nay


def parse_jira_datetime(date_str: Optional[str]) -> Optional[datetime]:
    """
    Chuyển đổi chuỗi ngày tháng từ Jira (ISO 8601 format) sang datetime object.
    Ví dụ: "2025-06-11T09:58:07.555+0700"
    """
    if not date_str:
        return None
    try:
        # fromisoformat có thể xử lý trực tiếp format này
        return datetime.fromisoformat(date_str)
    except (ValueError, TypeError):
        return None


def adjust_sprint_dates(
    start_date_str: str, end_date_str: str
) -> Tuple[datetime, datetime]:
    """
    Điều chỉnh ngày bắt đầu và kết thúc của sprint.
    - Start date: 00:00:00 của ngày bắt đầu.
    - End date: 23:59:59 của ngày Chủ Nhật trong tuần của ngày kết thúc.
    """
    # Chuyển đổi string sang datetime object, chỉ lấy phần ngày
    start_date = datetime.fromisoformat(start_date_str.replace("Z", "+00:00")).date()
    end_date = datetime.fromisoformat(end_date_str.replace("Z", "+00:00")).date()

    # Điều chỉnh start_date về 00:00:00
    adjusted_start = datetime.combine(start_date, datetime.min.time())

    # Tìm ngày chủ nhật của tuần chứa end_date
    # weekday() trả về 0 cho Thứ Hai, 6 cho Chủ Nhật
    days_to_sunday = 6 - end_date.weekday()
    sunday_of_week = end_date + timedelta(days=days_to_sunday)

    # Điều chỉnh end_date về 23:59:59 của ngày Chủ Nhật
    adjusted_end = datetime.combine(sunday_of_week, datetime.max.time())

    return adjusted_start, adjusted_end
