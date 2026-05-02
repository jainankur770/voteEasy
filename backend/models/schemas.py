from pydantic import BaseModel, Field

class AskRequest(BaseModel):
    question: str = Field(..., max_length=500, description="The user's question about voting")
    location: str = Field(..., max_length=100, description="The user's location")
    status: str = Field(..., max_length=50, description="The user's registration status")

class AskResponse(BaseModel):
    answer: str = Field(..., description="The beginner-friendly answer")
    next_step: str = Field(..., description="The recommended next step for the user")
