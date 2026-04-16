from langchain_groq import ChatGroq
from app.config import get_settings

ALLOWED_MODELS = {"llama-3.1-8b-instant", "llama-3.3-70b-versatile"}


def get_llm(model: str = None) -> ChatGroq:
    settings = get_settings()
    if model not in ALLOWED_MODELS:
        model = settings.DEFAULT_MODEL
    return ChatGroq(
        model=model,
        api_key=settings.GROQ_API_KEY,
        temperature=0.2,
        max_retries=2,
    )
