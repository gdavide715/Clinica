"""View — dashboard del diabetologo.

Lo stile grafico e' definito in assets/style.css. Questo file si occupa
solo di struttura (layout) e comportamento (callback); l'accesso ai dati
passa sempre da un controller, mai da DataManager direttamente.
"""

from datetime import datetime, date
from dash import html, dcc, Input, Output, State, callback
import plotly.graph_objects as go
import pandas as pd

from controllers.terapia_controller import TerapiaController
from controllers.segnalazione_controller import SegnalazioneController
from controllers.glicemia_controller import GlicemiaController
from controllers.paziente_controller import PazienteController
from models.my_enum.pasto import Pasto

segnalazione_controller = SegnalazioneController()
terapia_controller = TerapiaController()
glicemia_controller = GlicemiaController()
paziente_controller = PazienteController()


def diabetologo_layout(session_data):
    """Genera il layout per l'utente loggato come diabetologo."""
    nome = session_data.get("nome", "Dottore")

    return html.Div(className="dashboard-card dashboard-card--wide", children=[

        html.Div([
            html.H2(f"Area Medico — Dott. {nome}", className="dashboard-header"),
            html.Button("Logout", id="btn-logout", className="btn-logout"),
        ]),
        html.P("Seleziona un paziente per monitorare la sua glicemia o prescrivere nuove terapie.", className="dashboard-subtitle"),
        html.Hr(),

        # Selezione Paziente
        html.Div(className="med-selezione-paziente", children=[
            html.Label("Paziente Selezionato:"),
            dcc.Dropdown(
                id="med-paziente-select",
                placeholder="Caricamento pazienti in corso...",
                className="med-paziente-dropdown",
            ),
            html.Div(id="med-load-trigger", className="hidden"),
        ]),

        html.Div(id="med-dashboard-content", className="hidden", children=[
            dcc.Tabs([
                # Grafico Glicemia
                dcc.Tab(label='Andamento Glicemico', children=[
                    html.Div(className="tab-content", children=[
                        html.H4("Storico Rilevazioni"),
                        dcc.Graph(id="med-glicemia-graph"),
                    ])
                ]),

                # Prescrizione Terapia
                dcc.Tab(label='Prescrivi Terapia', children=[
                    html.Div(className="tab-content", children=[
                        html.H4("Nuova Terapia Farmacologica"),

                        html.Label("Codice Farmaco", className="form-label"),
                        dcc.Input(id="med-ter-farmaco", type="text", placeholder="es. MET850", className="form-input"),

                        html.Label("Assunzioni Giornaliere", className="form-label"),
                        dcc.Input(id="med-ter-assunzioni", type="number", placeholder="es. 2", className="form-input"),

                        html.Label("Quantità per assunzione (mg/ml)", className="form-label"),
                        dcc.Input(id="med-ter-qty", type="number", placeholder="es. 1.5", className="form-input"),

                        html.Label("Indicazioni", className="form-label"),
                        dcc.Input(id="med-ter-ind", type="text", placeholder="es. Assumere durante i pasti principali", className="form-input"),

                        html.Label("Data Inizio", className="form-label"),
                        dcc.DatePickerSingle(
                            id="med-ter-inizio", placeholder="Seleziona la data",
                            display_format="YYYY-MM-DD", className="form-datepicker",
                        ),

                        html.Label("Data Fine", className="form-label"),
                        dcc.DatePickerSingle(
                            id="med-ter-fine", placeholder="Seleziona la data",
                            display_format="YYYY-MM-DD", className="form-datepicker",
                        ),

                        html.Button("Salva Prescrizione", id="btn-salva-terapia", n_clicks=0, className="btn btn-verde"),
                        html.Div(id="msg-terapia", className="msg-box--empty"),
                    ])
                ]),

                # Segnalazioni Paziente
                dcc.Tab(label='Segnalazioni Ricevute', children=[
                    html.Div(className="tab-content", children=[
                        html.H4("Storico Sintomi e Messaggi"),
                        html.Div(id="med-segnalazioni-list", className="card-list-container"),
                    ])
                ]),
            ])
        ])
    ])


@callback(
    Output("med-paziente-select", "options"),
    Input("med-load-trigger", "children"),
    State("session-store", "data"),
)
def carica_lista_pazienti(dummy, session_data):
    """Carica nel dropdown solo i pazienti assegnati al medico loggato."""
    if not session_data or session_data.get("ruolo") != "diabetologo":
        return []

    codice_medico = session_data.get("codiceUtente")
    pazienti_assegnati = paziente_controller.get_pazienti_assegnati(codice_medico)

    return [
        {'label': f"{p['nome']} {p['cognome']} ({p['codiceUtente']})", 'value': p['codiceUtente']}
        for p in pazienti_assegnati
    ]


@callback(
    Output("med-dashboard-content", "className"),
    Output("med-glicemia-graph", "figure"),
    Input("med-paziente-select", "value")
)
def aggiorna_dashboard_paziente(codice_paziente):
    """Mostra la dashboard e genera il grafico quando viene scelto un paziente."""
    if not codice_paziente:
        return "hidden", go.Figure()

    storico_paziente = glicemia_controller.get_storico_paziente(codice_paziente)

    fig = go.Figure()

    if not storico_paziente.empty:
        storico_paziente['datetime'] = pd.to_datetime(storico_paziente['data'].astype(str) + ' ' + storico_paziente['ora'].astype(str))
        storico_paziente = storico_paziente.sort_values(by='datetime')

        pre_pasto = storico_paziente[storico_paziente['momentoPasto'] == Pasto.PRE_PASTO.value]
        post_pasto = storico_paziente[storico_paziente['momentoPasto'] == Pasto.POST_PASTO.value]

        fig.add_trace(go.Scatter(
            x=pre_pasto['datetime'], y=pre_pasto['livelloGlicemia'],
            mode='lines+markers', name='Pre-Pasto', line=dict(color='blue')
        ))

        fig.add_trace(go.Scatter(
            x=post_pasto['datetime'], y=post_pasto['livelloGlicemia'],
            mode='lines+markers', name='Post-Pasto', line=dict(color='red')
        ))

        fig.update_layout(
            title=f"Andamento Glicemico (Paziente: {codice_paziente})",
            xaxis_title="Data e Ora",
            yaxis_title="Livello (mg/dL)",
            margin=dict(l=20, r=20, t=40, b=20),
            hovermode="x unified"
        )
    else:
        fig.update_layout(
            title="Nessun dato glicemico disponibile per questo paziente.",
            xaxis={"visible": False}, yaxis={"visible": False}
        )

    return "", fig


@callback(
    Output("msg-terapia", "children"),
    Output("msg-terapia", "className"),
    Input("btn-salva-terapia", "n_clicks"),
    State("med-paziente-select", "value"),
    State("med-ter-farmaco", "value"),
    State("med-ter-assunzioni", "value"),
    State("med-ter-qty", "value"),
    State("med-ter-ind", "value"),
    State("med-ter-inizio", "date"),
    State("med-ter-fine", "date"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def salva_prescrizione(n_clicks, paziente_cod, farmaco, assunzioni, qty, indicazioni, inizio_str, fine_str, session_data):
    """Gestisce il form di inserimento di una nuova terapia."""
    if not paziente_cod:
        return "Errore critico: nessun paziente selezionato.", "msg-box msg-errore"

    if not all([farmaco, assunzioni, qty, indicazioni, inizio_str, fine_str]):
        return "Compila tutti i campi prima di salvare la prescrizione.", "msg-box msg-errore"

    try:
        data_inizio_obj = datetime.strptime(inizio_str, "%Y-%m-%d").date()
        data_fine_obj = datetime.strptime(fine_str, "%Y-%m-%d").date()
    except ValueError:
        return "Errore di formato. Inserisci le date come AAAA-MM-GG.", "msg-box msg-errore"

    codice_medico = session_data.get("codiceUtente")

    esito = terapia_controller.crea_terapia(
        codice_paziente=paziente_cod,
        codice_diabetologo=codice_medico,
        codice_farmaco=farmaco,
        assunzione_giornaliera=int(assunzioni),
        quantita=float(qty),
        indicazioni=indicazioni,
        data_inizio=data_inizio_obj,
        data_fine=data_fine_obj
    )

    return esito, "msg-box msg-successo"


@callback(
    Output("med-segnalazioni-list", "children"),
    Input("med-paziente-select", "value"),
    prevent_initial_call=True
)
def carica_messaggi_paziente(codice_paziente):
    if not codice_paziente:
        return []

    messaggi = segnalazione_controller.leggi_segnalazioni(codice_paziente)

    if not messaggi:
        return html.P("Nessun messaggio o sintomo segnalato da questo paziente.", className="card-list-empty")

    lista_html = []
    for msg in messaggi:
        card = html.Div(className="card-list-item", children=[
            html.Strong(f"Oggetto: {msg.get('evento', 'Segnalazione')}"),
            html.Span(f"Periodo: dal {msg.get('dataInizio')} al {msg.get('dataFine')}", className="card-list-meta"),
            html.P(msg.get('descrizione', '')),
        ])
        lista_html.append(card)

    return lista_html