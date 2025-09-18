/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true, // React の Strict Mode を有効化
  swcMinify: true,       // SWC を使った高速なコード圧縮
  compiler: {
    // 必要に応じて TypeScript や styled-components の設定
  },
  env: {
    // Docker Compose で渡す環境変数
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
  images: {
    // 外部画像ドメインを許可する場合
    domains: ['example.com'],
  },
};

module.exports = nextConfig;
