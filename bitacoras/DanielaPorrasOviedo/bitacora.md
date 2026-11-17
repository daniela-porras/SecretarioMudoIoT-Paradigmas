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

---

## Lunes 26/10/2026

### Actividades realizadas
- Mejora y finalización del Frontend (Panel Web) sobre la base creada por Javier.
- Implementación de mejoras visuales (UI/UX) con CSS, sombras, iconos (FontAwesome) y diseño responsivo.
- Integración de gráficos interactivos con Chart.js.
- Corrección de bugs en la lógica de eventos de JavaScript.

### Avances
- Panel web con diseño "Premium" totalmente funcional (probado con datos simulados).
- Corrección de la lógica de eventos en los botones de la tabla de Épocas.
- Commit: ebb9628a9b3b16fb7c473d8e9e16ccf0acffbd09 - "Mejora de UI: Tabla de épocas, iconos y fix de clics"

### Dificultades encontradas
- Los botones con iconos en la tabla de épocas no respondían al hacer clic (bug de JavaScript).

### Soluciones implementadas
- Se solucionó el bug usando la función `closest('button')` en JavaScript para detectar el clic sin importar si se presionaba el icono o el fondo.

### Decisiones técnicas
- Mantener los cambios en la rama `feature/desarrolloBackFront` (creada por Javier) hasta que la conexión física con el ESP8266 sea 100% estable, antes de fusionarla con la `main`.

### Pruebas efectuadas
- Prueba de navegación móvil: El panel se adapta correctamente a pantallas de celular.
- Prueba de UI con datos simulados: Los gráficos y la tabla responden bien a los filtros.

### Aprendizajes obtenidos
- Reforcé mis conocimientos en manipulación del DOM (JavaScript) para crear interfaces dinámicas e interactivas.

### Próximos pasos
- Subir la Guía de Conexión (creada por Javier) a la carpeta `docs` del repositorio.
- **Preparar el entorno para la prueba de integración del día martes junto a Diego.**
- Iniciar la redacción del artículo de investigación (Introducción y Planteamiento del Problema).

---

## Lunes 02/11/2026

### Actividades realizadas
- Prueba de integración general del prototipo con el panel web.
- Validación de lectura del DHT11, pantalla LCD, encoder rotativo, LED RGB, buzzer y conexión Wi-Fi.
- Revisión del comportamiento del LDR durante las pruebas.
- Reunión de equipo para decidir el alcance final del hardware.
- Redacción de mi parte del artículo: Planteamiento de la problemática, Objetivos y Metodología.

### Avances
- La prueba de integración funcionó correctamente en casi todos los componentes.
- El dispositivo envió datos al panel web y se verificó la recepción en la base de datos.
- Se documentó la decisión de quitar el LDR del alcance del proyecto.
- Avance en la redacción del artículo de investigación correspondiente a mi sección.

### Dificultades encontradas
- La lectura del LDR no fue confiable durante las pruebas.
- Fue necesario ajustar la documentación y el alcance del proyecto para eliminar las referencias al LDR.
- Coordinar la redacción del artículo con las pruebas finales del prototipo.

### Soluciones implementadas
- Se decidió retirar el LDR del proyecto y dejar únicamente el sensor DHT11 para temperatura y humedad.
- Se mantuvieron el LED RGB, el buzzer y el temporizador Pomodoro como parte funcional del dispositivo.
- Se actualizó el enfoque del artículo para que no se prometiera monitoreo de luz ni iluminación adaptativa.

### Decisiones técnicas
- **Eliminar el LDR del hardware y de la documentación técnica.**
- Mantener el DHT11 como único sensor ambiental.
- Conservar el LED RGB para la retroalimentación visual de los estados del Pomodoro.
- Documentar el proyecto sin referencias a fotorresistencia, luz o iluminación ambiental adaptativa.

### Pruebas efectuadas
- Prueba de integración general: exitosa en DHT11, LCD, encoder, LED RGB, buzzer, Wi-Fi y panel web.
- Prueba del LDR: no confiable; se determinó que no se incluiría en la versión final.
- Verificación de envío de datos al panel web: correcta.

### Aprendizajes obtenidos
- Es importante validar cada componente por separado antes de integrarlo al prototipo final.
- Documentar a tiempo los cambios de alcance evita inconsistencias entre el hardware, el README, la guía y el artículo.

### Próximos pasos
- **Revisar la corrección realizada por Javier después de quitar el LDR.**
- **Subir el archivo de código actualizado al repositorio.**
- Verificar que no queden referencias al LDR en diagramas, fotos, carcasa o documentación.
- Continuar con la revisión del artículo completo.

---

## Lunes 16/11/2026

### Actividades realizadas
- Revisión y ajuste de la documentación del proyecto después de eliminar el LDR.
- Actualización del README principal para corregir el enlace de la Guía de Conexión.
- Revisión de la Guía de Conexión para quitar referencias al LDR y unificar el nombre del archivo `.ino`.
- Limpieza del artículo: eliminación de nombres de responsables en los títulos y párrafos de instrucciones que quedaron como borrador.
- Revisión de coherencia entre el README, la guía, el artículo y el alcance final del hardware.

### Avances
- README corregido para que el enlace apunte al archivo PDF de la guía.
- Guía de Conexión actualizada sin LDR, con el nombre `secretario_mudo_esp8266.ino` unificado.
- Artículo revisado para quitar placeholders, nombres de responsables y referencias innecesarias.
- Se dejó claro que el único sensor ambiental del proyecto es el DHT11.

### Dificultades encontradas
- Quedaban referencias al LDR y al monitoreo de luz en algunos documentos.
- El README tenía un enlace que decía PDF pero apuntaba a un `.docx`.
- El artículo todavía tenía textos de instrucciones y nombres de responsables en los títulos.

### Soluciones implementadas
- Se eliminaron las menciones al LDR en README, guía y artículo.
- Se corrigió el enlace del README para que apunte al PDF en `docs/`.
- Se unificó el nombre del archivo de código como `secretario_mudo_esp8266.ino`.
- Se limpiaron los títulos y párrafos del artículo que no formaban parte del contenido final.

### Decisiones técnicas
- Publicar la guía en PDF como versión principal de lectura.
- Dejar el `.docx` únicamente como versión editable, si se necesita.
- Mantener el artículo sin referencias al LDR y con el DHT11 como único sensor ambiental.
- **Revisar el orden de autores para que sea el mismo en todos los documentos.**

### Pruebas efectuadas
- Verificación de enlaces del README.
- Revisión visual de la Guía de Conexión sin LDR.
- Revisión de coherencia del artículo después de quitar el LDR.
- Comprobación de que el nombre del archivo `.ino` fuera consistente en la guía y el README.

### Aprendizajes obtenidos
- Un cambio de alcance como quitar un sensor obliga a revisar todo el repositorio, no solo el código.
- Los enlaces del README deben probarse en GitHub para evitar rutas rotas.
- La documentación técnica debe mantenerse sincronizada con el hardware real.

### Próximos pasos
- **Revisar la corrección hecha por Javier después de quitar el LDR.**
- **Subir el archivo de código actualizado al repositorio.**
- Confirmar que no queden referencias al LDR en diagramas, fotos o carcasa 3D.
- Probar el enlace del README en GitHub en una ventana de incógnito.
- Insertar las figuras reales del prototipo y el panel web en el artículo.
- Exportar el artículo final a PDF y revisar el formato IEEE de dos columnas.

---

## Martes 17/11/2026 (Cierre del Proyecto)

### Actividades realizadas
- **Cierre total de los pendientes de la fase de integración y documentación.**
- Subida del archivo de código final (`secretario_mudo_esp8266.ino`) al repositorio de GitHub, tras la revisión y corrección de Javier (eliminación del LDR).
- Revisión exhaustiva de diagramas, fotos y la carcasa 3D para **confirmar la ausencia total de referencias al LDR**.
- Inserción de las figuras reales del prototipo físico y del panel web en el documento del artículo.
- Exportación final del artículo a PDF con el formato IEEE de dos columnas.
- Prueba de los enlaces del `README.md` en una ventana de incógnito para verificar su correcto funcionamiento en la web.

### Avances
- **Repositorio actualizado y 100% sincronizado** con el hardware final (sin LDR).
- El artículo de investigación se encuentra completamente redactado, con figuras y **exportado en formato PDF IEEE**.
- Se comprobó que el enlace de la Guía de Conexión en el README funciona perfectamente.
- **Proyecto listo para su entrega y evaluación final.**

### Dificultades encontradas
- Ninguna dificultad técnica mayor; la fase se centró en la revisión de calidad (QA) y la consistencia de la documentación.

### Soluciones implementadas
- Se realizó una revisión cruzada de los archivos para asegurar que el código, el README, la guía y el artículo dijeran exactamente lo mismo respecto al alcance del proyecto.

### Decisiones técnicas
- **Dar por concluida la fase de desarrollo y pasar a la entrega oficial.**
- Mantener en el repositorio únicamente el código final del ESP8266 para evitar confusiones al profesor evaluador.

### Pruebas efectuadas
- **Prueba de enlaces:** Verificación del README en ventana de incógnito (Exitosa).
- **Prueba de formato:** Revisión del PDF final en formato IEEE de dos columnas (Correcto).
- **Prueba de repositorio:** Verificación de que los archivos finales están en las carpetas correspondientes (`src`, `docs`, `arduino`).

### Aprendizajes obtenidos
- La importancia de la gestión de versiones y la documentación constante para reflejar el estado real de un proyecto de ingeniería.
- Un proyecto no termina cuando el código funciona, sino cuando la documentación y el código están perfectamente alineados.

### Próximos pasos, ya final
- Realizar presentación final del proyecto.
