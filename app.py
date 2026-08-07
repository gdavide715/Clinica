"""
Entry point dell'applicazione Dash.
"""

from dash import Dash, html

from views import login_view

app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Centro Diabetologico"

app.layout = html.Div(
    [
        login_view.login_layout(),
    ]
)

if __name__ == "__main__":
    app.run(debug=True)
