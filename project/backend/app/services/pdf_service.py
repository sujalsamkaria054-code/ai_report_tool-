from pydantic import BaseModel, Field

from app.ingestion.chunker import chunk_text
from app.ingestion.embedder import embed_chunks
from app.ingestion.pdf_loader import load_pdf
from app.ingestion.table_extractor import extract_tables
from app.ingestion.text_extractor import extract_text
from app.schemas.table_schema import TableSpec
from app.utils.logger import get_logger


logger = get_logger(__name__)


class DocumentMetadata(BaseModel):
    source_path: str
    file_size_bytes: int
    chunk_count: int
    table_count: int


class IngestionResult(BaseModel):
    metadata: DocumentMetadata
    raw_text: str
    chunks: list[str] = Field(default_factory=list)
    embeddings: list[list[float]] = Field(default_factory=list)
    tables: list[TableSpec] = Field(default_factory=list)


class PDFService:
    """Baseline PDF ingestion service with explicit extension points.

    Tables are normalized in ingestion layer and only safe structured tables
    are persisted in `IngestionResult.tables`.
    """

    def ingest(self, path: str) -> IngestionResult:
        pdf_bytes = load_pdf(path)
        raw_text = extract_text(pdf_bytes)
        chunks = chunk_text(raw_text)

        extracted_tables = extract_tables(pdf_bytes)
        tables = [table for table in extracted_tables if table.rows]
        skipped_unreadable = max(len(extracted_tables) - len(tables), 0)

        # Keep diagnostics high-level: counts only, never raw table or document dumps.
        logger.info(
            "Ingestion table stats | extracted=%d normalized=%d skipped_unreadable=%d",
            len(extracted_tables),
            len(tables),
            skipped_unreadable,
        )

        embeddings = embed_chunks(chunks)

        metadata = DocumentMetadata(
            source_path=path,
            file_size_bytes=len(pdf_bytes),
            chunk_count=len(chunks),
            table_count=len(tables),
        )

        return IngestionResult(
            metadata=metadata,
            raw_text=raw_text,
            chunks=chunks,
            embeddings=embeddings,
            tables=tables,
        )

    def export(self, content: str) -> bytes:
        return content.encode()
