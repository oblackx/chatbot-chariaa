from typing import TypedDict, List, Optional, Annotated
from langgraph.graph.message import add_messages    

class AgentState(TypedDict):  # définit un type de dictionnaire pour l'état de l'agent
    question : str  # question posée à l'agent
    question_embedding : List[float]  # vecteur d'embedding de la question
    intent : str  # intention détectée
    next_agent : str  # identifiant de l'agent suivant
    retreived_context : str  # contexte récupéré
    source : list  # source(s) du contexte
    answer: Optional[str]  # réponse générée, optionnelle
    session_id : str  # identifiant de session
    messages:  Annotated[List, add_messages]  # liste de messages avec traitement add_messages
    error: Optional[str]  # message d'erreur optionnel
