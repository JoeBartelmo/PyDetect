/*
 |||| CONFIG ||||
 */
//double clockCorrection = 64.0; (depreciated)
 
//Motor
int enablePin = 13; //enable/disable motor
int revPin = 11; //seting fwd/rev
int brakePin = 12; //brake pin
int speedPin = 5; //speedPin 
int voltagePin = A0; //ammeter voltage pin
int currentPin = A1; //ammeter current pin
int encoderPin = A5; //pin for motor controller
int speedDutyCycle; // duty cycle for speed PWM
char enable; //enable character in motor control code
char reverse; //direction character in motor control 
char brake; //brake character in motor control 
char speedValue; //speed character in motor control 
String input; //user input string
char codeArray[8]; //input string turned into an array
float encoderVoltage; //voltage coming off the encoder
float scaledVoltage; //scaled enoder voltage
float realRpm; //computed rpm coming off the encoder

//LEDS
int ledPin = 10;
int ledDutyCycle;
char ledValue;


//IRdistance sensors
int frontIrPin = A3;
int backIrPin = A4;
String distance;
String outputFrontDistance = "out of range";
String outputBackDistance = "out of range";
int numSamples = 10;

//Ammeter
double inputV;
double inputI;
double systemVoltage; 
double systemCurrent;
String daqString;





void setup() {
  //modifies registries to increase PWM frequency
  TCCR0B = (TCCR0B & 0b11111000) | 0x01;

  //enabling pins & setting status to LOW
  
   //Motor Control
  pinMode(enablePin,OUTPUT); 
  pinMode(revPin,OUTPUT);  
  pinMode(brakePin,OUTPUT);
  pinMode(speedPin,OUTPUT);
  digitalWrite(enablePin,LOW);
  digitalWrite(revPin,LOW);
  digitalWrite(brakePin,LOW);
  analogWrite(speedPin,LOW);
  
  //LEDS
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);

 
 //enabling the serial connection
  Serial.begin(9600);

}

int charToInt(char c)
{
  int o;

  if (c == '0')
  { o = 0; }
  else if (c == '1')
  { o = 1; }
  else if (c == '2')
  { o = 2; }
  else if (c == '3')
  { o = 3; }
  else if (c == '4')
  { o = 4;}
  else if (c == '5')
  { o = 5; }
  else if (c == '6')
  { o = 6; }
  else if (c == '7')
  { o = 7;}
  else if (c == '8')
  { o = 8;}
  else if (c == '9')
  { o = 9; }

  return o;
}

String ir_distance(int irPin)
{
  int sampleSum = 0;
  
  for (int i=0; i<numSamples; i++)
  {
   int distanceVoltage = analogRead(irPin);
   sampleSum = sampleSum + distanceVoltage;
   delay(60*64);
  }
  
  float avgVoltage = (float)sampleSum/(float)numSamples/205.0; // average divided by numSamples to average, then divided by 205 to convert to voltage
  if(avgVoltage > 2.5)
  { 
  distance = "0";
  }
  
  else if(avgVoltage < 1.4)
  {
  distance = "out of range";
  }
  else
  {
  distance = (String)(1011.6*.01*pow(avgVoltage,-2.621));
  } 
  return distance;
}


void control_input(String input)
{
      input = Serial.readString();
      input.toCharArray(codeArray,6);

       //Parsing the String into components
    char first = codeArray[0];

    /*======================= Command interpretation =====================*/
    
   /*_____________BEGIN MOTOR CONDITIONAL___________ */
    switch(first){
      case 'M':{
        enable = codeArray[1];
        reverse = codeArray[2];
        brake = codeArray[3];
        speedValue = codeArray[4];

      /* ========== CONTROLLING THE PINS ==========*/    
      //ENABLE PIN(13)
        if(enable == '0'){ //enable pin
          digitalWrite(enablePin,LOW);
        }
        else if(enable == '1'){
          digitalWrite(enablePin,HIGH);
        }
        else if(enable != '1' & enable != '0'){ //if the values are anything but a 0 or 1, then print error message
//          Serial.println("ERROR: ENABLE MUST '0' or '1'");
        }
        
      //REVERSE PIN(7)
        if(reverse == '0'){ //rev pin
          digitalWrite(revPin,LOW);
        }
        else if(reverse == '1'){
          digitalWrite(revPin,HIGH);
        }
        else if(reverse != '1' & reverse!= '0'){ //if the values are anything but a 0 or 1, then print error message
//          Serial.println("ERROR: ENABLE MUST '0' or '1'");
        }
          
      //BRAKE PIN(12)
        if(brake == '0'){ //brake pin
          digitalWrite(brakePin,HIGH); //NOTE BRAKE IS AN ACTIVE HIGH
        }
        else if(brake == '1'){
          digitalWrite(brakePin,LOW); //BRAKE IS ACTIVE HIGH
        }
        else if(brake != '1' && brake != '0'){ //if the values are anything but a 0 or 1, then print error message
//          Serial.println("ERROR: BRAKE MUST '0' or '1'");
        }
          
      //SPEED PIN(5)
        speedDutyCycle = charToInt(speedValue) * 25.5; //converts input ao a 0-255 scale
        analogWrite(speedPin, speedDutyCycle); //sets up PWM on the speedPin
    
      break;
      }
  /*_________END MOTOR CONDITIONAL______ */

/*_______________BEGIN LED CONDITIONAL______________*/
      
      case 'L':{
       ledValue = codeArray[1];
       ledDutyCycle = charToInt(ledValue) * 25.5;
       analogWrite(ledPin, ledDutyCycle); //sets up PWM on the speedPin
       break;
      }

/*____________END LED CONDITIONAL____________*/
      }
}
     

void daq()
{ 
  //  READING FROM CURRENT AND VOLTAGE PINS ON AMMETER
        inputV = analogRead(voltagePin);
        inputI = analogRead(currentPin);
        systemVoltage = (float)inputV/12.99; //conversion necessary for 90 Amp ammeter
        systemCurrent = (float)inputI/7.4; //conversion necessary for 90 Amp ammeter
          
        //READING RPM VALUES
          encoderVoltage = analogRead(encoderPin)*.0049; // multiplier to return a value in Volts
          scaledVoltage = encoderVoltage - 2.5; // subtracting 2.5 to rezero scale 1to4V --> -1.5to1.5
          realRpm = (scaledVoltage * 1333.33)-84.0; // 1V from motor controller corresponds to -2000 RPM, 4V-->2000RPM
                                        //^^^^^^^^Added offset - seems to make data a little more accurate
      

}


void save_and_send()
{
    daqString = String(realRpm) +","+ String(systemVoltage) +","+ String(systemCurrent) + "," + String(outputFrontDistance)+","+String(outputBackDistance);
    Serial.println(daqString);
}


void increase_accuracy()
{
//correcting noise in RPM
    if(abs(realRpm) < 75.0)
    {
    realRpm = 0.0; //arduino believes there is a small amount of motion even when stationary
    //this corrects the arduinos native offset, without affecting real data collection
    }    
  
}

void loop() {
  if(Serial.available() > 0)
  {
    control_input(input);      
  }
  outputFrontDistance = ir_distance(frontIrPin);
  outputBackDistance = ir_distance(backIrPin);
  daq();
  increase_accuracy();
  save_and_send(); 
  delay(32000);
}
