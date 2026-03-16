from __future__ import annotations

import httpx

from app.config import settings


class LLMConfigurationError(RuntimeError):
    pass


class LLMService:
    """Provider-ready LLM service scaffold for Groq chat models."""

    def __init__(self) -> None:
        self.model = settings.groq_model

    def create_groq_chat_client(self) -> httpx.Client:
        """Create a configured Groq HTTP client.

        Raises only at runtime when called and missing configuration.
        """
        if not settings.groq_api_key:
            raise LLMConfigurationError('GROQ_API_KEY is missing. Configure environment before using LLM service.')

        return httpx.Client(
            base_url='https://api.groq.com/openai/v1',
            headers={
                'Authorization': f'Bearer {settings.groq_api_key}',
                'Content-Type': 'application/json',
            },
            timeout=30.0,
        )

    def generate(self, prompt: str) -> str:
        """Placeholder generation path.

        Returns deterministic scaffold output without calling provider.
        """
        return f'[llm_stub:{self.model}] {prompt[:200]}'
