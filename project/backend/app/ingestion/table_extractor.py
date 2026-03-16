from __future__ import annotations

import re
from math import isnan
from typing import Any

from app.schemas.table_schema import TableSpec
from app.utils.logger import get_logger

logger = get_logger(__name__)

TABLE_DELIMITERS = ("|", "\t", ",")
MAX_TABLE_ROWS = 50
MAX_PREVIEW_ROWS = 5
BINARY_CHAR_RATIO_THRESHOLD = 0.20


# -------------------------
# Normalization helpers
# -------------------------
def clean_column_name(name: Any, index: int) -> str:
    """Normalize column labels to frontend-safe, deterministic names."""
    text = str(name or "").strip().lower()
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^a-zA-Z0-9_]", "", text)
    if not text:
        return f"column_{index + 1}"
    return text


def _looks_like_binary(text: str) -> bool:
    if not text:
        return False
    non_printable = sum(1 for ch in text if ord(ch) < 9 or (13 < ord(ch) < 32))
    return (non_printable / len(text)) > BINARY_CHAR_RATIO_THRESHOLD


def _looks_like_compressed_blob(text: str) -> bool:
    # Defensive heuristic: very long token without spaces and with many symbols.
    compact = text.strip()
    if len(compact) < 80:
        return False
    if " " in compact:
        return False
    symbol_count = sum(1 for ch in compact if not ch.isalnum())
    return symbol_count > (len(compact) * 0.25)


def sanitize_value(value: Any) -> Any:
    """Replace NaN/empty/unreadable values with safe frontend-friendly values."""
    if value is None:
        return ""

    if isinstance(value, bytes):
        return ""

    if isinstance(value, float) and isnan(value):
        return ""

    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return ""
        if _looks_like_binary(stripped) or _looks_like_compressed_blob(stripped):
            return ""

        # numeric coercion where possible
        int_match = re.fullmatch(r"[-+]?\d+", stripped)
        float_match = re.fullmatch(r"[-+]?\d*\.\d+", stripped)
        if int_match:
            try:
                return int(stripped)
            except ValueError:
                return stripped
        if float_match:
            try:
                return float(stripped)
            except ValueError:
                return stripped

        return stripped

    return value


def detect_numeric_columns(rows: list[dict[str, Any]], columns: list[str]) -> list[str]:
    numeric_columns: list[str] = []
    for column in columns:
        values = [row.get(column) for row in rows if row.get(column) not in ("", None)]
        if values and all(isinstance(v, (int, float)) for v in values):
            numeric_columns.append(column)
    return numeric_columns


def generate_table_preview(rows: list[dict[str, Any]], limit: int = MAX_PREVIEW_ROWS) -> list[dict[str, Any]]:
    return rows[:limit]


def _normalize_table_rows(raw_rows: list[list[Any]], table_name: str) -> TableSpec | None:
    if len(raw_rows) < 2:
        return None

    header = [clean_column_name(name, idx) for idx, name in enumerate(raw_rows[0])]

    # unique header names
    seen: dict[str, int] = {}
    unique_header: list[str] = []
    for col in header:
        if col not in seen:
            seen[col] = 0
            unique_header.append(col)
        else:
            seen[col] += 1
            unique_header.append(f"{col}_{seen[col]}")

    normalized_rows: list[dict[str, Any]] = []
    for row in raw_rows[1:]:
        if len(row) != len(unique_header):
            continue

        normalized_row: dict[str, Any] = {}
        for col_name, value in zip(unique_header, row):
            cleaned = sanitize_value(value)
            normalized_row[col_name] = cleaned

        # skip rows that are entirely empty after sanitation
        if any(value not in ("", None) for value in normalized_row.values()):
            normalized_rows.append(normalized_row)

        if len(normalized_rows) >= MAX_TABLE_ROWS:
            break

    if not normalized_rows:
        return None

    numeric_columns = detect_numeric_columns(normalized_rows, unique_header)

    return TableSpec(
        name=table_name,
        columns=unique_header,
        rows=normalized_rows,
        row_count=len(normalized_rows),
        numeric_columns=numeric_columns,
        preview=generate_table_preview(normalized_rows),
    )


# -------------------------
# Extraction helpers
# -------------------------
def _normalize_cell(cell: str) -> str:
    return cell.strip()


def _split_row(line: str) -> list[str] | None:
    for delimiter in TABLE_DELIMITERS:
        if delimiter in line:
            cells = [_normalize_cell(cell) for cell in line.split(delimiter)]
            if len(cells) > 1:
                return cells
    return None


def extract_tables(content: bytes) -> list[TableSpec]:
    """Extract and normalize table-like data from PDF bytes.

    - Enforces frontend-safe structure
    - Never returns raw binary/compressed-looking payloads
    - Skips unreadable tables with warning logs
    """
    if not content:
        return []

    text = content.decode("latin-1", errors="ignore")
    if _looks_like_binary(text):
        logger.warning("Skipping table extraction: payload looks binary/unreadable.")
        return []

    candidate_rows: list[list[str]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        split = _split_row(line)
        if split:
            candidate_rows.append(split)

    if len(candidate_rows) < 2:
        return []

    normalized = _normalize_table_rows(candidate_rows, table_name="extracted_table_1")
    if normalized is None:
        logger.warning("Skipping extracted table: unable to normalize to safe structured rows.")
        return []

    return [normalized]
