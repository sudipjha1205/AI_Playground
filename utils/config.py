"""
Configuration management for AI Playground.
Loads environment variables and validates required settings.
"""
import os
from dotenv import load_dotenv
from utils.logger import get_logger

logger = get_logger("config")

load_dotenv()


def get_api_key() -> str:
    """Retrieve and validate the Anthropic API key."""
    key = os.getenv("ANTHROPIC_API_KEY", "")
    if not key:
        logger.warning("ANTHROPIC_API_KEY not set in environment")
    return key


def get_model_name() -> str:
    return os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")


def get_temperature() -> float:
    return float(os.getenv("LLM_TEMPERATURE", "0.7"))


def get_max_tokens() -> int:
    return int(os.getenv("LLM_MAX_TOKENS", "2048"))


# App configuration
APP_CONFIG = {
    "api_key": get_api_key(),
    "model": get_model_name(),
    "temperature": get_temperature(),
    "max_tokens": get_max_tokens(),
    "app_title": "AI Playground",
    "version": "1.0.0"
}
