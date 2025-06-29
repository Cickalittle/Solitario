import time
import random
from datetime import timedelta
from models.carte import Carta, Mazzo, Pila, PilaFondazione, PilaStock, Seme, Valore

class StatoGioco:
    """Classe per rappresentare uno stato del gioco per undo/redo"""
    def __init__(self, tableau, fondazioni, stock, scarti):
        self.tableau = [[carta for carta in pila.carte] for pila in tableau]
        self.fondazioni = {seme: [carta for carta in pila.carte] for seme, pila in fondazioni.items()}
        self.stock = [carta for carta in stock.carte]
        self.scarti = [carta for carta in scarti]
        self.posizione_stock = stock.posizione
        self.carte_visibili = self._get_carte_visibili(tableau)
        self.carte_coperte = self._get_carte_coperte(tableau)

    def _get_carte_visibili(self, tableau):
        """Restituisce un set di tutte le carte visibili nel tableau"""
        visibili = set()
        for pila in tableau:
            for carta in pila.carte:
                if carta.visibile:
                    visibili.add((carta.seme, carta.valore))
        return visibili

    def _get_carte_coperte(self, tableau):
        """Restituisce un set di tutte le carte coperte nel tableau"""
        coperte = set()
        for pila in tableau:
            for carta in pila.carte:
                if not carta.visibile:
                    coperte.add((carta.seme, carta.valore))
        return coperte

class GiocoSolitario:
    """Classe principale che gestisce la logica del gioco"""
    def __init__(self):
        self.mazzo = Mazzo()
        self.tableau: list[Pila] = [Pila() for _ in range(7)] 
        self.fondazioni: dict[Seme, PilaFondazione] = {
            seme: PilaFondazione() for seme in Seme
        }
        self.stock = PilaStock()
        self.scarti: list[Carta] = []
        self.stati_undo: list[StatoGioco] = []  # Stack per undo
        self.stati_redo: list[StatoGioco] = []  # Stack per redo
        self.tempo_inizio = None
        self.punteggio = 0
        self._distribuisci_carte()

    
    def _salva_stato(self):
        """Salva lo stato corrente del gioco nello stack undo"""
        stato = StatoGioco(
            self.tableau,
            self.fondazioni,
            self.stock,
            self.scarti
        )
        self.stati_undo.append(stato)
        self.stati_redo.clear()
    
    def annulla(self):
        """Annulla l'ultima mossa"""
        if not self.stati_undo:
            return False
        
        # Salva lo stato corrente nello stack redo
        stato_corrente = StatoGioco(
            self.tableau,
            self.fondazioni,
            self.stock,
            self.scarti
        )
        self.stati_redo.append(stato_corrente)
        
        # Ripristina lo stato precedente
        stato = self.stati_undo.pop()
        self._ripristina_stato(stato)
        
        # Penalità punteggio per undo
        self.punteggio = max(0, self.punteggio - 15)
        
        return True

    def ripeti(self):
        """Ripete l'ultima mossa annullata"""
        if not self.stati_redo:
            return False
        
        # Salva lo stato corrente nello stack undo
        stato_corrente = StatoGioco(
            self.tableau,
            self.fondazioni,
            self.stock,
            self.scarti
        )
        self.stati_undo.append(stato_corrente)
        
        # Ripristina lo stato successivo
        stato = self.stati_redo.pop()
        self._ripristina_stato(stato)

        return True
    
    def _ripristina_stato(self, stato: StatoGioco):
        """Ripristina lo stato del gioco da uno stato salvato"""
        # Ripristina tableau
        for i in range(7):
            self.tableau[i].carte = []
            for carta in stato.tableau[i]:
                # Ripristina lo stato originale della carta
                if (carta.seme, carta.valore) in stato.carte_visibili:
                    carta.visibile = True
                elif (carta.seme, carta.valore) in stato.carte_coperte:
                    carta.visibile = False
                self.tableau[i].aggiungi_carta(carta)
            
            # Assicura che solo l'ultima carta sia visibile
            if self.tableau[i].carte:
                for carta in self.tableau[i].carte[:-1]:
                    if (carta.seme, carta.valore) not in stato.carte_visibili:
                        carta.visibile = False
                self.tableau[i].carte[-1].visibile = True
        
        # Ripristina fondazioni
        for seme in Seme:
            self.fondazioni[seme].carte = [carta for carta in stato.fondazioni[seme]]
        
        # Ripristina stock e scarti
        self.stock.carte = [carta for carta in stato.stock]
        self.stock.posizione = stato.posizione_stock
        self.scarti = [carta for carta in stato.scarti]

    def _distribuisci_carte(self):
        """Distribuisce le carte per iniziare il gioco"""
        for i in range(7):
            for j in range(i + 1):
                carta = self.mazzo.pesca()
                if j == i:  # Ultima carta della colonna è visibile
                    carta.gira()
                self.tableau[i].aggiungi_carta(carta)
        
        # Le carte rimanenti vanno nello stock
        while not self.mazzo.e_vuoto():
            carta = self.mazzo.pesca()
            carta.gira()  # Le carte nello stock sono coperte
            self.stock.aggiungi_carta(carta)
        
        # Avvia il timer di gioco
        self.tempo_inizio = time.time()
    
    def pesca_dallo_stock(self):
        """Pesca una carta dallo stock"""
        self._salva_stato()
        
        if not self.stock.carte:
            if self.scarti:
                self._ripristina_stock()
            else:
                return
        
        carta = self.stock.prossima_carta()
        if carta:
            if not carta.visibile:
                carta.gira()

            self.scarti.append(carta) 
            self.stock.carte.remove(carta)
            if self.stock.posizione > 0:
                self.stock.posizione -= 1
            
            # Aggiorna punteggio per aver pescato una carta
            self.punteggio += 2

    def _ripristina_stock(self):
        """Ripristina lo stock dagli scarti (mescolando le carte e mettendole tutte coperte)"""
        if not self.scarti:
            return
            
        # Mette tutte le carte coperte
        for carta in self.scarti:
            if carta.visibile:
                carta.gira()
        
        # Mescola le carte
        random.shuffle(self.scarti)
        
        # Sposta tutte le carte nello stock
        for carta in self.scarti:
            self.stock.aggiungi_carta(carta)
            
        self.scarti = []
        self.stock.posizione = 0
        
        # Penalità punteggio per riciclo scarti
        self.punteggio = max(0, self.punteggio - 20)

    def autocompletamento(self) -> bool:
        """Tenta di completare automaticamente il gioco spostando tutte le carte possibili nelle fondazioni"""
        if not self._puo_autocompletare():
            return False
        
        self._salva_stato()
        
        mosse_effettuate = False
        # Continua a provare finché non ci sono più mosse possibili
        while True:
            mossa_effettuata = False
            
            # Controlla prima gli scarti
            if self.scarti:
                carta_scarti = self.scarti[-1]
                for seme in Seme:
                    fondazione = self.fondazioni[seme]
                    if fondazione.puo_aggiungere_carta(carta_scarti):
                        carta_mossa = self.scarti.pop()
                        fondazione.aggiungi_carta(carta_mossa)
                        self.punteggio += 15
                        mossa_effettuata = True
                        mosse_effettuate = True
                        break
            
            # Controlla tableau
            for pila in self.tableau:
                if pila.carte:
                    carta_in_cima = pila.carta_in_cima()
                    if carta_in_cima and carta_in_cima.visibile:
                        for seme in Seme:
                            fondazione = self.fondazioni[seme]
                            if fondazione.puo_aggiungere_carta(carta_in_cima):
                                carta_mossa = pila.rimuovi_carta()
                                fondazione.aggiungi_carta(carta_mossa)
                                self.punteggio += 5
                                mossa_effettuata = True
                                mosse_effettuate = True
                                
                                if pila.carte and not pila.carta_in_cima().visibile:
                                    pila.carta_in_cima().gira()
                                break
            
            if not mossa_effettuata:
                break
        
        return mosse_effettuate
    
    def _puo_autocompletare(self) -> bool:
        """Verifica se l'autocompletamento è permesso (scarti vuoti e tutte le carte scoperte)"""
        # Verifica se gli scarti sono vuoti
        if self.scarti:
            return False
        
        # Verifica se tutte le carte nel tableau sono scoperte
        for pila in self.tableau:
            for carta in pila.carte:
                if not carta.visibile:
                    return False
        
        return True
    
    def muovi_carta(self, sorgente: str, destinazione: str, conteggio: int) -> bool:
        """
        Sposta una carta o una sequenza di carte

        :param sorgente: Origine ('tableau1-7', 't1-7', '1-7', 'scarti', 's', 'foundation_<seme>', 'f_<seme>', '<seme>')
        :param destinazione: Destinazione ('tableau1-7', 't1-7', '1-7', 'foundation_<seme>', 'f_<seme>', '<seme>')
        :param conteggio: Numero di carte da spostare (solo per tableau)
        :return: True se la mossa è valida ed è stata eseguita
        """

        self._salva_stato()

        # Movimento da fondazione a tableau
        if sorgente.startswith('fondazione_') and destinazione.startswith('tableau'):
            # Estrai il seme dalla sorgente
            parti = sorgente.split('_')
            if len(parti) != 2:
                return False

            nome_seme = parti[1].lower()
            try:
                seme = next(s for s in Seme if s.name.lower() == nome_seme)
            except StopIteration:
                return False

            pila_fondazione = self.fondazioni[seme]
            if not pila_fondazione.carte:
                return False

            carta_da_spostare = pila_fondazione.carta_in_cima()

            # Ottieni la pila di destinazione
            idx_dest = int(destinazione[7:]) - 1
            if idx_dest < 0 or idx_dest >= 7:
                return False

            pila_destinazione = self.tableau[idx_dest]

            # Verifica le regole per lo spostamento
            carta_dest_in_cima = pila_destinazione.carta_in_cima()
            if carta_dest_in_cima is None:
                # Solo i re possono essere posizionati su un tableau vuoto
                if carta_da_spostare.valore != Valore.RE:
                    return False
            else:
                # Colori alternati e valore inferiore di uno
                if not carta_da_spostare.puo_stare_sopra(carta_dest_in_cima):
                    return False

            # Esegui lo spostamento
            carta_mossa = pila_fondazione.rimuovi_carta()
            pila_destinazione.aggiungi_carta(carta_mossa)

            # Aggiorna il punteggio (penalità per spostare dalla fondazione)
            self.punteggio = max(0, self.punteggio - 5)
            print(f"Spostata 1 carta da {sorgente} a {destinazione}.")
            return True
        
        # Movimento verso fondazione (sempre 1 carta)
        if destinazione.startswith('fondazione_'):
            pila_sorgente, carta_sorgente = self._get_sorgente(sorgente)
            if not carta_sorgente:
                print(f"Sorgente non valida: {sorgente}. Nessuna carta disponibile.")
                return False
            
            pila_destinazione = self._get_destinazione(destinazione)
            if pila_destinazione is None:
                print(f"ERRORE: Impossibile trovare la pila di destinazione per {destinazione}")
                return False

            # Verifica validità mossa
            carta_fondazione_in_cima = pila_destinazione.carta_in_cima()
            if carta_fondazione_in_cima is None:
                if carta_sorgente.valore != Valore.ASSO:
                    return False
            elif not carta_sorgente.puo_stare_su_fondazione(carta_fondazione_in_cima):
                return False
            
            # Esegui il movimento
            if sorgente == 'scarti':
                carta_mossa = self.scarti.pop()
                pila_destinazione.aggiungi_carta(carta_mossa)
                self.punteggio += 15
            elif sorgente.startswith('tableau'):
                idx = int(sorgente[7:]) - 1
                carta_mossa = self.tableau[idx].rimuovi_carta()
                pila_destinazione.aggiungi_carta(carta_mossa)
                self.punteggio += 5
                
                # Rivela l'ultima carta se la colonna non è vuota
                if self.tableau[idx].carte and not self.tableau[idx].carta_in_cima().visibile:
                    self.tableau[idx].carta_in_cima().gira()
            
            print(f"Spostata 1 carta da {sorgente} a {destinazione}.")
            return True
        
        # Movimento verso tableau
        elif destinazione.startswith('tableau'):
            pila_sorgente, carta_sorgente = self._get_sorgente(sorgente)
            if not carta_sorgente:
                print(f"Sorgente non valida: {sorgente}. Nessuna carta disponibile.")
                return False
            
            pila_destinazione = self._get_destinazione(destinazione)
            if pila_destinazione is None:
                print(f"ERRORE: Impossibile trovare la pila di destinazione per {destinazione}")
                return False

            # Spostamento singola carta (conteggio = 1)
            if conteggio == 1:
                # Verifica validità mossa
                carta_destinazione_in_cima = pila_destinazione.carta_in_cima()
                if carta_destinazione_in_cima is None:
                    if carta_sorgente.valore != Valore.RE:
                        return False
                elif not carta_sorgente.puo_stare_sopra(carta_destinazione_in_cima):
                    return False
                
                # Esegui il movimento
                if sorgente == 'scarti':
                    carta_mossa = self.scarti.pop()
                    pila_destinazione.aggiungi_carta(carta_mossa)
                    self.punteggio += 10
                elif sorgente.startswith('tableau'):
                    idx = int(sorgente[7:]) - 1
                    carta_mossa = self.tableau[idx].rimuovi_carta()
                    pila_destinazione.aggiungi_carta(carta_mossa)
                    
                    # Rivela l'ultima carta se la colonna non è vuota
                    if self.tableau[idx].carte and not self.tableau[idx].carta_in_cima().visibile:
                        self.tableau[idx].carta_in_cima().gira()
                
                print(f"Spostata 1 carta da {sorgente} a {destinazione}.")
                return True
            
            # Spostamento multiplo carte (conteggio > 1)
            elif conteggio > 1:
                if not sorgente.startswith('tableau'):
                    return False
                    
                idx = int(sorgente[7:]) - 1
                carte_visibili = [carta for carta in self.tableau[idx].carte if carta.visibile]
                
                # Verifica validità mossa
                if conteggio > len(carte_visibili):
                    return False

                # Verifica che la sequenza sia valida internamente
                for i in range(len(carte_visibili)-conteggio, len(carte_visibili)-1):
                    if not carte_visibili[i+1].puo_stare_sopra(carte_visibili[i]):
                        return False

                # Verifica che la prima carta possa essere posizionata sul target
                prima_carta_da_spostare = carte_visibili[-conteggio]
                carta_destinazione_in_cima = pila_destinazione.carta_in_cima()

                if carta_destinazione_in_cima is None:
                    if prima_carta_da_spostare.valore != Valore.RE:
                        return False
                elif not prima_carta_da_spostare.puo_stare_sopra(carta_destinazione_in_cima):
                    return False
                
                # Esegui il movimento
                carte_mosse = []
                for _ in range(conteggio):
                    if self.tableau[idx].carte:
                        carte_mosse.append(self.tableau[idx].rimuovi_carta())
                
                # Aggiungi le carte in ordine inverso per mantenere la sequenza corretta
                for carta in reversed(carte_mosse):
                    pila_destinazione.aggiungi_carta(carta)
                
                # Rivela l'ultima carta se la colonna non è vuota
                if self.tableau[idx].carte and not self.tableau[idx].carta_in_cima().visibile:
                    self.tableau[idx].carta_in_cima().gira()
                
                print(f"Spostate {conteggio} carte da {sorgente} a {destinazione}.")
                return True
        
        return False

    def _get_sorgente(self, sorgente: str) -> tuple[Pila | None, Carta | None]:
        """Restituisce la pila e la carta sorgente"""
        
        if sorgente == 'scarti':
            if not self.scarti:
                return None, None
            return None, self.scarti[-1]
        
        if sorgente.startswith('tableau'):
            idx = int(sorgente[7:]) - 1
            if idx < 0 or idx >= 7 or not self.tableau[idx].carte:
                return None, None
            return self.tableau[idx], self.tableau[idx].carta_in_cima()
        
        if sorgente.startswith('fondazione_'):
            parti = sorgente.split('_')
            if len(parti) != 2:
                return None, None
                
            nome_seme = parti[1].lower()  
            
            try:
                for seme in Seme:
                    if seme.name.lower() == nome_seme:
                        return self.fondazioni[seme], self.fondazioni[seme].carta_in_cima()
                return None, None
            except:
                return None, None
        
        return None, None
    
    def _get_destinazione(self, destinazione: str) -> Pila | None:
        """Restituisce la pila di destinazione"""
        
        if destinazione.startswith('tableau'):
            idx = int(destinazione[7:]) - 1
            if idx < 0 or idx >= 7:
                return None
            return self.tableau[idx]
        
        if destinazione.startswith('fondazione_'):
            parti = destinazione.split('_')
            if len(parti) != 2:
                return None
                
            nome_seme = parti[1].lower()  
            
            try:
                for seme in Seme:
                    if seme.name.lower() == nome_seme:
                        return self.fondazioni[seme]
                return None
            except:
                return None
        
        return None
    
    def get_tempo_trascorso(self) -> int:
        """Restituisce il tempo trascorso in secondi"""
        if not self.tempo_inizio:
            return 0
        return int(time.time() - self.tempo_inizio)
    
    def formatta_tempo(self, secondi: int) -> str:
        """Formatta i secondi in HH:MM:SS"""
        return str(timedelta(seconds=secondi))
    
    def ha_vinto(self) -> bool:
        """Verifica se il giocatore ha vinto"""
        return all(len(pila) == 13 for pila in self.fondazioni.values())
    
    def get_stato_gioco(self) -> dict:
        """Restituisce lo stato corrente del gioco per la visualizzazione"""
        return {
            'tableau': [{'carte': pila.carte, 'conteggio': len(pila)} for pila in self.tableau],
            'fondazioni': {seme.name: {'in_cima': pila.carta_in_cima(), 'conteggio': len(pila)} 
                            for seme, pila in self.fondazioni.items()},
            'scarti': self.scarti[-1] if self.scarti else None,  # Mostra solo l'ultima carta degli scarti
            'conteggio_stock': len(self.stock.carte),
            'conteggio_scarti': len(self.scarti),
            'punteggio': self.punteggio,
            'tempo': self.get_tempo_trascorso()
        }

    def calcola_punteggio_finale(self) -> int:
        """Calcola il punteggio finale con bonus/penalità di tempo"""
        trascorso = self.get_tempo_trascorso()
        minuti = trascorso // 60
        
        # Punteggio base
        punteggio_finale = self.punteggio
        
        # Bonus completamento
        punteggio_finale += 100
        
        # Bonus tempo
        if minuti < 5:
            punteggio_finale += 350
        elif minuti < 10:
            punteggio_finale += 250
        elif minuti < 15:
            punteggio_finale += 150
        elif minuti < 20:
            punteggio_finale += 50
        
        # Penalità tempo (dopo 20 minuti)
        if trascorso > 1200:  # 20 minuti
            punteggio_finale -= ((trascorso - 1200) // 30) # 1 punto ogni 30 secondi 
        
        return max(0, punteggio_finale)
    