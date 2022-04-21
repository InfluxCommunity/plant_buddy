import dash_bootstrap_components as dbc
from dash import html
from dash import dcc
import base64
import users

def layout(sidebar):
    MAIN_STYLE = {
    "margin-left": "4rem",
    "margin-right": "2rem",
    "padding": "2rem 2rem 2rem 8rem",
    }
    # Main HTML / Bootstap structure for front end app
    layout = dbc.Container(
        [
            sidebar,
            dbc.Container([
            dcc.Store(id="store"),
            html.H1("Plant Buddy Dashboard"),
            html.Hr(),
            # Add your new tabs hear.
            dbc.Tabs(
                [
                    dbc.Tab(label="Data Explorer", tab_id="data_explorer"),
                    dbc.Tab(label="Soil and Room Temperature", tab_id="temperature"),
                    dbc.Tab(label="Room Humidity and Light", tab_id="hum_and_light"),
                ],
                id="tabs",
                active_tab="data_explorer",
            ),
            html.Div(id="tab-content", className="p-4"),], style=MAIN_STYLE)
        ]
    )
    return layout


def controls(forumMea,forumBuckets, graph_default):
    # Creates a drop down forum which queries influx for both a list of buckets and fields
    control = dbc.Card(
        [

                dbc.Label("Fields"),
                dcc.Dropdown(
                    id="y-variable",
                    options=[
                        {"label": col, "value": col} for col in forumMea
                    ],
                    value="Select a Field",
                ),
      

                dbc.Label("Bucket"),
                dcc.Dropdown(
                    id="bucket",
                    options=[
                        {"label": col, "value": col} for col in forumBuckets
                    ],
                    value=graph_default["bucket"],
                ),
        ],
        body=True,
    )
    return control


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

   


    image_filename = 'src/static/logo.png' # replace with your own image
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
