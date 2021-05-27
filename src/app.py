from flask import Flask, request, render_template

import users
import secret_store
import influxdb_client
import matplotlib.pyplot as plt, mpld3

app = Flask(__name__)

sensor_names = {"LI":"light", "HU":"humidity", "ST":"soil_temp",
                "AT":"air_temp", "SM":"soil_moisture"}

@app.route("/")
def index():
    user = users.authorize_and_get_user(request)

    return render_template("home.html", 
                            user_name = user["user_name"],
                            graph_code = "<i>put graph here</i>")

@app.route("/write", methods = ['POST'])
def write():
    user = users.authorize_and_get_user(request)
    d = parse_line(request.data.decode("UTF-8"), user["user_name"])
    print(d, flush=True)
    return {'result': "OK"}, 200

def parse_line(line, user_name):
    data = {"device" : line[:2],
            "sensor_name" : sensor_names.get(line[2:4], "unkown"),
            "value" : line[4:],
            "user": user_name}

    return data

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)