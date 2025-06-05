# 🏠 JIRA Dashboard

Ứng dụng web quản lý JIRA với Dashboard tích hợp Calendar và Worklog, được xây dựng bằng Streamlit.

## 📋 Tính năng chính

### 🏠 Dashboard

-   Hiển thị thông tin kết nối JIRA
-   Quản lý dự án mặc định
-   Giao diện chính để điều hướng

### 📅 Calendar - Quản lý ngày nghỉ

-   **Hiển thị lịch**: Giao diện lịch trực quan theo tháng
-   **Quản lý ngày nghỉ**: Thêm, xóa, chỉnh sửa ngày nghỉ của team
-   **Thống kê**: Báo cáo số ngày nghỉ theo từng thành viên
-   **Export dữ liệu**: Xuất báo cáo CSV, Excel, JSON
-   **Avatar người dùng**: Hiển thị avatar từ JIRA
-   **Sort & Filter**: Sắp xếp dữ liệu theo ngày, người dùng

### 📝 Worklog - Quản lý thời gian làm việc

-   **Theo dõi worklog**: Quản lý thời gian làm việc từ JIRA
-   **Báo cáo chi tiết**: Phân tích thời gian theo dự án, người dùng
-   **Tích hợp JIRA**: Đồng bộ dữ liệu trực tiếp từ JIRA API

## 🏗️ Kiến trúc dự án

```
jira2/
├── 📁 service/           # Business Logic Layer
│   ├── base/            # Base services
│   ├── clients/         # External API clients
│   │   ├── jira/        # JIRA API integration
│   │   └── supabase/    # Supabase database
│   ├── models/          # Data models
│   ├── utils/           # Utility functions
│   ├── time_off_service.py      # Time-off business logic
│   └── data_export_service.py   # Data export functionality
├── 📁 component/        # UI Components
│   ├── calendar_component.py    # Calendar UI component
│   ├── user_avatar_helper.py    # User avatar management
│   └── calendar_styles.py       # CSS styles
├── 📁 pages/            # Streamlit Pages
│   ├── 1_📝_Worklog.py
│   └── 2_📅_Calendar.py
├── 📁 .streamlit/       # Streamlit configuration
├── Dashboard.py         # Main entry point
├── conf.py             # Configuration management
└── requirements.txt    # Dependencies
```

## 🛠️ Công nghệ sử dụng

-   **Frontend**: [Streamlit](https://streamlit.io/) - Web framework cho Python
-   **Database**: [Supabase](https://supabase.com/) - PostgreSQL database
-   **API Integration**: [JIRA REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/)
-   **Data Processing**: [Pandas](https://pandas.pydata.org/) - Data manipulation
-   **Export**: CSV, Excel (openpyxl), JSON

## ⚙️ Cài đặt và cấu hình

### 1. Clone repository

```bash
git clone <repository-url>
cd jira2
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Cấu hình environment variables

Tạo file `.env` trong thư mục gốc:

```env
# JIRA Configuration
JIRA_URL=https://your-domain.atlassian.net
EMAIL=your-email@company.com
API_TOKEN=your-jira-api-token
DEFAULT_PROJECT=YOUR_PROJECT_KEY

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
```

### 4. Thiết lập JIRA API Token

1. Đăng nhập vào [Atlassian Account](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Tạo API Token mới
3. Copy token và paste vào file `.env`

### 5. Thiết lập Supabase

1. Tạo project mới tại [Supabase](https://supabase.com/)
2. Copy URL và anon key vào file `.env`
3. Tạo bảng `time_off` với schema phù hợp

## 🚀 Chạy ứng dụng

```bash
streamlit run Dashboard.py
```

Ứng dụng sẽ chạy tại: `http://localhost:8501`

## 📊 Sử dụng

### Calendar Page

1. **Xem lịch**: Điều hướng qua các tháng bằng nút ⬅️ ➡️
2. **Thêm ngày nghỉ**: Click vào ngày bất kỳ để mở modal
3. **Xem thống kê**: Sidebar hiển thị số ngày nghỉ của từng thành viên
4. **Export dữ liệu**: Sử dụng tab "Xem dữ liệu chi tiết"

### Worklog Page

1. **Xem worklog**: Theo dõi thời gian làm việc từ JIRA
2. **Báo cáo**: Phân tích dữ liệu theo nhiều tiêu chí
3. **Export**: Xuất báo cáo worklog

## 🏛️ Kiến trúc Clean Code

### Service Layer

-   **Separation of Concerns**: Business logic tách biệt khỏi UI
-   **Reusable Services**: `DataExportService`, `TimeOffService`
-   **API Abstraction**: JIRA và Supabase clients

### Component Layer

-   **Modular UI**: Components có thể tái sử dụng
-   **Performance Optimization**: User data caching
-   **Style Management**: CSS tập trung quản lý

### Best Practices

-   **Error Handling**: Graceful fallbacks
-   **Type Hints**: Strong typing với Python
-   **Configuration**: Environment-based config
-   **Documentation**: Comprehensive docstrings

## 🔧 Tính năng nâng cao

### Data Export

-   **Multiple Formats**: CSV, Excel, JSON
-   **Smart Sorting**: Intelligent date sorting
-   **Column Configuration**: Customizable display
-   **Batch Export**: Summary reports

### User Experience

-   **Avatar Integration**: JIRA user avatars
-   **Responsive Design**: Mobile-friendly UI
-   **Real-time Updates**: Automatic data refresh
-   **Intuitive Navigation**: User-friendly interface

## 🐛 Troubleshooting

### Lỗi kết nối JIRA

-   Kiểm tra JIRA_URL, EMAIL, API_TOKEN trong `.env`
-   Đảm bảo API Token còn hiệu lực
-   Kiểm tra quyền truy cập JIRA project

### Lỗi kết nối Supabase

-   Verify SUPABASE_URL và SUPABASE_KEY
-   Kiểm tra database schema
-   Đảm bảo RLS policies phù hợp

### Lỗi dependencies

```bash
pip install --upgrade -r requirements.txt
```

## 📝 License

[MIT License](LICENSE)

## 🤝 Contributing

1. Fork the project
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 👥 Team

Phát triển bởi team Internal Tools để tối ưu quy trình quản lý dự án JIRA.

---

**🚀 Happy Coding!**

Nếu gặp vấn đề, vui lòng tạo issue hoặc liên hệ team phát triển.
