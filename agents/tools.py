from langchain_core.tools import tool  
from rag.retriever import retrieve_context  

@tool  # décore la fonction pour en faire un outil LangChain
def search_documents(query: str) -> str:  # définit l'outil search_documents avec une entrée query de type str et une sortie str
    """
    Rechercher dans les documents officiels de la Faculté de Charia (cours, emplois du temps, bibliothèque, examens, annonces...).
    À utiliser dès qu'un étudiant pose une question sur la faculté.
    """
    results = retrieve_context(query, k=3)  # récupère les 3 contextes les plus pertinents pour la requête
    if not results:  # vérifie si aucun résultat n'a été trouvé
        return "Aucune information trouvée dans les documents de la faculté." \
        " Vous pouvez essayer de rechercher sur l'internet pour plus d'informations."  # renvoie un message par défaut si pas de résultats
    
    contexte = ""  # initialise la chaîne de texte qui contiendra le contexte assemblé
    for i, (content, metadata, score) in enumerate(results):  # parcourt chaque résultat avec son index, contenu, métadonnées et score
        contexte += f"--- Document {i+1} (similarité: {score:.2f}) ---\n{content}\n\n"  # ajoute chaque document formaté au contexte final
    return contexte  # renvoie le contexte assemblé