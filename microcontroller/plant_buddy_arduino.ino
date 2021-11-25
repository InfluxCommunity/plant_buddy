#include<stdlib.h>
#include <dht.h>
#include <OneWire.h>
#include <DallasTemperature.h>

dht DHT;
int moisturePin = A0;
int dhtPin = A2;
int lightPin = A4;
int powerPin = 4;
int oneWirePin = 2;

OneWire oneWire(oneWirePin);
DallasTemperature sensors(&oneWire);

String deviceCode = "01";

void setup() 
{ 
  Serial.begin(9600);

  sensors.begin();
                                                                                                                                                      
  pinMode(powerPin, OUTPUT);
  digitalWrite(powerPin, LOW);

  Serial.println("Begin Reading");
  Serial.println("-------------");
}

void loop()
{
  digitalWrite(powerPin, HIGH);
  delay(10);
  int moistureSenorReading = analogRead(moisturePin);

  DHT.read11(dhtPin);
  int airTemperatureReading = DHT.temperature;
  int himudityReading = DHT.humidity;

  sensors.requestTemperatures();
  int soilTemperatureReading = sensors.getTempCByIndex(0);

  int lightReading = analogRead(lightPin);

  Serial.println(transmitString("SM",moistureSenorReading));
  Serial.println(transmitString("AT",airTemperatureReading));
  Serial.println(transmitString("HU",himudityReading));
  Serial.println(transmitString("ST",soilTemperatureReading));
  Serial.println(transmitString("LI",lightReading));

  digitalWrite(powerPin, LOW);
  delay(60000);
}

String transmitString(String sensor, int reading) {
  String transmitString = deviceCode + sensor +  paddedString(reading);
  return transmitString;
}

String paddedString(int reading) {
  if(reading < 0) return "ERR";

  String str = String(reading);
  if(reading < 10) str = "00"  + str;
  else if(reading < 100) str = "0" + str;
  return str;
}
