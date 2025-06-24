from conf import DEFAULT_PROJECT
from service.base.jira_base import JiraBase


class ProjectService(JiraBase):
    """Service quản lý project trong Jira"""

    def __init__(self, project_key=None):
        super().__init__()
        self.project_key = project_key or DEFAULT_PROJECT
        self.project = None
        self.board_id = None
        self._initialize_project()

    def _initialize_project(self):
        """Khởi tạo thông tin project và board"""
        try:
            self.project = self.get_project(self.project_key)
            boards = self.get_board(self.project_key)
            if boards:
                self.board_id = boards[0].id
        except Exception as e:
            print(f"Lỗi khi khởi tạo project: {e}")

    def set_project_key(self, project_key):
        """Thiết lập project_key mới và khởi tạo lại"""
        self.project_key = project_key
        self._initialize_project()

    def get_project_info(self):
        """Lấy thông tin chi tiết của project"""
        if not self.project:
            return None

        # Safe way to get lead display name from JIRA User object
        lead_name = ""
        try:
            if hasattr(self.project, "lead") and self.project.lead:
                # JIRA User object has displayName attribute, not dictionary access
                lead_name = getattr(self.project.lead, "displayName", "")
        except Exception as e:
            print(f"Warning: Could not get project lead info: {e}")
            lead_name = "Unknown"

        return {
            "key": self.project.key,
            "name": self.project.name,
            "description": getattr(self.project, "description", ""),
            "lead": lead_name,
            "board_id": self.board_id,
        }

    def get_project_boards(self):
        """Lấy tất cả board của project"""
        return self.get_board(self.project_key)
