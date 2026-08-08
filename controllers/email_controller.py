"""
Gestisce l'invio e la ricezione delle email interne tra Paziente e Diabetologo.
"""
from datetime import date
from config import CSV_PATHS
from models.data_manager import DataManager

class EmailController:
    def __init__(self):
        self.dm_email = DataManager(CSV_PATHS["email"])
        self.dm_pazienti = DataManager(CSV_PATHS["pazienti"])

    def invia_email(self, codice_paziente: str, oggetto: str, testo: str, data_invio: date) -> str:
        # Recupera il medico di riferimento del paziente
        df_pazienti = self.dm_pazienti.read_all()
        paziente = df_pazienti[df_pazienti["codiceUtente"] == codice_paziente]
        
        if paziente.empty:
            return "Errore: Impossibile trovare il tuo profilo paziente."
            
        codice_medico = paziente.iloc[0]["codiceMedicoRiferimento"]

        nuovo_id = self.dm_email.get_next_id("id")
        self.dm_email.append_row({
            "id": nuovo_id,
            "codicePaziente": codice_paziente,
            "codiceMedico": codice_medico,
            "oggetto": oggetto,
            "testo": testo,
            "data_invio": data_invio
        })
        return "Email inviata correttamente al tuo diabetologo di riferimento."

    def leggi_email_medico(self, codice_medico: str):
        df_email = self.dm_email.read_all()
        if df_email.empty or "codiceMedico" not in df_email.columns:
            return []
        
        # Filtra solo le email destinate a questo medico specifico
        email_medico = df_email[df_email["codiceMedico"] == codice_medico]
        return email_medico.to_dict('records')