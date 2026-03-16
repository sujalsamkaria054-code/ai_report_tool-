from app.ingestion.embedder import embed_chunks
from app.services.vector_store_service import VectorStoreService


class RetrieverService:
    def __init__(self, vector_store: VectorStoreService | None = None) -> None:
        self.vector_store = vector_store or VectorStoreService()

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        query_embedding = embed_chunks([query])[0]
        return self.vector_store.query(embedding=query_embedding, top_k=top_k)

    @staticmethod
    def format_context(documents: list[dict]) -> str:
        if not documents:
            return ""

        lines: list[str] = []
        for idx, doc in enumerate(documents, start=1):
            source = doc.get("metadata", {}).get("source", "unknown")
            lines.append(f"[{idx}] ({source}) {doc.get('text', '').strip()}")
        return "\n".join(lines)
