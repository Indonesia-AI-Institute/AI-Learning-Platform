# =====================================================
# STAGE 1: deps — install dependencies only
# =====================================================
FROM oven/bun:1.4.2-alpine AS deps

WORKDIR /app

# Copy package files
COPY package.json bun.lock* ./

# trustedDependencies in package.json (sharp, msw, unrs-resolver) tells bun
# which packages are allowed to run postinstall scripts.
RUN bun install --frozen-lockfile

# =====================================================
# STAGE 2: builder — build Next.js app
# =====================================================
FROM oven/bun:1.4.2-alpine AS builder

WORKDIR /app

# Copy installed dependencies
COPY --from=deps /app/node_modules ./node_modules

# Copy source code
COPY . .

# Build Next.js
RUN bun run build

# =====================================================
# STAGE 3: runner — production image
# =====================================================
FROM oven/bun:1.4.2-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN apk add --no-cache curl

# Create non-root user
RUN addgroup -g 1001 -S bunjs && \
    adduser -S nextjs -u 1001

# Next.js standalone output
COPY --from=builder --chown=nextjs:bunjs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:bunjs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:bunjs /app/public ./public

# Entrypoint yang generate env-config.js dari env runtime sebelum server start
COPY --chown=nextjs:bunjs entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

USER nextjs

# No EXPOSE, no build-time PORT default — set at runtime by entrypoint.sh.
# Baking a value in here would defeat the point: this image is meant to
# run unmodified across environments that each set their own PORT.
# (HOSTNAME is force-set to 0.0.0.0 in entrypoint.sh, not left dynamic —
# see the comment there for why.)

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f "http://localhost:${PORT:-3000}/" || exit 1

ENTRYPOINT ["./entrypoint.sh"]