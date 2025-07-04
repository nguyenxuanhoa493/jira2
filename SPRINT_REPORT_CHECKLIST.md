### Checklist Công Việc - Trang Báo Cáo Sprint

**Phase 0: Khởi tạo và Lấy dữ liệu Sprint**

-   `[x]` **Task 0.1 (Data & UI):** Lấy danh sách Sprints và tạo Dropdown lựa chọn.
    -   **Mô tả:**
        -   Import `DEFAULT_PROJECT` từ `conf.py` và sử dụng làm `PROJECT_KEY`.
        -   Sử dụng `SprintService` để lấy danh sách sprints.
        -   Tạo một `st.selectbox` để cho phép người dùng chọn một sprint từ danh sách trả về.
        -   Cập nhật `BOARD_ID` chính xác cho project.

**Phase 1: Chuẩn bị Logic và Dữ liệu nền tảng**

-   `[x]` **Task 1.1 (Logic):** Tạo hàm tiện ích `adjust_sprint_dates`.
    -   **Mô tả:** Viết một hàm trong `service/utils/date_utils.py` nhận vào `start_date` và `end_date` của Sprint.
    -   Hàm này sẽ trả về `start_date` mới (vào lúc `00:00:00`) và `end_date` mới (là ngày Chủ Nhật tiếp theo của `end_date` ban đầu, vào lúc `23:59:59`).
-   `[x]` **Task 1.2 (Service):** Cập nhật `SprintService`.
    -   **Mô tả:** Tạo một hàm mới, ví dụ `get_sprint_details(sprint_id)`, để lấy thông tin chi tiết của một sprint, bao gồm danh sách các issue trong sprint đó.
    -   Trong hàm này, gọi API Jira để lấy issue.
    -   Tích hợp việc gọi hàm `adjust_sprint_dates` để có được khoảng thời gian báo cáo chính xác.
-   `[x]` **Task 1.3 (Service):** Xử lý đơn vị "point".
    -   **Mô tả:** Khi lấy dữ liệu issue từ Jira, cần xác định trường chứa thông tin `Original Estimate` (thường là `timeoriginalestimate` và có giá trị là giây).
    -   Viết logic để quy đổi giá trị này sang giờ (chia cho 3600) để sử dụng làm "point" trong báo cáo.

**Phase 2: Xây dựng Giao diện người dùng (UI) - Báo cáo một Sprint**

-   `[x]` **Task 2.1 (UI):** Thiết lập cấu trúc cơ bản cho trang `3_Report_Srpint.py`.
    -   **Mô tả:** Import các thư viện cần thiết (`streamlit`, các service đã tạo).
    -   Hardcode `PROJECT_KEY = "CLD"` và `BOARD_ID` tương ứng (cần tìm `BOARD_ID` của project `CLD`).
-   `[x]` **Task 2.2 (UI):** Xây dựng bộ chọn Sprint.
    -   **Mô tả:** Sử dụng `SprintService.get_list_sprints()` để lấy danh sách các sprint.
    -   Hiển thị một `st.selectbox` cho phép người dùng chọn một sprint. Mặc định sẽ chọn sprint có trạng thái `active`.
-   `[x]` **Task 2.3 (UI):** Hiển thị thông tin tổng quan (Summary) của Sprint.
    -   **Mô tả:** Sau khi người dùng chọn Sprint, hiển thị các thông tin cơ bản: Tên Sprint, Ngày bắt đầu và Ngày kết thúc (đã được điều chỉnh).
    -   _Các chỉ số chi tiết hơn (như tổng số point, thanh tiến độ) sẽ được thêm sau khi có dữ liệu từ Task 1.2 & 1.3._
-   `[x]` **Task 2.4 (UI):** Hiển thị danh sách Issue (dạng bảng).
    -   **Mô tả:** Dựa trên dữ liệu từ `get_sprint_details`, hiển thị một bảng (`st.dataframe` hoặc `st.data_editor`) các issue trong sprint với các cột cơ bản: `Key`, `Summary`, `Assignee`, `Status`, và `Points` (đã quy đổi).

**Phase 3: Báo cáo so sánh nhiều Sprint (Future)**

-   `[ ]` Task 3.1: Thiết kế giao diện cho phép chọn nhiều Sprint.
-   `[ ]` Task 3.2: Tính toán và hiển thị các chỉ số so sánh (ví dụ: biến động về tổng points, số lượng issue qua các sprint).

**Phase 4: Cải tiến Giao diện & Trải nghiệm người dùng (UI/UX)**

-   `[x]` **Task 4.1 (UI/UX):** Tối ưu hóa giao diện trang báo cáo.
    -   **Mô tả:**
        -   Di chuyển bộ chọn Sprint vào thanh bên (sidebar) để tiết kiệm không gian.
        -   Cập nhật tiêu đề chính của trang để hiển thị tên của Sprint đang được chọn, giúp người dùng dễ dàng xác định ngữ cảnh.
