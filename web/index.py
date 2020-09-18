import sys
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app

################################################################################
## Page specific code
from pages import app1, app2, ad9361_tx_quad_cal
from pages.data import search

pages = ["app1", "app2", "search", "ad9361_tx_quad_cal"]


def page_lookup(pathname):
    """ Lookup page to apps """
    root = "/pages/"
    for page in pages:
        if root + page == pathname:
            return getattr(sys.modules[__name__], page).layout
    return "404"


################################################################################
## Main Index
app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
)


def create_index_page():
    """ Dynamically create links for all app pages """
    links = []
    for page in pages:
        links.append(dcc.Link("Go to Page " + page, href="/pages/" + page))
        links.append(html.Br())
    return links


index_page = create_index_page()


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/":
        return index_page
    return page_lookup(pathname)


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
