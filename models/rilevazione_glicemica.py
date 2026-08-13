from dataclasses import dataclass
from datetime import date, time, datetime
from models.my_enum.pasto import Pasto

@dataclass
class RilevazioneGlicemica:
    id: int
    codicePaziente: str
    livelloGlicemia: float  # mg/dL
    data: date
    ora: time
    momentoPasto: Pasto

    def fuori_soglia(self, soglia_pre_min: float, soglia_pre_max: float,
                      soglia_post_max: float) -> bool:
        if self.momentoPasto == Pasto.PRE_PASTO:
            return not (soglia_pre_min <= self.livelloGlicemia <= soglia_pre_max)
        return self.livelloGlicemia > soglia_post_max

    def as_datetime(self) -> datetime:
        """Combina data e ora in un unico datetime, utile per ordinare/graficare."""
        return datetime.combine(self.data, self.ora)

    @staticmethod
    def from_row(row: dict) -> "RilevazioneGlicemica":
        return RilevazioneGlicemica(
            id=int(row["id"]),
            codicePaziente=row["codicePaziente"],
            livelloGlicemia=float(row["livelloGlicemia"]),
            data=date.fromisoformat(str(row["data"])),
            ora=datetime.strptime(str(row["ora"]), "%H:%M").time(),
            momentoPasto=Pasto(row["momentoPasto"]),
        )

    def to_row(self) -> dict:
        """Rappresentazione pronta per la scrittura su rilevazioni_glicemiche.csv."""
        return {
            "id": self.id,
            "codicePaziente": self.codicePaziente,
            "livelloGlicemia": self.livelloGlicemia,
            "data": self.data,
            "ora": self.ora.strftime("%H:%M"),
            "momentoPasto": self.momentoPasto.value,
        }
