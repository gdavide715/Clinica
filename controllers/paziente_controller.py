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


class PazienteController:

    def __init__(self):
        self.dm_pazienti = DataManager(CSV_PATHS["pazienti"])
        self.dm_utenti = DataManager(CSV_PATHS["utenti"])

    def get_pazienti_assegnati(self, codice_medico: str) -> list[dict]:
        """
        Restituisce l'elenco dei pazienti assegnati al medico, con i dati
        anagrafici (nome, cognome) gia' uniti a partire da utenti.csv.
        """
        df_pazienti = self.dm_pazienti.read_all()
        df_utenti = self.dm_utenti.read_all()

        pazienti_assegnati = df_pazienti[df_pazienti["codiceMedicoRiferimento"] == codice_medico]

        pazienti_completi = pazienti_assegnati.merge(
            df_utenti[["codiceUtente", "nome", "cognome"]], on="codiceUtente", how="left"
        )

        return pazienti_completi.to_dict("records")
