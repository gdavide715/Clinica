from dataclasses import dataclass
from models.my_enum.tipo_condizione_clinica import TipoCondizioneClinica

@dataclass
class AnamnesiPaziente:
    id: int
    codicePaziente: str
    tipologia: TipoCondizioneClinica 
    descrizione: str
