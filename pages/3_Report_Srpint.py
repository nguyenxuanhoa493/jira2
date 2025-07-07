import streamlit as st
from service.clients.jira.jira_client import get_jira_client
from service.clients.jira.sprint_service import SprintService
from component.dataframe import show_dataframe_with_filters
from component.report_sprint import (
    render_sprint_sidebar,
    render_cache_status,
    render_chart_by_status,
    render_pie_chart,
)

# --- Page Config ---
st.set_page_config(page_title="Báo cáo Sprint", page_icon="📈", layout="wide")


# --- Main ---
def main():
    """Hàm chính của trang Báo cáo Sprint"""
    # --- Services ---
    jira = get_jira_client()
    sprint_service = SprintService()

    # --- Sidebar: Sprint Selection & Cache Controls ---
    selected_sprint_id, selected_sprint_name, use_cache, all_sprints = (
        render_sprint_sidebar(jira, sprint_service)
    )

    # --- Main Page Title ---
    st.title(f"📈 Báo cáo: {selected_sprint_name}")
    # --- Main Page Content ---
    try:
        # Get details of the selected sprint
        selected_sprint_details = next(
            sprint for sprint in all_sprints if sprint["id"] == selected_sprint_id
        )
        sprint_service.set_data_sprint(selected_sprint_details)

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
        render_cache_status(cache_info)
        is_get_only_active = st.toggle("Chỉ lấy issues active", value=False)
        is_get_only_active = "active" if is_get_only_active else "all"

        # --- Calculations ---
        total_issues = len(sprint_issues)

        st.divider()

        # --- Display Issues Table ---
        st.subheader("Chi tiết các Issues trong Sprint")
        metric_sprint = sprint_service.get_metric_sprint()
        render_chart_by_status(metric_sprint["metric_by_status"][is_get_only_active])

        col1, col2, col3 = st.columns(3)
        with col1:
            render_pie_chart(
                metric_sprint["metric_by_type"][is_get_only_active],
                title="Phân bố Issues theo Loại",
            )
        with col2:
            render_pie_chart(
                metric_sprint["metric_by_priority"][is_get_only_active],
                title="Phân bố Issues theo Độ ưu tiên",
            )
        with col3:
            render_pie_chart(
                metric_sprint["metric_by_feature"][is_get_only_active],
                title="Phân bố Issues theo Feature",
            )
        st.write(metric_sprint)

        show_dataframe_with_filters(
            sprint_service.list_issues, columns=["assignee", "summary"]
        )

    except Exception as e:
        st.error(f"❌ Lỗi khi tải dữ liệu cho Sprint '{selected_sprint_name}': {e}")
        st.stop()


if __name__ == "__main__":
    main()
