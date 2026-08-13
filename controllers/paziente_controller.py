"""
Gestisce le query relative all'elenco dei pazienti assegnati a un
diabetologo.

Corrisponde concettualmente al ramo 'diabetologo' del sequence diagram
Autenticazione.txt (Sistema --> utente: pazientiAssegnati), esteso con i
dati anagrafici necessari per mostrare l'elenco nella dashboard del
medico (nome/cognome, che vivono in utenti.csv e non in pazienti.csv).
"""

from config import CSV_PATHS
from models.data_manager import DataManager
from models.paziente import Paziente


class PazienteController:

    def __init__(self):
        self.dm_pazienti = DataManager(CSV_PATHS["pazienti"])
        self.dm_utenti = DataManager(CSV_PATHS["utenti"])

    def get_pazienti_assegnati(self, codice_medico: str) -> list[Paziente]:
        """
        Restituisce l'elenco dei pazienti assegnati al medico, come oggetti
        Paziente (non dict). Usa lo stesso Paziente.from_row() gia' usato
        da AuthController al login, che unisce i dati anagrafici di
        utenti.csv con l'associazione medico-paziente di pazienti.csv.
        """
        df_pazienti = self.dm_pazienti.read_all()
        df_utenti = self.dm_utenti.read_all()

        pazienti_assegnati = df_pazienti[df_pazienti["codiceMedicoRiferimento"] == codice_medico]

        pazienti = []
        for row_paziente in pazienti_assegnati.to_dict("records"):
            match_utente = df_utenti[df_utenti["codiceUtente"] == row_paziente["codiceUtente"]]
            if match_utente.empty:
                continue
            row_utente = match_utente.iloc[0].to_dict()
            pazienti.append(Paziente.from_row(row_utente, row_paziente))

        return pazienti
