"""RAG (Retrieval Augmented Generation) system.

Note: RAG requires chromadb which may not be available on all Python versions.
The module will gracefully degrade if chromadb is not installed.
"""

from src.rag.document_loader import Document, DocumentLoader

# Lazy load chromadb-dependent modules
_vector_store = None
_retriever = None


def get_vector_store():
    """Get VectorStore instance, or None if chromadb unavailable."""
    global _vector_store
    if _vector_store is None:
        try:
            from src.rag.vector_store import VectorStore
            _vector_store = VectorStore
        except ImportError:
            return None
    return _vector_store


def get_retriever():
    """Get Retriever class, or None if chromadb unavailable."""
    global _retriever
    if _retriever is None:
        try:
            from src.rag.retriever import Retriever
            _retriever = Retriever
        except ImportError:
            return None
    return _retriever


# For backwards compatibility, try to import but don't fail
try:
    from src.rag.vector_store import VectorStore
    from src.rag.retriever import Retriever
    RAG_AVAILABLE = True
except ImportError:
    VectorStore = None
    Retriever = None
    RAG_AVAILABLE = False


__all__ = [
    "Document",
    "DocumentLoader",
    "VectorStore",
    "Retriever",
    "RAG_AVAILABLE",
    "get_vector_store",
    "get_retriever",
]
