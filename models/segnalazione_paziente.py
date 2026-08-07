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
