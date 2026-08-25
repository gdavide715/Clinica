# DataManager: layer di accesso ai dati (il nostro "database" su CSV).


import os
import datetime as _dt
import pandas as pd
from filelock import FileLock  # è un lucchetto per non permettere di 
# leggere/modificare lo stesso file csv in cotemporanea e avere problemi di lettura inconsistente, lettura sporca, aggiornamento fantasma....
# df.to_csv riscrive l'intero file csv --> serve un semaforo

class DataManager:
    # Gestisce lettura/scrittura di una singola 'tabella' CSV."""

    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.lock_path = csv_path + ".lock"
        if not os.path.exists(csv_path):
            raise FileNotFoundError(
                f"File CSV non trovato: {csv_path}. "
                "Assicurati di aver inizializzato la cartella data/."
            )

    def read_all(self) -> pd.DataFrame:
        # Restituisce l'intero contenuto della tabella come DataFrame.
        
        # un richiesta fatta dentro il blocco with FileLock(...) blocca
        # qualsiasi altra richiesta che prova ad acquisire lo stesso lock facendola restare in attesa
        # FileLock crea un file .lock accanto al file .csv che funge da semaforo e si salva il file fino al quel momento
        
        with FileLock(self.lock_path):
            return pd.read_csv(self.csv_path)

    def append_row(self, row: dict) -> None:
        # Aggiunge una riga in coda al CSV.
        with FileLock(self.lock_path):
            df = pd.read_csv(self.csv_path)
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
            df.to_csv(self.csv_path, index=False)

    def update_row(self, key_col: str, key_value, updates: dict) -> bool:
        
        # Aggiorna la prima riga con key_col == key_value applicando updates.
        # Restituisce True se una riga è stata trovata e aggiornata.
        
        with FileLock(self.lock_path):
            df = pd.read_csv(self.csv_path)
            mask = df[key_col] == key_value
            if not mask.any():
                return False
            for col, val in updates.items():
                if isinstance(val, (_dt.date, _dt.time, _dt.datetime)):
                    val = str(val)
                df.loc[mask, col] = val
            df.to_csv(self.csv_path, index=False)
            return True

    def delete_row(self, key_col: str, key_value) -> bool:
        with FileLock(self.lock_path):
            df = pd.read_csv(self.csv_path)
            mask = df[key_col] == key_value
            if not mask.any():
                return False
            df = df[~mask]
            df.to_csv(self.csv_path, index=False)
            return True

    def get_next_id(self, id_col: str = "id") -> int:
        # per generare id incrementali
        df = self.read_all()
        if df.empty or id_col not in df.columns:
            return 1
        return int(df[id_col].max()) + 1
