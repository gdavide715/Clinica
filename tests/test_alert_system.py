import unittest
import os
from datetime import date, timedelta
from config import CSV_PATHS
from controllers.alert_controller import AlertController

class TestAlertSystem(unittest.TestCase):

    def setUp(self):
        """
        Prepariamo un ambiente di test completamente isolato con 4 file CSV temporanei:
        - Terapie (per sapere cosa il paziente avrebbe dovuto assumere)
        - Assunzioni (per verificare cosa ha effettivamente preso)
        - Pazienti (per risalire al medico di riferimento)
        - Notifiche (per registrare gli alert generati)
        """
        self.test_terapie_csv = "data/test_alert_terapie.csv"
        self.test_assunzioni_csv = "data/test_alert_assunzioni.csv"
        self.test_pazienti_csv = "data/test_alert_pazienti.csv"
        self.test_notifiche_csv = "data/test_alert_notifiche.csv"

        self.orig_terapie = CSV_PATHS.get("terapie")
        self.orig_assunzioni = CSV_PATHS.get("assunzioni_farmaco")
        self.orig_pazienti = CSV_PATHS.get("pazienti")
        self.orig_notifiche = CSV_PATHS.get("notifiche")

        CSV_PATHS["terapie"] = self.test_terapie_csv
        CSV_PATHS["assunzioni_farmaco"] = self.test_assunzioni_csv
        CSV_PATHS["pazienti"] = self.test_pazienti_csv
        CSV_PATHS["notifiche"] = self.test_notifiche_csv

        # 1. Terapie: Paziente U001 ha una terapia attiva continuativa
        with open(self.test_terapie_csv, "w") as f:
            f.write("id,codicePaziente,codiceDiabetologo,codiceFarmaco,assunzioneGiornaliera,quantita,indicazioni,dataInizio,dataFine,ultimaModifica\n")
            f.write("1,U001,M001,F001,1,10.0,Test,2026-01-01,2027-12-31,2026-01-01\n")

        # 2. Assunzioni: Inizialmente vuoto (nessun farmaco assunto)
        with open(self.test_assunzioni_csv, "w") as f:
            f.write("id,codicePaziente,idTerapia,data,ora,quantita\n")

        # 3. Pazienti: U001 associato a M001
        with open(self.test_pazienti_csv, "w") as f:
            f.write("codiceUtente,codiceMedicoRiferimento\n")
            f.write("U001,M001\n")

        # 4. Notifiche: Vuoto
        with open(self.test_notifiche_csv, "w") as f:
            f.write("id,codiceUtente,tipo,messaggio,data,letta\n")

        self.controller = AlertController()

    def tearDown(self):
        """Pulizia e ripristino dei path originali."""
        for path in [self.test_terapie_csv, self.test_assunzioni_csv, self.test_pazienti_csv, self.test_notifiche_csv]:
            if os.path.exists(path):
                os.remove(path)

        if self.orig_terapie: CSV_PATHS["terapie"] = self.orig_terapie
        if self.orig_assunzioni: CSV_PATHS["assunzioni_farmaco"] = self.orig_assunzioni
        if self.orig_pazienti: CSV_PATHS["pazienti"] = self.orig_pazienti
        if self.orig_notifiche: CSV_PATHS["notifiche"] = self.orig_notifiche

    def test_alert_mancata_assunzione_paziente_e_medico(self):
        """Test: La mancata assunzione genera l'alert per il paziente e, se prolungata, per il medico."""
        ieri = date.today() - timedelta(days=1)

        risultato = self.controller.verifica_assunzioni("U001", data_richiesta=ieri)

        self.assertTrue(risultato["notifica_paziente"], "Il sistema deve segnalare la dimenticanza al paziente")
        self.assertTrue(risultato["notifica_diabetologo"], "Il sistema deve avvisare anche il diabetologo")

        # Verifichiamo che siano state scritte entrambe le notifiche (Paziente + Medico -> 3 righe totali)
        with open(self.test_notifiche_csv, "r") as f:
            righe = f.readlines()
            self.assertEqual(len(righe), 3, "Devono esserci la notifica per il paziente e quella per il medico nel CSV")

    def test_anti_spam_notifiche_giornaliere(self):
        """Test: Richiamare la verifica due volte nello stesso giorno non duplica le notifiche."""
        ieri = date.today() - timedelta(days=1)

        # Prima chiamata
        self.controller.verifica_assunzioni("U001", data_richiesta=ieri)
        # Seconda chiamata immediata (tentativo di spam)
        self.controller.verifica_assunzioni("U001", data_richiesta=ieri)

        # Il file delle notifiche non deve duplicare nulla: restano esattamente 3 righe (intestazione + 2 notifiche uniche)
        with open(self.test_notifiche_csv, "r") as f:
            righe = f.readlines()
            self.assertEqual(len(righe), 3, "Il meccanismo anti-spam deve impedire la duplicazione degli alert nello stesso giorno")

if __name__ == "__main__":
    unittest.main()