# =====================================================
# STAGE 1: deps — install dependencies only
# =====================================================
FROM node:22-alpine AS deps

# Install pnpm (pin version for reproducible builds)
RUN corepack enable && corepack prepare pnpm@10.17.1 --activate

WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml* ./

# Allow dependency build scripts (sharp, etc.)
RUN echo "only-built-dependencies[]=sharp" >> .npmrc && \
    echo "only-built-dependencies[]=msw" >> .npmrc && \
    echo "only-built-dependencies[]=unrs-resolver" >> .npmrc && \
    pnpm install --frozen-lockfile

# =====================================================
# STAGE 2: builder — build Next.js app
# =====================================================
FROM node:22-alpine AS builder

RUN corepack enable && corepack prepare pnpm@10.17.1 --activate

WORKDIR /app

# Copy installed dependencies
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/.npmrc ./.npmrc

# Copy source code
COPY . .

# Build Next.js
RUN pnpm build

# =====================================================
# STAGE 3: runner — production image
# =====================================================
FROM node:22-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Next.js standalone output
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

# Entrypoint yang generate env-config.js dari env runtime sebelum server start
COPY --chown=nextjs:nodejs entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME=0.0.0.0

ENTRYPOINT ["./entrypoint.sh"]