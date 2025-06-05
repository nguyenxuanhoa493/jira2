"""
Data Export Service - Service để xử lý export data ra các định dạng khác nhau
"""

import pandas as pd
import streamlit as st
from typing import List, Dict, Optional
from datetime import datetime


class DataExportService:
    """Service để xử lý export data"""

    @staticmethod
    def prepare_time_off_dataframe(time_off_data: List[Dict]) -> pd.DataFrame:
        """Chuẩn bị DataFrame từ time off data với cột STT"""
        if not time_off_data:
            return pd.DataFrame()

        df = pd.DataFrame(time_off_data)
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%d/%m/%Y")
        df = df.rename(
            columns={
                "date": "Ngày",
                "user_name": "Người nghỉ",
                "time_off": "Thời gian nghỉ",
                "note": "Ghi chú",
            }
        )

        # Thêm cột STT (số thứ tự) ở đầu
        df.insert(0, "STT", range(1, len(df) + 1))

        return df

    @staticmethod
    def render_dataframe_with_export(
        data: List[Dict],
        display_columns: List[str],
        filename_prefix: str,
        selected_month: Optional[int] = None,
        selected_year: Optional[int] = None,
        default_sort_column: Optional[str] = "Ngày",
        default_sort_ascending: bool = False,
        show_sort_options: bool = False,
    ):
        """Render dataframe với default sort và export options"""
        if not data:
            st.info("Không có dữ liệu để hiển thị")
            return

        df = DataExportService.prepare_time_off_dataframe(data)

        if df.empty:
            st.info("Không có dữ liệu để hiển thị")
            return

        # Apply default sorting trước
        if default_sort_column and default_sort_column in df.columns:
            df = DataExportService._apply_single_sort(
                df, default_sort_column, default_sort_ascending
            )

        # Hiển thị sort options nếu cần (optional)
        if show_sort_options:
            col_sort1, col_sort2 = st.columns([3, 1])

            with col_sort1:
                available_columns = (
                    display_columns if display_columns else df.columns.tolist()
                )
                sort_column = st.selectbox(
                    "Sắp xếp theo:",
                    options=available_columns,
                    index=(
                        available_columns.index(default_sort_column)
                        if default_sort_column in available_columns
                        else 0
                    ),
                    key=f"sort_column_{filename_prefix}",
                )

            with col_sort2:
                sort_ascending = st.radio(
                    "Thứ tự:",
                    options=[True, False],
                    format_func=lambda x: "Tăng dần ↑" if x else "Giảm dần ↓",
                    index=0 if default_sort_ascending else 1,
                    key=f"sort_order_{filename_prefix}",
                )

            # Apply user selected sorting
            if (
                sort_column != default_sort_column
                or sort_ascending != default_sort_ascending
            ):
                df = DataExportService._apply_single_sort(
                    df, sort_column, sort_ascending
                )

        # Hiển thị bảng với các cột được chọn
        display_df = df[display_columns] if display_columns else df

        # Config cột STT để nhỏ hơn
        column_config = {}
        if "STT" in display_df.columns:
            column_config["STT"] = st.column_config.NumberColumn(
                "STT", width="small", help="Số thứ tự"  # Cột nhỏ
            )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config=column_config,
        )

        # Export buttons với data đã được sort
        DataExportService._render_export_buttons(
            df, filename_prefix, selected_month, selected_year
        )

    @staticmethod
    def _render_export_buttons(
        df: pd.DataFrame,
        filename_prefix: str,
        selected_month: Optional[int] = None,
        selected_year: Optional[int] = None,
    ):
        """Render các nút export"""
        # Tạo filename
        if selected_month and selected_year:
            filename = f"{filename_prefix}_thang_{selected_month}_{selected_year}"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_{timestamp}"

        col1, col2, col3 = st.columns(3)

        with col1:
            # Export CSV
            csv = df.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                label="📥 Tải về CSV",
                data=csv,
                file_name=f"{filename}.csv",
                mime="text/csv",
            )

        with col2:
            # Export Excel (nếu cần)
            try:
                import io

                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False, sheet_name="Data")

                st.download_button(
                    label="📊 Tải về Excel",
                    data=buffer.getvalue(),
                    file_name=f"{filename}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            except ImportError:
                st.info("Cần cài đặt openpyxl để export Excel")

        with col3:
            # Export JSON (nếu cần)
            json_data = df.to_json(orient="records", force_ascii=False, indent=2)
            st.download_button(
                label="🗂️ Tải về JSON",
                data=json_data,
                file_name=f"{filename}.json",
                mime="application/json",
            )

    @staticmethod
    def get_user_stats_dataframe(user_stats: Dict[str, int]) -> pd.DataFrame:
        """Tạo DataFrame cho thống kê user với cột STT"""
        if not user_stats:
            return pd.DataFrame()

        stats_data = [
            {"Người dùng": user, "Số ngày nghỉ": count}
            for user, count in sorted(user_stats.items())
        ]
        df = pd.DataFrame(stats_data)

        # Thêm cột STT ở đầu
        df.insert(0, "STT", range(1, len(df) + 1))

        return df

    @staticmethod
    def export_calendar_summary(
        time_off_data: List[Dict],
        user_stats: Dict[str, int],
        selected_month: int,
        selected_year: int,
    ):
        """Export tổng hợp calendar (time off + stats)"""
        if not time_off_data and not user_stats:
            st.warning("Không có dữ liệu để export")
            return

        try:
            import io

            buffer = io.BytesIO()

            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                # Sheet 1: Chi tiết ngày nghỉ
                if time_off_data:
                    df_details = DataExportService.prepare_time_off_dataframe(
                        time_off_data
                    )
                    df_details.to_excel(
                        writer, sheet_name="Chi tiết ngày nghỉ", index=False
                    )

                # Sheet 2: Thống kê
                if user_stats:
                    df_stats = DataExportService.get_user_stats_dataframe(user_stats)
                    df_stats.to_excel(writer, sheet_name="Thống kê", index=False)

            filename = f"bao_cao_nghi_phep_thang_{selected_month}_{selected_year}.xlsx"

            st.download_button(
                label="📋 Tải báo cáo tổng hợp",
                data=buffer.getvalue(),
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        except ImportError:
            st.error("Cần cài đặt openpyxl để export Excel")
        except Exception as e:
            st.error(f"Lỗi khi export: {str(e)}")

    @staticmethod
    def _apply_single_sort(
        df: pd.DataFrame, sort_column: str, sort_ascending: bool
    ) -> pd.DataFrame:
        """Apply single column sorting với xử lý đặc biệt cho từng loại cột"""
        try:
            if sort_column == "Ngày":
                # Convert back to datetime để sort đúng
                df_temp = df.copy()
                df_temp["date_for_sort"] = pd.to_datetime(
                    df_temp["Ngày"], format="%d/%m/%Y"
                )
                df_temp = df_temp.sort_values("date_for_sort", ascending=sort_ascending)
                df = df_temp.drop("date_for_sort", axis=1)
            else:
                df = df.sort_values(sort_column, ascending=sort_ascending)

            # Reindex STT sau khi sort
            if "STT" in df.columns:
                df = df.reset_index(drop=True)
                df["STT"] = range(1, len(df) + 1)

            return df
        except Exception as e:
            st.warning(f"Không thể sắp xếp theo '{sort_column}': {str(e)}")
            return df
