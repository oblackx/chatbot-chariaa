# 🕌 Chatbot Charia — Guide d'installation pas à pas (Windows)

Ce guide vous permet d'installer et de lancer le chatbot sur un PC Windows sans aucune configuration préalable.

---

## 📋 1. Prérequis (à installer une seule fois)

Téléchargez et installez les outils suivants avec les options par défaut : 

1. **Python 3.13** : [python.org/downloads](https://www.python.org/downloads/) (⚠️ **Cochez "Add Python to PATH"**).
2. **Git** : [git-scm.com/download/win](https://git-scm.com/download/win).
3. **Docker Desktop** : [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/).
4. **Ollama** : [ollama.com/download/windows](https://ollama.com/download/windows).

---

## 🛠️ 2. Installation des outils de gestion

Ouvrez un terminal **PowerShell** (Rechercher "PowerShell" dans Windows) et installez `uv` pour gérer les dépendances :

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"


🚀 3. Déploiement du Projet
Copiez et collez ces commandes dans votre terminal PowerShell :

A. Clonage et configuration
powershell
cd $env:USERPROFILE\Desktop
git clone https://github.com/oblackx/chatbot-chariaa.git chatbot-charia
cd chatbot-charia

# Création de l'environnement virtuel et installation
uv sync

# Création du fichier de configuration .env
@"
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=admin123
DB_NAME=charia_db
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
OLLAMA_EMBED_MODEL=bge-m3
"@ | Out-File -FilePath .env -Encoding UTF8
B. Lancement de la base de données et des modèles
Lancez Docker Desktop.

Dans le terminal :

powershell
docker compose up -d
ollama pull qwen3:8b
ollama pull bge-m3
uv run python rag/database.py
uv run python rag/create_normalize_function.py
5. Importation des Données
Cette étape vectorise le Coran et les Hadiths (cela peut prendre quelques minutes selon votre GPU/CPU).

A. Importation du Coran
Assurez-vous que le fichier data/quran_77432_database.sqlite est présent.

powershell
uv run python data/import_quran.py
B. Importation de Sahih Bukhari
Assurez-vous que les fichiers JSON sont dans data/bukhari_json/.

powershell
uv run python data/import_bukhari.py
6. Lancement du Chatbot
Mode Interface Web (Recommandé)
C'est l'interface élégante avec le design "Mosquée" :

powershell
uv run streamlit run app.py
Votre navigateur s'ouvrira automatiquement à l'adresse http://localhost:8501.

Mode Terminal
Pour un test rapide en ligne de commande :

powershell
uv run python main.py