from langchain_ollama import ChatOllama  # Importe le client ChatOllama pour le modèle de langage
from langgraph.prebuilt import create_react_agent  # Importe la fonction de création d'agent React
from agents.tools import search_documents  # Importe l'outil de recherche de documents

def create_quran_agent():  # Définit l'agent spécialisé dans les questions sur le Coran
    llm = ChatOllama(model="qwen3:8b", temperature=0)  # Crée une instance du modèle Ollama avec température nulle
    tools = [search_documents]  # Définit la liste des outils disponibles pour l'agent
    
    system_prompt = """  
    Tu es un expert du Coran, spécialisé dans les versets et les sourates.
    Ta mission est de répondre aux questions des étudiants sur le Coran en te basant EXCLUSIVEMENT sur les résultats de l'outil 'search_documents'.

    RÈGLES STRICTES :
    1. Utilise OBLIGATOIREMENT l'outil 'search_documents' pour chaque question.
    2. Si l'outil ne trouve rien, réponds : "Désolé, je n'ai pas trouvé cette information dans les sources coraniques disponibles. Veuillez contacter l'administration."
    3. N'invente JAMAIS de verset ou d'interprétation. N'utilise PAS tes connaissances générales.
    4. Réponds en arabe ou en français selon la langue de la question.
    5. Sois respectueux et précis.
    """  # Fin du prompt système
    
    agent = create_react_agent(  # Crée l'agent avec le modèle, les outils et le prompt fourni
        model=llm,
        tools=tools,
        prompt=system_prompt
    )
    return agent  # Retourne l'agent Coranique

def create_hadith_agent():  # Définit l'agent spécialisé dans les questions sur les hadiths
    llm = ChatOllama(model="qwen3:8b", temperature=0)  # Crée une instance du modèle Ollama avec température nulle
    tools = [search_documents]  # Définit la liste des outils disponibles pour l'agent
    
    system_prompt = """ 
    Tu es un expert en hadiths du Prophète Muhammad (que la paix soit sur lui).
    Ta mission est de répondre aux questions des étudiants sur les hadiths en te basant EXCLUSIVEMENT sur les résultats de l'outil 'search_documents'.

    RÈGLES STRICTES :
    1. Utilise OBLIGATOIREMENT l'outil 'search_documents' pour chaque question.
    2. Si l'outil ne trouve rien, réponds : "Désolé, je n'ai pas trouvé ce hadith dans les sources disponibles. Veuillez contacter l'administration."
    3. N'invente JAMAIS de hadith ou de chaîne de transmission. N'utilise PAS tes connaissances générales.
    4. Réponds en arabe ou en français selon la langue de la question.
    5. Mentionne la source si elle est disponible dans les résultats.
    """  # Fin du prompt système
    
    agent = create_react_agent(  # Crée l'agent avec le modèle, les outils et le prompt fourni
        model=llm,
        tools=tools,
        prompt=system_prompt
    )
    return agent  # Retourne l'agent Hadith