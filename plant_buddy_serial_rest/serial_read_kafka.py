from ensurepip import bootstrap
import threading
import serial
import time
import json
from kafka import KafkaProducer
from kafka.errors import KafkaError

from os import environ
from uuid import uuid4

from confluent_kafka import  SerializingProducer, KafkaError, KafkaException
from confluent_kafka.serialization import StringSerializer
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient

connected = False
port = '/dev/tty.usbmodem143201'
baudrate = 9600 
producer = KafkaProducer(value_serializer=lambda m: json.dumps(m).encode('ascii'))

serial_port = serial.Serial(port)


   
#!/usr/bin/env python
#
# Copyright 2018 Confluent Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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


# Create producer
def sensor_to_dict(data, ctx):
    """
    Returns a dict representation of a User instance for serialization.
    Args:
        user (User): User instance.
        ctx (SerializationContext): Metadata pertaining to the serialization
            operation.
    Returns:
        dict: Dict populated with user attributes to be serialized.
    """
    # User._address must not be serialized; omit from dict
    return data


class kafka_producer: 
    def __init__ (self) -> None:
        self.schema_str = """{
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Generator",
            "description": "A fuel engines health data",
            "type": "object",
            "properties": {
                "device_id": {
                "description": "UniqueID of generator",
                "type": "string"
                },
                "air_temperature": {
                "description": "latitude",
                "type": "number"
                },
                "light": {
                "description": "longitude",
                "type": "number"
                },
                "soil_moisture": {
                "description": "temperature",
                "type": "number"
                },
                "soil_temperature": {
                "description": "pressure",
                "type": "number"
            },
            "required": []
            }"""

        
        schema_registry_conf = {'url': 'https://psrc-8vyvr.eu-central-1.aws.confluent.cloud', 
                                'basic.auth.user.info': environ.get('SCHEMEA_REGISTRY_LOGIN')}
        schema_registry_client = SchemaRegistryClient(schema_registry_conf)

        self.json_serializer = JSONSerializer(self.schema_str, schema_registry_client, engine_to_dict)

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
            self.p.produce(topic=topic, key=str(uuid4()), value=data,
                    on_delivery=delivery_report)

            # Trigger delivery report callbacks from previous produce calls.
            self.p.poll(0)

            # flush() is typically called when the producer is done sending messages to wait
            # for outstanding messages to be transmitted to the broker and delivery report
            # callbacks to get called. For continous producing you should call p.poll(0)
            # after each produce() call to trigger delivery report callbacks.
            self.p.flush(10)




def read_from_port(ser):
    # Wait until there is data waiting in the serial buffer
    while (True):
        if(ser.in_waiting > 0):
            # Read data out of the buffer until a carraige return / new line is found
            serialString = ser.readline()

            # Print the contents of the serial data
            #print(serialString.decode('Ascii'))
            kafka_producer(serialString.decode('Ascii'))
        else:
            time.sleep(5)






if __name__ == "__main__":
    try:
          thread = threading.Thread(target=read_from_port, args=(serial_port,))
          thread.start()  
    except KeyboardInterrupt:
        print('Interrupted closing Serial Connection')
        serial_port.close()

