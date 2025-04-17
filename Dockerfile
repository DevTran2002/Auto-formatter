# Sử dụng Python 3.9 làm base image
FROM python:3.9-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài đặt các dependencies cần thiết
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt trước để tận dụng cache của Docker
COPY requirements.txt .

# Cài đặt các thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Cài đặt model spaCy
RUN python -m spacy download en_core_web_sm

# Copy toàn bộ code vào container
COPY . .

# Tạo thư mục uploads và đảm bảo quyền ghi
RUN mkdir -p uploads && chmod 777 uploads

# Expose port 5000
EXPOSE 5000

# Khởi chạy ứng dụng
CMD ["python", "app.py"]