from typing import TypedDict, List, Optional, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    question: str
    question_embedding: List[float]
    intent: str
    next_agent: str
    retrieved_context: str
    sources: list
    answer: Optional[str]
    session_id: str
    messages: Annotated[list, add_messages]
    error: Optional[str]