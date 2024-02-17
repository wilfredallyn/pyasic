import dash
from dash import callback, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from io import StringIO
import json
from pyasic.viz import get_hashrate_fig
import pandas as pd


dash.register_page(__name__, path="/hashrate", name="Hashrate")


def layout():
    return html.Div(
        [
            dbc.Container(
                [
                    dbc.Row(
                        [
                            dcc.Graph(id="hashrate-graph"),
                        ]
                    )
                ]
            ),
            dcc.Store(id="data-store"),
        ]
    )


@callback(Output("hashrate-graph", "figure"), [Input("data-store", "data")])
def update_hashrate_graph(data):
    if data is None:
        return {}

    df_json = json.loads(data)
    df = pd.read_json(StringIO(df_json), orient="split")

    fig = get_hashrate_fig(df)
    return fig
