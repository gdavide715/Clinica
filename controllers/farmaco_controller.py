"""
Gestisce il catalogo dei farmaci (data/farmaci.csv).

NOTA: non va confuso con AssunzioneFarmacoController, che gestisce invece
le assunzioni giornaliere registrate dal paziente (model AssunzioneFarmaco).
Questo controller si occupa del model Farmaco, cioe' dell'anagrafica dei
farmaci prescrivibili.
"""

from config import CSV_PATHS
from models.data_manager import DataManager
from models.farmaco import Farmaco


class FarmacoController:

    def __init__(self):
        self.dm_farmaci = DataManager(CSV_PATHS["farmaci"])

    def get_farmaco(self, codice_farmaco: str) -> Farmaco | None:
        """Restituisce il Farmaco corrispondente al codice, o None se non esiste."""
        df = self.dm_farmaci.read_all()
        match = df[df["codiceFarmaco"] == codice_farmaco]
        if match.empty:
            return None
        return Farmaco.from_row(match.iloc[0].to_dict())

    def get_tutti_farmaci(self) -> list[Farmaco]:
        """Restituisce l'intero catalogo farmaci come oggetti Farmaco."""
        df = self.dm_farmaci.read_all()
        return [Farmaco.from_row(row) for row in df.to_dict("records")]
