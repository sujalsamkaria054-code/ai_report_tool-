from dataclasses import dataclass, field
from math import sqrt
from typing import Any, Protocol


@dataclass
class VectorRecord:
    id: str
    text: str
    embedding: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)


class VectorStoreBackend(Protocol):
    """Pluggable vector-store backend contract.

    Swap implementations with Chroma/FAISS/Pinecone/Supabase adapters later.
    """

    def upsert(self, records: list[VectorRecord]) -> None:
        ...

    def query(self, embedding: list[float], top_k: int = 3) -> list[VectorRecord]:
        ...


class InMemoryVectorStoreBackend:
    """Simple in-memory fallback backend for local development."""

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
    """Facade over a pluggable vector-store backend."""

    def __init__(self, backend: VectorStoreBackend | None = None) -> None:
        self.backend = backend or InMemoryVectorStoreBackend()

    def upsert(self, items: list[dict[str, Any]]) -> None:
        records = [
            VectorRecord(
                id=item["id"],
                text=item["text"],
                embedding=item["embedding"],
                metadata=item.get("metadata", {}),
            )
            for item in items
        ]
        self.backend.upsert(records)

    def query(self, embedding: list[float], top_k: int = 3) -> list[dict[str, Any]]:
        records = self.backend.query(embedding=embedding, top_k=top_k)
        return [
            {
                "id": record.id,
                "text": record.text,
                "embedding": record.embedding,
                "metadata": record.metadata,
            }
            for record in records
        ]
