import os

# Адреса фронтенда, которым разрешены запросы (через запятую в переменной окружения)
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

# Пороги статуса по прогнозу RUL (в циклах)
RUL_WARNING = 75
RUL_CRITICAL = 30
RUL_CLIP = 125
