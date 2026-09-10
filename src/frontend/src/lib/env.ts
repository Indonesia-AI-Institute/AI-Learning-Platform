declare global {
  interface Window {
    __ENV__?: {
      NEXT_PUBLIC_API_URL?: string;
    };
  }
}

export function getApiUrl(): string {
  // Client-side: read the value entrypoint.sh writes to window.__ENV__ at
  // container start. process.env.NEXT_PUBLIC_API_URL is NOT safe to read
  // here — Next.js inlines it into the client bundle at build time, and
  // this image is built without it so the same image works across envs.
  if (typeof window !== "undefined" && window.__ENV__?.NEXT_PUBLIC_API_URL) {
    return window.__ENV__.NEXT_PUBLIC_API_URL;
  }

  // Server-side (SSR/Route Handlers/middleware): process.env is safe here
  // since that code runs in the Node/Bun runtime per-request, never bundled.
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }

  return "http://localhost:8000/api/v1";
}
