#include <SPI.h>
#include <LoRa.h>
#include <Adafruit_GPS.h>
#include <HardwareSerial.h>
#include <Wire.h>
#include <Adafruit_BME280.h>
#include <SoftwareSerial.h>

Adafruit_BME280 bme;
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
byte localAddress = 0xBB;
//adress of the device you want to send it to
byte destination = 0xFF;

// Wind data variables
float windAngle = 0;
float windSpeed = 0;
bool windDataUpdated = false;

void setup() {
  pinMode(14, OUTPUT);
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);
  mySerial.begin(9600, SERIAL_8N1, 16, 17);
  GPS.begin(9600);
  sensorSerial.begin(9600);
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

//this function is there so we can pass the accurate GPS location to google maps API
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
  static String sentence;

  float lat = convertNMEADegMinToDecDeg(GPS.latitude, GPS.lat);
  float lon = convertNMEADegMinToDecDeg(GPS.longitude, GPS.lon);

  if (int(lat) == 0 and int(lon) == 0){
    digitalWrite(14, (millis() / 500) & 1);

  }else{
    digitalWrite(14, HIGH);

  }




  
  while (sensorSerial.available() > 0) {
    char incomingChar = sensorSerial.read();
    if (incomingChar == '\n') {
      parseMWVSentence(sentence);
      sentence = "";
    } else {
      sentence += incomingChar;
    }
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

void parseMWVSentence(String nmea) {
  if (!nmea.startsWith("$") || nmea.indexOf("MWV") < 0) {
    return;
  }
  
  nmea.trim();
  int firstCommaIndex = nmea.indexOf(',');
  if (firstCommaIndex < 0) {
    return;
  }
  
  const byte MAX_FIELDS = 7;
  String fields[MAX_FIELDS];
  byte fieldIndex = 0;
  int startIndex = 0;
  
  while (fieldIndex < MAX_FIELDS) {
    int commaIndex = nmea.indexOf(',', startIndex);
    if (commaIndex == -1) {
      fields[fieldIndex] = nmea.substring(startIndex);
      break;
    } else {
      fields[fieldIndex] = nmea.substring(startIndex, commaIndex);
    }
    startIndex = commaIndex + 1;
    fieldIndex++;
  }
  
  if (fieldIndex < 3) {
    return;
  }
  
  windAngle = fields[1].toFloat();
  windSpeed = fields[3].toFloat();
  windDataUpdated = true;
  
}

void sendCombinedData() {
  float lat = convertNMEADegMinToDecDeg(GPS.latitude, GPS.lat);
  float lon = convertNMEADegMinToDecDeg(GPS.longitude, GPS.lon);
  float alt = GPS.altitude;
  
  String combinedMessage = String("Lat1:") + String(lat, 6) + 
                         ",Lon1:" + String(lon, 6) + 
                         ",Alt1:" + String(alt, 2) + 
                         ",WindAngle1:" + String(windAngle) + 
                         ",WindSpeed1:" + String(windSpeed, 2);
  
  sendMessage(combinedMessage);

  Serial.println(combinedMessage);
 
  windDataUpdated = false;
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