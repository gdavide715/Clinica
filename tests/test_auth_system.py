import unittest
import os
from config import CSV_PATHS
from controllers.auth_controller import AuthController
from models.paziente import Paziente
from models.diabetologo import Diabetologo

class TestAuthSystem(unittest.TestCase):

    def setUp(self):
        """
        Prepariamo l'ambiente isolato:
        Creiamo tre file temporanei per utenti, pazienti e medici
        con tutte le colonne anagrafiche richieste dai modelli.
        """
        self.test_utenti_csv = "data/test_utenti.csv"
        self.test_pazienti_csv = "data/test_pazienti.csv"
        self.test_diabetologi_csv = "data/test_diabetologi.csv"
        
        # Salviamo i percorsi originali
        self.orig_utenti = CSV_PATHS.get("utenti")
        self.orig_pazienti = CSV_PATHS.get("pazienti")
        self.orig_diabetologi = CSV_PATHS.get("diabetologi")
        
        # Dirottiamo il sistema sui file temporanei
        CSV_PATHS["utenti"] = self.test_utenti_csv
        CSV_PATHS["pazienti"] = self.test_pazienti_csv
        CSV_PATHS["diabetologi"] = self.test_diabetologi_csv
        
        # 1. Creiamo un file utenti.csv completo
        with open(self.test_utenti_csv, "w") as f:
            f.write("codiceUtente,username,password,ruolo,nome,cognome,dataNascita,codiceFiscale\n")
            f.write("U999,paz_test,pwd123,paziente,Mario,Rossi,1980-01-01,RSSMRA80A01H501X\n")
            f.write("M999,med_test,pwd456,diabetologo,Luigi,Verdi,1970-05-10,VRDLGU70E10H501Y\n")
            
        # 2. Creiamo il file pazienti.csv
        with open(self.test_pazienti_csv, "w") as f:
            f.write("codiceUtente,codiceMedicoRiferimento\n")
            f.write("U999,M999\n")
            
        # 3. Creiamo il file diabetologi.csv
        with open(self.test_diabetologi_csv, "w") as f:
            f.write("codiceUtente,email\n")
            f.write("M999,luigi.verdi@clinica.it\n")
            
        self.auth_controller = AuthController()

    def tearDown(self):
        """Pulizia: eliminiamo i file finti e ripristiniamo i percorsi originali."""
        for path in [self.test_utenti_csv, self.test_pazienti_csv, self.test_diabetologi_csv]:
            if os.path.exists(path):
                os.remove(path)
                
        if self.orig_utenti: CSV_PATHS["utenti"] = self.orig_utenti
        if self.orig_pazienti: CSV_PATHS["pazienti"] = self.orig_pazienti
        if self.orig_diabetologi: CSV_PATHS["diabetologi"] = self.orig_diabetologi

    def test_login_successo_paziente(self):
        """Test: Autenticazione corretta come paziente e verifica fusione dati."""
        successo, ruolo, utente = self.auth_controller.login("paz_test", "pwd123")
        
        self.assertTrue(successo, "Il login deve avere successo")
        self.assertEqual(ruolo, "paziente", "Il ruolo restituito deve essere 'paziente'")
        self.assertIsInstance(utente, Paziente, "L'oggetto restituito deve essere un'istanza di Paziente")
        self.assertEqual(utente.codiceFiscale, "RSSMRA80A01H501X")
        self.assertEqual(utente.codiceMedicoRiferimento, "M999")

    def test_login_successo_medico(self):
        """Test: Autenticazione corretta come medico diabetologo."""
        successo, ruolo, utente = self.auth_controller.login("med_test", "pwd456")
        
        self.assertTrue(successo)
        self.assertEqual(ruolo, "diabetologo")
        self.assertIsInstance(utente, Diabetologo)
        self.assertEqual(utente.email, "luigi.verdi@clinica.it")

    def test_login_fallito_password_errata(self):
        """Test: Credenziali sbagliate devono essere respinte."""
        successo, ruolo, msg = self.auth_controller.login("paz_test", "sbagliata")
        
        self.assertFalse(successo)
        self.assertIsNone(ruolo)
        self.assertIn("errate", msg.lower())

    def test_login_fallito_utente_inesistente(self):
        """Test: Utente non presente a sistema."""
        successo, ruolo, msg = self.auth_controller.login("fantasma", "1234")
        
        self.assertFalse(successo)
        self.assertIsNone(ruolo)

if __name__ == "__main__":
    unittest.main()