"""Component hiển thị worklog data - Refactored version"""

import streamlit as st
import pandas as pd
from datetime import datetime
from component.worklog import display_worklog_table, display_worklog_statistics
from service.utils.time_utils import seconds_to_hours


def _prepare_worklog_data(worklog_data):
    """Chuẩn bị dữ liệu worklog cho hiển thị"""
    user_worklog_data = []

    for issue in worklog_data:
        for wl in issue["worklogs"]:
            worklog_date = datetime.strptime(wl["started"][:10], "%Y-%m-%d").strftime(
                "%d/%m/%Y"
            )
            worklog_time = wl["started"][11:16]  # Lấy giờ:phút

            user_worklog_data.append(
                {
                    "User": wl["author"],
                    "Date": worklog_date,
                    "Time": worklog_time,
                    "Issue Key": issue["key"],
                    "Issue Summary": issue["summary"],
                    "Status": issue["status"],
                    "Time Spent": wl["timeSpent"],
                    "Time (Hours)": seconds_to_hours(wl["timeSpentSeconds"]),
                    "Comment": wl.get("comment", ""),
                }
            )

    # Sắp xếp theo User, sau đó theo Date
    user_worklog_data.sort(key=lambda x: (x["User"], x["Date"]))
    return user_worklog_data


def _calculate_worklog_metrics(worklog_data):
    """Tính toán các metrics từ worklog data"""
    total_hours = 0
    total_worklogs = 0
    unique_users = set()
    unique_issues = set()

    for issue in worklog_data:
        unique_issues.add(issue["key"])
        for wl in issue["worklogs"]:
            total_hours += seconds_to_hours(wl["timeSpentSeconds"])
            total_worklogs += 1
            unique_users.add(wl["author"])

    return {
        "total_hours": total_hours,
        "total_worklogs": total_worklogs,
        "unique_users": len(unique_users),
        "unique_issues": len(unique_issues),
    }


def display_worklog_summary(worklog_data):
    """Hiển thị tổng quan worklog (có thể dùng cho dashboard)"""
    # Early return nếu không có dữ liệu
    if not worklog_data:
        return

    # Tính toán metrics
    metrics = _calculate_worklog_metrics(worklog_data)

    # Hiển thị metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Tổng giờ làm việc", f"{metrics['total_hours']:.1f}h")

    with col2:
        st.metric("Số worklog", metrics["total_worklogs"])

    with col3:
        st.metric("Số user", metrics["unique_users"])

    with col4:
        st.metric("Số issue", metrics["unique_issues"])


def display_worklog_data(worklog_data, start_date=None, end_date=None):
    """Hiển thị dữ liệu worklog theo user với export Excel"""
    # Early return nếu không có dữ liệu
    if not worklog_data:
        st.info("📭 Không có worklog nào trong khoảng thời gian đã chọn.")
        return

    # Chuẩn bị dữ liệu
    user_worklog_data = _prepare_worklog_data(worklog_data)

    # Hiển thị thống kê trước với dates cho export
    df_worklog = pd.DataFrame(user_worklog_data)

    # Format dates cho Excel filename
    start_date_str = start_date.strftime("%Y-%m-%d") if start_date else None
    end_date_str = end_date.strftime("%Y-%m-%d") if end_date else None

    display_worklog_statistics(df_worklog, start_date_str, end_date_str)

    # Hiển thị bảng worklog sau
    display_worklog_table(user_worklog_data)
