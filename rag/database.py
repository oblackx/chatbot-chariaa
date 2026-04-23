import os
import psycopg2
from pgvector.psycopg2 import register_vector
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "admin123"),
        dbname=os.getenv("DB_NAME", "charia_db"),
    )
    register_vector(conn)
    return conn

def create_tables():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS document_chunks (
            id        BIGSERIAL PRIMARY KEY,
            content   TEXT NOT NULL,
            metadata  JSONB DEFAULT '{}',
            embedding VECTOR(768)
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("Tables créées avec succès !")