import streamlit as st
import pandas as pd


def search_dataframe_by_keyword(df, keyword, columns=None):
    """
    Tìm kiếm các bản ghi trong DataFrame có chứa từ khóa trong bất kỳ cột nào

    Args:
        df (pd.DataFrame): DataFrame cần tìm kiếm
        keyword (str): Từ khóa cần tìm

    Returns:
        pd.DataFrame: DataFrame chỉ chứa các hàng có ít nhất một cột chứa từ khóa
    """
    if df.empty or not keyword.strip():
        return df

    # Chuyển keyword về lowercase để tìm kiếm không phân biệt hoa thường
    keyword_lower = keyword.strip().lower()

    # Tạo mask để kiểm tra từng hàng
    mask = pd.Series([False] * len(df), index=df.index)

    # Duyệt qua từng cột và kiểm tra có chứa keyword không
    list_columns = df.columns if columns is None else columns
    for column in list_columns:
        # Chuyển về string và lowercase, sau đó kiểm tra contains
        column_mask = (
            df[column].astype(str).str.lower().str.contains(keyword_lower, na=False)
        )
        mask = mask | column_mask

    return df[mask]


def show_dataframe_with_filters(dataframe, columns=None):
    col1, col2 = st.columns([1, 2])
    with col1:
        columns = st.multiselect(
            "Chọn cột để tìm kiếm:",
            options=dataframe.columns,
            default=[],
        )

    with col2:
        # Thêm chức năng tìm kiếm
        search_keyword = st.text_input(
            "🔍 Tìm kiếm issues:",
            placeholder="Nhập từ khóa để tìm kiếm",
            help="Tìm kiếm không phân biệt hoa thường trong tất cả các cột của bảng",
        )

    # Áp dụng tìm kiếm nếu có từ khóa
    if search_keyword:
        filtered_issues = search_dataframe_by_keyword(
            dataframe, search_keyword, columns=columns
        )
        st.info(
            f"🔍 Tìm thấy {len(filtered_issues)} / {len(dataframe)} issues chứa từ khóa '{search_keyword}'"
        )
        st.dataframe(filtered_issues, use_container_width=True)
    else:
        st.dataframe(dataframe, use_container_width=True)
