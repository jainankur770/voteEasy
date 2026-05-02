import requests
from backend.utils.config import settings
from typing import Tuple, List

def generate_answer(query: str, context_chunks: List[str]) -> Tuple[str, str]:
    """
    Calls Gemini API via REST to generate a beginner-friendly response based on RAG context.
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
        return ("Voting is a fundamental right. Consult your local laws.", "Check your state website.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.gemini_api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}], "role": "user"}]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        
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
        print(f"LLM Generation Error (REST): {e}")
        # In case the Google GenAI API key is invalid or errors out (e.g. 403 Forbidden), 
        # gracefully extract the civic data from our RAG context to supply the user robust UI answers
        fallback_answer = "Here is the localized voting information we retrieved for you:\n\n"
        
        if context_chunks and "LOCAL CIVIC DATA" in context_chunks[0]:
            fallback_answer += context_chunks[0].replace("LOCAL CIVIC DATA", "").replace(":\n", "\n").strip()
        else:
            fallback_answer += "Please check your local state's official website."
            
        return (
            fallback_answer, 
            "Make a plan to vote on Election Day or check your mail-in ballot deadlines!"
        )
