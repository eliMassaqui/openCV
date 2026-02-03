const int ledVerde    = 9;
const int ledAzul     = 10;
const int ledVermelho = 11;
const int ledAmarelo  = 12;

int leds[] = {ledVerde, ledAzul, ledVermelho, ledAmarelo};
int numLeds = 4;

void setup() {
  Serial.begin(9600);
  for (int i = 0; i < numLeds; i++) {
    pinMode(leds[i], OUTPUT);
    digitalWrite(leds[i], LOW);
  }
}

void loop() {
  if (Serial.available() > 0) {
    char recebido = Serial.read();
    int n = recebido - '0';

    if (n >= 0 && n <= 4) {
      for (int i = 0; i < numLeds; i++) {
        digitalWrite(leds[i], i < n ? HIGH : LOW);
      }
    }

    while (Serial.available() > 0) Serial.read();
  }
}
