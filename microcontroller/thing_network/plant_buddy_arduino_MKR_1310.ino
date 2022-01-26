#include <MKRWAN_v2.h>
//#include <MKRWAN.h>

#include<stdlib.h>


#include <DHT.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Arduino_JSON.h>

LoRaModem modem;

String appEui = "";
String appKey = "";
bool connected;
int err_count;

#define DHTPIN 2
#define DHTTYPE DHT11

int moisturePin = A0;
int lightPin = A4;
int oneWirePin = 3;

DHT dht(DHTPIN, DHTTYPE);
OneWire oneWire(oneWirePin);
DallasTemperature sensors(&oneWire);
String deviceCode = "01";
const int dry = 680;
const int wet = 295;


void setup() {
  // put your setup code here, to run once:
  modem.begin(EU868);
  delay(5000);      // apparently the murata dislike if this tempo is removed...
  connected=false;
  err_count=0;
  
  Serial.begin(115200);
  Serial.print("Your module version is: ");
  Serial.println(modem.version());
  Serial.print("Your device EUI is: ");
  Serial.println(modem.deviceEUI());
  sensors.begin();
  dht.begin();
}

void loop() {
  int sensorVal = analogRead(moisturePin);
  int moistureSenorReading = map(sensorVal, wet, dry, 100, 0);


  int airTemperatureReading = dht.readTemperature();
  int humidityReading = dht.readHumidity();

  sensors.requestTemperatures();
  int soilTemperatureReading = sensors.getTempCByIndex(0);
  int lightReading = analogRead(lightPin);
  
/*
  Serial.println(transmitString("SM",moistureSenorReading));
  Serial.println(transmitString("AT",airTemperatureReading));
  Serial.println(transmitString("HU",himudityReading));
  Serial.println(transmitString("ST",soilTemperatureReading));
  Serial.println(transmitString("LI",lightReading));
*/

  JSONVar sensorData;
  sensorData["soil_moisture"] = moistureSenorReading;
  sensorData["air_temperature"] = airTemperatureReading;
  sensorData["humidity"] = humidityReading;
  sensorData["soil_temperature"] = soilTemperatureReading;
  sensorData["light"] = lightReading;



  String jsonString = JSON.stringify(sensorData);
  Serial.print("Sending: " + jsonString + " - ");
  Serial.println();
  String sensorString = String(moistureSenorReading) + "-" + String(airTemperatureReading) + "-" + String(humidityReading) + "-" + String(soilTemperatureReading) + "-" + String(lightReading);
  char payload[sensorString.length()+1];
  sensorString.toCharArray(payload, sensorString.length() +1);
  Serial.print(payload);
  

  if ( !connected ) {
    
    int ret=modem.joinOTAA(appEui, appKey);
    if ( ret ) {
      connected=true;
      modem.minPollInterval(60);
      modem.setPort(3);
      modem.setADR(true);
      delay(100);          
      err_count=0;
    }
  }
  if ( connected ) {
    int err=0;
    modem.beginPacket();
     
    modem.write(payload, sizeof(payload));
    //modem.write(test, 5);
    err = modem.endPacket(true);
    if ( err > 0 ) {
      // Confirmation not received - jam or coverage fault
      err_count++;
      if ( err_count > 50 ) {
        connected = false;
        Serial.println(err_count);
      }
      // wait for 2min for duty cycle with SF12 - 1.5s frame
      for ( int i = 0 ; i < 120 ; i++ ) {
        delay(1000);
      }
    } else {
      err_count = 0;
      // wait for 10s for duty cycle with SF7 - 55ms frame
      delay(10000);
    }
  }


  delay(60000);
}


