import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Remove output: 'export' for Azure Web App deployment
  // Azure Web App needs server-side rendering
  trailingSlash: true,
  images: {
    unoptimized: true
  }
  // Removed experimental.appDir as it's now stable in Next.js 15
};

export default nextConfig;
