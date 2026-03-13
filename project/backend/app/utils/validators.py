def is_non_empty(value: str) -> bool:
    return bool(value and value.strip())


def validate_query(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("Query must not be empty.")
    return cleaned


def sanitize_filename(filename: str) -> str:
    return filename.replace("/", "_").replace("\\", "_")
