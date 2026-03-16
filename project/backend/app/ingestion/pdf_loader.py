from pathlib import Path


class PDFLoadError(Exception):
    """Raised when a PDF file cannot be loaded."""



def load_pdf(path: str) -> bytes:
    """Load PDF bytes from disk.

    Baseline implementation for local file ingestion.
    Extension point: support remote blobs (S3/GCS) or streaming loaders.
    """
    file_path = Path(path)
    if not file_path.exists() or not file_path.is_file():
        raise PDFLoadError(f"PDF file not found: {path}")

    if file_path.suffix.lower() != ".pdf":
        raise PDFLoadError(f"Expected a .pdf file, got: {file_path.suffix}")

    return file_path.read_bytes()
