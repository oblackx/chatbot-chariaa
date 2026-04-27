# main.py
# Point d'entrée du chatbot en ligne de commande.

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from graph.workflow import build_workflow
from langchain_core.messages import HumanMessage

def main():
    print("🚀 Démarrage du chatbot... Veuillez patienter.")
    app = build_workflow()
    print("✅ Chatbot prêt ! Tapez votre question (ou 'quit' pour quitter).\n")

    while True:
        question = input("👤 Vous : ")
        if question.lower() in ("quit", "exit", "q"):
            print("👋 Au revoir !")
            break

        initial_state = {
            "question": question,
            "messages": [HumanMessage(content=question)]
        }
        result = app.invoke(initial_state)
        reponse = result["messages"][-1].content
        print(f"🤖 Chatbot : {reponse}\n")

if __name__ == "__main__":
    main()