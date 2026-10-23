# Documentación Técnica: Migración de ESP32 a ESP8266MOD

## Motivación del cambio
Durante las pruebas de integración del proyecto Secretario Mudo IoT, se detectó un fallo crítico de hardware en el módulo ESP32. Al intentar inicializar el módulo Wi-Fi, la placa generaba un pico de corriente que no soportaba, provocando un reinicio constante (bootloop) y apagando el sistema.

## Solución implementada
Se optó por migrar todo el proyecto al módulo **ESP8266MOD**, el cual ofrece la misma conectividad Wi-Fi pero con un consumo energético más estable para nuestro circuito.

## Cambios técnicos realizados
1. **Hardware:** Re-mapeo de todos los pines (LCD, DHT11, LDR, LED RGB, Encoder y Buzzer) a los GPIO del ESP8266.
2. **Librerías:** Se reemplazó la librería `<WiFi.h>` por `<ESP8266WiFi.h>`.
3. **Sincronización NTP:** Se configuró el huso horario para Costa Rica (UTC-6) mediante `configTime`, logrando mostrar la hora exacta en la pantalla LCD sin necesidad de un reloj de tiempo real (RTC) físico.
4. **Código:** Se mantuvo la lógica del paradigma imperativo y el uso de `millis()` para evitar bloqueos en el reloj.
