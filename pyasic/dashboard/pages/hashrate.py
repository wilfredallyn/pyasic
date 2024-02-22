import dash
from dash import callback, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from io import StringIO
import json
import pandas as pd
import plotly.graph_objects as go
from pyasic.dashboard import get_hashrate_fig


dash.register_page(__name__, path="/hashrate", name="Hashrate")


def layout() -> html.Div:
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
def update_hashrate_graph(data: str) -> go.Figure:
    if data is None:
        return {}

    df_json = json.loads(data)
    df = pd.read_json(StringIO(df_json), orient="split")

    fig = get_hashrate_fig(df)
    return fig
