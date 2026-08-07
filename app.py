"""
Entry point dell'applicazione Dash.
"""

from dash import Dash, html

from views import login_view

app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Telemedicina Diabete"

app.layout = html.Div(
    [
        login_view.layout,
    ]
)

if __name__ == "__main__":
    app.run(debug=True)
