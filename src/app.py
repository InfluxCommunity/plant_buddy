from flask import Flask, request, render_template
import time
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
import plotly.graph_objects as go

server = Flask(__name__)
app = app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])

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


user = users.authorize_and_get_user(request)


#fig = px.line(df, x="time", y="value", title='Soil Moisture')

app.layout = dbc.Container(
    [
        dcc.Store(id="store"),
        html.H1("Dynamically rendered tab content"),
        html.Hr(),
        dbc.Button(
            "Regenerate graphs",
            color="primary",
            block=True,
            id="button",
            className="mb-3",
        ),
        dbc.Tabs(
            [
                dbc.Tab(label="Scatter", tab_id="scatter"),
                dbc.Tab(label="Histograms", tab_id="histogram"),
            ],
            id="tabs",
            active_tab="scatter",
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
        if active_tab == "scatter":
            return dcc.Graph(figure=data["scatter"])
        elif active_tab == "histogram":
            return dbc.Row(
                [
                    dbc.Col(dcc.Graph(figure=data["hist_1"]), width=6),
                    dbc.Col(dcc.Graph(figure=data["hist_2"]), width=6),
                ]
            )
    return "No tab selected"



@app.callback(Output("store", "data"), [Input("button", "n_clicks")])
def generate_graphs(n):
     query = open("/Users/jayclifford/Documents/repos/IoT_Plant_Demo/plant-buddy/src/graph.flux").read().format(user["user_name"])
     result = query_api.query(query, org=cloud_org)
     for table in result:
            x_vals = []
            y_vals = []
            label = ""
            for record in table:
                y_vals.append(record["_value"])
                x_vals.append(record["_time"])
                label = record["_measurement"]
     df = pd.DataFrame({
        "time": x_vals,
        "value": y_vals,
            })

     scatter = px.line(df, x="time", y="value", title='Soil Moisture')
  #  scatter = go.Scatter(df)

     hist_1 = px.line(df, x="time", y="value", title='Soil Moisture')


     hist_2 = px.line(df, x="time", y="value", title='Soil Moisture')


    # save figures in a dictionary for sending to the dcc.Store
     return {"scatter": scatter, "hist_1": hist_1, "hist_2": hist_2}






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

@server.route("/notify", methods = ['POST'])
def notify():
    print("notification received", flush=True)
    print(request.data, flush=True)
    return {'result': "OK"}, 200
    # TODO: check the authorization and actually notify the user

if __name__ == '__main__':
  app.run_server(host='0.0.0.0', port=5000, debug=True)