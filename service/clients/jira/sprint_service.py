from re import T

from narwhals import dataframe
from service.base.jira_base import JiraBase
import streamlit as st
import pandas as pd
from conf import DEFAULT_FIELDS_ISSUE, KEY_ISSUE_DEBUG, DEFAULT_MAX_ISSUE_PER_PAGE
from service.utils.time_utils import (
    cal_hours_since_update,
    convert_time_str_to_datetime,
    convert_seconds_to_jira_time,
)
from service.clients.jira.worklog_service import WorklogService
from service.utils.date_utils import parse_jira_datetime
from service.utils.cache_utils import file_cache
from typing import Optional
from datetime import datetime


class SprintService(JiraBase):
    start_date = None
    end_date = None

    """Service quản lý sprint trong Jira"""

    def __init__(self, board_id=None):
        super().__init__()
        self.board_id = board_id

    def set_board_id(self, board_id):
        """Thiết lập board_id cho service"""
        self.board_id = board_id

    def set_time_range(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def get_list_sprints(self, state: str = "", sort_by_state: bool = True):
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

        for idx, sprint in enumerate(filtered_sprints):
            filtered_sprints[idx][
                "name"
            ] = f"{sprint['name']} - {sprint['state'].upper()}"

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

    def get_issues_for_sprint(
        self,
        sprint_id: int,
        fields: list = DEFAULT_FIELDS_ISSUE,
        max_results: int = DEFAULT_MAX_ISSUE_PER_PAGE,
        use_cache: bool = True,
        return_cache_info: bool = False,
    ):
        """
        Lấy issues cho sprint với file cache (persistent - không expire tự động)

        Args:
            sprint_id: ID của sprint
            fields: List các field cần lấy
            max_results: Số lượng tối đa mỗi page
            use_cache: Có sử dụng cache không
            return_cache_info: Có trả về thông tin cache không

        Returns:
            issues list hoặc tuple (issues, cache_info) nếu return_cache_info=True
        """
        if not sprint_id:
            raise ValueError("Sprint ID is required")

        # Tạo cache key theo yêu cầu: cache_issues_sprint + board_id
        cache_key = f"cache_issues_sprint_{self.board_id}_{sprint_id}"
        cache_info = {"from_cache": False, "timestamp": None}

        # Kiểm tra cache trước nếu use_cache = True
        if use_cache:
            cached_issues, cache_metadata = file_cache.load_cache_with_metadata(
                cache_key
            )
            if cached_issues is not None:
                st.toast("⚡ Sprint issues loaded từ file cache")
                self.list_issues = pd.DataFrame(cached_issues)
                cache_info = {
                    "from_cache": True,
                    "timestamp": (
                        cache_metadata.get("timestamp") if cache_metadata else None
                    ),
                }

                if return_cache_info:
                    return cached_issues, cache_info
                return cached_issues

        # Nếu không có cache hoặc user chọn không dùng cache, call API
        with st.spinner(f"🔄 Đang load issues cho sprint {sprint_id}..."):
            all_issues = []
            start_at = 0
            while True:
                params = {
                    "fields": ",".join(fields),
                    "maxResults": max_results,
                    "startAt": start_at,
                    "expand": "changelog",
                }

                # Sử dụng endpoint chính tắc để lấy issue từ sprint
                response = self.jira._get_json(
                    f"sprint/{sprint_id}/issue",
                    params,
                    base=self.jira.AGILE_BASE_URL,
                )
                issues_on_page = response.get("issues", [])
                if not issues_on_page:
                    break

                all_issues.extend(issues_on_page)

                total = response.get("total", 0)
                # break  # Only get one page
                if len(all_issues) >= total:
                    break

                start_at += len(issues_on_page)

            # Xử lý và thêm "points" vào mỗi issue
            all_issues = [self._process_issue(issue) for issue in all_issues]

            # Cache kết quả nếu use_cache = True
            if use_cache and all_issues:
                file_cache.save_cache(cache_key, all_issues)
                st.toast(f"💾 Sprint issues đã được cache ({len(all_issues)} issues)")

        self.list_issues = pd.DataFrame(all_issues)

        if return_cache_info:
            return all_issues, cache_info
        return all_issues

    def clear_sprint_cache(self, sprint_id: int = 0):
        """
        Xóa cache cho sprint cụ thể hoặc tất cả sprint của board

        Args:
            sprint_id: ID sprint cần xóa cache, None để xóa tất cả
        """
        if sprint_id:
            cache_key = f"cache_issues_sprint_{self.board_id}_{sprint_id}"
            file_cache.clear_cache(cache_key)
            st.success(f"🗑️ Đã xóa cache cho sprint {sprint_id}")
        else:
            # Xóa tất cả cache sprint của board này
            # Vì file_cache không support pattern matching,
            # chúng ta sẽ chỉ clear toàn bộ cache
            file_cache.clear_cache()
            st.success(f"🗑️ Đã xóa tất cả cache")

    def get_cache_info(self):
        """Lấy thông tin cache hiện tại"""
        return file_cache.get_cache_info()

    def cal_report_metric(self, issues):
        return issues

    def get_issue_active_in_sprint(self):
        return self.list_issues[self.list_issues["active_in_sprint"]]

    def _process_issue(
        self,
        issue,
    ):
        """Xử lý dữ liệu cho một issue, ví dụ tính points."""
        worklog_service = WorklogService()
        # Đảm bảo issue có key 'fields'
        key = issue.get("key", "")
        # if key == "CLD-1060":

        #     st.write(key)
        #     st.write(issue)

        fields = issue.get("fields", {})
        summary = fields.get("summary", "")
        status = fields.get("status", {}).get("name", "")
        issuetype = fields.get("issuetype", {}).get("name", "")
        assignee = _get_field(fields, "assignee", "displayName")

        priority = fields.get("priority", {}).get("name", "")

        time_in_seconds = fields.get("timeoriginalestimate")
        points = round(time_in_seconds / 3600, 2) if time_in_seconds else 0.0
        tech = _get_field(data=fields, field_name="customfield_10192", key="value")
        is_development = _get_field(
            data=fields, field_name="customfield_10160", key="value", is_bool=True
        )
        is_popup = _get_field(
            data=fields, field_name="customfield_10130", key="value", is_bool=True
        )
        feature = _get_field(data=fields, field_name="customfield_10132", key="value")
        steve_estimate = _get_field(
            data=fields, field_name="customfield_10159", key="value"
        )
        customer = _get_field(data=fields, field_name="customfield_10092", key="value")
        has_subtasks = len(fields.get("subtasks", [])) > 0
        reporter = _get_field(data=fields, field_name="reporter", key="displayName")
        tester = _get_field(
            data=fields, field_name="customfield_10031", key="displayName"
        )
        env = _get_field(data=fields, field_name="customfield_10191", key="value")
        timetracking = fields.get("timetracking", {})
        remainingSeconds = timetracking.get(
            "originalEstimateSeconds", 0
        ) - timetracking.get("timeSpentSeconds", 0)
        remaining = convert_seconds_to_jira_time(remainingSeconds)
        duedate = convert_time_str_to_datetime(fields.get("duedate", ""))
        count_spinrt_closed = len(fields.get("closedSprints", []))
        updated_at = fields.get("updated", "")
        hours_since_update = cal_hours_since_update(updated_at)
        created_at = fields.get("created", "")
        worklogs = fields.get("worklog", {})
        worklog_list = worklogs.get("worklogs", [])
        # Lấy toàn bộ worklog cho issue nếu không đầy đủ
        if worklogs.get("total", 0) > len(worklog_list):
            st.toast(
                f"Lấy toàn bộ worklog cho issue {key} vì có {worklogs.get('total',0)} worklogs"
            )
            worklog_list = worklog_service.get_worklogs_by_issue_key(issue_key=key)

        # Kiểm tra và đảm bảo start_date và end_date không None trước khi gọi
        if self.start_date is None or self.end_date is None:
            st.error("start_date hoặc end_date không được None")
            return None

        data_worklog = worklog_service.calculate_worklog_data(
            worklog_list,
            start_date=self.start_date,
            end_date=self.end_date,
        )

        changelog = self._process_changelog(
            issue.get("changelog", {}).get("histories", [])
        )
        active_in_sprint = (
            True
            if (
                issuetype != "Epic"
                and data_worklog["time_spent_in_sprint_seconds"]
                and not has_subtasks
                and is_development
                and assignee
                and status != "Close"
            )
            else False
        )
        if key == KEY_ISSUE_DEBUG and KEY_ISSUE_DEBUG:
            st.write(issue)

        issue_processed = {
            "key": key,
            "summary": summary,
            "status": status,
            "issuetype": issuetype,
            "assignee": assignee,
            "reporter": reporter,
            "tester": tester,
            "priority": priority,
            "points": points,
            "steve_estimate": steve_estimate,
            "tech": tech,
            "env": env,
            "customer": customer,
            "is_development": is_development,
            "is_popup": is_popup,
            "feature": feature,
            "has_subtasks": has_subtasks,
            "active_in_sprint": active_in_sprint,
            "originalEstimate": timetracking.get("originalEstimate", "0h"),
            "timeSpent": timetracking.get("timeSpent", "0h"),
            "remaining": remaining,
            "remainingEstimate": timetracking.get("remainingEstimate", "0h"),
            "originalEstimateSeconds": timetracking.get("originalEstimateSeconds", 0),
            "timeSpentSeconds": timetracking.get("timeSpentSeconds", 0),
            "remainingEstimateSeconds": timetracking.get("remainingEstimateSeconds", 0),
            "remainingSeconds": remainingSeconds,
            "count_spinrt_closed": count_spinrt_closed,
            "created_at": created_at,
            "updated_at": updated_at,
            "hours_elapsed": hours_since_update.get("hours_elapsed", 0),
            "hours_elapsed_str": hours_since_update.get("hours_elapsed_str", "0h"),
            "date_elapsed": hours_since_update.get("date_elapsed", "0d 0h"),
            # Dữ liệu worklog mới
            "count_worklog": data_worklog["count_worklog"],
            "time_spent_in_sprint_hours": data_worklog["time_spent_in_sprint_hours"],
            "time_spent_in_sprint_seconds": data_worklog[
                "time_spent_in_sprint_seconds"
            ],
            "unique_loggers_count": data_worklog["unique_loggers_count"],
            "first_time_in_progress": changelog["first_time_in_progress"],
            "count_reopen": changelog["count_reopen"],
            "has_reopen": changelog["has_reopen"],
            "reopen_in_sprint": changelog["reopen_in_sprint"],
            "is_done_in_sprint": changelog["is_done_in_sprint"],
            "time_done_in_sprint": changelog["time_done_in_sprint"],
            "duration_hours_to_done": changelog["duration_hours_to_done"],
            "duration_date_to_done": changelog["duration_date_to_done"],
            "duedate": duedate,
        }
        return issue_processed

    def print_list_issues(self, data):
        data = data or self.list_issues
        st.write(data)

    def _process_changelog(self, histories: list):
        status_changes = []
        count_reopen = 0

        is_done_in_sprint = False
        first_time_in_progress = None
        time_done_in_sprint = None
        reopen_in_sprint = False

        # Sắp xếp lịch sử để đảm bảo xử lý đúng thứ tự thời gian
        histories.sort(key=lambda x: x.get("created", "s"))

        for history in histories:
            items = history.get("items", [])
            if len(items) == 1 and items[0].get("field") == "status":
                status_to = items[0].get("toString", "")
                status_from = items[0].get("fromString", "")
                time_change = convert_time_str_to_datetime(
                    history.get("created", "")
                )  # type: ignore
                author = history.get("author", {}).get("displayName", "")

                is_in_sprint = (
                    time_change is not None
                    and self.start_date is not None
                    and self.end_date is not None
                    and time_change >= self.start_date
                    and time_change <= self.end_date
                )

                if status_from == "Reopen":
                    count_reopen += 1
                    reopen_in_sprint = True if is_in_sprint else False

                if status_to == "Done" and is_in_sprint:
                    is_done_in_sprint = True
                    time_done_in_sprint = time_change

                status_changes.append(
                    {
                        "created": time_change,
                        "author": author,
                        "fromString": status_from,
                        "toString": status_to,
                    }
                )
        first_time_in_progress = (
            convert_time_str_to_datetime(status_changes[0]["created"])
            if status_changes
            else None
        )
        duration_hours_to_done = (
            (time_done_in_sprint - first_time_in_progress)
            if time_done_in_sprint and first_time_in_progress
            else None
        )
        duration_date_to_done = (
            round(duration_hours_to_done.total_seconds() / 3600 / 24, 2)
            if duration_hours_to_done
            else 0.0
        )

        return {
            "first_time_in_progress": first_time_in_progress,
            "count_reopen": count_reopen,
            "has_reopen": count_reopen > 0,
            "histories": status_changes,
            "is_done_in_sprint": is_done_in_sprint,
            "time_done_in_sprint": time_done_in_sprint,
            "duration_hours_to_done": duration_hours_to_done,
            "duration_date_to_done": duration_date_to_done,
            "reopen_in_sprint": reopen_in_sprint,
        }


def _get_field(data: dict, field_name: str, key: str = "value", is_bool: bool = False):
    data_field = data.get(field_name, {})
    if data_field:

        vaule_field = (
            data_field[0].get(key, "")
            if isinstance(data_field, list)
            else data_field.get(key, "")
        )
    else:
        vaule_field = ""
    if is_bool:
        return True if (vaule_field and vaule_field == "YES") else False
    return vaule_field
