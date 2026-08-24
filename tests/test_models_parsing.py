import unittest
from datetime import date, time
from models.notifica import Notifica
from models.my_enum.tipo_notifica import TipoNotifica
from models.rilevazione_glicemica import RilevazioneGlicemica
from models.my_enum.pasto import Pasto

class TestModelsParsing(unittest.TestCase):

    def test_parsing_notifica_da_dizionario(self):
        """
        Simula una riga letta dal CSV (tutte stringhe) e verifica 
        che from_row la converta nei tipi corretti (int, Enum, date, bool).
        """
        riga_csv = {
            "id": "10",
            "codiceUtente": "U001",
            "tipo": "Glicemia",
            "messaggio": "Allarme test",
            "data": "2026-08-24",
            "letta": "False" # Pandas spesso restituisce i booleani come stringhe
        }
        
        notifica = Notifica.from_row(riga_csv)
        
        self.assertIsInstance(notifica.id, int)
        self.assertEqual(notifica.id, 10)
        
        self.assertIsInstance(notifica.tipo, TipoNotifica)
        self.assertEqual(notifica.tipo, TipoNotifica.GLICEMIA)
        
        self.assertIsInstance(notifica.data, date)
        self.assertEqual(notifica.data, date(2026, 8, 24))
        
        self.assertIsInstance(notifica.letta, bool)
        self.assertFalse(notifica.letta)

    def test_parsing_notifica_booleano_true(self):
        """Verifica che la stringa 'True' venga convertita nel booleano True."""
        riga_csv = {
            "id": "11", "codiceUtente": "M001", "tipo": "Farmaco", 
            "messaggio": "Test", "data": "2026-08-24", 
            "letta": "True" 
        }
        notifica = Notifica.from_row(riga_csv)
        self.assertTrue(notifica.letta)

    def test_parsing_rilevazione_glicemica(self):
        """
        Testa la conversione di float, orari (time) e del momento del pasto (Enum).
        """
        riga_csv = {
            "id": "5",
            "codicePaziente": "U002",
            "livelloGlicemia": "145.5",
            "data": "2026-08-24",
            "ora": "14:30",
            "momentoPasto": "post_pasto"
        }
        
        ril = RilevazioneGlicemica.from_row(riga_csv)
        
        self.assertIsInstance(ril.id, int)
        self.assertIsInstance(ril.livelloGlicemia, float)
        self.assertEqual(ril.livelloGlicemia, 145.5)
        
        self.assertIsInstance(ril.ora, time)
        self.assertEqual(ril.ora, time(14, 30))
        
        self.assertIsInstance(ril.momentoPasto, Pasto)
        self.assertEqual(ril.momentoPasto, Pasto.POST_PASTO)

if __name__ == "__main__":
    unittest.main()