import re
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

_SUPERVISOR_PROMPT = """Tu es un superviseur chargé de router les questions des étudiants vers le bon agent.

Réponds UNIQUEMENT par l'un de ces deux tokens, sans aucun autre texte :
  [quran]  → si la question porte sur le Coran
  [hadith] → si la question porte sur les hadiths

En cas de doute ou de question générale sur l'Islam, réponds [quran].
N'ajoute aucune explication, aucun signe de ponctuation supplémentaire."""

def route_question(question: str) -> str:
    llm = ChatOllama(model="qwen3:8b", temperature=0)
    response = llm.invoke([
        SystemMessage(content=_SUPERVISOR_PROMPT),
        HumanMessage(content=question),
    ])
    content = response.content.strip()
    # Supprime les éventuelles balises <think>...</think>
    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
    content = content.lower()
    
    if "[hadith]" in content:
        return "hadith"
    return "quran"