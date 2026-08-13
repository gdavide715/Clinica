from dataclasses import dataclass

from models.utente import Utente


@dataclass
class Diabetologo(Utente):
    email: str = ""

    @staticmethod
    def from_row(row_utente: dict, row_diabetologo: dict) -> "Diabetologo":
        """Costruisce un Diabetologo unendo la riga di utenti.csv e diabetologi.csv."""
        return Diabetologo(
            codiceUtente=row_utente["codiceUtente"],
            username=row_utente["username"],
            password=row_utente["password"],
            nome=row_utente["nome"],
            cognome=row_utente["cognome"],
            dataNascita=row_utente["dataNascita"],
            codiceFiscale=row_utente["codiceFiscale"],
            email=row_diabetologo["email"],
        )
