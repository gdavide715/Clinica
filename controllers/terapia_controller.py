"""
Implementa il sequence diagram "AggiornaTerapia.txt":

alt terapia esistente -> aggiornaTerapia(...)
else -> creazioneTerapia(...)
"""

from datetime import date

from config import CSV_PATHS
from models.data_manager import DataManager


class TerapiaController:

    def __init__(self):
        self.dm_terapie = DataManager(CSV_PATHS["terapie"])

    def crea_terapia(self, codice_paziente: str, codice_diabetologo: str,
                      codice_farmaco: str, assunzione_giornaliera: int,
                      quantita: float, indicazioni: str,
                      data_inizio: date, data_fine: date) -> str:
        """Corrisponde a Terapia --> Diabetologo: esitoAggiunta(messaggio)"""
        nuovo_id = self.dm_terapie.get_next_id("id")
        self.dm_terapie.append_row({
            "id": nuovo_id,
            "codicePaziente": codice_paziente,
            "codiceDiabetologo": codice_diabetologo,
            "codiceFarmaco": codice_farmaco,
            "assunzioneGiornaliera": assunzione_giornaliera,
            "quantita": quantita,
            "indicazioni": indicazioni,
            "dataInizio": data_inizio,
            "dataFine": data_fine,
        })
        return f"Terapia creata con successo (id={nuovo_id})."

    def aggiorna_terapia(self, id_terapia: int, **campi_da_aggiornare) -> str:
        """Corrisponde a Terapia --> Diabetologo: esitoModifica(messaggio)"""
        ok = self.dm_terapie.update_row("id", id_terapia, campi_da_aggiornare)
        if ok:
            return f"Terapia {id_terapia} aggiornata con successo."
        return f"Errore: terapia {id_terapia} non trovata."

    def get_terapie_paziente(self, codice_paziente: str):
        df = self.dm_terapie.read_all()
        return df[df["codicePaziente"] == codice_paziente]
