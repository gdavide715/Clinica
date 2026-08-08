"""View — dashboard del paziente.
"""

from datetime import datetime
from dash import html, dcc, Input, Output, State, callback
from controllers.glicemia_controller import GlicemiaController
from controllers.farmaco_controller import FarmacoController
from models.my_enum.pasto import Pasto
from controllers.segnalazione_controller import SegnalazioneController
from models.my_enum.tipo_segnalazione_paziente import TipoSegnalazionePaziente
from controllers.email_controller import EmailController

email_controller = EmailController()
segnalazione_controller = SegnalazioneController()
glicemia_controller = GlicemiaController()
farmaco_controller = FarmacoController()

def paziente_layout(session_data):
    """Genera il layout per l'utente loggato come paziente."""
    nome = session_data.get("nome", "Paziente")
    
    return html.Div(style={'maxWidth': '800px', 'margin': '40px auto', 'padding': '20px', 'backgroundColor': 'white', 'boxShadow': '0 2px 8px rgba(0,0,0,0.1)', 'borderRadius': '8px'}, children=[
        html.Div([
            html.H2(f"Area Paziente — Benvenuto/a, {nome}", style={'display': 'inline-block', 'color': '#333'}),
            html.Button("Logout", id="btn-logout", style={'float': 'right', 'marginTop': '20px', 'padding': '8px 16px', 'backgroundColor': '#f44336', 'color': 'white', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer'})
        ]),
        html.P("Da questa dashboard puoi registrare i tuoi parametri clinici e l'assunzione delle terapie prescritte dal tuo diabetologo.", style={'color': '#666'}),
        html.Hr(),

        dcc.Tabs([
            # Rilevazione Glicemica
            dcc.Tab(label='Diario Glicemico', children=[
                html.Div(style={'padding': '20px', 'border': '1px solid #d6d6d6', 'borderTop': 'none', 'backgroundColor': '#fafafa'}, children=[
                    html.H4("Nuova Rilevazione", style={'marginTop': '0'}),
                    
                    html.Label("Data della misurazione", style={'display': 'block', 'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Input(id="paz-glic-data", type="text", placeholder="Formato: AAAA-MM-GG (es. 2026-08-08)", style={'width': '100%', 'padding': '8px', 'marginBottom': '15px', 'boxSizing': 'border-box'}),
                    
                    html.Label("Ora della misurazione", style={'display': 'block', 'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Input(id="paz-glic-ora", type="text", placeholder="Formato: HH:MM (es. 08:30)", style={'width': '100%', 'padding': '8px', 'marginBottom': '15px', 'boxSizing': 'border-box'}),
                    
                    html.Label("Livello Glicemia (mg/dL)", style={'display': 'block', 'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Input(id="paz-glic-livello", type="number", placeholder="es. 110", style={'width': '100%', 'padding': '8px', 'marginBottom': '15px', 'boxSizing': 'border-box'}),
                    
                    html.Label("Momento del Pasto", style={'display': 'block', 'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id="paz-glic-pasto",
                        options=[
                            {'label': 'Prima dei pasti (Pre-pasto)', 'value': Pasto.PRE_PASTO.value},
                            {'label': 'Dopo i pasti (Post-pasto)', 'value': Pasto.POST_PASTO.value}
                        ],
                        placeholder="Seleziona...",
                        style={'marginBottom': '20px'}
                    ),
                    
                    html.Button("Salva Glicemia", id="btn-salva-glic", n_clicks=0, style={'padding': '10px 20px', 'backgroundColor': '#4CAF50', 'color': 'white', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer', 'fontSize': '16px'}),
                    html.Div(id="msg-glicemia", style={'marginTop': '15px'})
                ])
            ]),

            # Assunzione Farmaci
            dcc.Tab(label='Assunzione Terapie', children=[
                html.Div(style={'padding': '20px', 'border': '1px solid #d6d6d6', 'borderTop': 'none', 'backgroundColor': '#fafafa'}, children=[
                    html.H4("Registra Farmaco", style={'marginTop': '0'}),
                    
                    html.Label("ID della Terapia", style={'display': 'block', 'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Input(id="paz-farm-idter", type="number", placeholder="es. 1", style={'width': '100%', 'padding': '8px', 'marginBottom': '15px', 'boxSizing': 'border-box'}),
                    
                    html.Label("Codice Farmaco", style={'display': 'block', 'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Input(id="paz-farm-cod", type="text", placeholder="es. MET850", style={'width': '100%', 'padding': '8px', 'marginBottom': '15px', 'boxSizing': 'border-box'}),
                    
                    html.Label("Data assunzione", style={'display': 'block', 'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Input(id="paz-farm-data", type="text", placeholder="Formato: AAAA-MM-GG", style={'width': '100%', 'padding': '8px', 'marginBottom': '15px', 'boxSizing': 'border-box'}),
                    
                    html.Label("Ora assunzione", style={'display': 'block', 'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Input(id="paz-farm-ora", type="text", placeholder="Formato: HH:MM", style={'width': '100%', 'padding': '8px', 'marginBottom': '15px', 'boxSizing': 'border-box'}),
                    
                    html.Label("Quantità assunta", style={'display': 'block', 'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Input(id="paz-farm-qty", type="number", placeholder="es. 1", style={'width': '100%', 'padding': '8px', 'marginBottom': '20px', 'boxSizing': 'border-box'}),
                    
                    html.Button("Registra Assunzione", id="btn-salva-farm", n_clicks=0, style={'padding': '10px 20px', 'backgroundColor': '#2196F3', 'color': 'white', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer', 'fontSize': '16px'}),
                    html.Div(id="msg-farmaco", style={'marginTop': '15px'})
                ])
            ]),

            # Invia Segnalazione
            dcc.Tab(label='Invia Segnalazione', children=[
                html.Div(style={'padding': '20px', 'border': '1px solid #d6d6d6', 'borderTop': 'none', 'backgroundColor': '#fafafa'}, children=[
                    html.H4("Nuova Segnalazione (Sintomi o Patologie)", style={'marginTop': '0'}),
                    
                    html.Label("Tipo Evento", style={'display': 'block', 'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id="paz-seg-evento",
                        options=[
                            {'label': 'Sintomo', 'value': 'Sintomo'},
                            {'label': 'Patologia Concomitante', 'value': 'PatologiaConcomitante'},
                            {'label': 'Terapia Concomitante', 'value': 'TerapiaConcomitante'}
                        ],
                        placeholder="Seleziona...", style={'marginBottom': '15px'}
                    ),
                    
                    html.Label("Descrizione", style={'display': 'block', 'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Textarea(id="paz-seg-desc", style={'width': '100%', 'height': '80px', 'padding': '8px', 'marginBottom': '15px', 'boxSizing': 'border-box'}),
                    
                    html.Label("Data Inizio", style={'display': 'inline-block', 'fontWeight': 'bold', 'marginBottom': '5px', 'marginRight': '10px'}),
                    dcc.Input(id="paz-seg-inizio", type="text", placeholder="AAAA-MM-GG", style={'width': '40%', 'padding': '8px', 'marginBottom': '15px', 'marginRight': '5%'}),
                    
                    html.Label("Data Fine", style={'display': 'inline-block', 'fontWeight': 'bold', 'marginBottom': '5px', 'marginRight': '10px'}),
                    dcc.Input(id="paz-seg-fine", type="text", placeholder="AAAA-MM-GG", style={'width': '40%', 'padding': '8px', 'marginBottom': '20px'}),
                    
                    html.Button("Invia al Medico", id="btn-salva-seg", n_clicks=0, style={'padding': '10px 20px', 'backgroundColor': '#FF9800', 'color': 'white', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer', 'fontSize': '16px', 'display': 'block'}),
                    html.Div(id="msg-segnalazione", style={'marginTop': '15px'})
                ])
            ]),

            # Contatta il Medico
            dcc.Tab(label='Contatta il Medico', children=[
                html.Div(style={'padding': '20px', 'border': '1px solid #d6d6d6', 'borderTop': 'none', 'backgroundColor': '#fafafa'}, children=[
                    html.H4("Invia un'email al tuo Diabetologo", style={'marginTop': '0'}),
                    
                    html.Label("Oggetto", style={'display': 'block', 'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Input(id="paz-email-ogg", type="text", placeholder="Es. Richiesta informazioni su dieta", style={'width': '100%', 'padding': '8px', 'marginBottom': '15px', 'boxSizing': 'border-box'}),
                    
                    html.Label("Testo del messaggio", style={'display': 'block', 'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Textarea(id="paz-email-testo", placeholder="Scrivi qui il tuo messaggio...", style={'width': '100%', 'height': '120px', 'padding': '8px', 'marginBottom': '20px', 'boxSizing': 'border-box'}),
                    
                    html.Button("Invia Email", id="btn-invia-email", n_clicks=0, style={'padding': '10px 20px', 'backgroundColor': '#673AB7', 'color': 'white', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer', 'fontSize': '16px', 'display': 'block'}),
                    html.Div(id="msg-email-esito", style={'marginTop': '15px'})
                ])
            ])
        ])
    ])

@callback(
    Output("msg-glicemia", "children"),
    Output("msg-glicemia", "style"),
    Input("btn-salva-glic", "n_clicks"),
    State("paz-glic-data", "value"),
    State("paz-glic-ora", "value"),
    State("paz-glic-livello", "value"),
    State("paz-glic-pasto", "value"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def handle_salva_glicemia(n_clicks, data_str, ora_str, livello, pasto_val, session_data):
    if not all([data_str, ora_str, livello, pasto_val]):
        return "Compila tutti i campi prima di salvare.", {'color': '#d32f2f', 'fontWeight': 'bold'}
    
    try:
        data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
        ora_obj = datetime.strptime(ora_str, "%H:%M").time()
    except ValueError:
        return "Errore di formato. Inserisci la data come AAAA-MM-GG e l'ora come HH:MM.", {'color': '#d32f2f', 'fontWeight': 'bold'}
        
    pasto_enum = Pasto(pasto_val)
    codice_paz = session_data.get("codiceUtente")
    
    esito, alert, medico = glicemia_controller.inserisci_rilevazione(codice_paz, data_obj, ora_obj, float(livello), pasto_enum)
    
    messaggio = f"Rilevazione registrata correttamente. L'esito clinico è: {esito.upper()}."
    stile = {'color': '#e65100' if alert else '#2e7d32', 'fontWeight': 'bold', 'padding': '10px', 'backgroundColor': '#fff3e0' if alert else '#e8f5e9', 'borderRadius': '4px', 'border': '1px solid'}
    
    if alert:
        messaggio += f" Il valore ha superato le soglie di sicurezza. È stato generato un ALERT per il tuo diabetologo (Codice Medico: {medico})."
        
    return messaggio, stile


@callback(
    Output("msg-farmaco", "children"),
    Output("msg-farmaco", "style"),
    Input("btn-salva-farm", "n_clicks"),
    State("paz-farm-idter", "value"),
    State("paz-farm-cod", "value"),
    State("paz-farm-data", "value"),
    State("paz-farm-ora", "value"),
    State("paz-farm-qty", "value"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def handle_salva_farmaco(n_clicks, id_ter, cod_farmaco, data_str, ora_str, qty, session_data):
    if not all([id_ter, cod_farmaco, data_str, ora_str, qty]):
        return "Compila tutti i campi prima di registrare l'assunzione.", {'color': '#d32f2f', 'fontWeight': 'bold'}
        
    try:
        data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
        ora_obj = datetime.strptime(ora_str, "%H:%M").time()
    except ValueError:
        return "Errore di formato. Inserisci la data come AAAA-MM-GG e l'ora come HH:MM.", {'color': '#d32f2f', 'fontWeight': 'bold'}
        
    codice_paz = session_data.get("codiceUtente")
    
    successo, msg_controller = farmaco_controller.registra_assunzione(codice_paz, id_ter, cod_farmaco, data_obj, ora_obj, float(qty))
    
    stile = {'color': '#2e7d32' if successo else '#d32f2f', 'fontWeight': 'bold', 'padding': '10px', 'backgroundColor': '#e8f5e9' if successo else '#ffebee', 'borderRadius': '4px', 'border': '1px solid'}
    
    return msg_controller, stile

@callback(
    Output("msg-segnalazione", "children"),
    Output("msg-segnalazione", "style"),
    Input("btn-salva-seg", "n_clicks"),
    State("paz-seg-evento", "value"),
    State("paz-seg-desc", "value"),
    State("paz-seg-inizio", "value"),
    State("paz-seg-fine", "value"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def handle_salva_segnalazione(n_clicks, evento_val, descrizione, inizio_str, fine_str, session_data):
    if not all([evento_val, descrizione, inizio_str, fine_str]):
        return "Compila tutti i campi del messaggio.", {'color': '#d32f2f', 'fontWeight': 'bold'}
        
    try:
        data_inizio_obj = datetime.strptime(inizio_str, "%Y-%m-%d").date()
        data_fine_obj = datetime.strptime(fine_str, "%Y-%m-%d").date()
    except ValueError:
        return "Errore di formato date (usa AAAA-MM-GG).", {'color': '#d32f2f', 'fontWeight': 'bold'}
        
    codice_paz = session_data.get("codiceUtente")
    evento_enum = TipoSegnalazionePaziente(evento_val)
    
    esito = segnalazione_controller.invia_segnalazione(codice_paz, descrizione, data_inizio_obj, data_fine_obj, evento_enum)
    
    stile = {'color': '#2e7d32', 'fontWeight': 'bold', 'padding': '10px', 'backgroundColor': '#e8f5e9', 'borderRadius': '4px', 'border': '1px solid'}
    return esito, stile

@callback(
    Output("msg-email-esito", "children"),
    Output("msg-email-esito", "style"),
    Input("btn-invia-email", "n_clicks"),
    State("paz-email-ogg", "value"),
    State("paz-email-testo", "value"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def handle_invia_email(n_clicks, oggetto, testo, session_data):
    if not all([oggetto, testo]):
        return "Compila oggetto e testo dell'email.", {'color': '#d32f2f', 'fontWeight': 'bold'}
        
    codice_paz = session_data.get("codiceUtente")
    oggi = datetime.now().date()
    
    esito = email_controller.invia_email(codice_paz, oggetto, testo, oggi)
    
    stile = {'color': '#2e7d32', 'fontWeight': 'bold', 'padding': '10px', 'backgroundColor': '#e8f5e9', 'borderRadius': '4px', 'border': '1px solid'}
    return esito, stile