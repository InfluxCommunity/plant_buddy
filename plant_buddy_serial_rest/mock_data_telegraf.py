
import time
import json
import random



sensors = dict()
variance = 0.02
deviceID = '01'
sensor_names = {"LI":"light", "HU":"humidity", "ST":"soil_temperature",
                "AT":"air_temperature", "SM":"soil_moisture"}
user = "jay"

# SM: Moisture Sensor
# AT: Air Temperature
# HU: Humidity
# ST: Soil Temperature
# LI: Light
def init_mock_sensors():
    random.seed()
    global sensors
    sensors = {
        'SM': random.randint(30, 70),
        'AT': random.randint(60, 90),
        'HU': random.randint(20, 80),
        'ST': random.randint(60, 90),
        'LI': random.randint(0, 100),
    }
 

def update_sensor_data():
    global sensors
    for sensor, value in sensors.items():
        diff = value * variance
        new_value = random.uniform(value-diff, value+diff)
        sensors[sensor] = new_value
        
def write_data_point():
    global sensors
    for sensor, value in sensors.items():
        jsondata("%s%s%03d" % (deviceID, sensor, value))



def jsondata(sensordata):
    d = parse_line(sensordata, user)
    print(json.dumps(d), flush=True)


def parse_line(line, user_name):
    if line[4:].rstrip() != "ERR":
        data = {"device" : line[:2],
                sensor_names.get(line[2:4], "unkown") : int(line[4:].rstrip()) ,
                "user": user_name}
    else:
        data = {"device" : line[:2],
                 sensor_names.get(line[2:4], "unkown"): int(0),
                "user": user_name}
    return data



if __name__ == "__main__":
    init_mock_sensors()
    while True:
        update_sensor_data()
        write_data_point()
        time.sleep(5)

