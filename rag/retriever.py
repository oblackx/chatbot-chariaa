"""
rag/retriever.py — Recherche vectorielle dans PostgreSQL/pgvector
et formattage du contexte avec métadonnées anti‑hallucination.
"""

import json
from rag.database import get_connection
from rag.embeddings import get_embed_model

def retrieve_context(query: str, k: int = 5) -> list[dict]:
    """
    Recherche les k versets les plus similaires à la requête.
    Retourne une liste de dicts avec :
        - content   : texte du verset
        - metadata  : dict contenant sourate_nom, sourate, verset, lieu, page
        - similarity: score de similarité cosinus
    """
    embed_model = get_embed_model()
    query_vector = embed_model.embed_query(query)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    content,
                    metadata,
                    1 - (embedding <=> %s::vector) AS similarity
                FROM document_chunks
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (query_vector, query_vector, k),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    results = []
    for content, metadata, similarity in rows:
        # metadata peut déjà être un dict si JSONB est parsé automatiquement
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        results.append({
            "content": content,
            "metadata": metadata or {},
            "similarity": round(float(similarity), 4),
        })
    return results

def format_context_for_prompt(results: list[dict]) -> str:
    """
    Formate les résultats en bloc texte structuré avec les vraies références.
    """
    if not results:
        return "Aucun résultat trouvé dans la base de données."

    lines = []
    for i, r in enumerate(results, 1):
        m = r["metadata"]

        sourate_num = m.get("sourate", "?")
        verse_num   = m.get("verset", "?")
        sourate_ar  = m.get("sourate_nom", "")
        lieu        = m.get("lieu", "")
        page        = m.get("page", "")

        reference = f"Sourate {sourate_ar} [{sourate_num}:{verse_num}]"
        if lieu:
            reference += f" — {lieu}"
        if page:
            reference += f", page {page}"

        lines.append(
            f"--- Résultat {i} | {reference} | Score : {r['similarity']} ---\n"
            f"{r['content']}"
        )

    return "\n\n".join(lines)