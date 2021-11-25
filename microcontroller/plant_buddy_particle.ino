SYSTEM_MODE(SEMI_AUTOMATIC);



#include <Adafruit_DHT.h>
#include <spark-dallas-temperature.h>
#include <OneWire.h>
#include <stdlib.h>




#define DHTPIN D3
#define DHTTYPE DHT11
int moisturePin = A0;

int lightPin = A4;
int oneWirePin = D4;

DHT dht(DHTPIN, DHTTYPE);
OneWire oneWire(oneWirePin);
DallasTemperature sensors(&oneWire);
String deviceCode = "01";
const int dry = 2730;
const int wet = 1177;


void setup() {
  Serial.begin(9600);
  Serial.println("Begin Reading");
  Serial.println("-------------");
  sensors.begin();
  dht.begin();
}

void loop() {

  delay(10);
  int sensorVal = analogRead(moisturePin);
  int moistureSenorReading = map(sensorVal, wet, dry, 100, 0);


  int airTemperatureReading = dht.getTempCelcius();
  int himudityReading = dht.getHumidity();

  sensors.requestTemperatures();
  int soilTemperatureReading = sensors.getTempCByIndex(0);
  int lightReading = analogRead(lightPin);

  Serial.println(transmitString("SM",moistureSenorReading));
  Serial.println(transmitString("AT",airTemperatureReading));
  Serial.println(transmitString("HU",himudityReading));
  Serial.println(transmitString("ST",soilTemperatureReading));
  Serial.println(transmitString("LI",lightReading));
  

  delay(10000);
}

String transmitString(String sensor, int reading) {
  String transmitString = deviceCode + sensor +  paddedString(reading);
  return transmitString;
}

String paddedString(int reading) {
  String str = String(reading);
  if(reading < 0) return "ERRDebug" + reading;

  //String str = String(reading);
  if(reading < 10) str = "00"  + str;
  else if(reading < 100) str = "0" + str;
  return str;
}