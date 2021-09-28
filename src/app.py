from flask import Flask, request
import time

from pandas.core.frame import DataFrame
import users
import secret_store
import influxdb_client
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd


server = Flask(__name__)
# Dashboard is built using plotly's dash package. This also includes bootstap styles from dash_bootstrap
app = app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Ref to serial sensor samples. 
sensor_names = {"LI":"light", "HU":"humidity", "ST":"soil_temp",
                "AT":"air_temp", "SM":"soil_moisture"}

cloud_org = "05ea551cd21fb6e4"
cloud_bucket = "plantbuddy"

client = influxdb_client.InfluxDBClient(
    url = "https://us-east-1-1.aws.cloud2.influxdata.com/",
    token = secret_store.get_bucket_secret(),
    org = cloud_org
)

write_api = client.write_api()
query_api = client.query_api()

# Get user. Currently static refrence. Used to filter sensor data in InfluxDB
# TODO change this to login in page. 
user = users.authorize_and_get_user(request)



# Main HTML / Bootstap structure for front end app
app.layout = dbc.Container(
    [
        dcc.Store(id="store"),
        html.H1("Plant Buddy Dashboard"),
        html.Hr(),
        dbc.Button(
            "Regenerate graphs",
            color="primary",
            block=True,
            id="button",
            className="mb-3",
        ),
        # Add your new tabs hear.
        dbc.Tabs(
            [
                dbc.Tab(label="Soil Moisture", tab_id="soil_moisture"),
                dbc.Tab(label="Soil and Room Temperature", tab_id="temperature"),
                dbc.Tab(label="Room Humidity and Light", tab_id="hum_and_light"),
            ],
            id="tabs",
            active_tab="soil_moisture",
        ),
        html.Div(id="tab-content", className="p-4"),
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
        if active_tab == "soil_moisture":
            return dcc.Graph(figure=data["soil_moisture"])
        elif active_tab == "temperature":
            return dbc.Row(
                [
                    dbc.Col(dcc.Graph(figure=data["soil_temp_graph"]), width=6),
                    dbc.Col(dcc.Graph(figure=data["air_temp_graph"]), width=6),
                ]
            )
        elif active_tab == "hum_and_light":
            return dbc.Row(
                [
                    dbc.Col(dcc.Graph(figure=data["humidity_graph"]), width=6),
                    dbc.Col(dcc.Graph(figure=data["light_graph"]), width=6),
                ]
            )
    return "No tab selected"



@app.callback(Output("store", "data"), [Input("button", "n_clicks")])
def generate_graphs(n):
# Generate graphs based upon pandas data frame. 
    df = querydata("plantbuddy", "soil_moisture", "jay" )
    soil_moisture = px.line(df, x="time", y="value", title= df.iloc[0]['label'])

    df = querydata("plantbuddy", "soil_temp", "jay" )
    soil_temp_graph = px.line(df, x="time", y="value", title=df.iloc[0]['label'])

    df = querydata("plantbuddy", "air_temp", "jay" )
    air_temp_graph= px.line(df, x="time", y="value", title=df.iloc[0]['label'])

    df = querydata("plantbuddy", "humidity", "jay" )
    humidity_graph= px.line(df, x="time", y="value", title=df.iloc[0]['label'])

    df = querydata("plantbuddy", "light", "jay" )
    light_graph= px.line(df, x="time", y="value", title=df.iloc[0]['label'])

    # save figures in a dictionary for sending to the dcc.Store
    return {"soil_moisture": soil_moisture, 
            "soil_temp_graph": soil_temp_graph, 
            "air_temp_graph": air_temp_graph, 
            "humidity_graph": humidity_graph, 
            "light_graph": light_graph
            }





# Server call used to write sensor data to InfluxDB
@server.route("/write", methods = ['POST'])
def write():
    user = users.authorize_and_get_user(request)
    d = parse_line(request.data.decode("UTF-8"), user["user_name"])
    write_to_influx(d)
    return {'result': "OK"}, 200

def write_to_influx(data):
    p = influxdb_client.Point(data["sensor_name"]).tag("user",data["user"]).tag("device_id",data["device"]).field("reading", int(data["value"]))
    write_api.write(bucket=cloud_bucket, org=cloud_org, record=p)
    print(p, flush=True)

def parse_line(line, user_name):
    data = {"device" : line[:2],
            "sensor_name" : sensor_names.get(line[2:4], "unkown"),
            "value" : line[4:],
            "user": user_name}
    return data
#####################
# Wrapper function used to query InfluxDB> Calls Flux scrip with paramaters. Data query to data frame.
def querydata(bucket, measurment, field) -> DataFrame:
    x_vals = []
    y_vals = []
    label = []
    query = open("/Users/jayclifford/Documents/repos/IoT_Plant_Demo/plant-buddy/src/graph.flux").read().format(bucket, measurment, field)
    result = query_api.query(query, org=cloud_org)
    for table in result:
            for record in table:
                y_vals.append(record["_value"])
                x_vals.append(record["_time"])
                label = record["_measurement"]
    df = pd.DataFrame({
        "time": x_vals,
        "value": y_vals,
        "label": label
            })
    print(df)
    return df

@server.route("/notify", methods = ['POST'])
def notify():
    print("notification received", flush=True)
    print(request.data, flush=True)
    return {'result': "OK"}, 200
    # TODO: check the authorization and actually notify the user

if __name__ == '__main__':
  app.run_server(host='0.0.0.0', port=5000, debug=True)