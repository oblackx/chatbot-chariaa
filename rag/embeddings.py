from langchain_ollama import OllamaEmbeddings

def get_embed_model():
    return OllamaEmbeddings(model="nomic-embed-text")
