"""
Controller per la gestione degli alert persistenti.
"""
from datetime import date
from config import CSV_PATHS
from models.data_manager import DataManager
from models.notifica import Notifica
from models.my_enum.tipo_notifica import TipoNotifica

class NotificaController:
    def __init__(self):
        # Utilizza il path da config o un fallback predefinito
        self.file_path = CSV_PATHS.get("notifiche", "data/notifiche.csv")
        self.dm_notifiche = DataManager(self.file_path)

    def crea_notifica(self, codice_utente: str, tipo: TipoNotifica, messaggio: str, data_notifica: date) -> None:
        """Salva un nuovo alert persistente nel sistema."""
        nuovo_id = self.dm_notifiche.get_next_id("id")
        notifica = Notifica(
            id=nuovo_id,
            codiceUtente=codice_utente,
            tipo=tipo,
            messaggio=messaggio,
            data=data_notifica,
            letta=False
        )
        self.dm_notifiche.append_row(notifica.to_row())

    def get_notifiche_utente(self, codice_utente: str, solo_non_lette: bool = True) -> list[Notifica]:
        """
        Recupera gli alert di un utente specifico. 
        Di default restituisce solo le notifiche non lette.
        """
        df = self.dm_notifiche.read_all()
        if df.empty or "codiceUtente" not in df.columns:
            return []
        
        # Filtriamo le righe grezze per l'utente richiesto
        df_utente = df[df["codiceUtente"] == codice_utente]
        
        notifiche = [Notifica.from_row(row) for row in df_utente.to_dict("records")]
        
        if solo_non_lette:
            notifiche = [n for n in notifiche if not n.letta]
            
        # Ordiniamo mettendo le più recenti per prime
        notifiche.sort(key=lambda x: x.data, reverse=True)
        return notifiche

    def segna_come_letta(self, id_notifica: int) -> bool:
        """Marca una notifica come letta per non mostrarla più in dashboard."""
        return self.dm_notifiche.update_row("id", id_notifica, {"letta": True})