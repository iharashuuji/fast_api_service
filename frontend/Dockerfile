# =========
# ビルドステージ
# =========
FROM node:18-alpine AS builder

WORKDIR /app

# パッケージファイルをコピー
COPY package*.json ./

# 依存関係をインストール
RUN npm install

# ソースコードをコピー
COPY . .

# Next.jsアプリケーションをビルド
RUN npm run build 

# =========
# 本番ステージ
# =========
FROM node:18-alpine AS runner

WORKDIR /app

# 本番環境用の依存関係のみをインストール
COPY package*.json ./
RUN npm install --production

# ビルドステージから必要なファイルのみをコピー
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.js ./

# ポートを公開
EXPOSE 3000

# システムユーザーを作成してセキュリティを向上
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs && \
    chown -R nextjs:nodejs /app

USER nextjs

# アプリケーションを起動
CMD ["npm", "run", "start"] 

# CMD ["npm", "run", "start"]  # 本番環境用コマンド