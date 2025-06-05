"""
Calendar Utilities - Các hàm tiện ích cho calendar
"""

import calendar
from datetime import datetime, date
from typing import List, Dict, Tuple


class CalendarUtils:
    """Utility class cho các chức năng calendar"""

    @staticmethod
    def get_month_range(year: int, month: int) -> Tuple[str, str]:
        """
        Lấy ngày đầu và cuối tháng

        Args:
            year: Năm
            month: Tháng (1-12)

        Returns:
            Tuple[str, str]: (start_date, end_date) format YYYY-MM-DD
        """
        start_date = f"{year}-{month:02d}-01"
        _, last_day = calendar.monthrange(year, month)
        end_date = f"{year}-{month:02d}-{last_day:02d}"
        return start_date, end_date

    @staticmethod
    def format_date_vietnamese(date_obj: date) -> str:
        """
        Format ngày theo kiểu Việt Nam

        Args:
            date_obj: Date object

        Returns:
            str: Ngày format dd/mm/yyyy
        """
        return date_obj.strftime("%d/%m/%Y")

    @staticmethod
    def parse_date_string(date_string: str) -> date:
        """
        Parse string thành date object

        Args:
            date_string: Date string format YYYY-MM-DD

        Returns:
            date: Date object
        """
        return datetime.strptime(date_string, "%Y-%m-%d").date()

    @staticmethod
    def is_weekend(date_obj: date) -> bool:
        """
        Kiểm tra có phải cuối tuần không

        Args:
            date_obj: Date object

        Returns:
            bool: True nếu là thứ 7 hoặc CN
        """
        return date_obj.weekday() >= 5

    @staticmethod
    def is_today(date_obj: date) -> bool:
        """
        Kiểm tra có phải ngày hôm nay không

        Args:
            date_obj: Date object

        Returns:
            bool: True nếu là hôm nay
        """
        return date_obj == date.today()

    @staticmethod
    def get_weekday_name_vietnamese(date_obj: date) -> str:
        """
        Lấy tên thứ trong tuần bằng tiếng Việt

        Args:
            date_obj: Date object

        Returns:
            str: Tên thứ (T2, T3, ..., CN)
        """
        weekday_names = {
            0: "T2",  # Monday
            1: "T3",  # Tuesday
            2: "T4",  # Wednesday
            3: "T5",  # Thursday
            4: "T6",  # Friday
            5: "T7",  # Saturday
            6: "CN",  # Sunday
        }
        return weekday_names.get(date_obj.weekday(), "")

    @staticmethod
    def get_month_name_vietnamese(month: int) -> str:
        """
        Lấy tên tháng bằng tiếng Việt

        Args:
            month: Số tháng (1-12)

        Returns:
            str: Tên tháng
        """
        month_names = {
            1: "Tháng Một",
            2: "Tháng Hai",
            3: "Tháng Ba",
            4: "Tháng Tư",
            5: "Tháng Năm",
            6: "Tháng Sáu",
            7: "Tháng Bảy",
            8: "Tháng Tám",
            9: "Tháng Chín",
            10: "Tháng Mười",
            11: "Tháng Mười Một",
            12: "Tháng Mười Hai",
        }
        return month_names.get(month, f"Tháng {month}")

    @staticmethod
    def validate_date_range(start_date: date, end_date: date) -> bool:
        """
        Validate khoảng thời gian

        Args:
            start_date: Ngày bắt đầu
            end_date: Ngày kết thúc

        Returns:
            bool: True nếu valid
        """
        return start_date <= end_date

    @staticmethod
    def get_business_days_count(start_date: date, end_date: date) -> int:
        """
        Đếm số ngày làm việc (không tính T7, CN)

        Args:
            start_date: Ngày bắt đầu
            end_date: Ngày kết thúc

        Returns:
            int: Số ngày làm việc
        """
        business_days = 0
        current_date = start_date

        while current_date <= end_date:
            if not CalendarUtils.is_weekend(current_date):
                business_days += 1
            current_date = date.fromordinal(current_date.toordinal() + 1)

        return business_days
