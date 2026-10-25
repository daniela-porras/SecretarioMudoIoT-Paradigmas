"""Secretario Mudo IoT - Backend (Flask + SQLite)
Ejecutar:  pip install flask flask-cors  &&  python app.py
Escucha en 0.0.0.0:5000 para que el ESP8266 lo alcance por la red local.
"""
import math, os, random, sqlite3
from datetime import datetime, timedelta, date, time as dtime
from flask import Flask, jsonify, request, send_from_directory, g
from flask_cors import CORS

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "secretario.db")
WEB = os.path.join(BASE, "..", "web")

app = Flask(__name__, static_folder=None)
CORS(app)

def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(_):
    d = g.pop("db", None)
    if d: d.close()

def init_db():
    c = sqlite3.connect(DB)
    c.executescript("""
    CREATE TABLE IF NOT EXISTS lecturas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dispositivo TEXT DEFAULT 'secretario-1',
        temperatura REAL, humedad REAL, luz INTEGER,
        creado TEXT DEFAULT (datetime('now','localtime')));
    CREATE TABLE IF NOT EXISTS epocas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        inicio TEXT NOT NULL,              -- YYYY-MM-DD
        fin TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS pomodoros(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dispositivo TEXT DEFAULT 'secretario-1',
        fase TEXT DEFAULT 'foco',          -- foco | descanso
        duracion_min INTEGER,              -- 15 | 25 | 45
        completado INTEGER DEFAULT 1,      -- 1 terminó, 0 se interrumpió
        creado TEXT DEFAULT (datetime('now','localtime')));
    """)
    c.commit(); c.close()

# ---------- Recepción desde el ESP8266 ----------
@app.post("/api/lecturas")
def post_lectura():
    d = request.get_json(force=True, silent=True) or {}
    if "temperatura" not in d or "humedad" not in d:
        return jsonify(error="Faltan campos: temperatura, humedad"), 400
    db().execute("INSERT INTO lecturas(dispositivo,temperatura,humedad,luz) VALUES(?,?,?,?)",
                 (d.get("dispositivo", "secretario-1"), d["temperatura"], d["humedad"], d.get("luz")))
    db().commit()
    return jsonify(ok=True), 201

@app.post("/api/pomodoros")
def post_pomodoro():
    d = request.get_json(force=True, silent=True) or {}
    if "duracion_min" not in d:
        return jsonify(error="Falta el campo: duracion_min"), 400
    db().execute("INSERT INTO pomodoros(dispositivo,fase,duracion_min,completado) VALUES(?,?,?,?)",
                 (d.get("dispositivo", "secretario-1"), d.get("fase", "foco"),
                  d["duracion_min"], 1 if d.get("completado", True) else 0))
    db().commit()
    return jsonify(ok=True), 201

# ---------- Consulta para el dashboard (con filtros de fecha) ----------
def filtro(desde, hasta, col="creado"):
    """Fragmento SQL (empieza con ' AND ') + argumentos para limitar por fechas."""
    f, a = "", []
    if desde: f += f" AND date({col}) >= ?"; a.append(desde)
    if hasta: f += f" AND date({col}) <= ?"; a.append(hasta)
    return f, a

def calcular(desde, hasta):
    q = lambda s, a: db().execute(s, a).fetchone()
    qa = lambda s, a: db().execute(s, a).fetchall()
    f, a = filtro(desde, hasta)
    fp, ap = filtro(desde, hasta, "p.creado")
    prom = q(f"SELECT AVG(temperatura) t, AVG(humedad) h, MIN(temperatura) tmin, MAX(temperatura) tmax, COUNT(*) n FROM lecturas WHERE 1=1{f}", a)
    confort = q(f"""SELECT AVG(CASE WHEN temperatura BETWEEN 20 AND 26 AND humedad BETWEEN 40 AND 60
                   THEN 1.0 ELSE 0 END)*100 p FROM lecturas WHERE 1=1{f}""", a)
    pom = q(f"""SELECT COUNT(*) total, SUM(completado) ok,
               SUM(CASE WHEN completado=1 THEN duracion_min ELSE 0 END) min_foco
               FROM pomodoros WHERE fase='foco'{f}""", a)
    por_dia = qa(f"""SELECT date(creado) dia, COUNT(*) total, SUM(completado) ok,
               SUM(CASE WHEN completado=1 THEN duracion_min ELSE 0 END) minutos
               FROM pomodoros WHERE fase='foco'{f} GROUP BY dia ORDER BY dia""", a)
    por_dur = qa(f"""SELECT duracion_min dur, COUNT(*) total, SUM(completado) ok
               FROM pomodoros WHERE fase='foco'{f} GROUP BY dur ORDER BY dur""", a)
    efecto = qa(f"""
        SELECT CASE WHEN l.temperatura BETWEEN 20 AND 26 THEN 'confort' ELSE 'fuera' END zona,
               COUNT(*) total, AVG(p.completado)*100 tasa
        FROM pomodoros p JOIN lecturas l ON l.id =
          (SELECT id FROM lecturas WHERE creado <= p.creado ORDER BY creado DESC LIMIT 1)
        WHERE p.fase='foco'{fp} GROUP BY zona""", ap)
    total = pom["total"] or 0
    return dict(
        promedios=dict(prom),
        confort_pct=round(confort["p"] or 0, 1),
        pomodoros=dict(total=total, completados=pom["ok"] or 0,
                       tasa=round((pom["ok"] or 0) / total * 100, 1) if total else 0,
                       minutos_foco=pom["min_foco"] or 0),
        por_dia=[dict(r) for r in por_dia],
        por_duracion=[dict(r) for r in por_dur],
        efecto_temperatura=[dict(r) for r in efecto])

def rango():
    return request.args.get("desde"), request.args.get("hasta")

@app.get("/api/lecturas")
def get_lecturas():
    desde, hasta = rango()
    f, a = filtro(desde, hasta)
    # Agrupación automática para que el gráfico no se sature con rangos largos
    r = db().execute(f"SELECT MIN(date(creado)) a, MAX(date(creado)) b FROM lecturas WHERE 1=1{f}", a).fetchone()
    dias = 1
    if r["a"]:
        dias = (datetime.fromisoformat(r["b"]) - datetime.fromisoformat(r["a"])).days + 1
    modo = "raw" if dias <= 1 else ("hora" if dias <= 14 else "dia")
    if modo == "raw":
        rows = db().execute(f"SELECT * FROM lecturas WHERE 1=1{f} ORDER BY id DESC LIMIT 2000", a).fetchall()
        datos = [dict(x) for x in reversed(rows)]
    else:
        fmt = "%Y-%m-%d %H:00" if modo == "hora" else "%Y-%m-%d"
        rows = db().execute(f"""SELECT strftime('{fmt}', creado) creado, AVG(temperatura) temperatura,
                 AVG(humedad) humedad, AVG(luz) luz FROM lecturas WHERE 1=1{f}
                 GROUP BY 1 ORDER BY 1""", a).fetchall()
        datos = [dict(x) for x in rows]
    return jsonify(modo=modo, datos=datos)

@app.get("/api/pomodoros")
def get_pomodoros():
    desde, hasta = rango()
    f, a = filtro(desde, hasta)
    rows = db().execute(f"SELECT * FROM pomodoros WHERE 1=1{f} ORDER BY id DESC LIMIT 200", a).fetchall()
    return jsonify([dict(r) for r in rows])

def periodo_previo(desde, hasta):
    """Periodo inmediatamente anterior y de la misma duración (para comparar)."""
    if not desde:
        return None
    d0 = date.fromisoformat(desde)
    d1 = date.fromisoformat(hasta) if hasta else date.today()
    n = max(1, (d1 - d0).days + 1)
    return str(d0 - timedelta(days=n)), str(d0 - timedelta(days=1))

@app.get("/api/stats")
def stats():
    desde, hasta = rango()
    ult = db().execute("SELECT * FROM lecturas ORDER BY id DESC LIMIT 1").fetchone()
    out = calcular(desde, hasta)
    out["ultima"] = dict(ult) if ult else None
    prev = periodo_previo(desde, hasta) if request.args.get("ref", "todo") != "todo" else None
    out["anterior"] = None
    if prev:
        pc = calcular(*prev)
        if pc["pomodoros"]["total"] or pc["promedios"]["n"]:
            out["anterior"] = dict(minutos_foco=pc["pomodoros"]["minutos_foco"], tasa=pc["pomodoros"]["tasa"],
                                   pomodoros=pc["pomodoros"]["total"], confort_pct=pc["confort_pct"])
    out["interpretacion"] = interpretar(desde, hasta, request.args.get("ref", "todo"), request.args.get("nombre"))
    return jsonify(out)

# ---------- Interpretación automática de los resultados ----------
# Reglas simples y ajustables (no usa IA): puntúa constancia, minutos de foco y pomodoros terminados.
META_DIA = 100   # minutos de foco completados por día que se consideran "meta" (~4 pomodoros de 25 min)
SUJETO = {"hoy": "Hoy", "semana": "Esta semana", "mes": "Este mes", "todo": "En todo el historial"}
ETIQUETA = {"excelente": "muy bien", "bien": "buen ritmo", "regular": "irregular", "bajo": "poco", "sin_datos": "sin datos"}

def hm(m):
    return f"{m} min" if m < 60 else f"{m // 60} h {m % 60:02d} min"

def interpretar(desde, hasta, ref="todo", nombre=None):
    hoy = date.today()
    c = calcular(desde, hasta)
    p = c["pomodoros"]
    sujeto = f"En «{nombre}»" if ref == "epoca" and nombre else SUJETO.get(ref, "En este periodo")
    if p["total"] == 0:
        return dict(nivel="sin_datos", etiqueta=ETIQUETA["sin_datos"],
                    titulo="Todavía no hay datos de estudio en este periodo.", puntos=[],
                    consejo="Inicia un Pomodoro en el Secretario Mudo y aquí aparecerá tu análisis.")
    primero = db().execute("SELECT MIN(date(creado)) m FROM pomodoros").fetchone()["m"]
    d0 = date.fromisoformat(desde) if desde else date.fromisoformat(primero)
    d1 = min(date.fromisoformat(hasta), hoy) if hasta else hoy
    dias = max(1, (d1 - d0).days + 1)
    activos = sum(1 for d in c["por_dia"] if d["minutos"] > 0)
    mins, tasa = p["minutos_foco"], p["tasa"]
    cumpl = min(mins / (META_DIA * dias), 1)
    const = activos / dias
    score = .5 * cumpl + .3 * tasa / 100 + .2 * const
    nivel = "excelente" if score >= .75 else "bien" if score >= .55 else "regular" if score >= .35 else "bajo"

    titulo = {"excelente": f"{sujeto} has estudiado muy bien.",
              "bien": f"{sujeto} has llevado un buen ritmo de estudio.",
              "regular": f"{sujeto} tu estudio ha sido irregular.",
              "bajo": f"{sujeto} has estudiado poco."}[nivel]
    if nivel == "excelente" and tasa >= 85:
        titulo = f"{sujeto} has estado muy concentrado y has estudiado muy bien."
    if ref == "hoy" and nivel in ("regular", "bajo") and datetime.now().hour < 14:
        titulo = f"Hoy vas empezando: ya llevas {hm(mins)} de foco."

    pts = [f"{hm(mins)} de foco completados; terminaste {p['completados']} de {p['total']} pomodoros sin interrumpir ({tasa} %)."]
    if dias > 1:
        pts.append(f"Estudiaste {activos} de {dias} días, con un promedio de {hm(round(mins / max(activos, 1)))} por día activo.")
        if len(c["por_dia"]) > 1:
            mejor = max(c["por_dia"], key=lambda d: d["minutos"])
            pts.append(f"Tu mejor día fue el {mejor['dia']}, con {hm(mejor['minutos'])} de foco.")
    # Comparación con el periodo anterior de la misma duración
    if desde and ref != "todo":
        pc = calcular(str(d0 - timedelta(days=dias)), str(d0 - timedelta(days=1)))["pomodoros"]["minutos_foco"]
        if pc > 0:
            if ref == "hoy":
                pts.append(f"Ayer completaste {hm(pc)} de foco.")
            else:
                cambio = round((mins - pc) / pc * 100)
                if abs(cambio) >= 5:
                    pts.append(f"Hiciste un {abs(cambio)} % {'más' if cambio > 0 else 'menos'} de foco que en el periodo anterior ({hm(pc)}).")
                else:
                    pts.append(f"Tu foco es parecido al del periodo anterior ({hm(pc)}).")
    # Duración favorita
    durs = [d for d in c["por_duracion"] if d["total"] >= 3]
    if len(durs) >= 2:
        b = max(durs, key=lambda d: d["ok"] / d["total"])
        pts.append(f"Terminas más a menudo los pomodoros de {b['dur']} min ({round(b['ok'] / b['total'] * 100)} %).")
    # Ambiente
    t, conf = c["promedios"]["t"], c["confort_pct"]
    if t is not None:
        if conf >= 60:
            pts.append(f"El ambiente fue favorable: {conf} % del tiempo dentro del rango confortable.")
        elif conf < 40:
            pts.append(f"El ambiente estuvo fuera del rango confortable el {round(100 - conf)} % del tiempo (temperatura media {t:.1f} °C).")
    ef = {e["zona"]: e for e in c["efecto_temperatura"]}
    if "confort" in ef and "fuera" in ef and min(ef["confort"]["total"], ef["fuera"]["total"]) >= 5 \
            and ef["confort"]["tasa"] - ef["fuera"]["tasa"] >= 8:
        pts.append(f"Con 20–26 °C terminaste el {round(ef['confort']['tasa'])} % de tus pomodoros, frente al {round(ef['fuera']['tasa'])} % fuera de ese rango.")

    # Sugerencia (la primera que aplique)
    if tasa < 70:
        consejo = "Se interrumpen muchos pomodoros. Prueba con bloques de 15 min para ganar ritmo y deja el celular lejos."
    elif t is not None and t > 28:
        consejo = "Hace calor en el escritorio y eso baja la concentración. Ventila o refresca el espacio."
    elif dias > 3 and const < .5:
        consejo = "Estudiaste pocos días. Intenta hacer aunque sean 1 o 2 pomodoros cada día."
    elif cumpl < .5:
        consejo = f"Apunta a {META_DIA} min de foco al día (unos 4 pomodoros de 25 min)."
    else:
        consejo = "Sigue así y respeta los descansos de 5 minutos."
    return dict(nivel=nivel, etiqueta=ETIQUETA[nivel], titulo=titulo, puntos=pts, consejo=consejo,
                minutos_foco=mins, puntaje=round(score, 2))

@app.get("/api/resumen")
def resumen():
    hoy = date.today()
    rangos = {"hoy": 0, "semana": 6, "mes": 29}
    return jsonify({k: interpretar(str(hoy - timedelta(days=n)), str(hoy), k) for k, n in rangos.items()})

# ---------- Épocas de estudio (periodos largos con nombre) ----------
@app.get("/api/epocas")
def get_epocas():
    res = []
    for e in db().execute("SELECT * FROM epocas ORDER BY inicio DESC").fetchall():
        c = calcular(e["inicio"], e["fin"])
        res.append(dict(e, minutos_foco=c["pomodoros"]["minutos_foco"], tasa=c["pomodoros"]["tasa"],
                        pomodoros=c["pomodoros"]["total"], temp=c["promedios"]["t"],
                        confort_pct=c["confort_pct"]))
    return jsonify(res)

@app.post("/api/epocas")
def post_epoca():
    d = request.get_json(force=True, silent=True) or {}
    nombre, ini, fin = (d.get("nombre") or "").strip(), d.get("inicio"), d.get("fin")
    try:
        ok = datetime.fromisoformat(ini) <= datetime.fromisoformat(fin)
    except (TypeError, ValueError):
        ok = False
    if not nombre or not ok:
        return jsonify(error="Escribe un nombre y fechas válidas (inicio no puede ser posterior al fin)."), 400
    db().execute("INSERT INTO epocas(nombre,inicio,fin) VALUES(?,?,?)", (nombre, ini, fin))
    db().commit()
    return jsonify(ok=True), 201

@app.delete("/api/epocas/<int:eid>")
def delete_epoca(eid):
    db().execute("DELETE FROM epocas WHERE id=?", (eid,))
    db().commit()
    return jsonify(ok=True)

# ---------- Datos de prueba (para desarrollar sin el hardware) ----------
@app.post("/api/demo")
def demo():
    """Borra TODO y genera ~4 meses de datos de prueba (para desarrollar sin el hardware)."""
    if request.args.get("reemplazar") != "1":
        return jsonify(error="Esto borra los datos actuales. Llama a /api/demo?reemplazar=1"), 400
    DIAS = 120
    now = datetime.now().replace(second=0, microsecond=0)
    hoy = now.date()
    c = db()
    for t in ("lecturas", "pomodoros", "epocas"):
        c.execute(f"DELETE FROM {t}")
    dias = [hoy - timedelta(days=i) for i in range(DIAS + 1)]
    off = {d: random.uniform(-2.5, 2.5) for d in dias}     # días más frescos o calurosos
    hoff = {d: random.uniform(-8, 8) for d in dias}

    def temp(t):
        h = t.hour + t.minute / 60
        return 24 + off[t.date()] + 4 * math.sin((h - 9) / 24 * 2 * math.pi)

    lect = []
    for i in range(DIAS * 48):
        t = now - timedelta(minutes=30 * i)
        h = t.hour + t.minute / 60
        luz = 900 if 7 <= h < 17 else 450 if 17 <= h < 20 else 120
        lect.append((round(temp(t) + random.uniform(-.5, .5), 1),
                     round(min(85, max(30, 55 + hoff[t.date()] + random.uniform(-4, 4))), 1),
                     int(min(1023, max(0, luz + random.uniform(-80, 80)))),
                     t.strftime("%Y-%m-%d %H:%M:%S")))
    c.executemany("INSERT INTO lecturas(temperatura,humedad,luz,creado) VALUES(?,?,?,?)", lect)

    EPOCAS = [("Parciales I", 100, 92), ("Proyecto de curso", 70, 56),
              ("Parciales II", 40, 32), ("Exámenes finales", 14, 4)]
    rangos = [(hoy - timedelta(days=a), hoy - timedelta(days=b)) for _, a, b in EPOCAS]
    en_epoca = lambda d: any(i <= d <= f for i, f in rangos)
    semana = {}
    pom = []
    for d in reversed(dias):
        fs = semana.setdefault(d.isocalendar()[:2], random.uniform(.25, 1.25))  # semanas buenas y malas
        finde = d.weekday() >= 5
        fac = (max(fs, .8) * 1.5 if en_epoca(d) else fs) * (0.5 if finde else 1)
        if not en_epoca(d) and random.random() < (0.35 if finde else 0.15):
            continue                                                            # día sin estudiar
        nses = max(1, round(random.uniform(.6, 1.7) * fac))
        for h in sorted(random.sample([8, 9, 10, 14, 15, 16, 19, 20, 21], k=min(nses, 9))):
            t = datetime.combine(d, dtime(h, random.randint(0, 40)))
            for _ in range(max(1, round(random.uniform(1.5, 3.5) * min(fac, 1.3)))):
                if t > now:
                    break
                dur = random.choice([25, 25, 25, 45, 15])
                p_ok = (0.9 if 20 <= temp(t) <= 26 else 0.68) + (0.05 if fac >= 1 else -0.05)
                pom.append((dur, 1 if random.random() < p_ok else 0, t.strftime("%Y-%m-%d %H:%M:%S")))
                t += timedelta(minutes=dur + 5)
    c.executemany("INSERT INTO pomodoros(fase,duracion_min,completado,creado) VALUES('foco',?,?,?)", pom)
    for (nom, _, _), (i, f) in zip(EPOCAS, rangos):
        c.execute("INSERT INTO epocas(nombre,inicio,fin) VALUES(?,?,?)", (nom, str(i), str(f)))
    c.commit()
    return jsonify(ok=True, lecturas=len(lect), pomodoros=len(pom), dias=DIAS)

@app.get("/")
def index():
    return send_from_directory(WEB, "index.html")

@app.get("/<path:f>")
def static_files(f):
    return send_from_directory(WEB, f)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)