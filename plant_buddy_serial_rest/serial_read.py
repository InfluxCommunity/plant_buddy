import threading
import time
import serial
import serial.tools.list_ports
import http.client
import argparse

connected_ports = []


def get_serial_ports():
        """
        Returns a list of serial ports
        """
        return [port.device for port in serial.tools.list_ports.comports(include_links=False)]


# Simple class to write to a http server. In this case we are writing to a flask server.
class http_writer():
    def __init__(self, url):
        self.conn = http.client.HTTPConnection(url)
    
    def send(self, sensordata):
            print("Sending data to Flask server", flush=True)
            
            headers = {'Content-type': 'text/plain'}
            self.conn.request('POST', '/write', sensordata, headers)
            response = self.conn.getresponse()

            print(response.read().decode(), flush=True)


# Custom wrapper class for connecting and reading from serial port.
class serial_device():
    def __init__(self, http_writer, port):
        self.port = port
        self.ser = None
        self.baudrate = 9600
        self.timeout = 1
        self.connected = False
        self.http_writer = http_writer

    def connect(self):
        global connected_ports
        # Establish a connection to the serial port. Also used to reconnect if the connection is lost.
        try: 
            if self.port is None:
                for port in get_serial_ports():
                    if port not in connected_ports:
                        self.port = port
                        break

            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            self.connected = True
            connected_ports.append(self.port)
            print("Connected to " + self.port)
        except:
            print("Error - could not connect to serial port")
            self.port = None
    
    def disconnect(self):
        #Disconnect from a serial port
        self.ser.close()
        self.connected = False
        return True

    
    
    def read(self):
        global connected_ports
        # Wait until there is data waiting in the serial buffer
        while (True):
            try: 
                if self.connected == False:
                    self.connect()
                    time.sleep(5)
                    print("Could not connect. Trying again in 5s...")
                else:
                    if(self.ser.in_waiting > 0):
                        print("Reading data...")
                        # Read data out of the buffer until a carraige return / new line is found
                        serialString = self.ser.readline()
                        self.http_writer.send(serialString.decode('Ascii'))
                    else:
                        time.sleep(5)
            except OSError:
                # catch class for a USB disconnect
                print(f"OSError - lost connection with ... {self.port}")
                self.connected = False
                connected_ports.remove(self.port)
                time.sleep(5)






def main(port, args):
    if args.url is None:
        writer = http_writer("localhost:5001")
    else:
        writer = http_writer(args.url)
# We create a serial_device class instance. Then attempt to connect and read from port.
    sd = serial_device(writer, port)
    sd.connect()
    sd.read()


if __name__ == "__main__":
    # Create argument parser to handle command line arguments.
    parser = argparse.ArgumentParser(description='Connection information')
    parser.add_argument('--url', dest='url', type=str, help='url of flask server')  
    args = parser.parse_args()

    # Get list of serial ports. 
    try:
     ports = get_serial_ports()
    # Iterate through the list of ports and attempt to connect to each USB port. 
    # Start a thread for USB ports.
     for port in ports:
        if "usb" in port:
            t = threading.Thread(target=main, args=(port,args))
            t.start()
        else:
            print(f"Port: {port} is not a USB port so will be skipped")
          
    except KeyboardInterrupt:
        print('Interrupted closing Serial Connection')
