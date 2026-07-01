"""LangChain function helpers for LLMPing.

This module provides small, reusable functions that build and invoke
LangChain chains for configured providers. Functions return a JSON-friendly
structure so callers can consume or print them directly.

Inputs: (provider: str, model: str, prompt: str)
Outputs: a dictionary with keys provider, model, prompt, ok, text,
status, and error.
"""

from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from config import get_provider_api_key


def build_chain(provider: str, model: str):
    """Build a LangChain chain for the given provider and model.

    Raises RuntimeError if the provider API key is missing. Returns a
    chain object that can be invoked with `.invoke({"prompt": ...})`.
    """
    api_key = get_provider_api_key(provider)
    if not api_key:
        raise RuntimeError(f"No API key configured for provider '{provider}'")

    # Provider-specific LangChain adapters
    if provider == "google_genai":
        from langchain_google_genai import ChatGoogleGenerativeAI

        llm = ChatGoogleGenerativeAI(model=model, google_api_key=api_key)
    elif provider == "mistral":
        from langchain_mistralai import ChatMistralAI

        llm = ChatMistralAI(model=model, api_key=api_key)
    elif provider == "groq":
        from langchain_groq import ChatGroq

        llm = ChatGroq(model_name=model, groq_api_key=api_key)
    elif provider == "cerebras":
        # Cerebras exposes an OpenAI-compatible endpoint; use the
        # langchain-openai adapter with a custom base_url.
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(model=model, api_key=api_key, base_url="https://api.cerebras.ai/v1")
    else:
        raise ValueError(f"Unsupported provider: {provider}")

    prompt = ChatPromptTemplate.from_messages([("human", "{prompt}")])
    return prompt | llm | StrOutputParser()


def call_chain(provider: str, model: str, prompt: str) -> dict[str, Any]:
    """Build and invoke a chain, returning a JSON-friendly payload.

    The payload is intentionally simple and easy to serialize or print.
    """
    try:
        chain = build_chain(provider, model)
        result = chain.invoke({"prompt": prompt})
        return {
            "provider": provider,
            "model": model,
            "prompt": prompt,
            "ok": True,
            "text": str(result).strip(),
            "status": "OK",
            "error": None,
        }
    except Exception as exc:
        return {
            "provider": provider,
            "model": model,
            "prompt": prompt,
            "ok": False,
            "text": "",
            "status": "FAILED",
            "error": str(exc),
        }


def main() -> None:  # simple runner for manual checks
    """Run all configured providers with a sample prompt.

    This mirrors the old test script but emphasizes the functional API.
    """
    from config import get_config_value

    configured = get_config_value("providerModels") or []
    prompt = "Say hello in 5 words or less."

    results = []
    for provider, model in configured:
        result = call_chain(provider, model, prompt)
        results.append(result)

    print({"prompt": prompt, "results": results})


if __name__ == "__main__":
    main()
