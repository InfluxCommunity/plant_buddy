from flask import Flask, request, render_template

import users
import secret_store
import influxdb_client
app = Flask(__name__)

sensor_names = {"LI":"light", "HU":"humidity", "ST":"soil_temp",
                "AT":"air_temp", "SM":"soil_moisture"}

client = influxdb_client.InfluxDBClient(
    url = "https://eastus-1.azure.cloud2.influxdata.com/",
    token = secret_store.get_write_secret(),
    org = "f1d35b5f11f06a1d"
)

write_api = client.write_api()

@app.route("/")
def index():
    user = users.authorize_and_get_user(request)

    return render_template("home.html", user_name = user["user_name"])

@app.route("/write", methods = ['POST'])
def write():
    user = users.authorize_and_get_user(request)
    d = parse_line(request.data.decode("UTF-8"), user["user_name"])
    write_to_influx(d)
    return {'result': "OK"}, 200

def write_to_influx(data):
    p = influxdb_client.Point(data["sensor_name"]).tag("user",data["user"]).tag("device_id",data["device"]).field("reading", data["value"])
    write_api.write(bucket="plantbuddy", org="f1d35b5f11f06a1d", record=p)
    print(p, flush=True)

def parse_line(line, user_name):
    data = {"device" : line[:2],
            "sensor_name" : sensor_names.get(line[2:4], "unkown"),
            "value" : line[4:],
            "user": user_name}

    return data


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)