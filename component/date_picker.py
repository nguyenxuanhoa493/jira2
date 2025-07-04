"""Component cho chọn ngày tháng với các tùy chọn nhanh"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Tuple, Optional
from service.utils.date_utils import get_date_range, get_default_dates

# Constants
DATE_FORMAT = "DD-MM-YYYY"
QUICK_SELECT_OPTIONS = ["Hôm nay", "Hôm qua", "Tuần này", "Tuần trước", "Tùy chỉnh"]


def initialize_date_session_state():
    """Khởi tạo session state cho date picker"""
    start_date, end_date = get_default_dates()

    defaults = {
        "quick_select": "Hôm nay",
        "start_date": start_date,
        "end_date": end_date,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def update_dates_from_quick_select(quick_select: str):
    """Cập nhật ngày khi thay đổi lựa chọn nhanh"""
    if quick_select != st.session_state.quick_select:
        st.session_state.quick_select = quick_select
        if quick_select != "Tùy chỉnh":
            start_date, end_date = get_date_range(quick_select)
            st.session_state.start_date = start_date
            st.session_state.end_date = end_date


def render_date_picker() -> Tuple[datetime.date, datetime.date]:
    """Render date picker với 3 cột: quick select, start date, end date"""
    col1, col2, col3 = st.columns(3)

    with col1:
        quick_select = st.selectbox(
            "Chọn nhanh khoảng thời gian",
            QUICK_SELECT_OPTIONS,
            index=2,
            key="quick_select_input",
        )

    # Cập nhật ngày khi thay đổi lựa chọn nhanh
    update_dates_from_quick_select(quick_select)

    is_custom_mode = quick_select == "Tùy chỉnh"

    with col2:
        start_date = st.date_input(
            "Ngày bắt đầu",
            value=st.session_state.start_date,
            format=DATE_FORMAT,
            disabled=not is_custom_mode,
            key="start_date_input",
        )

    with col3:
        end_date = st.date_input(
            "Ngày kết thúc",
            value=st.session_state.end_date,
            format=DATE_FORMAT,
            disabled=not is_custom_mode,
            key="end_date_input",
        )

    # Cập nhật session state khi người dùng thay đổi ngày (chỉ khi ở mode tùy chỉnh)
    if is_custom_mode:
        st.session_state.start_date = start_date
        st.session_state.end_date = end_date

    return start_date, end_date


def validate_and_show_date_range(
    start_date: datetime.date, end_date: datetime.date
) -> bool:
    """Validate và hiển thị thông tin khoảng thời gian"""
    if start_date > end_date:
        st.toast("Ngày bắt đầu không thể lớn hơn ngày kết thúc!", icon="❌")
        return False

    days_count = (end_date - start_date).days + 1
    st.toast(
        f"Khoảng thời gian: {start_date} → {end_date} ({days_count} ngày)", icon="✅"
    )
    return True
