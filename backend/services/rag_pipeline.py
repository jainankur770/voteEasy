import os
import json
import faiss
import numpy as np
import logging
from typing import List
from backend.services.scraper import load_data
from backend.services.embedding import get_embedding

logger = logging.getLogger(__name__)

INDEX_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "vectorstore", "faiss_index", "index.faiss")
CHUNKS_PATH = os.path.join(os.path.dirname(INDEX_PATH), "chunks.json")

FAQ_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "voter_faq.json")

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """Splits text into overlapping chunks of roughly `chunk_size` characters."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += (chunk_size - overlap)
    return chunks

def build_index() -> faiss.Index:
    """Builds and saves FAISS index along with chunk mappings from both scraped text and FAQ JSON."""
    all_chunks = []
    
    # 1. Load Scraped Data
    text = load_data()
    all_chunks.extend(chunk_text(text))
    
    # 2. Load FAQ Data
    if os.path.exists(FAQ_FILE):
        try:
            with open(FAQ_FILE, "r", encoding="utf-8") as f:
                faqs = json.load(f)
                for faq in faqs:
                    all_chunks.append(f"Q: {faq['question']}\nA: {faq['answer']}")
        except Exception as e:
            logger.error(f"Error loading FAQ data: {e}")

    dimension = 768 # Google's text-embedding-004 dimension
    index = faiss.IndexFlatL2(dimension)
    
    embeddings = []
    valid_chunks = []
    
    logger.info(f"Building index with {len(all_chunks)} chunks...")
    for chunk in all_chunks:
        if not chunk.strip():
            continue
        emb = get_embedding(chunk)
        if len(emb) == dimension:
            embeddings.append(emb)
            valid_chunks.append(chunk)
    
    if embeddings:
        np_embeddings = np.array(embeddings).astype('float32')
        index.add(np_embeddings)
        
        os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
        faiss.write_index(index, INDEX_PATH)
        
        with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
            json.dump(valid_chunks, f)
            
        logger.info(f"Index built and saved with {len(valid_chunks)} valid embeddings.")
        return index
    
    return faiss.IndexFlatL2(dimension)

def get_index() -> faiss.Index:
    """Loads existing index or builds a new one."""
    if os.path.exists(INDEX_PATH):
        try:
            return faiss.read_index(INDEX_PATH)
        except Exception:
            return build_index()
    return build_index()

def retrieve_top_k(query: str, k: int = 3) -> List[str]:
    """Retrieves top k chunks related to the query."""
    # Ensure chunks exist list
    if not os.path.exists(CHUNKS_PATH):
        build_index()
        
    try:
        with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
            valid_chunks = json.load(f)
    except FileNotFoundError:
        return []

    query_emb = get_embedding(query)
    # Validate query embedding dimension
    if len(query_emb) != 768:
        return []
        
    index = get_index()
    if index is None or index.ntotal == 0:
        return []

    np_query = np.array([query_emb]).astype('float32')
    # search top k
    distances, indices = index.search(np_query, min(k, index.ntotal))
    
    results = []
    for idx in indices[0]:
        if 0 <= idx < len(valid_chunks):
            results.append(valid_chunks[idx])
            
    return results
