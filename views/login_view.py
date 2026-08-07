from dash import html, dcc, Input, Output, State, callback

from controllers.auth_controller import AuthController

auth_controller = AuthController()

layout = html.Div(
    className="login-container",
    children=[
        html.H2("Servizio Clinico - Gestione Diabete"),
        dcc.Input(id="input-username", type="text", placeholder="Username"),
        dcc.Input(id="input-password", type="password", placeholder="Password"),
        html.Button("Accedi", id="btn-login", n_clicks=0),
        html.Div(id="login-output"),
        dcc.Store(id="session-store"),  # memorizza utente loggato lato client
    ],
)


@callback(
    Output("login-output", "children"),
    Output("session-store", "data"),
    Input("btn-login", "n_clicks"),
    State("input-username", "value"),
    State("input-password", "value"),
    prevent_initial_call=True,
)
def handle_login(n_clicks, username, password):
    if not username or not password:
        return "Inserisci username e password.", None

    successo, ruolo, dato = auth_controller.login(username, password)

    if not successo:
        return dato, None  # dato contiene il messaggio di errore

    session_data = {"codiceUtente": dato.codiceUtente, "ruolo": ruolo, "nome": dato.nome}
    return f"Benvenuto/a {dato.full_name()} ({ruolo})", session_data
