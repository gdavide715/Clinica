"""
Implementa il sequence diagram "RilevazioneRegistrazioneGlicemia.txt":

Paziente -> Sistema: inserisciRilevazione(...)
Sistema -> Rilevazione Glicemica: salvaRilevazione(...)
Sistema --> Paziente: confermaInserimento
alt valori fuori soglia -> Sistema -> Diabetologo: alertGlicemiaFuoriSoglia(...)
Sistema --> Paziente: esitoLivelloGlicemia
"""

from datetime import date, time

from config import (
    CSV_PATHS,
    GLICEMIA_PRE_PASTO_MIN,
    GLICEMIA_PRE_PASTO_MAX,
    GLICEMIA_POST_PASTO_MAX,
)
from models.data_manager import DataManager
from models.rilevazione_glicemica import RilevazioneGlicemica
from models.my_enum.pasto import Pasto


class GlicemiaController:

    def __init__(self):
        self.dm_rilevazioni = DataManager(CSV_PATHS["rilevazioni_glicemiche"])
        self.dm_pazienti = DataManager(CSV_PATHS["pazienti"])

    def inserisci_rilevazione(self, codice_paziente: str, data: date, ora: time,
                           livello_glicemia: float, momento_pasto: Pasto):
        """
        Restituisce (esito_livello: str, alert_inviato: bool, codice_medico|None)
        """
        nuovo_id = self.dm_rilevazioni.get_next_id("id")
        rilevazione = RilevazioneGlicemica(
            id=nuovo_id,
            codicePaziente=codice_paziente,
            livelloGlicemia=livello_glicemia,
            data=data,
            ora=ora,
            momentoPasto=momento_pasto,
        )
        

        # Sistema -> Rilevazione Glicemica: salvaRilevazione(...)
        self.dm_rilevazioni.append_row(rilevazione.to_row())

        fuori_soglia = rilevazione.fuori_soglia(
            GLICEMIA_PRE_PASTO_MIN, GLICEMIA_PRE_PASTO_MAX, GLICEMIA_POST_PASTO_MAX
        )

        alert_inviato = False
        codice_medico = None
        if fuori_soglia:
            # Sistema -> Diabetologo: alertGlicemiaFuoriSoglia(Lvl glicemia)
            df_pazienti = self.dm_pazienti.read_all()
            row = df_pazienti[df_pazienti["codiceUtente"] == codice_paziente]
            if not row.empty:
                codice_medico = row.iloc[0]["codiceMedicoRiferimento"]
                alert_inviato = True  # qui si aggancerebbe un notification_controller

        esito = "fuori soglia" if fuori_soglia else "nella norma"
        return esito, alert_inviato, codice_medico

    def get_storico_paziente(self, codice_paziente: str) -> list[RilevazioneGlicemica]:
        """Restituisce lo storico delle rilevazioni glicemiche di un paziente."""
        df = self.dm_rilevazioni.read_all()
        df_paziente = df[df["codicePaziente"] == codice_paziente]
        return [RilevazioneGlicemica.from_row(row) for row in df_paziente.to_dict("records")]
