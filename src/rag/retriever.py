from typing import List, Dict
from src.rag.vector_store import VectorStore


class Retriever:
    """Retrieve relevant passages and examples from the vector store."""

    def __init__(self, vector_store: VectorStore):
        self.vs = vector_store

    def retrieve_knowledge(self, query: str, k: int = 3) -> List[Dict]:
        """Retrieve stoic passages relevant to the query."""
        return self.vs.query(query, k=k, collection_name="stoic_knowledge")

    def retrieve_style_examples(self, query: str, k: int = 2) -> List[Dict]:
        """Retrieve style examples relevant to the query/content type."""
        return self.vs.query(query, k=k, collection_name="style_examples")

    def format_knowledge_context(self, results: List[Dict]) -> str:
        """Format retrieved knowledge passages as context for generation."""
        if not results:
            return "No relevant stoic passages found."

        context = "Relevant stoic wisdom:\n\n"
        for i, result in enumerate(results, 1):
            source = result["metadata"].get("source", "Unknown Source")
            content = result["content"]
            context += f"[{i}] ({source}):\n{content}\n\n"

        return context

    def format_style_examples(self, results: List[Dict]) -> str:
        """Format style examples for inclusion in prompts."""
        if not results:
            return ""

        examples = "Style examples:\n\n"
        for i, result in enumerate(results, 1):
            content = result["content"]
            examples += f"Example {i}:\n{content}\n\n"

        return examples

    def format_citations(self, results: List[Dict]) -> str:
        """Format source citations for display."""
        if not results:
            return ""

        citations = "Sources:\n"
        seen_sources = set()

        for result in results:
            source = result["metadata"].get("source", "Unknown")
            source_path = result["metadata"].get("source_path", "")

            if source not in seen_sources:
                citations += f"- {source}"
                if source_path:
                    citations += f" ({source_path})"
                citations += "\n"
                seen_sources.add(source)

        return citations
