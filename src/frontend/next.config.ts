import type { NextConfig } from "next";

// 'unsafe-inline' on script-src (not just style-src) is a deliberate
// tradeoff: a nonce-based strict CSP would block Next's own injected
// hydration scripts unless every page renders dynamically (no more static
// prerendering) and remains an experimental App Router feature. This app
// has no dangerouslySetInnerHTML / rehype-raw anywhere (verified) — CSP
// here is defense-in-depth on top of that, not the primary XSS defense.
const CSP = [
  "default-src 'self'",
  "script-src 'self' 'unsafe-inline'",
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data:",
  "font-src 'self' data:",
  // Can't pin this to the API's exact origin — NEXT_PUBLIC_API_URL is
  // resolved at container runtime (see src/lib/env.ts), not known here.
  "connect-src *",
  "object-src 'none'",
  "base-uri 'self'",
  "frame-ancestors 'none'",
].join("; ");

const nextConfig: NextConfig = {
  output: "standalone",
  poweredByHeader: false,
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "Content-Security-Policy", value: CSP },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
        ],
      },
    ];
  },
};

export default nextConfig;