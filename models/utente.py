from abc import ABC
from dataclasses import dataclass
from datetime import date


@dataclass
class Utente(ABC):
    codiceUtente: str
    username: str
    password: str
    nome: str
    cognome: str
    dataNascita: date
    codiceFiscale: str

    def full_name(self) -> str:
        return f"{self.nome} {self.cognome}"
