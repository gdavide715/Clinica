"""
Gestisce la registrazione delle assunzioni di farmaco da parte del paziente
(model AssunzioneFarmaco) e la verifica di coerenza con la terapia
prescritta (richiesta esplicita della specifica: "Il sistema deve
verificare che le assunzioni di farmaci da parte dei pazienti siano
coerenti con le terapie prescritte").

NOTA: non va confuso con FarmacoController, che gestisce invece il
catalogo dei farmaci (model Farmaco).
"""

from datetime import date, time

from config import CSV_PATHS
from models.data_manager import DataManager
from models.assunzione_farmaco import AssunzioneFarmaco
from models.terapia import TerapiaDiabetica


class AssunzioneFarmacoController:

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

        assunzione = AssunzioneFarmaco(
            id=self.dm_assunzioni.get_next_id("id"),
            codicePaziente=codice_paziente,
            idTerapia=id_terapia,
            data=data,
            ora=ora,
            quantita=quantita,
        )
        self.dm_assunzioni.append_row(assunzione.to_row())
        return True, "Assunzione registrata con successo."

    def _verifica_coerenza(self, codice_paziente: str, id_terapia: int,
                            codice_farmaco: str, quantita: float):
        df_terapie = self.dm_terapie.read_all()
        match = df_terapie[
            (df_terapie["id"] == id_terapia)
            & (df_terapie["codicePaziente"] == codice_paziente)
        ]
        if match.empty:
            return False, "Nessuna terapia corrispondente trovata per questo paziente."

        terapia = TerapiaDiabetica.from_row(match.iloc[0].to_dict())

        if codice_farmaco != terapia.codiceFarmaco:
            return False, (
                f"Farmaco non coerente con la terapia prescritta "
                f"(previsto: {terapia.codiceFarmaco}, inserito: {codice_farmaco})."
            )

        if quantita != terapia.quantita:
            return False, (
                f"Quantita' non coerente con la terapia prescritta "
                f"(prevista: {terapia.quantita}, inserita: {quantita})."
            )
        return True, "OK"
