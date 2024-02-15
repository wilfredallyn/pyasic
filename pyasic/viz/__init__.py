import pandas as pd
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
