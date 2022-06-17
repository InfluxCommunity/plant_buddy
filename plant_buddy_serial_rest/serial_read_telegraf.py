import threading
import serial
import time

import json

connected = False
port = '/dev/cu.usbmodem143301'
baudrate = 9600 
sensor_names = {"LI":"light", "HU":"humidity", "ST":"soil_temperature",
                "AT":"air_temperature", "SM":"soil_moisture"}
user = "jay"


serial_port = serial.Serial(port)

def jsondata(sensordata):
    d = parse_line(sensordata, user)
    print(json.dumps(sensordata), flush=True)



def parse_line(line, user_name):
    if line[4:].rstrip() != "ERR":
        data = {"device_id" : line[:2],
                sensor_names.get(line[2:4], "unkown") : int(line[4:].rstrip()) ,
                "user": user_name}
    else:
        data = {"device_id" : line[:2],
                 sensor_names.get(line[2:4], "unkown"): int(0),
                "user": user_name}
    return data

def read_from_port(ser):
    # Wait until there is data waiting in the serial buffer
    while (True):
        if(ser.in_waiting > 0):
            # Read data out of the buffer until a carraige return / new line is found
            serialString = ser.readline()


            jsondata(serialString.decode('Ascii'))
        else:
            time.sleep(5)






if __name__ == "__main__":
    try:
          thread = threading.Thread(target=read_from_port, args=(serial_port,))
          thread.start()  
    except KeyboardInterrupt:
        print('Interrupted closing Serial Connection')
        serial_port.close()

