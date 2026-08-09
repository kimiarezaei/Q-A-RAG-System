from langchain_anthropic import ChatAnthropic

from config import settings
from utils.logger import get_logger


logger = get_logger(__name__)


def call_llm(
    prompt: str,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    """
    Generic LLM call wrapper.
    Keeps model configuration isolated from application logic.
    """

    try:
        logger.info("Calling Claude API")

        llm = ChatAnthropic(
            api_key=settings.anthropic_api_key,
            model=settings.model_name,
            temperature=(
                settings.temperature
                if temperature is None
                else temperature
            ),
            max_tokens=(
                settings.max_tokens
                if max_tokens is None
                else max_tokens
            ),
        )

        response = llm.invoke(prompt)

        logger.info("Claude response received successfully")

        return response.content

    except Exception:
        logger.exception("Claude API call failed")
        raise