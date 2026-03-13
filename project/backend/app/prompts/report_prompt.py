REPORT_PROMPT_TEMPLATE = """
You are a professional reporting assistant.

Inputs:
- user query
- RAG findings
- structured analysis results
- chart metadata (type/title/metric only)

Task:
Generate a professional report as structured fields:
- title
- summary
- insights (list)
- recommendations (list)
- conclusion

Constraints:
- narrate results clearly and concisely
- do not decide routing
- do not emit raw chart specs
- keep output suitable for schema-based response handling
""".strip()


def build_report_prompt(query: str, rag_text: str, analysis_summary: str, chart_summary: str) -> str:
    return (
        f"{REPORT_PROMPT_TEMPLATE}\n\n"
        f"Query: {query.strip()}\n"
        f"RAG: {rag_text.strip() or '<no rag findings>'}\n"
        f"Analysis: {analysis_summary.strip() or '<no analysis findings>'}\n"
        f"Chart Metadata: {chart_summary.strip() or '<no charts>'}\n"
    )
