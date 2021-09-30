import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import base64

def createNav():
# the style arguments for the sidebar. We use position:fixed and a fixed width
    SIDEBAR_STYLE = {
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "15rem",
        "padding": "2rem 1rem",
        "background-color": "#f8f9fa",
    }

    # the styles for the main content position it to the right of the sidebar and
    # add some padding.
    CONTENT_STYLE = {
        "margin-left": "18rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem",
    }
    image_filename = './static/logo.png' # replace with your own image
    encoded_image = base64.b64encode(open(image_filename, 'rb').read())
    sidebar = html.Div(
        [
            html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode())),
            html.Hr(),
            html.P(
                "Click here to query InfluxDB for new data", className="lead"
            ),
            dbc.Nav(
                [
            dbc.Button(
                "Regenerate graphs",
                color="primary",
                id="button",
                className="mb-3",
                    )
                ],
                vertical=True,
                pills=True,
            ),
        ],
        style=SIDEBAR_STYLE,
    )

    return sidebar