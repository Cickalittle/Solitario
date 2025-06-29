import os
import sqlite3

# Percorso della cartella 'data' nella root del progetto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

NOME_DB = os.path.join(DATA_DIR, "solitario.db")

def inizializza_db():
    with sqlite3.connect(NOME_DB) as conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS utenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Tabella sessioni di gioco
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessioni_gioco (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP,
            score INTEGER DEFAULT 0,
            duration INTEGER DEFAULT 0,
            won BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES utenti(id)
        )
        """)
        
        # Tabella punteggi migliori
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS punteggi_migliori (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            duration INTEGER NOT NULL,
            achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES utenti(id)
        )
        """)

        conn.commit()

def controllo_punteggio(user_id):
    with sqlite3.connect(NOME_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT score FROM punteggi_migliori WHERE user_id = ?
        """, (user_id,))
        risultati = cursor.fetchall()
        if risultati:
            score = risultati[0][0]
        else:
            score = 0        
        
        return score