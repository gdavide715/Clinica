"""View — pagina di login.
"""

from dash import html, dcc, Input, Output, State, callback

from controllers.auth_controller import AuthController

auth_controller = AuthController()


def login_layout():
    return html.Div(className="login-card", children=[
        html.H2("Centro Diabetologico", className="login-title"),
        html.P("Accedi con le tue credenziali", className="login-subtitle"),
        html.Hr(),

        html.Label("Username", className="login-label"),
        dcc.Input(
            id="input-user", type="text", placeholder="es. mrossi o averdi...",
            className="login-input",
        ),

        html.Label("Password", className="login-label"),
        dcc.Input(
            id="input-pass", type="password", placeholder="mrossipwd o averdipwd...",
            className="login-input",
        ),

        html.Button("Login", id="btn-login", n_clicks=0, className="login-button"),

        html.Div(id="login-error", className="login-message-error"),
        html.Div(id="login-success", className="login-message-success"),

        dcc.Store(id="session-store"),  # memorizza utente loggato lato client
    ])


@callback(
    Output("login-error", "children"),
    Output("login-success", "children"),
    Output("session-store", "data"),
    Input("btn-login", "n_clicks"),
    State("input-user", "value"),
    State("input-pass", "value"),
    prevent_initial_call=True,
)
def handle_login(n_clicks, username, password):
    if not username or not password:
        return "Inserisci username e password.", "", None

    successo, ruolo, dato = auth_controller.login(username, password)

    if not successo:
        return dato, "", None  # dato contiene il messaggio di errore

    session_data = {
        "codiceUtente": dato.codiceUtente,
        "ruolo": ruolo,
        "nome": dato.nome,
        "email": getattr(dato, "email", None),  # presente solo per Diabetologo
    }
    return "", f"Benvenuto/a {dato.full_name()} ({ruolo})", session_data
