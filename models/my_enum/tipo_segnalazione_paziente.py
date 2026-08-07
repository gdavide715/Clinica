from enum import Enum

class TipoSegnalazionePaziente(Enum):
    SINTOMO = "Sintomo"
    PATOLOGIA_CONCOMITANTE = "PatologiaConcomitante"
    TERAPIA_CONCOMITANTE = "TerapiaConcomitante"