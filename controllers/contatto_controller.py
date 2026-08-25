"""
Gestisce il recupero dei dati di contatto (es. email) del diabetologo
di riferimento di un paziente.

NOTA: lo scambio dei messaggi NON e' gestito internamente all'applicativo.
Questo controller serve solo a recuperare l'indirizzo email del medico da
usare per precompilare un link "mailto:"/Gmail lato client (vedi
paziente_view.py, tab "Contatta il Medico").
"""

from config import CSV_PATHS
from models.data_manager import DataManager


class ContattoController:

    def __init__(self):
        self.dm_pazienti = DataManager(CSV_PATHS["pazienti"])
        self.dm_diabetologi = DataManager(CSV_PATHS["diabetologi"])
        self.dm_utenti = DataManager(CSV_PATHS["utenti"])

    def get_email_medico(self, codice_paziente: str) -> str | None:
        """
        Restituisce l'email del diabetologo di riferimento del paziente,
        oppure None se il paziente o il medico non vengono trovati.
        """
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
        """
        Restituisce nome e cognome del diabetologo di riferimento del
        paziente, oppure None se il paziente o il medico non vengono
        trovati. Il nome vive in utenti.csv, non in diabetologi.csv.
        """
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
