from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.agents.rag_agent import RagAgent
from app.config import settings
from app.graph.graph import build_graph
from app.schemas.response_schema import APIResponse
from app.services.pdf_service import IngestionResult, PDFService
from app.services.retriever_service import RetrieverService
from app.services.vector_store_service import VectorStoreService
from app.utils.logger import get_logger
from app.utils.validators import sanitize_filename, validate_query

logger = get_logger(__name__)
app = FastAPI(title=settings.app_name, debug=settings.debug)

vector_store = VectorStoreService()
retriever_service = RetrieverService(vector_store=vector_store)
rag_agent = RagAgent(retriever_service=retriever_service)
graph = build_graph(rag_agent=rag_agent)
pdf_service = PDFService()

UPLOAD_DIR = Path("project/backend/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DOCUMENTS: dict[str, IngestionResult] = {}


class QueryPayload(BaseModel):
    query: str = Field(..., min_length=1)
    document_id: str | None = None


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    content_type: str
    size_bytes: int
    status: str = "uploaded"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/query", response_model=APIResponse)
def query(payload: QueryPayload) -> APIResponse:
    try:
        user_query = validate_query(payload.query)
        logger.info("Received query: %s", user_query)

        tables = []
        sources: list[str] = []

        if payload.document_id:
            ingestion = DOCUMENTS.get(payload.document_id)
            if ingestion is None:
                raise HTTPException(status_code=404, detail="document_id not found")
            tables = ingestion.tables
            sources = [f"document://{payload.document_id}", ingestion.metadata.source_path]

        state = graph.invoke(
            query=user_query,
            document_id=payload.document_id,
            tables=tables,
            sources=sources,
        )

        if state.errors:
            logger.warning("Graph completed with errors: %s", state.errors)

        if not state.formatter_output:
            raise HTTPException(status_code=500, detail="Unable to format final response.")

        return APIResponse(**state.formatter_output)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected error during /query execution")
        raise HTTPException(status_code=500, detail="Failed to process query.") from exc


@app.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)) -> UploadResponse:
    content = await file.read()
    safe_name = sanitize_filename(file.filename or "uploaded_file.pdf")
    document_id = uuid4().hex
    stored_path = UPLOAD_DIR / f"{document_id}_{safe_name}"
    stored_path.write_bytes(content)

    logger.info("Uploaded file received: %s", safe_name)

    ingestion = pdf_service.ingest(str(stored_path))
    DOCUMENTS[document_id] = ingestion

    items = [
        {
            "id": f"{document_id}:{idx}",
            "text": chunk,
            "embedding": ingestion.embeddings[idx],
            "metadata": {"source": str(stored_path), "document_id": document_id, "chunk_index": idx},
        }
        for idx, chunk in enumerate(ingestion.chunks)
    ]
    if items:
        vector_store.upsert(items)

    return UploadResponse(
        document_id=document_id,
        filename=safe_name,
        content_type=file.content_type or "application/octet-stream",
        size_bytes=len(content),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.debug)
