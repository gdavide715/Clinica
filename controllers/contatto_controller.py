"""Recupera i dati di contatto (email, nome) del diabetologo di un paziente, per il tab 'Contatta il Medico'."""

from config import CSV_PATHS
from models.data_manager import DataManager


class ContattoController:

    def __init__(self):
        self.dm_pazienti = DataManager(CSV_PATHS["pazienti"])
        self.dm_diabetologi = DataManager(CSV_PATHS["diabetologi"])
        self.dm_utenti = DataManager(CSV_PATHS["utenti"])

    def get_email_medico(self, codice_paziente: str) -> str | None:
        df_pazienti = self.dm_pazienti.read_all()
        paziente = df_pazienti[df_pazienti["codiceUtente"] == codice_paziente]
        if paziente.empty:
            return None

        codice_medico = paziente.iloc[0]["codiceMedicoRiferimento"]

        df_diabetologi = self.dm_diabetologi.read_all()
        medico = df_diabetologi[df_diabetologi["codiceUtente"] == codice_medico]
        if medico.empty:
            return None

        return medico.iloc[0]["email"]

    def get_nome_medico(self, codice_paziente: str) -> str | None:
        # nome/cognome del medico stanno in utenti.csv, non in diabetologi.csv
        df_pazienti = self.dm_pazienti.read_all()
        paziente = df_pazienti[df_pazienti["codiceUtente"] == codice_paziente]
        if paziente.empty:
            return None

        codice_medico = paziente.iloc[0]["codiceMedicoRiferimento"]

        df_utenti = self.dm_utenti.read_all()
        medico = df_utenti[df_utenti["codiceUtente"] == codice_medico]
        if medico.empty:
            return None

        return f"{medico.iloc[0]['nome']} {medico.iloc[0]['cognome']}"
