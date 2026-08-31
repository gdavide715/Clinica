from dataclasses import dataclass
from datetime import date

from models.utente import Utente


@dataclass
class Paziente(Utente):
    codiceMedicoRiferimento: str = ""

    @staticmethod
    def from_row(row_utente: dict, row_paziente: dict) -> "Paziente":
        # i dati del paziente sono divisi tra utenti.csv e pazienti.csv
        return Paziente(
            codiceUtente=row_utente["codiceUtente"],
            username=row_utente["username"],
            password=row_utente["password"],
            nome=row_utente["nome"],
            cognome=row_utente["cognome"],
            dataNascita=row_utente["dataNascita"],
            codiceFiscale=row_utente["codiceFiscale"],
            codiceMedicoRiferimento=row_paziente["codiceMedicoRiferimento"],
        )
