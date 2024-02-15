import dash
from dash import html, dash_table
import dash_bootstrap_components as dbc


dash.register_page(__name__, path="/", name="Home")


def layout():
    layout = html.Div([dbc.Container([dbc.Row([html.P(["home"])])])])
    return layout
