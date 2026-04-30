"""
data/import_bukhari.py
======================
Import Sahih Bukhari (7345 hadiths) from JSON → PostgreSQL + pgvector

Structure de la table :
  - content   : matn arabe (Arabic_Matn)
  - metadata  : chapitre, section, numéro, isnad, grade...
  - embedding : vecteur bge-m3 (768 dims) via Ollama

Usage :
  uv run python data/import_bukhari.py
  uv run python data/import_bukhari.py --dry-run   # teste sans insérer
"""

import json
import glob
import os
import sys
import argparse
import time
from pathlib import Path

# ── Ajoute le répertoire racine au path ──────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag.database import get_connection
from rag.embeddings import get_embed_model


# ── Chemin vers les fichiers JSON Bukhari ────────────────────────────────────
JSON_DIR = Path(__file__).parent / "bukhari_json"   # copier les json_files/ ici

# Fallback : cherche dans les emplacements courants
FALLBACK_DIRS = [
    Path(__file__).parent / "json_files",
    Path(__file__).parent.parent / "json_files",
]


def find_json_dir() -> Path:
    if JSON_DIR.exists():
        return JSON_DIR
    for d in FALLBACK_DIRS:
        if d.exists():
            return d
    raise FileNotFoundError(
        f"Dossier JSON introuvable. Copie les fichiers Bukhari dans : {JSON_DIR}"
    )


def load_all_hadiths(json_dir: Path) -> list[dict]:
    """Charge tous les hadiths depuis les fichiers Chapter*.json"""
    files = sorted(
        json_dir.glob("Chapter*.json"),
        key=lambda f: float(f.stem.replace("Chapter", ""))
    )
    if not files:
        raise FileNotFoundError(f"Aucun fichier Chapter*.json dans {json_dir}")

    all_hadiths = []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            all_hadiths.extend(data)
        except Exception as e:
            print(f"  ⚠️  {f.name} : {e}")

    print(f"✅ {len(all_hadiths)} hadiths chargés depuis {len(files)} fichiers")
    return all_hadiths


def build_content(h: dict) -> str:
    """
    Construit le texte à stocker + embedder.
    On utilise le Matn arabe (sans isnad) car c'est le texte du hadith lui-même.
    L'isnad est gardé dans les métadonnées.
    """
    matn = (h.get("Arabic_Matn") or "").strip()
    if not matn or matn == "nan":
        # Fallback sur le hadith complet si le matn est vide
        matn = (h.get("Arabic_Hadith") or "").strip()
    return matn


def build_metadata(h: dict) -> dict:
    """Construit les métadonnées structurées pour un hadith."""
    def clean(v):
        s = str(v).strip() if v is not None else ""
        return "" if s == "nan" else s

    return {
        "source":           "bukhari",
        "hadith_number":    clean(h.get("Hadith_number")),
        "chapter_number":   clean(h.get("Chapter_Number")),
        "chapter_arabic":   clean(h.get("Chapter_Arabic")),
        "chapter_english":  clean(h.get("Chapter_English")),
        "section_number":   clean(h.get("Section_Number")),
        "section_arabic":   clean(h.get("Section_Arabic")),
        "section_english":  clean(h.get("Section_English")),
        "isnad_arabic":     clean(h.get("Arabic_Isnad")),
        "matn_english":     clean(h.get("English_Matn")),
        "grade_arabic":     clean(h.get("Arabic_Grade")),
        "grade_english":    clean(h.get("English_Grade")),
    }


def import_hadiths(dry_run: bool = False, batch_size: int = 50):
    json_dir = find_json_dir()
    print(f"📂 Source JSON : {json_dir}")

    hadiths = load_all_hadiths(json_dir)

    # Filtre les hadiths sans matn arabe
    valid = [(build_content(h), build_metadata(h)) for h in hadiths]
    valid = [(c, m) for c, m in valid if c]
    print(f"✅ {len(valid)} hadiths avec matn arabe valide")

    if dry_run:
        print("\n🔍 DRY-RUN — 3 exemples :")
        for content, meta in valid[:3]:
            print(f"\n  [{meta['hadith_number']}] {meta['chapter_arabic']}")
            print(f"  Matn : {content[:120]}...")
            print(f"  Grade: {meta['grade_arabic']}")
        print(f"\n✅ Dry-run terminé — {len(valid)} hadiths prêts à importer")
        return

    # ── Embedding model ──────────────────────────────────────────────────────
    print("\n🤖 Chargement du modèle d'embedding (bge-m3)...")
    embed_model = get_embed_model()

    # ── Connexion DB ─────────────────────────────────────────────────────────
    conn = get_connection()
    cur = conn.cursor()

    # Vérifie si des hadiths Bukhari existent déjà
    cur.execute(
        "SELECT COUNT(*) FROM document_chunks WHERE metadata->>'source' = 'bukhari'"
    )
    existing = cur.fetchone()[0]
    if existing > 0:
        print(f"⚠️  {existing} hadiths Bukhari déjà dans la base.")
        answer = input("Supprimer et réimporter ? [o/N] ").strip().lower()
        if answer == "o":
            cur.execute(
                "DELETE FROM document_chunks WHERE metadata->>'source' = 'bukhari'"
            )
            conn.commit()
            print("🗑️  Anciens hadiths supprimés.")
        else:
            print("❌ Import annulé.")
            conn.close()
            return

    # ── Import par batchs ────────────────────────────────────────────────────
    total    = len(valid)
    inserted = 0
    errors   = 0
    t0       = time.time()

    print(f"\n🚀 Import de {total} hadiths (batch={batch_size})...\n")

    for i in range(0, total, batch_size):
        batch = valid[i : i + batch_size]
        contents = [c for c, _ in batch]
        metas    = [m for _, m in batch]

        try:
            vectors = embed_model.embed_documents(contents)
        except Exception as e:
            print(f"  ❌ Batch {i//batch_size + 1} — embedding échoué : {e}")
            errors += len(batch)
            continue

        for content, meta, vector in zip(contents, metas, vectors):
            try:
                cur.execute(
                    """
                    INSERT INTO document_chunks (content, metadata, embedding)
                    VALUES (%s, %s::jsonb, %s::vector)
                    """,
                    (content, json.dumps(meta, ensure_ascii=False), vector),
                )
                inserted += 1
            except Exception as e:
                print(f"  ⚠️  hadith {meta.get('hadith_number')} : {e}")
                errors += 1

        conn.commit()
        elapsed = time.time() - t0
        speed   = inserted / elapsed if elapsed > 0 else 0
        eta     = (total - inserted) / speed if speed > 0 else 0
        print(
            f"  [{inserted:>5}/{total}] "
            f"batch {i//batch_size + 1:>3} — "
            f"{speed:.1f} hadiths/s — "
            f"ETA {eta/60:.1f} min"
        )

    cur.close()
    conn.close()

    elapsed = time.time() - t0
    print(f"\n{'='*55}")
    print(f"✅ Import terminé en {elapsed/60:.1f} minutes")
    print(f"   Insérés : {inserted}")
    print(f"   Erreurs : {errors}")
    print(f"{'='*55}")
    print("\n💡 Pour tester :")
    print("   uv run python data/import_bukhari.py --verify")


def verify():
    """Vérifie le contenu importé."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM document_chunks WHERE metadata->>'source' = 'bukhari'"
    )
    count = cur.fetchone()[0]
    print(f"✅ {count} hadiths Bukhari dans document_chunks")

    cur.execute(
        """
        SELECT content, metadata
        FROM document_chunks
        WHERE metadata->>'source' = 'bukhari'
        ORDER BY metadata->>'hadith_number'
        LIMIT 3
        """
    )
    rows = cur.fetchall()
    print("\n3 exemples :")
    for content, meta in rows:
        print(f"\n  [{meta.get('hadith_number')}] "
              f"{meta.get('chapter_arabic')} — {meta.get('grade_arabic')}")
        print(f"  {content[:150]}...")

    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import Bukhari → PostgreSQL")
    parser.add_argument("--dry-run",  action="store_true", help="Teste sans insérer")
    parser.add_argument("--verify",   action="store_true", help="Vérifie l'import")
    parser.add_argument("--batch",    type=int, default=50, help="Taille du batch")
    args = parser.parse_args()

    if args.verify:
        verify()
    else:
        import_hadiths(dry_run=args.dry_run, batch_size=args.batch)