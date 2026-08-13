from datetime import datetime, date
from dash import html, dcc, Input, Output, State, callback
import plotly.graph_objects as go

from controllers.terapia_controller import TerapiaController
from controllers.segnalazione_controller import SegnalazioneController
from controllers.glicemia_controller import GlicemiaController
from controllers.paziente_controller import PazienteController
from models.my_enum.pasto import Pasto
from controllers.anamnesi_controller import AnamnesiController
from models.my_enum.tipo_condizione_clinica import TipoCondizioneClinica

anamnesi_controller = AnamnesiController()
segnalazione_controller = SegnalazioneController()
terapia_controller = TerapiaController()
glicemia_controller = GlicemiaController()
paziente_controller = PazienteController()


def diabetologo_layout(session_data):
    nome = session_data.get("nome", "Dottore")

    return html.Div(className="dashboard-card dashboard-card--wide", children=[

        html.Div([
            html.H2(f"Area Medico — Dott. {nome}", className="dashboard-header"),
            html.Button("Logout", id="btn-logout", className="btn-logout"),
        ]),
        html.P("Seleziona un paziente per monitorare la sua glicemia o prescrivere nuove terapie.", className="dashboard-subtitle"),
        html.Hr(),

        html.Div(className="med-selezione-paziente", children=[
            html.Label("Paziente selezionato:"),
            dcc.Dropdown(
                id="med-paziente-select",
                placeholder="Caricamento pazienti in corso...",
                className="med-paziente-dropdown",
            ),
            html.Div(id="med-load-trigger", className="hidden"),
        ]),

        html.Div(id="med-dashboard-content", className="hidden", children=[
            dcc.Tabs([

                dcc.Tab(label='Andamento glicemico', children=[
                    html.Div(className="tab-content", children=[
                        html.H4("Storico rilevazioni"),

                        html.Div(
                            dcc.DatePickerRange(
                                id="med-glicemia-range",
                                start_date_placeholder_text="Inizio",
                                end_date_placeholder_text="Fine",
                                display_format="YYYY-MM-DD",
                                className="med-range-picker"
                            ),
                            className="med-range-container"
                        ),

                        dcc.Graph(id="med-glicemia-graph"),
                    ])
                ]),

                dcc.Tab(label='Prescrivi terapia', children=[
                    html.Div(className="tab-content", children=[
                        html.H4("Nuova terapia farmacologica"),

                        html.Label("Codice farmaco", className="form-label"),
                        dcc.Input(id="med-ter-farmaco", type="text", className="form-input"),

                        html.Label("Assunzioni giornaliere", className="form-label"),
                        dcc.Input(id="med-ter-assunzioni", type="number", className="form-input"),

                        html.Label("Quantità per assunzione (mg/ml)", className="form-label"),
                        dcc.Input(id="med-ter-qty", type="number", className="form-input"),

                        html.Label("Indicazioni", className="form-label"),
                        dcc.Input(id="med-ter-ind", type="text", className="form-input"),

                        html.Label("Data inizio", className="form-label"),
                        dcc.DatePickerSingle(
                            id="med-ter-inizio",
                            display_format="YYYY-MM-DD",
                            className="form-datepicker",
                        ),

                        html.Label("Data fine", className="form-label"),
                        dcc.DatePickerSingle(
                            id="med-ter-fine",
                            display_format="YYYY-MM-DD",
                            className="form-datepicker",
                        ),

                        html.Button("Salva prescrizione", id="btn-salva-terapia", n_clicks=0, className="btn btn-verde"),
                        html.Div(id="msg-terapia", className="msg-box--empty"),
                    ])
                ]),

                dcc.Tab(label='Segnalazioni ricevute', children=[
                    html.Div(className="tab-content", children=[
                        html.H4("Storico sintomi e messaggi"),
                        html.Div(id="med-segnalazioni-list", className="card-list-container"),
                    ])
                ]),

                dcc.Tab(label='Anamnesi clinica', children=[
                    html.Div(className="tab-content", children=[
                        html.H4("Gestione fascicolo clinico"),

                        html.Label("Patologie pregresse", className="form-label"),
                        dcc.Textarea(id="med-anam-patologie", className="form-textarea"),

                        html.Label("Comorbidità", className="form-label"),
                        dcc.Textarea(id="med-anam-comorbidita", className="form-textarea"),

                        html.Label("Fattori di rischio", className="form-label"),
                        dcc.Textarea(id="med-anam-rischio", className="form-textarea"),

                        html.Button("Salva anamnesi", id="btn-salva-anamnesi", n_clicks=0, className="btn btn-arancio"),
                        html.Div(id="msg-anamnesi", className="msg-box--empty"),
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
    if not session_data or session_data.get("ruolo") != "diabetologo":
        return []

    codice_medico = session_data.get("codiceUtente")
    pazienti_assegnati = paziente_controller.get_pazienti_assegnati(codice_medico)

    return [
        {'label': f"{p.nome} {p.cognome} ({p.codiceUtente})", 'value': p.codiceUtente}
        for p in pazienti_assegnati
    ]


def filtra_intervallo(storico, Inizio, Fine):
    if not Inizio or not Fine:
        return storico

    start_dt = datetime.strptime(Inizio, "%Y-%m-%d")
    end_dt = datetime.strptime(Fine, "%Y-%m-%d")

    return [r for r in storico if start_dt <= r.as_datetime() <= end_dt]


@callback(
    Output("med-dashboard-content", "className"),
    Output("med-glicemia-graph", "figure"),
    Input("med-paziente-select", "value"),
    Input("med-glicemia-range", "start_date"),
    Input("med-glicemia-range", "end_date")
)
def aggiorna_dashboard_paziente(codice_paziente, Inizio, Fine):
    if not codice_paziente:
        return "hidden", go.Figure()

    storico_paziente = glicemia_controller.get_storico_paziente(codice_paziente)
    fig = go.Figure()

    if storico_paziente:
        storico_ordinato = sorted(storico_paziente, key=lambda r: r.as_datetime())
        storico_filtrato = filtra_intervallo(storico_ordinato, Inizio, Fine)

        pre_pasto = [r for r in storico_filtrato if r.momentoPasto == Pasto.PRE_PASTO]
        post_pasto = [r for r in storico_filtrato if r.momentoPasto == Pasto.POST_PASTO]

        # Range glicemico consigliato (esempio clinico)
        range_min = 70
        range_max = 180

        fig.add_shape(
            type="rect",
            xref="paper", yref="y",
            x0=0, x1=1,
            y0=range_min, y1=range_max,
            fillcolor="rgba(0, 200, 0, 0.10)",
            line=dict(width=0),
            layer="below"
        )

        # Punti fuori range evidenziati
        def colore_punto(valore):
            return "red" if valore > range_max or valore < range_min else "blue"

        fig.add_trace(go.Scatter(
            x=[r.as_datetime() for r in pre_pasto],
            y=[r.livelloGlicemia for r in pre_pasto],
            mode='markers+lines',
            name='Pre-pasto',
            marker=dict(color=[colore_punto(r.livelloGlicemia) for r in pre_pasto], size=8),
            line=dict(color='blue')
        ))

        fig.add_trace(go.Scatter(
            x=[r.as_datetime() for r in post_pasto],
            y=[r.livelloGlicemia for r in post_pasto],
            mode='markers+lines',
            name='Post-pasto',
            marker=dict(color='red', size=8),
            line=dict(color='red')
        ))

        # Linea di trend (media mobile)
        if len(storico_filtrato) >= 3:
            valori = [r.livelloGlicemia for r in storico_filtrato]
            date_x = [r.as_datetime() for r in storico_filtrato]
            media_mobile = []
            for i in range(len(valori)):
                start = max(0, i - 2)
                media_mobile.append(sum(valori[start:i+1]) / (i - start + 1))

            fig.add_trace(go.Scatter(
                x=date_x,
                y=media_mobile,
                mode='lines',
                name='Trend (media mobile)',
                line=dict(color='orange', width=3, dash='dash')
            ))

        fig.update_layout(
            title=f"Andamento glicemico (Paziente: {codice_paziente})",
            xaxis_title="Data e ora",
            yaxis_title="Livello (mg/dL)",
            margin=dict(l=20, r=20, t=40, b=20),
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
    else:
        fig.update_layout(
            title="Nessun dato glicemico disponibile per questo paziente.",
            xaxis={"visible": False}, yaxis={"visible": False}
        )

    return "", fig


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
            html.Strong(f"Oggetto: {msg.evento.value}"),
            html.Span(f"Periodo: dal {msg.dataInizio} al {msg.dataFine}", className="card-list-meta"),
            html.P(msg.descrizione),
        ])
        lista_html.append(card)

    return lista_html


@callback(
    Output("med-anam-patologie", "value"),
    Output("med-anam-comorbidita", "value"),
    Output("med-anam-rischio", "value"),
    Input("med-paziente-select", "value"),
    prevent_initial_call=True
)
def carica_anamnesi_paziente(codice_paziente):
    if not codice_paziente:
        return "", "", ""

    dati = anamnesi_controller.ottieni_anamnesi(codice_paziente)
    return (
        dati.get(TipoCondizioneClinica.PREGRESSA_PATOLOGIA.value, ""),
        dati.get(TipoCondizioneClinica.COMORBIDITA.value, ""),
        dati.get(TipoCondizioneClinica.FATTORE_RISCHIO.value, "")
    )


@callback(
    Output("msg-anamnesi", "children"),
    Output("msg-anamnesi", "className"),
    Input("btn-salva-anamnesi", "n_clicks"),
    State("med-paziente-select", "value"),
    State("med-anam-patologie", "value"),
    State("med-anam-comorbidita", "value"),
    State("med-anam-rischio", "value"),
    prevent_initial_call=True
)
def salva_anamnesi(n_clicks, codice_paziente, patologie, comorbidita, rischio):
    if not codice_paziente:
        return "Attenzione: seleziona un paziente prima di salvare.", "msg-box msg-errore"

    esito = anamnesi_controller.aggiorna_anamnesi(
        codice_paziente,
        patologie or "",
        comorbidita or "",
        rischio or ""
    )

    return esito, "msg-box msg-successo"
