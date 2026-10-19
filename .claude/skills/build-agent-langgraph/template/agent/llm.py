import os
from langchain_openai import ChatOpenAI


def llm(temperature: float = 0.0) -> ChatOpenAI:
    """One model client for every step. Swap provider here if the customer isn't on OpenAI."""
    if not os.getenv("OPENAI_BASE_URL"):
        os.environ.pop("OPENAI_BASE_URL", None)   # an empty value would point the client at nothing
    return ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"), temperature=temperature,
                      base_url=os.getenv("OPENAI_BASE_URL") or None)
