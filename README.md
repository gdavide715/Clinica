# Sistema di Telemedicina per Pazienti Diabetici

Applicazione web (Dash + Plotly) con persistenza su CSV, architettura MVC.

## Struttura

```
models/       -> Entità (dataclass) + DataManager (accesso CSV)
controllers/  -> Logica di business
views/        -> Layout e callback Dash
data/         -> CSV
tests/        -> Test automatici (unittest)
```

## Funzionalità principali

- Login con ruoli separati (paziente / diabetologo)
- Diario glicemico con calcolo automatico di gravità e alert al medico
- Registrazione assunzioni farmaco, verificata contro la terapia prescritta
- Prescrizione di nuove terapie e modifica di quelle esistenti (la data di
  inizio non è modificabile una volta fissata)
- Segnalazioni cliniche del paziente e anamnesi gestita dal medico
- Alert automatico per mancata assunzione farmaci (job periodico)
- Centro notifiche persistente per entrambi i ruoli
- Contatto diretto col medico via Gmail (l'email del paziente non viene
  gestita internamente all'app)

