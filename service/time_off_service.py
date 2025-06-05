"""
Service quản lý ngày nghỉ (Time Off Management)
"""

import calendar
from datetime import datetime, date
from typing import List, Dict, Optional

from .get_client import get_supabase


class TimeOffService:
    """Service quản lý ngày nghỉ của team"""

    def __init__(self):
        self.supabase = get_supabase()

    def get_time_off_data(self, year: int, month: int) -> List[Dict]:
        """
        Lấy dữ liệu ngày nghỉ trong tháng

        Args:
            year: Năm
            month: Tháng (1-12)

        Returns:
            List[Dict]: Danh sách ngày nghỉ
        """
        try:
            start_date = f"{year}-{month:02d}-01"
            # Tính ngày cuối tháng
            _, last_day = calendar.monthrange(year, month)
            end_date = f"{year}-{month:02d}-{last_day:02d}"

            # Query Supabase
            data = self.supabase.select_with_filter(
                "time_off", "date", start_date, "gte"
            )
            if data:
                # Lọc thêm để chỉ lấy trong tháng
                filtered_data = []
                for item in data:
                    item_date = datetime.strptime(item["date"], "%Y-%m-%d").date()
                    if item_date.year == year and item_date.month == month:
                        filtered_data.append(item)
                return filtered_data
            return []
        except Exception as e:
            raise Exception(f"Lỗi khi lấy dữ liệu ngày nghỉ: {str(e)}")

    def save_time_off(
        self, selected_date: date, user_name: str, time_off_type: str, note: str
    ) -> bool:
        """
        Lưu thông tin ngày nghỉ vào database

        Args:
            selected_date: Ngày nghỉ
            user_name: Tên người nghỉ
            time_off_type: Loại nghỉ (Cả ngày, Buổi sáng, Buổi chiều)

        Returns:
            bool: True nếu thành công
        """
        try:
            data = {
                "date": selected_date.strftime("%Y-%m-%d"),
                "user_name": user_name,
                "time_off": time_off_type,
                "note": note,
            }

            result = self.supabase.insert_data("time_off", data)
            return bool(result)
        except Exception as e:
            raise Exception(f"Lỗi khi lưu ngày nghỉ: {str(e)}")

    def delete_time_off(self, time_off_id: int) -> bool:
        """
        Xóa ngày nghỉ theo ID

        Args:
            time_off_id: ID của ngày nghỉ

        Returns:
            bool: True nếu thành công
        """
        try:
            result = self.supabase.delete_data("time_off", "id", time_off_id)
            return bool(result)
        except Exception as e:
            raise Exception(f"Lỗi khi xóa ngày nghỉ: {str(e)}")

    def get_user_stats(self, time_off_data: List[Dict]) -> Dict[str, int]:
        """
        Thống kê số ngày nghỉ theo user

        Args:
            time_off_data: Dữ liệu ngày nghỉ

        Returns:
            Dict[str, int]: Dictionary với key là tên user, value là số ngày nghỉ
        """
        user_stats = {}
        for item in time_off_data:
            user = item["user_name"]
            if user not in user_stats:
                user_stats[user] = 0
            user_stats[user] += 1 if item["time_off"] == "Cả ngày" else 0.5
        return user_stats

    def create_time_off_dict(self, time_off_data: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Tạo dictionary để tra cứu nhanh ngày nghỉ theo ngày

        Args:
            time_off_data: Dữ liệu ngày nghỉ

        Returns:
            Dict[str, List[Dict]]: Dictionary với key là ngày (YYYY-MM-DD), value là list ngày nghỉ
        """
        time_off_dict = {}
        for item in time_off_data:
            item_date = item["date"]
            if item_date not in time_off_dict:
                time_off_dict[item_date] = []
            time_off_dict[item_date].append(item)
        return time_off_dict
