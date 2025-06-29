import time
import sys
import os
import sqlite3
from datetime import datetime, timedelta
from colorama import Fore, Style
from database.db import controllo_punteggio, NOME_DB
from models.gioco import GiocoSolitario
from models.utenti import GestoreUtenti
from models.carte import Carta, Seme

class InterfacciaSolitario:
    """Classe che gestisce l'interfaccia utente del gioco"""
    def __init__(self):
        self.gioco = None
        self.gestore_utenti = GestoreUtenti()
    
    def pulisci_schermo(self):
        """Pulisce lo schermo della console"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def anima_testo(self, testo: str, ritardo: float = 0.03):
        """Anima la stampa del testo con ritardo tra i caratteri"""
        for char in testo:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(ritardo)
        print()
    
    def mostra_schermata_titolo(self):
        """Mostra la schermata del titolo con ASCII art"""
        self.pulisci_schermo()
        titolo = r"""
 ______   _______ _   _  ___  _   _   ____   ___  _     ___ _____  _    ___ ____  _____ 
|  _ \ \ / /_   _| | | |/ _ \| \ | | / ___| / _ \| |   |_ _|_   _|/ \  |_ _|  _ \| ____|
| |_) \ V /  | | | |_| | | | |  \| | \___ \| | | | |    | |  | | / _ \  | || |_) |  _|  
|  __/ | |   | | |  _  | |_| | |\  |  ___) | |_| | |___ | |  | |/ ___ \ | ||  _ <| |___ 
|_|    |_|   |_| |_| |_|\___/|_| \_| |____/ \___/|_____|___| |_/_/   \_\___|_| \_\_____|                                                                                         
        """
        print(Fore.YELLOW + titolo + Style.RESET_ALL)
        print(f"{Fore.CYAN}Benvenuto in Solitario Python!{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}Usa il menu qui sotto per iniziare.{Style.RESET_ALL}\n")
    
    def mostra_benvenuto(self):
        """Mostra la schermata di benvenuto"""
        self.mostra_schermata_titolo()
        print("1. Login")
        print("2. Registrati")
        print("3. Gioca come Ospite")
        print("4. Visualizza Punteggi Migliori")
        print("5. Visualizza Sessioni di Gioco")
        print("6. Come Guadagnare Punti")
        print("7. Tutorial Interattivo")
        print("8. Esci")
        
        # Mostra l'utente corrente se loggato
        if self.gestore_utenti.e_loggato():
            utente = self.gestore_utenti.get_utente_corrente()
            print(f"\n{Fore.GREEN}Loggato come: {utente['username']}{Style.RESET_ALL}")
        print(f"{Fore.RED}\nPremi 'q' durante il gioco per tornare a questo menu{Style.RESET_ALL}")

    def mostra_caricamento(self, messaggio: str = "Caricamento", durata: float = 1.0):
        """Mostra un'animazione di caricamento"""
        self.pulisci_schermo()
        print(messaggio, end="", flush=True)
        for _ in range(5):
            print(".", end="", flush=True)
            time.sleep(durata / 5)
        print()
    
    def mostra_animazione_carta(self, carta: Carta, messaggio: str):
        """Mostra una semplice animazione di carta senza pulire lo schermo"""
        print(f"\n{messaggio}")
        print(" " * 20 + str(carta))
        time.sleep(0.3)  # Ridotto il tempo di attesa
    
    def gestisci_autenticazione(self):
        """Gestisce il flusso di autenticazione dell'utente"""
        while True:
            self.mostra_benvenuto()
            scelta = input("Seleziona un'opzione: ").strip()
            
            if scelta == '1':  # Login
                username = input("Username: ").strip()
                if self.gestore_utenti.login(username):
                    self.mostra_caricamento(f"Bentornato, {username}")
                    time.sleep(0.5)
                    return  # Torna al gioco
                else:
                    print("Username o password non validi.")
                    time.sleep(1)
            
            elif scelta == '2':  # Registrazione
                username = input("Scegli un username: ").strip()
                if self.gestore_utenti.registra(username):
                    self.mostra_caricamento("Registrazione completata! Accesso in corso...")
                    self.gestore_utenti.login(username)
                    time.sleep(0.5)
                    return  # Torna al gioco
                else:
                    print("Registrazione fallita. Prova con un username diverso.")
                    time.sleep(1)
            
            elif scelta == '3':  # Gioca come ospite
                self.mostra_caricamento("Avvio come ospite")
                time.sleep(0.5)
                return  # Torna al gioco
            
            elif scelta == '4':  # Visualizza punteggi migliori
                self.mostra_punteggi_migliori()
                input("\nPremi Invio per continuare...")
            
            elif scelta == '5':  # Visualizza sessioni di gioco
                self.mostra_sessioni_gioco()

            elif scelta == '6':  # Info punteggio
                self.mostra_info_punteggio()

            elif scelta == '7':  # Tutorial 
                self.mostra_tutorial()

            elif scelta == '8':  # Esci
                raise SystemExit("Arrivederci!")
    
    def mostra_punteggi_migliori(self):
        """Mostra i punteggi migliori con ASCII art"""
        self.pulisci_schermo()
        print(Fore.YELLOW + r"""
 _   _ ___ ____ _   _   ____   ____ ___  ____  _____ ____  
| | | |_ _/ ___| | | | / ___| / ___/ _ \|  _ \| ____/ ___| 
| |_| || | |  _| |_| | \___ \| |  | | | | |_) |  _| \___ \ 
|  _  || | |_| |  _  |  ___) | |__| |_| |  _ <| |___ ___) |
|_| |_|___\____|_| |_| |____/ \____\___/|_| \_\_____|____/ 
        """ + Style.RESET_ALL)
        
        punteggi = self.gestore_utenti.get_punteggi_migliori()
        if not punteggi:
            print("\nAncora nessun punteggio migliore!")
            return
        
        print(f"\n{'Pos':<5}{'Giocatore':<15}{'Punteggio':<10}{'Tempo':<15}{'Data'}")
        print("-" * 50)
        for i, (username, punteggio, durata, data_ottenimento) in enumerate(punteggi, 1):
            str_tempo = timedelta(seconds=durata)
            str_data = datetime.strptime(data_ottenimento, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
            print(f"{i:<5}{Fore.CYAN}{username:<15}{Style.RESET_ALL}{Fore.GREEN}{punteggio:<10}{Style.RESET_ALL}{str_tempo!s:<15}{str_data}")

    def mostra_sessioni_gioco(self):
        """Mostra la tabella delle sessioni di gioco"""
        self.pulisci_schermo()
        print(Fore.YELLOW + r"""
  ____    _    __  __ _____   ____  _____ ____ ____ ___ ___  _   _ ____  
 / ___|  / \  |  \/  | ____| / ___|| ____/ ___/ ___|_ _/ _ \| \ | / ___| 
| |  _  / _ \ | |\/| |  _|   \___ \|  _| \___ \___ \| | | | |  \| \___ \ 
| |_| |/ ___ \| |  | | |___   ___) | |___ ___) |__) | | |_| | |\  |___) |
 \____/_/   \_\_|  |_|_____| |____/|_____|____/____/___\___/|_| \_|____/ 
        """ + Style.RESET_ALL)
        
        # Se l'utente è loggato, mostra solo le sue sessioni, altrimenti mostra tutte
        user_id = None
        if self.gestore_utenti.e_loggato():
            user_id = self.gestore_utenti.get_utente_corrente()['id']
        
        sessioni = self.gestore_utenti.get_sessioni_gioco(user_id)
        
        if not sessioni:
            print("\nNessuna sessione di gioco trovata.")
            input("\nPremi Invio per continuare...")
            return
        
        print(f"\n{'ID':<5}{'Utente':<15}{'Inizio':<20}{'Fine':<20}{'Punteggio':<10}{'Durata':<12}{'Risultato'}")
        print("-" * 90)
        
        for sessione in sessioni:
            id_sess, username, inizio, fine, punteggio, durata, vinto = sessione
            str_inizio = datetime.strptime(inizio, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M")
            str_fine = datetime.strptime(fine, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M") if fine else "In corso"
            str_durata = str(timedelta(seconds=durata)) if durata else "-"
            risultato = f"{Fore.GREEN}Vittoria{Style.RESET_ALL}" if vinto else f"{Fore.RED}Sconfitta{Style.RESET_ALL}"
            
            print(f"{id_sess:<5}{Fore.CYAN}{username:<15}{Style.RESET_ALL}{str_inizio:<20}{str_fine:<20}{punteggio:<10}{str_durata:<12}{risultato}")
        
        input("\nPremi Invio per continuare...")


    def mostra_info_punteggio(self):
        """Mostra informazioni sul sistema di punteggio"""
        self.pulisci_schermo()
        print(Fore.YELLOW + r"""
 ____   ____ ___  ____  ___ _   _  ____   ____   ___ ___ _   _ _____ ____  
/ ___| / ___/ _ \|  _ \|_ _| \ | |/ ___| |  _ \ / _ \_ _| \ | |_   _/ ___| 
\___ \| |  | | | | |_) || ||  \| | |  _  | |_) | | | | ||  \| | | | \___ \ 
 ___) | |__| |_| |  _ < | || |\  | |_| | |  __/| |_| | || |\  | | |  ___) |
|____/ \____\___/|_| \_\___|_| \_|\____| |_|    \___/___|_| \_| |_| |____/ 
        """ + Style.RESET_ALL)
        
        print(f"\n{Fore.CYAN}Nuovo Sistema di Punteggio:{Style.RESET_ALL}\n")
        print(f"{Fore.GREEN}+10 punti{Style.RESET_ALL} - Per ogni carta spostata da scarti a tableau")
        print(f"{Fore.GREEN}+15 punti{Style.RESET_ALL} - Per ogni carta spostata da scarti a fondazione")
        print(f"{Fore.GREEN}+5 punti{Style.RESET_ALL}  - Per ogni carta spostata da tableau a fondazione")
        print(f"{Fore.GREEN}+5 punti{Style.RESET_ALL}  - Per scoprire una carta coperta nel tableau")
        print(f"{Fore.GREEN}+2 punti{Style.RESET_ALL}  - Per ogni carta pescata dallo stock")
        print(f"{Fore.GREEN}+100 punti{Style.RESET_ALL} - Bonus per completamento il gioco")
        print(f"\n{Fore.RED}-15 punti{Style.RESET_ALL} - Per ogni operazione di annullamento")
        print(f"{Fore.RED}-20 punti{Style.RESET_ALL} - Per riciclare gli scarti nello stock")
        print(f"{Fore.RED}-5 punti{Style.RESET_ALL} - Per spostare una carta dalla fondazione al tableau")
        
        print("\n" + Fore.MAGENTA + "Bonus/Penalità Tempo:")
        print("0-5 minuti: +350 punti")
        print("5-10 minuti: +250 punti")
        print("10-15 minuti: +150 punti")
        print("15-20 minuti: +50 punti")
        print("20+ minuti: -1 punto ogni 30 secondi oltre i 20 minuti" + Style.RESET_ALL)
        
        input("\nPremi Invio per tornare al menu principale...")

    def salva_risultato_gioco(self, vinto: bool = False) -> None:
        """Salva il risultato del gioco nel database"""
        if not self.gestore_utenti.e_loggato():
            return
        
        id_utente = self.gestore_utenti.get_utente_corrente()['id']
        durata = self.gioco.get_tempo_trascorso()
        punteggio = self.gioco.calcola_punteggio_finale()
        
        try:
            with sqlite3.connect(NOME_DB) as conn:
                cursor = conn.cursor()
                
                # Salva nelle sessioni di gioco
                cursor.execute("""
                    INSERT INTO sessioni_gioco (user_id, start_time, end_time, score, duration, won)
                    VALUES (?, datetime('now'), datetime('now'), ?, ?, ?)
                """, (id_utente, punteggio, durata, vinto))

                # Se vinto, salva nei punteggi migliori
                if vinto:
                    score = controllo_punteggio()
                    if score == 0:
                        cursor.execute("""
                            INSERT INTO punteggi_migliori (user_id, score, duration) 
                            VALUES (?, ?, ?)
                        """, (id_utente, punteggio, durata))
                    elif punteggio > score:
                        cursor.execute("""
                            DELETE FROM punteggi_migliori WHERE user_id = ?
                            """, (id_utente,))
                        cursor.execute("""
                            INSERT INTO punteggi_migliori (user_id, score, duration) 
                            VALUES (?, ?, ?)
                        """, (id_utente, punteggio, durata))
                    else:
                        pass
                   
        except Exception as e:
            print(f"Errore nel salvataggio del risultato: {e}")
    
    def mostra_gioco(self):
        """Mostra lo stato corrente del gioco con allineamento perfetto"""
        if not self.gioco:
            return
            
        stato = self.gioco.get_stato_gioco()
        self.pulisci_schermo()
        
        output = []

        # Intestazione con info gioco
        intestazione = f"{Fore.YELLOW}┌────────────────────────────────────────────────────────────┐{Style.RESET_ALL}"
        piè_di_pagina = f"{Fore.YELLOW}└────────────────────────────────────────────────────────────┘{Style.RESET_ALL}"
        
        # Info giocatore e statistiche
        info_giocatore = ""
        if self.gestore_utenti.e_loggato():
            utente = self.gestore_utenti.get_utente_corrente()
            info_giocatore = f" {Fore.CYAN}Giocatore:{Style.RESET_ALL} {utente['username']:<15} "

        statistiche = f"{Fore.CYAN}Punteggio:{Style.RESET_ALL} {stato['punteggio']:<5} {Fore.CYAN}Tempo:{Style.RESET_ALL} {self.gioco.formatta_tempo(stato['tempo'])}"
        spazio_rimanente = 30 - len(info_giocatore) - len(statistiche)        
        spaziatura = " " * (spazio_rimanente // 2)
        
        output.append(intestazione)
        output.append(f"{Fore.YELLOW}│{Style.RESET_ALL}{info_giocatore}{spaziatura}{statistiche}{Fore.YELLOW}{Style.RESET_ALL}")
        output.append(piè_di_pagina)
        
        # Fondazioni - versione con allineamento perfetto
        output.append(f"\n{Fore.MAGENTA}╒═══════════════════════════════════════════════════════════╕{Style.RESET_ALL}")
        output.append(f"{Fore.MAGENTA}│{Style.RESET_ALL} {Fore.CYAN}Fondazioni:{Style.RESET_ALL}")
        
        # Calcola la larghezza massima delle carte per allineamento
        larghezza_max_carta = 4
        
        # Prima riga (CUORI e QUADRI)
        cuori = stato['fondazioni']['CUORI']
        quadri = stato['fondazioni']['QUADRI']
        carta_c = str(cuori['in_cima']) if cuori['in_cima'] else '[  ]'
        carta_q = str(quadri['in_cima']) if quadri['in_cima'] else '[  ]'
        
        output.append(f"{Fore.MAGENTA}│{Style.RESET_ALL} "
            f"CUORI:   {carta_c:<{larghezza_max_carta}} ({cuori['conteggio']:>2}/13 )   "
            f"QUADRI: {carta_q:<{larghezza_max_carta}} ({quadri['conteggio']:>2}/13 )")
        
        # Seconda riga (FIORI e PICCHE)
        fiori = stato['fondazioni']['FIORI']
        picche = stato['fondazioni']['PICCHE']
        carta_f = str(fiori['in_cima']) if fiori['in_cima'] else '[  ]'
        carta_p = str(picche['in_cima']) if picche['in_cima'] else '[  ]'
        
        output.append(f"{Fore.MAGENTA}│{Style.RESET_ALL} "
            f"FIORI:   {carta_f:<{larghezza_max_carta}} ({fiori['conteggio']:>2}/13 )   "
            f"PICCHE: {carta_p:<{larghezza_max_carta}} ({picche['conteggio']:>2}/13 )")
        
        # Stock e Scarti
        stock_scarti = f"{Fore.CYAN}Stock:{Style.RESET_ALL}         ( {stato['conteggio_stock']:02d} )    {Fore.CYAN}Scarti:{Style.RESET_ALL} "
        if self.gioco.scarti:
            stock_scarti += f"{self.gioco.scarti[-1]}  ( {len(self.gioco.scarti):02d} )"
        else:
            stock_scarti += "[  ]  ( 00 )"
        
        output.append(f"{Fore.MAGENTA}│{Style.RESET_ALL} {stock_scarti}")
        output.append(f"{Fore.MAGENTA}╘═══════════════════════════════════════════════════════════╛{Style.RESET_ALL}")
        
        # Tableau con allineamento perfetto
        output.append(f"\n{Fore.MAGENTA}╒═══════════════════════════════════════════════════════════╕{Style.RESET_ALL}")
        output.append(f"{Fore.MAGENTA}│{Style.RESET_ALL} {Fore.CYAN}Tableau:{Style.RESET_ALL}")
    
        for i, pila in enumerate(stato['tableau'], 1):
            str_pila = f"{i}: " + " ".join(str(carta) for carta in pila['carte'])
            output.append(f"{Fore.MAGENTA}│{Style.RESET_ALL} {str_pila}")
    
        output.append(f"{Fore.MAGENTA}╘═══════════════════════════════════════════════════════════╛{Style.RESET_ALL}")

        output.append(f"\n{Fore.GREEN}╒═══════════════════════════════════════════════════════════╕{Style.RESET_ALL}")
        output.append(f"{Fore.GREEN}│{Style.RESET_ALL} {Fore.YELLOW}Comandi:{Style.RESET_ALL}")
        output.append(f"{Fore.GREEN}│{Style.RESET_ALL} - {Fore.CYAN}(p){Style.RESET_ALL}esca dallo stock")
        output.append(f"{Fore.GREEN}│{Style.RESET_ALL} - {Fore.CYAN}(m){Style.RESET_ALL}uovi carte (es. 'm scarti fondazione_cuori')")
        output.append(f"{Fore.GREEN}│{Style.RESET_ALL} - {Fore.CYAN}(a){Style.RESET_ALL}utocompletamento (quando possibile)")
        output.append(f"{Fore.GREEN}│{Style.RESET_ALL} - {Fore.CYAN}(u){Style.RESET_ALL}ndo ultima mossa")
        output.append(f"{Fore.GREEN}│{Style.RESET_ALL} - {Fore.CYAN}(r){Style.RESET_ALL}edo ultima mossa annullata")
        output.append(f"{Fore.GREEN}│{Style.RESET_ALL} - {Fore.CYAN}(q){Style.RESET_ALL}uit esci dal gioco")
        output.append(f"{Fore.GREEN}│{Style.RESET_ALL} {Fore.YELLOW}Sintassi mossa:{Style.RESET_ALL} m <sorgente> <destinazione> [conteggio]")
        output.append(f"{Fore.GREEN}│{Style.RESET_ALL} {Fore.YELLOW}Sorgenti:{Style.RESET_ALL} scarti/s, tableau1-7/1-7, fondazione_<seme>/<seme>")
        output.append(f"{Fore.GREEN}│{Style.RESET_ALL} {Fore.YELLOW}Destinazioni:{Style.RESET_ALL} fondazione_<seme>/<seme>, tableau1-7/1-7")

        output.append(f"{Fore.GREEN}╘═══════════════════════════════════════════════════════════╛{Style.RESET_ALL}")
        
        # Stampa tutto in una volta
        print("\n".join(output))
    
    def elabora_comando(self, comando: str) -> str:
        """Elabora il comando dell'utente
        Restituisce:
            'continua' - continua il gioco
            'menu' - torna al menu principale
            'esci' - esci dal gioco
        """
        if not comando:
            return 'continua'
        
        if comando == 'q':
            return 'menu'  # Torna al menu principale
        
        if comando == 'p':
            self.gioco.pesca_dallo_stock()
            return 'continua'
        
        if comando == 'a':
            if self.gioco.autocompletamento():
                print(f"\n{Fore.GREEN}Autocompletamento riuscito!{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}Impossibile autocompletare ora. Assicurati che gli scarti siano vuoti e tutte le carte scoperte.{Style.RESET_ALL}")
            time.sleep(1)
            return 'continua'
        
        if comando == 'u':
            if self.gioco.annulla():
                print(f"\n{Fore.GREEN}Annullamento riuscito!{Style.RESET_ALL}")
            else:
                print("\nNiente da annullare.")
            time.sleep(0.3)
            return 'continua'
        
        if comando == 'r':
            if self.gioco.ripeti():
                print(f"\n{Fore.GREEN}Ripetizione riuscita!{Style.RESET_ALL}")
            else:
                print("\nNiente da ripetere.")
            time.sleep(0.3)
            return 'continua'
        
        if comando.startswith('m'):
            parti = comando.split()
            if len(parti) < 3:
                print("\nComando di movimento non valido. Uso: m <sorgente> <destinazione> [conteggio]")
                return 'continua'
            
            sorgente = self._normalizza_comando(str(parti[1]))
            destinazione = self._normalizza_comando(str(parti[2]))
            conteggio = 1
            
            if len(parti) > 3:
                try:
                    conteggio = int(parti[3])
                except ValueError:
                    print("\nConteggio non valido. Uso 1.")
                    conteggio = 1
            
            if not self._valida_parametri_mossa(sorgente, destinazione):
                return 'continua'
            
            if not self.gioco.muovi_carta(sorgente, destinazione, conteggio):
                print(f"\n{Fore.RED}Mossa non valida! Controlla le regole.{Style.RESET_ALL}")
                time.sleep(1)
            
            return 'continua'

        print(f"\n{Fore.RED}Comando sconosciuto{Style.RESET_ALL}")
        time.sleep(0.5)
        return 'continua'
    
    def _normalizza_comando(self, comando: str) -> str:
        """Normalizza i comandi in input per gestire forme abbreviate e alternative"""
        if not comando:
            return comando
            
        comando = comando.lower().strip()
        
        # Gestione tableau (1-7 o tableau1-7)
        if comando.isdigit() and 1 <= int(comando) <= 7:
            return f"tableau{comando}"
        if comando.startswith("t") and comando[1:].isdigit() and 1 <= int(comando[1:]) <= 7:
            return f"tableau{comando[1:]}"
        
        # Gestione fondazione (seme o f_seme o foundation_seme)
        if comando in ["cuori", "quadri", "picche", "fiori"]:
            return f"fondazione_{comando}"
        if comando.startswith(("f_", "fondazione_")):
            seme = comando.split("_")[-1]
            if seme in ["cuori", "quadri", "picche", "fiori"]:
                return f"fondazione_{seme}"
        
        # Gestione scarti (s o scarti)
        if comando in ["s", "scarti"]:
            return "scarti"
            
        return comando

    def _valida_parametri_mossa(self, sorgente: str, destinazione: str) -> bool:
        """Verifica che i parametri di movimento siano validi"""
        sorgenti_valide = ['scarti'] + [f'tableau{i}' for i in range(1, 8)] + [f'fondazione_{seme.name.lower()}' for seme in Seme]
        destinazioni_valide = [f'fondazione_{seme.name.lower()}' for seme in Seme] + [f'tableau{i}' for i in range(1, 8)]
        
        if sorgente not in sorgenti_valide:
            print(f"\nSorgente non valida. Deve essere una di: {', '.join(sorgenti_valide)}")
            return False
        
        if destinazione not in destinazioni_valide:
            print(f"\nDestinazione non valida. Deve essere una di: {', '.join(destinazioni_valide)}")
            return False
        
        return True
    
    def esegui(self):
        """Esegue il loop principale del gioco"""
        while True:
            # Mostra il menu principale
            self.gestisci_autenticazione()
            
            # Se arriviamo qui, l'utente ha scelto di giocare (login/ospite)
            self.gioco = GiocoSolitario()
            
            # Loop di gioco
            while True:
                self.mostra_gioco()
                
                if self.gioco.ha_vinto():
                    self._mostra_messaggio_vittoria()
                    self.salva_risultato_gioco(True)
                    break
                
                try:
                    comando = input(f"{Fore.RED}>>>{Style.RESET_ALL} ").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    print("\nGioco terminato dall'utente.")
                    return
                
                risultato = self.elabora_comando(comando)
                
                if risultato == 'menu':
                    self.salva_risultato_gioco(False)
                    break  # Torna al menu principale
                elif risultato == 'esci':
                    self.salva_risultato_gioco(False)
                    print("\nGrazie per aver giocato!")
                    return
            
            # Chiedi se vuoi giocare di nuovo solo se la partita è finita naturalmente
            if self.gioco.ha_vinto():
                scelta = input("\nGiocare ancora? (s/n): ").strip().lower()
                if scelta != 's':
                    print("\nGrazie per aver giocato!")
                    return

    def _mostra_messaggio_vittoria(self):
        """Mostra il messaggio di vittoria con ASCII art"""
        trascorso = self.gioco.get_tempo_trascorso()
        str_tempo = self.gioco.formatta_tempo(trascorso)
        punteggio_finale = self.gioco.calcola_punteggio_finale()
        
        self.pulisci_schermo()
        print(Fore.GREEN + r"""
  ____ ___  _   _  ____ ____      _  _____ _   _ _        _  _____ ___ ___  _   _ 
 / ___/ _ \| \ | |/ ___|  _ \    / \|_   _| | | | |      / \|_   _|_ _/ _ \| \ | |
| |  | | | |  \| | |  _| |_) |  / _ \ | | | | | | |     / _ \ | |  | | | | |  \| |
| |__| |_| | |\  | |_| |  _ <  / ___ \| | | |_| | |___ / ___ \| |  | | |_| | |\  |
 \____\___/|_| \_|\____|_| \_\/_/   \_\_|  \___/|_____/_/   \_\_| |___\___/|_| \_|
        """ + Style.RESET_ALL)
        
        print(" " * 20 + f"{Fore.YELLOW}╔════════════════════════════════╗{Style.RESET_ALL}")
        print(" " * 20 + f"{Fore.YELLOW}║{Style.RESET_ALL}         {Fore.CYAN}COMPLIMENTI!{Style.RESET_ALL}           {Fore.YELLOW}║{Style.RESET_ALL}")
        print(" " * 20 + f"{Fore.YELLOW}║{Style.RESET_ALL}          {Fore.GREEN}HAI VINTO!{Style.RESET_ALL}            {Fore.YELLOW}║{Style.RESET_ALL}")
        print(" " * 20 + f"{Fore.YELLOW}╠════════════════════════════════╣{Style.RESET_ALL}")
        print(" " * 20 + f"{Fore.YELLOW}║{Style.RESET_ALL} {Fore.CYAN}Punteggio Base:{Style.RESET_ALL} {self.gioco.punteggio:<15}{Fore.YELLOW}║{Style.RESET_ALL}")
        print(" " * 20 + f"{Fore.YELLOW}║{Style.RESET_ALL} {Fore.CYAN}Punteggio Finale:{Style.RESET_ALL} {punteggio_finale:<13}{Fore.YELLOW}║{Style.RESET_ALL}")
        print(" " * 20 + f"{Fore.YELLOW}║{Style.RESET_ALL} {Fore.CYAN}Tempo:{Style.RESET_ALL} {str_tempo!s:<20} {Fore.YELLOW}   ║{Style.RESET_ALL}")
        print(" " * 20 + f"{Fore.YELLOW}╚════════════════════════════════╝{Style.RESET_ALL}")
        
        print("\n" + " " * 15 + "Tutte le carte sono state spostate nelle rispettive fondazioni.")
        input("\nPremi Invio per continuare...")

    def mostra_tutorial(self):
        """Mostra un tutorial interattivo passo-passo"""
        self.pulisci_schermo()
        print(Fore.YELLOW + r"""
 _____ _   _ _____ ___  ____  ___    _    _     
|_   _| | | |_   _/ _ \|  _ \|_ _|  / \  | |    
  | | | | | | | || | | | |_) || |  / _ \ | |    
  | | | |_| | | || |_| |  _ < | | / ___ \| |___ 
  |_|  \___/  |_| \___/|_| \_\___/_/   \_\_____|
        """ + Style.RESET_ALL)
        
        input("\nPremi Invio per iniziare il tutorial...")
        
        # Passo 1: Introduzione
        self.pulisci_schermo()
        print(f"{Fore.CYAN}=== INTRODUZIONE AL SOLITARIO ==={Style.RESET_ALL}\n")
        print("Lo scopo del gioco è spostare tutte le carte nelle 4 fondazioni")
        print("(una per seme) in ordine dall'Asso al Re.\n")
        input("\nPremi Invio per continuare...")
        
        # Passo 2: Tableau
        self.pulisci_schermo()
        print(f"{Fore.CYAN}=== IL TABLEAU ==={Style.RESET_ALL}\n")
        print("Le 7 colonne in basso sono il tableau. Puoi spostare le carte:")
        print("- Le carte devono essere di colore alternato (rosso/nero)")
        print("- Devono essere in ordine decrescente (Re, Donna, Jack, 10, ...)\n")
        print("Esempio: puoi mettere il 9♠ (nero) sul 10♦ (rosso)")
        input("\nPremi Invio per continuare...")
        
        # Passo 3: Fondazioni
        self.pulisci_schermo()
        print(f"{Fore.CYAN}=== LE FONDAZIONI ==={Style.RESET_ALL}\n")
        print("Le fondazioni si costruiscono dall'Asso al Re, tutte dello stesso seme.")
        print("Esempio: A♥ → 2♥ → 3♥ → ... → K♥")
        input("\nPremi Invio per continuare...")
        
        # Passo 4: Stock e Scarti
        self.pulisci_schermo()
        print(f"{Fore.CYAN}=== STOCK E SCARTI ==={Style.RESET_ALL}\n")
        print("Lo stock contiene le carte coperte rimanenti.")
        print("Premi 'p' per pescare una carta dallo stock.")
        print("Le carte pescate vanno negli scarti e possono essere usate.")
        input("\nPremi Invio per continuare...")
        
        # Passo 5: Comandi
        self.pulisci_schermo()
        print(f"{Fore.CYAN}=== COMANDI PRINCIPALI ==={Style.RESET_ALL}\n")
        print("p - Pesca una carta dallo stock")
        print("m - Muovi carte (es: 'm scarti fondazione_cuori')")
        print("a - Autocompletamento (quando possibile)")
        print("u - Annulla ultima mossa")
        print("r - Ripeti ultima mossa annullata")
        print("q - Torna al menu principale")
        input("\nPremi Invio per terminare il tutorial...")
