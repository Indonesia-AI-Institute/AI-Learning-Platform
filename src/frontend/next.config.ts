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
        destination: `${process.env.NEXT_PUBLIC_API_URL}/:path*`,
      },
    ];
  },
};

export default nextConfig;