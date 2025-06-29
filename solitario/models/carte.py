import random
from enum import Enum
from colorama import Fore, Back, Style


class Seme(Enum):
    """Rappresenta i semi delle carte"""
    CUORI = '♥'
    QUADRI = '♦'
    FIORI = '♣'
    PICCHE = '♠'
    
    @property
    def colore(self):
        return 'rosso' if self in [Seme.CUORI, Seme.QUADRI] else 'nero'

class Valore(Enum):
    """Rappresenta i valori delle carte"""
    ASSO = 'A'
    DUE = '2'
    TRE = '3'
    QUATTRO = '4'
    CINQUE = '5'
    SEI = '6'
    SETTE = '7'
    OTTO = '8'
    NOVE = '9'
    DIECI = '10'
    JACK = 'J'
    DONNA = 'Q'
    RE = 'K'
    
    @classmethod
    def valori(cls):
        """Restituisce tutti i valori in ordine"""
        return [cls.ASSO, cls.DUE, cls.TRE, cls.QUATTRO, cls.CINQUE, 
                cls.SEI, cls.SETTE, cls.OTTO, cls.NOVE, cls.DIECI,
                cls.JACK, cls.DONNA, cls.RE]

class Carta:
    """Classe che rappresenta una singola carta da gioco"""
    def __init__(self, seme: Seme, valore: Valore):
        self.seme = seme
        self.valore = valore
        self.visibile = False 
    
    def __str__(self):
        if not self.visibile:
            return Fore.WHITE + Back.BLUE + Style.DIM + '[X]' + Style.RESET_ALL
        
        # Colori diversi per semi rossi e neri
        colore = Fore.RED + Back.WHITE + Style.BRIGHT if self.seme.colore == 'rosso' else Fore.BLACK + Back.WHITE + Style.BRIGHT
        return colore + f'[{self.valore.value}{self.seme.value}]' + Style.RESET_ALL
    
    def __repr__(self):
        return f'Carta({self.seme}, {self.valore}, visibile={self.visibile})'
    
    @property
    def colore(self):
        return self.seme.colore
    
    def gira(self):
        """Gira la carta (da coperta a scoperta o viceversa)"""
        self.visibile = not self.visibile
        return self
    
    def puo_stare_sopra(self, altra_carta) -> bool:
        """
        Verifica se questa carta può essere posizionata sopra un'altra carta nelle colonne di gioco
        Regole: colore alternato e valore inferiore di uno
        """
        if not altra_carta or not altra_carta.visibile:
            return False
        
        indice_valore_corrente = Valore.valori().index(self.valore)
        indice_valore_altra = Valore.valori().index(altra_carta.valore)
        
        return (self.colore != altra_carta.colore and 
                indice_valore_corrente == indice_valore_altra - 1)
    
    def puo_stare_su_fondazione(self, carta_fondazione) -> bool:
        """
        Verifica se questa carta può essere posizionata su una fondazione
        Regole: stesso seme e valore superiore di uno
        """
        if carta_fondazione is None:
            return self.valore == Valore.ASSO  # Solo gli assi possono iniziare una fondazione
        
        indice_valore_corrente = Valore.valori().index(self.valore)
        indice_valore_fondazione = Valore.valori().index(carta_fondazione.valore)
        
        return (self.seme == carta_fondazione.seme and 
                indice_valore_corrente == indice_valore_fondazione + 1)

class Mazzo:
    """Classe che rappresenta un mazzo di carte"""
    def __init__(self):
        self.carte: list[Carta] = []
        self._crea_mazzo()
        self.mescola()
    
    def _crea_mazzo(self):
        """Crea un mazzo standard di 52 carte"""
        self.carte = [Carta(seme, valore) 
                     for seme in Seme 
                     for valore in Valore]
    
    def mescola(self):
        """Mescola il mazzo"""
        random.shuffle(self.carte)
    
    def pesca(self) -> Carta:
        """Pesca una carta dal mazzo"""
        if not self.carte:
            self._crea_mazzo()
            self.mescola()
        return self.carte.pop()
    
    def e_vuoto(self) -> bool:
        """Verifica se il mazzo è vuoto"""
        return len(self.carte) == 0
    
    def __len__(self):
        return len(self.carte)

class Pila:
    """Classe per rappresentare una pila di carte (tableau, fondazioni, ecc.)"""
    def __init__(self):
        self.carte: list[Carta] = []
    
    def aggiungi_carta(self, carta: Carta):
        """Aggiunge una carta in cima alla pila"""
        self.carte.append(carta)
    
    def rimuovi_carta(self) -> Carta:
        """Rimuove e restituisce la carta in cima alla pila"""
        if not self.carte:
            raise IndexError("Pila vuota")
        return self.carte.pop()
    
    def carta_in_cima(self) -> Carta | None:
        """Restituisce la carta in cima alla pila senza rimuoverla"""
        return self.carte[-1] if self.carte else None
    
    def puo_aggiungere_carta(self, carta: Carta) -> bool:
        """Verifica se una carta può essere aggiunta a questa pila"""
        carta_in_cima = self.carta_in_cima()
        if carta_in_cima is None:
            return carta.valore == Valore.RE  # Solo i re possono stare su pile vuote
        return carta.puo_stare_sopra(carta_in_cima)
    
    def puo_aggiungere_sequenza(self, carte: list[Carta]) -> bool:
        """Verifica se una sequenza di carte può essere aggiunta a questa pila"""
        if not carte:
            return False
        
        # Verifica che la sequenza sia valida internamente
        for i in range(len(carte) - 1):
            if not carte[i].puo_stare_sopra(carte[i + 1]):
                return False
        
        # Verifica che la prima carta possa essere posizionata sulla pila
        return self.puo_aggiungere_carta(carte[0])
    
    def __len__(self):
        return len(self.carte)
    
    def __str__(self):
        return ' '.join(str(carta) for carta in self.carte)

class PilaFondazione(Pila):
    """Classe per le pile di fondazione"""
    def puo_aggiungere_carta(self, carta: Carta) -> bool:
        """Verifica se una carta può essere aggiunta alla fondazione"""
        carta_in_cima = self.carta_in_cima()
        return carta.puo_stare_su_fondazione(carta_in_cima)

class PilaStock(Pila):
    """Classe per lo stock (le carte coperte)"""
    def __init__(self):
        super().__init__()
        self.posizione = 0  # Per tenere traccia della carta corrente quando si sfogliano
    
    def prossima_carta(self) -> Carta | None:
        """Restituisce la prossima carta nello stock"""
        if not self.carte:
            return None
        
        if self.posizione >= len(self.carte):
            self.posizione = 0
        
        carta = self.carte[self.posizione]
        self.posizione += 1
        return carta
    
    def resetta(self):
        """Resetta la posizione corrente"""
        self.posizione = 0
