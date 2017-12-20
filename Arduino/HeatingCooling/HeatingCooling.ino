int HeatingCoolingState;

const int heatLED = 12;
const int coolLED = 6;

const int coolRelay = 8;
const int heatRelay = 9;

void setup() {
  // put your setup code here, to run once:

  digitalWrite(coolRelay,LOW);
  digitalWrite(heatRelay,LOW);

  pinMode(heatLED,OUTPUT);
  pinMode(coolLED,OUTPUT);

  pinMode(coolRelay,OUTPUT);
  pinMode(heatRelay,OUTPUT);

  digitalWrite(heatLED,LOW);
  digitalWrite(coolLED,LOW);

  digitalWrite(coolRelay,HIGH);
  digitalWrite(heatRelay,HIGH);

  Serial.begin(9600);

  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    HeatingCoolingState = Serial.read();
    Serial.println(HeatingCoolingState);
    set_state(int(HeatingCoolingState));
  }
  

}

void set_state(int state)
{
  Serial.println(state);
  if (state == 48) {
    
    digitalWrite(coolLED,LOW);
    digitalWrite(heatLED,HIGH);
    
    digitalWrite(coolRelay,HIGH);
    digitalWrite(heatRelay,LOW);

  }

  else if(state == 49) {
    digitalWrite(heatLED,LOW);
    digitalWrite(coolLED,HIGH);

    digitalWrite(heatRelay,HIGH);
    digitalWrite(coolRelay,LOW);
    
  }

  else if (state == 50) {
    digitalWrite(heatLED,LOW);
    digitalWrite(coolLED,LOW);

    digitalWrite(heatRelay,HIGH);
    digitalWrite(coolRelay,HIGH);
  }
}

