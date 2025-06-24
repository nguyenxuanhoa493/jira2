import streamlit as st
from service.clients.jira.jira_client import get_jira_client
from conf import DEFAULT_PROJECT

jira = get_jira_client()

st.set_page_config(
    page_title="Jira Dashboard",
    page_icon="🏠",
    layout="wide",  # Full độ rộng
    initial_sidebar_state="expanded",
)
st.write(jira.test_connection())
# st.write(
#     jira.jira.get(sprint_id=408, board_id=jira.default_board_id)
# )  # Hiển thị trạng thái kết nối và tên dự án mặc định ở dưới cùng sidebar
