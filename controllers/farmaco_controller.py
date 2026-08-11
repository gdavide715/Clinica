"""
Gestisce la registrazione delle assunzioni di farmaco da parte del paziente
e la verifica di coerenza con la terapia prescritta (richiesta esplicita
della specifica: "Il sistema deve verificare che le assunzioni di farmaci
da parte dei pazienti siano coerenti con le terapie prescritte").
"""

from datetime import date, time

from config import CSV_PATHS
from models.data_manager import DataManager


class FarmacoController:

    def __init__(self):
        self.dm_assunzioni = DataManager(CSV_PATHS["assunzioni_farmaco"])
        self.dm_terapie = DataManager(CSV_PATHS["terapie"])

    def registra_assunzione(self, codice_paziente: str, id_terapia: int,
                             codice_farmaco: str, data: date, ora: time,
                             quantita: float):
        coerente, messaggio = self._verifica_coerenza(
            codice_paziente, id_terapia, codice_farmaco, quantita
        )
        if not coerente:
            return False, messaggio

        nuovo_id = self.dm_assunzioni.get_next_id("id")
        self.dm_assunzioni.append_row({
            "id": nuovo_id,
            "codicePaziente": codice_paziente,
            "idTerapia": id_terapia,
            "data": data,
            "ora": ora.strftime("%H:%M"),
            "quantita": quantita,
        })
        return True, "Assunzione registrata con successo."

    def _verifica_coerenza(self, codice_paziente: str, id_terapia: int,
                            codice_farmaco: str, quantita: float):
        df_terapie = self.dm_terapie.read_all()
        terapia = df_terapie[
            (df_terapie["id"] == id_terapia)
            & (df_terapie["codicePaziente"] == codice_paziente)
        ]
        if terapia.empty:
            return False, "Nessuna terapia corrispondente trovata per questo paziente."

        farmaco_previsto = terapia.iloc[0]["codiceFarmaco"]
        if codice_farmaco != farmaco_previsto:
            return False, (
                f"Farmaco non coerente con la terapia prescritta "
                f"(previsto: {farmaco_previsto}, inserito: {codice_farmaco})."
            )

        quantita_prevista = terapia.iloc[0]["quantita"]
        if quantita != quantita_prevista:
            return False, (
                f"Quantita' non coerente con la terapia prescritta "
                f"(prevista: {quantita_prevista}, inserita: {quantita})."
            )
        return True, "OK"