# Base image: Python 3.10
FROM python:3.10-slim

# Làm việc trong thư mục /app
WORKDIR /app

# Sao chép toàn bộ mã nguồn vào container
COPY . .

# Cài đặt Flask và SocketIO
RUN pip install --no-cache-dir flask flask-socketio eventlet

# Zeabur dùng port 8080
EXPOSE 8080

# Chạy app
CMD ["python", "app.py"]
