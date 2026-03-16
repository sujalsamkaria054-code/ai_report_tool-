REPORT_PROMPT_TEMPLATE = """
You are a business reporting assistant.

Inputs:
- user query
- retrieved context
- structured analysis summary
- safe table summaries (names/counts only)
- chart metadata

Task:
Generate a concise, professional report object with fields:
- title
- summary
- insights (list)
- recommendations (list)
- conclusion

Grounding rules:
- stay strictly grounded in provided inputs
- do not repeat the user prompt as the summary
- do not include raw table dumps, encoded text, or compressed payload fragments
- do not invent values, KPIs, or trends that are not supported
- avoid implementation phrases such as "based on retrieved context" unless needed for a limitation note
- if data is partial or incomplete, state limitations clearly and professionally
- when facts are limited, produce an honest partial report
""".strip()


def build_report_prompt(
    query: str,
    rag_text: str,
    analysis_summary: str,
    table_summary: str,
    chart_summary: str,
) -> str:
    return (
        f"{REPORT_PROMPT_TEMPLATE}\n\n"
        f"Query: {query.strip() or '<empty query>'}\n"
        f"Retrieved Context: {rag_text.strip() or '<no useful retrieval>'}\n"
        f"Analysis Summary: {analysis_summary.strip() or '<no analysis>'}\n"
        f"Table Summaries: {table_summary.strip() or '<no readable tables>'}\n"
        f"Chart Metadata: {chart_summary.strip() or '<no charts>'}\n"
    )
