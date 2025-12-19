def build_summary_prompt(text: str) -> str:
    """Build prompt for document summarization."""
    return f"""Please provide a comprehensive summary of the following document. 
The summary should capture the main points, key arguments, and important details.
Keep the summary concise but informative, around 3-5 paragraphs.

Document:
{text}

Summary:"""


def build_classification_prompt(text: str, summary: str) -> str:
    """Build prompt for document classification."""
    return f"""Based on the following document and its summary, classify the document into one of these categories:
- Legal
- Financial
- Technical
- Medical
- Academic
- Business
- Personal
- Government
- Other

Respond with ONLY the category name, nothing else.

Summary:
{summary}

First 2000 characters of document:
{text[:2000]}

Category:"""


def build_chat_prompt(
    query: str,
    context_chunks: list[str],
    conversation_history: list[dict] | None = None,
) -> str:
    """Build prompt for chat with document context."""
    context = "\n\n---\n\n".join(context_chunks)

    history_text = ""
    if conversation_history:
        history_parts = []
        for msg in conversation_history[-5:]:  # Last 5 messages
            role = "User" if msg["role"] == "user" else "Assistant"
            history_parts.append(f"{role}: {msg['content']}")
        history_text = "\n".join(history_parts)
        history_text = f"\nPrevious conversation:\n{history_text}\n"

    return f"""You are a helpful assistant that answers questions based on the provided document context.
Use the context below to answer the user's question. If the answer is not in the context, say so.
Be concise and accurate.

Document Context:
{context}
{history_text}
User Question: {query}

Answer:"""


SYSTEM_PROMPT_CHAT = """You are a helpful document assistant. Answer questions based on the provided context from the user's documents. Be accurate, concise, and cite specific parts of the document when relevant. If the context doesn't contain enough information to answer the question, clearly state that."""

SYSTEM_PROMPT_SUMMARY = """You are a document summarization expert. Create clear, comprehensive summaries that capture key points and main ideas."""

SYSTEM_PROMPT_CLASSIFICATION = """You are a document classification expert. Classify documents accurately into the provided categories."""
