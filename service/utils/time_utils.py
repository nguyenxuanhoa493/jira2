import streamlit as st
from datetime import datetime

"""Utility functions cho xử lý thời gian"""


def format_time_spent(seconds):
    """
    Chuyển đổi giây thành định dạng thời gian dễ đọc

    Args:
        seconds (int): Số giây

    Returns:
        str: Định dạng thời gian dễ đọc (ví dụ: "2h 30m", "1h", "45m")
    """
    if not seconds:
        return "0h"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if hours > 0 and minutes > 0:
        return f"{hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h"
    elif minutes > 0:
        return f"{minutes}m"
    else:
        return f"{seconds}s"


def seconds_to_hours(seconds):
    """
    Chuyển đổi giây thành giờ (decimal)

    Args:
        seconds (int): Số giây

    Returns:
        float: Số giờ (làm tròn 2 chữ số thập phân)
    """
    if not seconds:
        return 0.0
    return round(seconds / 3600, 2)


def format_duration(start_time, end_time):
    """
    Tính và format khoảng thời gian giữa 2 thời điểm

    Args:
        start_time (datetime): Thời gian bắt đầu
        end_time (datetime): Thời gian kết thúc

    Returns:
        str: Khoảng thời gian được format
    """
    duration = end_time - start_time
    total_seconds = int(duration.total_seconds())
    return format_time_spent(total_seconds)


def cal_hours_since_update(input_time_str: str):

    import pytz

    input_time = convert_time_str_to_datetime(input_time_str)
    now = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh"))

    # Bỏ thông tin timezone để so sánh
    if input_time.tzinfo is not None:
        now = now.astimezone(input_time.tzinfo)

    # Calculate elapsed time
    elapsed = now.replace(tzinfo=None) - input_time.replace(tzinfo=None)
    total_hours = round(elapsed.total_seconds() / 3600, 2)
    hours = int(total_hours)
    days = hours // 24
    remaining_hours = hours % 24

    return {
        "hours_elapsed": hours,
        "hours_elapsed_str": f"{hours}h",
        "date_elapsed": f"{days}d {remaining_hours}h",
    }


def convert_time_str_to_datetime(time_str) -> datetime:

    from dateutil import parser

    if not time_str:
        return ""

    if isinstance(time_str, datetime):
        return time_str
    try:
        parsed_datetime = parser.parse(time_str)
        return parsed_datetime.replace(tzinfo=None)
    except Exception as e:
        raise ValueError(f"Không thể parse chuỗi thời gian '{time_str}': {str(e)}")


def convert_seconds_to_jira_time(seconds: int) -> str:
    """
    Chuyển đổi số giây thành định dạng thời gian Jira.

    Quy ước:
    - 1 tuần = 7 ngày
    - 1 ngày = 8 giờ
    - 1 giờ = 60 phút
    - 1 phút = 60 giây

    Args:
        seconds (int): Số giây cần chuyển đổi

    Returns:
        str: Định dạng thời gian theo chuẩn Jira (vd: "1w 2d 3h 30m")
    """
    if seconds == 0:
        return "0m"
    
    # Xử lý số âm
    is_negative = seconds < 0
    abs_seconds = abs(seconds)
    
    if abs_seconds == 0:
        return "0m"

    # Tính toán các đơn vị thời gian
    minutes = abs_seconds // 60
    hours = minutes // 60
    days = hours // 8  # 1 ngày = 8 giờ
    weeks = days // 7  # 1 tuần = 7 ngày

    # Tính phần dư
    remaining_days = days % 7
    remaining_hours = hours % 8
    remaining_minutes = minutes % 60

    # Tạo chuỗi kết quả
    result_parts = []

    if weeks > 0:
        result_parts.append(f"{weeks}w")
    if remaining_days > 0:
        result_parts.append(f"{remaining_days}d")
    if remaining_hours > 0:
        result_parts.append(f"{remaining_hours}h")
    if remaining_minutes > 0:
        result_parts.append(f"{remaining_minutes}m")

    result = " ".join(result_parts) if result_parts else "0m"
    
    # Thêm dấu trừ nếu là số âm
    return f"-{result}" if is_negative else result
