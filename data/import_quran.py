# import_quran.py
# Importe les versets du Coran depuis la base SQLite du Pr. Qasimi
# vers notre base PostgreSQL/pgvector.

import sqlite3, json, sys
from pathlib import Path

# Permet de lancer le script depuis n'importe quel dossier
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.embeddings import get_embed_model
from rag.database import get_connection
from pgvector import Vector

# --- CONFIGURATION ---
FICHIER_SQLITE = "data/quran_77432_database.sqlite"
NOM_TABLE = "Quran_MetaData_Khair_77432"

def importer_coran():
    """Extrait les versets uniques de la base SQLite et les vectorise."""

    # 1. Lecture de la source SQLite
    print("📖 Connexion à la base SQLite...")
    conn_sql = sqlite3.connect(FICHIER_SQLITE)
    curseur = conn_sql.cursor()

    # Chaque ligne = un mot. On regroupe par sourate + verset.
    requete = f"""
        SELECT DISTINCT
            "رقم السورة", "اسم السورة", "رقم الاية في السورة",
            "نص الآية  بالتشكيل", "مكية أو مدنية", "رقم الصفحة من القرآن"
        FROM {NOM_TABLE}
        ORDER BY "رقم السورة", "رقم الاية في السورة"
    """
    curseur.execute(requete)
    versets = curseur.fetchall()
    curseur.close()
    conn_sql.close()
    print(f"   → {len(versets)} versets uniques extraits.")

    # 2. Préparation des outils de vectorisation et de la base cible
    modele = get_embed_model()             # nomic-embed-text (local Ollama)
    conn_pg = get_connection()            # PostgreSQL + pgvector
    curseur_pg = conn_pg.cursor()

    # 3. Insertion des versets
    for i, v in enumerate(versets):
        num_s, nom_s, num_a, texte, lieu, page = v

        # Vectorise le texte arabe (768 dimensions)
        vec = modele.embed_query(texte)

        # Métadonnées en JSON (pour filtrage futur)
        meta = {
            "source": "Coran",
            "sourate": num_s,
            "sourate_nom": nom_s,
            "verset": num_a,
            "lieu": lieu,
            "page": page
        }

        curseur_pg.execute(
            "INSERT INTO document_chunks (content, metadata, embedding) VALUES (%s, %s, %s)",
            (texte, json.dumps(meta, ensure_ascii=False), Vector(vec))
        )

        # Barre de progression tous les 1000 versets
        if i % 1000 == 0:
            print(f"   ⏳ {i}/{len(versets)} versets traités...")

    # 4. Sauvegarde et nettoyage
    conn_pg.commit()
    curseur_pg.close()
    conn_pg.close()
    print(f"🎉 Terminé ! {len(versets)} versets ajoutés à document_chunks.")

if __name__ == "__main__":
    importer_coran()