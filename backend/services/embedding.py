import requests
from backend.utils.config import settings

from typing import List

def get_embedding(text: str) -> List[float]:
    """
    Generates an embedding for a given text using Google's generative AI (REST API).
    This avoids Python version conflicts with the google-generativeai SDK.
    """
    if not settings.gemini_api_key or settings.gemini_api_key == "placeholder_if_not_set":
        return [0.0] * 768

    url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={settings.gemini_api_key}"
    payload = {
        "model": "models/text-embedding-004",
        "content": {"parts": [{"text": text}]}
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["embedding"]["values"]
    except Exception as e:
        # Check if it's an API Key restriction (403)
        if "403" in str(e):
            print(f"⚠️ Warning: Your Gemini API Key is restricted or invalid for text-embedding. Using safe mock embeddings instead.")
        else:
            print(f"Error generating embedding via REST: {e}. Using safe mock embeddings.")
        # Return a zero vector as fallback
        return [0.0] * 768
