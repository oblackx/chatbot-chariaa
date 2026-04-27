from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

@tool
def transfer_to_agent(agent_name: str) -> str:
    """
    Transférer la question à un agent spécialisé.
    agent_name peut être : "quran" ou "hadith".
    """
    valid_agents = ["quran", "hadith"]
    if agent_name not in valid_agents:
        return f"Agent inconnu : {agent_name}. Agents disponibles : {', '.join(valid_agents)}"
    return f"Transfert vers l'agent {agent_name} effectué."

def create_supervisor_agent():
    llm = ChatOllama(model="qwen3:8b", temperature=0)
    tools = [transfer_to_agent]
    
    system_prompt = """
    Tu es le superviseur d'un système multi-agents pour la Faculté de Charia d'Aït Melloul.
    Ton rôle est d'analyser la question de l'étudiant et de décider quel agent spécialisé peut y répondre.

    Agents disponibles :
    - "quran" : pour les questions sur le Coran, les versets, leur interprétation, les sourates.
    - "hadith" : pour les questions sur les hadiths du Prophète (que la paix soit sur lui), leur authenticité, leur transmission.

    RÈGLES :
    1. Analyse la question et choisis l'agent le plus approprié.
    2. Utilise OBLIGATOIREMENT l'outil 'transfer_to_agent' avec le nom de l'agent choisi.
    3. Si la question ne correspond à aucun agent, réponds simplement : "Je ne peux pas répondre à cette question. Veuillez contacter l'administration."
    4. Ne réponds jamais directement à la question de l'étudiant, transfère-la toujours à l'agent compétent.
    """
    
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt
    )
    return agent