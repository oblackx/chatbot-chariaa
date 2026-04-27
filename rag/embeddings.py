"""
rag/embeddings.py — Modèle d'embedding local nomic-embed-text via Ollama.
"""

from langchain_ollama import OllamaEmbeddings

def get_embed_model():
    """Retourne le modèle bge-m3 (768 dimensions, multilingue)."""
    return OllamaEmbeddings(model="bge-m3")
