# Plant Buddy with Thing Network

This README will help guide you through the process or wiring and connecting a Arduino-WAN-1310 to the Thing Network. The example is based off the original Plant Buddy Demo. 


## Hardware List
List of hardware required to recreate demo: 
### Control Board
- [Arduino](https://store-usa.arduino.cc/products/arduino-mkr-wan-1310)

### Sensor List
- [DS18B20 Temperature Sensor(Waterproof)](https://randomnerdtutorials.com/guide-for-ds18b20-temperature-sensor-with-arduino/)
- [Soil Moisture Sensor v1.2](https://how2electronics.com/interface-capacitive-soil-moisture-sensor-arduino/)
- [Photoresistor module](https://arduinomodules.info/ky-018-photoresistor-module/)
- [DH11 Temperature Humidity Sensor](https://create.arduino.cc/projecthub/pibots555/how-to-connect-dht11-sensor-with-arduino-uno-f4d239)

### Hardware Wiring
![Plant_Buddy_bb](plant_buddy_v2_MKR_1310_bb.png)


## Setup
1. Wire your WAN-1310 based on hardware wiring provided. Although not required I highly recommed using a breadboard, this saves you soldering the wires to the controller.
2. Create a Thing Network account [here](https://account.thethingsnetwork.org/)
3. Go to [applications](https://eu1.cloud.thethings.network/console/applications) and click create new application.
4. Once you have created a new application, enter it and click on end devices.
5. I now advise following the offical connection guide [here](https://docs.arduino.cc/tutorials/mkr-wan-1300/the-things-network)
6. Once complete you can now edit [plant_buddy_arduino_MKR_1310](microcontroller/thing_network/plant_buddy_arduino_MKR_1310.ino). Change the following to fit your end device credentials:
```cpp
String appEui = "######";
String appKey = "######";
```
7. Load the project onto your WAN-1310



## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.
