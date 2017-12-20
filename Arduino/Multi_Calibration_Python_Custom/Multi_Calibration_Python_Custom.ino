#include <OneWire.h>
#include <DallasTemperature.h>

#include <SPI.h>
#include <SD.h>

unsigned long timeSince;

int boxToRead;

const int R2 = 10000;
const int numberOfReadings = 25;
const int sensorArrayLength = 3;

// Controlling Sensor
const int sensorPin = 3;

// Theta Probe
const int readPin = 9;
const int transistorON = 6;
const int thetaPin = A1;
float voltage = 0;

//celsius
const float maxRoomTemp = 27.0;
const float higherReadingTemp = 20.5;
const float lowerReadingTemp = 19.5;

//millis
const int waitToReadTime = 45000;
const int refreshTime = 1000;

const int readLed = 8;

//lets program know we can read data
bool canRead = false;

//Temp Sensor Init
OneWire oneWire(7);
DallasTemperature tempSensor(&oneWire);

void setup() {

  // Set theta probe read pin
  pinMode(readPin,OUTPUT);
  digitalWrite(readPin,LOW);

    //set sensor read pin
  pinMode(sensorPin,OUTPUT);
  digitalWrite(sensorPin,LOW);

  pinMode(transistorON,OUTPUT);
  digitalWrite(transistorON,LOW);

  //begin clocking program time
  timeSince = millis();

  //set Error Pin
  pinMode(readLed,OUTPUT);
  digitalWrite(readLed,LOW);

  //open serial communications 
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  //start the temperature sensors and setup LED pins
  tempSensor.begin();

}
void loop() {

  float tempValue = getTemperature();

  while(tempValue == -196.00 || tempValue == 185.00 || tempValue == -127.00){
    digitalWrite(readLed,HIGH);
    delay(250);
    digitalWrite(readLed,LOW);
    delay(250);
    tempValue = getTemperature();
   
  }

  if (Serial.available() > 0) {
    set_sensor_state(int(Serial.read()));
  }

  displayData();
  
  delay(refreshTime);

}

void displayData(){

//  int adcValue = 0; //R2 ADC
//    
//  for(int i=0;i<numberOfReadings;i++){
//      adcValue += analogRead(A0);
//      delay(25);
//  }
//
//  int meanAdc = adcValue / numberOfReadings;

  int meanAdc = readSensor();

  float voltage = meanAdc * 5.0 / 1023.0; //Resistor Voltage
  float resistance = R2 * (5.0 / voltage - 1.0); //Sensor Resistance
  
  //Serial.println("Sensor0");
  Serial.println("ADC: " + String(meanAdc));
  Serial.println("Voltage: " + String(voltage));
  Serial.println("Resistance: " + String(resistance));
  Serial.println("Temperature: " + String(getTemperature()) + " C");

  float mV = readThetaProbe();
  Serial.println("Theta Probe: " + String(mV));
  
  delay(25);
}

float readThetaProbe(){

  if(canRead){
    digitalWrite(transistorON,HIGH);
    digitalWrite(readPin,HIGH);
    
    delay(100);
    int a1 = analogRead(thetaPin);
    voltage = a1 * (5.0 / 1023);
    float millivolts = 1000 * voltage;
    
    digitalWrite(readPin,LOW);
    digitalWrite(transistorON,LOW);
    delay(100);
    
    return millivolts;
  }else{
    return 0.0;
  }

}

int readSensor(){

  if(canRead){

    digitalWrite(sensorPin,HIGH);
    delay(100);
    int adcValue = 0; //R2 ADC
    
    for(int i=0;i<numberOfReadings;i++){
      adcValue += analogRead(A0);
      delay(25);
    }

    digitalWrite(sensorPin,LOW);
    delay(100);

    return (adcValue / numberOfReadings);
  }else{
    return 0;
  }

  
}

float getTemperature(){
  float currentTemp;
  tempSensor.requestTemperatures();
  currentTemp = tempSensor.getTempCByIndex(0);
  //Serial.println("Temperature: " + String(currentTemp) + "C");
  return currentTemp;
 
}

void set_sensor_state(int state)
{
  if (state == 48) {
    digitalWrite(readLed,LOW);
    //digitalWrite(sensorPin,LOW);
    canRead = false;
  }

  else if(state == 49) {
    digitalWrite(readLed,HIGH);
    //digitalWrite(sensorPin,HIGH);
    canRead = true;
  }
}

