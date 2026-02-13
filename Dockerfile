# =====================================================
# BASE IMAGE
# =====================================================
FROM python:3.11-slim

# =====================================================
# ENV SETTINGS
# =====================================================
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# VERY IMPORTANT → supaya src bisa di import
ENV PYTHONPATH=/app/src

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
    && rm -rf /var/lib/apt/lists/*

# =====================================================
# COPY REQUIREMENTS FIRST (CACHE OPTIMIZATION)
# =====================================================
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# =====================================================
# COPY SOURCE CODE
# =====================================================
COPY src ./src

# Optional kalau kamu simpan .env di root container
# COPY .env .env

# =====================================================
# SECURITY → NON ROOT USER
# =====================================================
RUN useradd -m appuser
USER appuser

# =====================================================
# EXPOSE PORT
# =====================================================
EXPOSE 8000

# =====================================================
# START COMMAND (PRODUCTION MODE)
# =====================================================
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
