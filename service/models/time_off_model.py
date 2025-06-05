"""
Time Off Models - Định nghĩa cấu trúc dữ liệu cho ngày nghỉ
"""

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional


class TimeOffType(Enum):
    """Enum cho các loại nghỉ"""

    FULL_DAY = "Cả ngày"
    MORNING = "Buổi sáng"
    AFTERNOON = "Buổi chiều"


@dataclass
class TimeOffRecord:
    """Model cho một record ngày nghỉ"""

    id: Optional[int]
    date: date
    user_name: str
    time_off_type: TimeOffType
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "TimeOffRecord":
        """
        Tạo TimeOffRecord từ dictionary

        Args:
            data: Dictionary chứa dữ liệu

        Returns:
            TimeOffRecord: Instance của TimeOffRecord
        """
        # Parse date từ string nếu cần
        if isinstance(data["date"], str):
            date_obj = date.fromisoformat(data["date"])
        else:
            date_obj = data["date"]

        # Parse time_off_type
        time_off_type = TimeOffType(data["time_off"])

        return cls(
            id=data.get("id"),
            date=date_obj,
            user_name=data["user_name"],
            time_off_type=time_off_type,
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def to_dict(self) -> dict:
        """
        Chuyển TimeOffRecord thành dictionary

        Returns:
            dict: Dictionary representation
        """
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "user_name": self.user_name,
            "time_off": self.time_off_type.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def __str__(self) -> str:
        """String representation"""
        return f"{self.user_name} - {self.time_off_type.value} ({self.date.strftime('%d/%m/%Y')})"


@dataclass
class TimeOffStats:
    """Model cho thống kê ngày nghỉ"""

    user_name: str
    total_days: int
    full_days: int
    half_days: int

    def __str__(self) -> str:
        """String representation"""
        return f"{self.user_name}: {self.total_days} ngày ({self.full_days} cả ngày, {self.half_days} nửa ngày)"


@dataclass
class MonthlyTimeOffSummary:
    """Model cho tổng kết ngày nghỉ trong tháng"""

    year: int
    month: int
    total_records: int
    unique_users: int
    user_stats: list[TimeOffStats]

    def __str__(self) -> str:
        """String representation"""
        return f"Tháng {self.month}/{self.year}: {self.total_records} lượt nghỉ từ {self.unique_users} người"
