from rag.embeddings import get_embed_model
from rag.database import get_connection
from pgvector import Vector

def retrieve_context(query: str, k: int = 3):
    embed_model = get_embed_model()
    query_vector = embed_model.embed_query(query)
    
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT content, metadata, 1 - (embedding <=> %s) AS similarity
        FROM document_chunks
        ORDER BY embedding <=> %s
        LIMIT %s;
    """, (Vector(query_vector), Vector(query_vector), k))
    
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return results