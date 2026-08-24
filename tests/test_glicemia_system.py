import unittest
import os
from datetime import date, time
from config import CSV_PATHS
from controllers.glicemia_controller import GlicemiaController
from models.my_enum.pasto import Pasto

class TestGlicemiaSystem(unittest.TestCase):

    def setUp(self):
        """
        Prepariamo l'ambiente isolato creando tre file temporanei.
        Ci serve un paziente assegnato a un medico per verificare
        l'invio dell'alert al diabetologo corretto.
        """
        self.test_ril_csv = "data/test_rilevazioni.csv"
        self.test_paz_csv = "data/test_pazienti_glic.csv"
        self.test_notifiche_csv = "data/test_notifiche.csv"

        self.orig_ril = CSV_PATHS.get("rilevazioni_glicemiche")
        self.orig_paz = CSV_PATHS.get("pazienti")
        self.orig_notifiche = CSV_PATHS.get("notifiche")

        CSV_PATHS["rilevazioni_glicemiche"] = self.test_ril_csv
        CSV_PATHS["pazienti"] = self.test_paz_csv
        CSV_PATHS["notifiche"] = self.test_notifiche_csv

        # 1. CSV Rilevazioni (vuoto all'inizio)
        with open(self.test_ril_csv, "w") as f:
            f.write("id,codicePaziente,livelloGlicemia,data,ora,momentoPasto\n")

        # 2. CSV Pazienti (creiamo U001 assegnato al medico M001)
        with open(self.test_paz_csv, "w") as f:
            f.write("codiceUtente,codiceMedicoRiferimento\n")
            f.write("U001,M001\n")

        # 3. CSV Notifiche (vuoto all'inizio)
        with open(self.test_notifiche_csv, "w") as f:
            f.write("id,codiceUtente,tipo,messaggio,data,letta\n")

        self.controller = GlicemiaController()

    def tearDown(self):
        """Pulizia finale."""
        for path in [self.test_ril_csv, self.test_paz_csv, self.test_notifiche_csv]:
            if os.path.exists(path):
                os.remove(path)

        if self.orig_ril: CSV_PATHS["rilevazioni_glicemiche"] = self.orig_ril
        if self.orig_paz: CSV_PATHS["pazienti"] = self.orig_paz
        if self.orig_notifiche: CSV_PATHS["notifiche"] = self.orig_notifiche

    # TEST CASES

    def test_inserimento_glicemia_nella_norma(self):
        """Test: Glicemia pre-pasto a 100 mg/dL non genera alcun alert."""
        esito, alert, medico = self.controller.inserisci_rilevazione(
            codice_paziente="U001",
            data_ril=date.today(),
            ora=time(8, 0),
            livello_glicemia=100.0,
            momento_pasto=Pasto.PRE_PASTO
        )

        self.assertEqual(esito, "nella norma")
        self.assertFalse(alert, "Non deve partire nessun alert")
        self.assertIsNone(medico)

        # Controlliamo fisicamente il CSV delle notifiche: deve avere solo 1 riga (l'intestazione)
        with open(self.test_notifiche_csv, "r") as f:
            righe = f.readlines()
            self.assertEqual(len(righe), 1, "Non deve essere stata scritta alcuna notifica nel CSV")

    def test_inserimento_iperglicemia_grave(self):
        """Test: Glicemia pre-pasto a 190 mg/dL (soglia +60) genera alert grave al medico."""
        esito, alert, medico = self.controller.inserisci_rilevazione(
            codice_paziente="U001",
            data_ril=date.today(),
            ora=time(12, 0),
            livello_glicemia=190.0,
            momento_pasto=Pasto.PRE_PASTO
        )

        self.assertIn("Grave", esito, "Lo scarto di +60 deve essere classificato come Grave")
        self.assertTrue(alert, "Deve partire un alert al medico")
        self.assertEqual(medico, "M001", "L'alert deve essere indirizzato al medico corretto")

        # Controlliamo fisicamente il CSV delle notifiche: deve avere 2 righe (intestazione + 1 notifica)
        with open(self.test_notifiche_csv, "r") as f:
            righe = f.readlines()
            self.assertEqual(len(righe), 2, "Deve essere stata scritta la notifica nel CSV")
            
            # Verifichiamo che il messaggio contenga le keyword corrette
            notifica = righe[1]
            self.assertIn("M001", notifica)
            self.assertIn("GRAVE", notifica)
            self.assertIn("190.0", notifica)

if __name__ == "__main__":
    unittest.main()