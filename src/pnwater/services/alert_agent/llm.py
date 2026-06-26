"""Lazy LLM client construction.

A sibling project (RepoMindMCP) hit this the hard way: constructing a
Gemini client eagerly validates the API key immediately, so a service
with no key configured fails at import/startup time instead of falling
back gracefully exactly when it's needed. `get_llm_client()` returns
None the first time it's called with no key configured, and every
caller treats None as "use the deterministic message" rather than an
error -- no API key is required for this service to run correctly.
"""

from __future__ import annotations

from typing import Any

from pnwater.config import settings

_client: Any = None
_attempted = False


def get_llm_client() -> Any | None:
    global _client, _attempted
    if _attempted:
        return _client

    _attempted = True
    if not settings.google_api_key:
        return None

    from langchain_google_genai import ChatGoogleGenerativeAI

    _client = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=settings.google_api_key)
    return _client


def reset_for_test() -> None:
    global _client, _attempted
    _client = None
    _attempted = False
