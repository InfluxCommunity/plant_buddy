import time
import http.client
import random
import signal

conn = http.client.HTTPConnection('localhost:5001')

sensors = dict()
variance = 0.02
deviceID = '01'
interrupt = False
# SM: Moisture Sensor
# AT: Air Temperature
# HU: Humidity
# ST: Soil Temperature
# LI: Light
def init_mock_sensors():
    random.seed()
    global sensors
    sensors = {
        'SM': random.randint(40, 70),
        'AT': random.randint(60, 90),
        'HU': random.randint(20, 80),
        'ST': random.randint(60, 90),
        'LI': random.randint(0, 100),
    }
    print("Initialized mock sensors: %s" % sensors)

def update_sensor_data():
    global interrupt
    interrupt = False
    global sensors
    for sensor, value in sensors.items():
        diff = value * variance
        new_value = random.uniform(value-diff, value+diff)
        sensors[sensor] = new_value
        
def write_data_point():
    global sensors
    for sensor, value in sensors.items():
        httpclient("%s%s%03d" % (deviceID, sensor, value))

def httpclient(sensordata):
    print("Sending data to Flask server: %s"%sensordata, flush=True)
    headers = {'Content-type': 'text/plain'}
    
    global conn
    conn.request('POST', '/write', sensordata, headers)

    response = conn.getresponse()
    print(response.read().decode())

def trigger_low_moisture(signum, frame):
    global interrupt
    if interrupt:
        exit(0)
    interrupt = True
    global sensors
    if sensors['SM'] <= 30:
        sensors['SM'] = 60.0
        print("Soil Moisture set to 60%")
    else:
        sensors['SM'] = 20.0
        print("Soil Moisture set to 20%")

if __name__ == "__main__":
    init_mock_sensors()
    signal.signal(signal.SIGINT, trigger_low_moisture)

    while True:
        update_sensor_data()
        write_data_point()
        time.sleep(5)

