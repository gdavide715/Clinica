"""
Implementa il sequence diagram "RilevazioneRegistrazioneGlicemia.txt"
con l'aggiunta delle notifiche persistenti e della gravità differenziata.
"""
from datetime import date, time

from config import (
    CSV_PATHS,
    GLICEMIA_PRE_PASTO_MIN,
    GLICEMIA_PRE_PASTO_MAX,
    GLICEMIA_POST_PASTO_MAX,
)
from models.data_manager import DataManager
from models.rilevazione_glicemica import RilevazioneGlicemica
from models.my_enum.pasto import Pasto
from models.my_enum.tipo_notifica import TipoNotifica
from controllers.notifica_controller import NotificaController


class GlicemiaController:

    LIVELLO_GLICEMIA_MIN, LIVELLO_GLICEMIA_MAX = 10, 600

    def __init__(self):
        self.dm_rilevazioni = DataManager(CSV_PATHS["rilevazioni_glicemiche"])
        self.dm_pazienti = DataManager(CSV_PATHS["pazienti"])
        self.notifica_controller = NotificaController()

    def inserisci_rilevazione(self, codice_paziente: str, data_ril: date, ora: time,
                           livello_glicemia: float, momento_pasto: Pasto) -> tuple[bool, str, bool, str | None]:
        """
        Restituisce (successo: bool, esito: str, alert_inviato: bool, codice_medico: str|None).
        Se successo e' False, esito contiene il messaggio di errore e gli
        altri due campi sono rispettivamente False e None.
        """
        if livello_glicemia is None or not (self.LIVELLO_GLICEMIA_MIN <= livello_glicemia <= self.LIVELLO_GLICEMIA_MAX):
            return False, (
                f"Il livello di glicemia deve essere un valore tra "
                f"{self.LIVELLO_GLICEMIA_MIN} e {self.LIVELLO_GLICEMIA_MAX} mg/dL."
            ), False, None

        nuovo_id = self.dm_rilevazioni.get_next_id("id")
        rilevazione = RilevazioneGlicemica(
            id=nuovo_id,
            codicePaziente=codice_paziente,
            livelloGlicemia=livello_glicemia,
            data=data_ril,
            ora=ora,
            momentoPasto=momento_pasto,
        )
        
        # Salvataggio fisico nel file rilevazioni_glicemiche.csv
        self.dm_rilevazioni.append_row(rilevazione.to_row())

        fuori_soglia = rilevazione.fuori_soglia(
            GLICEMIA_PRE_PASTO_MIN, GLICEMIA_PRE_PASTO_MAX, GLICEMIA_POST_PASTO_MAX
        )

        alert_inviato = False
        codice_medico = None
        esito = "nella norma"

        if fuori_soglia:
            # 1. Calcolo matematico dello scarto dai limiti consentiti
            delta = 0
            if momento_pasto == Pasto.PRE_PASTO:
                if livello_glicemia < GLICEMIA_PRE_PASTO_MIN:
                    delta = GLICEMIA_PRE_PASTO_MIN - livello_glicemia
                elif livello_glicemia > GLICEMIA_PRE_PASTO_MAX:
                    delta = livello_glicemia - GLICEMIA_PRE_PASTO_MAX
            else:
                if livello_glicemia > GLICEMIA_POST_PASTO_MAX:
                    delta = livello_glicemia - GLICEMIA_POST_PASTO_MAX
            
            # 2. Assegnazione gravità differenziata in base allo scarto
            if delta <= 20:
                gravita = "Lieve"
            elif delta <= 50:
                gravita = "Media"
            else:
                gravita = "Grave"
                
            esito = f"fuori soglia ({gravita})"

            # 3. Identificazione del medico e salvataggio della notifica persistente
            df_pazienti = self.dm_pazienti.read_all()
            row = df_pazienti[df_pazienti["codiceUtente"] == codice_paziente]
            
            if not row.empty:
                codice_medico = row.iloc[0]["codiceMedicoRiferimento"]
                alert_inviato = True 
                
                # Costruiamo il testo che il medico leggerà nella sua Tab
                msg = (f"Anomalia {gravita.upper()}: glicemia a {livello_glicemia} mg/dL "
                       f"({momento_pasto.value}) registrata il {data_ril} alle {ora.strftime('%H:%M')}. "
                       f"Paziente: {codice_paziente}")
                
                # Scrittura su notifiche.csv per renderla leggibile al prossimo login
                self.notifica_controller.crea_notifica(
                    codice_utente=codice_medico,
                    tipo=TipoNotifica.GLICEMIA,
                    messaggio=msg,
                    data_notifica=date.today()
                )

        return True, esito, alert_inviato, codice_medico

    def get_storico_paziente(self, codice_paziente: str) -> list[RilevazioneGlicemica]:
        """Restituisce lo storico delle rilevazioni glicemiche di un paziente."""
        df = self.dm_rilevazioni.read_all()
        if df.empty or "codicePaziente" not in df.columns:
            return []
            
        df_paziente = df[df["codicePaziente"] == codice_paziente]
        return [RilevazioneGlicemica.from_row(row) for row in df_paziente.to_dict("records")]