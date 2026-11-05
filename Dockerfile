FROM python:3.12-slim

# xgboost требует OpenMP
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 MODEL_PATH=/app/model.json

WORKDIR /app

COPY backend/requirements.txt backend/requirements.txt
COPY ml/requirements.txt ml/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt -r ml/requirements.txt

COPY backend backend
COPY ml ml
COPY data/train_FD001.txt data/train_FD001.txt

# Модель обучается при сборке, поэтому образ сразу готов к работе
WORKDIR /app/ml
RUN python baseline_model.py ../data/train_FD001.txt
