from dataclasses import dataclass
from datetime import date, time


@dataclass
class AssunzioneFarmaco:
    id: int
    codicePaziente: str
    idTerapia: int
    data: date
    ora: time
    quantita: float
