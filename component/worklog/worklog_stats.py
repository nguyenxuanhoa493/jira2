"""Component hiển thị thống kê worklog"""

import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
from .worklog_utils import _get_user_avatar


def _create_sorted_pivot_table(df_worklog, add_totals=True):
    """Tạo pivot table với columns được sort theo thời gian tăng dần"""
    # Tạo pivot table: hàng = User, cột = Date, giá trị = tổng giờ
    pivot_table = df_worklog.pivot_table(
        index="User", columns="Date", values="Time (Hours)", aggfunc="sum", fill_value=0
    ).round(2)

    # SORT CỘT THEO THỜI GIAN TĂNG DẦN
    # Convert column names to datetime for sorting
    date_columns = []
    other_columns = []

    for col in pivot_table.columns:
        if col == "Tổng (h)":
            other_columns.append(col)
        else:
            try:
                # Parse DD/MM/YYYY format
                date_obj = datetime.strptime(col, "%d/%m/%Y")
                date_columns.append((date_obj, col))
            except:
                other_columns.append(col)

    # Sort date columns by datetime object
    date_columns.sort(key=lambda x: x[0])
    sorted_date_columns = [col for _, col in date_columns]

    # Reorder columns: sorted dates first, then other columns (like "Tổng (h)")
    new_column_order = sorted_date_columns + other_columns
    pivot_table = pivot_table.reindex(columns=new_column_order)

    # Chỉ thêm totals nếu được yêu cầu
    if add_totals:
        # Kiểm tra số ngày để quyết định có hiển thị tổng hay không
        num_dates = len(sorted_date_columns)
        show_totals = num_dates > 1

        if show_totals:
            # Thêm cột tổng chỉ khi có nhiều ngày (nếu chưa có)
            if "Tổng (h)" not in pivot_table.columns:
                pivot_table["Tổng (h)"] = pivot_table[sorted_date_columns].sum(axis=1)

            # Thêm hàng tổng chỉ khi có nhiều ngày
            total_row = pivot_table.sum(axis=0)
            total_row.name = "TỔNG"
            pivot_table = pd.concat([pivot_table, total_row.to_frame().T])

    return pivot_table


def _create_excel_export_data(df_worklog):
    """Tạo data export Excel từ worklog dataframe - TÁCH BIỆT khỏi UI"""
    # Tạo copy của dataframe để không ảnh hưởng UI
    df_copy = df_worklog.copy()
    return _create_sorted_pivot_table(df_copy, add_totals=True)


def _export_to_excel(df_worklog, start_date=None, end_date=None):
    """Export worklog statistics to Excel file - HOÀN TOÀN TÁCH BIỆT"""
    # Tạo deep copy để đảm bảo không ảnh hưởng original data
    df_export = df_worklog.copy(deep=True)

    # Tạo data cho export - sử dụng data copy
    pivot_table = _create_excel_export_data(df_export)

    # Tạo BytesIO buffer để lưu Excel file
    output = BytesIO()

    # Tạo Excel writer
    with pd.ExcelWriter(output, engine="openpyxl") as writer:  # type: ignore
        # Export pivot table
        pivot_table.to_excel(
            writer,
            sheet_name="Thống kê theo User",
            startrow=4,  # Để chỗ cho header info
            index=True,
        )

        # Export raw data (sử dụng original df copy, không phải pivot)
        df_export.to_excel(writer, sheet_name="Raw Data", index=False)

        # Get workbook and worksheets
        workbook = writer.book
        stats_sheet = writer.sheets["Thống kê theo User"]
        raw_sheet = writer.sheets["Raw Data"]

        # Add header info to stats sheet
        stats_sheet["A1"] = "📊 BÁO CÁO THỐNG KÊ WORKLOG THEO USER"
        stats_sheet["A2"] = (
            f"📅 Khoảng thời gian: {start_date} → {end_date}"
            if start_date and end_date
            else ""
        )
        stats_sheet["A3"] = f"📊 Tổng số user: {len(pivot_table.index)}"

        # Format header
        from openpyxl.styles import Font, Alignment

        stats_sheet["A1"].font = Font(bold=True, size=14)
        stats_sheet["A2"].font = Font(size=12)
        stats_sheet["A3"].font = Font(size=12)

        # Auto-adjust column widths
        for sheet in [stats_sheet, raw_sheet]:
            for column in sheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                sheet.column_dimensions[column_letter].width = adjusted_width

    # Get Excel data
    output.seek(0)
    return output.getvalue()


def display_worklog_statistics(df_worklog, start_date=None, end_date=None):
    """Hiển thị thống kê tổng hợp theo user dạng pivot table với export Excel"""

    # TẠO COPY CỦA DATA NGAY TỪ ĐẦU để tránh mọi side effects
    df_display = df_worklog.copy(deep=True)

    # Header với button export
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("📊 Thống kê theo User")

    with col2:
        # EXCEL EXPORT với session state tracking
        if start_date and end_date:
            filename = f"worklog_stats_{start_date}_to_{end_date}.xlsx"
        else:
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"worklog_stats_{current_time}.xlsx"

        # Create stable key không thay đổi theo thời gian
        export_key = (
            f"excel_export_{abs(hash(f'{len(df_worklog)}_{start_date}_{end_date}'))}"
        )

        try:
            st.download_button(
                label="📥 Xuất Excel",
                data=_export_to_excel(df_worklog, start_date, end_date),
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help=f"Click để tải file {filename}",
                key=export_key,
                use_container_width=False,  # Avoid UI layout shifts
            )
        except Exception as e:
            st.error(f"❌ Lỗi tạo file Excel: {str(e)}")
            st.info("💡 Thử lại sau hoặc liên hệ admin")

    # UI DISPLAY - Tạo pivot table HOÀN TOÀN RIÊNG BIỆT
    # Đảm bảo không bị ảnh hưởng bởi export action
    try:
        pivot_table = _create_sorted_pivot_table(df_display, add_totals=True)

        # Tạo formatted index với avatar cho users (trừ hàng TỔNG)
        formatted_index = []
        for user in pivot_table.index:
            if user == "TỔNG":
                formatted_index.append("📊 TỔNG")
            else:
                avatar_url = _get_user_avatar(user)
                if avatar_url:
                    formatted_user = f'<img src="{avatar_url}" width="24" style="border-radius: 50%; margin-right: 6px; vertical-align: middle;">{user}'
                else:
                    formatted_user = f"👤 {user}"
                formatted_index.append(formatted_user)

        # Gán formatted index
        pivot_table.index = formatted_index

        # Generate HTML table
        html_table = _generate_stats_html_table(pivot_table)

        # Hiển thị HTML table
        st.markdown(html_table, unsafe_allow_html=True)

        # CSS styling
        _add_stats_css()

    except Exception as e:
        st.error(f"❌ Lỗi hiển thị bảng thống kê: {str(e)}")
        st.info("💡 Thử refresh trang hoặc liên hệ admin")


def _format_date_header(date_str):
    """Format header ngày với DD/MM ở trên và thứ ở dưới"""
    if date_str == "Tổng (h)":
        return "Tổng<br/>(h)"

    try:
        # Parse date từ DD/MM/YYYY
        date_obj = datetime.strptime(date_str, "%d/%m/%Y")

        # Tạo DD/MM
        day_month = date_obj.strftime("%d/%m")

        # Tạo thứ trong tuần
        weekdays = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "CN"]
        weekday = weekdays[date_obj.weekday()]

        return f"{day_month}<br/><small>{weekday}</small>"
    except:
        return date_str


def _format_hours_cell(value, is_total_row=False, is_total_col=False):
    """Format ô giờ với biên độ và màu sắc"""
    if value == 0:
        return "0.00"

    # Không format biên độ cho hàng/cột tổng
    if is_total_row or is_total_col:
        return f"{value:.2f}"

    # Tính biên độ so với 8h
    diff = value - 8.0

    if diff > 0:
        # Trên 8h - màu xanh
        color = "#28a745"
        formatted = f"{value:.2f} (+{diff:.1f})"
    elif diff < 0:
        # Dưới 8h - màu đỏ
        color = "#dc3545"
        formatted = f"{value:.2f} ({diff:.1f})"
    else:
        # Đúng 8h - màu bình thường
        color = "#000000"
        formatted = f"{value:.2f}"

    return f'<span style="color: {color}; font-weight: 500;">{formatted}</span>'


def _generate_stats_html_table(pivot_table):
    """Tạo HTML table với formatting tùy chỉnh"""
    html_table = '<table id="worklog_stats">\n'

    # Header với format ngày đặc biệt
    html_table += "<thead><tr><th>User</th>"
    for col in pivot_table.columns:
        formatted_header = _format_date_header(col)
        html_table += f"<th>{formatted_header}</th>"
    html_table += "</tr></thead>\n"

    # Body
    html_table += "<tbody>\n"
    for i, (user, row) in enumerate(pivot_table.iterrows()):
        is_total_row = user == "📊 TỔNG"
        row_class = ' class="total-row"' if is_total_row else ""
        html_table += f"<tr{row_class}>"
        html_table += f'<td class="user-col">{user}</td>'

        for j, (col_name, cell_value) in enumerate(row.items()):
            is_total_col = col_name == "Tổng (h)"
            formatted_value = _format_hours_cell(cell_value, is_total_row, is_total_col)
            html_table += f"<td>{formatted_value}</td>"

        html_table += "</tr>\n"

    html_table += "</tbody></table>"
    return html_table


def _add_stats_css():
    """Thêm CSS styling cho bảng thống kê"""
    st.markdown(
        """
        <style>
        #worklog_stats {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }
        #worklog_stats th, #worklog_stats td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
            vertical-align: middle;
        }
        #worklog_stats th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        #worklog_stats th small {
            font-size: 0.8em;
            color: #666;
            font-weight: normal;
        }
        #worklog_stats tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        #worklog_stats .total-row {
            background-color: #e6f3ff !important;
            font-weight: bold;
        }
        #worklog_stats .user-col {
            text-align: left !important;
            min-width: 200px;
        }
        #worklog_stats td:not(.user-col) {
            min-width: 120px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
