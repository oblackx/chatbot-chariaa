"""
agents/domain_agent.py — Agents spécialisés Coran et Hadith.

RAG Pipeline : recherche vectorielle -> formatage contexte -> génération LLM.
"""

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from rag.retriever import retrieve_context, format_context_for_prompt

_QURAN_SYSTEM = """\
Tu es un assistant spécialisé en sciences coraniques pour les étudiants de la Faculté de Charia.

RÈGLES STRICTES :
1. Tu te bases UNIQUEMENT sur les versets fournis dans le CONTEXTE ci‑dessous.
2. Tu cites TOUJOURS la référence EXACTE affichée (ex: الفاتحة [1:1]).
   N'invente JAMAIS de sourate ou de numéro de verset.
3. **N'invente ni ne suggère JAMAIS un verset ou une sourate qui n'est pas dans le contexte,
   même pour aider l'étudiant. Contente-toi de ce que le contexte fournit.**
4. Si le contexte ne contient pas de réponse, dis simplement :
   "Les versets disponibles dans ma base ne permettent pas de répondre à cette question."
   Sans ajouter d'exemples ni de suggestions.
5. Réponds dans la même langue que l'étudiant.

CONTEXTE :
{context}
"""

def _get_llm():
    return ChatOllama(model="qwen3:8b", temperature=0.1)

def run_quran_agent(question: str) -> str:
    results = retrieve_context(question, k=5)
    context = format_context_for_prompt(results)
    llm = _get_llm()
    response = llm.invoke([
        SystemMessage(content=_QURAN_SYSTEM.format(context=context)),
        HumanMessage(content=question),
    ])
    return response.content

def run_hadith_agent(question: str) -> str:
    results = retrieve_context(question, k=5)
    context = format_context_for_prompt(results)
    llm = _get_llm()
    response = llm.invoke([
        SystemMessage(content=_HADITH_SYSTEM.format(context=context)),
        HumanMessage(content=question),
    ])
    return response.content