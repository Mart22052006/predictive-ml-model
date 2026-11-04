import os

from dotenv import load_dotenv

load_dotenv()

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

RUL_WARNING = int(os.getenv("RUL_WARNING"))
RUL_CRITICAL = int(os.getenv("RUL_CRITICAL"))
RUL_CLIP = int(os.getenv("RUL_CLIP"))
