//CONFIG
char character;
int enablePin = 13; //enable/disable motor
int revPin = 7; //seting fwd/rev
int brakePin = 12; //brake pin
int speedPin = 5; //speedPin 
int voltagePin = A0;
int currentPin = A1;
int encoderPin = A5;

int inputV;
int inputI;
float systemVoltage; 
float systemCurrent;


char codeArray[5];
String input;
float encoderVoltage;
float scaledVoltage;
float realRpm;

String daqString;


void setup()
{
  TCCR0B = (TCCR0B & 0b11111000) | 0x01;

  //enabling pins & setting status to LOW
  pinMode(enablePin,OUTPUT); 
  pinMode(revPin,OUTPUT);  
  pinMode(brakePin,OUTPUT);
  pinMode(speedPin,OUTPUT);
  digitalWrite(enablePin,LOW);
  digitalWrite(revPin,LOW);
  digitalWrite(brakePin,LOW);
  analogWrite(speedPin,LOW);
  
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

void loop()
{
  
/* ============ READING AND PARSING THE INPUT STRING ==============*/
  if(Serial.available() > 0){    
      input = Serial.readString();
      input.toCharArray(codeArray,5);
  
  //Parsing the String into components
    char first = codeArray[0];
    char second = codeArray[1];
    char third = codeArray[2];
    char speedValue = codeArray[3];

/* =============== CONTROLLING THE PINS =================*/    
    //ENABLE PIN(13)
      if(first == '0'){ //enable pin
        digitalWrite(enablePin,LOW);
      }
      else if(first == '1'){
        digitalWrite(enablePin,HIGH);
      }
      else if(first != '1' & first != '0'){ //if the values are anything but a 0 or 1, then print error message
        Serial.println("ERROR: ENABLE MUST '0' or '1'");
      }
      
    //REVERSE PIN(7)
      if(second == '0'){ //enable pin
        digitalWrite(revPin,LOW);
      }
      else if(second == '1'){
        digitalWrite(revPin,HIGH);
      }
      else if(third != '1' & first != '0'){ //if the values are anything but a 0 or 1, then print error message
        Serial.println("ERROR: ENABLE MUST '0' or '1'");
      }
        
    //BRAKE PIN(12)
      if(third == '0'){ //enable pin
        digitalWrite(brakePin,HIGH); //NOTE BRAKE IS AN ACTIVE HIGH
      }
      else if(third == '1'){
        digitalWrite(brakePin,LOW); //BRAKE IS ACTIVE HIGH
      }
      else if(third != '1' && third != '0'){ //if the values are anything but a 0 or 1, then print error message
        Serial.println("ERROR: BRAKE MUST '0' or '1'");
      }
        
    //SPEED PIN(5)
      int dutyCycle = charToInt(speedValue) * 25.5;
      analogWrite(speedPin, dutyCycle); //sets up PWM on the speedPin
  }
/* ================= DATA AQUISITION ====================*/
//  READING FROM CURRENT AND VOLTAGE PINS ON AMMETER
  inputV = analogRead(voltagePin);
  inputI = analogRead(currentPin);
  systemVoltage = inputV/12.99; //conversion necessary for 90 Amp ammeter
  systemCurrent = inputI/7.4; //conversion necessary for 90 Amp ammeter
    
  //READING RPM VALUES
    encoderVoltage = analogRead(encoderPin)*.0049; // multiplier to return a value in Volts
    scaledVoltage = encoderVoltage - 2.5; // subtracting 2.5 to rezero scale 1to4V --> 1.5to1.5
    realRpm = (scaledVoltage * 1333.33)-134; // 1V from motor controller corresponds to -2000 RPM, 4V-->2000RPM
                                  //^^^^^^^^Added offset - seems to make data a little more accurate

    if(abs(realRpm) < 120.0){
      realRpm = 0.0; //arduino believes there is a small amount of motion even when stationary
      //this corrects the arduinos native offset, without affecting real data collection
    }
    

  daqString = String(realRpm) +","+ String(systemVoltage) +","+ String(systemCurrent);
  Serial.println(daqString);
  delay(75000);
    


    
  }
 
