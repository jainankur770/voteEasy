import logging
import google.generativeai as genai
from backend.utils.config import settings
from typing import List

logger = logging.getLogger(__name__)

def get_embedding(text: str) -> List[float]:
    """
    Generates an embedding for a given text using Google's generative AI SDK.
    Provides a safe fallback to prevent application crashes on API restrictions.
    """
    if not settings.gemini_api_key or settings.gemini_api_key == "placeholder_if_not_set":
        return [0.0] * 768

    try:
        genai.configure(api_key=settings.gemini_api_key)
        # Using text-embedding-004 model natively
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text
        )
        return result['embedding']
    except Exception as e:
        if "403" in str(e):
            logger.warning("Gemini API Key restricted. Using safe mock embeddings.")
        else:
            logger.error(f"Embedding error: {e}. Using safe mock embeddings.")
        # Return a zero vector as fallback
        return [0.0] * 768
