# Sử dụng Python base image
FROM python:3.9-slim

# Cài đặt các dependencies cần thiết
RUN apt-get update && apt-get install -y \
    socat \
    && rm -rf /var/lib/apt/lists/*

# Tạo working directory
WORKDIR /app

# Copy requirements và install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy challenge files
COPY chall.py .
COPY flag.txt .

# Tạo user không có quyền root để chạy challenge
RUN useradd -m -s /bin/bash ctf
RUN chown -R ctf:ctf /app
USER ctf


# Expose port
EXPOSE 1337

# Chạy challenge server qua socat
CMD ["socat", "-T60", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:python3 chall.py"]
