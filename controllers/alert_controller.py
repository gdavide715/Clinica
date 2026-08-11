"""
Implementa il sequence diagram "AlertDimenticanze.txt":
"""

from datetime import date, timedelta

from config import CSV_PATHS, GIORNI_CONSECUTIVI_ALERT_MEDICO
from models.data_manager import DataManager

#bisogna gestire l'invio di alert al medico e al paziente in modo che mandi un messaggio e finché lo stato non cambia "resta"
#quel messaggio lì

class AlertController:

    def __init__(self):
        self.dm_terapie = DataManager(CSV_PATHS["terapie"])
        self.dm_assunzioni = DataManager(CSV_PATHS["assunzioni_farmaco"])
        self.dm_pazienti = DataManager(CSV_PATHS["pazienti"])

    def verifica_assunzioni(self, codice_paziente: str, data_odierna: date):
        
        # Restituisce un dizionario con:
        # - notifica_paziente: bool
        # - notifica_diabetologo: bool
        # - codice_medico: str|None
        
        df_terapie = self.dm_terapie.read_all()
        terapie_paziente = df_terapie[df_terapie["codicePaziente"] == codice_paziente]
        num_assunzioni_previste = terapie_paziente["assunzioneGiornaliera"].sum()

        df_assunzioni = self.dm_assunzioni.read_all()
        df_assunzioni["data"] = df_assunzioni["data"].astype(str)
        assunzioni_oggi = df_assunzioni[
            (df_assunzioni["codicePaziente"] == codice_paziente)
            & (df_assunzioni["data"] == str(data_odierna))
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
            if self._nessuna_assunzione_da_giorni(
                codice_paziente, data_odierna, GIORNI_CONSECUTIVI_ALERT_MEDICO
            ):
                df_pazienti = self.dm_pazienti.read_all()
                row = df_pazienti[df_pazienti["codiceUtente"] == codice_paziente]
                if not row.empty:
                    risultato["notifica_diabetologo"] = True
                    risultato["codice_medico"] = row.iloc[0]["codiceMedicoRiferimento"]

        return risultato

    def _nessuna_assunzione_da_giorni(self, codice_paziente: str,
                                       data_odierna: date, num_giorni: int) -> bool:
        df_assunzioni = self.dm_assunzioni.read_all()
        df_assunzioni["data"] = df_assunzioni["data"].astype(str)
        for i in range(num_giorni):
            giorno = str(data_odierna - timedelta(days=i))
            if not df_assunzioni[
                (df_assunzioni["codicePaziente"] == codice_paziente)
                & (df_assunzioni["data"] == giorno)
            ].empty:
                return False  # trovata almeno un'assunzione -> non e' "senza assunzioni"
        return True
