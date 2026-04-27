import sqlite3
import os

db_path = os.path.join("data", "quran_77432_database.sqlite")

if not os.path.exists(db_path):
    print(f"❌ Fichier introuvable : {db_path}")
    exit()

print(f" Analyse de {db_path}...")
conn = sqlite3.connect(db_path)

# Récupérer toutes les tables
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print(f"📋 {len(tables)} tables trouvées :\n")

for t in tables:
    table_name = t[0]
    cols = conn.execute(f"PRAGMA table_info('{table_name}')").fetchall()
    
    print(f" Table : {table_name} ({len(cols)} colonnes)")
    for col in cols:
        col_name = col[1]
        col_type = col[2]
        print(f"   • {col_name} ({col_type})")
    print()

conn.close()