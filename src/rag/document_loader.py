import re
from pathlib import Path
from typing import List, Dict


class Document:
    """Represents a document chunk."""

    def __init__(self, content: str, metadata: Dict):
        self.content = content
        self.metadata = metadata

    def __repr__(self):
        return f"Document(length={len(self.content)}, source={self.metadata.get('source')})"


class DocumentLoader:
    """Load and process documents from various sources."""

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load_markdown_files(self, directory: str) -> List[Document]:
        """Load all markdown files from a directory."""
        documents = []
        path = Path(directory)

        if not path.exists():
            print(f"Warning: Directory {directory} does not exist")
            return documents

        for md_file in path.glob("**/*.md"):
            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()

                title = self._extract_title(content, md_file.name)
                chunks = self._chunk_text(content, title, str(md_file.relative_to(path)))
                documents.extend(chunks)

                print(f"Loaded: {md_file.name} ({len(chunks)} chunks)")
            except Exception as e:
                print(f"Error loading {md_file}: {e}")

        return documents

    def load_text_files(self, directory: str) -> List[Document]:
        """Load all text files from a directory."""
        documents = []
        path = Path(directory)

        if not path.exists():
            print(f"Warning: Directory {directory} does not exist")
            return documents

        for txt_file in path.glob("**/*.txt"):
            try:
                with open(txt_file, "r", encoding="utf-8") as f:
                    content = f.read()

                title = txt_file.stem
                chunks = self._chunk_text(content, title, str(txt_file.relative_to(path)))
                documents.extend(chunks)

                print(f"Loaded: {txt_file.name} ({len(chunks)} chunks)")
            except Exception as e:
                print(f"Error loading {txt_file}: {e}")

        return documents

    def _extract_title(self, content: str, filename: str) -> str:
        """Extract title from markdown content or filename."""
        match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return filename.replace(".md", "").replace("_", " ").title()

    def _chunk_text(
        self, text: str, source_title: str, source_path: str
    ) -> List[Document]:
        """Split text into chunks with overlap."""
        text = self._clean_markdown(text)
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        chunks = []
        current_chunk = ""
        chunk_count = 0

        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) < self.chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk:
                    chunks.append(
                        Document(
                            current_chunk.strip(),
                            {
                                "source": source_title,
                                "source_path": source_path,
                                "chunk_id": chunk_count,
                            },
                        )
                    )
                    chunk_count += 1

                current_chunk = paragraph + "\n\n"

        if current_chunk:
            chunks.append(
                Document(
                    current_chunk.strip(),
                    {
                        "source": source_title,
                        "source_path": source_path,
                        "chunk_id": chunk_count,
                    },
                )
            )

        return chunks

    @staticmethod
    def _clean_markdown(text: str) -> str:
        """Convert markdown to plain text."""
        text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
        text = re.sub(r"`([^`]+)`", r"\1", text)
        text = re.sub(r"```[\s\S]*?```", "[code block]", text)
        text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"\*\*([^\*]+)\*\*", r"\1", text)
        text = re.sub(r"__([^_]+)__", r"\1", text)
        text = re.sub(r"\*([^\*]+)\*", r"\1", text)
        text = re.sub(r"_([^_]+)_", r"\1", text)
        text = re.sub(r"^[\-\*]{3,}$", "", text, flags=re.MULTILINE)

        return text
