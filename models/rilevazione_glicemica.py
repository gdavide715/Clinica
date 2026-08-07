from dataclasses import dataclass
from datetime import date, time
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
