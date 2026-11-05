FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/ml

COPY ml/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY data/train_FD001.txt /app/data/train_FD001.txt
COPY ml/ .
