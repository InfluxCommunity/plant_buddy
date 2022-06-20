# Plant Buddy (Edge to Cloud Demo)

This demo is based of the [Plant Buddy IoT project](https://github.com/rickspencer3/plant-buddy) created by Rick Spencer. 
***Note: This branch is designed to demo Edge Data Replication. The setup and architecture of this design will not match the main branch***

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

## Installation
Before going through the setup instructions make sure you carried out the following installation steps:
1. Add your InfluxDB Cloud credentials to `src/default_settings.py`. Save the file.
	```python	
	INFLUXDB_HOST = 'https://us-east-1-1.aws.cloud2.influxdata.com'
	INFLUXDB_ORG = 'cloud_org' #signup email
	INFLUXDB_BUCKET = 'cloud_bucket' #plantbuddy
	INFLUXDB_TOKEN = 'cloud_token' # Generate all access token
	```
2. Build the Plant Buddy docker image:
	```bash
	docker build --pull --rm -f "dockerfile" -t plantbuddy:latest "."
	```
3. Install Telegraf localy. You can find the the binary install [here](https://portal.influxdata.com/downloads/). **(Note: if you are installing on a Ubuntu / Debian based host you can make use of the included Telegraf docker image)**

4. Install the local requirements file (Pyserial)
	```
	python3 -m pip install -r requirements.txt
	```

## Setup
Now that we have installed all componets required for running the project. Lets finish setting up:
1. Spin up the docker-compose file. This will launch InfluxDB OSS (Edge) and the Plant Buddy server app.
	```bash
	docker-compose -d . 
	```
2. Connect to the InfluxDB Edge instance with the Influx CLI and appy the included template:
	```bash
	influx config create -a -n plantbuddy-edge -u http://localhost:8086 -t plantbuddy -o plantbuddy 
	influx influx apply  -f ./docker/influxdb/influx_edge_template.yml
	```
	
3. Check which USB port your Arduino device is connected to. For example: 
	```
	'/dev/tty.usbmodem141101'
	```
	Is a common example for MacOS. An easy way to check is with the Arduino IDE.

4. Export the USB port as an enviroment varible and run the Telegraf config: 
	```bash
	export SERIAL_PORT=/dev/cu.usbmodem143301
	telegraf --debug --config ./docker/telegraf/telegraf.conf
	```

### Edge to Cloud Replication
This section will teach you how to configure InfluxDB OSS (Edge) to send data to InfluxDB Cloud.

1. Create a remote connection

```bash
influx remote create --name plant-buddy-cloud --remote-url https://us-east-1-1.aws.cloud2.influxdata.com --remote-org-id <ORG_ID> --remote-api-token <CLOUD_TOKEN>
```

2. Create a replication between a local bucket and a cloud bucket
```bash
influx replication create --local-bucket-id 1f158076adc417f5 --remote-bucket-id 621a1bf27327b2fc --remote-id 0947082f21c3e000  --name edge_to_cloud
```

### Setting up the Twillio alert
This task can be run at the edge or cloud depending on your architecture and setup. If you are security conscious and want to keep exposure to your edge device a minimum I recommend deploying the task to InfluxDB Cloud:

1. Create a Twilio account:  https://console.twilio.com/
2. Open `flux/twilio.flux`. You will need to modify lines `46 & 54` with your account credentials and phone numbers. 
	```
		    |> monitor["notify"](
	        data: notification,
	        endpoint:
	            http.endpoint(
	                url: "https://api.twilio.com/2010-04-01/Accounts/<INSERT_TWILIO_ACCOUNT>/Messages.json",
	            )(
	                mapFn: (r) => {
	                    body = r._message

	                    return {
	                        headers: {"Content-Type": "application/x-www-form-urlencoded", Authorization: auth},
	                        data: bytes(v: "To=########&From=#######&Body="+ body) ,
	                    }
	                },
	            ),
	    )
    ```
   3. Create two InfluxDB secrets with called: `twilio_username` and `twilio_password`. 
 
## Dashboard Access
To access the Plant Buddy dashboard head to [http//localhost:5001](http://locahost:5001) after setup. 
 

## Troubleshooting

<img width="999" alt="Screen Shot 2022-01-13 at 10 18 28 AM" src="https://user-images.githubusercontent.com/6667389/149377837-ed3ae5c9-11e4-4a37-981a-bbd4393b9651.png">

This probably indicates that your data is not being loaded in from the IOT side. 


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

