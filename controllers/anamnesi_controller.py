"""
Controller per la gestione dell'anamnesi clinica del paziente.
"""
from config import CSV_PATHS
from models.data_manager import DataManager
from models.anamnesi_paziente import AnamnesiPaziente
from models.my_enum.tipo_condizione_clinica import TipoCondizioneClinica

class AnamnesiController:
    def __init__(self):
        self.dm_anamnesi = DataManager(CSV_PATHS.get("anamnesi_paziente", "data/anamnesi_paziente.csv"))

    def ottieni_anamnesi(self, codice_paziente: str) -> dict:
        """Recupera e formatta l'anamnesi raggruppandola per tipologia."""
        df = self.dm_anamnesi.read_all()
        
        risultati = {
            TipoCondizioneClinica.PREGRESSA_PATOLOGIA.value: [],
            TipoCondizioneClinica.COMORBIDITA.value: [],
            TipoCondizioneClinica.FATTORE_RISCHIO.value: []
        }
        
        if df.empty or "codicePaziente" not in df.columns:
            return risultati

        # Filtriamo le righe come fatto negli altri controller
        record_paz = df[df["codicePaziente"] == codice_paziente]

        for row in record_paz.to_dict("records"):
            anamnesi = AnamnesiPaziente.from_row(row)
            if anamnesi.tipologia.value in risultati:
                risultati[anamnesi.tipologia.value].append(anamnesi.descrizione)

        return {
            TipoCondizioneClinica.PREGRESSA_PATOLOGIA.value: "\n".join(risultati[TipoCondizioneClinica.PREGRESSA_PATOLOGIA.value]),
            TipoCondizioneClinica.COMORBIDITA.value: "\n".join(risultati[TipoCondizioneClinica.COMORBIDITA.value]),
            TipoCondizioneClinica.FATTORE_RISCHIO.value: "\n".join(risultati[TipoCondizioneClinica.FATTORE_RISCHIO.value])
        }

    def aggiorna_anamnesi(self, codice_paziente: str, patologie: str, comorbidita: str, fattori_rischio: str) -> tuple[bool, str]:
        """Sovrascrive l'anamnesi spezzettando i testi in record singoli."""
        if not codice_paziente:
            return False, "Codice paziente mancante."

        # 1. Eliminiamo i vecchi record
        self.dm_anamnesi.delete_row("codicePaziente", codice_paziente)

        # 2. Funzione interna di supporto per salvare i singoli record
        def salva_voci(testo: str, tipologia: TipoCondizioneClinica):
            if not testo:
                return

            voci = [v.strip() for v in testo.replace(',', '\n').split('\n') if v.strip()]

            for voce in voci:
                nuovo_id = self.dm_anamnesi.get_next_id("id")
                anamnesi = AnamnesiPaziente(
                    id=nuovo_id,
                    codicePaziente=codice_paziente,
                    tipologia=tipologia,
                    descrizione=voce
                )
                self.dm_anamnesi.append_row(anamnesi.to_row())

        # 3. Creazione delle nuove righe
        salva_voci(patologie, TipoCondizioneClinica.PREGRESSA_PATOLOGIA)
        salva_voci(comorbidita, TipoCondizioneClinica.COMORBIDITA)
        salva_voci(fattori_rischio, TipoCondizioneClinica.FATTORE_RISCHIO)

        return True, "Anamnesi aggiornata con successo nel fascicolo clinico."