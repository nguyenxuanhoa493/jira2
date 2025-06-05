"""
Calendar Styles - Quản lý CSS styles cho calendar component
"""


class CalendarStyles:
    """Class quản lý CSS styles cho calendar"""

    @staticmethod
    def get_calendar_css() -> str:
        """Trả về CSS string cho calendar"""
        return """
        <style>     
        /* CSS cho nút calendar sử dụng attribute selector */
        [data-testid*="stButton"] button[kind="secondary"]:hover {
            transform: scale(1.02) !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        }
        
        /* Style riêng cho nút calendar */
        [data-testid*="stButton"] button[kind="secondary"] {
            min-height: 90px !important;
            height: 90px !important;
            border-radius: 8px !important;
            border: 1px solid #e0e0e0 !important;
            background-color: white !important;
            transition: all 0.2s ease !important;
        }
        
        /* Hover effect chỉ cho nút calendar */
        [data-testid*="stButton"] button[kind="secondary"]:hover {
            background-color: #f0f8ff !important;
            border-color: #4CAF50 !important;
        }
        
        /* Style cho ngày hôm nay - target bằng class chứa "st-key-today_day_" */
        [class*="st-key-today_day_"] button[kind="secondary"] {
            background-color: #e3f2fd !important;
            border: 2px solid #2196F3 !important;
            box-shadow: 0 0 8px rgba(33, 150, 243, 0.3) !important;
        }
        
        /* Hover effect cho ngày hôm nay */
        [class*="st-key-today_day_"] button[kind="secondary"]:hover {
            background-color: #bbdefb !important;
            border-color: #1976D2 !important;
            box-shadow: 0 0 12px rgba(33, 150, 243, 0.5) !important;
        }
        
        /* Style cho ngày có TEAM nghỉ - target bằng class chứa "st-key-team_day_" */
        [class*="st-key-team_day_"] button[kind="secondary"] {
            background-color: #FFF7F1 !important;
            border: 2px solid #E78895 !important;
            box-shadow: 0 0 8px rgba(231, 136, 149, 0.4) !important;
        }
        
        /* Hover effect cho ngày có TEAM nghỉ */
        [class*="st-key-team_day_"] button[kind="secondary"]:hover {
            background-color: #ffeee1 !important;
            border-color: #ec7b8a !important;
            box-shadow: 0 0 12px rgba(231, 136, 149, 0.6) !important;
        }
        
        /* Navigation buttons (primary type) giữ nguyên style mặc định */
        [data-testid*="stButton"] button[kind="primary"] {
            /* Giữ nguyên style mặc định của Streamlit */
            min-height: auto !important;
            height: auto !important;
        }
    
        img {
            max-height: 32px !important;
            max-width: 32px !important;
            border-radius: 50% !important;
        }
        </style>
        """

    @staticmethod
    def get_calendar_header_html() -> str:
        """Trả về HTML cho calendar header"""
        return """
        <div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 2px; margin-bottom: 10px;">
            <div style="text-align: center; font-weight: bold; padding: 10px;">T2</div>
            <div style="text-align: center; font-weight: bold; padding: 10px;">T3</div>
            <div style="text-align: center; font-weight: bold; padding: 10px;">T4</div>
            <div style="text-align: center; font-weight: bold; padding: 10px;">T5</div>
            <div style="text-align: center; font-weight: bold; padding: 10px;">T6</div>
            <div style="text-align: center; font-weight: bold; padding: 10px;">T7</div>
            <div style="text-align: center; font-weight: bold; padding: 10px;">CN</div>
        </div>
        """
