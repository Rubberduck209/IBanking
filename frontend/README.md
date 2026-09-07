# Frontend — Đóng học phí (Phần 2a & 2b)

Web app thuần HTML/CSS/JS, không cần build tool. Đáp ứng đúng luồng:

1. Đăng nhập bằng username/password (`POST /login` ở user-service).
2. Sau đăng nhập, tự động lấy và hiển thị **thông tin người nộp tiền** (Họ tên, SĐT, Email) — không cho chỉnh sửa (`GET /users/me/payer-info`).
3. Nhập **MSSV** để tra cứu học phí cần đóng, hiển thị tên sinh viên, khoản thu và số tiền cần thanh toán (`GET /api/tuitions/{student_id}` ở tuition-service).

## Chạy thử

1. Chạy 2 backend (mỗi service một cổng khác nhau), ví dụ:
   ```bash
   # trong thư mục user-service
   uvicorn main:app --reload --port 8000

   # trong thư mục tuition-service
   uvicorn main:app --reload --port 8001
   ```
2. Mở `app.js`, sửa 2 dòng cấu hình đầu file nếu bạn dùng cổng/host khác:
   ```js
   const USER_API = "http://localhost:8000";
   const TUITION_API = "http://localhost:8001";
   ```
3. Mở `index.html` trực tiếp bằng trình duyệt, hoặc chạy 1 static server đơn giản:
   ```bash
   python3 -m http.server 5500
   ```
   rồi truy cập `http://localhost:5500`.

> Cả 2 backend đã được bật `CORSMiddleware` (`allow_origins=["*"]`) để frontend gọi được từ origin khác lúc dev. Khi triển khai thật, nên giới hạn lại `allow_origins` về đúng domain frontend.

## Các trạng thái đã xử lý

- Sai username/password → hiện banner lỗi ở form đăng nhập.
- Token hết hạn khi đang dùng dashboard → tự động đăng xuất, quay về màn hình đăng nhập kèm thông báo.
- MSSV không tồn tại / không có khoản nợ → banner lỗi đỏ, không hiện phiếu học phí.
- Học phí đã thanh toán hoàn tất → backend trả 400 kèm message, hiển thị nguyên message đó cho người dùng.
- Token và phiên đăng nhập lưu ở `localStorage`, refresh trang vẫn giữ đăng nhập (đến khi token hết hạn hoặc bấm Đăng xuất).

## Việc chưa làm ở đây (thuộc phần 2c/3/4 — thanh toán & OTP)

Frontend này dừng ở bước tra cứu (2a/2b). Phần xác nhận số dư, gửi OTP, xác thực giao dịch và cập nhật trạng thái "đã thanh toán" cần một service thanh toán riêng (`payment_DB` / `transactions`, `otp_codes`) chưa nằm trong phạm vi này — có thể thêm một cột "Xác nhận giao dịch" ngay dưới phiếu học phí khi phần đó được hiện thực.
