import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

CACHE_BACKEND = os.getenv("CACHE_BACKEND", "memory")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.92"))

DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "openai")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
FALLBACK_PROVIDER = os.getenv("FALLBACK_PROVIDER", "anthropic")
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "claude-3-haiku-20240307")
LOCAL_FALLBACK = os.getenv("LOCAL_FALLBACK", "false").lower() == "true"

COST_LIMIT_DAILY = float(os.getenv("COST_LIMIT_DAILY", "10.0"))
