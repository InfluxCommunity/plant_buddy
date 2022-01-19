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
graph_default = {"measurment":"soil_moisture", "bucket": cloud_bucket}

influx = influxHelper(cloud_org, cloud_bucket)

# Get user. Currently static refrence. Used to filter sensor data in InfluxDB
# TODO change this to login in page. 
user = users.authorize_and_get_user(request)
forumMea= influx.getMeasurements(cloud_bucket)
forumBuckets = influx.getBuckets()

# Creates a drop down forum which queries influx for both a list of buckets and fields
controls = main_html.controls(forumMea,forumBuckets, graph_default)
sidebar = main_html.createNav()
# Main HTML / Bootstap structure for front end app
app.layout = main_html.layout(sidebar)

@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab"), Input("store", "data")],
)

@app.callback(Output("store", "data"), [Input("button", "n_clicks")])
def generate_graphs(n):
# Generate graphs based upon pandas data frame. 
    # This is our editable graph, you can change the parameters
    df = influx.querydata(graph_default["bucket"], graph_default["measurment"], "jay" )
    data_explorer = px.line(df, x="_time", y="_value", title= df.iloc[0]['_measurement'])
    # This is a hard coded graph
    df = influx.querydata(cloud_bucket, "soil_temp", "jay" )
    soil_temp_graph = px.line(df, x="_time", y="_value", title=df.iloc[0]['_measurement'])

    df = influx.querydata(cloud_bucket, "air_temp", "jay" )
    air_temp_graph= px.line(df, x="_time", y="_value", title=df.iloc[0]['_measurement'])

    df = influx.querydata(cloud_bucket, "humidity", "jay" )
    humidity_graph= px.line(df, x="_time", y="_value", title=df.iloc[0]['_measurement'])

    #TODO Part of demo (Part-4) we will add this in
    df = influx.querydataStatic()
    #df = influx.querydata(cloud_bucket, "light", "jay" )
    light_graph= px.line(df, x="_time", y="_value", title=df.iloc[0]['_measurement'])
    ########

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