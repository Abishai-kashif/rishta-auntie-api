from pydantic import BaseModel
from agents import TResponseInputItem

class PromptRequest(BaseModel):
    history: list[TResponseInputItem] = []

class GuardrailOutput(BaseModel):
    """ 
        `is_relevant_query` indicates if the user's query is related to matches.
        `reasoning` provides the reasoning behind the decision.
    """
    is_relevant_query: bool
    reasoning: str