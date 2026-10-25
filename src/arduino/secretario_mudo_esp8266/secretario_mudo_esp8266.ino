/*
  Secretario Mudo IoT - ESP8266 (NodeMCU / ESP8266MOD)

  MAPA DE PINES (etiqueta NodeMCU -> GPIO)
  LCD I2C  : SDA=D2(GPIO4)  SCL=D1(GPIO5)  VCC=VIN(5V)  GND
  DHT11    : DATA=D5(GPIO14)  VCC=3V3  GND
  LDR      : divisor (LDR + resistor 10k a GND) -> punto medio a A0, extremo a 3V3
  LED RGB  : R=D6(GPIO12)  G=D7(GPIO13)  B=D8(GPIO15)  (cada uno con 220 ohm; GND comun)
  Encoder  : CLK=D3(GPIO0)  DT=D4(GPIO2)  SW=D0(GPIO16)  (+ a 3V3, GND)
             * SW en D0 necesita una resistencia pull-up externa de 10k a 3V3
  Buzzer   : RX(GPIO3) (buzzer activo) y GND
             * Se usa Serial solo en TX para liberar el pin RX

  NUEVO: envio de datos por HTTP al backend (Flask).
    POST /api/lecturas  cada 30 s  -> temperatura, humedad, luz
    POST /api/pomodoros al terminar/cancelar una fase de FOCO
*/
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <time.h>

// ---------- WiFi / NTP ----------
const char* WIFI_SSID = "BUKA";
const char* WIFI_PASS = "diego123.";
const long  GMT_OFFSET_SEG = -6 * 3600;   // Costa Rica UTC-6
const int   DST_OFFSET_SEG = 0;           // sin horario de verano

// ---------- Backend ----------
// IP de la compu donde corre app.py (misma red WiFi). Ver con ipconfig / ifconfig.
const char* SERVER_URL = "http://192.168.X.X:5000";
const unsigned long intervaloEnvio = 30000;   // lecturas cada 30 s
unsigned long ultimoEnvio = 0;

// Pomodoro pendiente de enviar (se envia desde el loop para no retrasar el beep/LED)
bool pomPendiente = false;
int  pomMinutos = 0;
bool pomCompletado = false;

// ---------- Pines ----------
const int pinSDA = 4,  pinSCL = 5;        // D2, D1
#define DHTPIN 14                         // D5
#define DHTTYPE DHT11
const int pinLDR = A0;                    // unico pin analogico (0-1023)
const int pinRojo = 12, pinVerde = 13, pinAzul = 15;   // D6, D7, D8
const int pinCLK = 0, pinDT = 2, pinSW = 16;           // D3, D4, D0
const int pinBuzzer = 3;                               // RX

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
const float brilloMinimo = 0.50;
const float umbralInf = 0.30, umbralSup = 0.50;
const float suavizado = 0.15;
int luzMin = 80, luzMax = 900;            // ADC de 10 bits (0-1023); ajusta viendo el Serial
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

// ---------- HTTP -> backend ----------
void enviarJSON(const char* ruta, const String& json) {
  if (WiFi.status() != WL_CONNECTED) return;
  WiFiClient client;
  HTTPClient http;
  http.setTimeout(1500);                    // si el servidor no responde, no congela el reloj
  if (http.begin(client, String(SERVER_URL) + ruta)) {
    http.addHeader("Content-Type", "application/json");
    int code = http.POST(json);
    Serial.printf("POST %s -> %d\n", ruta, code);
    http.end();
  }
}

void registrarPomodoro(bool completado) {   // solo marca; el envio ocurre en enviarDatos()
  pomPendiente = true;
  pomMinutos = duracionFase / 60000UL;
  pomCompletado = completado;
}

void enviarDatos() {
  // 1) Pomodoro terminado/cancelado (tiene prioridad)
  if (pomPendiente) {
    pomPendiente = false;
    enviarJSON("/api/pomodoros",
      "{\"fase\":\"foco\",\"duracion_min\":" + String(pomMinutos) +
      ",\"completado\":" + (pomCompletado ? "true" : "false") + "}");
    return;
  }
  // 2) Lectura periodica de sensores
  if (millis() - ultimoEnvio < intervaloEnvio) return;
  if (isnan(temperatura) || isnan(humedad)) return;
  ultimoEnvio = millis();
  enviarJSON("/api/lecturas",
    "{\"temperatura\":" + String(temperatura, 1) +
    ",\"humedad\":" + String(humedad, 0) +
    ",\"luz\":" + String(leerLuz()) + "}");
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
      registrarPomodoro(true);              // termino completo (duracionFase aun es la de foco)
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
      if (estado == FOCO) registrarPomodoro(false);   // interrumpido a mitad del foco
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
    char hora[9] = "--:--:--";
    time_t ahora = time(nullptr);
    if (ahora > 1700000000) {               // la hora ya fue sincronizada por NTP
      struct tm ti;
      localtime_r(&ahora, &ti);
      strftime(hora, sizeof(hora), "%H:%M:%S", &ti);
    }
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
  Serial.begin(115200, SERIAL_8N1, SERIAL_TX_ONLY);   // solo TX, RX queda libre para el buzzer
  delay(500);

  pinMode(pinCLK, INPUT_PULLUP);
  pinMode(pinDT, INPUT_PULLUP);
  pinMode(pinSW, INPUT);                    // GPIO16 no tiene pull-up interno: usa 10k externa a 3V3
  pinMode(pinBuzzer, OUTPUT);
  digitalWrite(pinBuzzer, LOW);
  pinMode(pinRojo, OUTPUT);
  pinMode(pinVerde, OUTPUT);
  pinMode(pinAzul, OUTPUT);
  analogWriteRange(255);                    // PWM de 0-255 como en el ESP32
  ultimoEstadoCLK = digitalRead(pinCLK);

  Wire.begin(pinSDA, pinSCL);
  lcd.init();
  lcd.backlight();
  dht.begin();

  lcd.setCursor(0, 0);
  lcd.print("Conectando WiFi");
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  unsigned long ini = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - ini < 15000) delay(250);

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
  enviarDatos();
}
