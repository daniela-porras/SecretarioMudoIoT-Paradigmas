# Proyecto: Secretario Mudo IoT
# Bitácora de: [Daniela Porras Oviedo]

## Semana 1 - [12/10/2026] a [16/10/2026]

### Actividades realizadas
- [Reunión de equipo para definir el proyecto "Secretario Mudo IoT"]
- [Creación del repositorio en GitHub y estructura inicial de carpetas]
- [Configuración de la bitácora individual]

### Avances
- [Repositorio configurado con las carpetas src, docs, tests y bitacoras]
- [README principal redactado con la descripción del proyecto]
- Commit: d19ccb622ed6ae204cc231f4f2f04c73b6cff073 - "Initial commit"
- Commit: 7b31a535c53c9965328767992b4f48793b06bcb7 - "Add README.md with project source folder description"
- Commit: 271283224f856d65fb0aef6f4d6842461a61b90f - "Add README.md for diagrams and documentation"
- Commit: 52b3fb64c278bc841ca8484f75393ffaf384fbb4 - "Add README.md for tests directory"
- Commit: bf1485bef19e122db08224a42830a71e52734589 - "Add README for individual log folder"

### Dificultades encontradas
- [Aprender a crear carpetas en GitHub, ya que no hay un botón directo]
- [Coordinar horarios para la reunión de equipo]

### Soluciones implementadas
- [Se investigó cómo crear carpetas usando la ruta en el nombre del archivo]
- [Comunicación por WhatsApp para definir el proyecto]

### Decisiones técnicas
- [Se eligió el proyecto "Secretario Mudo IoT" por su viabilidad y utilidad]
- [Se decidió usar el microcontrolador ESP32 en lugar de Arduino por su conectividad Wi-Fi]

### Pruebas efectuadas
- [Verificación de la estructura del repositorio en la web de GitHub]

### Aprendizajes obtenidos
- [Manejo básico de GitHub para proyectos colaborativos]
- [Importancia de la organización desde el día 1]

### Próximos pasos
- [Investigar el funcionamiento del sensor DHT11 y la pantalla LCD]
- [Instalar Arduino IDE y configurar la placa ESP32]


---

## Sábado 17/10/2026

### Actividades realizadas
- Trabajo en equipo para la integración de los sensores al ESP32.
- Revisión conjunta del código base (paradigma imperativo).
- Pruebas de funcionamiento del temporizador Pomodoro.

### Avances
- El ESP32 funcionó como cerebro central con todos los sensores.
- Éxito en la lectura del DHT11 y el control del Pomodoro.

### Dificultades encontradas
- Al intentar activar el Wi-Fi, el ESP32 entró en un bucle de reinicio (bootloop).

### Soluciones implementadas
- Nos reunimos todo el equipo para analizar el problema. Tras revisar el código, concluimos que era un fallo físico (pico de corriente) del módulo Wi-Fi del ESP32.

### Decisiones técnicas
- Mantener el paradigma imperativo para la lógica de los sensores.
- Investigar alternativas para la conectividad.

### Pruebas efectuadas
- Prueba de integración de sensores: Exitosa.
- Prueba de conexión Wi-Fi: Fallida por apagón del ESP32.

### Aprendizajes obtenidos
- Comprendí que un error de hardware puede parecer un error de código; la importancia de aislar variables en equipo.

### Próximos pasos
- Reunión para evaluar el cambio de microcontrolador.
- Investigar el módulo ESP8266MOD.

---

## Martes 20/10/2026

### Actividades realizadas
- Reunión de equipo para coordinar la migración del proyecto al ESP8266MOD.
- Colaboración en la revisión de la adaptación del código.
- Validación final de la función IoT y definición de la arquitectura Web/IoT.

### Avances
- Proyecto migrado exitosamente al ESP8266MOD.
- Wi-Fi, sincronización NTP y LCD funcionando.
- Commit: 61046e16d038a8821dc1bacf9336348591f1c494 - "Actualización de bitácora y validación de migración"

### Dificultades encontradas
- Reorganizar el hardware y el software al mismo tiempo.
- Definir cómo se comunicará el ESP8266 con la página web.

### Soluciones implementadas
- Trabajamos en bloque: Javier ajustó el hardware, Diego y Henry adaptaron el código, y yo validé que la integración general no perdiera funciones.

### Decisiones técnicas
- Adoptar el ESP8266MOD y mantener el paradigma imperativo usando `millis()`.
- **División de roles para la fase final: Me asignaron el desarrollo del Frontend (Página Web) y la documentación en el README.**

### Pruebas efectuadas
- Prueba de integración total: Sensores + Wi-Fi + Pantalla sin apagones.

### Aprendizajes obtenidos
- La comunicación asertiva en equipo es vital en la ingeniería.

### Próximos pasos
- Investigar frameworks de CSS (como Bootstrap) para el diseño del Dashboard Web.
- Crear la estructura base de la página web en `src/web`.
- Coordinar con Javier (Backend) cómo se van a consumir los datos de la Base de Datos.
