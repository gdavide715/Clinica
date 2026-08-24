import unittest
from models.paziente import Paziente
from models.diabetologo import Diabetologo

class TestUtentiModels(unittest.TestCase):

    def setUp(self):
        """
        Prepariamo un dizionario di base che simula una riga letta da utenti.csv.
        Questo dizionario è comune sia per i pazienti che per i medici.
        """
        self.row_utente_base = {
            "codiceUtente": "U123",
            "username": "mrossi",
            "password": "pwd_segreta",
            "nome": "Mario",
            "cognome": "Rossi",
            "dataNascita": "1980-01-01",
            "codiceFiscale": "RSSMRA80A01H501X"
        }

    def test_metodo_full_name_ereditato(self):
        """Test: Il metodo full_name() ereditato dalla classe astratta Utente funziona correttamente."""
        row_paziente = {"codiceMedicoRiferimento": "M001"}
        paziente = Paziente.from_row(self.row_utente_base, row_paziente)
        
        self.assertEqual(
            paziente.full_name(), 
            "Mario Rossi", 
            "Il nome completo deve essere la concatenazione di nome e cognome"
        )

    def test_creazione_paziente_da_dizionari_multipli(self):
        """Test: Paziente.from_row() fonde correttamente i dati anagrafici e clinici."""
        row_paziente = {"codiceMedicoRiferimento": "M001"}
        
        paziente = Paziente.from_row(self.row_utente_base, row_paziente)
        
        # Verifica che abbia ereditato i dati da Utente
        self.assertEqual(paziente.codiceUtente, "U123")
        self.assertEqual(paziente.codiceFiscale, "RSSMRA80A01H501X")
        
        # Verifica che abbia i dati specifici del Paziente
        self.assertEqual(paziente.codiceMedicoRiferimento, "M001")

    def test_creazione_diabetologo_da_dizionari_multipli(self):
        """Test: Diabetologo.from_row() fonde correttamente i dati anagrafici e professionali."""
        row_medico = {"email": "mario.rossi@clinica.it"}
        
        medico = Diabetologo.from_row(self.row_utente_base, row_medico)
        
        # Verifica che abbia ereditato i dati da Utente
        self.assertEqual(medico.codiceUtente, "U123")
        
        # Verifica che abbia i dati specifici del Medico
        self.assertEqual(medico.email, "mario.rossi@clinica.it")


if __name__ == "__main__":
    unittest.main()