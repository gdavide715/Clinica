from dataclasses import dataclass
from datetime import date


@dataclass
class TerapiaDiabetica:
    id: int
    codicePaziente: str
    codiceDiabetologo: str
    codiceFarmaco: str
    assunzioneGiornaliera: int
    quantita: float
    indicazioni: str
    dataInizio: date
    dataFine: date

    def is_attiva(self, oggi: date) -> bool:
        return self.dataInizio <= oggi <= self.dataFine
