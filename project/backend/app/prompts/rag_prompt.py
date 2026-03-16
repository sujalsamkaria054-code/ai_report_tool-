RAG_PROMPT_TEMPLATE = """
You are a grounded assistant.
Use only the context below to answer the question.
If the answer is not in the context, say that explicitly.

Question:
{query}

Context:
{context}

Answer:
""".strip()


def build_rag_prompt(query: str, context: str) -> str:
    return RAG_PROMPT_TEMPLATE.format(query=query.strip(), context=context.strip() or "<no context>")
