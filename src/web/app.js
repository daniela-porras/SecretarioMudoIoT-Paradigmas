// =========================================================
// Secretario Mudo - Panel
// =========================================================
const $ = id => document.getElementById(id);
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const API = ""; // vacío = mismo servidor que sirve la página

// ---------- 1. Utilidades ----------
const esc = s => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const iso = d => d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
const haceDias = n => { const d = new Date(); d.setDate(d.getDate() - n); return d; };
const hm = m => m < 60 ? `${m} min` : `${Math.floor(m / 60)} h ${String(m % 60).padStart(2, "0")} min`;

// ---------- 2. Filtro de periodo ----------
const PRESETS = {
  hoy:   { label: "Hoy",               ref: "hoy",    rango: () => [iso(new Date()), iso(new Date())] },
  "7d":  { label: "Última semana",     ref: "semana", rango: () => [iso(haceDias(6)), iso(new Date())] },
  "30d": { label: "Último mes",        ref: "mes",    rango: () => [iso(haceDias(29)), iso(new Date())] },
  todo:  { label: "Todo el historial", ref: "todo",   rango: () => [null, null] }
};
let filtro = { key: "todo", desde: null, hasta: null, label: PRESETS.todo.label, ref: "todo" };

function qs() {
  const p = new URLSearchParams();
  if (filtro.desde) p.set("desde", filtro.desde);
  if (filtro.hasta) p.set("hasta", filtro.hasta);
  return p.toString();
}
function qStats() {
  const p = new URLSearchParams(qs());
  p.set("ref", filtro.ref); p.set("nombre", filtro.label);
  return p.toString();
}
function aplicarFiltro(key, desde, hasta, label) {
  filtro = { key, desde, hasta, label, ref: PRESETS[key]?.ref || "epoca" };
  document.querySelectorAll("#seg button").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.f === key)));
  if (!key.startsWith("epoca:")) $("selEpoca").value = "";
  $("periodo").textContent = "Mostrando: " + label + (desde ? ` (${desde}${hasta !== desde ? " a " + hasta : ""})` : "");
  cargar();
}
document.querySelectorAll("#seg button").forEach(b => b.onclick = () => {
  const p = PRESETS[b.dataset.f]; const [d, h] = p.rango(); aplicarFiltro(b.dataset.f, d, h, p.label);
});

// ---------- 3. Gráficos ----------
const charts = {};
const fusionar = (a, b) => {
  for (const k in b) a[k] = (b[k] && typeof b[k] === "object" && !Array.isArray(b[k])) ? fusionar(a[k] || {}, b[k]) : b[k];
  return a;
};
function chart(id, cfg) {
  const refresco = !!charts[id];
  if (refresco) charts[id].destroy();
  Chart.defaults.font.family = '"IBM Plex Sans", system-ui, sans-serif';
  Chart.defaults.font.size = 12;
  Chart.defaults.color = css("--suave");
  const base = {
    maintainAspectRatio: false,
    animation: refresco ? false : undefined,
    interaction: { mode: "index", intersect: false },
    plugins: {
      legend: { position: "top", align: "start", labels: { usePointStyle: true, boxWidth: 8, boxHeight: 8 } },
      tooltip: { backgroundColor: "#1f2933", padding: 10, cornerRadius: 6, boxPadding: 4 }
    },
    scales: {
      x: { grid: { display: false }, border: { color: css("--linea") }, ticks: { maxTicksLimit: 8, maxRotation: 0 } },
      y: { grid: { color: css("--linea") }, border: { display: false }, beginAtZero: true }
    }
  };
  charts[id] = new Chart($(id), { type: cfg.type, data: cfg.data, options: fusionar(base, cfg.options || {}) });
}

// ---------- 4. Carga de datos ----------
function delta(id, actual, previo, tipo) {
  const el = $(id);
  el.textContent = "";
  if (previo == null) return;
  const cambio = tipo === "pct" ? (previo > 0 ? Math.round((actual - previo) / previo * 100) : null) : Math.round(actual - previo);
  if (cambio == null) return;
  const b = document.createElement("b");
  if (cambio === 0) { b.textContent = "Sin cambios "; }
  else {
    b.className = cambio > 0 ? "sube" : "baja";
    b.textContent = (cambio > 0 ? "▲ " : "▼ ") + Math.abs(cambio) + (tipo === "pct" ? " %" : " pts") + " ";
  }
  el.append(b, filtro.ref === "hoy" ? "vs ayer" : "vs periodo anterior");
}

async function cargar() {
  let l, s;
  try {
    [l, s] = await Promise.all([
      fetch(API + "/api/lecturas?" + qs()).then(r => r.json()),
      fetch(API + "/api/stats?" + qStats()).then(r => r.json())
    ]);
  } catch (e) {
    $("dotConexion").className = "dot mal";
    $("estado").textContent = "Sin conexión con el servidor. Revisa que app.py esté corriendo.";
    return;
  }
  try {
    const datos = l.datos;
    const etiqueta = x => l.modo === "dia" ? x.creado.slice(5) : x.creado.slice(5, 16).replace("-", "/");

    $("dotConexion").className = "dot ok";
    $("estado").textContent = s.ultima ? "Conectado · datos del dispositivo" : "Conectado · aún no hay datos";

    // Ahora mismo
    if (s.ultima) {
      const u = s.ultima;
      $("tNow").textContent = u.temperatura.toFixed(1);
      $("hNow").textContent = u.humedad.toFixed(0);
      $("lNow").textContent = u.luz ?? "–";
      $("ultima").textContent = "Última lectura: " + u.creado;
      const confort = u.temperatura >= 20 && u.temperatura <= 26 && u.humedad >= 40 && u.humedad <= 60;
      const fuera = u.temperatura > 28 || u.temperatura < 18;
      $("led").className = "dot " + (confort ? "ok" : fuera ? "mal" : "alerta");
      $("ahoraTxt").textContent = confort ? "Ambiente confortable" : fuera ? "Fuera del rango recomendado" : "Ambiente aceptable";
    } else {
      ["tNow", "hNow", "lNow"].forEach(i => $(i).textContent = "–");
      $("led").className = "dot"; $("ahoraTxt").textContent = "Sin lecturas"; $("ultima").textContent = "";
    }

    // Resultados del periodo
    const p = s.pomodoros, ant = s.anterior;
    $("kFoco").textContent = p.minutos_foco;
    $("kFocoSub").textContent = p.minutos_foco >= 60 ? "≈ " + hm(p.minutos_foco) + " completados" : "Pomodoros completados";
    $("kTasa").textContent = p.tasa;
    $("kTasaSub").textContent = `${p.completados} de ${p.total} sin interrumpir`;
    $("kConfort").textContent = s.confort_pct;
    $("kPom").textContent = p.total;
    delta("dFoco", p.minutos_foco, ant?.minutos_foco, "pct");
    delta("dTasa", p.tasa, ant ? ant.tasa : null, "pts");
    delta("dConfort", s.confort_pct, ant ? ant.confort_pct : null, "pts");
    delta("dPom", p.total, ant?.pomodoros, "pct");
    renderInterp(s.interpretacion);

    const azul = css("--azul"), gris = "#c3cad4", naranja = "#e8710a";

    chart("cDia", { type: "bar", data: { labels: s.por_dia.map(d => d.dia.slice(5)),
      datasets: [{ label: "Minutos de foco", data: s.por_dia.map(d => d.minutos), backgroundColor: azul, borderRadius: 3, maxBarThickness: 28 }] },
      options: { plugins: { legend: { display: false } } } });

    chart("cDur", { type: "bar", data: { labels: s.por_duracion.map(d => d.dur + " min"),
      datasets: [{ label: "Terminados", data: s.por_duracion.map(d => d.ok), backgroundColor: azul, maxBarThickness: 48 },
                 { label: "Interrumpidos", data: s.por_duracion.map(d => d.total - d.ok), backgroundColor: gris, maxBarThickness: 48 }] },
      options: { scales: { x: { stacked: true }, y: { stacked: true } } } });

    chart("cClima", { type: "line", data: { labels: datos.map(etiqueta), datasets: [
      { label: "Temperatura (°C)", data: datos.map(x => x.temperatura), borderColor: naranja, borderWidth: 2, pointRadius: 0, tension: .3, yAxisID: "y" },
      { label: "Humedad (%)", data: datos.map(x => x.humedad), borderColor: azul, borderWidth: 2, pointRadius: 0, tension: .3, yAxisID: "y1" }] },
      options: { scales: { y: { beginAtZero: false, title: { display: true, text: "°C" } },
                           y1: { position: "right", beginAtZero: false, grid: { display: false }, border: { display: false }, title: { display: true, text: "%" } } } } });

    chart("cEfecto", { type: "bar", data: { labels: s.efecto_temperatura.map(e => e.zona === "confort" ? "Entre 20 y 26 °C" : "Fuera de ese rango"),
      datasets: [{ label: "% terminados", data: s.efecto_temperatura.map(e => +e.tasa.toFixed(1)),
                   backgroundColor: s.efecto_temperatura.map(e => e.zona === "confort" ? azul : gris), maxBarThickness: 64 }] },
      options: { indexAxis: "y", plugins: { legend: { display: false } },
                 scales: { x: { min: 0, max: 100, grid: { color: css("--linea") }, ticks: { callback: v => v + " %" } }, y: { grid: { display: false } } } } });

    chart("cLuz", { type: "line", data: { labels: datos.map(etiqueta), datasets: [
      { label: "Luz", data: datos.map(x => x.luz), borderColor: css("--gris"), backgroundColor: "rgba(154,165,177,.18)", fill: true, borderWidth: 2, pointRadius: 0, tension: .3 }] },
      options: { plugins: { legend: { display: false } }, scales: { y: { max: 1023 } } } });
  } catch (e) {
    console.error(e);
    if (typeof Chart === "undefined") $("estado").textContent = "Conectado · no se pudo cargar la librería de gráficos (revisa tu internet)";
  }
}

// ---------- 5. Estado general ----------
function renderInterp(i) {
  $("interp").dataset.nivel = i.nivel;
  $("iNivel").textContent = "Estado general: " + i.etiqueta;
  $("iTitulo").textContent = i.titulo;
  $("iPuntos").replaceChildren(...i.puntos.map(t => Object.assign(document.createElement("li"), { textContent: t })));
  $("iConsejo").textContent = i.consejo ? "Sugerencia: " + i.consejo : "";
  document.querySelector("#interp .detalle").hidden = !i.puntos.length && !i.consejo;
}
async function cargarResumen() {
  try {
    const r = await fetch(API + "/api/resumen").then(x => x.json());
    const items = [["hoy", "Hoy", "hoy"], ["semana", "Esta semana", "7d"], ["mes", "Este mes", "30d"]];
    $("vistazo").replaceChildren(...items.map(([k, nombre, f]) => {
      const b = document.createElement("button");
      const dot = document.createElement("span"); dot.className = "dot " + r[k].nivel;
      b.append(dot, `${nombre}: ${r[k].etiqueta}`);
      b.onclick = () => document.querySelector(`#seg [data-f="${f}"]`).click();
      return b;
    }));
  } catch (e) {}
}

// ---------- 6. Épocas de estudio ----------
let epocas = [];
const verEpoca = e => aplicarFiltro("epoca:" + e.id, e.inicio, e.fin, e.nombre);

async function cargarEpocas() {
  epocas = await fetch(API + "/api/epocas").then(r => r.json());
  const sel = $("selEpoca");
  sel.innerHTML = '<option value="">Ninguna</option>' + epocas.map(e => `<option value="${e.id}">${esc(e.nombre)}</option>`).join("");
  if (filtro.key.startsWith("epoca:")) sel.value = filtro.key.slice(6);
  const tb = $("tbEpocas");
  if (!epocas.length) { tb.innerHTML = '<tr><td colspan="6">Aún no hay épocas. Crea la primera con el formulario.</td></tr>'; return; }
  tb.innerHTML = epocas.map(e => `<tr>
    <td>${esc(e.nombre)}</td><td>${e.inicio} a ${e.fin}</td><td>${e.minutos_foco}</td>
    <td>${e.pomodoros ? e.tasa + " %" : "–"}</td><td>${e.temp != null ? e.temp.toFixed(1) + " °C" : "–"}</td>
    <td><button class="btn-icon" data-ver="${e.id}" title="Ver detalles"><i class="fa-solid fa-arrow-up-right-from-square"></i></button>
    <button class="btn-icon" data-del="${e.id}" title="Eliminar época"><i class="fa-solid fa-trash"></i></button></td></tr>`).join("");
}
$("selEpoca").onchange = ev => {
  const e = epocas.find(x => String(x.id) === ev.target.value);
  if (e) verEpoca(e); else document.querySelector('#seg [data-f="todo"]').click();
};
$("tbEpocas").onclick = async ev => {
  const btn = ev.target.closest('button');
  if (!btn) return; 

  const ver = btn.dataset.ver, del = btn.dataset.del;
  if (ver) { 
    verEpoca(epocas.find(x => String(x.id) === ver)); 
    window.scrollTo({ top: 0, behavior: "smooth" }); 
  }
  if (del && confirm("¿Eliminar esta época? Los datos registrados no se borran.")) {
    await fetch(API + "/api/epocas/" + del, { method: "DELETE" });
    if (filtro.key === "epoca:" + del) document.querySelector('#seg [data-f="todo"]').click();
    cargarEpocas();
  }
};
$("formEpoca").onsubmit = async ev => {
  ev.preventDefault();
  const r = await fetch(API + "/api/epocas", { method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nombre: $("eNombre").value, inicio: $("eInicio").value, fin: $("eFin").value }) });
  if (!r.ok) { $("eError").textContent = (await r.json()).error; return; }
  $("eError").textContent = ""; $("formEpoca").reset(); cargarEpocas();
};

// ---------- 7. Inicio ----------
$("btnDemo").onclick = async () => {
  if (!confirm("Esto BORRA todos los datos actuales y carga 4 meses de datos de prueba. ¿Continuar?")) return;
  await fetch(API + "/api/demo?reemplazar=1", { method: "POST" });
  cargarEpocas(); cargarResumen(); cargar();
};
aplicarFiltro("todo", null, null, PRESETS.todo.label);
cargarEpocas();
cargarResumen();
setInterval(() => { cargar(); cargarEpocas(); cargarResumen(); }, 10000); // se actualiza solo cada 10 s