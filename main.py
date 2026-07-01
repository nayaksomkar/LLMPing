"""CLI entry point for testing LLM providers.

This script uses the LangChain helper to construct a model chain for each
provider/model pair and prints a JSON-serializable result payload.
"""

import argparse
import json
from typing import List

from config import get_config_value
from lanchainfunc import call_chain


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(description="Test configured LLM provider API keys using LangChain")
    parser.add_argument("--prompt", default="Say hello in 5 words or less.", help="Prompt to send")
    parser.add_argument("--provider", help="Test one provider only")
    parser.add_argument("--model", help="Test one model for the selected provider")
    return parser


def select_models(provider: str | None, model: str | None) -> List[List[str]]:
    """Choose the provider/model pairs to test."""
    configured_models = get_config_value("providerModels") or []

    if provider and model:
        return [[provider, model]]

    if provider:
        selected = [entry for entry in configured_models if entry[0] == provider]
        if not selected:
            raise SystemExit(f"No configured model entry found for provider '{provider}'.")
        return selected

    if model:
        raise SystemExit("--model requires --provider.")

    if configured_models:
        return configured_models

    default_provider = get_config_value("defaultProvider")
    default_model = get_config_value("defaultModel")
    if default_provider and default_model:
        return [[default_provider, default_model]]

    raise SystemExit("No provider models are configured in config.json.")


def run_checks(prompt: str, selected_models: List[List[str]]) -> None:
    """Run the LangChain chain for each selected provider/model pair."""
    results = []
    for provider, model in selected_models:
        results.append(call_chain(provider, model, prompt))

    print(json.dumps({"prompt": prompt, "results": results}, indent=2))


def main() -> None:
    """Parse arguments and start the check run."""
    parser = build_parser()
    args = parser.parse_args()

    selected_models = select_models(args.provider, args.model)
    run_checks(args.prompt, selected_models)


if __name__ == "__main__":
    main()
