"""
Controller per le terapie. Due azioni separate, mai automatiche tra loro:
- crea_terapia(): nuova prescrizione, nuova riga.
- correggi_terapia(): modifica una riga esistente (mai dataInizio), notifica
  il paziente. Per interrompere una terapia si imposta dataFine a oggi.
"""

from datetime import date

from config import CSV_PATHS
from models.data_manager import DataManager
from models.terapia import TerapiaDiabetica
from models.my_enum.tipo_notifica import TipoNotifica
from controllers.notifica_controller import NotificaController
from controllers.farmaco_controller import FarmacoController


class TerapiaController:

    ASSUNZIONI_MIN, ASSUNZIONI_MAX = 1, 10
    QUANTITA_MIN, QUANTITA_MAX = 0.01, 1000

    def __init__(self):
        self.dm_terapie = DataManager(CSV_PATHS["terapie"])
        self.notifica_controller = NotificaController()
        self.farmaco_controller = FarmacoController()

    def crea_terapia(self, codice_paziente: str, codice_diabetologo: str,
                      codice_farmaco: str, assunzione_giornaliera: int,
                      quantita: float, indicazioni: str,
                      data_inizio: date, data_fine: date) -> tuple[bool, str]:
        """Corrisponde a Terapia --> Diabetologo: esitoAggiunta(messaggio)."""
        valido, errore = self._valida_parametri(assunzione_giornaliera, quantita, data_inizio, data_fine)
        if not valido:
            return False, errore

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
            ultimaModifica=date.today(),
        )
        self.dm_terapie.append_row(terapia.to_row())
        return True, f"Terapia creata con successo (id={terapia.id})."

    def correggi_terapia(self, id_terapia: int, codice_farmaco: str,
                          assunzione_giornaliera: int, quantita: float,
                          indicazioni: str, data_fine: date) -> tuple[bool, str]:
        """Modifica la riga esistente (mai dataInizio) e notifica il paziente."""
        terapia_esistente = self.get_terapia_by_id(id_terapia)
        if terapia_esistente is None:
            return False, f"Terapia {id_terapia} non trovata."

        valido, errore = self._valida_parametri(
            assunzione_giornaliera, quantita, terapia_esistente.dataInizio, data_fine
        )
        if not valido:
            return False, errore

        self.dm_terapie.update_row("id", id_terapia, {
            "codiceFarmaco": codice_farmaco,
            "assunzioneGiornaliera": assunzione_giornaliera,
            "quantita": quantita,
            "indicazioni": indicazioni,
            "dataFine": data_fine,
            "ultimaModifica": date.today(),
        })

        nome_farmaco = self._nome_farmaco(codice_farmaco)
        self.notifica_controller.crea_notifica(
            codice_utente=terapia_esistente.codicePaziente,
            tipo=TipoNotifica.TERAPIA,
            messaggio=(
                f"Il tuo diabetologo ha modificato la terapia con {nome_farmaco}. "
                f"Controlla i dettagli aggiornati nella tua area personale."
            ),
            data_notifica=date.today(),
        )
        return True, f"Terapia {id_terapia} aggiornata con successo. Il paziente e' stato notificato."

    def get_terapia_by_id(self, id_terapia: int) -> TerapiaDiabetica | None:
        """Restituisce una singola terapia dato il suo id, o None se non esiste."""
        df = self.dm_terapie.read_all()
        match = df[df["id"] == id_terapia]
        if match.empty:
            return None
        return TerapiaDiabetica.from_row(match.iloc[0].to_dict())

    def _df_terapie_paziente(self, codice_paziente: str):
        """Helper interno: righe grezze di terapie.csv per un paziente."""
        df = self.dm_terapie.read_all()
        return df[df["codicePaziente"] == codice_paziente]

    def get_terapie_attive_paziente(self, codice_paziente: str, oggi: date = None) -> list[TerapiaDiabetica]:
        """Solo le terapie ancora attive alla data indicata."""
        oggi = oggi or date.today()
        df = self._df_terapie_paziente(codice_paziente)

        terapie = [TerapiaDiabetica.from_row(row) for row in df.to_dict("records")]
        return [t for t in terapie if t.is_attiva(oggi)]

    def get_tutte_terapie_paziente(self, codice_paziente: str) -> list[TerapiaDiabetica]:
        """Restituisce tutte le terapie del paziente, attive e non, come oggetti TerapiaDiabetica."""
        df = self._df_terapie_paziente(codice_paziente)
        return [TerapiaDiabetica.from_row(row) for row in df.to_dict("records")]

    def _valida_parametri(self, assunzione_giornaliera, quantita, data_inizio: date, data_fine: date) -> tuple[bool, str]:
        """Validazione di dominio comune a crea_terapia e correggi_terapia."""
        if assunzione_giornaliera is None or not (self.ASSUNZIONI_MIN <= assunzione_giornaliera <= self.ASSUNZIONI_MAX):
            return False, f"Le assunzioni giornaliere devono essere un numero tra {self.ASSUNZIONI_MIN} e {self.ASSUNZIONI_MAX}."
        if quantita is None or not (self.QUANTITA_MIN <= quantita <= self.QUANTITA_MAX):
            return False, f"La quantita' per assunzione deve essere un valore tra {self.QUANTITA_MIN} e {self.QUANTITA_MAX}."
        if data_fine < data_inizio:
            return False, "La data di fine non puo' essere precedente alla data di inizio."
        return True, ""

    def _nome_farmaco(self, codice_farmaco: str) -> str:
        farmaco = self.farmaco_controller.get_farmaco(codice_farmaco)
        return farmaco.nome if farmaco else codice_farmaco
