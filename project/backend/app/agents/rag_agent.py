from app.prompts.rag_prompt import build_rag_prompt
from app.services.llm_service import LLMService
from app.services.retriever_service import RetrieverService


class RagAgent:
    def __init__(
        self,
        retriever_service: RetrieverService | None = None,
        llm_service: LLMService | None = None,
    ) -> None:
        self.retriever_service = retriever_service or RetrieverService()
        self.llm_service = llm_service or LLMService()

    def run(self, query: str, top_k: int = 3) -> str:
        documents = self.retriever_service.retrieve(query=query, top_k=top_k)
        context = self.retriever_service.format_context(documents)

        if not context:
            return "I could not find relevant context to answer this question."

        prompt = build_rag_prompt(query=query, context=context)
        _ = self.llm_service.generate(prompt)

        return self._build_grounded_answer(query=query, context=context)

    @staticmethod
    def _build_grounded_answer(query: str, context: str) -> str:
        context_lines = [line for line in context.splitlines() if line.strip()]
        context_preview = " ".join(context_lines[:2]).strip()
        return (
            f"Based on retrieved context, here is the answer to '{query.strip()}': "
            f"{context_preview}"
        )
