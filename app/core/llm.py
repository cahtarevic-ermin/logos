from typing import AsyncIterator
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.config import get_settings

settings = get_settings()


def get_llm() -> ChatGoogleGenerativeAI:
    """Get LLM instance."""
    return ChatGoogleGenerativeAI(
        model=settings.llm_model,
        google_api_key=settings.google_api_key,
        temperature=0.7,
    )


def generate_response(prompt: str, system_prompt: str | None = None) -> str:
    """Generate a response from the LLM."""
    llm = get_llm()
    messages = []

    if system_prompt:
        messages.append(SystemMessage(content=system_prompt))

    messages.append(HumanMessage(content=prompt))

    response = llm.invoke(messages)
    return response.content


async def generate_response_stream(
    prompt: str, system_prompt: str | None = None
) -> AsyncIterator[str]:
    """Stream response from the LLM."""
    llm = get_llm()
    messages = []

    if system_prompt:
        messages.append(SystemMessage(content=system_prompt))

    messages.append(HumanMessage(content=prompt))

    async for chunk in llm.astream(messages):
        if chunk.content:
            yield chunk.content
