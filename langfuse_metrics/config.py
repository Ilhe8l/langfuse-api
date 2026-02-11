import os
from dotenv import load_dotenv

load_dotenv()

LANGFUSE_HOST = os.getenv("LANGFUSE_HOST")
PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

GLOBAL_START_DATE = os.getenv("GLOBAL_START_DATE", "2025-01-01")
CACHE_TTL_SECONDS = 60 * 60 * 24  # 24 Horas

AUTH = (PUBLIC_KEY, SECRET_KEY)
HEADERS = {"Content-Type": "application/json"}
MAX_WORKERS = 10

DJANGO_AUTH_URL = os.getenv(
    "DJANGO_AUTH_URL",
    "http://controlpanel:8002/api/validate-token/"
)