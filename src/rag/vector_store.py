import chromadb
from typing import List, Dict
from src.rag.document_loader import Document


class VectorStore:
    """Manage ChromaDB vector store for RAG."""

    def __init__(self, db_path: str = "./chroma_db"):
        self.db_path = db_path
        self.client = chromadb.PersistentClient(path=db_path)

        self.knowledge_collection = self.client.get_or_create_collection(
            name="stoic_knowledge",
            metadata={"hnsw:space": "cosine"},
        )

        self.style_collection = self.client.get_or_create_collection(
            name="style_examples",
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(self, documents: List[Document], collection_name: str = "stoic_knowledge"):
        """Add documents to the vector store."""
        collection = (
            self.knowledge_collection
            if collection_name == "stoic_knowledge"
            else self.style_collection
        )

        ids = []
        contents = []
        metadatas = []

        for i, doc in enumerate(documents):
            doc_id = f"{doc.metadata.get('source_path', 'unknown')}_{i}"
            ids.append(doc_id)
            contents.append(doc.content)
            metadatas.append(doc.metadata)

        collection.add(ids=ids, documents=contents, metadatas=metadatas)

        print(f"Added {len(documents)} documents to {collection_name}")

    def query(
        self, query_text: str, k: int = 3, collection_name: str = "stoic_knowledge"
    ) -> List[Dict]:
        """Query the vector store."""
        collection = (
            self.knowledge_collection
            if collection_name == "stoic_knowledge"
            else self.style_collection
        )

        results = collection.query(query_texts=[query_text], n_results=k)

        retrieved = []
        if results["documents"] and len(results["documents"]) > 0:
            for i, doc in enumerate(results["documents"][0]):
                retrieved.append(
                    {
                        "content": doc,
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i]
                        if results["distances"]
                        else None,
                    }
                )

        return retrieved

    def clear_collection(self, collection_name: str = "stoic_knowledge"):
        """Clear a collection."""
        if collection_name == "stoic_knowledge":
            self.client.delete_collection(name="stoic_knowledge")
            self.knowledge_collection = self.client.get_or_create_collection(
                name="stoic_knowledge",
                metadata={"hnsw:space": "cosine"},
            )
        else:
            self.client.delete_collection(name="style_examples")
            self.style_collection = self.client.get_or_create_collection(
                name="style_examples",
                metadata={"hnsw:space": "cosine"},
            )

    def get_stats(self) -> Dict:
        """Get statistics about the vector store."""
        return {
            "knowledge_documents": self.knowledge_collection.count(),
            "style_examples": self.style_collection.count(),
        }
