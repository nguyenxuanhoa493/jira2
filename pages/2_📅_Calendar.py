import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from datetime import datetime

# PHẢI ĐẶT ĐẦU TIÊN
st.set_page_config(
    page_title="Calendar - Ngày nghỉ",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Import các service và component đã tách
from service.time_off_service import TimeOffService
from component.calendar_component import CalendarComponent

# Khởi tạo services và components
time_off_service = TimeOffService()
calendar_component = CalendarComponent()

# Render CSS styles
calendar_component.render_calendar_styles()

# Render month navigation và lấy tháng/năm được chọn
selected_year, selected_month = calendar_component.render_month_navigation()

# Render sidebar chỉ với thống kê
calendar_component.render_sidebar()

# Lấy dữ liệu ngày nghỉ - chỉ gọi 1 lần
try:
    time_off_data = time_off_service.get_time_off_data(selected_year, selected_month)
    time_off_dict = time_off_service.create_time_off_dict(time_off_data)
except Exception as e:
    st.error(f"Lỗi khi tải dữ liệu: {str(e)}")
    time_off_data = []
    time_off_dict = {}

# Modal Dialog - hiển thị khi có ngày được chọn
if st.session_state.get("show_time_off_dialog", False):
    selected_date = st.session_state.get("selected_date")
    if selected_date:
        calendar_component.render_time_off_modal(selected_date, time_off_data)

# Render calendar header
calendar_component.render_calendar_header()

# Render calendar grid
calendar_component.render_calendar_grid(selected_year, selected_month, time_off_dict)

# Render bảng dữ liệu chi tiết
calendar_component.render_data_table(time_off_data, selected_month, selected_year)
