# Proyecto: Secretario Mudo IoT
# Bitácora de: Diego González Oviedo

## Semana 1 - [12/10/2026] a [16/10/2026]

### Actividades realizadas
- Reunión de equipo para definir el proyecto "Secretario Mudo IoT".
- Investigación sobre los componentes necesarios (ESP32, DHT11, pantalla LCD I2C).
- Revisión de la estructura del repositorio creado por mi compañera Daniela Porras.

### Avances
- Proyecto definido y aprobado por el equipo.
- Repositorio y README principal revisados y validados.
- Commit: `3b09d9bcf088878a414d1cfbabefac8378205eff` - "Creacion bitacora Diego"

### Dificultades encontradas
- Encontrar documentación clara sobre cómo conectar la pantalla LCD 16x2 al ESP32.
- Coordinar horarios para la reunión de equipo.

### Soluciones implementadas
- Se buscaron tutoriales en YouTube y foros de Arduino para entender el protocolo I2C.
- Se creó un grupo de WhatsApp para comunicación rápida y definición del proyecto.

### Decisiones técnicas
- Se aceptó la propuesta de usar el ESP32 por su conectividad Wi-Fi integrada.
- Se decidió usar la técnica Pomodoro física con un potenciómetro para evitar distracciones.

### Pruebas efectuadas
- Verificación de acceso al repositorio de GitHub (Colaborador agregado exitosamente).
- Revisión de la estructura de carpetas (`src`, `docs`, `tests`, `bitacoras`).

### Aprendizajes obtenidos
- Importancia de la organización desde el día 1 en proyectos de IoT.
- Conocimiento inicial sobre el funcionamiento de los sensores DHT11 y LDR.

### Próximos pasos
- Instalar Arduino IDE en mi computadora.
- Investigar cómo sincronizar la hora por NTP con el ESP32.
- Revisar el datasheet del sensor DHT11 para su integración.

## Sábado 17/10/2026

### Actividades realizadas
- Desarrollo de la estructura inicial del código aplicando el paradigma imperativo.
- Colaboración con el equipo en el cableado y prueba de los sensores.
- Pruebas de la función Wi-Fi para sincronización de hora (NTP).

### Avances
- Lógica del temporizador Pomodoro y visualización de datos funcionando.
- Commit: `c068cd44454909e4291ef317790794d9b6fe2d58` - "Código Arduino V1"

### Dificultades encontradas
- El ESP32 entraba en bootloop al inicializar el Wi-Fi.

### Soluciones implementadas
- Revisamos el código en equipo y, mediante pruebas de descarte con el hardware, confirmamos que era una falla de corriente del ESP32.

### Decisiones técnicas
- Uso del paradigma imperativo para el control secuencial.
- Concluir que debíamos cambiar de microcontrolador.

### Pruebas efectuadas
- Prueba de integración: DHT11 + LCD + Temporizador (Exitosa).
- Prueba de conexión Wi-Fi en ESP32 (Fallida).

### Aprendizajes obtenidos
- Aprendí a diagnosticar fallas de hardware mediante la eliminación de variables.

### Próximos pasos
- Investigar en conjunto la migración al ESP8266MOD.

---

## Martes 20/10/2026

### Actividades realizadas
- Adaptación del código al ESP8266MOD en colaboración con Henry.
- Reescritura de las funciones de red y del timer usando `millis()`.
- Implementación de la sincronización NTP.

### Avances
- Código adaptado y compilado exitosamente en el nuevo módulo.
- Wi-Fi conectado, hora sincronizada y mostrada en la LCD.
- Commit: `4fa8049d2b57d1394f1b9a525191a12d1159f375` - "Código adaptado al esp8266MOD"

### Dificultades encontradas
- La distribución de pines cambió, requirió reasignar variables en el código.

### Soluciones implementadas
- Coordiné con Javier el nuevo mapeo de pines. Henry y yo ajustamos la zona horaria del servidor NTP.

### Decisiones técnicas
- Mantener el paradigma imperativo usando `millis()` para evitar bloqueos.
- **Me asignaron el diseño de la carcasa (hardware) y la integración del envío de datos por HTTP para el backend.**

### Pruebas efectuadas
- Prueba de conexión Wi-Fi en ESP8266: Exitosa.
- Prueba de sincronización: Hora exacta en la LCD.

### Aprendizajes obtenidos
- Adaptabilidad a nuevas arquitecturas de hardware.

### Próximos pasos
- Diseñar y construir la carcasa/gabinete físico del Secretario Mudo.
- Investigar cómo hacer peticiones HTTP (GET/POST) desde el ESP8266 hacia el servidor de Javier.
