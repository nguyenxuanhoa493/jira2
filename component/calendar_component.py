"""
Calendar Component - UI components cho calendar (Refactored version)
"""

import streamlit as st
import calendar
import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Optional

from service.time_off_service import TimeOffService
from service.get_client import get_jira
from service.data_export_service import DataExportService
from component.user_avatar_helper import UserAvatarHelper
from component.calendar_styles import CalendarStyles


class CalendarComponent:
    """Component quản lý UI của Calendar"""

    def __init__(self):
        self.time_off_service = TimeOffService()
        self.jira = get_jira()
        self.user_helper = UserAvatarHelper(self.jira)

    def render_calendar_styles(self):
        """Render CSS styles cho calendar"""
        css_content = CalendarStyles.get_calendar_css()
        st.markdown(css_content, unsafe_allow_html=True)

    def render_sidebar(self) -> None:
        """Render sidebar chỉ hiển thị thống kê"""
        with st.sidebar:
            st.markdown("### 🔍 Thống kê")
            self._render_sidebar_stats()

    def _render_sidebar_stats(self):
        """Render thống kê trong sidebar"""
        selected_year = st.session_state.get("selected_year", datetime.now().year)
        selected_month = st.session_state.get("selected_month", datetime.now().month)

        try:
            time_off_data = self.time_off_service.get_time_off_data(
                selected_year, selected_month
            )

            if not time_off_data:
                st.info("Chưa có dữ liệu ngày nghỉ")
                return

            user_stats = self.time_off_service.get_user_stats(time_off_data)
            st.markdown("**Số ngày nghỉ:**")

            for user_name, count in sorted(user_stats.items()):
                # Sử dụng UserAvatarHelper thay vì logic cũ
                user_display = self.user_helper.render_user_display_with_avatar(
                    user_name, additional_info=f": **{count}** ngày"
                )
                st.markdown(user_display, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Lỗi khi tải thống kê: {str(e)}")

    def render_month_navigation(self) -> tuple:
        """Render navigation cho tháng/năm ở main page"""
        self._init_session_state()

        month_name = st.session_state.selected_month
        st.title(
            f"📅 Lịch Ngày Nghỉ Team - {month_name} /{st.session_state.selected_year}"
        )

        self._render_navigation_buttons()
        return st.session_state.selected_year, st.session_state.selected_month

    def _init_session_state(self):
        """Khởi tạo session state"""
        current_date = datetime.now()
        if "selected_year" not in st.session_state:
            st.session_state.selected_year = current_date.year
        if "selected_month" not in st.session_state:
            st.session_state.selected_month = current_date.month

    def _render_navigation_buttons(self):
        """Render navigation buttons"""
        # Thêm wrapper div với class để target CSS
        st.markdown('<div class="navigation-buttons">', unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 6, 1])

        with col1:
            if st.button("⬅️ Tháng trước", key="prev_month", type="primary"):
                self._navigate_previous_month()

        with col3:
            if st.button("Tháng sau ➡️", key="next_month", type="primary"):
                self._navigate_next_month()

        st.markdown("</div>", unsafe_allow_html=True)

    def _navigate_previous_month(self):
        """Chuyển về tháng trước"""
        if st.session_state.selected_month == 1:
            st.session_state.selected_month = 12
            st.session_state.selected_year -= 1
        else:
            st.session_state.selected_month -= 1

        # Đóng modal nếu đang mở
        if "show_time_off_dialog" in st.session_state:
            st.session_state.show_time_off_dialog = False

        st.rerun()

    def _navigate_next_month(self):
        """Chuyển sang tháng sau"""
        if st.session_state.selected_month == 12:
            st.session_state.selected_month = 1
            st.session_state.selected_year += 1
        else:
            st.session_state.selected_month += 1

        # Đóng modal nếu đang mở
        if "show_time_off_dialog" in st.session_state:
            st.session_state.show_time_off_dialog = False

        st.rerun()

    def render_calendar_header(self):
        """Render header của calendar"""
        header_html = CalendarStyles.get_calendar_header_html()
        st.markdown(header_html, unsafe_allow_html=True)

    def render_calendar_grid(
        self, selected_year: int, selected_month: int, time_off_dict: Dict
    ):
        """Render calendar grid với các ngày sử dụng grid layout đồng nhất"""
        cal = calendar.monthcalendar(selected_year, selected_month)

        for week in cal:
            self._render_week_row_improved(
                week, selected_year, selected_month, time_off_dict
            )

    def _render_week_row_improved(
        self,
        week: List[int],
        selected_year: int,
        selected_month: int,
        time_off_dict: Dict,
    ):
        """Render một hàng tuần trong calendar với kích thước đồng nhất"""
        cols = st.columns(7)

        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    # Ô trống cho những ngày không thuộc tháng này
                    st.markdown(
                        '<div style="height: 80px; border: 1px solid transparent;"></div>',
                        unsafe_allow_html=True,
                    )
                    continue

                self._render_day_button_improved(
                    day, i, selected_year, selected_month, time_off_dict
                )

    def _render_day_button_improved(
        self,
        day: int,
        day_index: int,
        selected_year: int,
        selected_month: int,
        time_off_dict: Dict,
    ):
        """Render button cho một ngày với kích thước cố định và hiển thị shortName"""
        current_day = date(selected_year, selected_month, day)
        day_str = current_day.strftime("%Y-%m-%d")

        # Kiểm tra có phải hôm nay không
        is_today = current_day == date.today()

        # Kiểm tra có lịch nghỉ không
        has_timeoff = day_str in time_off_dict

        # Kiểm tra có TEAM nghỉ trong ngày này không
        has_team_off = False
        if has_timeoff:
            users_off = time_off_dict[day_str]
            has_team_off = any(
                user_data["user_name"] == "TEAM" for user_data in users_off
            )

        # Tạo nội dung hiển thị đồng nhất với 2 hàng
        display_content = self._get_day_display_content_improved(
            day, day_str, time_off_dict
        )

        # Tạo help text với indicator cho ngày hôm nay
        help_text = (
            f"Click để thêm/xem ngày nghỉ cho {day}/{selected_month}/{selected_year}"
        )
        if is_today:
            help_text = f"HÔM NAY - {help_text}"

        # Tạo key có điều kiện cho CSS targeting (ưu tiên hôm nay trước)
        if is_today:
            button_key = f"today_day_{day}_{selected_month}_{selected_year}"
        elif has_team_off:
            button_key = f"team_day_{day}_{selected_month}_{selected_year}"
        else:
            button_key = f"day_{day}_{selected_month}_{selected_year}"

        # Sử dụng button với styling tùy chỉnh
        if st.button(
            display_content,
            key=button_key,
            help=help_text,
            use_container_width=True,
            type="secondary",
        ):
            st.session_state.selected_date = current_day
            st.session_state.show_time_off_dialog = True
            st.rerun()

    def _get_day_display_content_improved(
        self, day: int, day_str: str, time_off_dict: Dict
    ) -> str:
        """Tạo nội dung hiển thị cho ngày với 2 hàng: ngày + danh sách shortName"""
        # Hàng 1: Số ngày (luôn có)
        display_content = f"**{day}**\n"

        # Hàng 2: Danh sách shortName của users nghỉ
        if day_str in time_off_dict:
            # Lấy danh sách users nghỉ trong ngày này
            users_off = time_off_dict[day_str]

            # Sử dụng UserAvatarHelper để render danh sách avatar
            avatar_list_html = self.user_helper.render_avatar_list_for_day(users_off)
            display_content += f"\n{avatar_list_html}"
        else:
            # Thêm dòng trống để đảm bảo chiều cao đồng nhất
            display_content += f"\n ‎ "

        return display_content

    def render_time_off_modal(self, selected_date: date, time_off_data: List[Dict]):
        """Render modal để quản lý ngày nghỉ"""

        @st.dialog(
            f"📅 Ngày nghỉ - {selected_date.strftime('%d/%m/%Y')}", width="large"
        )
        def show_time_off_modal():
            existing_time_offs = self._get_existing_time_offs(
                selected_date, time_off_data
            )

            col_existing, col_form = st.columns([1, 1])

            with col_existing:
                self._render_existing_time_offs(existing_time_offs)

            with col_form:
                self._render_add_time_off_form(selected_date)

        show_time_off_modal()

    def _get_existing_time_offs(
        self, selected_date: date, time_off_data: List[Dict]
    ) -> List[Dict]:
        """Lấy danh sách ngày nghỉ hiện có cho ngày được chọn"""
        day_str = selected_date.strftime("%Y-%m-%d")
        return [item for item in time_off_data if item["date"] == day_str]

    def _render_existing_time_offs(self, existing_time_offs: List[Dict]):
        """Render danh sách ngày nghỉ hiện có"""
        st.markdown("### 🏖️ Ngày nghỉ hiện có")

        if not existing_time_offs:
            st.info("Chưa có ngày nghỉ nào")
            return

        for item in existing_time_offs:
            self._render_time_off_item(item)

    def _render_time_off_item(self, item: Dict):
        """Render một item ngày nghỉ"""
        col_info, col_delete = st.columns([3, 1])

        with col_info:
            note = f"- {item.get('note', '')}" if item.get("note", "") else ""

            # Sử dụng UserAvatarHelper để render user display
            user_display = self.user_helper.render_user_display_with_avatar(
                item["user_name"],
                additional_info=f" - {item['time_off']} {note}",
                use_short_name=False,  # Sử dụng tên đầy đủ trong modal
            )
            st.markdown(user_display, unsafe_allow_html=True)

        with col_delete:
            if st.button("🗑️", key=f"delete_{item['id']}", help="Xóa", type="tertiary"):
                self._delete_time_off(item["id"])

    def _delete_time_off(self, time_off_id: str):
        """Xóa ngày nghỉ"""
        try:
            if self.time_off_service.delete_time_off(time_off_id):
                st.session_state.show_time_off_dialog = False
                st.rerun()
        except Exception as e:
            st.error(f"Lỗi khi xóa: {str(e)}")

    def _render_add_time_off_form(self, selected_date: date):
        """Render form thêm ngày nghỉ mới"""
        st.markdown("### ➕ Thêm ngày nghỉ mới")

        with st.form("add_time_off_selected"):
            selected_user, selected_time_off, time_off_note = self._render_form_inputs()

            if st.form_submit_button("💾 Lưu", type="primary"):
                self._save_time_off(
                    selected_date, selected_user, selected_time_off, time_off_note
                )

    def _render_form_inputs(self) -> tuple:
        """Render form inputs và trả về giá trị được chọn"""
        # Lấy user options với fallback
        try:
            user_options = self.jira.user_service.get_all_display_names()
        except AttributeError:
            # Fallback: extract từ jira.users
            user_options = [user["displayName"] for user in self.jira.users]

        selected_user = st.selectbox(
            "Chọn người nghỉ",
            options=user_options,
            index=0,
            key="selected_day_user",
        )

        time_off_options = ["Cả ngày", "Buổi sáng", "Buổi chiều"]
        selected_time_off = st.selectbox(
            "Thời gian nghỉ",
            options=time_off_options,
            index=0,
            key="selected_day_time",
        )
        note = st.text_input("Ghi chú", key="time_off_note")

        return selected_user, selected_time_off, note

    def _save_time_off(
        self, selected_date: date, selected_user: str, selected_time_off: str, note: str
    ):
        """Lưu ngày nghỉ mới"""
        try:
            if self.time_off_service.save_time_off(
                selected_date, selected_user, selected_time_off, note
            ):
                st.toast("✅ Đã lưu thành công!")
                st.session_state.show_time_off_dialog = False
                st.rerun()
        except Exception as e:
            st.error(f"Lỗi khi lưu: {str(e)}")

    def render_data_table(
        self, time_off_data: List[Dict], selected_month: int, selected_year: int
    ):
        """Render bảng dữ liệu chi tiết với default sort theo ngày (mới nhất trước)"""
        with st.expander("📊 Xem dữ liệu chi tiết", expanded=False):
            # Đơn giản: mặc định sort theo Ngày, mới nhất trước (giảm dần)
            DataExportService.render_dataframe_with_export(
                data=time_off_data,
                display_columns=[
                    "STT",
                    "Ngày",
                    "Người nghỉ",
                    "Thời gian nghỉ",
                    "Ghi chú",
                ],
                filename_prefix="ngay_nghi",
                selected_month=selected_month,
                selected_year=selected_year,
                default_sort_column="Ngày",
                default_sort_ascending=True,  # Mới nhất trước
                show_sort_options=False,  # Không hiển thị options
            )
