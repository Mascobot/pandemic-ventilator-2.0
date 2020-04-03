
#include <Wire.h> // I2C library
// Outputs:
int epr1 = 3;// PWM for Electronic Pressure Regulator 1 - Air 
int epr2 = 5;// PWM for Electronic Pressure Regulator 2 - Oxygen
int buzzer = 6;// PWM for Buzzer
int ev1 = 2;// Electric Valve 1
int ev2 = 4;// Electric Valve 2
int address_flow_sensor = 73; // (0x49)


// Inputs:
int power_reference = A4;//Power detection
int sensor_a = A0;// Pressure of tank 
int sensor_epr1 = A1;// Pressure sensor on Electronic Pressure Regulator 1 - Air
int sensor_epr2 = A2; // Pressure sensor on Electronic Pressure Regulator 2 - Oxygen
int sensor_b = A3;// Input pressure 
int sensor_c = A5;// Pressure sensor on exhalation 

//Variables
int start_var = 0;
bool stringComplete = false; 
int flow_meter_read = 0;

//Variables fro receiving data from USB:
String inputString = ""; 
String temp = "";
String volumeString = "";
String breathString = "";
String peepString = "";
String ratioString = "";
String oxygenString = "";
String alarmString = "";
String temp_string = "";

//Variables for setting outputs:
int epr1_presssure = 0;
int epr2_presssure = 0;

//Misc Variables:
int a = 0;
int volume = 0;
int breath = 12;
int peep = 5;
int ratio = 1;
int oxygen = 21;
int alarm = 30;
int lenght = 0;

void setup() {
  // Declare pins an OUTPUT:
  pinMode(epr1, OUTPUT);
  pinMode(epr2, OUTPUT);
  pinMode(buzzer, OUTPUT);
  pinMode(ev1, OUTPUT);
  pinMode(ev2, OUTPUT);

  

  // Declare pins an INPUT:
  pinMode(power_reference, INPUT);//Power detection
  pinMode(sensor_a, INPUT);//Air pressure in Tank 
  pinMode(sensor_epr1, INPUT);//Air pressure
  pinMode(sensor_epr2, INPUT);//Oxygen pressure
  pinMode(sensor_b, INPUT);//Input pressure
  pinMode(sensor_c, INPUT);//Exhale pressure

  digitalWrite(ev1, LOW); //Close Valve 1
  digitalWrite(ev2, HIGH); //Open Valve 2
 

  // Comm setup:
  Wire.begin();// join i2c bus (address optional for master)
  Serial.begin(9600);// start Serial for output
  //incoming_data.reserve(200);


}



//Main program
void loop() {
  Serial.print("-O:");//ERP1 Reading
  Serial.print(analogRead(sensor_epr1));
  Serial.print(",");
  Serial.print("-T:");//ERP2 Reading
  Serial.print(analogRead(sensor_epr2));
  Serial.print(",");
  Serial.print("-A:");//Sensor A reading
  Serial.print(((analogRead(sensor_a))-40)/2.58);
  Serial.print("-B:");//Sensor B reading
  Serial.print(analogRead(sensor_b));
  Serial.print("-C:");//Sensor C reading
  Serial.print(analogRead(sensor_c));
  Serial.print("-F:");//Flow reading
  Serial.print(flow_meter_read);
  Serial.print("-P:");//Power reference (to detect if power goes down).
  Serial.print(analogRead(power_reference));
  Serial.println(",");

  
  serialEvent();
 if (stringComplete) {
    
    temp = inputString.charAt(0); 
    lenght = inputString.length();
    volumeString ="";
    breathString = "";
    peepString = "";
    ratioString = "";
    oxygenString = "";
    alarmString = "";
    
    if (temp == "v") {
      for (int i = 1; i <= lenght; i = i + 1){
        temp_string = inputString.charAt(i);
        volumeString += temp_string;
      }
      volume = volumeString.toInt();  
      Serial.println(volume);
    }
    else if (temp == "b") {
      for (int i = 1; i <= lenght; i = i + 1){
        temp_string = inputString.charAt(i);
        breathString += temp_string;
      }
      breath = breathString.toInt();  
      Serial.println(breath);
    }
    else if (temp == "p") {
      for (int i = 1; i <= lenght; i = i + 1){
        temp_string = inputString.charAt(i);
        peepString += temp_string;
      }
      peep = peepString.toInt();  
      Serial.println(peep);
    }
     else if (temp == "o") {
      for (int i = 1; i <= lenght; i = i + 1){
        temp_string = inputString.charAt(i);
        oxygenString += temp_string;
      }
      oxygen = oxygenString.toInt();  
      Serial.println(oxygen);
    }
    else if (temp == "r") {
      for (int i = 1; i <= lenght; i = i + 1){
        temp_string = inputString.charAt(i);
        ratioString += temp_string;
      }
      ratio = ratioString.toInt();  
      Serial.println(ratio);
    }
    else if (temp == "a") {
      for (int i = 1; i <= lenght; i = i + 1){
        temp_string = inputString.charAt(i);
        alarmString += temp_string;
      }
      alarm = alarmString.toInt();  
      Serial.println(alarm);
    }    
    // clear the string:
    inputString = "";
    stringComplete = false;
    
 
  }

  digitalWrite(ev1, HIGH); //Open Valve 1
  digitalWrite(ev2, LOW); //Close Valve 2 
  analogWrite(epr1, volume);  
  int time_ratio = (((60/breath)/(1+ratio))*60)/2.85;
  for (int bal = 0; bal < time_ratio; bal = bal + 1) {
    Serial.print("-O:");//ERP1 Reading
    Serial.print(analogRead(sensor_epr1));
    Serial.print(",");
    Serial.print("-T:");//ERP2 Reading
    Serial.print(analogRead(sensor_epr2));
    Serial.print(",");
    Serial.print("-A:");//Sensor A reading
     Serial.print(((analogRead(sensor_a))-40)/2.58);
    Serial.print("-B:");//Sensor B reading
    Serial.print(analogRead(sensor_b));
    Serial.print("-C:");//Sensor C reading
    Serial.print(analogRead(sensor_c));
    Serial.print("-F:");//Flow reading
    Serial.print(flow_meter_read);
    Serial.print("-P:");//Power reference (to detect if power goes down).
    Serial.print(analogRead(power_reference));
    Serial.println(",");
    serialEvent();
    delay(1);
    
  }
  analogWrite(epr1, 0);  
  digitalWrite(ev2, HIGH); //Open Valve 2 
    int comp = time_ratio*ratio;
    for (int dela = 0; dela < comp; dela = dela + 1) {
    Serial.print("-O:");//ERP1 Reading
    Serial.print(analogRead(sensor_epr1));
    Serial.print(",");
    Serial.print("-T:");//ERP2 Reading
    Serial.print(analogRead(sensor_epr2));
    Serial.print(",");
    Serial.print("-A:");//Sensor A reading
     Serial.print(((analogRead(sensor_a))-40)/2.58);
    Serial.print("-B:");//Sensor B reading
    Serial.print(analogRead(sensor_b));
    Serial.print("-C:");//Sensor C reading
    Serial.print(analogRead(sensor_c));
    Serial.print("-F:");//Flow reading
    Serial.print(flow_meter_read);
    Serial.print("-P:");//Power reference (to detect if power goes down).
    Serial.print(analogRead(power_reference));
    Serial.println(",");
    serialEvent();
    delay(1);
    
  }
 }
  

  


void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    inputString += inChar;
    // if the incoming character is a newline, set a flag so the main loop can
    // do something about it:
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}


int read_flow(int address) {
  //start the communication with IC with the address 73
  Wire.beginTransmission(address); 
  //send a bit and ask for register zero
  Wire.write(0);
  //end transmission
  Wire.endTransmission();
  //request 1 byte from address 73
  Wire.requestFrom(address, 1);
  //wait for response
  while(Wire.available() == 0);
  //put the temperature in variable c
  int cs = Wire.read();   
  return cs;
}

  
  


  
