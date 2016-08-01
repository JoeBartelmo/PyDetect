#include "MemoryFree.h"
#include "DaqTelemetry.h"

//Defined as a global for memory 
DaqTelemetry *daqTelemetry;

//Motor
int enablePin = 13; //enable/disable motor
int revPin = 11; //seting fwd/rev
int brakePin = 12; //brake pin
int speedPin = 9; //speedPin
int voltagePin = A0; //ammeter voltage pin
int currentPin = A1; //ammeter current pin
int encoderPin = A5; //pin for motor controller

//LEDS
int ledPin = 10;

//IRdistance sensors
int frontIrPin = A3;
int backIrPin = A4;
int numSamples = 10;



void setup() {
  //modifies registries to increase PWM frequency
  TCCR1B = (TCCR1B & 0b11111000) | 0x01;

  //enabling pins & setting status to LOW

  //Motor Control
  pinMode(enablePin, OUTPUT);
  pinMode(revPin, OUTPUT);
  pinMode(brakePin, OUTPUT);
  pinMode(speedPin, OUTPUT);
  digitalWrite(enablePin, LOW);
  digitalWrite(revPin, LOW);
  digitalWrite(brakePin, LOW);
  analogWrite(speedPin, LOW);

  //LEDS
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);

  //enabling the serial connection
  Serial.begin(9600);
}

/**
   Quick conversion that relies on the offset of the character '0'

   @param c: character to be encoded
*/
int charToInt(char c) {
  return c - '0';
}

/**
   Computes the distance from "WALL-E" (a distance sensor)

   @param irPin: The pin at which to access the distance sensor
*/
double ir_distance(int irPin)
{
  int sampleSum = 0;

  for (int index = 0; index < numSamples; index++)
  {
    int distanceVoltage = analogRead(irPin);
    sampleSum += distanceVoltage;
    delay(60);
  }

  // average divided by numSamples to average, then divided by 205 to convert to voltage
  float avgVoltage = ((float) sampleSum / (float) numSamples) / 205.0;
  double distance = -1;

  if (avgVoltage > 2.5) {
    distance = 0;
  }
  else if (avgVoltage < 1.4) {
    distance = -1;
  }
  else {
    // These coefficents are not subject to change, and have no offical name
    // To obtain these values we regressed using a table of Distance vs Voltage
    distance = (double)(1011.6 * .01 * pow(avgVoltage, -2.621));
  }
  return distance;
}

/**
   Reads a string from serial input and parses based off of our format
   specified in our documentation, then executes given command.
*/
void control_input()
{
  String input = Serial.readString();
  char codeArray[8]; //input string turned into an array
  input.toCharArray(codeArray, 6);

  //First character defines what type of command
  char first = codeArray[0];

  switch (first) {
    //Motor code
    case 'M': {
        char enable = codeArray[1] == '0' ? LOW : HIGH;
        char reverse = codeArray[2] == '0' ? LOW : HIGH;
        char brake = codeArray[3] == '1' ? LOW : HIGH;
        char speedValue = codeArray[4];

        digitalWrite(enablePin, enable); //ENABLE PIN(13)
        digitalWrite(revPin, reverse); //REVERSE PIN(7)
        digitalWrite(brakePin, brake); //NOTE BRAKE IS AN ACTIVE HIGH BRAKE PIN(12)

        //SPEED PIN(5)
        int speedDutyCycle = charToInt(speedValue) * 25.5; //converts input ao a 0-255 scale
        analogWrite(speedPin, speedDutyCycle); //sets up PWM on the speedPin
        break;
      }
    //LED code
    case 'L': {
        char ledValue = codeArray[1];
        char ledDutyCycle = charToInt(ledValue) * 25.5;
        analogWrite(ledPin, ledDutyCycle); //sets up PWM on the speedPin
        break;
      }
  }
}

/**
   Generates a DaqTelemetry object
*/
DaqTelemetry* daq(double frontDistance, double backDistance)
{
  daqTelemetry = new DaqTelemetry();

  //  READING FROM CURRENT AND VOLTAGE PINS ON AMMETER
  double inputV = analogRead(voltagePin);
  double inputI = analogRead(currentPin);

  // multiplier to return a value in Volts
  double encoderVoltage = analogRead(encoderPin) * .0049;
  // subtracting 2.5 to rezero scale 1to4V --> -1.5to1.5
  double scaledVoltage = encoderVoltage - 2.5;
  // 1V from motor controller corresponds to -2000 RPM, 4V-->2000RPM
  daqTelemetry->systemRpm = (scaledVoltage * 1333.33);
  //conversion necessary for 90 Amp ammeter
  daqTelemetry->systemVoltage = inputV / 12.99;
  //conversion necessary for 90 Amp ammeter
  daqTelemetry->systemCurrent = inputI / 7.4;

  //Copy over
  daqTelemetry->frontDistance = frontDistance;
  daqTelemetry->backDistance = backDistance;

  return daqTelemetry;
}

/**
   Send daqTelemtry data over the serial
*/

String distance_to_string(double distance){
  String outputDistance = (String)distance;
    
  if(outputDistance == "-1") {
     outputDistance = "out of range";
  }
  return outputDistance;
}


void save_and_send(DaqTelemetry *daqTelemetry)
{
  String outputFrontDistance = distance_to_string(daqTelemetry->frontDistance);
  String outputBackDistance = distance_to_string(daqTelemetry->backDistance);
  
  String daqString = String(daqTelemetry->systemRpm) + "," +
                     String(daqTelemetry->systemVoltage) + "," +
                     String(daqTelemetry->systemCurrent) + "," +
                     String(outputFrontDistance) + "," +
                     String(outputBackDistance);
  Serial.println(daqString);
}

/**
   TBD
*/
void increase_accuracy(DaqTelemetry *daqTelemetry)
{
  //arduino believes there is a small amount of motion even when stationary
  //this corrects the arduinos native offset, without affecting real data collection
  if (abs(daqTelemetry->systemRpm) < 75.0) {
    daqTelemetry->systemRpm = 0.0; //arduino believes there is a small amount of motion even when stationary
  }

}

void loop() {
  if (Serial.available() > 0) {
    control_input();
  }
  //Solve serial buffer problem
  Serial.print('\0');
  daqTelemetry = daq(ir_distance(frontIrPin), ir_distance(backIrPin));
  increase_accuracy(daqTelemetry);
  save_and_send(daqTelemetry);
  delete daqTelemetry;
  //Serial.print("freeMemory()=");
  //Serial.println(freeMemory());
}

