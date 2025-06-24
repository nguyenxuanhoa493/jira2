from jira import JIRA
from conf import JIRA_SERVER, JIRA_USER, JIRA_API_TOKEN


class JiraBase:
    """Class cơ bản để kết nối đến Jira API"""

    def __init__(self):
        self.jira = JIRA(server=JIRA_SERVER, basic_auth=(JIRA_USER, JIRA_API_TOKEN))
        self.server = JIRA_SERVER
        self.user = JIRA_USER
        self.api_token = JIRA_API_TOKEN
        self.company = (
            (
                JIRA_SERVER.split("//")[-1].split(".")[0]
                if "//" in JIRA_SERVER
                else JIRA_SERVER.split(".")[0]
            )
        ).upper()

    def get_project(self, project_key):
        """Lấy thông tin project theo key"""
        return self.jira.project(project_key)

    def get_board(self, project_key_or_id):
        """Lấy board của project"""
        return self.jira.boards(projectKeyOrID=project_key_or_id)
