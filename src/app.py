from flask import Flask, request, render_template
import matplotlib.pyplot as plt, mpld3
import users
import secret_store
import influxdb_client

app = Flask(__name__)

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

@app.route("/")
def index():
    user = users.authorize_and_get_user(request)
    query = open("graph.flux").read().format(user["user_name"])
    result = query_api.query(query, org=cloud_org)
    
    fig = plt.figure()
    for table in result:
        x_vals = []
        y_vals = []
        label = ""
        for record in table:
            y_vals.append(record["_value"])
            x_vals.append(record["_time"])
            label = record["_measurement"]
        plt.plot(x_vals, y_vals, label=label)

    plt.legend()
    grph = mpld3.fig_to_html(fig)
    return render_template("home.html", 
                            user_name = user["user_name"],
                            graph_code = grph)

@app.route("/write", methods = ['POST'])
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

@app.route("/notify", methods = ['POST'])
def notify():
    print("notification received", flush=True)
    print(request.data, flush=True)
    return {'result': "OK"}, 200
    # TODO: check the authorization and actually notify the user

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)