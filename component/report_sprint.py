import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from service.clients.jira.sprint_service import SprintService
from service.utils.cache_utils import file_cache
from conf import STATUS_ORDER


def render_cache_status(cache_info):
    """
    Hiển thị thông báo Cache Status

    Args:
        cache_info: Dictionary chứa thông tin cache
    """
    if cache_info and cache_info.get("from_cache") and cache_info.get("timestamp"):
        cache_time = cache_info["timestamp"]
        formatted_time = cache_time.strftime("%d/%m/%Y lúc %H:%M:%S")
        st.info(f"📦 **Dữ liệu từ cache** - Cập nhật lần cuối: {formatted_time}")
    elif cache_info and not cache_info.get("from_cache"):
        st.success("🔄 **Dữ liệu mới từ API** - Vừa được cập nhật")


def render_sprint_sidebar(jira_client, sprint_service: SprintService):
    """
    Render sidebar cho trang Sprint Report

    Args:
        jira_client: JIRA client instance
        sprint_service: Sprint service instance

    Returns:
        tuple: (selected_sprint_id, selected_sprint_name, use_cache)
    """
    all_sprints = []
    sprint_name_to_id = {}

    with st.sidebar:
        st.markdown("### 📊 Chọn Sprint")

        try:
            with st.spinner("Đang tải Sprints..."):
                all_sprints = jira_client.get_list_sprints()

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

    return selected_sprint_id, selected_sprint_name, use_cache, all_sprints


def render_chart_by_status(data_dict):
    """
    Render stacked horizontal bar chart theo status với màu sắc tùy chỉnh

    Args:
        data_dict: Dictionary với key là status và value là số lượng
        Ví dụ: {"Reopen":10,"To Do":31,"In Progress":19,"Wait for review":12,"Dev Done":75,"Test Done":32,"Deployed":21,"Done":3,"Close":3}
    """
    if not data_dict:
        st.warning("Không có dữ liệu để hiển thị chart")
        return

    # Lấy danh sách status theo thứ tự từ STATUS_ORDER
    status_names = []
    counts = []
    colors = []

    for status, count in data_dict.items():
        if count > 0:  # Chỉ hiển thị status có số lượng > 0
            status_names.append(status)
            counts.append(count)
            # Lấy màu từ STATUS_ORDER, nếu không có thì dùng màu mặc định
            color = STATUS_ORDER.get(status, {}).get("color", "#95a5a6")
            colors.append(color)

    if not status_names:
        st.warning("Không có dữ liệu để hiển thị chart")
        return

    # Tạo stacked horizontal bar chart với plotly
    fig = go.Figure()

    # Thêm từng status như một trace riêng biệt để tạo stacked bar
    for i, (status, count, color) in enumerate(zip(status_names, counts, colors)):
        fig.add_trace(
            go.Bar(
                x=[count],
                y=["Issues"],
                orientation="h",
                name=status,
                marker_color=color,
                text=f"{status}: {count}",
                textposition="inside",
                textfont=dict(size=10, color="white"),
                hovertemplate=f"<b>{status}</b><br>Số lượng: {count}<br>Tỷ lệ: {count/sum(counts)*100:.1f}%<extra></extra>",
            )
        )

    # Tùy chỉnh layout cho stacked horizontal bar chart
    fig.update_layout(
        title={
            "text": "Phân bố Issues theo Status",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 16, "color": "#2c3e50"},
        },
        xaxis_title="",
        yaxis_title="",
        xaxis=dict(tickfont=dict(size=10)),
        yaxis=dict(
            tickfont=dict(size=12),
            showticklabels=False,  # Ẩn nhãn trục Y vì chỉ có 1 thanh
        ),
        height=250,  # Tăng chiều cao cho chart
        showlegend=True,
        legend=dict(
            orientation="h",  # Nằm ngang
            yanchor="top",
            y=8,  # Đặt ở dưới chart
            xanchor="left",
            x=0,  # Căn trái
            font=dict(size=10),
        ),
        # margin=dict(l=50, r=50, t=80, b=120),  # Tăng margin dưới để hiển thị legend
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        barmode="stack",  # Chế độ xếp chồng
    )

    # Hiển thị chart trong streamlit
    st.plotly_chart(fig, use_container_width=True)


def render_pie_chart(
    data_dict, title: str = "Phân bố Issues theo Loại", show_legend: bool = False
):
    # Tạo pie chart cho phân bố issues theo loại
    if not data_dict:
        st.warning("Không có dữ liệu để hiển thị")
        return

    # Chuẩn bị dữ liệu cho pie chart
    labels = list(data_dict.keys())
    values = list(data_dict.values())

    # Tạo figure cho pie chart
    fig = go.Figure()

    fig.add_trace(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.4,  # Tạo donut chart
            textinfo="label+percent",
            textposition="inside",
            textfont=dict(size=12, color="white"),
            hovertemplate="<b>%{label}</b><br>Số lượng: %{value}<br>Tỷ lệ: %{percent}<extra></extra>",
            marker=dict(
                colors=[
                    "#3498db",
                    "#e74c3c",
                    "#f1c40f",
                    "#2ecc71",
                    "#9b59b6",
                    "#1abc9c",
                    "#e67e22",
                    "#34495e",
                ]
            ),
        )
    )

    # Tùy chỉnh layout cho pie chart
    fig.update_layout(
        title={
            "text": title,
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 16, "color": "#2c3e50"},
        },
        height=400,
        showlegend=show_legend,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02,
            font=dict(size=10),
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    # Hiển thị chart trong streamlit
    st.plotly_chart(fig, use_container_width=True)
