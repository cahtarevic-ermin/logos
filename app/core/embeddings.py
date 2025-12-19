from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import get_settings

settings = get_settings()

_embeddings_model = None


def get_embeddings_model() -> GoogleGenerativeAIEmbeddings:
    """Get or create embeddings model instance."""
    global _embeddings_model
    if _embeddings_model is None:
        _embeddings_model = GoogleGenerativeAIEmbeddings(
            model=settings.embedding_model,
            google_api_key=settings.google_api_key,
        )
    return _embeddings_model


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of texts.
    Returns list of embedding vectors.
    """
    model = get_embeddings_model()
    return model.embed_documents(texts)


def generate_query_embedding(query: str) -> list[float]:
    """Generate embedding for a single query."""
    model = get_embeddings_model()
    return model.embed_query(query)
