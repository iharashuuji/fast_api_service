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

FROM python:3.11-slim

WORKDIR /app
# builderステージからPoetryをコピー

COPY --from=builder /root/.local /root/.local
ENV PATH="/root/.local/bin:${PATH}"

COPY ./app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

