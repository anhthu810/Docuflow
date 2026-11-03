# DocuFlow AI — Nền Tảng Trích Xuất Hóa Đơn & Tài Liệu Sang Excel

Dự án môn học **EXE101 (Experiential Entrepreneurship)**.

Hệ thống đã được tích hợp đầy đủ:
- **Frontend**: Giao diện HTML5, Tailwind CSS, Dark/Light Mode, Workspace bóc tách hóa đơn trực quan.
- **Backend**: Python **FastAPI** hiệu năng cao, tự động sinh tài liệu API Swagger UI tại `/docs`.
- **Cơ sở dữ liệu (Database)**: **SQLite** (`docuflow.db`), lưu trữ dữ liệu bền vững ngay trên máy cục bộ, không cần cài server riêng.
- **AI OCR**: Tích hợp **Google Gemini API** (hỗ trợ mô hình `gemini-1.5-flash`), kèm bộ bóc tách thông minh dự phòng (Smart Fallback Parser) giúp ứng dụng luôn chạy mượt mà ngay cả khi không có mạng hoặc chưa nhập API Key.

---

## 🚀 Cách Khởi Chạy Nhanh

### Cách 1: Chạy bằng file `run.bat` (Khuyên dùng trên Windows)
Chỉ cần nhấp đúp vào tệp **`run.bat`**. Hệ thống sẽ tự động kích hoạt môi trường ảo Python và mở trình duyệt web.

### Cách 2: Chạy bằng dòng lệnh (Terminal / PowerShell)
1. Kích hoạt môi trường ảo:
   ```powershell
   .\.venv\Scripts\activate
   ```
2. Khởi chạy máy chủ:
   ```powershell
   python main.py
   ```
   *(hoặc dùng lệnh `uvicorn main:app --reload --port 8000`)*

---

## 🌐 Các Đường Dẫn Trên Website

Sau khi máy chủ khởi động tại cổng **8000**:
- **Trang chủ (Landing Page)**: [http://localhost:8000](http://localhost:8000)
- **Không gian làm việc (Workspace/App)**: [http://localhost:8000/app](http://localhost:8000/app)
- **Đăng nhập & Đăng ký**: [http://localhost:8000/login](http://localhost:8000/login)
- **Cách hoạt động**: [http://localhost:8000/cach-thuc-hoat-dong.html](http://localhost:8000/cach-thuc-hoat-dong.html)
- **Về chúng tôi**: [http://localhost:8000/ve-chung-toi.html](http://localhost:8000/ve-chung-toi.html)
- **Gói dịch vụ**: [http://localhost:8000/bang-gia.html](http://localhost:8000/bang-gia.html)
- **Hỏi đáp & Liên hệ**: [http://localhost:8000/faq.html](http://localhost:8000/faq.html)
- **Tài liệu API (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🗄️ Cấu Trúc Cơ Sở Dữ Liệu (`docuflow.db`)

Hệ thống sử dụng SQLite với 3 bảng chính:

1. **`users`**:
   - `id`: Mã định danh người dùng.
   - `email`: Địa chỉ email.
   - `password_hash`: Mật khẩu mã hóa bảo mật với thuật toán Bcrypt.
   - `full_name`: Họ và tên.
   - `credits`: Số lượt bóc tách còn lại (mặc định 20 credits).
   - `role`: Vai trò ('user', 'admin').
   - `created_at`: Thời gian đăng ký.

2. **`documents`**:
   - `id`: Mã tài liệu/hóa đơn.
   - `user_id`: Người dùng sở hữu (liên kết khóa ngoại với bảng `users`).
   - `file_name`: Tên tệp gốc (PDF, PNG, JPG).
   - `file_path`: Đường dẫn lưu file trên server (`/uploads/...`).
   - `format`: Định dạng file ('PDF • 1 trang', 'JPG • Ảnh chụp'...).
   - `supplier`: Tên nhà cung cấp / đối tác xuất hóa đơn.
   - `tax_id`: Mã số thuế.
   - `invoice_no`: Ký hiệu số hóa đơn.
   - `date`: Ngày xuất hóa đơn.
   - `subtotal`: Tiền hàng chưa thuế.
   - `tax`: Tiền thuế GTGT (VAT).
   - `total`: Tổng tiền thanh toán.
   - `has_low_confidence`: Cờ đánh dấu trường mờ/nghi vấn cần đối soát.
   - `audit_done`: Trạng thái đã xác nhận đối soát.
   - `created_at`, `updated_at`: Thời gian tạo & chỉnh sửa.

3. **`contact_messages`**:
   - `id`: Mã tin nhắn.
   - `name`: Tên người gửi.
   - `email`: Email liên hệ.
   - `topic`: Chủ đề quan tâm.
   - `message`: Nội dung câu hỏi / yêu cầu demo.
   - `created_at`: Thời gian gửi.

---

## 🔑 Cấu Hình Google Gemini API (Tùy chọn)

Để bật trích xuất AI thật với Google Gemini:
1. Mở tệp **`.env`** trong thư mục dự án.
2. Điền API Key của bạn vào dòng:
   ```env
   GEMINI_API_KEY=AIzaSy...
   ```
*(Lấy API key hoàn toàn miễn phí tại [Google AI Studio](https://aistudio.google.com/app/apikey))*.
> **Lưu ý**: Nếu chưa điền `GEMINI_API_KEY`, ứng dụng sẽ tự động chuyển sang chế độ phân tích thông minh mẫu, đảm bảo mọi thao tác demo và thuyết trình dự án đều hoạt động 100% trơn tru, không báo lỗi.

---

## 🛠️ Cấu Trúc Mã Nguồn

```
exeWeb/
│
├── backend/
│   ├── ai_service.py       # Tích hợp AI Google Gemini & Fallback Parser
│   ├── auth.py             # Xác thực JWT, Hash mật khẩu Bcrypt
│   ├── database.py         # Kết nối cơ sở dữ liệu SQLAlchemy SQLite
│   ├── models.py           # Định nghĩa các bảng (User, Document, Contact)
│   ├── schemas.py          # Pydantic schemas kiểm tra dữ liệu đầu vào/ra
│   └── routers/
│       ├── auth_routes.py     # API Đăng ký, Đăng nhập, Google OAuth, Quên MK
│       ├── document_routes.py # API Tải lên, Cập nhật, Xóa, Xuất Excel/CSV
│       └── contact_routes.py  # API Nhận thông tin liên hệ / demo
│
├── uploads/                # Thư mục lưu trữ các file hóa đơn tải lên
├── docuflow.db             # File cơ sở dữ liệu SQLite
├── main.py                 # File khởi động chính của Backend & Web Server
├── run.bat                 # File bấm chạy 1-click cho Windows
├── requirements.txt        # Danh sách thư viện Python cần thiết
├── .env                    # Biến môi trường & API Key
│
├── index.html              # Trang chủ Landing Page
├── docuflow_ai_web_application.html # Không gian làm việc Workspace
├── login.html              # Trang đăng nhập & đăng ký
├── bang-gia.html           # Trang bảng giá gói cước
├── cach-thuc-hoat-dong.html# Trang quy trình hoạt động
├── ve-chung-toi.html       # Trang giới thiệu đội ngũ
└── faq.html                # Trang hỏi đáp và biểu mẫu liên hệ
```

