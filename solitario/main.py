from database.db import inizializza_db
from ui.cli import InterfacciaSolitario

def main():
    try:
        inizializza_db()    
        ui = InterfacciaSolitario()
        ui.esegui()
    except KeyboardInterrupt:
        print("\nGioco terminato dall'utente.")
    except Exception as e:
        print(f"\nSi è verificato un errore: {e}")

if __name__ == "__main__":
    main()