"""
Implementa il sequence diagram "AggiornaTerapia.txt":

alt terapia esistente -> aggiornaTerapia(...)
else -> creazioneTerapia(...)
"""

from datetime import date

from config import CSV_PATHS
from models.data_manager import DataManager
from models.terapia import TerapiaDiabetica


class TerapiaController:

    def __init__(self):
        self.dm_terapie = DataManager(CSV_PATHS["terapie"])

    def crea_terapia(self, codice_paziente: str, codice_diabetologo: str,
                      codice_farmaco: str, assunzione_giornaliera: int,
                      quantita: float, indicazioni: str,
                      data_inizio: date, data_fine: date) -> str:
        """Corrisponde a Terapia --> Diabetologo: esitoAggiunta(messaggio)"""
        terapia = TerapiaDiabetica(
            id=self.dm_terapie.get_next_id("id"),
            codicePaziente=codice_paziente,
            codiceDiabetologo=codice_diabetologo,
            codiceFarmaco=codice_farmaco,
            assunzioneGiornaliera=assunzione_giornaliera,
            quantita=quantita,
            indicazioni=indicazioni,
            dataInizio=data_inizio,
            dataFine=data_fine,
        )
        self.dm_terapie.append_row(terapia.to_row())
        return f"Terapia creata con successo (id={terapia.id})."

    def aggiorna_terapia(self, id_terapia: int, **campi_da_aggiornare) -> str:
        """Corrisponde a Terapia --> Diabetologo: esitoModifica(messaggio)"""
        ok = self.dm_terapie.update_row("id", id_terapia, campi_da_aggiornare)
        if ok:
            return f"Terapia {id_terapia} aggiornata con successo."
        return f"Errore: terapia {id_terapia} non trovata."

    def _df_terapie_paziente(self, codice_paziente: str):
        """Helper interno: righe grezze di terapie.csv per un paziente."""
        df = self.dm_terapie.read_all()
        return df[df["codicePaziente"] == codice_paziente]

    def get_terapie_attive_paziente(self, codice_paziente: str, oggi: date = None) -> list[TerapiaDiabetica]:
        """
        Restituisce solo le terapie ancora attive del paziente, come oggetti
        TerapiaDiabetica (non righe pandas). Usa il metodo di dominio
        is_attiva() gia' definito nel model, invece di confrontare le date
        manualmente ad ogni chiamata.
        """
        oggi = oggi or date.today()
        df = self._df_terapie_paziente(codice_paziente)

        terapie = [TerapiaDiabetica.from_row(row) for row in df.to_dict("records")]
        return [t for t in terapie if t.is_attiva(oggi)]
