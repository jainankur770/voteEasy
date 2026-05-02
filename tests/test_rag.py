import os
from backend.services.rag_pipeline import chunk_text

def test_chunking_logic():
    """Verify efficiency constraint: texts are chunked cleanly and safely."""
    sample_text = "This is a short sample string to test the chunking functionality of the rag pipeline."
    # Chunk by exactly 20 chars with 5 char overlap for testing
    chunks = chunk_text(sample_text, chunk_size=20, overlap=5)
    
    assert len(chunks) > 0
    assert len(chunks[0]) == 20
    assert chunks[0] == "This is a short samp"
    assert "samp" in chunks[1]  # Verify overlap
