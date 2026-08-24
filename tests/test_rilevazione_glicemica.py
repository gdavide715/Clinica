import unittest
from datetime import date, time
from models.rilevazione_glicemica import RilevazioneGlicemica
from models.my_enum.pasto import Pasto

class TestRilevazioneGlicemica(unittest.TestCase):

    def setUp(self):
        """
        Metodo eseguito automaticamente prima di OGNI test.
        Prepariamo le soglie cliniche (come da costanti in config.py).
        """
        self.soglia_pre_min = 80
        self.soglia_pre_max = 130
        self.soglia_post_max = 180
        self.data_test = date(2026, 8, 24)
        self.ora_test = time(12, 0)

    # TEST PRE-PASTO

    def test_glicemia_pre_pasto_nella_norma(self):
        rilevazione = RilevazioneGlicemica(
            id=1, codicePaziente="U001", livelloGlicemia=100.0, 
            data=self.data_test, ora=self.ora_test, momentoPasto=Pasto.PRE_PASTO
        )
        esito = rilevazione.fuori_soglia(self.soglia_pre_min, self.soglia_pre_max, self.soglia_post_max)
        self.assertFalse(esito, "100 mg/dL pre-pasto è nel range (80-130), deve restituire False")

    def test_glicemia_pre_pasto_ipoglicemia(self):
        rilevazione = RilevazioneGlicemica(
            id=2, codicePaziente="U001", livelloGlicemia=70.0, 
            data=self.data_test, ora=self.ora_test, momentoPasto=Pasto.PRE_PASTO
        )
        esito = rilevazione.fuori_soglia(self.soglia_pre_min, self.soglia_pre_max, self.soglia_post_max)
        self.assertTrue(esito, "70 mg/dL pre-pasto è un'ipoglicemia (<80), deve restituire True")

    def test_glicemia_pre_pasto_iperglicemia(self):
        rilevazione = RilevazioneGlicemica(
            id=3, codicePaziente="U001", livelloGlicemia=140.0, 
            data=self.data_test, ora=self.ora_test, momentoPasto=Pasto.PRE_PASTO
        )
        esito = rilevazione.fuori_soglia(self.soglia_pre_min, self.soglia_pre_max, self.soglia_post_max)
        self.assertTrue(esito, "140 mg/dL pre-pasto è un'iperglicemia (>130), deve restituire True")


    # TEST POST-PASTO

    def test_glicemia_post_pasto_nella_norma(self):
        rilevazione = RilevazioneGlicemica(
            id=4, codicePaziente="U001", livelloGlicemia=160.0, 
            data=self.data_test, ora=time(14, 0), momentoPasto=Pasto.POST_PASTO
        )
        esito = rilevazione.fuori_soglia(self.soglia_pre_min, self.soglia_pre_max, self.soglia_post_max)
        self.assertFalse(esito, "160 mg/dL post-pasto è tollerato (<180), deve restituire False")

    def test_glicemia_post_pasto_iperglicemia(self):
        rilevazione = RilevazioneGlicemica(
            id=5, codicePaziente="U001", livelloGlicemia=200.0, 
            data=self.data_test, ora=time(14, 0), momentoPasto=Pasto.POST_PASTO
        )
        esito = rilevazione.fuori_soglia(self.soglia_pre_min, self.soglia_pre_max, self.soglia_post_max)
        self.assertTrue(esito, "200 mg/dL post-pasto è un'iperglicemia (>180), deve restituire True")

if __name__ == "__main__":
    unittest.main()