# =====================================================
# BASE IMAGE
# =====================================================
FROM python:3.11-slim-bookworm AS base

# =====================================================
# ENV SETTINGS
# =====================================================
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # FIX: harus /app agar "from src.backend..." bekerja
    PYTHONPATH=/app

# =====================================================
# WORKDIR
# =====================================================
WORKDIR /app

# =====================================================
# SYSTEM DEPENDENCIES
# =====================================================
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# =====================================================
# DEPENDENCIES (layer terpisah untuk cache)
# =====================================================
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# =====================================================
# SOURCE CODE
# =====================================================
COPY src ./src

# Alembic config (untuk migration)
COPY alembic.ini .
COPY alembic ./alembic

# =====================================================
# SECURITY — non-root user
# =====================================================
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# =====================================================
# PORT
# =====================================================
EXPOSE 8000

# =====================================================
# ENTRYPOINT — jalankan migration lalu start server
# =====================================================
# Pisahkan di entrypoint.sh agar migration tidak
# dijalankan ulang setiap container restart
CMD ["uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]