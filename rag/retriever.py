from rag.embeddings import get_embed_model
from rag.database import get_connection

def retrieve_context(query: str, k: int = 3):
    embed_model = get_embed_model()
    query_vector = embed_model.embed_query(query)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT5 content, metadata, 
