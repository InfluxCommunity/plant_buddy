import dash_bootstrap_components as dbc
from dash import html
import base64
import users
def createNav():
    name = users.get_user_name()
# the style arguments for the sidebar. We use position:fixed and a fixed width
    SIDEBAR_STYLE = {
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "18rem",
        "padding": "2rem 1rem",
        "background-color": "#f8f9fa",
    }

   


    image_filename = './static/logo.png' # replace with your own image
    encoded_image = base64.b64encode(open(image_filename, 'rb').read())
    sidebar = html.Div(
        [
            html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode())),
            html.Hr(),
            html.P(
                "Welcome:" + name, className="lead"
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
            html.Hr(),
            html.P(
                "Click here to query InfluxDB for new data", className="lead"
            ),
        ],
        style=SIDEBAR_STYLE,
    )

    return sidebar