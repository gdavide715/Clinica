"""
Implementa il sequence diagram "Autenticazione.txt":

Utente -> Sistema: login(username, pwd)
alt utente non esistente -> errore
alt paziente -> ritorna terapia
alt diabetologo -> ritorna pazientiAssegnati
"""

from config import CSV_PATHS
from models.data_manager import DataManager
from models.paziente import Paziente
from models.diabetologo import Diabetologo


class AuthController:

    def __init__(self):
        self.dm_utenti = DataManager(CSV_PATHS["utenti"])
        self.dm_pazienti = DataManager(CSV_PATHS["pazienti"])
        self.dm_diabetologi = DataManager(CSV_PATHS["diabetologi"])

    def login(self, username: str, password: str):
        
        # Restituisce (successo: bool, ruolo: str|None, oggetto_utente|messaggio_errore)
        
        df_utenti = self.dm_utenti.read_all()
        match = df_utenti[
            (df_utenti["username"] == username) & (df_utenti["password"] == password)
        ]

        if match.empty:
            return False, None, "Utente non esistente o credenziali errate."

        row = match.iloc[0].to_dict()

        if row["ruolo"] == "paziente":
            df_pazienti = self.dm_pazienti.read_all()
            row_paziente = df_pazienti[
                df_pazienti["codiceUtente"] == row["codiceUtente"]
            ].iloc[0].to_dict()
            paziente = Paziente.from_row(row, row_paziente)
            return True, "paziente", paziente

        # ruolo == diabetologo
        df_diabetologi = self.dm_diabetologi.read_all()
        match_medico = df_diabetologi[df_diabetologi["codiceUtente"] == row["codiceUtente"]]
        row_diabetologo = match_medico.iloc[0].to_dict() if not match_medico.empty else {"email": ""}

        diabetologo = Diabetologo.from_row(row, row_diabetologo)
        return True, "diabetologo", diabetologo
