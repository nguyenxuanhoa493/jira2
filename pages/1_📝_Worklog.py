# 📝 Worklog
import streamlit as st
from datetime import datetime
from service.clients.jira.jira_client import get_jira_client
from service.clients.jira.worklog_service import WorklogService
from component.worklog_display import display_worklog_data, display_worklog_summary
from component.date_picker import (
    initialize_date_session_state,
    render_date_picker,
    validate_and_show_date_range,
)


def format_date_for_title(start_date, end_date):
    """Format ngày cho title"""
    start_str = start_date.strftime("%d/%m/%Y")
    end_str = end_date.strftime("%d/%m/%Y")

    if start_date == end_date:
        return f"📝 Worklog - {start_str}"
    else:
        return f"📝 Worklog - {start_str} → {end_str}"


def load_worklog_data(start_date, end_date):
    """Load worklog data với caching - CHỈ load data, KHÔNG hiển thị"""
    # Tạo cache key từ dates
    cache_key = f"worklog_data_{start_date}_{end_date}"

    # Kiểm tra xem data đã có trong session state chưa
    if cache_key in st.session_state:
        # Data đã có cache, return ngay không cần API call
        return st.session_state[cache_key], True  # True = from cache

    # Chỉ call API khi chưa có cache
    worklog_service = WorklogService()

    with st.spinner("Đang tìm kiếm worklog..."):
        try:
            # Chuyển đổi datetime.date thành datetime.datetime để tránh lỗi so sánh
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())

            # Lấy dữ liệu worklog từ API
            worklog_data = worklog_service.get_issues_with_worklog_in_period(
                start_datetime, end_datetime
            )

            # Cache data vào session state
            st.session_state[cache_key] = worklog_data

            return worklog_data, False  # False = from API

        except Exception as e:
            st.error(f"❌ Lỗi khi tìm kiếm worklog: {str(e)}")
            return [], False


def display_worklog_results(
    worklog_data, from_cache=False, start_date=None, end_date=None
):
    """Hiển thị kết quả worklog với indicator cache"""
    # Hiển thị indicator cache status
    if from_cache:
        st.toast("⚡ Dữ liệu được load từ cache (không query API)")
    else:
        st.toast("🔄 Dữ liệu mới được load từ Jira API")

    # Hiển thị summary metrics
    display_worklog_summary(worklog_data)

    # Hiển thị kết quả chi tiết với filter và dates cho export
    display_worklog_data(worklog_data, start_date, end_date)


def render_worklog_interface():
    """Render giao diện worklog"""
    # Initialize session state
    initialize_date_session_state()

    # Tạo placeholder cho title
    title_placeholder = st.empty()

    # Render date inputs
    start_date, end_date = render_date_picker()

    # Cập nhật title trong placeholder
    title = format_date_for_title(start_date, end_date)
    title_placeholder.title(title)

    # Validation and display
    is_valid = validate_and_show_date_range(start_date, end_date)

    # Early return nếu ngày không hợp lệ
    if not is_valid:
        return

    # KIỂM TRA VÀ RESET FILTER KHI DATE RANGE THAY ĐỔI
    current_date_range = f"{start_date}_{end_date}"
    last_date_range_key = "last_worklog_date_range"
    user_filter_key = "worklog_user_filter"

    # Kiểm tra nếu date range đã thay đổi
    if last_date_range_key in st.session_state:
        if st.session_state[last_date_range_key] != current_date_range:
            # Date range đã thay đổi -> Reset filter
            if user_filter_key in st.session_state:
                del st.session_state[user_filter_key]

    # Lưu date range hiện tại
    st.session_state[last_date_range_key] = current_date_range

    # TÁCH BIỆT: Load data và hiển thị data
    # Load data chỉ phụ thuộc vào date, KHÔNG phụ thuộc vào UI filters
    worklog_data, from_cache = load_worklog_data(start_date, end_date)

    # Hiển thị results với cache indicator và dates cho export
    display_worklog_results(worklog_data, from_cache, start_date, end_date)


def clear_worklog_cache():
    """Xóa cache worklog data và reset filters"""
    # Xóa cache data
    keys_to_remove = [
        key for key in st.session_state.keys() 
        if isinstance(key, str) and key.startswith("worklog_data_")
    ]
    for key in keys_to_remove:
        del st.session_state[key]

    # Reset user filter
    user_filter_key = "worklog_user_filter"
    if user_filter_key in st.session_state:
        del st.session_state[user_filter_key]

    # Reset date range tracking
    last_date_range_key = "last_worklog_date_range"
    if last_date_range_key in st.session_state:
        del st.session_state[last_date_range_key]

    st.success("🗑️ Đã xóa cache worklog và reset tất cả filters")


def main():
    """Hàm chính của trang Worklog"""
    # Setup
    jira = get_jira_client()
    st.set_page_config(page_title="Worklog", page_icon="📝", layout="wide")

    # Sidebar với debug info
    with st.sidebar:
        # Button clear cache
        if st.button("🗑️ Xóa Cache Worklog", help="Xóa cache và reset tất cả filters"):
            clear_worklog_cache()

        # Cache data info
        cache_keys = [
            key for key in st.session_state.keys() 
            if isinstance(key, str) and key.startswith("worklog_data_")
        ]
        if cache_keys:
            st.write(f"📦 **Cache data:** {len(cache_keys)} entries")
            for key in cache_keys:
                st.text(f"• {key[13:]}")
        else:
            st.write("📭 **Không có cache data**")

    # Render worklog interface (title sẽ được set bên trong)
    render_worklog_interface()


if __name__ == "__main__":
    main()
