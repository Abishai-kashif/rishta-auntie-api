from typing_extensions import TypedDict
from pydantic import BaseModel

class UserProfile(TypedDict):
    name: str
    age: int
    location: str
    interests: list[str]
    gender: str

class History(BaseModel):
    role: str
    content: str

class PromptRequest(BaseModel):
    history: list[History] = []

class GuardrailOutput(BaseModel):
    """ 
        `is_relevant_query` indicates if the user's query is related to matches.
        `reasoning` provides the reasoning behind the decision.
    """
    is_relevant_query: bool
    reasoning: str