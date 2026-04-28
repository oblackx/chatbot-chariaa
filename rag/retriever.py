# rag/retriever.py — Recherche hybride : sémantique (pgvector) + exacte normalisée (SQL)

import json
from rag.database import get_connection
from rag.embeddings import get_embed_model


def retrieve_context(
    query: str,
    k: int = 5,
    keywords: list[str] | None = None,
) -> list[dict]:
    """
    Recherche hybride :

    1. Recherche SÉMANTIQUE via pgvector (distance cosinus) sur `query`.
       → `query` doit être la question complète pour une meilleure représentation
         vectorielle.  Un mot-clé court donne un vecteur pauvre.

    2. Recherche EXACTE normalisée sur chaque terme de `keywords`.
       → Les deux côtés du LIKE passent par normalize_arabic() pour neutraliser
         les diacritiques, les variantes de alif et la tâ' marbûta.
       → Si `keywords` est None, on utilise `query` comme unique mot-clé exact.

    Fusion : on garde le meilleur score par verset (score exact = 1.0 prime
    toujours sur le score sémantique).
    """
    # --- Embedding sur la question complète --------------------------------
    embed_model = get_embed_model()
    query_vector = embed_model.embed_query(query)

    # Si aucun mot-clé fourni, on utilise query comme seul terme exact
    search_terms = keywords if keywords else [query]

    conn = get_connection()
    try:
        with conn.cursor() as cur:

            # 1. Recherche sémantique (pgvector) ────────────────────────────
            cur.execute(
                """
                SELECT content, metadata,
                       1 - (embedding <=> %s::vector) AS similarity
                FROM document_chunks
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (query_vector, query_vector, k),
            )
            semantic_rows = cur.fetchall()

            # 2. Recherche exacte normalisée ─────────────────────────────────
            # RÈGLE psycopg2 : les % littéraux s'écrivent %% (sinon IndexError).
            # RÈGLE Arabic   : normalize_arabic() sur les DEUX côtés du LIKE.
            exact_rows: list[tuple] = []
            for term in search_terms:
                if not term or not term.strip():
                    continue
                cur.execute(
                    """
                    SELECT content, metadata, 1.0 AS similarity
                    FROM document_chunks
                    WHERE normalize_arabic(content)
                          LIKE '%%' || normalize_arabic(%s) || '%%'
                    LIMIT %s
                    """,
                    (term, k),
                )
                exact_rows.extend(cur.fetchall())

    finally:
        conn.close()

    # --- Fusion ─────────────────────────────────────────────────────────────
    combined: dict[str, dict] = {}
    for content, metadata, similarity in semantic_rows + exact_rows:
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        sim = round(float(similarity), 4)
        if content not in combined or sim > combined[content]["similarity"]:
            combined[content] = {
                "content": content,
                "metadata": metadata or {},
                "similarity": sim,
            }

    results = sorted(
        combined.values(), key=lambda x: x["similarity"], reverse=True
    )[:k]
    return results


def format_context_for_prompt(results: list[dict]) -> str:
    """
    Formate les résultats en un bloc texte structuré avec les vraies références
    (nom de la sourate, numéro de sourate, numéro de verset, lieu de révélation).
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