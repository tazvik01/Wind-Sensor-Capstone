#include <SPI.h>
#include <LoRa.h>
#include <Adafruit_GPS.h>
#include <HardwareSerial.h>
#include <Wire.h>
#include <Adafruit_BME680.h>
#include <SoftwareSerial.h>

Adafruit_BME680 bme;
#define SEALEVELPRESSURE_HPA (1013.25)
//windsensor connection
#define RX_PIN 22
#define TX_PIN 21
//for the LoRa
const int csPin = 5;
const int resetPin = 2;
const int irqPin = 26;
//just a led 
const int ledPin = 33;
//for the wind sensor
SoftwareSerial sensorSerial(RX_PIN, TX_PIN);
unsigned long lastSent = 0;
//every 1 second
const unsigned long sendInterval = 1000;  // Send combined data every 1 second
//just creating a hardware seiral object
HardwareSerial mySerial(2);
//same as winsensor right above creating a hardware serial for GPS 
Adafruit_GPS GPS(&mySerial);
//mountain time
#define TIME_ZONE_OFFSET -7
String outMessage;
byte msgCount = 0;
String contents = "";
//address of the current device
byte localAddress = 0x18;
//adress of the device you want to send it to
byte destination = 0xFF;

void setup() {
  pinMode(ledPin, OUTPUT);
  pinMode(14, OUTPUT);
  Serial.begin(9600);
  mySerial.begin(9600, SERIAL_8N1, 16, 17);
  GPS.begin(9600);
  bme.begin(0x77);
  gps_initialization();
  Serial.println("Initializing Lora..");
  LoRa.setPins(csPin, resetPin, irqPin);
  if (!LoRa.begin(915E6)) {
    Serial.println("Starting LoRa failed!");
    while (1);
  }
}

void gps_initialization() {
  mySerial.begin(9600, SERIAL_8N1, 16, 17);
  GPS.begin(9600);
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);
  GPS.sendCommand(PGCMD_ANTENNA);
  delay(1000);
}

float convertNMEADegMinToDecDeg(float val, char dir) {
  int degrees = (int)(val / 100);
  float minutes = val - (degrees * 100);
  float decDeg = degrees + minutes / 60.0;
  if (dir == 'S' || dir == 'W') {
    decDeg = -decDeg;
  }
  return decDeg;
}

void printCoordinates() {
  float lat = convertNMEADegMinToDecDeg(GPS.latitude, GPS.lat);
  float lon = convertNMEADegMinToDecDeg(GPS.longitude, GPS.lon);
  Serial.print("Latitude: ");
  Serial.print(lat, 6);
  Serial.print("+Longitude$");
  Serial.println(lon, 6);
  Serial.print("Altitude(m):");
  Serial.println(GPS.altitude);
}

void loop() {
  digitalWrite(ledPin, HIGH);
  char c = GPS.read();

  float lat = convertNMEADegMinToDecDeg(GPS.latitude, GPS.lat);
  float lon = convertNMEADegMinToDecDeg(GPS.longitude, GPS.lon);

  if (int(lat) == 0 and int(lon) == 0){
    digitalWrite(14, (millis() / 500) & 1);

  }else{
    digitalWrite(14, HIGH);

  }



  if (GPS.newNMEAreceived()) {
    if (GPS.parse(GPS.lastNMEA())) {
      int localHour = GPS.hour + TIME_ZONE_OFFSET;
      if (localHour < 0) localHour += 24;
      if (localHour >= 24) localHour -= 24;
    }
  }

  unsigned long now = millis();
  if (now - lastSent >= sendInterval) {
    sendCombinedData();
    lastSent = now;
  }
}

void sendCombinedData() {
  float lat = convertNMEADegMinToDecDeg(GPS.latitude, GPS.lat);
  float lon = convertNMEADegMinToDecDeg(GPS.longitude, GPS.lon);
  float alt = GPS.altitude;

  float temperature = bme.readTemperature();
  float pressure = bme.readPressure() / 100.0F;
  float humidity = bme.readHumidity();

  String combinedMessage = String("Lat2:") + String(lat, 6) + 
                           ",Lon2:" + String(lon, 6) + 
                           ",Alt2:" + String(alt, 2) + 
                           ",Temp:" + String(temperature, 2) +
                           ",Pressure:" + String(pressure, 2) +
                           ",Humidity:" + String(humidity, 2);

  sendMessage(combinedMessage);

  Serial.println(combinedMessage);
}

void sendMessage(String outgoing) {
  LoRa.beginPacket();
  LoRa.write(destination);
  LoRa.write(localAddress);
  LoRa.write(msgCount);
  LoRa.write(outgoing.length());
  LoRa.print(outgoing);
  LoRa.endPacket();
  msgCount++;
}
