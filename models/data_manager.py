# Gestisce lettura/scrittura dei CSV, con lock per evitare scritture concorrenti

import os
import datetime as _dt
import pandas as pd
from filelock import FileLock


class DataManager:

    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.lock_path = csv_path + ".lock"
        if not os.path.exists(csv_path):
            raise FileNotFoundError(
                f"File CSV non trovato: {csv_path}. "
                "Assicurati di aver inizializzato la cartella data/."
            )

    def read_all(self) -> pd.DataFrame:
        with FileLock(self.lock_path):
            return pd.read_csv(self.csv_path)

    def append_row(self, row: dict) -> None:
        with FileLock(self.lock_path):
            df = pd.read_csv(self.csv_path)
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
            df.to_csv(self.csv_path, index=False)

    def update_row(self, key_col: str, key_value, updates: dict) -> bool:
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
        df = self.read_all()
        if df.empty or id_col not in df.columns:
            return 1
        return int(df[id_col].max()) + 1
