int HeatingCoolingState;

const int heatLED = 12;
const int coolLED = 6;

const int coolRelay = 8; // label=C, relay=k2
const int heatRelay1 = 9; // label=H1 relay=k4
const int heatRelay2 = 10; // label=H2, relay=k1

void setup() {
  // put your setup code here, to run once:

  digitalWrite(coolRelay,LOW);
  digitalWrite(heatRelay1,LOW);
  digitalWrite(heatRelay2,LOW);

  pinMode(heatLED,OUTPUT);
  pinMode(coolLED,OUTPUT);

  pinMode(coolRelay,OUTPUT);
  pinMode(heatRelay1,OUTPUT);
  pinMode(heatRelay2,OUTPUT);

  digitalWrite(heatLED,LOW);
  digitalWrite(coolLED,LOW);

  digitalWrite(coolRelay,HIGH);
  digitalWrite(heatRelay1,HIGH);
  digitalWrite(heatRelay2,HIGH);

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
    digitalWrite(heatRelay1,LOW);
    digitalWrite(heatRelay2,LOW);

  }

  else if(state == 49) {
    digitalWrite(heatLED,LOW);
    digitalWrite(coolLED,HIGH);

    digitalWrite(heatRelay1,HIGH);
    digitalWrite(heatRelay2,HIGH);
    digitalWrite(coolRelay,LOW);
    
  }

  else if (state == 50) {
    digitalWrite(heatLED,LOW);
    digitalWrite(coolLED,LOW);

    digitalWrite(heatRelay1,HIGH);
    digitalWrite(heatRelay2,HIGH);
    digitalWrite(coolRelay,HIGH);
  }
}

