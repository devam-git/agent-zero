"""
Simple Langfuse SDK v3 integration helpers for Agent Zero.
Provides a lightweight tracer wrapper, decorator passthrough, and safe client access.
"""
import os
from dataclasses import dataclass

# Try to import Langfuse SDK v3
try:
    from langfuse import observe, get_client  # type: ignore
    LANGFUSE_AVAILABLE = True
except Exception:
    observe = None  # type: ignore
    get_client = None  # type: ignore
    LANGFUSE_AVAILABLE = False


def _build_client():
    if not LANGFUSE_AVAILABLE:
        return None
    if os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"):
        try:
            return get_client()  # type: ignore
        except Exception as e:  # pragma: no cover
            print(f"[LangFuse] Failed to initialize client: {e}")
            return None
    return None


client = _build_client()
TRACING_ENABLED = client is not None
if TRACING_ENABLED:
    print("[LangFuse] SDK v3 initialized successfully")
else:
    print("[LangFuse] Tracing disabled (missing credentials or SDK)")


@dataclass
class _TracerConfig:
    enabled: bool
    host: str | None


class _Tracer:
    """Minimal tracer facade to satisfy tests and centralize Langfuse usage."""

    def __init__(self):
        self._client = client

    def is_enabled(self) -> bool:
        return self._client is not None

    def get_config(self) -> _TracerConfig:
        return _TracerConfig(
            enabled=self.is_enabled(),
            host=os.getenv("LANGFUSE_HOST"),
        )

    def flush(self) -> None:
        if self._client:
            self._client.flush()


tracer = _Tracer()


def flush():
    """Flush traces synchronously."""
    tracer.flush()


def trace_conversation_async(name: str = "Agent Conversation"):
    """Decorator to create a traced async function using @observe when available."""

    def decorator(func):
        if not observe or not TRACING_ENABLED:
            return func

        @observe(name=name)  # type: ignore
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        return wrapper

    return decorator