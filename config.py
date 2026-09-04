"""Simple configuration helpers for the LLMPing CLI."""

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


def _parse_provider_models(env_value: str) -> list[list[str]]:
    """Parse provider/models from env format: 'provider:model,provider:model'"""
    models = []
    for entry in env_value.split(","):
        entry = entry.strip()
        if ":" in entry:
            provider, model = entry.split(":", 1)
            models.append([provider.strip(), model.strip()])
    return models


def default_config() -> dict[str, Any]:
    """Return the default values used by the app."""
    return {
        "defaultProvider": "mistral",
        "defaultModel": "mistral-small-latest",
        "providerModels": [],
        "contextProvider": "",
        "contextModel": "",
        "sessionTTL": 1800,
        "sessionMaxHistory": 5,
        "providerTimeout": 30,
    }


def load_runtime_config(config_path: str | None = None) -> dict[str, Any]:
    """Load config from config.json and merge it with defaults + env vars."""
    base_dir = Path(__file__).resolve().parent
    config_file = Path(config_path) if config_path else base_dir / "config.json"

    load_dotenv(dotenv_path=base_dir / ".env", override=False)

    config = default_config()
    if config_file.exists():
        with config_file.open("r", encoding="utf-8") as handle:
            loaded_config = json.load(handle)
        config.update(loaded_config)

    config["providerModels"] = config.get("providerModels", [])

    # Env var overrides for all settings
    # PROVIDER_MODELS overrides config.json providerModels
    env_models = os.getenv("PROVIDER_MODELS", "").strip()
    if env_models:
        parsed = _parse_provider_models(env_models)
        if parsed:
            config["providerModels"] = parsed

    # Simple string/int overrides
    env_overrides = {
        "sessionTTL": ("SESSION_TTL", int),
        "sessionMaxHistory": ("SESSION_MAX_HISTORY", int),
        "providerTimeout": ("PROVIDER_TIMEOUT", int),
        "contextProvider": ("CONTEXT_PROVIDER", str),
        "contextModel": ("CONTEXT_MODEL", str),
        "defaultProvider": ("DEFAULT_PROVIDER", str),
        "defaultModel": ("DEFAULT_MODEL", str),
    }
    for config_key, (env_key, cast) in env_overrides.items():
        value = os.getenv(env_key, "").strip()
        if value:
            try:
                config[config_key] = cast(value)
            except (ValueError, TypeError):
                pass

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
