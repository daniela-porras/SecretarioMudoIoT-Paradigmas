# Proyecto: Secretario Mudo IoT
# Bitácora de: Henry Yamir Pérez Barahona

## Semana 1 - [12/10/2026] a [16/10/2026]

### Actividades realizadas
- Reunión de equipo para definir el proyecto "Secretario Mudo IoT".
- Investigación sobre los componentes necesarios (ESP32, DHT11, pantalla LCD I2C).
- Revisión de la estructura del repositorio creado por mi compañera Daniela Porras.

### Avances
- Proyecto definido y aprobado por el equipo.
- Repositorio y README principal revisados y validados.
- Commit: `b60146625bb235345e0e271e5802bc6b54144097` - "Create bitacora.md"

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

---

## Sábado 17/10/2026

### Actividades realizadas
- Investigación y revisión de las librerías de los sensores (DHT11, LCD I2C).
- Apoyo directo en la revisión del código (paradigma imperativo).
- Pruebas de lectura de datos en el monitor serial.

### Avances
- Se identificaron y resolvieron conflictos entre librerías.
- Verificación del correcto funcionamiento lógico del temporizador.

### Dificultades encontradas
- El ESP32 se reiniciaba abruptamente al intentar conectar el Wi-Fi.

### Soluciones implementadas
- Descartamos errores de programación y confirmamos junto a Javier que era un problema de consumo eléctrico.

### Decisiones técnicas
- Se mantuvo el paradigma imperativo para estructurar la lógica.
- Se acordó investigar el ESP8266MOD como alternativa.

### Pruebas efectuadas
- Prueba de monitor serial: Verificación de datos del DHT11.

### Aprendizajes obtenidos
- Aprendí a leer el monitor serial y a diferenciar errores de código de fallas de hardware.

### Próximos pasos
- Investigar la documentación del ESP8266MOD y sus librerías Wi-Fi.

---

## Martes 20/10/2026

### Actividades realizadas
- Investigación sobre la librería `ESP8266WiFi.h` y el protocolo NTP.
- Apoyo en la reescritura del código para el nuevo microcontrolador.
- Documentación técnica de la migración y diseño de la arquitectura del sistema.

### Avances
- Código adaptado para el ESP8266MOD con conexión Wi-Fi exitosa.
- Commit: `f35ed1826b6ade8f427b9fbbcebee98157e4bc1f` - "Documentación técnica de migración a ESP8266"

### Dificultades encontradas
- La zona horaria por defecto no era la de Costa Rica.
- Definir cómo interactúa el hardware con la base de datos y la web.

### Soluciones implementadas
- Ajustamos el huso horario (offset UTC) en el código junto a Diego.
- **Me asignaron el diseño del diagrama de arquitectura (incluyendo el flujo IoT) y la búsqueda de referencias en IEEE.**

### Decisiones técnicas
- Uso de NTP por su precisión. Mantener la estructura imperativa.

### Pruebas efectuadas
- Prueba de sincronización: Hora exacta en la LCD.

### Aprendizajes obtenidos
- Comprendí el protocolo NTP y cómo documentar los cambios de hardware.

### Próximos pasos
- Diseñar el diagrama de arquitectura (ESP8266 -> Backend -> DB -> Web) y subirlo a `docs`.
- Documentar las pruebas en la carpeta `tests`.
- Buscar artículos académicos sobre IoT y Pomodoro para las referencias del artículo.
