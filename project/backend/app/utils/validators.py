from __future__ import annotations

from app.config import Settings, settings


def is_non_empty(value: str) -> bool:
    return bool(value and value.strip())


def validate_query(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError('Query must not be empty.')
    return cleaned


def sanitize_filename(filename: str) -> str:
    return filename.replace('/', '_').replace('\\', '_')


def validate_groq_config(app_settings: Settings = settings) -> dict[str, object]:
    configured = bool(app_settings.groq_api_key and app_settings.groq_model)
    return {
        'configured': configured,
        'model': app_settings.groq_model,
        'missing': [] if configured else ['GROQ_API_KEY'],
    }


def validate_huggingface_config(app_settings: Settings = settings) -> dict[str, object]:
    configured = bool(app_settings.huggingface_embedding_model)
    missing: list[str] = []
    if not app_settings.huggingface_embedding_model:
        missing.append('HUGGINGFACE_EMBEDDING_MODEL')
    return {
        'configured': configured,
        'provider': app_settings.embedding_provider,
        'embedding_model': app_settings.huggingface_embedding_model,
        'dimension': app_settings.embedding_dimension,
        'missing': missing,
    }


def validate_supabase_config(app_settings: Settings = settings) -> dict[str, object]:
    missing: list[str] = []
    if not app_settings.supabase_url:
        missing.append('SUPABASE_URL')
    if not (app_settings.supabase_service_role_key or app_settings.supabase_anon_key):
        missing.append('SUPABASE_SERVICE_ROLE_KEY|SUPABASE_ANON_KEY')

    configured = len(missing) == 0
    return {
        'configured': configured,
        'schema': app_settings.supabase_db_schema,
        'documents_table': app_settings.supabase_documents_table,
        'chunks_table': app_settings.supabase_chunks_table,
        'match_function': app_settings.supabase_match_function,
        'missing': missing,
    }


def get_configuration_status(app_settings: Settings = settings) -> dict[str, object]:
    groq = validate_groq_config(app_settings)
    hf = validate_huggingface_config(app_settings)
    supabase = validate_supabase_config(app_settings)

    return {
        'groq_configured': groq['configured'],
        'huggingface_configured': hf['configured'],
        'supabase_configured': supabase['configured'],
        'model': groq['model'],
        'embedding_model': hf['embedding_model'],
        'embedding_dimension': hf['dimension'],
        'supabase_schema': supabase['schema'],
        'supabase_tables': {
            'documents': supabase['documents_table'],
            'chunks': supabase['chunks_table'],
        },
        'supabase_match_function': supabase['match_function'],
        'issues': [
            *[f'groq:{item}' for item in groq['missing']],
            *[f'huggingface:{item}' for item in hf['missing']],
            *[f'supabase:{item}' for item in supabase['missing']],
        ],
    }
