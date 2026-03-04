# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Thêm các thư viện cần thiết để biên dịch psycopg2 từ source
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Cài đặt dependencies vào một thư mục tạm
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Cài đặt libpq5 (cần cho psycopg2) và curl (cần cho HEALTHCHECK)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies từ builder
COPY --from=builder /install /usr/local

# Tạo non-root user
RUN addgroup --system appuser && adduser --system --group appuser

# Copy source code trước khi phân quyền
COPY . .

# Phân quyền cho toàn bộ thư mục app và script cho appuser
RUN chown -R appuser:appuser /app && \
    chmod +x /app/scripts/entrypoint.sh

# Chuyển sang non-root user
USER appuser

ENV PORT=8000
EXPOSE 8000

# Kiểm tra sức khỏe container
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["/bin/sh", "./scripts/entrypoint.sh"]
# Mặc định chạy uvicorn nếu không có command nào được truyền từ docker-compose
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]