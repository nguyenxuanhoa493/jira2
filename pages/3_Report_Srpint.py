import streamlit as st
from service.clients.jira.jira_client import get_jira_client
from service.clients.jira.sprint_service import SprintService
from service.utils.date_utils import adjust_sprint_dates
from service.utils.cache_utils import file_cache
import pandas as pd
from conf import DEFAULT_PROJECT

# --- Page Config ---
st.set_page_config(page_title="Báo cáo Sprint", page_icon="📈", layout="wide")


# --- Main ---
def main():
    """Hàm chính của trang Báo cáo Sprint"""
    # --- Services ---
    jira = get_jira_client()
    sprint_service = SprintService()
    all_sprints = []
    sprint_name_to_id = {}

    # --- Sidebar: Sprint Selection & Cache Controls ---
    with st.sidebar:
        st.markdown("### 📊 Chọn Sprint")

        try:
            with st.spinner("Đang tải Sprints..."):
                all_sprints = jira.get_list_sprints()

            if not all_sprints:
                st.error("Không tìm thấy Sprint nào cho Board này.")
                st.stop()

            # Find the active sprint to set as default
            active_sprint_index = 0

            # Create a dictionary for easy lookup: {sprint_name: sprint_id}
            sprint_name_to_id = {sprint["name"]: sprint["id"] for sprint in all_sprints}

            # Display the sprint selector in the sidebar
            selected_sprint_name = st.selectbox(
                "Chọn Sprint:",
                options=sprint_name_to_id.keys(),
                index=active_sprint_index,
                help="Sprint 'active' được chọn mặc định nếu có.",
            )

            selected_sprint_id = sprint_name_to_id[selected_sprint_name]

        except Exception as e:
            st.error(f"❌ Lỗi khi tải danh sách Sprint: {e}")
            st.stop()

        # --- Cache Controls ---
        st.markdown("### 💾 Quản lý Cache")

        # Cache settings
        use_cache = st.toggle(
            "Sử dụng cache",
            value=True,
            help="Cache persistent - chỉ update khi user thao tác",
        )

        # Cache info
        cache_info = file_cache.get_cache_info()
        if cache_info:
            st.write(f"📁 **Cache files:** {cache_info.get('total_files', 0)}")
            st.write(f"💽 **Total size:** {cache_info.get('total_size_mb', 0)} MB")
        else:
            st.write("📁 **Cache files:** 0")
            st.write("💽 **Total size:** 0 MB")

        # Nút xóa cache cho sprint hiện tại
        cache_key_current = (
            f"cache_issues_sprint_{sprint_service.board_id}_{selected_sprint_id}"
        )
        cached_data_current = file_cache.load_cache(cache_key_current)

        if cached_data_current:
            if st.button(
                f"🗑️ Xóa Cache Sprint này",
                help=f"Xóa cache cho sprint hiện tại ({len(cached_data_current)} issues)",
                use_container_width=True,
            ):
                sprint_service.clear_sprint_cache(selected_sprint_id)
                st.success("✅ Cache sprint đã được xóa!")
                st.rerun()
        else:
            st.info("📭 Sprint hiện tại chưa có cache")

        # Xóa tất cả cache
        if st.button(
            "🗑️ Xóa Tất Cả Cache",
            help="Xóa toàn bộ cache files",
            use_container_width=True,
        ):
            file_cache.clear_cache()
            st.success("✅ Tất cả cache đã được xóa!")
            st.rerun()

    # --- Main Page Title ---
    st.title(f"📈 Báo cáo: {selected_sprint_name}")

    # --- Main Page Content ---
    try:
        # Get details of the selected sprint
        selected_sprint_details = next(
            sprint for sprint in all_sprints if sprint["id"] == selected_sprint_id
        )

        # Fetch and display issues với cache
        start_date_str = selected_sprint_details.get("startDate", "N/A")
        end_date_str = selected_sprint_details.get("endDate", "N/A")
        adj_start, adj_end = adjust_sprint_dates(start_date_str, end_date_str)
        sprint_service.set_time_range(adj_start, adj_end)

        # Load issues với cache control và lấy cache info
        result = sprint_service.get_issues_for_sprint(
            selected_sprint_id, use_cache=use_cache, return_cache_info=True
        )

        if isinstance(result, tuple):
            sprint_issues, cache_info = result
        else:
            sprint_issues = result
            cache_info = {"from_cache": False, "timestamp": None}

        # Ensure sprint_issues is a list
        if sprint_issues is None:
            sprint_issues = []

        # --- Thông báo Cache Status ---
        if cache_info and cache_info.get("from_cache") and cache_info.get("timestamp"):
            cache_time = cache_info["timestamp"]
            formatted_time = cache_time.strftime("%d/%m/%Y lúc %H:%M:%S")
            st.info(f"📦 **Dữ liệu từ cache** - Cập nhật lần cuối: {formatted_time}")
        elif cache_info and not cache_info.get("from_cache"):
            st.success("🔄 **Dữ liệu mới từ API** - Vừa được cập nhật")

        # --- Calculations ---
        total_issues = len(sprint_issues)

        # Display sprint info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📋 Total Issues", total_issues)
        with col2:
            active_issues = len(
                [
                    issue
                    for issue in sprint_issues
                    if issue and issue.get("active_in_sprint", False)
                ]
            )
            st.metric("🔥 Active Issues", active_issues)
        with col3:
            total_points = sum(
                issue.get("points", 0) for issue in sprint_issues if issue
            )
            st.metric("⭐ Total Points", f"{total_points:.1f}h")

        # Display sprint dates
        st.caption(
            f"**Thời gian Sprint:** {adj_start.strftime('%d/%m/%Y')} → {adj_end.strftime('%d/%m/%Y')}"
        )

        st.divider()

        # --- Display Issues Table ---
        st.subheader("Chi tiết các Issues trong Sprint")
        list_issues_active_in_sprint = sprint_service.get_issue_active_in_sprint()

        if not list_issues_active_in_sprint.empty:
            st.dataframe(sprint_service.list_issues, use_container_width=True)
        else:
            st.info("Không có issues active trong sprint này.")

    except Exception as e:
        st.error(f"❌ Lỗi khi tải dữ liệu cho Sprint '{selected_sprint_name}': {e}")
        st.stop()


if __name__ == "__main__":
    main()
