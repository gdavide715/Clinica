import unittest
from datetime import date
from models.terapia import TerapiaDiabetica

class TestTerapiaDiabetica(unittest.TestCase):

    def setUp(self):
        """
        Creiamo un'istanza di TerapiaDiabetica valida 
        per tutto l'anno 2026, da riutilizzare in ogni test.
        """
        self.terapia = TerapiaDiabetica(
            id=1,
            codicePaziente="U001",
            codiceDiabetologo="M001",
            codiceFarmaco="F001",
            assunzioneGiornaliera=2,
            quantita=50.0,
            indicazioni="Assumere dopo i pasti",
            dataInizio=date(2026, 1, 1),
            dataFine=date(2026, 12, 31),
            ultimaModifica=date(2026, 1, 1)
        )

    def test_terapia_attiva_nel_periodo(self):
        # 24 Agosto 2026 è in pieno periodo di validità
        data_test = date(2026, 8, 24)
        self.assertTrue(
            self.terapia.is_attiva(data_test), 
            "La terapia dovrebbe risultare attiva ad Agosto 2026"
        )

    def test_terapia_non_ancora_iniziata(self):
        # Una data antecedente a dataInizio (es. fine 2025)
        data_test = date(2025, 12, 31)
        self.assertFalse(
            self.terapia.is_attiva(data_test), 
            "La terapia non dovrebbe essere attiva prima della sua data di inizio"
        )

    def test_terapia_scaduta(self):
        # Una data successiva a dataFine (es. inizio 2027)
        data_test = date(2027, 1, 1)
        self.assertFalse(
            self.terapia.is_attiva(data_test), 
            "La terapia non dovrebbe essere attiva dopo la sua data di fine"
        )

    def test_terapia_attiva_giorno_esatto_inizio(self):
        # Limite inferiore: esattamente il 1° Gennaio 2026
        data_test = date(2026, 1, 1)
        self.assertTrue(
            self.terapia.is_attiva(data_test), 
            "La terapia deve risultare attiva proprio nel giorno in cui inizia"
        )

    def test_terapia_attiva_giorno_esatto_fine(self):
        # Limite superiore: esattamente il 31 Dicembre 2026
        data_test = date(2026, 12, 31)
        self.assertTrue(
            self.terapia.is_attiva(data_test), 
            "La terapia deve risultare attiva nell'ultimo giorno di validità"
        )

if __name__ == "__main__":
    unittest.main()