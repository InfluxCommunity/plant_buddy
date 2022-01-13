# Plant Buddy with Dash

This demo is based of the [Plant Buddy IoT project](https://github.com/rickspencer3/plant-buddy) created by Rick Spencer. 

The goal:
This demo shows how InfluxDB can be successfully used as a storage backend for a Flask server. Leverage Flux queries to filter and retrive your IoT data and then use Dash plotly to visualise. The below BPMN outlines the overall architecture and data flow:
![PlantBuddy_Architecture](https://user-images.githubusercontent.com/45856600/135630864-a1d67f87-0789-47e2-b7e7-dbff583f91ea.png)

## Hardware List
List of hardware required to recreate demo: 
### Control Board
- [Arduino](https://store.arduino.cc/collections/most-popular/products/arduino-uno-rev3)

or
- [Argon / Boron](https://store.particle.io/collections/dev-kits/products/argon-kit)
### Sensor List
- [DS18B20 Temperature Sensor(Waterproof)](https://randomnerdtutorials.com/guide-for-ds18b20-temperature-sensor-with-arduino/)
- [Soil Moisture Sensor v1.2](https://how2electronics.com/interface-capacitive-soil-moisture-sensor-arduino/)
- [Photoresistor module](https://arduinomodules.info/ky-018-photoresistor-module/)
- [DH11 Temperature Humidity Sensor](https://create.arduino.cc/projecthub/pibots555/how-to-connect-dht11-sensor-with-arduino-uno-f4d239)

### Hardware Wiring
![Plant_Buddy_bb](/microcontroller/plant_buddy_arduino.png)


## Setup
When setting up the project you will need to add a secret folder in src and add your token in a token.json file like so:
```
{"token":"imatokensupersecret"}
```

You will want to edit the line in secret_store.py:
```
f = open ('/myfilestructure/plant-buddy/src/secret/token.json', "r")
```
You might need to change the port in serial_read.py depending on the device you are using:
```
port = '/dev/tty.usbmodem141101'
```

in app.py you will want to add your own org and bucket:
```
cloud_org = "yourorgid"
cloud_bucket = "yourbucket"
```

To run the project you want to run from the src file:
```
python3 app.py
```


## Troubleshooting

<img width="999" alt="Screen Shot 2022-01-13 at 10 18 28 AM" src="https://user-images.githubusercontent.com/6667389/149377837-ed3ae5c9-11e4-4a37-981a-bbd4393b9651.png">

This probably indicates that your data is not being loaded in from the IOT side. 


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.
