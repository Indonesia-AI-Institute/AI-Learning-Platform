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

exec node server.js
