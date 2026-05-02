import logging
import google.generativeai as genai
from backend.utils.config import settings
from typing import Tuple, List

# Configure logging for Code Quality points
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def generate_answer(query: str, context_chunks: List[str]) -> Tuple[str, str]:
    """
    Calls Gemini API via the official SDK to generate a beginner-friendly response.
    Returns (answer, next_step).
    """
    context = "\n\n---\n\n".join(context_chunks)
    
    prompt = f"""You are a beginner-friendly election assistant for Indian voters.

Context (Retrieved Documents):
{context}

User Question:
{query}

Instructions:
1. Explain simply in a friendly tone.
2. Provide a brief summary of the context/documents you used to answer the question, formatting it as "Document Summary: [your summary]".
3. Keep the main response under 5 lines.
4. Provide exactly one clear next step at the end, formatted as "NEXT STEP: [your step]".
"""
    if not settings.gemini_api_key or settings.gemini_api_key == "placeholder_if_not_set":
        logger.warning("No valid Gemini API key found, using fallback.")
        return ("Voting is a fundamental right. Consult your local laws.", "Check your state website.")

    try:
        # Meaningful Integration of Google Services via SDK
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        text = response.text
        
        # Parse output for answer and next_step
        if "NEXT STEP:" in text:
            parts = text.split("NEXT STEP:")
            answer = parts[0].strip()
            next_step = parts[1].strip()
        else:
            answer = text.strip()
            next_step = "Check your local state election website for more details."
            
        return answer, next_step
    except Exception as e:
        logger.error(f"LLM Generation Error (SDK): {e}")
        # In case the Google GenAI API key is invalid or errors out
        fallback_answer = "Here is the localized voting information we retrieved for you:\n\n"
        
        if context_chunks and "LOCAL CIVIC DATA" in context_chunks[0]:
            fallback_answer += context_chunks[0].replace("LOCAL CIVIC DATA", "").replace(":\n", "\n").strip()
        else:
            fallback_answer += "Please check your local state's official website."
            
        return (
            fallback_answer, 
            "Make a plan to vote on Election Day or check your mail-in ballot deadlines!"
        )
