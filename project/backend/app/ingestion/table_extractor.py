from app.schemas.table_schema import TableSpec


TABLE_DELIMITERS = ("|", "\t", ",")



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
    """Extract simple table-like rows from PDF-derived text.

    Baseline heuristic parser for delimited lines.
    Extension point: integrate Camelot/Tabula/pdfplumber.
    """
    text = content.decode("latin-1", errors="ignore")
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

    header = candidate_rows[0]
    body = [row for row in candidate_rows[1:] if len(row) == len(header)]
    if not body:
        return []

    rows = [dict(zip(header, row)) for row in body]
    return [TableSpec(name="extracted_table_1", columns=header, rows=rows)]
