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
    ultimaModifica: date

    def is_attiva(self, oggi: date) -> bool:
        return self.dataInizio <= oggi <= self.dataFine

    @staticmethod
    def from_row(row: dict) -> "TerapiaDiabetica":
        """Costruisce una TerapiaDiabetica a partire da una riga di terapie.csv."""
        return TerapiaDiabetica(
            id=int(row["id"]),
            codicePaziente=row["codicePaziente"],
            codiceDiabetologo=row["codiceDiabetologo"],
            codiceFarmaco=row["codiceFarmaco"],
            assunzioneGiornaliera=int(row["assunzioneGiornaliera"]),
            quantita=float(row["quantita"]),
            indicazioni=row["indicazioni"],
            dataInizio=date.fromisoformat(str(row["dataInizio"])),
            dataFine=date.fromisoformat(str(row["dataFine"])),
            ultimaModifica=date.fromisoformat(str(row["ultimaModifica"]))
        )

    def to_row(self) -> dict:
        """Rappresentazione pronta per la scrittura su terapie.csv."""
        return {
            "id": self.id,
            "codicePaziente": self.codicePaziente,
            "codiceDiabetologo": self.codiceDiabetologo,
            "codiceFarmaco": self.codiceFarmaco,
            "assunzioneGiornaliera": self.assunzioneGiornaliera,
            "quantita": self.quantita,
            "indicazioni": self.indicazioni,
            "dataInizio": self.dataInizio,
            "dataFine": self.dataFine,
            "ultimaModifica": self.ultimaModifica
        }
