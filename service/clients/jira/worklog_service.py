from datetime import datetime
from conf import DEFAULT_PROJECT
from service.base.jira_base import JiraBase


class WorklogService(JiraBase):
    """Service quản lý worklog trong Jira"""

    def __init__(self, project_key=None):
        super().__init__()
        self.project_key = project_key or DEFAULT_PROJECT

    def set_project_key(self, project_key):
        """Thiết lập project_key cho service"""
        self.project_key = project_key

    def get_issues_with_worklog_in_period(self, start_date, end_date):
        """
        Lấy tất cả issue có worklog trong khoảng thời gian từ start_date đến end_date

        Args:
            start_date (str hoặc datetime): Ngày bắt đầu (format: 'YYYY-MM-DD' hoặc datetime object)
            end_date (str hoặc datetime): Ngày kết thúc (format: 'YYYY-MM-DD' hoặc datetime object)

        Returns:
            list: Danh sách issue có worklog trong khoảng thời gian
        """
        # Chuyển đổi string thành datetime nếu cần
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # Format ngày cho JQL query
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        # JQL query để tìm issue có worklog trong khoảng thời gian
        jql_query = f'project = "{self.project_key}" AND worklogDate >= "{start_date_str}" AND worklogDate <= "{end_date_str}"'
        # print(jql_query)
        try:
            # Xử lý phân trang để lấy tất cả issue
            all_issues = []
            start_at = 0
            while True:
                issues = self.jira.search_issues(
                    jql_query,
                    startAt=start_at,
                    maxResults=100,  # Lấy 100 issue mỗi lần để phân trang
                    expand="worklog",  # Mở rộng để lấy thông tin worklog
                )
                if not issues:
                    break  # Dừng nếu không còn issue
                all_issues.extend(issues)
                start_at += len(issues)
                if len(issues) < 100:
                    break  # Đã lấy trang cuối cùng

            result = []
            for issue in all_issues:
                issue_data = {
                    "key": issue.key,
                    "summary": issue.fields.summary,
                    "status": issue.fields.status.name,
                    "assignee": (
                        issue.fields.assignee.displayName
                        if issue.fields.assignee
                        else None
                    ),
                    "worklog_count": len(issue.fields.worklog.worklogs),
                    "worklogs": [],
                }

                # Lọc worklog trong khoảng thời gian
                for worklog in issue.fields.worklog.worklogs:
                    worklog_date = datetime.strptime(worklog.started[:10], "%Y-%m-%d")
                    if start_date <= worklog_date <= end_date:
                        worklog_data = {
                            "id": worklog.id,
                            "author": worklog.author.displayName,
                            "started": worklog.started,
                            "timeSpent": worklog.timeSpent,
                            "timeSpentSeconds": worklog.timeSpentSeconds,
                            "comment": getattr(worklog, "comment", ""),
                        }
                        issue_data["worklogs"].append(worklog_data)

                # Chỉ thêm issue nếu có worklog trong khoảng thời gian
                if issue_data["worklogs"]:
                    result.append(issue_data)

            return result

        except Exception as e:
            print(f"Lỗi khi lấy issue có worklog: {e}")
            return []
