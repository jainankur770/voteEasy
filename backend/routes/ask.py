from fastapi import APIRouter, HTTPException
from backend.models.schemas import AskRequest, AskResponse
from backend.services.rag_pipeline import retrieve_top_k
from backend.services.llm import generate_answer
from backend.services.civic_api import get_civic_data

router = APIRouter()

@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    Endpoint that processes the user query using Hybrid RAG (Civic API + Local FAISS) and Gemini.
    """
    try:
        # Enhance the query with location and status for better context
        enhanced_query = (
            f"User Location: {request.location}. "
            f"Registration Status: {request.status}. "
            f"Question: {request.question}"
        )
        
        # 1. Retrieve RAG chunks from FAISS vector store
        context_chunks = retrieve_top_k(enhanced_query, k=3)
        
        # 2. Retrieve Hybrid context from Google Civic API
        civic_data = get_civic_data(request.location)
        if civic_data:
            context_chunks.insert(0, civic_data) # Inject live data at top of context
        
        # Generate the answer and next step using LLM
        answer, next_step = generate_answer(enhanced_query, context_chunks)
        
        return AskResponse(answer=answer, next_step=next_step)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
