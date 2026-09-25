# Sử dụng Python 3.10 (hoặc phiên bản bạn đang dùng) bản slim cho nhẹ
FROM python:3.12

# Thiết lập thư mục làm việc bên trong container
WORKDIR /app

# Copy file requirements.txt vào trước để tận dụng Docker cache
COPY requirements.txt .

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn của service vào (đã bỏ qua .venv nhờ .dockerignore)
COPY . .

# Mở port 8000
EXPOSE 8000

# Lệnh chạy FastAPI bằng uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]