#include <SPI.h>
#include <LoRa.h>

// Pin definitions
const int csPin = 5;
const int resetPin = 2;
const int irqPin = 26;

byte localAddress = 0xBB;
byte destination = 0xFF;

void setup() {
  Serial.begin(9600);

  LoRa.setPins(csPin, resetPin, irqPin);
  if (!LoRa.begin(915E6)) {
    Serial.println("Starting LoRa failed!");
    while (1);
  }

  // Start in 'idle' mode; parsePacket() will handle reading.
  // Don’t use LoRa.receive() or LoRa.onReceive() if you are using parsePacket().
}

void loop() {
  int packetSize = LoRa.parsePacket();
  if (packetSize > 0) {
    // Now read the first four bytes for address info
    int recipient = LoRa.read();    
    byte sender = LoRa.read();      
    byte incomingMsgId = LoRa.read();
    byte incomingLength = LoRa.read();

    // Read the rest of the data
    String incoming = "";
    while (LoRa.available()) {
      incoming += (char)LoRa.read();
    }

 
    // if (incomingLength != incoming.length()) {
    //   Serial.println("Error: message length does not match");
    //   return;
    // }
    // if (recipient != localAddress && recipient != 0xFF) {
    //   Serial.println("This message is not for me.");
    //   return;
    // }

    // Print info
    Serial.println("Message: " + incoming);
    Serial.println();
  }
}
