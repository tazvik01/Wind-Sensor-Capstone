#include <SPI.h>
#include <LoRa.h>
#include <Adafruit_GPS.h>
#include <HardwareSerial.h>
#include <Wire.h>
#include <Adafruit_BME280.h>
#include <SoftwareSerial.h>

// ------------------ Your existing code & setup ------------------
Adafruit_BME280 bme; 
#define SEALEVELPRESSURE_HPA (1013.25)
#define RX_PIN 22  
#define TX_PIN 21

const int csPin = 5;
const int resetPin = 2;
const int irqPin = 26;
const int ledPin = 33;

SoftwareSerial sensorSerial(RX_PIN, TX_PIN);

HardwareSerial mySerial(2); // Use Serial2 for ESP32
Adafruit_GPS GPS(&mySerial);

#define TIME_ZONE_OFFSET -7

String outMessage;

byte msgCount = 0;

String contents = "";

String buttonPress = "button pressed";

bool rcvButtonState;

byte localAddress = 0xBB;
byte destination = 0xFF;

int buttonPin = 15;
int sendButtonState;

// For timing LoRa transmissions:
unsigned long lastSendTime = 0;
const unsigned long sendInterval = 2000; // send every 2 seconds

void setup() {
  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);

  // GPS serial lines
  mySerial.begin(9600, SERIAL_8N1, 16, 17); // RX=16, TX=17
  GPS.begin(9600);
  sensorSerial.begin(9600);

  gps_initialization();

  // ---------- ENABLE LoRa here ----------
  Serial.println("Initializing LoRa ...");
  LoRa.setPins(csPin, resetPin, irqPin);

  if (!LoRa.begin(915E6)) {
    Serial.println("Starting LoRa failed!");
    while (1);
  }

  // If you want to receive data, enable:
  // LoRa.onReceive(onReceive);
  // LoRa.receive();

  Serial.println("LoRa init succeeded.");

  // BME280 init (uncomment if you’re actually using BME280)
  // if (!bme.begin(0x77)) {
  //   Serial.println("Could not find BME280 sensor!");
  //   while (1);
  // }
}

void gps_initialization(){
  mySerial.begin(9600, SERIAL_8N1, 16, 17); // RX=16, TX=17
  GPS.begin(9600);

  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA); // Enable GPRMC and GPGGA
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);    // 1 Hz update rate
  GPS.sendCommand(PGCMD_ANTENNA);               // Check antenna status

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

void loop() {
  // Read wind-sensor lines
  char c = GPS.read();
  static String sentence;

  while (sensorSerial.available() > 0) {
    char incomingChar = sensorSerial.read();
    if (incomingChar == '\n') {
      parseMWVSentence(sentence);
      sentence = "";
    } else {
      sentence += incomingChar;
    }
  }

  // Read GPS data
  if (GPS.newNMEAreceived()) {
    if (GPS.parse(GPS.lastNMEA())) {
      // Print for debugging; also gather for LoRa
      printCoordinates();
    }
  }

  unsigned long now = millis();
  if (now - lastSendTime >= sendInterval) {
    lastSendTime = now;

    // Example: gather BME and GPS data in a single message
    float lat = convertNMEADegMinToDecDeg(GPS.latitude, GPS.lat);
    float lon = convertNMEADegMinToDecDeg(GPS.longitude, GPS.lon);
    float alt = GPS.altitude; // from Adafruit_GPS

    // If you have BME280:
    // float temperature = bme.readTemperature();
    // float humidity = bme.readHumidity();
    // float press = bme.readPressure() / 100.0F;

    // Compose a string for LoRa:
    // For example, just send lat/lon/alt. Adjust to your liking:
    String messageToSend = String("Lat:") + String(lat, 6) +
                           ",Lon:" + String(lon, 6) +
                           ",Alt:" + String(alt, 2);

    // Use your existing function or do it manually:
    sendMessage(messageToSend);
    // Then go back to listening (if you want half-duplex)
    // LoRa.receive();
  }
}

// Example for sending
void sendMessage(String outgoing) {
  // Start packet
  LoRa.beginPacket();
  // Optional: If you are doing addressing:
  LoRa.write(destination);
  LoRa.write(localAddress);
  LoRa.write(msgCount);
  LoRa.write(outgoing.length());

  // Send the text
  LoRa.print(outgoing);

  // Finish packet and actually transmit
  LoRa.endPacket();

  msgCount++;
  Serial.print("LoRa sent: ");
  Serial.println(outgoing);
}

// If you want to handle incoming LoRa data, re-enable this callback:
void onReceive(int packetSize) {
  if (packetSize == 0) return;

  int recipient = LoRa.read();
  byte sender = LoRa.read();
  byte incomingMsgId = LoRa.read();
  byte incomingLength = LoRa.read();

  String incoming = "";
  while (LoRa.available()) {
    incoming += (char)LoRa.read();
  }

  if (incomingLength != incoming.length()) {
    Serial.println("error: message length mismatch");
    return;
  }

  if (recipient != localAddress && recipient != 0xFF) {
    Serial.println("Not for me.");
    return;
  }

  Serial.print("LoRa Received from: 0x");
  Serial.println(sender, HEX);
  Serial.print("Sent to: 0x");
  Serial.println(recipient, HEX);
  Serial.print("Message ID: ");
  Serial.println(incomingMsgId);
  Serial.print("Message length: ");
  Serial.println(incomingLength);
  Serial.print("Message: ");
  Serial.println(incoming);
  Serial.print("RSSI: ");
  Serial.println(LoRa.packetRssi());
  Serial.print("Snr: ");
  Serial.println(LoRa.packetSnr());
  Serial.println();

  // Example: toggle LED if it matches "buttonPress"
  if (incoming.equals(buttonPress)) {
    rcvButtonState = !rcvButtonState;
  }
  digitalWrite(ledPin, rcvButtonState ? HIGH : LOW);
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

void parseMWVSentence(String nmea) {
  if (!nmea.startsWith("$") || !nmea.indexOf("MWV")) {
    return;
  }
  nmea.trim();

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

  if (fieldIndex < 3) return;

  float windAngle = fields[1].toFloat();
  float windSpeed = fields[3].toFloat();
  char unit = fields[4].charAt(0); // K, M, or N

  Serial.print("Wind Angle: ");
  Serial.println(windAngle, 1);
  Serial.print(" Wind Speed: ");
  Serial.println(windSpeed, 2);

  // If you also want to send the wind data over LoRa each time you parse it:
  //   String windMessage = String("Angle:") + String(windAngle) 
  //                       + ",Speed:" + String(windSpeed, 2);
  //   sendMessage(windMessage);
}
