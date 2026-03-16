from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(dotenv_path=Path('.env'), override=False)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra='ignore', case_sensitive=False)

    # App settings
    app_env: str = Field(default='development', alias='APP_ENV')
    app_name: str = Field(default='multi-agent-report-tool', alias='APP_NAME')
    debug: bool = True

    # Backend API
    host: str = Field(default='0.0.0.0', alias='BACKEND_HOST')
    port: int = Field(default=8000, alias='BACKEND_PORT')
    frontend_url: str = Field(default='http://localhost:3000', alias='FRONTEND_URL')

    # Groq
    groq_api_key: str | None = Field(default=None, alias='GROQ_API_KEY')
    groq_model: str = Field(default='llama-3.3-70b-versatile', alias='GROQ_MODEL')
    groq_temperature: float = Field(default=0.2, alias='GROQ_TEMPERATURE')
    groq_max_tokens: int = Field(default=2048, alias='GROQ_MAX_TOKENS')

    # Embeddings
    embedding_provider: str = Field(default='huggingface', alias='EMBEDDING_PROVIDER')
    huggingface_api_key: str | None = Field(default=None, alias='HUGGINGFACE_API_KEY')
    huggingface_embedding_model: str = Field(
        default='sentence-transformers/all-MiniLM-L6-v2',
        alias='HUGGINGFACE_EMBEDDING_MODEL',
    )
    embedding_dimension: int = Field(default=384, alias='EMBEDDING_DIMENSION')

    # Supabase
    supabase_url: str | None = Field(default=None, alias='SUPABASE_URL')
    supabase_anon_key: str | None = Field(default=None, alias='SUPABASE_ANON_KEY')
    supabase_service_role_key: str | None = Field(default=None, alias='SUPABASE_SERVICE_ROLE_KEY')
    supabase_db_schema: str = Field(default='public', alias='SUPABASE_DB_SCHEMA')
    supabase_documents_table: str = Field(default='documents', alias='SUPABASE_DOCUMENTS_TABLE')
    supabase_chunks_table: str = Field(default='document_chunks', alias='SUPABASE_CHUNKS_TABLE')
    supabase_match_function: str = Field(default='match_document_chunks', alias='SUPABASE_MATCH_FUNCTION')

    # Retrieval/chunking
    default_chunk_size: int = Field(default=1000, alias='DEFAULT_CHUNK_SIZE')
    default_chunk_overlap: int = Field(default=200, alias='DEFAULT_CHUNK_OVERLAP')
    default_top_k: int = Field(default=5, alias='DEFAULT_TOP_K')

    # Frontend public
    next_public_api_base_url: str = Field(default='http://localhost:8000', alias='NEXT_PUBLIC_API_BASE_URL')

    def groq_ready(self) -> bool:
        return bool(self.groq_api_key and self.groq_model)

    def huggingface_ready(self) -> bool:
        return bool(self.huggingface_embedding_model and self.embedding_provider == 'huggingface')

    def supabase_ready(self) -> bool:
        return bool(self.supabase_url and (self.supabase_service_role_key or self.supabase_anon_key))


settings = Settings()


def validate_settings() -> dict[str, object]:
    """Safe, non-throwing validation summary for runtime checks/endpoints."""
    issues: list[str] = []
    if settings.default_chunk_overlap >= settings.default_chunk_size:
        issues.append('DEFAULT_CHUNK_OVERLAP must be smaller than DEFAULT_CHUNK_SIZE')

    return {
        'app_env': settings.app_env,
        'groq_ready': settings.groq_ready(),
        'huggingface_ready': settings.huggingface_ready(),
        'supabase_ready': settings.supabase_ready(),
        'issues': issues,
    }
