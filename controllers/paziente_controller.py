"""Elenco pazienti assegnati a un diabetologo (unisce utenti.csv e pazienti.csv)."""

from config import CSV_PATHS
from models.data_manager import DataManager
from models.paziente import Paziente


class PazienteController:

    def __init__(self):
        self.dm_pazienti = DataManager(CSV_PATHS["pazienti"])
        self.dm_utenti = DataManager(CSV_PATHS["utenti"])

    def get_pazienti_assegnati(self, codice_medico: str) -> list[Paziente]:
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
