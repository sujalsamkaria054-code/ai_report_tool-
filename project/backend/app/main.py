from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.agents.rag_agent import RagAgent
from app.config import settings
from app.graph.graph import build_graph
from app.schemas.response_schema import APIResponse
from app.services.pdf_service import IngestionResult, PDFService
from app.services.retriever_service import RetrieverService
from app.services.vector_store_service import VectorStoreService
from app.utils.logger import get_logger
from app.utils.validators import get_configuration_status, sanitize_filename, validate_query

logger = get_logger(__name__)
app = FastAPI(title=settings.app_name, debug=settings.debug)

# Explicit local-dev CORS allowlist for frontend ports 3000/3001.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.local_dev_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vector_store = VectorStoreService()
retriever_service = RetrieverService(vector_store=vector_store)
rag_agent = RagAgent(retriever_service=retriever_service)
graph = build_graph(rag_agent=rag_agent)
pdf_service = PDFService()

BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BASE_DIR / 'uploads'
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
    status: str = 'uploaded'


@app.on_event('startup')
def on_startup() -> None:
    logger.info(
        'App startup | env=%s host=%s port=%d upload_dir=%s cors_origins=%s',
        settings.app_env,
        settings.host,
        settings.port,
        str(UPLOAD_DIR),
        settings.local_dev_cors_origins(),
    )


@app.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}


@app.get('/debug/app-info')
def debug_app_info() -> dict[str, object]:
    """Small non-secret debug endpoint to confirm running app + local config."""
    return {
        'app_name': settings.app_name,
        'app_env': settings.app_env,
        'upload_dir': str(UPLOAD_DIR),
        'cors_allow_origins': settings.local_dev_cors_origins(),
    }


@app.get('/config-status')
def config_status() -> dict[str, object]:
    """Return safe provider configuration status without exposing secrets."""
    return get_configuration_status(settings)


@app.post('/query', response_model=APIResponse)
def query(payload: QueryPayload) -> APIResponse:
    try:
        user_query = validate_query(payload.query)
        logger.info('Query request received | has_document=%s', bool(payload.document_id))

        tables = []
        sources: list[str] = []

        if payload.document_id:
            ingestion = DOCUMENTS.get(payload.document_id)
            if ingestion is None:
                raise HTTPException(status_code=404, detail='document_id not found')
            tables = ingestion.tables
            sources = [f'document://{payload.document_id}', ingestion.metadata.source_path]

        state = graph.invoke(
            query=user_query,
            document_id=payload.document_id,
            tables=tables,
            sources=sources,
        )

        if state.errors:
            logger.warning('Graph completed with errors: %s', state.errors)

        if not state.formatter_output:
            raise HTTPException(status_code=500, detail='Unable to format final response.')

        logger.info('Formatter output generated | has_report=%s', bool(state.report_output))
        return APIResponse(**state.formatter_output, document_id=payload.document_id)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception('Unexpected error during /query execution')
        raise HTTPException(status_code=500, detail='Failed to process query.') from exc


@app.post('/upload', response_model=UploadResponse)
async def upload(file: UploadFile = File(...)) -> UploadResponse:
    try:
        logger.info('Upload request received | filename=%s content_type=%s', file.filename, file.content_type)

        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail='Uploaded file is empty.')

        safe_name = sanitize_filename(file.filename or 'uploaded_file.pdf')
        document_id = uuid4().hex
        stored_path = UPLOAD_DIR / f'{document_id}_{safe_name}'
        stored_path.write_bytes(content)
        logger.info('Upload file saved | path=%s size_bytes=%d', str(stored_path), len(content))

        # Keep transport concerns separated from processing for easier diagnosis.
        logger.info('Ingestion started | document_id=%s', document_id)
        ingestion = pdf_service.ingest(str(stored_path))
        logger.info(
            'Ingestion completed | document_id=%s chunks=%d tables=%d',
            document_id,
            len(ingestion.chunks),
            len(ingestion.tables),
        )

        DOCUMENTS[document_id] = ingestion

        items = [
            {
                'id': f'{document_id}:{idx}',
                'text': chunk,
                'embedding': ingestion.embeddings[idx],
                'metadata': {'source': str(stored_path), 'document_id': document_id, 'chunk_index': idx},
            }
            for idx, chunk in enumerate(ingestion.chunks)
        ]
        if items:
            logger.info('Vector upsert started | document_id=%s items=%d', document_id, len(items))
            vector_store.upsert(items)
            logger.info('Vector upsert completed | document_id=%s', document_id)

        logger.info('Upload complete | document_id=%s', document_id)

        return UploadResponse(
            document_id=document_id,
            filename=safe_name,
            content_type=file.content_type or 'application/octet-stream',
            size_bytes=len(content),
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception('Unexpected error during /upload execution')
        raise HTTPException(status_code=500, detail='Failed to process upload.') from exc


if __name__ == '__main__':
    import uvicorn

    uvicorn.run('app.main:app', host=settings.host, port=settings.port, reload=settings.debug)
