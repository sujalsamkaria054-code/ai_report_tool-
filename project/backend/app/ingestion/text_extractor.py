from io import BytesIO



def extract_text(content: bytes) -> str:
    """Extract text from PDF bytes with a practical baseline fallback.

    Strategy:
    1) Try `pypdf` for real page-level text extraction.
    2) Fallback to lossy byte decode for robustness in constrained envs.

    Extension point: replace with OCR pipeline or layout-aware extraction.
    """
    if not content:
        return ""

    try:
        from pypdf import PdfReader  # optional dependency

        reader = PdfReader(BytesIO(content))
        pages_text: list[str] = []
        for page in reader.pages:
            pages_text.append(page.extract_text() or "")
        extracted = "\n".join(pages_text).strip()
        if extracted:
            return extracted
    except Exception:
        pass

    return content.decode("latin-1", errors="ignore").strip()
