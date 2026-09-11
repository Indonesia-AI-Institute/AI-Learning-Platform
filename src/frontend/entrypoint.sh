#!/bin/sh
set -e

# Generate runtime env config yang dibaca browser (lewat <script src="/env-config.js">)
# sebelum bundle JS lain jalan. Ini yang membuat NEXT_PUBLIC_API_URL bisa
# berubah per container run, tanpa perlu rebuild image.
cat <<EOF > /app/public/env-config.js
window.__ENV__ = {
  NEXT_PUBLIC_API_URL: "${NEXT_PUBLIC_API_URL:-}"
};
EOF

# PORT is runtime-only (no build-time default — see Dockerfile). Next.js's
# standalone server.js reads it from its own environment, so exporting an
# explicit fallback here keeps that self-documented rather than relying
# silently on server.js's internal default.
export PORT="${PORT:-3000}"

# HOSTNAME is NOT a "${HOSTNAME:-...}" fallback on purpose: Docker/Linux
# auto-populates HOSTNAME with the container ID before this script ever
# runs, so a fallback here would never trigger — server.js would bind to
# whatever IP that container-ID hostname resolves to instead of listening
# on all interfaces, making the app unreachable from its own localhost
# (this broke the container's own HEALTHCHECK when tried). Binding to
# anything other than every interface has no legitimate use inside a
# container, so this is an unconditional override, not a default.
export HOSTNAME=0.0.0.0

exec bun server.js
