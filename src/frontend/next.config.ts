import { getApiUrl } from "@/lib/env";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // WAJIB untuk Docker multi-stage build
  // Menghasilkan .next/standalone yang minimal (tidak perlu node_modules penuh)
  output: "standalone",

  // Izinkan request ke API backend di Docker network
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${getApiUrl()}/:path*`,
      },
    ];
  },
};

export default nextConfig;