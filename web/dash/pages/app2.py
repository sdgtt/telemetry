import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash
from app import app
import numpy

import plotly.graph_objects as go  # or plotly.express as px
from elasticsearch import Elasticsearch

port = 9200
index_name = "evm_tests"
server = "alpine"
es = Elasticsearch([{"host": server, "port": port}], http_auth=("elastic", "changeme"))
fig = go.Figure()  # or any Plotly Express function e.g. px.bar(...)


def get_test_dates():
    body2 = {"query": {"match_all": {}}}
    res = es.search(index=index_name, size=1000, body=body6,)


def get_data(iteration):

    body2 = {"query": {"query_string": {"query": "lte*", "fields": ["test_name"],}}}
    body4 = {"query": {"match": {"iterations": "1"}}}
    body6 = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {"test_name": "evm_1",},
                        "match": {"iteration": str(iteration)},
                    },
                ]
            }
        }
    }
    res = es.search(index=index_name, size=1000, body=body6,)

    # print(res["hits"]["hits"])
    # for val in res["hits"]["hits"]:
    #     # print(val['_source'])
    #     print(val["_source"]["carrier_frequency"])

    x = [val["_source"]["carrier_frequency"] for val in res["hits"]["hits"]]
    y = [val["_source"]["evm_db"] for val in res["hits"]["hits"]]

    x = numpy.array(x)
    y = numpy.array(y)
    inds = x.argsort()
    x = x[inds]
    y = y[inds]
    x = x / 1000000

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines+markers", name="EVM"))
    fig.update_xaxes(title_text="LO (MHz)", title_font={"size": 20}, title_standoff=25)
    fig.update_yaxes(title_text="EVM (dB)", title_font={"size": 20}, title_standoff=25)
    return fig


layout = html.Div(
    [
        html.H4("EVM Tests"),
        html.Div(
            [
                html.H6("""Select Iteration""", style={"margin-right": "2em"}),
                dcc.Dropdown(
                    id="iteration-dropdown",
                    options=[
                        {"label": "1", "value": 1},
                        {"label": "2", "value": 2},
                        {"label": "3", "value": 3},
                    ],
                    value="1",
                    style=dict(width="40%", verticalAlign="middle"),
                ),
            ],
            style=dict(display="flex"),
        ),
        html.Div(id="dd-output-container"),
        html.Div(
            [
                html.H6("""Select Test Date""", style={"margin-right": "2em"}),
                dcc.Dropdown(
                    id="testdate-dropdown",
                    options=[
                        {"label": "1", "value": 1},
                        {"label": "2", "value": 2},
                        {"label": "3", "value": 3},
                    ],
                    value="1",
                    style=dict(width="40%", verticalAlign="middle"),
                ),
            ],
            style=dict(display="flex"),
        ),
        html.Div(id="testdate-output-container"),
        dcc.Graph(id="evm_plot", figure=fig),
    ]
)


@app.callback(
    [
        dash.dependencies.Output("dd-output-container", "children"),
        dash.dependencies.Output("evm_plot", "figure"),
    ],
    [dash.dependencies.Input("iteration-dropdown", "value")],
)
def update_output(value):
    return ['You have selected "{}"'.format(value), get_data(value)]
