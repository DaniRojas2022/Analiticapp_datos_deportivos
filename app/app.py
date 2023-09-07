import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html

app = dash.Dash(__name__, use_pages=True,  external_stylesheets=[dbc.themes.BOOTSTRAP])

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("Premier League", className="display-6"),
        html.Hr(),
        #html.P(
        #    "Página web para la analitica de datos de resultados de los partidos de futbol de la Premier League. Con datos desde 2016", className="lead"
        #),
        dbc.Nav(
            [
                dbc.NavLink("Resumen", href="/resumen", active="exact"),
                dbc.NavLink("Defensa", href="/defensa", active="exact"),
                dbc.NavLink("Ataque", href="/ataque", active="exact"),
                dbc.NavLink("Versus", href="/versus", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE
)

content = html.Div(dash.page_container
        ,style=CONTENT_STYLE
        ,id="page-content"
    )

app.layout = html.Div([
    dcc.Location(id="url")
    ,sidebar
    ,content])




if __name__ == "__main__":
    app.run_server(port=8888, debug=True)