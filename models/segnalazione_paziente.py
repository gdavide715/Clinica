from dataclasses import dataclass
from datetime import date
from models.my_enum.tipo_segnalazione_paziente import TipoSegnalazionePaziente

@dataclass
class SegnalazionePaziente:
    id: int
    codicePaziente: str
    descrizione: str
    dataInizio: date
    dataFine: date
    evento: TipoSegnalazionePaziente

    @staticmethod
    def from_row(row: dict) -> "SegnalazionePaziente":
        return SegnalazionePaziente(
            id=int(row["id"]),
            codicePaziente=row["codicePaziente"],
            descrizione=row["descrizione"],
            dataInizio=date.fromisoformat(str(row["dataInizio"])),
            dataFine=date.fromisoformat(str(row["dataFine"])),
            evento=TipoSegnalazionePaziente(row["evento"]),
        )

    def to_row(self) -> dict:
        """Rappresentazione pronta per la scrittura su segnalazioni_paziente.csv."""
        return {
            "id": self.id,
            "codicePaziente": self.codicePaziente,
            "descrizione": self.descrizione,
            "dataInizio": self.dataInizio,
            "dataFine": self.dataFine,
            "evento": self.evento.value,
        }
