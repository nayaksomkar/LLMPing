"""In-memory session store with tag-based relevance matching.

Each session stores entries with {summary, tags, last_used}.
Context relevance is determined by tag overlap with current query.
"""

import threading
import time
from typing import Optional


class SessionStore:
    """Thread-safe in-memory session storage with tag-based retrieval."""

    def __init__(self, ttl_seconds: int = 3600, max_entries: int = 20):
        self._sessions: dict[str, list[dict]] = {}
        self._ttl = ttl_seconds
        self._max_entries = max_entries
        self._lock = threading.Lock()

    def get_relevant_entries(self, session_id: str, query_tags: set[str]) -> list[dict]:
        """Return entries sorted by tag relevance to query."""
        with self._lock:
            entries = self._sessions.get(session_id, [])
            if not entries:
                return []

            now = time.time()
            # Filter expired, score by tag overlap, sort by relevance
            valid = []
            for entry in entries:
                if now - entry["last_used"] > self._ttl:
                    continue
                overlap = len(entry["tags"] & query_tags)
                if overlap > 0:
                    entry["_score"] = overlap
                    valid.append(entry)

            valid.sort(key=lambda e: e["_score"], reverse=True)
            return valid

    def add_entry(self, session_id: str, summary: str, tags: set[str]) -> None:
        """Add a new entry with summary and tags."""
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = []

            self._sessions[session_id].append({
                "summary": summary,
                "tags": tags,
                "last_used": time.time(),
            })

            # Trim oldest if over max
            if len(self._sessions[session_id]) > self._max_entries:
                self._sessions[session_id] = self._sessions[session_id][-self._max_entries:]

    def touch_entry(self, session_id: str, index: int) -> None:
        """Update last_used timestamp (for gradual cleanup)."""
        with self._lock:
            entries = self._sessions.get(session_id, [])
            if 0 <= index < len(entries):
                entries[index]["last_used"] = time.time()

    def clear_session(self, session_id: str) -> bool:
        """Remove all entries for a session."""
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False

    def cleanup_expired(self) -> int:
        """Remove expired entries. Returns count removed."""
        with self._lock:
            now = time.time()
            removed = 0
            for session_id in list(self._sessions.keys()):
                original_len = len(self._sessions[session_id])
                self._sessions[session_id] = [
                    e for e in self._sessions[session_id]
                    if now - e["last_used"] <= self._ttl
                ]
                removed += original_len - len(self._sessions[session_id])
                if not self._sessions[session_id]:
                    del self._sessions[session_id]
            return removed

    @property
    def active_count(self) -> int:
        """Return number of active sessions."""
        with self._lock:
            return len(self._sessions)
