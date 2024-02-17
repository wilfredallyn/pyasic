import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def get_status_fig(df):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=df["datetime"], y=df["hashrate"], name="Hashrate"),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=df["datetime"], y=df["temperature_avg"], name="Temperature"),
        secondary_y=True,
    )

    fig.update_layout(
        title="Hashrate and Temperature over Time",
        xaxis_title="Time",
    )
    fig.update_yaxes(title_text="Hashrate", secondary_y=False)
    fig.update_yaxes(title_text="Temperature", secondary_y=True)
    fig.update_yaxes(range=[0, 50], secondary_y=False)
    fig.update_yaxes(range=[0, 100], secondary_y=True)

    return fig


def get_hashrate_fig(df):
    avg_hashrate = (
        df[["hashboards_0_hashrate", "hashboards_1_hashrate", "hashboards_2_hashrate"]]
        .mean(axis=0)
        .sum()
    )

    fig = px.line(
        df,
        x="datetime",
        y=["hashboards_0_hashrate", "hashboards_1_hashrate", "hashboards_2_hashrate"],
        labels={"value": "Hashrate", "variable": "Hashboards"},
        title="Hashrate over Time",
    )

    for trace, new_name in zip(fig.data, ["0", "1", "2"]):
        trace.name = new_name

    fig.add_hline(
        y=avg_hashrate,
        line_dash="dot",
        annotation_text=f"Average Hashrate ({avg_hashrate.round(2)} TH/s)",
        annotation_position="bottom right",
    )
    fig.update_yaxes(range=[0, avg_hashrate * 1.1])

    return fig
