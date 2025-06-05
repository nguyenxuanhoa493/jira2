from service.base.jira_base import JiraBase


class SprintService(JiraBase):
    """Service quản lý sprint trong Jira"""

    def __init__(self, board_id=None):
        super().__init__()
        self.board_id = board_id

    def set_board_id(self, board_id):
        """Thiết lập board_id cho service"""
        self.board_id = board_id

    def get_list_sprints(self, state=None, sort_by_state=True):
        """
        Lấy danh sách sprint của 1 board.
        state: 'active', 'future', 'closed' hoặc None
        """
        if not self.board_id:
            raise ValueError("Board ID chưa được thiết lập")

        params = {}
        if state:
            params["state"] = state
        list_sprint = self.jira._get_json(
            f"board/{self.board_id}/sprint",
            params,
            base=self.jira.AGILE_BASE_URL,
        ).get("values", [])

        filtered_sprints = [
            sprint
            for sprint in list_sprint
            if sprint.get("originBoardId") == self.board_id
        ][::-1]

        # Sắp xếp theo thứ tự state: active, future, closed
        state_order = {"active": 0, "future": 1, "closed": 2}

        def sort_key(sprint):
            sprint_state = sprint.get("state", "").lower()
            return state_order.get(sprint_state, 3)  # Các state khác sẽ được đặt cuối

        return (
            sorted(filtered_sprints, key=sort_key)
            if sort_by_state
            else filtered_sprints
        )
