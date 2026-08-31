"""View — dashboard del paziente."""

from datetime import datetime, date
import urllib.parse
from dash import html, dcc, Input, Output, State, callback
import plotly.graph_objects as go

from controllers.glicemia_controller import GlicemiaController
from controllers.assunzione_farmaco_controller import AssunzioneFarmacoController
from controllers.farmaco_controller import FarmacoController
from controllers.segnalazione_controller import SegnalazioneController
from controllers.contatto_controller import ContattoController
from controllers.terapia_controller import TerapiaController
from models.my_enum.pasto import Pasto
from models.my_enum.tipo_segnalazione_paziente import TipoSegnalazionePaziente
from dash import ctx
from controllers.notifica_controller import NotificaController

notifica_controller = NotificaController()
segnalazione_controller = SegnalazioneController()
glicemia_controller = GlicemiaController()
assunzione_controller = AssunzioneFarmacoController()
farmaco_controller = FarmacoController()
contatto_controller = ContattoController()
terapia_controller = TerapiaController()


def _terapia_attiva_per_id(codice_paziente, id_terapia):
    terapie = terapia_controller.get_terapie_attive_paziente(codice_paziente)
    return next((t for t in terapie if t.id == id_terapia), None)


def _opzioni_terapie_paziente(codice_paziente):
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
    nome = session_data.get("nome", "Paziente")
    codice_paz = session_data.get("codiceUtente")

    email_diabetologo = contatto_controller.get_email_medico(codice_paz)
    oggetto_email = f"Richiesta consulenza - Paziente {nome}"

    gmail_url = (
        f"https://mail.google.com/mail/?view=cm&fs=1&{urllib.parse.urlencode({'to': email_diabetologo, 'su': oggetto_email})}"
        if email_diabetologo else None
    )

    return html.Div(className="dashboard-card", children=[

        html.Div([
            html.H2(f"Area Paziente — Benvenuto/a, {nome}", className="dashboard-header"),
            html.Button("Logout", id="btn-logout", className="btn-logout"),
        ]),

        html.P("Da questa dashboard puoi registrare i tuoi parametri clinici e visualizzare le tue terapie attive.", className="dashboard-subtitle"),
        html.Hr(),

        dcc.Tabs([

            dcc.Tab(label='Diario Glicemico', children=[
                html.Div(className="tab-content", children=[
                    html.H4("Nuova Rilevazione"),

                    html.Label("Data della misurazione", className="form-label"),
                    dcc.DatePickerSingle(
                        id="paz-glic-data",
                        display_format="YYYY-MM-DD",
                        max_date_allowed=date.today(),
                        className="form-datepicker",
                    ),

                    html.Label("Ora della misurazione", className="form-label"),
                    dcc.Input(id="paz-glic-ora", type="time", className="form-input"),

                    html.Label("Livello Glicemia (mg/dL)", className="form-label"),
                    dcc.Input(id="paz-glic-livello", type="number", className="form-input"),

                    html.Label("Momento del Pasto", className="form-label"),
                    dcc.Dropdown(id="paz-glic-pasto", options=_OPZIONI_MOMENTO_PASTO, className="form-dropdown"),

                    html.Button("Salva Glicemia", id="btn-salva-glic", n_clicks=0, className="btn btn-verde"),
                    html.Div(id="msg-glicemia", className="msg-box--empty"),
                ])
            ]),

            dcc.Tab(label='Informazioni Personali', children=[
                html.Div(className="tab-content", children=[

                    html.H4("Andamento Glicemico Personale"),

                    html.Div(
                        dcc.DatePickerRange(
                            id="paz-info-range",
                            start_date_placeholder_text="Inizio",
                            end_date_placeholder_text="Fine",
                            display_format="YYYY-MM-DD",
                            className="med-range-picker"
                        ),
                        className="med-range-container"
                    ),

                    dcc.Graph(id="paz-info-grafico"),

                    html.Hr(),

                    html.H4("Terapie Attive"),
                    html.Div(id="paz-info-terapie", className="card-list-container"),
                ])
            ]),

            dcc.Tab(label='Assunzione Terapie', children=[
                html.Div(className="tab-content", children=[
                    html.H4("Registra Farmaco"),

                    html.Label("Terapia prescritta", className="form-label"),
                    dcc.Dropdown(
                        id="paz-farm-terapia-select",
                        options=_opzioni_terapie_paziente(codice_paz),
                        className="form-dropdown",
                    ),

                    html.Label("Data assunzione", className="form-label"),
                    dcc.DatePickerSingle(
                        id="paz-farm-data",
                        display_format="YYYY-MM-DD",
                        max_date_allowed=date.today(),
                        className="form-datepicker",
                    ),

                    html.Label("Ora assunzione", className="form-label"),
                    dcc.Input(id="paz-farm-ora", type="time", className="form-input"),

                    html.Label("Quantità assunta", className="form-label"),
                    dcc.Input(id="paz-farm-qty", type="number", className="form-input"),

                    html.Button("Registra Assunzione", id="btn-salva-farm", n_clicks=0, className="btn btn-blu"),
                    html.Div(id="msg-farmaco", className="msg-box--empty"),
                ])
            ]),

            dcc.Tab(label='Invia Segnalazione', children=[
                html.Div(className="tab-content", children=[
                    html.H4("Nuova Segnalazione"),

                    html.Label("Tipo Evento", className="form-label"),
                    dcc.Dropdown(id="paz-seg-evento", options=_OPZIONI_TIPO_SEGNALAZIONE, className="form-dropdown"),

                    html.Label("Descrizione", className="form-label"),
                    dcc.Textarea(id="paz-seg-desc", className="form-textarea"),

                    html.Label("Data Inizio", className="form-label"),
                    dcc.DatePickerSingle(id="paz-seg-inizio", display_format="YYYY-MM-DD", className="form-datepicker"),

                    html.Label("Data Fine", className="form-label"),
                    dcc.DatePickerSingle(id="paz-seg-fine", display_format="YYYY-MM-DD", className="form-datepicker"),

                    html.Button("Invia al Medico", id="btn-salva-seg", n_clicks=0, className="btn btn-arancio"),
                    html.Div(id="msg-segnalazione", className="msg-box--empty"),
                ])
            ]),

            dcc.Tab(label='Centro Notifiche', children=[
                html.Div(className="tab-content", children=[
                    html.H4("Avvisi e Promemoria"),
                    html.P("Elenco delle notifiche di sistema relative alle tue terapie e al diario clinico.", className="dashboard-subtitle"),
                    
                    html.Button("Segna tutte come lette", id="btn-leggi-notifiche-paz", n_clicks=0, className="btn btn-blu btn-mb-lg"),
                    
                    html.Div(id="paz-notifiche-lista", className="card-list-container"),

                    dcc.Interval(id="paz-interval-notifiche", interval=30000, n_intervals=0)
                ])
            ]),

            dcc.Tab(label='Contatta il Medico', children=[
                html.Div(className="tab-content contatto-medico-box", children=[
                    html.H4("Hai bisogno di contattare il tuo Diabetologo?"),
                    html.P("Clicca per aprire Gmail e scrivere al tuo medico."),

                    html.A("✉️ Scrivi al Medico", href=gmail_url, target="_blank", className="btn-gmail")
                    if gmail_url else
                    html.P("Email del medico non disponibile.", className="contatto-medico-errore")
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
        return "Compila tutti i campi.", "msg-box msg-errore"

    try:
        data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
        ora_obj = datetime.strptime(ora_str, "%H:%M").time()
    except ValueError:
        return "Errore nel formato di data o ora.", "msg-box msg-errore"

    codice_paz = session_data.get("codiceUtente")
    pasto_enum = Pasto(pasto_val)

    successo, esito, alert, medico = glicemia_controller.inserisci_rilevazione(
        codice_paz, data_obj, ora_obj, float(livello), pasto_enum
    )

    if not successo:
        return esito, "msg-box msg-errore"

    msg = f"Rilevazione registrata. Esito: {esito.upper()}."
    classe = "msg-box msg-alert" if alert else "msg-box msg-successo"

    if alert:
        msg += f" È stato inviato un alert al diabetologo ({medico})."

    return msg, classe


@callback(
    Output("paz-farm-qty", "value"),
    Input("paz-farm-terapia-select", "value"),
    State("session-store", "data"),
)
def precompila_quantita(id_terapia, session_data):
    if not id_terapia:
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
        return "Compila tutti i campi.", "msg-box msg-errore"

    try:
        data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
        ora_obj = datetime.strptime(ora_str, "%H:%M").time()
    except ValueError:
        return "Errore nel formato di data o ora.", "msg-box msg-errore"

    codice_paz = session_data.get("codiceUtente")
    terapia = _terapia_attiva_per_id(codice_paz, id_terapia)

    if terapia is None:
        return "Terapia non trovata.", "msg-box msg-errore"

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
        return "Compila tutti i campi.", "msg-box msg-errore"

    try:
        data_inizio_obj = datetime.strptime(inizio_str, "%Y-%m-%d").date()
        data_fine_obj = datetime.strptime(fine_str, "%Y-%m-%d").date()
    except ValueError:
        return "Errore nel formato delle date.", "msg-box msg-errore"

    codice_paz = session_data.get("codiceUtente")
    evento_enum = TipoSegnalazionePaziente(evento_val)

    successo, esito = segnalazione_controller.invia_segnalazione(
        codice_paz, descrizione, data_inizio_obj, data_fine_obj, evento_enum
    )

    classe = "msg-box msg-successo" if successo else "msg-box msg-errore"
    return esito, classe

@callback(
    Output("paz-info-grafico", "figure"),
    Input("paz-info-range", "start_date"),
    Input("paz-info-range", "end_date"),
    State("session-store", "data")
)
def aggiorna_grafico_personale(Inizio, Fine, session_data):
    codice_paz = session_data.get("codiceUtente")
    storico = glicemia_controller.get_storico_paziente(codice_paz)

    fig = go.Figure()

    if not storico:
        fig.update_layout(
            title="Nessun dato glicemico disponibile.",
            xaxis={"visible": False},
            yaxis={"visible": False}
        )
        return fig

    storico_ordinato = sorted(storico, key=lambda r: r.as_datetime())

    if Inizio and Fine:
        start_dt = datetime.strptime(Inizio, "%Y-%m-%d")
        end_dt = datetime.strptime(Fine, "%Y-%m-%d")
        storico_ordinato = [
            r for r in storico_ordinato
            if start_dt <= r.as_datetime() <= end_dt
        ]

    if not storico_ordinato:
        fig.update_layout(
            title="Nessun dato nel periodo selezionato.",
            xaxis={"visible": False},
            yaxis={"visible": False}
        )
        return fig

    pre = [r for r in storico_ordinato if r.momentoPasto == Pasto.PRE_PASTO]
    post = [r for r in storico_ordinato if r.momentoPasto == Pasto.POST_PASTO]

    fig.add_trace(go.Scatter(
        x=[r.as_datetime() for r in pre],
        y=[r.livelloGlicemia for r in pre],
        mode='markers+lines',
        name='Pre-pasto',
        marker=dict(color='blue', size=8),
        line=dict(color='blue')
    ))

    fig.add_trace(go.Scatter(
        x=[r.as_datetime() for r in post],
        y=[r.livelloGlicemia for r in post],
        mode='markers+lines',
        name='Post-pasto',
        marker=dict(color='red', size=8),
        line=dict(color='red')
    ))

    fig.update_layout(
        title=f"Andamento glicemico personale ({codice_paz})",
        xaxis_title="Data e ora",
        yaxis_title="Livello (mg/dL)",
        hovermode="x unified",
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return fig

@callback(
    Output("paz-info-terapie", "children"),
    State("session-store", "data"),
    Input("paz-info-range", "start_date")  # trigger leggero
)
def carica_terapie_personali(session_data, _):
    codice_paz = session_data.get("codiceUtente")
    terapie = terapia_controller.get_terapie_attive_paziente(codice_paz)

    if not terapie:
        return html.P("Nessuna terapia attiva al momento.", className="card-list-empty")

    lista = []
    nome_medico = contatto_controller.get_nome_medico(codice_paz) or "Medico di riferimento"

    for t in terapie:
        farmaco = farmaco_controller.get_farmaco(t.codiceFarmaco)
        nome_farmaco = farmaco.nome if farmaco else t.codiceFarmaco

        card = html.Div(className="card-list-item", children=[
            html.Strong(f"Farmaco: {nome_farmaco}"),
            html.Span(
                f"Posologia: {t.assunzioneGiornaliera}x/giorno — {t.quantita}",
                className="card-list-meta"
            ),
            html.P(f"Indicazioni: {t.indicazioni}"),
            html.P(f"Periodo: {t.dataInizio} → {t.dataFine}"),
            html.P(f"Diabetologo: {nome_medico}"),
            html.P(f"Ultima modifica: {t.ultimaModifica}"),
        ])

        lista.append(card)

    return lista

@callback(
    Output("paz-notifiche-lista", "children"),
    Input("session-store", "data"),
    Input("btn-leggi-notifiche-paz", "n_clicks"),
    Input("paz-interval-notifiche", "n_intervals")
)
def carica_notifiche_paziente(session_data, n_clicks, n_intervals):
    if not session_data or session_data.get("ruolo") != "paziente":
        return []

    codice_paziente = session_data.get("codiceUtente")

    if ctx.triggered_id == "btn-leggi-notifiche-paz":
        notifiche_non_lette = notifica_controller.get_notifiche_utente(codice_paziente, solo_non_lette=True)
        for n in notifiche_non_lette:
            notifica_controller.segna_come_letta(n.id)

    notifiche = notifica_controller.get_notifiche_utente(codice_paziente, solo_non_lette=True)
    
    if not notifiche:
        return html.P("Nessun nuovo avviso o promemoria.", className="card-list-empty")
        
    lista_html = []
    for notifica in notifiche:
        card = html.Div(className="card-list-item msg-alert", children=[
            html.Strong(f"Tipo: {notifica.tipo.value}"),
            html.Span(f"Data: {notifica.data}", className="card-list-meta"),
            html.P(notifica.messaggio, className="card-list-message"),
        ])
        lista_html.append(card)
        
    return lista_html