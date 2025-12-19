from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import get_settings

settings = get_settings()


def chunk_text(text: str) -> list[dict]:
    """
    Split text into chunks for embedding.
    Returns list of dicts with content and metadata.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.split_text(text)

    return [
        {
            "content": chunk,
            "chunk_index": i,
            "char_count": len(chunk),
        }
        for i, chunk in enumerate(chunks)
    ]
