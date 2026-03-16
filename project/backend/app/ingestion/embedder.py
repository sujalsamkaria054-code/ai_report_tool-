from __future__ import annotations

import hashlib

from app.config import settings


class EmbeddingConfigurationError(RuntimeError):
    pass


class EmbeddingClient:
    """Provider-ready embedding client scaffold."""

    def __init__(self, provider: str, model: str, api_key: str | None = None) -> None:
        self.provider = provider
        self.model = model
        self.api_key = api_key


class EmbeddingService:
    def create_client(self) -> EmbeddingClient:
        provider = settings.embedding_provider
        if provider == 'huggingface':
            return EmbeddingClient(
                provider='huggingface',
                model=settings.huggingface_embedding_model,
                api_key=settings.huggingface_api_key,
            )
        raise EmbeddingConfigurationError(f'Unsupported embedding provider: {provider}')


def embed_chunks(chunks: list[str], vector_dim: int | None = None) -> list[list[float]]:
    """Deterministic placeholder embeddings for scaffolding.

    Keeps backend bootable without external provider calls.
    """
    dim = vector_dim or settings.embedding_dimension
    if dim <= 0:
        raise ValueError('embedding dimension must be > 0')

    vectors: list[list[float]] = []
    for chunk in chunks:
        digest = hashlib.sha256(chunk.encode('utf-8')).digest()
        if dim > len(digest):
            values = [(digest[i % len(digest)] / 255.0) for i in range(dim)]
        else:
            values = [digest[i] / 255.0 for i in range(dim)]
        vectors.append(values)
    return vectors
