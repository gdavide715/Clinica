from dataclasses import dataclass


@dataclass
class Farmaco:
    codiceFarmaco: str
    nome: str

    @staticmethod
    def from_row(row: dict) -> "Farmaco":
        return Farmaco(codiceFarmaco=row["codiceFarmaco"], nome=row["nome"])
