#include <SoftwareSerial.h>

SoftwareSerial mySerial(10,11,true); // RX, TX

void setup()
{
  // Open serial communications and wait for port to open:
  Serial.begin(9600);
  // set the data rate for the SoftwareSerial port
  mySerial.begin(9600);
}

void loop() // run over and over
{
  if (mySerial.available()) {
    char input = mySerial.read();
    Serial.print(input);
  }


}
