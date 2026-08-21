from dataclasses import dataclass
from datetime import date
from models.my_enum.tipo_notifica import TipoNotifica

@dataclass
class Notifica:
    id: int
    codiceUtente: str
    tipo: TipoNotifica
    messaggio: str
    data: date
    letta: bool

    @staticmethod
    def from_row(row: dict) -> "Notifica":
        letta_val = row["letta"]
        if isinstance(letta_val, str):
            letta_bool = letta_val.lower() == 'true'
        else:
            letta_bool = bool(letta_val)

        return Notifica(
            id=int(row["id"]),
            codiceUtente=row["codiceUtente"],
            tipo=TipoNotifica(row["tipo"]),
            messaggio=row["messaggio"],
            data=date.fromisoformat(str(row["data"])),
            letta=letta_bool,
        )

    def to_row(self) -> dict:
        """Rappresentazione pronta per la scrittura su notifiche.csv."""
        return {
            "id": self.id,
            "codiceUtente": self.codiceUtente,
            "tipo": self.tipo.value,
            "messaggio": self.messaggio,
            "data": self.data,
            "letta": self.letta,
        }