"""View — dashboard del paziente.

Lo stile grafico e' definito in assets/style.css. Questo file si occupa
solo di struttura (layout) e comportamento (callback). L'accesso ai dati
passa sempre da un controller, mai da DataManager/CSV direttamente.
"""

from datetime import datetime, date
import urllib.parse
from dash import html, dcc, Input, Output, State, callback

from controllers.glicemia_controller import GlicemiaController
from controllers.assunzione_farmaco_controller import AssunzioneFarmacoController
from controllers.farmaco_controller import FarmacoController
from controllers.segnalazione_controller import SegnalazioneController
from controllers.contatto_controller import ContattoController
from controllers.terapia_controller import TerapiaController
from models.my_enum.pasto import Pasto
from models.my_enum.tipo_segnalazione_paziente import TipoSegnalazionePaziente

segnalazione_controller = SegnalazioneController()
glicemia_controller = GlicemiaController()
assunzione_controller = AssunzioneFarmacoController()
farmaco_controller = FarmacoController()
contatto_controller = ContattoController()
terapia_controller = TerapiaController()


def _terapia_attiva_per_id(codice_paziente, id_terapia):
    """Trova, tra le terapie attive del paziente, quella con l'id dato."""
    terapie = terapia_controller.get_terapie_attive_paziente(codice_paziente)
    return next((t for t in terapie if t.id == id_terapia), None)


def _opzioni_terapie_paziente(codice_paziente):
    """
    Costruisce le opzioni del dropdown 'Terapia prescritta' a partire dalle
    terapie ATTIVE del paziente loggato (usa TerapiaDiabetica.is_attiva(),
    cosi' una terapia scaduta non compare piu' come opzione). Ogni opzione
    mostra il nome del farmaco e la posologia, cosi' il paziente sceglie la
    terapia senza dover conoscere o digitare codici tecnici.
    """
    if not codice_paziente:
        return []

    terapie_attive = terapia_controller.get_terapie_attive_paziente(codice_paziente)

    opzioni = []
    for terapia in terapie_attive:
        farmaco = farmaco_controller.get_farmaco(terapia.codiceFarmaco)
        nome_farmaco = farmaco.nome if farmaco else terapia.codiceFarmaco

        label = (
            f"{nome_farmaco} — {terapia.assunzioneGiornaliera}x/giorno "
            f"da {terapia.quantita} ({terapia.indicazioni})"
        )
        opzioni.append({"label": label, "value": terapia.id})

    return opzioni


# Opzioni del dropdown "Tipo Evento" costruite a partire dall'enum, cosi'
# se TipoSegnalazionePaziente cambia le opzioni si aggiornano da sole
# invece di disallinearsi silenziosamente.
_OPZIONI_TIPO_SEGNALAZIONE = [
    {'label': 'Sintomo', 'value': TipoSegnalazionePaziente.SINTOMO.value},
    {'label': 'Patologia Concomitante', 'value': TipoSegnalazionePaziente.PATOLOGIA_CONCOMITANTE.value},
    {'label': 'Terapia Concomitante', 'value': TipoSegnalazionePaziente.TERAPIA_CONCOMITANTE.value},
]

_OPZIONI_MOMENTO_PASTO = [
    {'label': 'Prima dei pasti (Pre-pasto)', 'value': Pasto.PRE_PASTO.value},
    {'label': 'Dopo i pasti (Post-pasto)', 'value': Pasto.POST_PASTO.value},
]


def paziente_layout(session_data):
    """Genera il layout per l'utente loggato come paziente."""
    nome = session_data.get("nome", "Paziente")

    # Email del diabetologo di riferimento, recuperata dinamicamente
    # (pazienti.csv -> codiceMedicoRiferimento -> diabetologi.csv -> email)
    codice_paz_corrente = session_data.get("codiceUtente")
    email_diabetologo = contatto_controller.get_email_medico(codice_paz_corrente)
    oggetto_email = f"Richiesta consulenza - Paziente {nome}"

    if email_diabetologo:
        params = urllib.parse.urlencode({'to': email_diabetologo, 'su': oggetto_email})
        gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&{params}"
    else:
        gmail_url = None

    return html.Div(className="dashboard-card", children=[
        html.Div([
            html.H2(f"Area Paziente — Benvenuto/a, {nome}", className="dashboard-header"),
            html.Button("Logout", id="btn-logout", className="btn-logout"),
        ]),
        html.P("Da questa dashboard puoi registrare i tuoi parametri clinici e l'assunzione delle terapie prescritte dal tuo diabetologo.", className="dashboard-subtitle"),
        html.Hr(),

        dcc.Tabs([
            # Rilevazione Glicemica
            dcc.Tab(label='Diario Glicemico', children=[
                html.Div(className="tab-content", children=[
                    html.H4("Nuova Rilevazione"),

                    html.Label("Data della misurazione", className="form-label"),
                    dcc.DatePickerSingle(
                        id="paz-glic-data", placeholder="Seleziona la data",
                        display_format="YYYY-MM-DD", max_date_allowed=date.today(),
                        className="form-datepicker",
                    ),

                    html.Label("Ora della misurazione", className="form-label"),
                    dcc.Input(id="paz-glic-ora", type="time", className="form-input"),

                    html.Label("Livello Glicemia (mg/dL)", className="form-label"),
                    dcc.Input(id="paz-glic-livello", type="number", placeholder="es. 110", className="form-input"),

                    html.Label("Momento del Pasto", className="form-label"),
                    dcc.Dropdown(id="paz-glic-pasto", options=_OPZIONI_MOMENTO_PASTO, placeholder="Seleziona...", className="form-dropdown"),

                    html.Button("Salva Glicemia", id="btn-salva-glic", n_clicks=0, className="btn btn-verde"),
                    html.Div(id="msg-glicemia", className="msg-box--empty"),
                ])
            ]),

            # Assunzione Farmaci
            dcc.Tab(label='Assunzione Terapie', children=[
                html.Div(className="tab-content", children=[
                    html.H4("Registra Farmaco"),

                    html.Label("Terapia prescritta", className="form-label"),
                    dcc.Dropdown(
                        id="paz-farm-terapia-select",
                        options=_opzioni_terapie_paziente(codice_paz_corrente),
                        placeholder="Seleziona la terapia per cui registri l'assunzione...",
                        className="form-dropdown",
                    ),

                    html.Label("Data assunzione", className="form-label"),
                    dcc.DatePickerSingle(
                        id="paz-farm-data", placeholder="Seleziona la data",
                        display_format="YYYY-MM-DD", max_date_allowed=date.today(),
                        className="form-datepicker",
                    ),

                    html.Label("Ora assunzione", className="form-label"),
                    dcc.Input(id="paz-farm-ora", type="time", className="form-input"),

                    html.Label("Quantità assunta", className="form-label"),
                    dcc.Input(id="paz-farm-qty", type="number", placeholder="es. 1", className="form-input"),

                    html.Button("Registra Assunzione", id="btn-salva-farm", n_clicks=0, className="btn btn-blu"),
                    html.Div(id="msg-farmaco", className="msg-box--empty"),
                ])
            ]),

            # Invia Segnalazione
            dcc.Tab(label='Invia Segnalazione', children=[
                html.Div(className="tab-content", children=[
                    html.H4("Nuova Segnalazione (Sintomi o Patologie)"),

                    html.Label("Tipo Evento", className="form-label"),
                    dcc.Dropdown(id="paz-seg-evento", options=_OPZIONI_TIPO_SEGNALAZIONE, placeholder="Seleziona...", className="form-dropdown"),

                    html.Label("Descrizione", className="form-label"),
                    dcc.Textarea(id="paz-seg-desc", className="form-textarea"),

                    html.Label("Data Inizio", className="form-label form-label--inline"),
                    dcc.DatePickerSingle(
                        id="paz-seg-inizio", placeholder="Seleziona la data",
                        display_format="YYYY-MM-DD", className="form-datepicker",
                    ),

                    html.Label("Data Fine", className="form-label form-label--inline"),
                    dcc.DatePickerSingle(
                        id="paz-seg-fine", placeholder="Seleziona la data",
                        display_format="YYYY-MM-DD", className="form-datepicker",
                    ),

                    html.Button("Invia al Medico", id="btn-salva-seg", n_clicks=0, className="btn btn-arancio"),
                    html.Div(id="msg-segnalazione", className="msg-box--empty"),
                ])
            ]),

            # Contatta il Medico
            dcc.Tab(label='Contatta il Medico', children=[
                html.Div(className="tab-content contatto-medico-box", children=[
                    html.H4("Hai bisogno di contattare il tuo Diabetologo?"),
                    html.P("Clicca sul pulsante sottostante per aprire Gmail e inviare direttamente un'email al tuo medico curante."),

                    html.A("✉️ Apri Gmail e scrivi al Medico", href=gmail_url, target="_blank", className="btn-gmail")
                    if gmail_url else
                    html.P("Email del medico non disponibile al momento. Contatta l'assistenza.", className="contatto-medico-errore")
                ])
            ])
        ])
    ])


@callback(
    Output("msg-glicemia", "children"),
    Output("msg-glicemia", "className"),
    Input("btn-salva-glic", "n_clicks"),
    State("paz-glic-data", "date"),
    State("paz-glic-ora", "value"),
    State("paz-glic-livello", "value"),
    State("paz-glic-pasto", "value"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def handle_salva_glicemia(n_clicks, data_str, ora_str, livello, pasto_val, session_data):
    if not all([data_str, ora_str, livello, pasto_val]):
        return "Compila tutti i campi prima di salvare.", "msg-box msg-errore"

    try:
        data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
        ora_obj = datetime.strptime(ora_str, "%H:%M").time()
    except ValueError:
        return "Errore di formato. Inserisci la data come AAAA-MM-GG e l'ora come HH:MM.", "msg-box msg-errore"

    pasto_enum = Pasto(pasto_val)
    codice_paz = session_data.get("codiceUtente")

    esito, alert, medico = glicemia_controller.inserisci_rilevazione(codice_paz, data_obj, ora_obj, float(livello), pasto_enum)

    messaggio = f"Rilevazione registrata correttamente. L'esito clinico è: {esito.upper()}."
    classe = "msg-box msg-alert" if alert else "msg-box msg-successo"

    if alert:
        messaggio += f" Il valore ha superato le soglie di sicurezza. È stato generato un ALERT per il tuo diabetologo (Codice Medico: {medico})."

    return messaggio, classe


@callback(
    Output("paz-farm-qty", "value"),
    Input("paz-farm-terapia-select", "value"),
    State("session-store", "data"),
)
def precompila_quantita(id_terapia, session_data):
    """Precompila la quantita' con la posologia prescritta per la terapia scelta."""
    if not id_terapia or not session_data:
        return None

    codice_paz = session_data.get("codiceUtente")
    terapia = _terapia_attiva_per_id(codice_paz, id_terapia)
    return terapia.quantita if terapia else None


@callback(
    Output("msg-farmaco", "children"),
    Output("msg-farmaco", "className"),
    Input("btn-salva-farm", "n_clicks"),
    State("paz-farm-terapia-select", "value"),
    State("paz-farm-data", "date"),
    State("paz-farm-ora", "value"),
    State("paz-farm-qty", "value"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def handle_salva_farmaco(n_clicks, id_terapia, data_str, ora_str, qty, session_data):
    if not all([id_terapia, data_str, ora_str, qty]):
        return "Seleziona la terapia e compila tutti i campi prima di registrare l'assunzione.", "msg-box msg-errore"

    try:
        data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
        ora_obj = datetime.strptime(ora_str, "%H:%M").time()
    except ValueError:
        return "Errore di formato. Inserisci la data come AAAA-MM-GG e l'ora come HH:MM.", "msg-box msg-errore"

    codice_paz = session_data.get("codiceUtente")

    # Il farmaco non e' piu' un campo libero: si ricava dalla terapia scelta
    # (oggetto TerapiaDiabetica), cosi' non e' possibile abbinare per errore
    # un farmaco che non corrisponde alla terapia selezionata (l'unico input
    # davvero libero e' la quantita').
    terapia = _terapia_attiva_per_id(codice_paz, id_terapia)
    if terapia is None:
        return "Terapia non trovata o non piu' attiva.", "msg-box msg-errore"

    successo, msg_controller = assunzione_controller.registra_assunzione(
        codice_paz, id_terapia, terapia.codiceFarmaco, data_obj, ora_obj, float(qty)
    )

    classe = "msg-box msg-successo" if successo else "msg-box msg-errore"
    return msg_controller, classe


@callback(
    Output("msg-segnalazione", "children"),
    Output("msg-segnalazione", "className"),
    Input("btn-salva-seg", "n_clicks"),
    State("paz-seg-evento", "value"),
    State("paz-seg-desc", "value"),
    State("paz-seg-inizio", "date"),
    State("paz-seg-fine", "date"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def handle_salva_segnalazione(n_clicks, evento_val, descrizione, inizio_str, fine_str, session_data):
    if not all([evento_val, descrizione, inizio_str, fine_str]):
        return "Compila tutti i campi del messaggio.", "msg-box msg-errore"

    try:
        data_inizio_obj = datetime.strptime(inizio_str, "%Y-%m-%d").date()
        data_fine_obj = datetime.strptime(fine_str, "%Y-%m-%d").date()
    except ValueError:
        return "Errore di formato date (usa AAAA-MM-GG).", "msg-box msg-errore"

    codice_paz = session_data.get("codiceUtente")
    evento_enum = TipoSegnalazionePaziente(evento_val)

    esito = segnalazione_controller.invia_segnalazione(codice_paz, descrizione, data_inizio_obj, data_fine_obj, evento_enum)

    return esito, "msg-box msg-successo"
