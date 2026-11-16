"""Pruebas de las señales que envía el ESP8266 al backend.

Archivos que intervienen:
  - Firmware:  secretario_mudo_esp8266.ino
  - Backend:   app.py (misma carpeta que este archivo)

Parte A: lee el .ino como texto y verifica que sea compatible con app.py.

Parte B: manda al backend los mismos JSON que mandaría el firmware y verifica
         que se guarden bien y que el panel los muestre.

Parte C: protecciones y cálculos clave del backend (borrado de datos, panel vacío,
         filtros de fecha, confort y efecto de la temperatura).

Se usa una base de datos temporal

Ejecutar:
  python -m unittest test_firmware -v
"""
import os
import re
import sqlite3
import sys
import tempfile
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.normpath(os.path.join(AQUI, ".."))        

# Permite encontrar app.py aunque este archivo esté en la carpeta tests
sys.path.insert(0, os.path.join(RAIZ, "src", "backend"))
import app as backend

# Ruta fija al firmware. Si la carpeta o el nombre cambian, hay que cambiarla aquí.
RUTA_INO = os.path.join(RAIZ, "src", "arduino",
                        "secretario_mudo_esp8266", "secretario_mudo_esp8266.ino")


# ---------------------------------------------------------------
# FUNCIONES AUXILIARES
# ---------------------------------------------------------------
def leer_firmware():
    """Función para leer el archivo .ino completo.
    Si el archivo no existe en RUTA_INO, falla mostrando la ruta que buscó."""
    if not os.path.isfile(RUTA_INO):
        raise AssertionError(f"No se encontró el firmware en: {RUTA_INO}")
    with open(RUTA_INO, encoding="utf-8") as f:
        return f.read()


def envios_del_firmware(src):
    """Función para encontrar a qué rutas envía datos el firmware.
    Busca cada llamada enviarJSON("/api/...", ...) y devuelve {ruta: texto del JSON}.
    Si se agrega un envío nuevo en el .ino, aparece aquí automáticamente."""
    return {m.group(1): m.group(2)
            for m in re.finditer(r'enviarJSON\(\s*"(/api/[a-z_]+)"\s*,(.*?)\);',
                                 src, flags=re.DOTALL)}


def claves_json(texto):
    """Función para sacar los nombres de los campos del JSON que arma el firmware.
    En el .ino los campos se escriben como \\"campo\\": y esta función devuelve solo los nombres."""
    return set(re.findall(r'\\"([A-Za-z_]+)\\"\s*:', texto))


def presets_del_firmware(src):
    """Función para leer los tiempos de pomodoro del .ino (presets[] = {15, 25, 45}).
    Si se cambian los tiempos en el firmware, las pruebas usan los nuevos valores solas.
    Devuelve lista vacía si no encuentra presets[]."""
    m = re.search(r'presets\s*\[\s*\]\s*=\s*\{([^}]*)\}', src)
    return [int(x) for x in re.findall(r'\d+', m.group(1))] if m else []


def json_lectura(temp, hum):
    """Función para armar el JSON de una lectura igual que el firmware.
    Temperatura con 1 decimal y humedad sin decimales.
    Si cambia el formato en el .ino, hay que cambiarlo aquí (una prueba avisa)."""
    return '{"temperatura":%.1f,"humedad":%.0f}' % (temp, hum)


def json_pomodoro(minutos, completado):
    """Función para armar el JSON de un pomodoro de foco igual que el firmware.
    completado=True envía true y completado=False envía false.
    Si cambia el formato en el .ino, hay que cambiarlo aquí (una prueba avisa)."""
    return '{"fase":"foco","duracion_min":%d,"completado":%s}' % (
        minutos, "true" if completado else "false")


class BaseAPI(unittest.TestCase):
    """Clase base para las pruebas que usan el backend.
    Antes de cada prueba crea una base de datos temporal vacía y la borra al terminar."""

    def setUp(self):
        # Crea la BD temporal y apunta el backend hacia ella
        self._fd, self._ruta = tempfile.mkstemp(suffix=".db")
        os.close(self._fd)
        self._db_original = backend.DB
        backend.DB = self._ruta
        backend.init_db()
        backend.app.config["TESTING"] = True
        self.client = backend.app.test_client()

    def tearDown(self):
        # Devuelve el backend a su BD original y borra la temporal
        backend.DB = self._db_original
        try:
            os.remove(self._ruta)
        except OSError:
            pass

    def enviar(self, ruta, texto):
        """Función para mandar un texto JSON tal cual a una ruta, como lo haría el ESP8266.
        Sirve también para mandar JSON dañado a propósito."""
        return self.client.post(ruta, data=texto, content_type="application/json")

    def contar(self, tabla):
        """Función para contar cuántas filas hay en una tabla de la BD temporal.
        Se usa para comprobar que un envío rechazado no guardó nada."""
        c = sqlite3.connect(self._ruta)
        n = c.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
        c.close()
        return n

    def insertar_lectura(self, temp, hum, creado):
        """Función para guardar una lectura con la fecha y hora elegidas (formato 'AAAA-MM-DD HH:MM:SS').
        Al enviar por la API, la fecha la pone el servidor; aquí se fija a mano para controlar el orden."""
        c = sqlite3.connect(self._ruta)
        c.execute("INSERT INTO lecturas(temperatura,humedad,creado) VALUES(?,?,?)", (temp, hum, creado))
        c.commit()
        c.close()

    def insertar_pomodoro(self, minutos, completado, creado):
        """Función para guardar un pomodoro de foco con la fecha y hora elegidas.
        completado=True lo marca como terminado y False como interrumpido."""
        c = sqlite3.connect(self._ruta)
        c.execute("INSERT INTO pomodoros(fase,duracion_min,completado,creado) VALUES('foco',?,?,?)",
                  (minutos, 1 if completado else 0, creado))
        c.commit()
        c.close()


# ---------------------------------------------------------------
# PARTE A: lo que dice el código del firmware
# ---------------------------------------------------------------
class TestFirmwareCompatibleConBackend(unittest.TestCase):
    """Pruebas que leen el .ino como texto y lo comparan con lo que acepta app.py."""

    @classmethod
    def setUpClass(cls):
        # Lee el firmware una sola vez para todas las pruebas de esta clase
        cls.src = leer_firmware()
        cls.codigo = cls.src
        cls.envios = envios_del_firmware(cls.src)

    def test_envia_solo_a_rutas_que_existen_en_el_backend(self):
        """Verifica que las rutas del .ino existan en Flask como POST.
        Si se cambia el nombre de una ruta en el .ino o en app.py, falla."""
        post_flask = {r.rule for r in backend.app.url_map.iter_rules() if "POST" in r.methods}
        self.assertEqual(set(self.envios), {"/api/lecturas", "/api/pomodoros"})
        self.assertTrue(set(self.envios) <= post_flask,
                        f"Rutas del .ino sin backend: {set(self.envios) - post_flask}")

    def test_claves_json_del_firmware(self):
        """Verifica los campos del JSON que arma el firmware:
        - lectura: exactamente temperatura y humedad,
        - pomodoro: exactamente fase, duracion_min y completado.
        Si se agrega o quita un campo en el .ino, falla y avisa que hay que
        actualizar json_lectura(), json_pomodoro() y el backend."""
        self.assertEqual(claves_json(self.envios["/api/lecturas"]), {"temperatura", "humedad"})
        self.assertEqual(claves_json(self.envios["/api/pomodoros"]),
                         {"fase", "duracion_min", "completado"})

    def test_solo_envia_pomodoros_de_foco(self):
        """Verifica que el firmware solo reporte la fase "foco".
        Si se empieza a enviar la fase "descanso", falla porque el panel no la espera."""
        arg = self.envios["/api/pomodoros"]
        self.assertIn('\\"fase\\":\\"foco\\"', arg)
        self.assertNotIn("descanso", arg.lower())

    def test_registra_pomodoro_completado_y_tambien_el_interrumpido_en_foco(self):
        """Verifica cuándo se registra un pomodoro.
        - Existe el registro de pomodoro terminado (true).
        - El pomodoro cancelado (false) solo se registra si el estado era FOCO.
        Si se quita la condición de FOCO, cancelar un descanso contaría como pomodoro interrumpido."""
        self.assertRegex(self.codigo, r'registrarPomodoro\s*\(\s*true\s*\)')
        self.assertRegex(self.codigo,
                         r'if\s*\(\s*estado\s*==\s*FOCO\s*\)\s*registrarPomodoro\s*\(\s*false\s*\)')

    def test_no_envia_nan_si_el_sensor_fallo(self):
        """Verifica que el firmware no envíe nada si temperatura o humedad son NaN.
        Si se quita esa revisión, un fallo del DHT11 mandaría "nan", que no es JSON válido."""
        self.assertRegex(self.codigo,
                         r'isnan\s*\(\s*temperatura\s*\)\s*\|\|\s*isnan\s*\(\s*humedad\s*\)\s*\)\s*return')

    def test_el_puerto_coincide_con_el_de_app_py(self):
        """Verifica que el puerto de SERVER_URL (.ino) sea igual al de app.run (app.py).
        Si se cambia el puerto en solo uno de los dos archivos, falla."""
        url = re.search(r'SERVER_URL\s*=\s*"([^"]+)"', self.codigo).group(1)
        puerto_ino = re.search(r':(\d+)$', url)
        self.assertIsNotNone(puerto_ino, f"SERVER_URL sin puerto: {url}")
        with open(backend.__file__, encoding="utf-8") as f:
            puerto_py = re.search(r'port\s*=\s*(\d+)', f.read())
        self.assertIsNotNone(puerto_py, "No se encontró port=... en app.py")
        self.assertEqual(puerto_ino.group(1), puerto_py.group(1))

    def test_sin_referencias_al_ldr(self):
        """Verifica que el código ya no use el sensor de luz (LDR).
        Si reaparece luz, ldr, leerLuz o analogRead en el archivo, falla.
        Incluye los comentarios: una mención vieja al LDR en un comentario también hace fallar."""
        m = re.search(r'\b(luz|ldr|pinLDR|leerLuz|nivelLuz|analogRead)\b', self.codigo, re.IGNORECASE)
        self.assertIsNone(m, f"El .ino todavía menciona: {m.group(0) if m else ''}")


# ---------------------------------------------------------------
# PARTE B: lo que hace el backend con esas señales
# ---------------------------------------------------------------
class TestSenalesDelESP8266(BaseAPI):
    """Pruebas que mandan al backend los mismos JSON que armaría el firmware."""

    @classmethod
    def setUpClass(cls):
        # Lee los tiempos de pomodoro del .ino para probar exactamente esos
        cls.presets = presets_del_firmware(leer_firmware())

    def stats(self):
        """Función para pedir /api/stats y verificar que responda 200.
        Devuelve el resultado ya convertido a diccionario."""
        r = self.client.get("/api/stats")
        self.assertEqual(r.status_code, 200)
        return r.get_json()

    def test_lectura_con_el_formato_exacto_del_firmware(self):
        """Verifica que una lectura con el formato del firmware se guarde bien.
        Si el backend deja de aceptar ese formato, falla."""
        r = self.enviar("/api/lecturas", json_lectura(24.3, 58))
        self.assertEqual(r.status_code, 201)
        fila = self.client.get("/api/lecturas").get_json()["datos"][0]
        self.assertEqual(fila["temperatura"], 24.3)
        self.assertEqual(fila["humedad"], 58)

    def test_extremos_del_sensor_dht11(self):
        """Verifica que se acepten los valores límite del DHT11 (0 a 50 °C, 20 a 90 % de humedad).
        Incluye 0.0 °C, que no debe confundirse con "dato faltante".
        Si el backend rechaza algún extremo, falla."""
        for t, h in [(0.0, 20), (50.0, 90), (25.0, 55)]:
            with self.subTest(temperatura=t, humedad=h):
                self.assertEqual(self.enviar("/api/lecturas", json_lectura(t, h)).status_code, 201)
        datos = self.client.get("/api/lecturas").get_json()["datos"]
        self.assertEqual([(d["temperatura"], d["humedad"]) for d in datos],
                         [(0.0, 20), (50.0, 90), (25.0, 55)])

    def test_rafaga_de_lecturas_se_guarda_completa_y_en_orden(self):
        """Verifica que 50 lecturas seguidas se guarden todas y en el orden en que llegaron.
        Si se pierde alguna o se desordenan, falla."""
        for i in range(50):
            self.assertEqual(self.enviar("/api/lecturas", json_lectura(20 + i / 10, 50)).status_code, 201)
        r = self.client.get("/api/lecturas").get_json()
        self.assertEqual(r["modo"], "raw")
        self.assertEqual(len(r["datos"]), 50)
        self.assertEqual(r["datos"][0]["temperatura"], 20.0)
        self.assertEqual(r["datos"][-1]["temperatura"], 24.9)

    def test_cada_preset_del_firmware_se_guarda_y_suma_minutos(self):
        """Verifica cada tiempo de pomodoro del firmware (por ejemplo 15, 25 y 45 min).
        Primero comprueba que presets[] se haya podido leer del .ino; si no, falla.
        Por cada tiempo se envía un pomodoro terminado y uno cancelado y se revisa que:
        - el total y los completados sean correctos,
        - solo los terminados sumen minutos de foco,
        - cada duración aparezca con 2 pomodoros y 1 completado.
        Si se cambia un preset en el .ino, la prueba se adapta sola."""
        self.assertTrue(self.presets, "No se pudo leer presets[] del firmware")
        for p in self.presets:
            self.assertEqual(self.enviar("/api/pomodoros", json_pomodoro(p, True)).status_code, 201)
            self.assertEqual(self.enviar("/api/pomodoros", json_pomodoro(p, False)).status_code, 201)
        s = self.stats()
        n = len(self.presets)
        self.assertEqual(s["pomodoros"]["total"], 2 * n)
        self.assertEqual(s["pomodoros"]["completados"], n)
        self.assertEqual(s["pomodoros"]["minutos_foco"], sum(self.presets))
        por_dur = {d["dur"]: d for d in s["por_duracion"]}
        for p in self.presets:
            self.assertEqual((por_dur[p]["total"], por_dur[p]["ok"]), (2, 1))

    def test_pomodoro_interrumpido_no_suma_minutos(self):
        """Verifica que un pomodoro cancelado cuente en el total pero no sume minutos de foco.
        Si empieza a sumar minutos, las estadísticas quedarían infladas."""
        self.enviar("/api/pomodoros", json_pomodoro(25, False))
        p = self.stats()["pomodoros"]
        self.assertEqual((p["total"], p["completados"], p["minutos_foco"]), (1, 0, 0))

    def test_json_truncado_por_timeout_se_rechaza_y_no_guarda_nada(self):
        """Verifica qué pasa si el mensaje llega cortado (por ejemplo, se cae el WiFi a la mitad).
        Debe responder error 400 y no guardar ninguna fila.
        Si el backend guarda datos a medias, falla."""
        self.assertEqual(self.enviar("/api/lecturas", '{"temperatura":24.3,"hum').status_code, 400)
        self.assertEqual(self.enviar("/api/pomodoros", '{"fase":"foco","duracion_min":25,"comp').status_code, 400)
        self.assertEqual((self.contar("lecturas"), self.contar("pomodoros")), (0, 0))

    def test_valores_nan_se_rechazan(self):
        """Verifica que una lectura con "nan" (sensor fallido) se rechace y no se guarde.
        Es la segunda barrera: la primera está en el firmware, que no debería enviarla."""
        r = self.enviar("/api/lecturas", '{"temperatura":nan,"humedad":nan}')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(self.contar("lecturas"), 0)

    def test_sesion_completa_se_refleja_en_el_panel(self):
        """Verifica una sesión completa como la haría el ESP8266:
        lectura, pomodoro terminado, lectura, pomodoro cancelado.
        Después revisa que el panel muestre:
        - la última temperatura enviada,
        - el número de lecturas,
        - totales, completados, minutos de foco y tasa (50 %),
        - la lista de pomodoros con el más reciente primero,
        - el resumen del día.
        Si algo del flujo completo se rompe, falla."""
        self.enviar("/api/lecturas", json_lectura(22.0, 50))
        self.enviar("/api/pomodoros", json_pomodoro(25, True))
        self.enviar("/api/lecturas", json_lectura(31.5, 45))
        self.enviar("/api/pomodoros", json_pomodoro(45, False))

        s = self.stats()
        self.assertEqual(s["ultima"]["temperatura"], 31.5)
        self.assertEqual(s["promedios"]["n"], 2)
        self.assertEqual(s["pomodoros"]["total"], 2)
        self.assertEqual(s["pomodoros"]["completados"], 1)
        self.assertEqual(s["pomodoros"]["minutos_foco"], 25)
        self.assertEqual(s["pomodoros"]["tasa"], 50.0)

        lista = self.client.get("/api/pomodoros").get_json()
        self.assertEqual([(p["duracion_min"], p["completado"]) for p in lista], [(45, 0), (25, 1)])

        resumen = self.client.get("/api/resumen")
        self.assertEqual(resumen.status_code, 200)
        self.assertIn("nivel", resumen.get_json()["hoy"])


# ---------------------------------------------------------------
# PARTE C: protecciones y cálculos clave del backend
# ---------------------------------------------------------------
class TestProteccionesYCalculos(BaseAPI):
    """Pruebas de lo que protege los datos y de las cifras principales del panel."""

    def test_demo_exige_confirmacion_y_no_borra_nada(self):
        """Verifica que /api/demo sin ?reemplazar=1 responda error 400 y no toque los datos.
        Esa ruta borra todo lo guardado; si se quita la confirmación, un clic por accidente
        perdería los datos reales y esta prueba falla."""
        self.insertar_lectura(22, 50, "2026-03-01 08:00:00")
        r = self.client.post("/api/demo")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(self.contar("lecturas"), 1)

    def test_panel_con_base_de_datos_vacia_no_se_cae(self):
        """Verifica que /api/stats responda bien cuando todavía no hay ningún dato.
        Es lo que ocurre la primera vez que se abre el panel, antes de que llegue algo del Arduino.
        Debe dar totales en 0, ninguna última lectura y nivel "sin_datos".
        Si hay una división entre cero o un dato vacío mal manejado, falla."""
        r = self.client.get("/api/stats")
        self.assertEqual(r.status_code, 200)
        s = r.get_json()
        self.assertEqual(s["pomodoros"]["total"], 0)
        self.assertEqual(s["pomodoros"]["tasa"], 0)
        self.assertIsNone(s["ultima"])
        self.assertEqual(s["interpretacion"]["nivel"], "sin_datos")

    def test_filtro_por_fechas_solo_devuelve_ese_rango(self):
        """Verifica que ?desde=...&hasta=... devuelva solo las lecturas de ese rango.
        Los botones de hoy, semana y mes del panel dependen de esto.
        Si el filtro falla, las gráficas mezclarían días que no corresponden."""
        self.insertar_lectura(22, 50, "2026-03-01 08:00:00")
        self.insertar_lectura(25, 52, "2026-03-10 08:00:00")
        r = self.client.get("/api/lecturas?desde=2026-03-05&hasta=2026-03-31").get_json()
        self.assertEqual(len(r["datos"]), 1)
        self.assertEqual(r["datos"][0]["temperatura"], 25)

    def test_porcentaje_de_confort(self):
        """Verifica el cálculo del porcentaje de tiempo en rango cómodo (20 a 26 °C y 40 a 60 % de humedad).
        Con una lectura cómoda (22 °C, 50 %) y una no cómoda (30 °C, 50 %), debe dar 50 %.
        Si cambia el cálculo o los rangos, falla."""
        self.insertar_lectura(22, 50, "2026-03-10 07:00:00")
        self.insertar_lectura(30, 50, "2026-03-10 07:30:00")
        s = self.client.get("/api/stats").get_json()
        self.assertEqual(s["confort_pct"], 50.0)

    def test_efecto_de_la_temperatura_en_los_pomodoros(self):
        """Verifica la relación entre la temperatura y terminar el pomodoro.
        Cada pomodoro se compara con la última lectura anterior a su inicio:
        - con 22 °C (zona de confort) el pomodoro se termina: tasa 100 %,
        - con 31 °C (fuera de confort) se interrumpe: tasa 0 %.
        Es la pregunta central del proyecto; si el cálculo falla, el panel muestra conclusiones erróneas."""
        self.insertar_lectura(22, 50, "2026-03-10 08:00:00")
        self.insertar_pomodoro(25, True, "2026-03-10 08:10:00")
        self.insertar_lectura(31, 50, "2026-03-10 12:00:00")
        self.insertar_pomodoro(25, False, "2026-03-10 12:10:00")
        ef = {e["zona"]: e for e in self.client.get("/api/stats").get_json()["efecto_temperatura"]}
        self.assertEqual(ef["confort"]["tasa"], 100)
        self.assertEqual(ef["fuera"]["tasa"], 0)
        self.assertEqual(ef["confort"]["total"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
