declare global {
  interface Window {
    __ENV__?: {
      NEXT_PUBLIC_API_URL?: string;
    };
  }
}

export function getApiUrl(): string {
  // Di browser: baca dari window.__ENV__ yang di-generate entrypoint.sh saat runtime.
  if (typeof window !== "undefined" && window.__ENV__?.NEXT_PUBLIC_API_URL) {
    return window.__ENV__.NEXT_PUBLIC_API_URL;
  }

  // Di server (SSR/Route Handler/middleware): boleh baca process.env langsung,
  // karena kode server jalan di Node runtime saat request, bukan di-bundle ke client.
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }

  // Fallback terakhir kalau env belum diset sama sekali.
  return "http://localhost:8000/api/v1";
}
