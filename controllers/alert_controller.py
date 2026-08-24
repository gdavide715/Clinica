"""
Implementa il sequence diagram "AlertDimenticanze.txt"
con salvataggio su database delle notifiche persistenti, blocco duplicati giornalieri
e verifica di fine giornata (ore 22:00).
"""
from datetime import date, timedelta, datetime, time

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
        
    def _notifica_gia_inviata_oggi(self, codice_utente: str, tipo: TipoNotifica, data_riferimento: date) -> bool:
        """Verifica se una notifica dello stesso tipo è già stata creata per quella specifica data."""
        notifiche_storico = self.notifica_controller.get_notifiche_utente(codice_utente, solo_non_lette=False)
        for n in notifiche_storico:
            if n.tipo == tipo and n.data == data_riferimento:
                return True
        return False

    def verifica_assunzioni(self, codice_paziente: str, data_richiesta: date):
        ora_attuale = datetime.now().time()
        ora_limite = time(22, 0)
        
        if data_richiesta == date.today() and ora_attuale < ora_limite:
            data_da_verificare = data_richiesta - timedelta(days=1)
        else:
            data_da_verificare = data_richiesta

        # 1. Calcolo assunzioni previste per la data_da_verificare
        df_terapie = self.dm_terapie.read_all()
        terapie = [TerapiaDiabetica.from_row(r) for r in df_terapie.to_dict("records")]
        
        terapie_attive = [t for t in terapie if t.codicePaziente == codice_paziente and t.is_attiva(data_da_verificare)]
        num_assunzioni_previste = sum(t.assunzioneGiornaliera for t in terapie_attive)

        # 2. Calcolo assunzioni effettuate nella data_da_verificare
        df_assunzioni = self.dm_assunzioni.read_all()
        num_assunzioni_effettuate = 0
        
        if not df_assunzioni.empty and "data" in df_assunzioni.columns:
            df_assunzioni["data"] = df_assunzioni["data"].astype(str)
            assunzioni_eseguite = df_assunzioni[
                (df_assunzioni["codicePaziente"] == codice_paziente) & 
                (df_assunzioni["data"] == str(data_da_verificare))
            ]
            num_assunzioni_effettuate = len(assunzioni_eseguite)

        insufficiente = num_assunzioni_effettuate < num_assunzioni_previste

        risultato = {
            "notifica_paziente": False,
            "notifica_diabetologo": False,
            "codice_medico": None,
        }

        # Generiamo l'alert solo se le assunzioni previste erano > 0 e non sono state rispettate
        if num_assunzioni_previste > 0 and insufficiente:
            risultato["notifica_paziente"] = True
            
            # Controllo anti-spam per il paziente sulla data di riferimento
            if not self._notifica_gia_inviata_oggi(codice_paziente, TipoNotifica.FARMACO, data_da_verificare):
                msg_paz = f"Attenzione: non risultano registrate tutte le assunzioni di farmaci previste per la giornata del {data_da_verificare}."
                self.notifica_controller.crea_notifica(
                    codice_utente=codice_paziente,
                    tipo=TipoNotifica.FARMACO,
                    messaggio=msg_paz,
                    data_notifica=data_da_verificare
                )

            if self._nessuna_assunzione_da_giorni(codice_paziente, data_da_verificare, GIORNI_CONSECUTIVI_ALERT_MEDICO):
                df_pazienti = self.dm_pazienti.read_all()
                row = df_pazienti[df_pazienti["codiceUtente"] == codice_paziente]
                
                if not row.empty:
                    codice_medico = row.iloc[0]["codiceMedicoRiferimento"]
                    risultato["notifica_diabetologo"] = True
                    risultato["codice_medico"] = codice_medico
                    
                    # Controllo anti-spam per il medico
                    if not self._notifica_gia_inviata_oggi(codice_medico, TipoNotifica.FARMACO, data_da_verificare):
                        msg_med = (f"Allarme aderenza: il paziente {codice_paziente} non registra "
                                   f"assunzioni di farmaci da {GIORNI_CONSECUTIVI_ALERT_MEDICO} giorni consecutivi "
                                   f"(fino al {data_da_verificare}).")
                        
                        self.notifica_controller.crea_notifica(
                            codice_utente=codice_medico,
                            tipo=TipoNotifica.FARMACO,
                            messaggio=msg_med,
                            data_notifica=data_da_verificare
                        )

        return risultato

    def _nessuna_assunzione_da_giorni(self, codice_paziente: str, data_di_partenza: date, num_giorni: int) -> bool:
        df_assunzioni = self.dm_assunzioni.read_all()
        if df_assunzioni.empty or "data" not in df_assunzioni.columns:
            return True
            
        df_assunzioni["data"] = df_assunzioni["data"].astype(str)
        # Controlliamo a ritroso a partire dalla data_di_partenza
        for i in range(num_giorni):
            giorno = str(data_di_partenza - timedelta(days=i))
            if not df_assunzioni[
                (df_assunzioni["codicePaziente"] == codice_paziente) & 
                (df_assunzioni["data"] == giorno)
            ].empty:
                return False 
        return True