import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import pandas as pd

def init_dash(server):
    dash_app1 = dash.Dash(__name__, server=server, url_base_pathname='/api/dash0/')

    dash_app1.layout = html.Div([
        html.H1(' ', id='title1'),
        dcc.Interval(id='interval1', interval=60000)
    ])

    @dash_app1.callback(
        Output('title1', 'children'),
        [Input('interval1', 'n_intervals')]
    )
    def update_graph1(n):
        return ' '
