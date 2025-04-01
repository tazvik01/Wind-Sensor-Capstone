#include <SPI.h>
#include <LoRa.h>


const int csPin = 5;
const int resetPin = 2;
const int irqPin = 26;

byte localAddress = 0xBB;
bool firstMessage = true;

void setup() {
  Serial.begin(9600);
  LoRa.setPins(csPin, resetPin, irqPin);
  if (!LoRa.begin(915E6)) {
    Serial.println("Starting LoRa failed!");
    while (1);
  }
  Serial.println("LoRa Receiver Started...");
}

void loop() {

  int packetSize = LoRa.parsePacket();
  if (packetSize > 0) {
    
    int recipient = LoRa.read();    
    byte sender = LoRa.read();      
    byte incomingMsgId = LoRa.read();
    byte incomingLength = LoRa.read();

  
    String incoming = "";
    while (LoRa.available()) {
      incoming += (char)LoRa.read();
    }

   

    if (firstMessage) {
      Serial.print("Device 0x");
      Serial.print(sender, HEX);
      Serial.print(": ");
      Serial.print(incoming);
      firstMessage = false;
    } else {
      Serial.print(" | Device 0x");
      Serial.print(sender, HEX);
      Serial.print(": ");
      Serial.print(incoming);

      Serial.println();
      firstMessage = true;
      
    }

    

  }

}