from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.ask import router as ask_router
from backend.services.rag_pipeline import build_index
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup behavior: Build/ensure FAISS index exists
    print("Initializing FAISS index and mock data on startup...")
    build_index()
    yield
    # Shutdown behavior
    print("Shutting down VoteEasy API...")

app = FastAPI(
    title="VoteEasy API",
    description="Backend API for VoteEasy Voting Assistant",
    version="1.0.0",
    lifespan=lifespan
)

# Apply CORS middleware for security and frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to Streamlit's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ask_router)

@app.get("/")
def health_check():
    return {"status": "ok"}
