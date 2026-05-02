from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check():
    """Verify backend health check returns 200"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_ask_validation_error():
    """Verify security constraint: Requests missing required fields are rejected (422)"""
    payload = {
        "question": "How to vote?",
        "status": "Registered"
        # Missing 'location'
    }
    response = client.post("/ask", json=payload)
    assert response.status_code == 422 

def test_ask_length_validation():
    """Verify security constraint: Excessive string length gets rejected"""
    payload = {
        "question": "a" * 1000, # Max length is 500
        "location": "NY",
        "status": "Registered"
    }
    response = client.post("/ask", json=payload)
    assert response.status_code == 422

def test_ask_success_mocked(monkeypatch):
    """Verify standard logic flow when Gemini API processes query"""
    from backend.routes import ask
    
    # Mock LLM and Embeddings to run test without requiring a real API Key
    def mock_retrieve(*args, **kwargs):
        return ["Voting is important. Polling places open at 7am."]
        
    def mock_generate(*args, **kwargs):
        return ("This is a simple answer.", "Go to your local polling place.")
        
    monkeypatch.setattr(ask, "retrieve_top_k", mock_retrieve)
    monkeypatch.setattr(ask, "generate_answer", mock_generate)
    
    payload = {
        "question": "When do polls open?",
        "location": "NY",
        "status": "Registered"
    }
    
    response = client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "This is a simple answer."
    assert data["next_step"] == "Go to your local polling place."
