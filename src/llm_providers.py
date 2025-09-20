"""Utility module providing lightweight wrappers around supported LLM providers."""

from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from typing import List, Optional

logger = logging.getLogger(__name__)

try:
    from anthropic import Anthropic  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    Anthropic = None

try:
    from openai import OpenAI  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    OpenAI = None

try:
    from groq import Groq  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    Groq = None


class BaseLLMClient(ABC):
    """Simple abstract interface shared by supported LLM providers."""

    provider_label: str

    @abstractmethod
    def generate(self, prompt: str, *, max_tokens: int, temperature: float) -> str:
        """Generate text given the prompt."""


class AnthropicClient(BaseLLMClient):
    """Wrapper around Anthropic's Messages API."""

    def __init__(self, model: Optional[str] = None):
        if Anthropic is None:
            raise ImportError("anthropic package is not installed")

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set")

        self.client = Anthropic(api_key=api_key)
        self.model = model or "claude-3-sonnet-20240229"
        self.provider_label = "Anthropic Claude"

    def generate(self, prompt: str, *, max_tokens: int, temperature: float) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text.strip()


class OpenAIClient(BaseLLMClient):
    """Wrapper around OpenAI's Chat Completions API."""

    def __init__(self, model: Optional[str] = None):
        if OpenAI is None:
            raise ImportError("openai package is not installed")

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set")

        self.client = OpenAI(api_key=api_key)
        self.model = model or "gpt-4o-mini"
        self.provider_label = "OpenAI"

    def generate(self, prompt: str, *, max_tokens: int, temperature: float) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return (completion.choices[0].message.content or "").strip()


class GroqClient(BaseLLMClient):
    """Wrapper around Groq's Chat Completions API."""

    def __init__(self, model: Optional[str] = None):
        if Groq is None:
            raise ImportError("groq package is not installed")

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set")

        self.client = Groq(api_key=api_key)
        self.model = model or "mixtral-8x7b-32768"
        self.provider_label = "Groq"

    def generate(self, prompt: str, *, max_tokens: int, temperature: float) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return (completion.choices[0].message.content or "").strip()


_PROVIDER_BUILDERS = {
    "groq": GroqClient,
    "openai": OpenAIClient,
    "anthropic": AnthropicClient,
}


def _resolve_order(preferred: Optional[str]) -> List[str]:
    base_order = list(_PROVIDER_BUILDERS.keys())
    if not preferred:
        return base_order

    preferred = preferred.lower()
    if preferred not in _PROVIDER_BUILDERS:
        logger.warning("Unknown provider '%s' requested; using default order", preferred)
        return base_order

    reordered = [preferred] + [name for name in base_order if name != preferred]
    return reordered


def load_llm_client(preferred_provider: Optional[str] = None) -> BaseLLMClient:
    """Return the first available client based on configured API keys."""

    errors = []
    for provider_key in _resolve_order(preferred_provider):
        builder = _PROVIDER_BUILDERS[provider_key]
        try:
            client = builder()
            logger.info("Using %s for AI summarization", client.provider_label)
            return client
        except (ImportError, ValueError) as exc:
            errors.append(f"{provider_key}: {exc}")
            continue
        except Exception as exc:  # pragma: no cover - defensive
            errors.append(f"{provider_key}: unexpected error {exc}")
            continue

    joined_errors = "; ".join(errors) or "no providers attempted"
    raise EnvironmentError(
        "No LLM provider is correctly configured. Set GROQ_API_KEY, OPENAI_API_KEY, "
        f"or ANTHROPIC_API_KEY and install the matching client library. Details: {joined_errors}"
    )
