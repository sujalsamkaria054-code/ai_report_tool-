from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt
from typing import Any, Protocol

from app.config import settings

from supabase import Client, create_client

@dataclass
class VectorRecord:
    id: str
    text: str
    embedding: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)


class VectorStoreBackend(Protocol):
    def upsert(self, records: list[VectorRecord]) -> None: ...
    def query(self, embedding: list[float], top_k: int = 3) -> list[VectorRecord]: ...


class InMemoryVectorStoreBackend:
    def __init__(self) -> None:
        self._records: dict[str, VectorRecord] = {}

    def upsert(self, records: list[VectorRecord]) -> None:
        for record in records:
            self._records[record.id] = record

    def query(self, embedding: list[float], top_k: int = 3) -> list[VectorRecord]:
        if top_k <= 0:
            return []
        ranked = sorted(
            self._records.values(),
            key=lambda record: self._cosine_similarity(embedding, record.embedding),
            reverse=True,
        )
        return ranked[:top_k]

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        if not a or not b:
            return 0.0
        size = min(len(a), len(b))
        a_slice = a[:size]
        b_slice = b[:size]
        dot = sum(x * y for x, y in zip(a_slice, b_slice))
        norm_a = sqrt(sum(x * x for x in a_slice))
        norm_b = sqrt(sum(y * y for y in b_slice))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


class VectorStoreService:
    """Provider-aware vector store scaffold with in-memory fallback."""

    def __init__(self, backend: VectorStoreBackend | None = None) -> None:
        self.backend = backend or InMemoryVectorStoreBackend()

    def create_supabase_client(self) -> Client:
        if not settings.supabase_url or not settings.supabase_service_role_key:
            raise RuntimeError('Supabase is not fully configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.')
        return create_client(settings.supabase_url, settings.supabase_service_role_key)

    # Existing local fallback methods
    def upsert(self, items: list[dict[str, Any]]) -> None:
        records = [
            VectorRecord(
                id=item['id'],
                text=item['text'],
                embedding=item['embedding'],
                metadata=item.get('metadata', {}),
            )
            for item in items
        ]
        self.backend.upsert(records)

    def query(self, embedding: list[float], top_k: int = 3) -> list[dict[str, Any]]:
        records = self.backend.query(embedding=embedding, top_k=top_k)
        return [
            {'id': r.id, 'text': r.text, 'embedding': r.embedding, 'metadata': r.metadata}
            for r in records
        ]

    # Provider-ready placeholders
    def insert_document(self, document: dict[str, Any]) -> dict[str, Any]:
        return {'status': 'not_implemented', 'target': settings.supabase_documents_table, 'document': document}

    def insert_chunks(self, chunks: list[dict[str, Any]]) -> dict[str, Any]:
        return {'status': 'not_implemented', 'target': settings.supabase_chunks_table, 'count': len(chunks)}

    def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int | None = None,
        document_id: str | None = None,
    ) -> list[dict[str, Any]]:
        _ = (query_embedding, document_id)
        return [
            {
                'status': 'not_implemented',
                'match_function': settings.supabase_match_function,
                'top_k': top_k or settings.default_top_k,
            }
        ]
