/*
  Secretario Mudo IoT - ESP32

  MAPA DE PINES
  LCD I2C  : SDA=21  SCL=22  VCC=VIN(5V)  GND
  DHT11    : DATA=4  VCC=3V3  GND
  LDR      : divisor (LDR + resistor 10k a GND) -> punto medio a GPIO34, extremo a 3V3
  LED RGB  : R=25  G=26  B=27  (cada uno con resistor 220 ohm; GND comun)
  Encoder  : CLK=18  DT=19  SW=5  (+ a 3V3, GND)
  Buzzer   : GPIO23 (buzzer activo) y GND
*/
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>
#include <WiFi.h>
#include <time.h>

// ---------- WiFi / NTP ----------
const char* WIFI_SSID = "Bukatoria";
const char* WIFI_PASS = "diego123";
const long  GMT_OFFSET_SEG = -6 * 3600;   // Costa Rica UTC-6
const int   DST_OFFSET_SEG = 0;           // sin horario de verano

// ---------- Pines ----------
const int pinSDA = 21, pinSCL = 22;
#define DHTPIN 4
#define DHTTYPE DHT11
const int pinLDR = 34;                    // ADC1 (no usar pines ADC2 con WiFi)
const int pinRojo = 25, pinVerde = 26, pinAzul = 27;
const int pinCLK = 18, pinDT = 19, pinSW = 5;
const int pinBuzzer = 23;

// ---------- Objetos ----------
DHT dht(DHTPIN, DHTTYPE);
LiquidCrystal_I2C lcd(0x27, 16, 2);       // usa 0x3F si no enciende

// ---------- Pomodoro ----------
enum Estado { REPOSO, FOCO, DESCANSO };
Estado estado = REPOSO;

const int  presets[] = {15, 25, 45};      // minutos de trabajo
const int  numPresets = 3;
int        idxPreset = 1;                 // arranca en 25 min
const int  minutosDescanso = 5;

unsigned long inicioFase = 0;
unsigned long duracionFase = 0;           // en ms

// ---------- Alertas ambientales (LED azul en reposo) ----------
const float TEMP_MAX = 30.0;
const float HUM_MIN = 30.0, HUM_MAX = 70.0;

// ---------- Sensores ----------
float temperatura = NAN, humedad = NAN;
unsigned long ultimoDHT = 0;
const unsigned long intervaloDHT = 2000;

// ---------- LDR / brillo ----------
const float brilloMinimo = 0.05;
const float umbralInf = 0.30, umbralSup = 0.50;
const float suavizado = 0.15;
int luzMin = 300, luzMax = 3500;          // ajusta viendo el Serial
float brilloActual = 1.0;
unsigned long ultimoLED = 0;
const unsigned long intervaloLED = 20;

// ---------- Encoder / boton ----------
int ultimoEstadoCLK;
unsigned long ultimoBoton = 0;
const unsigned long tiempoDebounce = 250;

// ---------- Pantalla ----------
unsigned long ultimoLCD = 0;
const unsigned long intervaloLCD = 250;

// ---------- Buzzer sin bloqueo ----------
int beepRestantes = 0;
bool beepOn = false;
unsigned long ultimoBeep = 0;
unsigned long beepDurOn = 100, beepDurOff = 100;

void iniciarBeep(int veces, unsigned long durOn, unsigned long durOff) {
  beepRestantes = veces;
  beepDurOn = durOn;
  beepDurOff = durOff;
  beepOn = false;
  ultimoBeep = millis() - durOff;         // suena de inmediato
}

void actualizarBuzzer() {
  if (beepRestantes <= 0) { digitalWrite(pinBuzzer, LOW); return; }
  unsigned long ahora = millis();
  if (!beepOn && ahora - ultimoBeep >= beepDurOff) {
    digitalWrite(pinBuzzer, HIGH);
    beepOn = true;
    ultimoBeep = ahora;
  } else if (beepOn && ahora - ultimoBeep >= beepDurOn) {
    digitalWrite(pinBuzzer, LOW);
    beepOn = false;
    beepRestantes--;
    ultimoBeep = ahora;
  }
}

// ---------- LDR ----------
int leerLuz() {
  long suma = 0;
  for (int i = 0; i < 10; i++) suma += analogRead(pinLDR);   // promedio de 10 lecturas
  return suma / 10;
}

float nivelLuz(int luz) {
  int span = max(luzMax - luzMin, 1);
  return constrain((luz - luzMin) / (float)span, 0.0, 1.0);
}

float pasoSuave(float a, float b, float x) {
  float t = constrain((x - a) / (b - a), 0.0, 1.0);
  return t * t * (3 - 2 * t);
}

// ---------- LED RGB ----------
bool hayAlertaAmbiental() {
  if (isnan(temperatura) || isnan(humedad)) return false;
  return temperatura > TEMP_MAX || humedad < HUM_MIN || humedad > HUM_MAX;
}

void actualizarLED() {
  if (millis() - ultimoLED < intervaloLED) return;
  ultimoLED = millis();

  int cr = 0, cg = 0, cb = 0;
  switch (estado) {
    case FOCO:     cg = 255; break;                 // verde
    case DESCANSO: cr = 255; break;                 // rojo
    case REPOSO:   if (hayAlertaAmbiental()) cb = 255; break;  // azul
  }

  float nivel = nivelLuz(leerLuz());
  float objetivo = brilloMinimo + (1.0 - brilloMinimo) * pasoSuave(umbralInf, umbralSup, nivel);
  brilloActual += (objetivo - brilloActual) * suavizado;

  analogWrite(pinRojo,  (int)(cr * brilloActual));
  analogWrite(pinVerde, (int)(cg * brilloActual));
  analogWrite(pinAzul,  (int)(cb * brilloActual));
}

// ---------- DHT ----------
void actualizarDHT() {
  if (millis() - ultimoDHT < intervaloDHT) return;
  ultimoDHT = millis();
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  if (!isnan(h)) humedad = h;               // si falla, conserva el ultimo valor
  if (!isnan(t)) temperatura = t;
}

// ---------- Pomodoro ----------
void iniciarFase(Estado nuevo, unsigned long minutos) {
  estado = nuevo;
  inicioFase = millis();
  duracionFase = minutos * 60UL * 1000UL;
}

void actualizarPomodoro() {
  if (estado == REPOSO) return;
  if (millis() - inicioFase >= duracionFase) {
    if (estado == FOCO) {
      iniciarBeep(4, 150, 150);
      iniciarFase(DESCANSO, minutosDescanso);
    } else {
      iniciarBeep(2, 300, 200);
      estado = REPOSO;
    }
  }
}

// ---------- Entradas ----------
void leerEncoder() {
  int estadoCLK = digitalRead(pinCLK);
  if (estadoCLK != ultimoEstadoCLK && estadoCLK == LOW) {
    if (estado == REPOSO) {                 // solo se cambia el tiempo en reposo
      if (digitalRead(pinDT) != estadoCLK) idxPreset = (idxPreset + 1) % numPresets;
      else idxPreset = (idxPreset + numPresets - 1) % numPresets;
    }
  }
  ultimoEstadoCLK = estadoCLK;
}

void leerBoton() {
  if (digitalRead(pinSW) == LOW && millis() - ultimoBoton > tiempoDebounce) {
    ultimoBoton = millis();
    if (estado == REPOSO) {
      iniciarFase(FOCO, presets[idxPreset]);
      iniciarBeep(1, 80, 0);
    } else {
      estado = REPOSO;                      // cancelar
      iniciarBeep(1, 200, 0);
    }
  }
}

// ---------- LCD ----------
void imprimirLinea(int fila, String texto) {
  while (texto.length() < 16) texto += ' ';
  lcd.setCursor(0, fila);
  lcd.print(texto.substring(0, 16));
}

void actualizarLCD() {
  if (millis() - ultimoLCD < intervaloLCD) return;
  ultimoLCD = millis();

  if (estado == REPOSO) {
    struct tm ti;
    char hora[9] = "--:--:--";
    if (getLocalTime(&ti, 0)) strftime(hora, sizeof(hora), "%H:%M:%S", &ti);
    imprimirLinea(0, String(hora) + " " + String(presets[idxPreset]) + "min");

    String l2 = "T:";
    l2 += isnan(temperatura) ? "--" : String(temperatura, 1);
    l2 += "C H:";
    l2 += isnan(humedad) ? "--" : String((int)humedad);
    l2 += "%";
    imprimirLinea(1, l2);
  } else {
    unsigned long restanteSeg = (duracionFase - (millis() - inicioFase)) / 1000UL;
    char buf[17];
    snprintf(buf, sizeof(buf), "Resta: %02lu:%02lu", restanteSeg / 60, restanteSeg % 60);
    imprimirLinea(0, estado == FOCO ? "== MODO FOCO ==" : "== DESCANSO ==");
    imprimirLinea(1, String(buf));
  }
}

// ---------- Setup / Loop ----------
void setup() {
  Serial.begin(115200);
  delay(500);

  pinMode(pinCLK, INPUT_PULLUP);
  pinMode(pinDT, INPUT_PULLUP);
  pinMode(pinSW, INPUT_PULLUP);
  pinMode(pinBuzzer, OUTPUT);
  digitalWrite(pinBuzzer, LOW);
  pinMode(pinRojo, OUTPUT);
  pinMode(pinVerde, OUTPUT);
  pinMode(pinAzul, OUTPUT);
  analogReadResolution(12);
  ultimoEstadoCLK = digitalRead(pinCLK);

  Wire.begin(pinSDA, pinSCL);
  lcd.init();
  lcd.backlight();
  dht.begin();

  lcd.setCursor(0, 0);
  lcd.print("Conectando WiFi");
 // WiFi.begin(WIFI_SSID, WIFI_PASS);

  unsigned long ini = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - ini < 10000) delay(250);

  configTime(GMT_OFFSET_SEG, DST_OFFSET_SEG, "pool.ntp.org", "time.google.com");
  lcd.clear();
  imprimirLinea(0, WiFi.status() == WL_CONNECTED ? "WiFi OK" : "Sin WiFi");
  delay(1000);
  lcd.clear();
}

void loop() {
  leerEncoder();
  leerBoton();
  actualizarDHT();
  actualizarPomodoro();
  actualizarLED();
  actualizarBuzzer();
  actualizarLCD();
}
