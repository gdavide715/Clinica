"""
Implementa il sequence diagram "AlertDimenticanze.txt"
con salvataggio su database delle notifiche persistenti e blocco dei duplicati giornalieri.
"""
from datetime import date, timedelta

from config import CSV_PATHS, GIORNI_CONSECUTIVI_ALERT_MEDICO
from models.data_manager import DataManager
from models.my_enum.tipo_notifica import TipoNotifica
from controllers.notifica_controller import NotificaController
from models.terapia import TerapiaDiabetica


class AlertController:

    def __init__(self):
        self.dm_terapie = DataManager(CSV_PATHS["terapie"])
        self.dm_assunzioni = DataManager(CSV_PATHS["assunzioni_farmaco"])
        self.dm_pazienti = DataManager(CSV_PATHS["pazienti"])
        self.notifica_controller = NotificaController()
        
    def _notifica_gia_inviata_oggi(self, codice_utente: str, tipo: TipoNotifica, oggi: date) -> bool:
        """Verifica se una notifica dello stesso tipo è già stata creata oggi per questo utente."""
        # Recuperiamo tutte le notifiche, comprese quelle già smarcate come 'lette'
        notifiche_storico = self.notifica_controller.get_notifiche_utente(codice_utente, solo_non_lette=False)
        for n in notifiche_storico:
            if n.tipo == tipo and n.data == oggi:
                return True
        return False

    def verifica_assunzioni(self, codice_paziente: str, data_odierna: date):
        df_terapie = self.dm_terapie.read_all()
        terapie = [TerapiaDiabetica.from_row(r) for r in df_terapie.to_dict("records")]
        
        terapie_attive = [t for t in terapie if t.codicePaziente == codice_paziente and t.is_attiva(data_odierna)]
        num_assunzioni_previste = sum(t.assunzioneGiornaliera for t in terapie_attive)

        df_assunzioni = self.dm_assunzioni.read_all()
        num_assunzioni_oggi = 0
        
        if not df_assunzioni.empty and "data" in df_assunzioni.columns:
            df_assunzioni["data"] = df_assunzioni["data"].astype(str)
            assunzioni_oggi = df_assunzioni[
                (df_assunzioni["codicePaziente"] == codice_paziente) & 
                (df_assunzioni["data"] == str(data_odierna))
            ]
            num_assunzioni_oggi = len(assunzioni_oggi)

        insufficiente = num_assunzioni_oggi < num_assunzioni_previste

        risultato = {
            "notifica_paziente": False,
            "notifica_diabetologo": False,
            "codice_medico": None,
        }

        if insufficiente:
            risultato["notifica_paziente"] = True
            
            # Controllo anti-spam per il paziente
            if not self._notifica_gia_inviata_oggi(codice_paziente, TipoNotifica.FARMACO, data_odierna):
                msg_paz = f"Attenzione: non risultano registrate tutte le assunzioni previste per oggi ({data_odierna})."
                self.notifica_controller.crea_notifica(
                    codice_utente=codice_paziente,
                    tipo=TipoNotifica.FARMACO,
                    messaggio=msg_paz,
                    data_notifica=data_odierna
                )

            if self._nessuna_assunzione_da_giorni(codice_paziente, data_odierna, GIORNI_CONSECUTIVI_ALERT_MEDICO):
                df_pazienti = self.dm_pazienti.read_all()
                row = df_pazienti[df_pazienti["codiceUtente"] == codice_paziente]
                
                if not row.empty:
                    codice_medico = row.iloc[0]["codiceMedicoRiferimento"]
                    risultato["notifica_diabetologo"] = True
                    risultato["codice_medico"] = codice_medico
                    
                    # Controllo anti-spam per il medico
                    if not self._notifica_gia_inviata_oggi(codice_medico, TipoNotifica.FARMACO, data_odierna):
                        msg_med = (f"Allarme aderenza: il paziente {codice_paziente} non registra "
                                   f"assunzioni di farmaci da {GIORNI_CONSECUTIVI_ALERT_MEDICO} giorni consecutivi.")
                        
                        self.notifica_controller.crea_notifica(
                            codice_utente=codice_medico,
                            tipo=TipoNotifica.FARMACO,
                            messaggio=msg_med,
                            data_notifica=data_odierna
                        )

        return risultato

    def _nessuna_assunzione_da_giorni(self, codice_paziente: str, data_odierna: date, num_giorni: int) -> bool:
        df_assunzioni = self.dm_assunzioni.read_all()
        if df_assunzioni.empty or "data" not in df_assunzioni.columns:
            return True
            
        df_assunzioni["data"] = df_assunzioni["data"].astype(str)
        for i in range(num_giorni):
            giorno = str(data_odierna - timedelta(days=i))
            if not df_assunzioni[
                (df_assunzioni["codicePaziente"] == codice_paziente) & 
                (df_assunzioni["data"] == giorno)
            ].empty:
                return False 
        return True