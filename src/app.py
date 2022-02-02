from flask import Flask, request
import users
import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
from influx_helper import influxHelper
import nav


server = Flask(__name__)
# Dashboard is built using plotly's dash package. This also includes bootstap styles from dash_bootstrap
app = app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

cloud_org = "05ea551cd21fb6e4"
cloud_bucket = "plantbuddy"
graph_default = {"_field":"air_temperature", "bucket": cloud_bucket}

influx = influxHelper(cloud_org, cloud_bucket)



# Get user. Currently static refrence. Used to filter sensor data in InfluxDB
# TODO change this to login in page. 
user = users.authorize_and_get_user(request)
forumMea= influx.getMeasurements(cloud_bucket)
forumBuckets = influx.getBuckets()

# Creates a drop down forum which queries influx for both a list of buckets and fields
controls = dbc.Card(
    [

                dbc.Label("Measurment"),
                dcc.Dropdown(
                    id="y-variable",
                    options=[
                        {"label": col, "value": col} for col in forumMea
                    ],
                    value="Select a measurment",
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

sidebar = nav.createNav()
MAIN_STYLE = {
    "margin-left": "4rem",
    "margin-right": "2rem",
    "padding": "2rem 2rem 2rem 8rem",
    }

# Main HTML / Bootstap structure for front end app
app.layout = dbc.Container(
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

@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab"), Input("store", "data")],
)
def render_tab_content(active_tab, data):
    """
    This callback takes the 'active_tab' property as input, as well as the
    stored graphs, and renders the tab content depending on what the value of
    'active_tab' is.
    """
    if active_tab and data is not None:
        if active_tab == "data_explorer":
            return dbc.Row(
                [
                dbc.Col(controls, md=4),
                dbc.Col( dbc.Card([dcc.Graph(figure=data["data_explorer"])],style={"width": "auto"}), md=8),
                ]
            )
        elif active_tab == "temperature":
            return dbc.Row(
                [
                    dbc.Col( dbc.Card([dcc.Graph(figure=data["soil_temp_graph"])],style={"width": "auto"}), md=6),
                    dbc.Col( dbc.Card([dcc.Graph(figure=data["air_temp_graph"])],style={"width": "auto"}), md=6),
     
                ]
            )
        elif active_tab == "hum_and_light":
            return dbc.Row(
                [   
                    dbc.Col( dbc.Card([dcc.Graph(figure=data["humidity_graph"])],style={"width": "auto"}), md=6),
                    dbc.Col( dbc.Card([dcc.Graph(figure=data["light_graph"])],style={"width": "auto"}), md=6),
                ]
            )
    return "No tab selected"



@app.callback(Output("store", "data"), [Input("button", "n_clicks")])
def generate_graphs(n):
# Generate graphs based upon pandas data frame. 
# This is our editable graph, you can change the parameters
    df = influx.querydata(graph_default["bucket"], graph_default["_field"], "eui-323932326d306512" )
    print(df)
    data_explorer = px.line(df, x="_time", y="_value", title= df.iloc[0]['device_id'])
     # This is a hard coded graph
    df = influx.querydata(cloud_bucket, "soil_moisture", "eui-323932326d306512" )
    soil_temp_graph = px.line(df, x="_time", y="_value", title=df.iloc[0]['_measurement'])

    df = influx.querydata(cloud_bucket, "air_temperature", "eui-323932326d306512" )
    air_temp_graph= px.line(df, x="_time", y="_value", title=df.iloc[0]['_measurement'])

    df = influx.querydata(cloud_bucket, "humidity", "eui-323932326d306512" )
    humidity_graph= px.line(df, x="_time", y="_value", title=df.iloc[0]['_measurement'])

    #This queries our hard coded flux query
    df = influx.querydataStatic()
    light_graph= px.line(df, x="_time", y="_value", title=df.iloc[0]['_measurement'])

    # save figures in a dictionary for sending to the dcc.Store
    return {"data_explorer": data_explorer, 
            "soil_temp_graph": soil_temp_graph, 
            "air_temp_graph": air_temp_graph, 
            "humidity_graph": humidity_graph, 
            "light_graph": light_graph
            }


# Updates inital graphs default query variables (measurment and bucket)
@app.callback(Output("y-variable", "value"), [Input("y-variable", "value"), Input("bucket", "value")], prevent_initial_call=True)
def updateForumData(y, b):
    graph_default["bucket"] = b
    graph_default["measurment"] = y
    return y





# Server call used to write sensor data to InfluxDB
# The methods in this function are inside influx_helper.py
@server.route("/write", methods = ['POST'])
def write():
    user = users.authorize_and_get_user(request)
    d = influx.parse_line(request.data.decode("UTF-8"), user["user_name"])
    influx.write_to_influx(d)
    return {'result': "OK"}, 200



@server.route("/notify", methods = ['POST'])
def notify():
    print("notification received", flush=True)
    print(request.data, flush=True)
    return {'result': "OK"}, 200
    # TODO: check the authorization and actually notify the user

if __name__ == '__main__':
  app.run_server(host='0.0.0.0', port=5000, debug=True)