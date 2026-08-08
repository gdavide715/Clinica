"""View — dashboard del diabetologo.
"""

from datetime import datetime
from dash import html, dcc, Input, Output, State, callback, no_update
import plotly.graph_objects as go
import pandas as pd

from config import CSV_PATHS
from models.data_manager import DataManager
from controllers.terapia_controller import TerapiaController
from controllers.segnalazione_controller import SegnalazioneController
from controllers.email_controller import EmailController

email_controller = EmailController()
segnalazione_controller = SegnalazioneController()
terapia_controller = TerapiaController()
dm_pazienti = DataManager(CSV_PATHS["pazienti"])
dm_rilevazioni = DataManager(CSV_PATHS["rilevazioni_glicemiche"])

def diabetologo_layout(session_data):
    """Genera il layout per l'utente loggato come diabetologo."""
    nome = session_data.get("nome", "Dottore")
    
    return html.Div(style={'maxWidth': '1000px', 'margin': '40px auto', 'padding': '20px', 'backgroundColor': 'white', 'boxShadow': '0 2px 8px rgba(0,0,0,0.1)', 'borderRadius': '8px'}, children=[
        
        html.Div([
            html.H2(f"Area Medico — Dott. {nome}", style={'display': 'inline-block', 'color': '#333'}),
            html.Button("Logout", id="btn-logout", style={'float': 'right', 'marginTop': '20px', 'padding': '8px 16px', 'backgroundColor': '#f44336', 'color': 'white', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer'})
        ]),
        html.P("Seleziona un paziente per monitorare la sua glicemia o prescrivere nuove terapie.", style={'color': '#666'}),
        html.Hr(),

        # Selezione Paziente
        html.Div(style={'marginBottom': '30px', 'padding': '15px', 'backgroundColor': '#f4f6f8', 'borderRadius': '5px'}, children=[
            html.Label("Paziente Selezionato:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
            dcc.Dropdown(
                id="med-paziente-select",
                placeholder="Caricamento pazienti in corso...",
                style={'width': '300px', 'display': 'inline-block', 'verticalAlign': 'middle'}
            ),
            html.Div(id="med-load-trigger", style={'display': 'none'})
        ]),

        html.Div(id="med-dashboard-content", style={'display': 'none'}, children=[
            dcc.Tabs([
                # Grafico Glicemia
                dcc.Tab(label='Andamento Glicemico', children=[
                    html.Div(style={'padding': '20px', 'border': '1px solid #d6d6d6', 'borderTop': 'none', 'backgroundColor': '#fafafa'}, children=[
                        html.H4("Storico Rilevazioni", style={'marginTop': '0'}),
                        dcc.Graph(id="med-glicemia-graph")
                    ])
                ]),

                # Prescrizione Terapia
                dcc.Tab(label='Prescrivi Terapia', children=[
                    html.Div(style={'padding': '20px', 'border': '1px solid #d6d6d6', 'borderTop': 'none', 'backgroundColor': '#fafafa'}, children=[
                        html.H4("Nuova Terapia Farmacologica", style={'marginTop': '0'}),
                        
                        html.Label("Codice Farmaco", style={'display': 'block', 'fontWeight': 'bold', 'marginBottom': '5px'}),
                        dcc.Input(id="med-ter-farmaco", type="text", placeholder="es. MET850", style={'width': '100%', 'padding': '8px', 'marginBottom': '15px', 'boxSizing': 'border-box'}),
                        
                        html.Label("Assunzioni Giornaliere", style={'display': 'block', 'fontWeight': 'bold', 'marginBottom': '5px'}),
                        dcc.Input(id="med-ter-assunzioni", type="number", placeholder="es. 2", style={'width': '100%', 'padding': '8px', 'marginBottom': '15px', 'boxSizing': 'border-box'}),
                        
                        html.Label("Quantità per assunzione (mg/ml)", style={'display': 'block', 'fontWeight': 'bold', 'marginBottom': '5px'}),
                        dcc.Input(id="med-ter-qty", type="number", placeholder="es. 1.5", style={'width': '100%', 'padding': '8px', 'marginBottom': '15px', 'boxSizing': 'border-box'}),
                        
                        html.Label("Indicazioni", style={'display': 'block', 'fontWeight': 'bold', 'marginBottom': '5px'}),
                        dcc.Input(id="med-ter-ind", type="text", placeholder="es. Assumere durante i pasti principali", style={'width': '100%', 'padding': '8px', 'marginBottom': '15px', 'boxSizing': 'border-box'}),
                        
                        html.Label("Data Inizio", style={'display': 'block', 'fontWeight': 'bold', 'marginBottom': '5px'}),
                        dcc.Input(id="med-ter-inizio", type="text", placeholder="AAAA-MM-GG", style={'width': '48%', 'padding': '8px', 'marginBottom': '15px', 'marginRight': '4%', 'boxSizing': 'border-box'}),
                        
                        html.Label("Data Fine", style={'display': 'block', 'fontWeight': 'bold', 'marginBottom': '5px', 'display': 'inline-block'}),
                        dcc.Input(id="med-ter-fine", type="text", placeholder="AAAA-MM-GG", style={'width': '48%', 'padding': '8px', 'marginBottom': '20px', 'boxSizing': 'border-box'}),
                        
                        html.Button("Salva Prescrizione", id="btn-salva-terapia", n_clicks=0, style={'padding': '10px 20px', 'backgroundColor': '#4CAF50', 'color': 'white', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer', 'fontSize': '16px', 'display': 'block'}),
                        html.Div(id="msg-terapia", style={'marginTop': '15px'})
                    ])
                ]),

                # Segnalazioni Paziente
                dcc.Tab(label='Segnalazioni Ricevute', children=[
                    html.Div(style={'padding': '20px', 'border': '1px solid #d6d6d6', 'borderTop': 'none', 'backgroundColor': '#fafafa'}, children=[
                        html.H4("Storico Sintomi e Messaggi", style={'marginTop': '0'}),
                        html.Div(id="med-segnalazioni-list", style={'maxHeight': '300px', 'overflowY': 'auto'})
                    ])
                ]),

                # Casella di Posta
                dcc.Tab(label='Casella di Posta', children=[
                    html.Div(style={'padding': '20px', 'border': '1px solid #d6d6d6', 'borderTop': 'none', 'backgroundColor': '#fafafa'}, children=[
                        html.H4("Email ricevute dai tuoi pazienti", style={'marginTop': '0'}),
                        html.Button("Aggiorna Posta", id="btn-refresh-email", n_clicks=0, style={'marginBottom': '15px', 'padding': '6px 12px'}),
                        html.Div(id="med-email-list", style={'maxHeight': '400px', 'overflowY': 'auto'})
                    ])
                ])
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
    df_pazienti = dm_pazienti.read_all()
    
    pazienti_assegnati = df_pazienti[df_pazienti["codiceMedicoRiferimento"] == codice_medico]
    
    options = []
    for _, row in pazienti_assegnati.iterrows():
        label = f"{row['nome']} {row['cognome']} ({row['codiceUtente']})"
        options.append({'label': label, 'value': row['codiceUtente']})
        
    return options

@callback(
    Output("med-dashboard-content", "style"),
    Output("med-glicemia-graph", "figure"),
    Input("med-paziente-select", "value")
)
def aggiorna_dashboard_paziente(codice_paziente):
    """Mostra la dashboard e genera il grafico quando viene scelto un paziente."""
    if not codice_paziente:
        return {'display': 'none'}, go.Figure()
        
    df_ril = dm_rilevazioni.read_all()
    storico_paziente = df_ril[df_ril["codicePaziente"] == codice_paziente].copy()
    
    fig = go.Figure()
    
    if not storico_paziente.empty:
        storico_paziente['datetime'] = pd.to_datetime(storico_paziente['data'].astype(str) + ' ' + storico_paziente['ora'].astype(str))
        storico_paziente = storico_paziente.sort_values(by='datetime')
        
        pre_pasto = storico_paziente[storico_paziente['momentoPasto'] == 'pre_pasto']
        post_pasto = storico_paziente[storico_paziente['momentoPasto'] == 'post_pasto']
        
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

    return {'display': 'block'}, fig

@callback(
    Output("msg-terapia", "children"),
    Output("msg-terapia", "style"),
    Input("btn-salva-terapia", "n_clicks"),
    State("med-paziente-select", "value"),
    State("med-ter-farmaco", "value"),
    State("med-ter-assunzioni", "value"),
    State("med-ter-qty", "value"),
    State("med-ter-ind", "value"),
    State("med-ter-inizio", "value"),
    State("med-ter-fine", "value"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def salva_prescrizione(n_clicks, paziente_cod, farmaco, assunzioni, qty, indicazioni, inizio_str, fine_str, session_data):
    """Gestisce il form di inserimento di una nuova terapia."""
    if not paziente_cod:
        return "Errore critico: nessun paziente selezionato.", {'color': '#d32f2f', 'fontWeight': 'bold'}
        
    if not all([farmaco, assunzioni, qty, indicazioni, inizio_str, fine_str]):
        return "Compila tutti i campi prima di salvare la prescrizione.", {'color': '#d32f2f', 'fontWeight': 'bold'}
        
    try:
        data_inizio_obj = datetime.strptime(inizio_str, "%Y-%m-%d").date()
        data_fine_obj = datetime.strptime(fine_str, "%Y-%m-%d").date()
    except ValueError:
        return "Errore di formato. Inserisci le date come AAAA-MM-GG.", {'color': '#d32f2f', 'fontWeight': 'bold'}
        
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
    
    stile = {'color': '#2e7d32', 'fontWeight': 'bold', 'padding': '10px', 'backgroundColor': '#e8f5e9', 'borderRadius': '4px', 'border': '1px solid'}
    
    return esito, stile

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
        return html.P("Nessun messaggio o sintomo segnalato da questo paziente.", style={'color': '#666', 'fontStyle': 'italic'})
        
    lista_html = []
    for msg in messaggi:
        card = html.Div(style={'border': '1px solid #ccc', 'padding': '10px', 'marginBottom': '10px', 'borderRadius': '5px', 'backgroundColor': '#fff'}, children=[
            html.Strong(f"Oggetto: {msg.get('evento', 'Segnalazione')}", style={'display': 'block', 'color': '#1976d2'}),
            html.Span(f"Periodo: dal {msg.get('dataInizio')} al {msg.get('dataFine')}", style={'fontSize': '12px', 'color': '#888', 'display': 'block', 'marginBottom': '5px'}),
            html.P(msg.get('descrizione', ''), style={'margin': '0'})
        ])
        lista_html.append(card)
        
    return lista_html

@callback(
    Output("med-email-list", "children"),
    Input("btn-refresh-email", "n_clicks"),
    Input("med-load-trigger", "children"), # Si aggiorna all'apertura della pagina
    State("session-store", "data"),
)
def carica_casella_posta(n_clicks, dummy, session_data):
    if not session_data or session_data.get("ruolo") != "diabetologo":
        return []
        
    codice_medico = session_data.get("codiceUtente")
    email_ricevute = email_controller.leggi_email_medico(codice_medico)
    
    if not email_ricevute:
        return html.P("Nessuna email ricevuta al momento.", style={'color': '#666', 'fontStyle': 'italic'})
        
    lista_html = []
    # Mostriamo le più recenti per prime
    for msg in reversed(email_ricevute):
        card = html.Div(style={'border': '1px solid #9e9e9e', 'padding': '15px', 'marginBottom': '15px', 'borderRadius': '5px', 'backgroundColor': '#f5f5f5'}, children=[
            html.Strong(f"Oggetto: {msg.get('oggetto', '')}", style={'display': 'block', 'fontSize': '16px', 'marginBottom': '5px'}),
            html.Span(f"Da: Paziente [{msg.get('codicePaziente')}] - Ricevuta il: {msg.get('data_invio')}", style={'fontSize': '12px', 'color': '#555', 'display': 'block', 'marginBottom': '10px'}),
            html.P(msg.get('testo', ''), style={'margin': '0', 'whiteSpace': 'pre-wrap'})
        ])
        lista_html.append(card)
        
    return lista_html