# Sử dụng Python 3.10 làm base image
FROM python:3.10-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài công cụ hỗ trợ build
RUN apt-get update && apt-get install -y gcc libsqlite3-dev

# Sao chép toàn bộ project vào container
COPY . .

# Cập nhật pip và cài các thư viện Python
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Mở port cho Flask
EXPOSE 5000

# Chạy ứng dụng
CMD ["python", "app.py"]
