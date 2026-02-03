// Definição dos Pinos e Cores
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
    // Lê o caractere enviado pelo Python
    char recebido = Serial.read();
    int n = recebido - '0'; // Converte ASCII para Inteiro

    // Verifica se o valor é válido (0 a 4)
    if (n >= 0 && n <= 4) {
      for (int i = 0; i < numLeds; i++) {
        if (i < n) {
          digitalWrite(leds[i], HIGH); // Liga os LEDs em sequência
        } else {
          digitalWrite(leds[i], LOW);  // Desliga o restante
        }
      }
    }
    
    // Limpeza de segurança do buffer
    while(Serial.available() > 0) Serial.read();
  }
}