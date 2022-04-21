from flask import Flask, request
import users
import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
from influx_helper import influxHelper
import main_html


server = Flask(__name__)
# Dashboard is built using plotly's dash package. This also includes bootstap styles from dash_bootstrap
app = app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

cloud_org = "05ea551cd21fb6e4"
cloud_bucket = "plantbuddy"
graph_default = {"_field":"air_temperature", "bucket": cloud_bucket, "deviceID": "01"}


influx = influxHelper(cloud_org, cloud_bucket)

# Get user. Currently static refrence. Used to filter sensor data in InfluxDB
# TODO change this to login in page. 
user = users.authorize_and_get_user(request)
forumMea= influx.getFields(cloud_bucket)
forumBuckets = influx.getBuckets()

# This is our html snippets from the main_html file
controls =  main_html.controls(forumMea,forumBuckets, graph_default)
sidebar = main_html.createNav()
app.layout = main_html.layout(sidebar)


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
    df = influx.querydata(bucket=graph_default["bucket"], sensor_name=graph_default["_field"], deviceID=graph_default["deviceID"] )
    data_explorer = px.line(df, x="_time", y="_value", title= df.iloc[0]['_field'])
    
     # This is a hard coded graph
    df = influx.querydata(cloud_bucket, "soil_moisture", graph_default["deviceID"] )
    soil_temp_graph = px.line(df, x="_time", y="_value", title=df.iloc[0]['_field'])

    df = influx.querydata(cloud_bucket, "air_temperature", graph_default["deviceID"] )
    air_temp_graph= px.line(df, x="_time", y="_value", title=df.iloc[0]['_field'])

    df = influx.querydata(cloud_bucket, "humidity", graph_default["deviceID"] )
    humidity_graph= px.line(df, x="_time", y="_value", title=df.iloc[0]['_field'])

    #This queries our hard coded flux query
   # df = influx.querydataStatic()
    df = influx.querydata(cloud_bucket, "light", graph_default["deviceID"] )
    light_graph= px.line(df, x="_time", y="_value", title=df.iloc[0]['_field'])

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
    graph_default["_field"] = y
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
  app.run_server(host='0.0.0.0', port=5001, debug=True)