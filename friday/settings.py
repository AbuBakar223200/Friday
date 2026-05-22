import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def _env_int(name: str, default: int | None = None) -> int | None:
    value = os.environ.get(name, "").strip()
    if not value:
        return default

    try:
        return int(value)
    except ValueError:
        return default


def _env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name, "").strip().lower()
    if not value:
        return default

    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    return default


# Global Configuration Constants
AI_PROVIDER = os.environ.get("AI_PROVIDER", "auto").strip().lower()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "")

GEMINI_TEXT_MODELS = os.environ.get(
    "GEMINI_TEXT_MODELS",
    "gemini-2.5-flash-lite,gemini-2.5-flash,gemini-2.0-flash",
)
GEMINI_VISION_MODELS = os.environ.get(
    "GEMINI_VISION_MODELS",
    "gemini-2.5-flash,gemini-2.0-flash",
)
OPENAI_TEXT_MODEL = os.environ.get("OPENAI_TEXT_MODEL", "gpt-5")
OPENAI_VISION_MODEL = os.environ.get("OPENAI_VISION_MODEL", "gpt-5")
ANTHROPIC_TEXT_MODEL = os.environ.get("ANTHROPIC_TEXT_MODEL", "claude-sonnet-4-20250514")
ANTHROPIC_VISION_MODEL = os.environ.get("ANTHROPIC_VISION_MODEL", "claude-sonnet-4-20250514")
OPENROUTER_TEXT_MODEL = os.environ.get("OPENROUTER_TEXT_MODEL", "openrouter/auto")
OPENROUTER_VISION_MODEL = os.environ.get("OPENROUTER_VISION_MODEL", "openrouter/auto")

LISTEN_TIMEOUT = _env_float("LISTEN_TIMEOUT", 5)
PHRASE_TIME_LIMIT = _env_float("PHRASE_TIME_LIMIT", 30)
WAKE_PHRASE_TIME_LIMIT = _env_float("WAKE_PHRASE_TIME_LIMIT", 8)
PAUSE_THRESHOLD = _env_float("PAUSE_THRESHOLD", 1.6)
NON_SPEAKING_DURATION = _env_float("NON_SPEAKING_DURATION", 0.6)
PHRASE_THRESHOLD = _env_float("PHRASE_THRESHOLD", 0.3)
AMBIENT_NOISE_DURATION = _env_float("AMBIENT_NOISE_DURATION", 0.8)
DYNAMIC_ENERGY_THRESHOLD = _env_bool("DYNAMIC_ENERGY_THRESHOLD", True)
ENERGY_THRESHOLD = _env_int("ENERGY_THRESHOLD")
MICROPHONE_DEVICE_INDEX = _env_int("MICROPHONE_DEVICE_INDEX")
STT_LANGUAGE = os.environ.get("STT_LANGUAGE", "en-US").strip() or "en-US"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
VLC_PATH = r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"
