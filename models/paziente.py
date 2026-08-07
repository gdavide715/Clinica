"""
Paziente: sottoclasse di Utente. Ha un medico di riferimento
"""

from dataclasses import dataclass
from datetime import date

from models.utente import Utente


@dataclass
class Paziente(Utente):
    codiceMedicoRiferimento: str = ""

    @staticmethod
    def from_row(row_utente: dict, row_paziente: dict) -> "Paziente":
        # i dati di paziente sono sparsi tra utenti e pazienti. Bisogna ricomporre
        # le righe. 1 riga di utente NON è per forza un paziente. E una riga di 
        # paziente NON contiene tutte le informazioni di paziente. 
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
