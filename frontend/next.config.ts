import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactCompiler: true,
  allowedDevOrigins: ["*.local", "192.168.*.*", "10.*.*.*"],
  async rewrites() {
    return [
      {
        source: "/py/:path*",
        destination: "http://localhost:8000/:path*",
      },
    ];
  },
};

export default nextConfig;
