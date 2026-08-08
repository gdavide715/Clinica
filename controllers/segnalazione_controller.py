"""
Gestisce l'invio e la lettura delle segnalazioni tra paziente e medico.
"""
from datetime import date
from config import CSV_PATHS
from models.data_manager import DataManager
from models.my_enum.tipo_segnalazione_paziente import TipoSegnalazionePaziente

class SegnalazioneController:

    def __init__(self):
        self.dm_segnalazioni = DataManager(CSV_PATHS["segnalazioni_paziente"])

    def invia_segnalazione(self, codice_paziente: str, descrizione: str, 
                           data_inizio: date, data_fine: date, evento: TipoSegnalazionePaziente) -> str:
        nuovo_id = self.dm_segnalazioni.get_next_id("id")
        self.dm_segnalazioni.append_row({
            "id": nuovo_id,
            "codicePaziente": codice_paziente,
            "descrizione": descrizione,
            "dataInizio": data_inizio,
            "dataFine": data_fine,
            "evento": evento.value
        })
        return "Segnalazione inviata con successo al diabetologo."

    def leggi_segnalazioni(self, codice_paziente: str):
        df = self.dm_segnalazioni.read_all()
        if df.empty or "codicePaziente" not in df.columns:
            return []
        paziente_df = df[df["codicePaziente"] == codice_paziente]
        return paziente_df.to_dict('records')