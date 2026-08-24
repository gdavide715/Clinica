import unittest
import os
from datetime import date
from config import CSV_PATHS
from controllers.terapia_controller import TerapiaController

class TestTerapiaSystem(unittest.TestCase):

    def setUp(self):
        """
        Prepariamo l'ambiente isolato:
        Creiamo un CSV finto per le terapie inserendo un record di partenza
        intestato al paziente U001, valido da Gennaio a Giugno 2026.
        """
        self.test_terapie_csv = "data/test_terapie.csv"
        self.orig_terapie = CSV_PATHS.get("terapie")
        
        # Dirottiamo il sistema
        CSV_PATHS["terapie"] = self.test_terapie_csv

        # Creiamo il file e inseriamo la terapia base (ID 1)
        with open(self.test_terapie_csv, "w") as f:
            f.write("id,codicePaziente,codiceDiabetologo,codiceFarmaco,assunzioneGiornaliera,quantita,indicazioni,dataInizio,dataFine,ultimaModifica\n")
            f.write("1,U001,M001,F001,2,50.0,Dopo i pasti,2026-01-01,2026-06-30,2026-01-01\n")

        self.controller = TerapiaController()

    def tearDown(self):
        """Pulizia finale post-test."""
        if os.path.exists(self.test_terapie_csv):
            os.remove(self.test_terapie_csv)
        if self.orig_terapie:
            CSV_PATHS["terapie"] = self.orig_terapie

    # TEST CASES

    def test_crea_terapia_e_lettura(self):
        """Test: Creazione di una nuova terapia e scrittura fisica nel file."""
        oggi = date.today()
        esito = self.controller.crea_terapia(
            codice_paziente="U002",
            codice_diabetologo="M001",
            codice_farmaco="F002",
            assunzione_giornaliera=1,
            quantita=15.0,
            indicazioni="Assumere la mattina",
            data_inizio=oggi,
            data_fine=date(2027, 1, 1),
            ultima_modifica=oggi
        )

        self.assertIn("con successo", esito)

        # Usiamo il controller per rileggere dal file e verificare l'esistenza
        terapie = self.controller.get_tutte_terapie_paziente("U002")
        self.assertEqual(len(terapie), 1, "La nuova terapia non è stata letta correttamente")
        self.assertEqual(terapie[0].codiceFarmaco, "F002")

    def test_aggiorna_terapia(self):
        """Test: Aggiornamento parziale di una terapia esistente (es. cambio posologia)."""
        esito = self.controller.aggiorna_terapia(
            id_terapia=1,
            assunzioneGiornaliera=3,
            indicazioni="Aggiornato"
        )
        
        self.assertIn("con successo", esito)

        # Verifichiamo che i dati sul file siano stati effettivamente alterati
        terapie = self.controller.get_tutte_terapie_paziente("U001")
        self.assertEqual(terapie[0].assunzioneGiornaliera, 3)
        self.assertEqual(terapie[0].indicazioni, "Aggiornato")

    def test_get_terapie_attive_filtro_temporale(self):
        """Test: Verifica che le terapie scadute vengano escluse dalla lettura."""
        # La terapia di U001 scade il 30-06-2026. 
        # Test 1: Inseriamo una data in cui è ancora attiva
        data_valida = date(2026, 3, 1)
        attive_marzo = self.controller.get_terapie_attive_paziente("U001", oggi=data_valida)
        self.assertEqual(len(attive_marzo), 1)

        # Test 2: Inseriamo una data in cui è scaduta
        data_scaduta = date(2026, 8, 1)
        attive_agosto = self.controller.get_terapie_attive_paziente("U001", oggi=data_scaduta)
        self.assertEqual(len(attive_agosto), 0, "La terapia scaduta non deve apparire tra le attive")

if __name__ == "__main__":
    unittest.main()