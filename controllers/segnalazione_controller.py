"""
Gestisce l'invio e la lettura delle segnalazioni tra paziente e medico
(model SegnalazionePaziente).
"""
from datetime import date
from config import CSV_PATHS
from models.data_manager import DataManager
from models.segnalazione_paziente import SegnalazionePaziente
from models.my_enum.tipo_segnalazione_paziente import TipoSegnalazionePaziente


class SegnalazioneController:

    def __init__(self):
        self.dm_segnalazioni = DataManager(CSV_PATHS["segnalazioni_paziente"])

    def invia_segnalazione(self, codice_paziente: str, descrizione: str,
                            data_inizio: date, data_fine: date,
                            evento: TipoSegnalazionePaziente) -> str:
        segnalazione = SegnalazionePaziente(
            id=self.dm_segnalazioni.get_next_id("id"),
            codicePaziente=codice_paziente,
            descrizione=descrizione,
            dataInizio=data_inizio,
            dataFine=data_fine,
            evento=evento,
        )
        self.dm_segnalazioni.append_row(segnalazione.to_row())
        return "Segnalazione inviata con successo al diabetologo."

    def leggi_segnalazioni(self, codice_paziente: str) -> list[SegnalazionePaziente]:
        df = self.dm_segnalazioni.read_all()
        if df.empty or "codicePaziente" not in df.columns:
            return []
        df_paziente = df[df["codicePaziente"] == codice_paziente]
        return [SegnalazionePaziente.from_row(row) for row in df_paziente.to_dict("records")]
