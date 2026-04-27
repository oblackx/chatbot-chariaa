"""
agents/tools.py — Outils utilisés par les agents (recherche dans la base).
"""

from langchain_core.tools import tool
from rag.retriever import retrieve_context

@tool
def search_documents(query: str) -> str:
    """
    Cherche des informations dans les documents de la faculté.
    Retourne un bloc texte avec les versets et leurs références.
    """
    results = retrieve_context(query, k=5)
    if not results:
        return "Aucune information trouvée dans la base de connaissances."

    from rag.retriever import format_context_for_prompt
    return format_context_for_prompt(results)