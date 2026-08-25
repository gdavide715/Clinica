import unittest
import os
from datetime import date
from config import CSV_PATHS
from controllers.terapia_controller import TerapiaController
from controllers.notifica_controller import NotificaController


class TestTerapiaSystem(unittest.TestCase):

    def setUp(self):
        """
        Prepariamo l'ambiente isolato: CSV finti per terapie e notifiche
        (TerapiaController crea notifiche quando una terapia viene
        corretta, quindi va isolato anche quel file).
        """
        self.test_terapie_csv = "data/test_terapie.csv"
        self.test_notifiche_csv = "data/test_notifiche.csv"
        self.orig_terapie = CSV_PATHS.get("terapie")
        self.orig_notifiche = CSV_PATHS.get("notifiche")

        CSV_PATHS["terapie"] = self.test_terapie_csv
        CSV_PATHS["notifiche"] = self.test_notifiche_csv

        with open(self.test_terapie_csv, "w") as f:
            f.write("id,codicePaziente,codiceDiabetologo,codiceFarmaco,assunzioneGiornaliera,quantita,indicazioni,dataInizio,dataFine,ultimaModifica\n")
            f.write("1,U001,M001,F001,2,50.0,Dopo i pasti,2026-01-01,2026-06-30,2026-01-01\n")

        with open(self.test_notifiche_csv, "w") as f:
            f.write("id,codiceUtente,tipo,messaggio,data,letta\n")

        self.controller = TerapiaController()
        self.notifica_controller = NotificaController()

    def tearDown(self):
        for path in (self.test_terapie_csv, self.test_notifiche_csv):
            if os.path.exists(path):
                os.remove(path)
        if self.orig_terapie:
            CSV_PATHS["terapie"] = self.orig_terapie
        if self.orig_notifiche:
            CSV_PATHS["notifiche"] = self.orig_notifiche

    # TEST CASES

    def test_crea_terapia_e_lettura(self):
        """Test: Creazione di una nuova terapia (nuova riga) e scrittura fisica nel file."""
        oggi = date.today()
        successo, esito = self.controller.crea_terapia(
            codice_paziente="U002",
            codice_diabetologo="M001",
            codice_farmaco="F002",
            assunzione_giornaliera=1,
            quantita=15.0,
            indicazioni="Assumere la mattina",
            data_inizio=oggi,
            data_fine=date(2027, 1, 1),
        )

        self.assertTrue(successo)
        self.assertIn("con successo", esito)

        terapie = self.controller.get_tutte_terapie_paziente("U002")
        self.assertEqual(len(terapie), 1, "La nuova terapia non è stata letta correttamente")
        self.assertEqual(terapie[0].codiceFarmaco, "F002")

    def test_crea_terapia_non_tocca_terapie_esistenti(self):
        """crea_terapia non deve mai cancellare o modificare righe esistenti, anche se sovrapposte."""
        successo, _ = self.controller.crea_terapia(
            codice_paziente="U001",
            codice_diabetologo="M001",
            codice_farmaco="F001",  # stesso farmaco della terapia id=1
            assunzione_giornaliera=1,
            quantita=25.0,
            indicazioni="Nuova prescrizione sovrapposta",
            data_inizio=date(2026, 3, 1),  # dentro il periodo della terapia id=1
            data_fine=date(2026, 9, 1),
        )
        self.assertTrue(successo)

        terapie = self.controller.get_tutte_terapie_paziente("U001")
        self.assertEqual(len(terapie), 2, "La terapia precedente non deve essere cancellata dalla creazione di una nuova")
        terapia_originale = next(t for t in terapie if t.id == 1)
        self.assertEqual(terapia_originale.dataFine, date(2026, 6, 30), "La terapia originale non deve essere alterata")

    def test_correggi_terapia_modifica_riga_esistente(self):
        """correggi_terapia aggiorna la stessa riga (stesso id), non ne crea una nuova."""
        successo, esito = self.controller.correggi_terapia(
            id_terapia=1,
            codice_farmaco="F001",
            assunzione_giornaliera=3,
            quantita=60.0,
            indicazioni="Aggiornato",
            data_fine=date(2026, 6, 30),
        )

        self.assertTrue(successo)
        self.assertIn("con successo", esito)

        terapie = self.controller.get_tutte_terapie_paziente("U001")
        self.assertEqual(len(terapie), 1, "correggi_terapia non deve creare nuove righe")
        self.assertEqual(terapie[0].id, 1)
        self.assertEqual(terapie[0].assunzioneGiornaliera, 3)
        self.assertEqual(terapie[0].indicazioni, "Aggiornato")

    def test_correggi_terapia_non_modifica_data_inizio(self):
        """La data di inizio deve restare invariata anche se non viene passata a correggi_terapia."""
        data_inizio_originale = self.controller.get_terapia_by_id(1).dataInizio

        self.controller.correggi_terapia(
            id_terapia=1,
            codice_farmaco="F001",
            assunzione_giornaliera=2,
            quantita=50.0,
            indicazioni="Solo la fine cambia",
            data_fine=date(2026, 8, 15),
        )

        terapia = self.controller.get_terapia_by_id(1)
        self.assertEqual(terapia.dataInizio, data_inizio_originale, "dataInizio non deve mai cambiare")
        self.assertEqual(terapia.dataFine, date(2026, 8, 15))

    def test_correggi_terapia_per_interrompere(self):
        """Interrompere una terapia = correggi_terapia con dataFine = oggi."""
        oggi = date.today()
        # La terapia id=1 e' valida fino al 2026-06-30: la interrompiamo prima, se oggi lo consente,
        # altrimenti verifichiamo comunque che dataFine venga impostata correttamente.
        successo, _ = self.controller.correggi_terapia(
            id_terapia=1,
            codice_farmaco="F001",
            assunzione_giornaliera=2,
            quantita=50.0,
            indicazioni="Terapia interrotta",
            data_fine=date(2026, 1, 1),  # >= dataInizio (2026-01-01)
        )
        self.assertTrue(successo)
        terapia = self.controller.get_terapia_by_id(1)
        self.assertEqual(terapia.dataFine, date(2026, 1, 1))

    def test_correggi_terapia_id_inesistente(self):
        successo, esito = self.controller.correggi_terapia(
            id_terapia=999,
            codice_farmaco="F001",
            assunzione_giornaliera=2,
            quantita=50.0,
            indicazioni="x",
            data_fine=date(2026, 6, 30),
        )
        self.assertFalse(successo)
        self.assertIn("non trovata", esito)

    def test_correggi_terapia_notifica_il_paziente(self):
        """Ogni correzione deve generare una notifica di tipo Terapia per il paziente."""
        self.controller.correggi_terapia(
            id_terapia=1,
            codice_farmaco="F001",
            assunzione_giornaliera=4,
            quantita=50.0,
            indicazioni="Cambio posologia",
            data_fine=date(2026, 6, 30),
        )

        notifiche = self.notifica_controller.get_notifiche_utente("U001", solo_non_lette=True)
        self.assertEqual(len(notifiche), 1)
        self.assertEqual(notifiche[0].tipo.value, "Terapia")
        self.assertIn("modificato", notifiche[0].messaggio)

    def test_validazione_assunzioni_fuori_range(self):
        successo, esito = self.controller.crea_terapia(
            codice_paziente="U002", codice_diabetologo="M001", codice_farmaco="F001",
            assunzione_giornaliera=150000, quantita=10.0, indicazioni="x",
            data_inizio=date(2026, 1, 1), data_fine=date(2026, 12, 31),
        )
        self.assertFalse(successo)
        self.assertIn("assunzioni giornaliere", esito)

    def test_validazione_data_fine_precedente_inizio(self):
        successo, esito = self.controller.crea_terapia(
            codice_paziente="U002", codice_diabetologo="M001", codice_farmaco="F001",
            assunzione_giornaliera=2, quantita=10.0, indicazioni="x",
            data_inizio=date(2026, 6, 1), data_fine=date(2026, 1, 1),
        )
        self.assertFalse(successo)
        self.assertIn("data di fine", esito)

    def test_get_terapie_attive_filtro_temporale(self):
        """Test: Verifica che le terapie scadute vengano escluse dalla lettura."""
        data_valida = date(2026, 3, 1)
        attive_marzo = self.controller.get_terapie_attive_paziente("U001", oggi=data_valida)
        self.assertEqual(len(attive_marzo), 1)

        data_scaduta = date(2026, 8, 1)
        attive_agosto = self.controller.get_terapie_attive_paziente("U001", oggi=data_scaduta)
        self.assertEqual(len(attive_agosto), 0, "La terapia scaduta non deve apparire tra le attive")


if __name__ == "__main__":
    unittest.main()
