from pydantic import BaseModel

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