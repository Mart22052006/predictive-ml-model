import os

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

RUL_WARNING = 75
RUL_CRITICAL = 30
RUL_CLIP = 125
