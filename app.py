"""
Entry point dell'applicazione Dash.

Per ora espone solo la pagina di login per validare la catena
View -> Controller -> Model -> CSV. Le view paziente_view.py e
diabetologo_view.py sono i prossimi passi (vedi README).
"""

from dash import Dash, html

from views import login_view

app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Telemedicina Diabete"

app.layout = html.Div(
    [
        login_view.layout,
        # In futuro: routing tra paziente_view e diabetologo_view
        # in base a session-store, usando dcc.Location + callback.
    ]
)

if __name__ == "__main__":
    app.run(debug=True)
