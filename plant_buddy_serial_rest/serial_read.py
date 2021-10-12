import threading
import serial
import time
import http.client
import json

connected = False
port = '/dev/tty.usbmodem143201'
baudrate = 9600 
conn = http.client.HTTPConnection('localhost:5000')

serial_port = serial.Serial(port)

def httpclient(sensordata):
    print("Sending data to Flask server", flush=True)
    headers = {'Content-type': 'text/plain'}
    
    global conn
    conn.request('POST', '/write', sensordata, headers)

    response = conn.getresponse()
    print(response.read().decode())


def read_from_port(ser):
    # Wait until there is data waiting in the serial buffer
    while (True):
        if(ser.in_waiting > 0):
            # Read data out of the buffer until a carraige return / new line is found
            serialString = ser.readline()

            # Print the contents of the serial data
            #print(serialString.decode('Ascii'))
            httpclient(serialString.decode('Ascii'))
        else:
            time.sleep(5)






if __name__ == "__main__":
    try:
          thread = threading.Thread(target=read_from_port, args=(serial_port,))
          thread.start()  
    except KeyboardInterrupt:
        print('Interrupted closing Serial Connection')
        serial_port.close()

