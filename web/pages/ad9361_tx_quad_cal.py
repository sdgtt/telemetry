import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash
from app import app
import numpy

import plotly.graph_objects as go  # or plotly.express as px
from elasticsearch import Elasticsearch

port = 9200
index_name = "ad936x_tx_quad_cal"
server = "alpine"
es = Elasticsearch([{"host": server, "port": port}], http_auth=("elastic", "changeme"))
fig = go.Figure()  # or any Plotly Express function e.g. px.bar(...)


def get_test_dates():
    body2 = {"query": {"match_all": {}}}
    res = es.search(index=index_name, size=1000, body=body6,)


def get_data(device):

    print(device)
    # body1 = {"sort": [{"date": {"order": "asc"}}], "query": {"match_all": {}}}
    # body2 = {"query": {"query_string": {"query": "lte*", "fields": ["test_name"],}}}
    # body6 = {
    #     "query": {
    #         "bool": {
    #             "must": [
    #                 {
    #                     "match": {"channel": "evm_1",},
    #                     "match": {"device": "device"},
    #                 },
    #             ]
    #         }
    #     }
    # }

    fig = go.Figure()

    for chan in range(2):
        body7 = {
            "sort": [{"date": {"order": "asc"}}],
            "query": {
                "bool": {"must": [{"match": {"channel": str(chan)}}, {"match": {"device": device}}]}
            }
        }

        body6 = {
            "sort": [{"date": {"order": "asc"}}],
            "query": {
                "bool": {
                    "must": [
                        {"match": {"channel": str(1)}, "match": {"device": device},},
                    ]
                }
            },
        }

        # body4 = {"sort": [{"date": {"order": "asc"}}],"query": {"match": {"channel": str(chan)}}}
        res = es.search(index=index_name, size=1000, body=body7,)
        d = [val["_source"] for val in res["hits"]["hits"]]
        for k in d:
            print(k["date"], k["channel"])

        x = [val["_source"]["date"] for val in res["hits"]["hits"]]
        y = [val["_source"]["failed"] for val in res["hits"]["hits"]]
        t = [val["_source"]["iterations"] for val in res["hits"]["hits"]]

        y = [y[k] / t[k] for k in range(len(y))]
        fig.add_trace(
            go.Scatter(x=x, y=y, mode="lines+markers", name="Channel " + str(chan))
        )

    fig.update_xaxes(title_text="Date", title_font={"size": 20}, title_standoff=25)
    fig.update_yaxes(title_text="Calibration Failure (%)", title_font={"size": 20}, title_standoff=25)
    return fig


layout = html.Div(
    [
        html.H4("AD9361 TX Quad Calibration Tests"),
        html.Div(
            [
                html.H6("""Device """, style={"margin-right": "2em"}),
                dcc.Dropdown(
                    id="iteration-dropdown",
                    options=[
                        {"label": "NA", "value": "NA"},
                        {"label": "fmcomms2", "value": "fmcomms2"},
                        {"label": "adrv9361", "value": "adrv9361"},
                        {"label": "pluto", "value": "pluto"},
                    ],
                    value="NA",
                    style=dict(width="40%", verticalAlign="middle"),
                ),
            ],
            style=dict(display="flex"),
        ),
        html.Div(id="tt-output-container"),
        # html.Div(
        #     [
        #         html.H6("""Select Test Date""", style={"margin-right": "2em"}),
        #         dcc.Dropdown(
        #             id="testdate-dropdown",
        #             options=[
        #                 {"label": "1", "value": 1},
        #                 {"label": "2", "value": 2},
        #                 {"label": "3", "value": 3},
        #             ],
        #             value="1",
        #             style=dict(width="40%", verticalAlign="middle"),
        #         ),
        #     ],
        #     style=dict(display="flex"),
        # ),
        html.Div(id="testdate-output-container"),
        dcc.Graph(id="quad_cal_plot", figure=fig),
    ]
)


@app.callback(
    [
        dash.dependencies.Output("tt-output-container", "children"),
        dash.dependencies.Output("quad_cal_plot", "figure"),
    ],
    [dash.dependencies.Input("iteration-dropdown", "value")],
)
def update_output(value):
    return ['You have selected "{}"'.format(value), get_data(value)]
