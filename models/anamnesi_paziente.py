from dataclasses import dataclass
from models.my_enum.tipo_condizione_clinica import TipoCondizioneClinica

@dataclass
class AnamnesiPaziente:
    id: int
    codicePaziente: str
    tipologia: TipoCondizioneClinica
    descrizione: str

    @staticmethod
    def from_row(row: dict) -> "AnamnesiPaziente":
        return AnamnesiPaziente(
            id=int(row["id"]),
            codicePaziente=row["codicePaziente"],
            tipologia=TipoCondizioneClinica(row["tipologia"]),
            descrizione=row["descrizione"],
        )

    def to_row(self) -> dict:
        """Rappresentazione pronta per la scrittura su anamnesi_paziente.csv."""
        return {
            "id": self.id,
            "codicePaziente": self.codicePaziente,
            "tipologia": self.tipologia.value,
            "descrizione": self.descrizione,
        }
