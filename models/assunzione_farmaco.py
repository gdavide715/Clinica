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

    def to_row(self) -> dict:
        """Rappresentazione pronta per la scrittura su assunzioni_farmaco.csv."""
        return {
            "id": self.id,
            "codicePaziente": self.codicePaziente,
            "idTerapia": self.idTerapia,
            "data": self.data,
            "ora": self.ora.strftime("%H:%M"),
            "quantita": self.quantita,
        }
