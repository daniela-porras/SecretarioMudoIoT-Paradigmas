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

---

## Miércoles 28/10/2026

### Actividades realizadas
- Elaboración del diagrama de flujo general del proyecto "Secretario Mudo IoT".
- Análisis del funcionamiento completo del sistema para representar gráficamente sus procesos, decisiones y secuencia de ejecución.
- Incorporación del diagrama de flujo al repositorio de GitHub como parte de la documentación del proyecto.

### Avances
- Diagrama de flujo general finalizado, representando el funcionamiento completo del sistema.
- Documentación visual incorporada al repositorio de GitHub para facilitar la comprensión de la lógica del proyecto.

### Dificultades encontradas
- Organizar correctamente los procesos y las decisiones del sistema para representar de forma clara su funcionamiento.

### Soluciones implementadas
- Se revisó la lógica del programa para identificar y organizar las operaciones principales antes de representarlas en el diagrama de flujo.

### Decisiones técnicas
- Se utilizó un diagrama de flujo para documentar visualmente la lógica general del sistema y facilitar su comprensión.

### Pruebas efectuadas
- Revisión del diagrama de flujo para verificar que la secuencia representada correspondiera con el funcionamiento del programa.

### Aprendizajes obtenidos
- Reforcé mis conocimientos sobre la representación gráfica de algoritmos y procesos.
- Comprendí la importancia de documentar el funcionamiento de un sistema IoT para facilitar su mantenimiento y futuras modificaciones.

### Próximos pasos
- Dar seguimiento a las modificaciones y mejoras pendientes del código.
- Colaborar con la planificación y publicación del proyecto en la web.

### Lunes 16/11/2026

**Actividades realizadas**
- Revisión y modificación del diagrama de flujo general del proyecto "Secretario Mudo IoT".
- Análisis de las observaciones del equipo sobre las dificultades presentadas durante las pruebas con el sensor LDR.
- Revisión y complementación del artículo científico del proyecto.
- Elaboración de mejoras para las secciones de resultados, discusión y conclusiones del artículo.

**Avances**
- Código PlantUML del diagrama de flujo modificado para eliminar los procesos relacionados con el sensor LDR.
- Diagrama actualizado para representar el funcionamiento del dispositivo sin el sensor de luz ambiental.
- Se revisó y amplió el contenido de las secciones de resultados, discusión y conclusiones del artículo científico.
- Se incorporó en la discusión la justificación técnica de la decisión de excluir el sensor LDR.
- Commit: `85911f062eae3538eedaf6130badff054244d06b` - "Actualizar diagrama de flujo y eliminar sensor LDR"

**Dificultades encontradas**
- Necesidad de ajustar la documentación del proyecto debido a los cambios realizados en los componentes y funcionalidades del prototipo.
- Identificación de información que necesitaba mayor desarrollo en el artículo científico, especialmente en la interpretación de los resultados y las limitaciones del proyecto.

**Soluciones implementadas**
- Se modificó el código del diagrama de flujo para eliminar las decisiones y acciones relacionadas con la iluminación ambiental.
- Se revisaron y complementaron las secciones del artículo científico para mantener la coherencia entre la documentación y el funcionamiento real del prototipo.
- Se explicó la exclusión del LDR debido a las interferencias identificadas durante las pruebas de integración.

**Decisiones técnicas**
- Se acordó excluir definitivamente el sensor LDR del proyecto.
- Se mantuvo el sensor DHT11 para el monitoreo de temperatura y humedad.
- Se conservaron los indicadores LED según los estados del temporizador: verde para FOCO, rojo para DESCANSO y apagado para REPOSO.
- Se decidió mantener en el artículo únicamente las funcionalidades que forman parte de la implementación del sistema.

**Pruebas efectuadas**
- Revisión del código PlantUML para comprobar la eliminación de los procesos relacionados con el LDR.
- Verificación de la coherencia entre las funciones descritas en el artículo y las características del prototipo desarrollado.

**Aprendizajes**
- Comprendí la importancia de mantener actualizados los diagramas y documentos técnicos cuando se realizan cambios en el diseño de un proyecto.
- Reforcé mis conocimientos sobre la documentación científica y la importancia de relacionar los resultados obtenidos con los objetivos establecidos.
- Comprendí la necesidad de justificar las decisiones técnicas y reconocer las limitaciones durante el desarrollo de un proyecto IoT.

**Próximos pasos**
- Finalizar la revisión del artículo científico y completar las secciones pendientes.
- Incorporar fotografías del prototipo físico y capturas del panel web.
- Compartir el artículo con los integrantes del equipo para recibir observaciones.
- Actualizar la documentación del proyecto en GitHub.
- Preparar los materiales necesarios para la exposición del proyecto.
