from conf import DEFAULT_PROJECT
from service.base.hybrid_singleton import HybridSingletonBase, create_hybrid_getter
from .project_service import ProjectService
from .user_service import UserService
from .sprint_service import SprintService
from .worklog_service import WorklogService
import streamlit as st


class JiraHybridClient(HybridSingletonBase):
    """
    JIRA Client sử dụng Hybrid Singleton pattern
    Đảm bảo hiệu suất tối ưu với 3-layer optimization
    """

    def _initialize(self):
        """Initialize JIRA client - called by HybridSingletonBase"""
        print("🔧 Initializing JIRA Hybrid Client...")

        self.project_key = DEFAULT_PROJECT

        try:
            # Khởi tạo các service
            self.project_service = ProjectService(self.project_key)
            self.user_service = UserService()
            self.sprint_service = SprintService()
            self.worklog_service = WorklogService(self.project_key)

            # Thiết lập board_id cho sprint service
            if self.project_service.board_id:
                self.sprint_service.set_board_id(self.project_service.board_id)

            # Backward compatibility - expose properties từ project service
            self.project = self.project_service.project
            self.board_id = self.project_service.board_id
            self.users = self.user_service.users

            # Expose jira connection từ project service
            self.jira = self.project_service.jira
            self.server = self.project_service.server
            self.user = self.project_service.user
            self.api_token = self.project_service.api_token
            self.company = self.project_service.company

            self.is_connected = True
            print(f"✅ JIRA Hybrid Client initialized successfully!")

        except Exception as e:
            st.error(f"❌ Failed to initialize JIRA client: {str(e)}")
            self.is_connected = False

    # ===== PROJECT METHODS =====
    def get_project(self, project_key):
        """Lấy thông tin project theo key"""
        return self.project_service.get_project(project_key)

    def get_board(self, project_key_or_id):
        """Lấy board của project"""
        return self.project_service.get_board(project_key_or_id)

    def get_project_info(self):
        """Lấy thông tin chi tiết của project hiện tại"""
        return self.project_service.get_project_info()

    # ===== USER METHODS =====
    def get_list_users(self, limit=200):
        """Lấy danh sách user từ Jira Cloud"""
        return self.user_service.get_list_users(limit)

    def search_users(self):
        """Tìm kiếm user có thể assign cho project"""
        return self.user_service.search_users()

    # ===== SPRINT METHODS =====
    def get_list_sprints(self, state=None):
        """Lấy danh sách sprint của board hiện tại"""
        return self.sprint_service.get_list_sprints(state)

    # ===== WORKLOG METHODS =====
    def get_issues_with_worklog_in_period(self, start_date, end_date):
        """Lấy tất cả issue có worklog trong khoảng thời gian"""
        return self.worklog_service.get_issues_with_worklog_in_period(
            start_date, end_date
        )

    # ===== UTILITY METHODS =====
    def switch_project(self, project_key):
        """Chuyển đổi sang project khác"""
        self.project_key = project_key
        self.project_service.set_project_key(project_key)
        self.worklog_service.set_project_key(project_key)

        # Cập nhật board_id cho sprint service
        if self.project_service.board_id:
            self.sprint_service.set_board_id(self.project_service.board_id)

        # Cập nhật backward compatibility properties
        self.project = self.project_service.project
        self.board_id = self.project_service.board_id

    def get_data(self, project_key):
        """Backward compatibility method"""
        self.switch_project(project_key)

    def test_connection(self):
        """Test JIRA connection"""
        if not self.is_connected:
            return False, "JIRA client is not initialized"

        try:
            # Test by getting project info
            project_info = self.get_project_info()
            if project_info:
                return (
                    True,
                    f"JIRA connection successful - Project: {project_info['name']}",
                )
            else:
                return False, "Failed to get project information"
        except Exception as e:
            return False, f"JIRA connection failed: {str(e)}"


# ===== HYBRID GETTER FUNCTIONS =====

# Create hybrid getter functions
get_jira_hybrid_client = create_hybrid_getter(
    client_class=JiraHybridClient,
    cache_key="jira_hybrid_client",
    session_key="jira_hybrid_session",
)

# Alternative getter without session state (lighter)
get_jira_hybrid_client_lite = create_hybrid_getter(
    client_class=JiraHybridClient, cache_key="jira_hybrid_client_lite", session_key=None
)


# ===== BACKWARD COMPATIBILITY =====

# Keep original JiraClient for backward compatibility
JiraClient = JiraHybridClient


def get_jira_client() -> JiraHybridClient:
    """
    Backward compatibility function - now uses HybridSingleton
    Provides 3-layer optimization automatically
    """
    return get_jira_hybrid_client()


# Utility functions
def get_jira_hybrid_info():
    """Get JIRA hybrid client information"""
    return JiraHybridClient.get_instance_info()


def reset_jira_hybrid():
    """Reset JIRA hybrid client"""
    JiraHybridClient.reset_instance()
    st.cache_resource.clear()

    # Clear session state
    keys_to_remove = [k for k in st.session_state.keys() if "jira_hybrid" in k]
    for key in keys_to_remove:
        del st.session_state[key]

    st.success("🔄 JIRA Hybrid Client has been reset!")
