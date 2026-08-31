# Path CSV e costanti cliniche

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

CSV_PATHS = {
    "utenti": os.path.join(DATA_DIR, "utenti.csv"),
    "pazienti": os.path.join(DATA_DIR, "pazienti.csv"),
    "farmaci": os.path.join(DATA_DIR, "farmaci.csv"),
    "terapie": os.path.join(DATA_DIR, "terapie.csv"),
    "assunzioni_farmaco": os.path.join(DATA_DIR, "assunzioni_farmaco.csv"),
    "rilevazioni_glicemiche": os.path.join(DATA_DIR, "rilevazioni_glicemiche.csv"),
    "segnalazioni_paziente": os.path.join(DATA_DIR, "segnalazioni_paziente.csv"),
    "anamnesi_paziente": os.path.join(DATA_DIR, "anamnesi_paziente.csv"),
    "diabetologi": os.path.join(DATA_DIR, "diabetologi.csv"),
    "notifiche": os.path.join(DATA_DIR, "notifiche.csv"),
}

# soglie glicemia mg/dL, da specifica
GLICEMIA_PRE_PASTO_MIN = 80
GLICEMIA_PRE_PASTO_MAX = 130
GLICEMIA_POST_PASTO_MAX = 180

GIORNI_CONSECUTIVI_ALERT_MEDICO = 3
