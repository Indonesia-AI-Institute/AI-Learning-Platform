#!/bin/bash
# =====================================================================
# deploy.sh — Pull image terbaru dari GHCR dan restart services
#
# Cara pakai:
#   ./deploy.sh                    # deploy latest
#   ./deploy.sh v1.2.3             # deploy versi spesifik
#   ./deploy.sh latest api         # deploy hanya API service
# =====================================================================

set -e

IMAGE_TAG="${1:-latest}"
SERVICE="${2:-}"   # kosong = semua service

COMPOSE_FILE="docker-compose.prod.yml"

echo "🚀 Deploying AI Learning Platform"
echo "   Image tag : ${IMAGE_TAG}"
echo "   Service   : ${SERVICE:-all}"
echo "   Compose   : ${COMPOSE_FILE}"
echo ""

# Pastikan .env.be dan .env.fe ada
if [ ! -f ".env.be" ] || [ ! -f ".env.fe" ]; then
  echo "❌ .env.be and/or .env.fe not found. Copy from .env.be.example / .env.fe.example and fill in values."
  exit 1
fi

# Export tag yang akan dipakai
export IMAGE_TAG="${IMAGE_TAG}"

# Login ke GHCR jika belum (butuh CR_PAT di env atau interaktif)
if [ -n "${CR_PAT}" ]; then
  echo "🔑 Logging in to GHCR..."
  echo "${CR_PAT}" | docker login ghcr.io -u "${GITHUB_ACTOR}" --password-stdin
fi

# Pull image terbaru
echo "📦 Pulling images (tag: ${IMAGE_TAG})..."
if [ -n "${SERVICE}" ]; then
  docker compose -f "${COMPOSE_FILE}" pull "${SERVICE}"
else
  docker compose -f "${COMPOSE_FILE}" pull api frontend
fi

# Restart containers dengan image baru
echo "🔄 Restarting containers..."
if [ -n "${SERVICE}" ]; then
  docker compose -f "${COMPOSE_FILE}" up -d "${SERVICE}"
else
  docker compose -f "${COMPOSE_FILE}" up -d
fi

# Hapus image lama yang tidak terpakai
echo "🧹 Removing unused images..."
docker image prune -f

echo ""
echo "✅ Deploy complete!"
echo ""
echo "Status:"
docker compose -f "${COMPOSE_FILE}" ps
