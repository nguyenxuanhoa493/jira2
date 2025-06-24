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
