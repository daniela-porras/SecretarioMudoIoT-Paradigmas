# Proyecto: Secretario Mudo IoT
# Bitácora de: Javier Pérez Barquero.

## Semana 1 - [12/10/2026] a [16/10/2026]

### Actividades realizadas
- Reunión de equipo para definir el proyecto "Secretario Mudo IoT".
- Investigación sobre los componentes necesarios (ESP32, DHT11, pantalla LCD I2C).
- Revisión de la estructura del repositorio creado por mi compañera Daniela Porras.

### Avances
- Proyecto definido y aprobado por el equipo.
- Repositorio y README principal revisados y validados.
- Commit: `8af323465c516e2d68468c2d1feb11d894d6be6b` - "Creación de bitacora Javier"

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



## Semana 2 - [19/10/2026] a [23/10/2026]

## Sábado 17/10/2026

### Actividades realizadas
- Armado y cableado del circuito en el protoboard.
- Pruebas de voltaje y conexión de todos los sensores al ESP32.
- Apoyo en las pruebas de integración física.

### Avances
- Circuito base armado y verificado.

### Dificultades encontradas
- Al conectar múltiples sensores, el cableado era difícil de rastrear.
- El ESP32 se apagaba al probar el Wi-Fi.

### Soluciones implementadas
- Ordené los cables por colores para facilitar la depuración.
- Ayudé a descartar problemas de cableado y confirmamos que el ESP32 no soportaba el pico de corriente.

### Decisiones técnicas
- Se utilizó el paradigma imperativo para estructurar las pruebas paso a paso.

### Pruebas efectuadas
- Prueba de continuidad y voltaje.
- Prueba física de respuesta de los sensores.

### Aprendizajes obtenidos
- Aprendí la importancia de un cableado ordenado y cómo diagnosticar problemas de energía.

### Próximos pasos
- Preparar el protoboard para el cambio de microcontrolador.


## Martes 20/10/2026

### Actividades realizadas
- Desmontaje del ESP32 y montaje del ESP8266MOD en el protoboard.
- Re-mapeo del cableado hacia los nuevos pines junto a Diego.
- Definición de la arquitectura de software para el Backend.

### Avances
- Migración física completada exitosamente.
- Sensores operando en el nuevo módulo sin apagones.
- Commit: `ddf1acd5c605ff4baca06ed5565b7ae7ca1ce9e4` - "Actualización de esquema de cableado para ESP8266"

### Dificultades encontradas
- La distribución de pines era diferente, requirió mover casi todo.
- Definir qué base de datos usar para el proyecto.

### Soluciones implementadas
- Dibujé el esquema de conexiones junto a Diego para validar el flujo eléctrico antes de encender.
- **Me asignaron el desarrollo del Backend y la Base de Datos. Decidí investigar Python con SQLite por su facilidad para proyectos IoT.**

### Decisiones técnicas
- Evitar pines de arranque para los sensores.
- Implementar un servidor local para recibir los datos del ESP8266.

### Pruebas efectuadas
- Prueba de encendido exitoso del ESP8266MOD.
- Verificación física de la hora en la LCD.

### Aprendizajes obtenidos
- Aprendí a adaptar un circuito físico a un microcontrolador diferente.

### Próximos pasos
- Crear la estructura de la Base de Datos (tablas de temperatura y Pomodoro).
- Investigar cómo crear una API básica con Python/Flask o Node.js en la carpeta `src/backend`.
- Documentar el esquema eléctrico final para `hardware`.
