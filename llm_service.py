"""LLM service with provider fallback and tag-based session memory.

Simple flow:
    query → tag-based context lookup → build prompt → provider fallback → answer

Session memory (optional):
    - Stores {summary, tags} per exchange
    - Tags extracted from query, matched against stored tags
    - More matches = more relevant context
    - Auto-cleans entries not used for a while
"""

import concurrent.futures
from typing import Optional

from config import get_config_value
from lanchainfunc import call_chain
from sessions import SessionStore


class AllProvidersFailed(Exception):
    """Raised when all providers in the fallback chain fail."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__(f"All providers failed: {'; '.join(errors)}")


# Common stop words filtered from tag extraction
_STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "shall", "to", "of", "in", "for",
    "on", "with", "at", "by", "from", "as", "into", "through", "during",
    "before", "after", "above", "below", "between", "out", "off", "over",
    "under", "again", "further", "then", "once", "here", "there", "when",
    "where", "why", "how", "all", "both", "each", "few", "more", "most",
    "other", "some", "such", "no", "nor", "not", "only", "own", "same",
    "so", "than", "too", "very", "just", "because", "but", "and", "or",
    "if", "while", "about", "up", "what", "which", "who", "whom", "this",
    "that", "these", "those", "i", "me", "my", "myself", "we", "our",
    "you", "your", "he", "him", "his", "she", "her", "it", "its", "they",
    "them", "their", "tell", "describe", "explain", "give", "make", "let",
    "know", "show", "find", "get", "take", "come", "go", "say", "said",
}


class LLMService:
    """Simple LLM calls with optional tag-based session memory."""

    def __init__(self, session_store: Optional[SessionStore] = None):
        self._sessions = session_store or self._default_session_store()

    def chat(self, query: str, session_id: str = "") -> dict:
        """Process a query. session_id optional for context."""
        # Get relevant context if session provided
        context = ""
        query_tags = self._extract_tags(query)

        if session_id.strip():
            relevant = self._sessions.get_relevant_entries(session_id, query_tags)
            if relevant:
                context = "\n".join(e["summary"] for e in relevant[:3])

        # Build prompt
        if context:
            prompt = f"Context:\n{context}\n\nQuery: {query}"
        else:
            prompt = query

        # Call providers
        providers = get_config_value("providerModels") or []
        if not providers:
            raise AllProvidersFailed(["No providers configured"])

        timeout = get_config_value("providerTimeout") or 30
        result = self._call_with_fallback(prompt, providers, timeout)

        # Store exchange if session provided
        if session_id.strip():
            summary = f"Q: {query[:100]} | A: {result['text'][:150]}"
            self._sessions.add_entry(session_id, summary, query_tags)

        return {
            "answer": result["text"],
            "provider": result["provider"],
            "model": result["model"],
        }

    @property
    def active_sessions(self) -> int:
        return self._sessions.active_count

    def configured_providers(self) -> list[str]:
        providers = get_config_value("providerModels") or []
        return [p[0] for p in providers]

    def _extract_tags(self, text: str) -> set[str]:
        """Extract meaningful keyword tags from text."""
        words = text.lower().split()
        return {
            "".join(c for c in w if c.isalnum())
            for w in words
            if len("".join(c for c in w if c.isalnum())) > 2
            and "".join(c for c in w if c.isalnum()) not in _STOP_WORDS
        }

    def _call_with_fallback(
        self, prompt: str, providers: list[list[str]], timeout: int
    ) -> dict:
        """Try each provider in order, return first success."""
        errors = []
        for provider, model in providers:
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(call_chain, provider, model, prompt)
                    result = future.result(timeout=timeout)
                if result["ok"] and result["text"]:
                    return result
                errors.append(f"{provider}/{model}: {result.get('error', 'empty')}")
            except concurrent.futures.TimeoutError:
                errors.append(f"{provider}/{model}: timeout after {timeout}s")
            except Exception as exc:
                errors.append(f"{provider}/{model}: {str(exc)}")

        raise AllProvidersFailed(errors)

    @staticmethod
    def _default_session_store() -> SessionStore:
        ttl = get_config_value("sessionTTL") or 3600
        max_entries = get_config_value("sessionMaxHistory") or 20
        return SessionStore(ttl_seconds=ttl, max_entries=max_entries)
