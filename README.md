# SecretarioMudoIoT-Paradigmas
Proyecto Secretario Mudo IoT - Paradigmas de Programación UNA
**Profesor:** Eddier López  

## Descripción del Proyecto
El Secretario Mudo IoT es una solución tecnológica compacta diseñada para espacios de trabajo o estudio. Utiliza un microcontrolador ESP8266MOD para actuar como un asistente ambiental y de enfoque. Reúne en un solo punto físico información clave (hora sincronizada por Wi-Fi, temperatura y humedad) y herramientas de gestión del tiempo (temporizador Pomodoro interactivo con iluminación ambiental adaptativa). 
*(Nota: Se incluye un panel web complementario para visualizar los datos históricos).*

**Objetivo:** Reducir las distracciones digitales cotidianas, evitando que el usuario revise su teléfono móvil o abra nuevas pestañas en el navegador.

## Tecnologías y Componentes
- **Microcontrolador:** ESP8266MOD *(se migró del ESP32 por fallos de corriente)*
- **Sensores:** DHT11 (Temp/Humedad), Fotorresistencia LDR (Luz)
- **Actuadores:** Pantalla LCD 16x2 I2C, LED RGB, Buzzer
- **Entradas:** Encoder Rotativo (Selección de tiempo)
- **Software:** Arduino IDE, C++ (Paradigma Imperativo), Python (Flask), SQLite, HTML/CSS/JS.

## Estructura del Repositorio
- `/src/arduino`: Código fuente del microcontrolador.
- `/src/backend`: Código del servidor (Flask + SQLite).
- `/src/web`: Código del panel web (Dashboard).
- `/docs`: Diagramas de arquitectura y documentación técnica.
- `/tests`: Resultados de las pruebas realizadas.
- `/bitacoras`: Bitácoras individuales de cada integrante.
- `/Hardware`: Esquemas de conexión y fotos del prototipo físico.

## Paradigma de Programación
Se utilizó el **Paradigma Imperativo** para el desarrollo del código del microcontrolador. La lógica se basa en un flujo secuencial de instrucciones para la lectura de sensores y actualización de la pantalla. Además, se implementó una máquina de estados mediante condicionales (`switch`, `if`) y se utilizó la función `millis()` para gestionar los tiempos del Pomodoro de forma no bloqueante, asegurando que el reloj no se congele.

**Para ejecutar el panel web:**
1. Abrir una terminal en la carpeta `src/backend`.
2. Instalar dependencias: `pip install -r requirements.txt`
3. Ejecutar el servidor: `python app.py`
4. Abrir en el navegador: `http://localhost:5000`

## Instrucciones de Ejecución
Para ver el paso a paso detallado (desde instalar el Arduino IDE hasta conectar la placa al servidor), consulta nuestra guía completa aquí:
**[Descargar Guía de Conexión (PDF)](./docs/Guia_Conexion_Secretario_Mudo.docx)**

## Integrantes
- Daniela Porras Oviedo
- Diego González Oviedo
- Javier Pérez Barquero
- Henry Yamir Pérez Barahona
