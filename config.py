"""Simple configuration helpers for the LLMPing CLI."""

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


def default_config() -> dict[str, Any]:
    """Return the default values used by the app."""
    return {
        "defaultProvider": "mistral",
        "defaultModel": "mistral-small-latest",
        "providerModels": [],
    }


def load_runtime_config(config_path: str | None = None) -> dict[str, Any]:
    """Load config from config.json and merge it with defaults."""
    base_dir = Path(__file__).resolve().parent
    config_file = Path(config_path) if config_path else base_dir / "config.json"

    load_dotenv(dotenv_path=base_dir / ".env", override=False)

    config = default_config()
    if config_file.exists():
        with config_file.open("r", encoding="utf-8") as handle:
            loaded_config = json.load(handle)
        config.update(loaded_config)

    config["providerModels"] = config.get("providerModels", [])
    return config


def get_config_value(key: str, config_path: str | None = None) -> Any:
    """Read one value from the runtime configuration."""
    config = load_runtime_config(config_path)
    return config.get(key)


def get_provider_api_key(provider: str, config_path: str | None = None) -> str:
    """Read the API key for one provider from the environment."""
    config = load_runtime_config(config_path)
    mapping = config.get("providerApiKeys", {}) or {}

    candidate_keys: list[str] = []
    explicit = mapping.get(provider)
    if explicit:
        candidate_keys.append(explicit)

    if provider == "google_genai":
        candidate_keys.extend(["GOOGLE_GENAI_API_KEY", "GEMINI_API_KEY"])
    else:
        safe = "".join(ch if ch.isalnum() else "_" for ch in provider.upper())
        candidate_keys.append(f"{safe}_API_KEY")

    for env_key in candidate_keys:
        value = os.getenv(env_key, "").strip()
        if value:
            return value

    return ""


runtime_config = load_runtime_config()
