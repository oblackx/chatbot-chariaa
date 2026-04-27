"""
graph/workflow.py — Graphe LangGraph final.
"""

from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage

from graph.state import AgentState
from agents.supervisor import route_question
from agents.domain_agent import run_quran_agent, run_hadith_agent

def node_supervisor(state: AgentState) -> dict:
    dest = route_question(state["question"])
    return {"destination": dest}

def node_quran(state: AgentState) -> dict:
    answer = run_quran_agent(state["question"])
    return {"messages": [AIMessage(content=answer)]}

def node_hadith(state: AgentState) -> dict:
    answer = run_hadith_agent(state["question"])
    return {"messages": [AIMessage(content=answer)]}

def _router(state: AgentState) -> str:
    return state.get("destination", "quran")

def build_workflow():
    graph = StateGraph(AgentState)
    graph.add_node("supervisor", node_supervisor)
    graph.add_node("quran_agent", node_quran)
    graph.add_node("hadith_agent", node_hadith)
    graph.set_entry_point("supervisor")
    graph.add_conditional_edges("supervisor", _router, {"quran": "quran_agent", "hadith": "hadith_agent"})
    graph.add_edge("quran_agent", END)
    graph.add_edge("hadith_agent", END)
    return graph.compile()