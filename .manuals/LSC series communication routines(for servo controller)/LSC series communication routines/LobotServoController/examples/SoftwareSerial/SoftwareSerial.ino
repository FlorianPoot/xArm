#include "LobotServoController.h"

#define rxPin 10
#define txPin 11

SoftwareSerial mySerial(rxPin, txPin);
LobotServoController myse(mySerial);   

void setup() {
  pinMode(13,OUTPUT);
  Serial.begin(9600);
  
  mySerial.begin(9600);  //opens software serial port, sets data rate to 9600 bps
  Serial.begin(9600);
  digitalWrite(13,HIGH);

  myse.moveServos(5,1000,0,1300,2,700,4,600,6,900,8,790); 
  //Control 5 servos, action time is 1000ms, move No.0 servo to 1300 position, move No.2 servo to 700 position, move No.4 servo to 600 position
  //Move No.6 servo to 900 position, move No.8 servo to 790 position
  delay(2000);

  LobotServo servos[2];   //an array of struct LobotServo
  servos[0].ID = 2;       //No.2 servo
  servos[0].Position = 1400;  //1400 position
  servos[1].ID = 4;          //No.4 servo
  servos[1].Position = 700;  //700 position
  myse.moveServos(servos,2,1000);  //control 2 servos, action time is 1000ms, ID and position are specified by the structure array "servos"
}

void loop() {
  if (Serial.available()) {
    String data = Serial.readString();
    mySerial.print(data);
  }
}
