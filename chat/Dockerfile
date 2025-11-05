# --- Sử dụng Python làm môi trường ---
FROM python:3.10

# Tạo thư mục làm việc
WORKDIR /app

# Sao chép toàn bộ mã nguồn vào container
COPY . .

# Cài thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Expose cổng 5000
EXPOSE 5000

# Chạy ứng dụng
CMD ["python", "app.py"]
