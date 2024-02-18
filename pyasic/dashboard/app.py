import argparse
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import json
from pyasic.db import load_db


app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.SPACELAB],
    suppress_callback_exceptions=True,
)

page_order = ["Status", "Hashrate", "Temperature"]
ordered_pages = sorted(
    dash.page_registry.values(), key=lambda page: page_order.index(page["name"])
)


sidebar = dbc.Nav(
    [
        dbc.NavLink(
            html.Div(page["name"], className="ms-2"), href=page["path"], active="exact"
        )
        for page in ordered_pages
    ],
    vertical=True,
    pills=True,
    className="bg-light",
)

app.layout = dbc.Container(
    [
        dcc.Location(id="url", refresh=False),
        dbc.Row(
            [dbc.Col(html.Div("pyasic", style={"fontSize": 50, "textAlign": "center"}))]
        ),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col([sidebar], xs=4, sm=4, md=2, lg=2, xl=2, xxl=2),
                dbc.Col([dash.page_container], xs=8, sm=8, md=10, lg=10, xl=10, xxl=10),
            ]
        ),
        dcc.Store(id="data-store", storage_type="session"),
    ],
    fluid=True,
)

parser = argparse.ArgumentParser(description="miner data dashboard")
parser.add_argument(
    "data_file",
    type=str,
    nargs="?",
    default="miner_data.db",
    help="File path to miner data",
)
parser.add_argument(
    "table_name", type=str, nargs="?", default="data", help="File path to miner data"
)
args = parser.parse_args()


@app.callback(Output("data-store", "data"), [Input("url", "pathname")])
def load_data(pathname):
    df = load_db(args.data_file, table_name=args.table_name)
    # json serialize for dcc.store
    return json.dumps(df.to_json(orient="split"))


if __name__ == "__main__":
    app.run_server(debug=True)
