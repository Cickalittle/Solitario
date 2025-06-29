import sqlite3
import hashlib
import getpass
from typing import Optional
from database.db import NOME_DB

class GestoreUtenti:
    """Gestisce l'autenticazione e la registrazione degli utenti"""
    def __init__(self):
        self.utente_corrente = None
    
    def registra(self, username: str, password: str = None) -> bool:
        """Registra un nuovo utente"""
        if not username:
            return False
        
        try:
            # Se password non è fornita, chiedila con getpass
            if password is None:
                password = getpass.getpass("Scegli una password: ")
            
            if not password:
                return False
            
            with sqlite3.connect(NOME_DB) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO utenti (username, password_hash) VALUES (?, ?)",
                    (username, self._hash_password(password))
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            print("Username già esistente.")
            return False
        except Exception as e:
            print(f"Errore durante la registrazione: {e}")
            return False
    
    def login(self, username: str, password: str = None) -> bool:
        """Effettua il login di un utente"""
        try:
            # Se password non è fornita, chiedila con getpass
            if password is None:
                password = getpass.getpass("Password: ")
            
            with sqlite3.connect(NOME_DB) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, password_hash FROM utenti WHERE username = ?",
                    (username,)
                )
                risultato = cursor.fetchone()
                
                if risultato and risultato[1] == self._hash_password(password):
                    self.utente_corrente = {
                        'id': risultato[0],
                        'username': username
                    }
                    return True
        except Exception as e:
            print(f"Errore durante il login: {e}")
        
        return False
    
    def logout(self):
        """Effettua il logout dell'utente corrente"""
        self.utente_corrente = None
    
    def e_loggato(self) -> bool:
        """Verifica se un utente è loggato"""
        return self.utente_corrente is not None
    
    def get_utente_corrente(self) -> dict | None:
        """Restituisce le informazioni dell'utente corrente"""
        return self.utente_corrente
    
    def _hash_password(self, password: str) -> str:
        """Hash della password (in un'app reale, usare bcrypt o PBKDF2)"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def get_punteggi_migliori(self, limite=15) -> list:
        """Restituisce i migliori punteggi dal database"""
        try:
            with sqlite3.connect(NOME_DB) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT u.username, pm.score, pm.duration, pm.achieved_at 
                    FROM punteggi_migliori pm
                    JOIN utenti u ON pm.user_id = u.id
                    ORDER BY pm.score DESC, pm.duration ASC
                    LIMIT ?
                """, (limite,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Errore nel recupero dei punteggi migliori: {e}")
            return []
    
    def get_sessioni_gioco(self, user_id: Optional[int] = None, limite=20) -> list:
        """Restituisce le sessioni di gioco dal database"""
        try:
            with sqlite3.connect(NOME_DB) as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT 
                        s.id, 
                        u.username, 
                        s.start_time, 
                        s.end_time, 
                        s.score, 
                        s.duration, 
                        s.won
                    FROM sessioni_gioco s
                    JOIN utenti u ON s.user_id = u.id
                """
                
                params = []
                
                if user_id is not None:
                    query += " WHERE s.user_id = ?"
                    params.append(user_id)
                
                query += " ORDER BY s.start_time DESC LIMIT ?"
                params.append(limite)
                
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Errore nel recupero delle sessioni di gioco: {e}")
            return []
