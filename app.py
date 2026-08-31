"""Entry point dell'applicazione Dash."""

from datetime import date
from dash import Dash, html, dcc, Input, Output, State, no_update
from dash.exceptions import PreventUpdate

from views import login_view
from views.paziente_view import paziente_layout
from views.diabetologo_view import diabetologo_layout

from controllers.alert_controller import AlertController

app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Centro Diabetologico"

alert_controller = AlertController()

app.layout = html.Div([

    html.Div(
        id="view-login",
        children=[login_view.login_layout()],
        style={'display': 'block'}
    ),

    html.Div(
        id="view-paziente",
        children=[],
        style={'display': 'none'}
    ),

    html.Div(
        id="view-medico",
        children=[],
        style={'display': 'none'}
    ),

    dcc.Interval(
        id="background-interval",
        interval=60000,
        n_intervals=0
    )
])


# routing tra login / dashboard paziente / dashboard medico
@app.callback(
    Output("view-login", "style"),
    Output("view-paziente", "children"),
    Output("view-paziente", "style"),
    Output("view-medico", "children"),
    Output("view-medico", "style"),
    Input("session-store", "data")
)
def update_route(session_data):
    if not session_data:
        return {'display': 'block'}, [], {'display': 'none'}, [], {'display': 'none'}

    ruolo = session_data.get("ruolo")

    if ruolo == "paziente":
        return {'display': 'none'}, paziente_layout(session_data), {'display': 'block'}, [], {'display': 'none'}

    elif ruolo == "diabetologo":
        return {'display': 'none'}, [], {'display': 'none'}, diabetologo_layout(session_data), {'display': 'block'}

    return {'display': 'block'}, [], {'display': 'none'}, [], {'display': 'none'}


@app.callback(
    Output("session-store", "data", allow_duplicate=True),
    Input("btn-logout", "n_clicks"),
    prevent_initial_call=True
)
def esegui_logout(n_clicks):
    if n_clicks and n_clicks > 0:
        return None
    raise PreventUpdate


# job periodico: controlla l'aderenza alle terapie di tutti i pazienti
@app.callback(
    Output("background-interval", "n_intervals"),
    Input("background-interval", "n_intervals"),
    prevent_initial_call=True
)
def run_background_tasks(n):
    df_pazienti = alert_controller.dm_pazienti.read_all()
    oggi = date.today()

    for _, row in df_pazienti.iterrows():
        codice_paz = row["codiceUtente"]
        esito_alert = alert_controller.verifica_assunzioni(codice_paz, oggi)

        if esito_alert["notifica_diabetologo"]:
            print(f"[{oggi} - ALERT MEDICO] Attenzione: il paziente {codice_paz} non assume regolarmente i farmaci. (Inviato al medico: {esito_alert['codice_medico']})")
        elif esito_alert["notifica_paziente"]:
            print(f"[{oggi} - ALERT PAZIENTE] Paziente {codice_paz}, ricordati di assumere i farmaci prescritti!")

    return no_update

if __name__ == "__main__":
    app.run(debug=False)
