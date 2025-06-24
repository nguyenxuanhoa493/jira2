"""Component hiển thị bảng worklog chi tiết"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
from service.utils.time_utils import seconds_to_hours
from .worklog_utils import _get_user_avatar, _break_long_text, _truncate_comment


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
                    "Comment": _truncate_comment(wl["comment"]),
                }
            )

    # Sắp xếp theo User, sau đó theo Date
    user_worklog_data.sort(key=lambda x: (x["User"], x["Date"]))
    return user_worklog_data


def _display_user_header(user, user_data):
    """Hiển thị header với avatar và thông tin user - UI gọn"""
    # Tính tổng giờ cho user này
    total_hours = sum(item["Time (Hours)"] for item in user_data)
    unique_issues = len(set(item["Issue Key"] for item in user_data))

    # Lấy avatar
    avatar_url = _get_user_avatar(user)

    # Layout compact với nền xám
    with st.container():
        # Tạo một div với nền xám bao quanh toàn bộ header
        st.markdown(
            f"""
            <div style="
                background-color: #f0f2f6; 
                padding: 8px 12px; 
                border-radius: 4px; 
                margin-bottom: 8px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            ">
                <div style="display: flex; align-items: center;">
                    {'<img src="' + avatar_url + '" width="32" style="border-radius: 50%; margin-right: 8px;">' if avatar_url else '👤'} 
                    <strong>{user}</strong>
                </div>
                <div style="font-weight: 600;">
                    {len(user_data)} worklog | {total_hours:.1f}h | {unique_issues} issues
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _display_user_filter(all_users, user_groups):
    """Hiển thị bộ lọc user với avatar và thống kê"""
    # Initialize filter session state key
    filter_key = "worklog_user_filter"

    # Tạo options với avatar và số liệu thống kê cho từng user
    user_options = []
    user_mapping = {}  # Để map từ formatted option về user name

    for user in all_users:
        # Lấy avatar
        avatar_url = _get_user_avatar(user)

        # Tính toán metrics cho user này
        user_data = user_groups[user]
        total_hours = sum(item["Time (Hours)"] for item in user_data)
        worklog_count = len(user_data)

        # Format với avatar và metrics
        if avatar_url:
            formatted = f"👤 {user} ({worklog_count} logs, {total_hours:.1f}h)"
        else:
            formatted = f"👤 {user} ({worklog_count} logs, {total_hours:.1f}h)"

        user_options.append(formatted)
        user_mapping[formatted] = user

    # Container cho filter với styling đẹp
    with st.container():
        # Multiselect dropdown với session state
        selected_formatted = st.multiselect(
            "🔍 **Lọc theo User:**",
            options=user_options,
            default=st.session_state.get(filter_key, []),  # Load từ session state
            help="💡 **Để trống** = hiển thị tất cả users | **Chọn cụ thể** = chỉ hiển thị users được chọn",
            placeholder="🎯 Chọn users cần xem hoặc để trống để hiển thị tất cả",
            key=filter_key,  # Bind to session state
        )

    # Convert formatted options back to user names
    if selected_formatted:
        # Có chọn cụ thể -> chỉ hiển thị users được chọn
        selected_users = [user_mapping[formatted] for formatted in selected_formatted]
    else:
        # Không chọn gì -> hiển thị tất cả
        selected_users = all_users

    return selected_users


def display_worklog_table(user_worklog_data):
    """Hiển thị bảng worklog theo user - mỗi user một bảng"""

    # CSS để force text wrap trong dataframe
    st.markdown(
        """
    <style>
    .stDataFrame [data-testid="stDataFrameResizeHandle"] {
        display: none;
    }
    .stDataFrame td {
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
        max-width: 300px !important;
        vertical-align: top !important;
    }
    .stDataFrame th {
        white-space: nowrap !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Group data theo user từ data có sẵn (KHÔNG call API)
    user_groups = {}
    for item in user_worklog_data:
        user = item["User"]
        if user not in user_groups:
            user_groups[user] = []
        user_groups[user].append(item)

    # Lấy danh sách tất cả users từ data đã load
    all_users = list(user_groups.keys())

    # Header và bộ lọc trên cùng một hàng
    col1, col2, col3 = st.columns([2, 2, 2])

    with col1:
        st.subheader("👥 Danh sách Worklog theo User")

    with col2:
        # Bộ lọc user với avatar - CHỈ ẨN/HIỆN bảng, KHÔNG render lại data
        if len(all_users) > 1:  # Chỉ hiển thị filter nếu có nhiều hơn 1 user
            selected_users = _display_user_filter(all_users, user_groups)
        else:
            selected_users = all_users

    with col3:
        # Info export Excel - updated for new UX
        st.info("💡 **📥 Xuất Excel** ở phần Thống kê sẽ tải trực tiếp")

    # Hiển thị bảng cho từng user (CHỈ users được chọn)
    # Data đã có sẵn, chỉ quyết định hiển thị hay skip
    for user, user_data in user_groups.items():
        if user not in selected_users:
            continue  # CHỈ SKIP hiển thị, data vẫn còn nguyên

        # Hiển thị header với avatar và thông tin
        _display_user_header(user, user_data)

        # Tạo DataFrame cho user này từ data có sẵn
        user_df_data = []
        for idx, item in enumerate(user_data, 1):  # Bắt đầu từ 1
            # Tạo URL từ issue key
            issue_key = item["Issue Key"]
            issue_url = f"https://vieted.atlassian.net/browse/{issue_key}"

            # Break long text
            issue_summary = _break_long_text(item["Issue Summary"], 40)
            comment = _break_long_text(item["Comment"], 50)

            user_df_data.append(
                {
                    "STT": idx,
                    "Date": item["Date"],
                    "Time": item["Time"],
                    "Issue Key": issue_url,  # Store URL nhưng sẽ display issue key
                    "Issue Summary": issue_summary,
                    "Time (Hours)": item["Time (Hours)"],
                    "Comment": comment,
                }
            )

        df_user = pd.DataFrame(user_df_data)
        st.dataframe(
            df_user,
            use_container_width=True,
            hide_index=True,  # Ẩn cột index đầu tiên
            column_config={
                "STT": st.column_config.NumberColumn(
                    "STT", help="Số thứ tự", width="small"
                ),
                "Date": st.column_config.Column("Date", width="small"),
                "Time": st.column_config.Column("Time", width="small"),
                "Issue Key": st.column_config.LinkColumn(
                    "Issue Key",
                    help="Click để mở issue trong Jira",
                    display_text=r"https://vieted\.atlassian\.net/browse/(.+)",
                    width="small",
                ),
                "Issue Summary": st.column_config.TextColumn(
                    "Issue Summary", width="large"
                ),
                "Time (Hours)": st.column_config.NumberColumn(
                    "Time (Hours)", width="small", format="%.2f"
                ),
                "Comment": st.column_config.TextColumn("Comment", width="large"),
            },
        )
