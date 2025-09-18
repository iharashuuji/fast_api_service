#=========
# Builder stage
#=========

FROM python:3.11-slim AS builder

WORKDIR /app

# ビルドに必要なツールを入れる
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Poetryのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#=========
# Final stage
#=========

# final stage
FROM python:3.11-slim

WORKDIR /app

# builderステージから pip install 済みパッケージをコピー
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# サービスアカウントキーをコピー
COPY ./keys /app/keys

# 環境変数でパスを指定
ENV GOOGLE_APPLICATION_CREDENTIALS=/home/hiroto/gen-lang-client-0738370520-45d672cb2326.json

# アプリケーションコピー
COPY ./app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
