import threading
import serial
import time
import http.client
import json
from confluent_kafka import  SerializingProducer, KafkaError, KafkaException
from confluent_kafka.serialization import StringSerializer
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient

from os import environ
from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

connected = False
port = '/dev/cu.usbmodem143201'
baudrate = 9600 
serial_port = serial.Serial(port)
sensor_names = {"LI":"light", "HU":"humidity", "ST":"soil_temperature",
                "AT":"air_temperature", "SM":"soil_moisture"}
user = "jay"


def error_cb(err):
    """ The error callback is used for generic client errors. These
        errors are generally to be considered informational as the client will
        automatically try to recover from all errors, and no extra action
        is typically required by the application.
        For this example however, we terminate the application if the client
        is unable to connect to any broker (_ALL_BROKERS_DOWN) and on
        authentication errors (_AUTHENTICATION). """

    print("Client error: {}".format(err))
    if err.code() == KafkaError._ALL_BROKERS_DOWN or \
       err.code() == KafkaError._AUTHENTICATION:
        # Any exception raised from this callback will be re-raised from the
        # triggering flush() or poll() call.
        raise KafkaException(err)


def delivery_report(err, msg):
    """
    Reports the failure or success of a message delivery.
    Args:
        err (KafkaError): The error that occurred on None on success.
        msg (Message): The message that was produced or failed.
    Note:
        In the delivery report callback the Message.key() and Message.value()
        will be the binary format as encoded by any configured Serializers and
        not the same object that was passed to produce().
        If you wish to pass the original object(s) for key and value to delivery
        report callback we recommend a bound callback or lambda where you pass
        the objects along.
    """
    if err is not None:
        print("Delivery failed for User record {}: {}".format(msg.key(), err))
        return
    print('User record {} successfully produced to {} [{}] at offset {}'.format(
        msg.key(), msg.topic(), msg.partition(), msg.offset()))

def sensor_to_dict(sensor, ctx):

    template = {"measurement": "sensor_data", "tags": {"device": sensor['device'], "user": sensor['user'] }, sensor['sensor_name']: sensor['value'] }
    print(template)
    # User._address must not be serialized; omit from dict
    return template



class kafka_producer: 
    def __init__ (self) -> None:
        self.schema_str = """{
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "PlantBuddy",
            "description": "Plant Health Data",
            "type": "object",
            "properties": {
                "measurement": {
                "description": "measurment_name",
                "type": "string"
                },
            "tags": {
                "description": "tags",
                "type": "object",
                "properties": {
                    "device": {
                        "description": "UniqueID of device",
                        "type": "string" 
                        },
                    "user": {
                        "description": "user",
                        "type": "string" 
                        } 
                }
            },
            "soil_moisture": {
            "description": "soil_moisture",
            "type": "number"
                },
            "air_temperature": {
            "description": "air_temperature",
            "type": "number"
                },
            "humidity": {
            "description": "humidity",
            "type": "number"
                },
            "light": {
            "description": "light",
            "type": "number"
                },
            "soil_temperature": {
            "description": "soil_temperature",
            "type": "number"
                }
            },
            "required": []
            }"""


        schema_registry_conf = {'url': 'https://psrc-8vyvr.eu-central-1.aws.confluent.cloud', 
                                'basic.auth.user.info': environ.get('SCHEMEA_REGISTRY_LOGIN')}
        schema_registry_client = SchemaRegistryClient(schema_registry_conf)

        self.json_serializer = JSONSerializer(self.schema_str, schema_registry_client, sensor_to_dict)

        self.p = SerializingProducer({
        'bootstrap.servers': 'pkc-41wq6.eu-west-2.aws.confluent.cloud:9092',
        'sasl.mechanism': 'PLAIN',
        'security.protocol': 'SASL_SSL',
        'sasl.username': environ.get('SASL_USERNAME'),
        'sasl.password': environ.get('SASL_PASSWORD'),
        'error_cb': error_cb,
        'key.serializer': StringSerializer('utf_8'),
        'value.serializer': self.json_serializer
        })


    def sendSample(self, topic, data):
            # Produce message: this is an asynchronous operation.
            # Upon successful or permanently failed delivery to the broker the
            # callback will be called to propagate the produce result.
            # The delivery callback is triggered from poll() or flush().
            # For long running
            # produce loops it is recommended to call poll() to serve these
            # delivery report callbacks.
            self.p.produce(topic=topic, key=str(data['device']), value=data,
                    on_delivery=delivery_report)

            # Trigger delivery report callbacks from previous produce calls.
            self.p.poll(0)

            # flush() is typically called when the producer is done sending messages to wait
            # for outstanding messages to be transmitted to the broker and delivery report
            # callbacks to get called. For continous producing you should call p.poll(0)
            # after each produce() call to trigger delivery report callbacks.
            self.p.flush(10)




def parse_line(line, user_name):
    if line[4:].rstrip() != "ERR":
        data = {"device" : line[:2],
                "sensor_name" : sensor_names.get(line[2:4], "unkown"),
                "value" : int(line[4:].rstrip()) ,
                "user": user_name}
    else:
        data = {"device" : line[:2],
                "sensor_name" : sensor_names.get(line[2:4], "unkown"),
                "value" : int(0) ,
                "user": user_name}
    return data


def send(sensordata, kafka):
    d = parse_line(sensordata, user)
    kafka.sendSample("plant_buddy_data", d)


def read_from_port(ser):
    kafkaProducer = kafka_producer()
    # Wait until there is data waiting in the serial buffer
    while (True):
        if(ser.in_waiting > 0):
            # Read data out of the buffer until a carraige return / new line is found
            serialString = ser.readline()

            # Print the contents of the serial data
            #print(serialString.decode('Ascii'))
            send(serialString.decode('Ascii'), kafkaProducer)
        else:
            time.sleep(5)






if __name__ == "__main__":
    try:
          thread = threading.Thread(target=read_from_port, args=(serial_port,))
          thread.start()  
    except KeyboardInterrupt:
        print('Interrupted closing Serial Connection')
        serial_port.close()

