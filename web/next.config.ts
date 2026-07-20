import type { NextConfig } from "next";

// 정적 배포(Vercel/S3 등) 전제 — 서버 기능 없이 output: "export"
const nextConfig: NextConfig = {
  output: "export",
  images: { unoptimized: true },
};

export default nextConfig;
