"""
graph/state.py — État partagé du graphe LangGraph.
"""

import operator
from typing import Annotated, Optional
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    question: str
    messages: Annotated[list[BaseMessage], operator.add]
    destination: Optional[str]