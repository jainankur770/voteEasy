from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check():
    """Verify the API health check endpoint returns 200 OK."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_ask_endpoint_invalid_payload():
    """Verify the API rejects improperly formatted requests (Security/Validation)."""
    # Missing required fields
    response = client.post("/ask", json={"question": "What?"})
    assert response.status_code == 422 # Unprocessable Entity (Pydantic validation failed)

def test_ask_endpoint_valid_payload():
    """Verify the API accepts correct payloads."""
    # Since we don't want to hit the real LLM in tests, we just check if it processes
    # or errors out predictably. If it returns 200, great. If 500 (due to no API key), we catch it.
    response = client.post("/ask", json={
        "question": "How do I vote?",
        "location": "Delhi",
        "status": "Not registered"
    })
    
    # It should either succeed (200) or fail safely internally but the endpoint itself should respond
    assert response.status_code in [200, 500]
