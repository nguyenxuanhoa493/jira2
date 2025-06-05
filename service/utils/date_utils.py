"""Utilities cho xử lý ngày tháng trong ứng dụng"""

from datetime import datetime, timedelta
from typing import Tuple

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
