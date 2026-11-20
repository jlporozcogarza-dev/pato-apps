/**
 * Puente entre las apps (tracker y finanzas) y tus Google Sheets.
 * Imita las 4 operaciones del conector de Google Sheets que usaban los artefactos de Claude:
 * get_values, update_values, append_values y update_spreadsheet.
 * Se implementa como Aplicación web: Ejecutar como "Yo", Acceso "Cualquier usuario".
 * Sin la CLAVE correcta no lee ni escribe nada, y solo toca las dos hojas de HOJAS.
 */
const CLAVE = '__CLAVE__';
const HOJAS = ['1L90iaeKk-U3Y7siZ4h7pFOfguUrEbK4IVvqk1YEuFFM', '1Wj1YoOCuqjQB-4rtikdTKAhFRCSRloNsWJeLMez4vic', '1Slfw8A9kXoBCsWPFIQyA6bi7XKKoURifbZcyqGzf_x0'];

function doPost(e) {
  let out;
  try {
    const req = JSON.parse(e.postData.contents);
    if (!igual(String(req.k || ''), CLAVE)) throw new Error('Clave incorrecta');
    const x = req.input || {};
    if (req.tool !== 'eventos' && req.tool !== 'evento' && HOJAS.indexOf(x.spreadsheetId) < 0) throw new Error('Hoja no permitida');
    out = { result: correr(req.tool, x) };
  } catch (err) {
    out = { error: String((err && err.message) || err) };
  }
  return ContentService.createTextOutput(JSON.stringify(out)).setMimeType(ContentService.MimeType.JSON);
}

function doGet() {
  return ContentService.createTextOutput('Puente listo.');
}

function igual(a, b) {
  if (a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}

function correr(tool, x) {
  if (tool === 'eventos') return eventos(x);
  if (tool === 'evento') return evento(x);
  const ss = SpreadsheetApp.openById(x.spreadsheetId);
  if (tool === 'get_values') return { values: leer(rango(ss, x.range)) };
  const lock = LockService.getScriptLock();
  lock.waitLock(25000);
  try {
    if (tool === 'update_values') {
      escribir(rango(ss, x.range), x.values);
      return { updatedRange: x.range };
    }
    if (tool === 'append_values') {
      const r0 = rango(ss, x.range), sh = r0.getSheet(), fila = sh.getLastRow() + 1;
      const ancho = Math.max.apply(null, x.values.map(function (v) { return v.length; }));
      const r = sh.getRange(fila, r0.getColumn(), x.values.length, ancho);
      escribir(r, x.values);
      return { updates: { updatedRange: "'" + sh.getName() + "'!" + r.getA1Notation() } };
    }
    if (tool === 'update_spreadsheet') {
      (x.requests || []).forEach(function (q) {
        if (q.deleteDimension) {
          const g = q.deleteDimension.range;
          const sh = ss.getSheets().filter(function (s) { return s.getSheetId() === g.sheetId; })[0];
          if (!sh) throw new Error('No existe la pestaña ' + g.sheetId);
          if (g.dimension === 'ROWS') sh.deleteRows(g.startIndex + 1, g.endIndex - g.startIndex);
          else sh.deleteColumns(g.startIndex + 1, g.endIndex - g.startIndex);
        } else if (q.addSheet) {
          const t = q.addSheet.properties.title;
          if (ss.getSheetByName(t)) throw new Error('Ya existe la pestaña ' + t);
          ss.insertSheet(t);
        } else throw new Error('Operación no soportada');
      });
      return {};
    }
    throw new Error('Herramienta desconocida: ' + tool);
  } finally {
    lock.releaseLock();
  }
}

// "Dias!A:K", "'Mi hoja'!A1", o solo "Whoop" (toda la pestaña)
function rango(ss, a1) {
  const i = a1.lastIndexOf('!');
  const nombre = (i < 0 ? a1 : a1.slice(0, i)).replace(/^'|'$/g, '');
  const sh = ss.getSheetByName(nombre);
  if (!sh) throw new Error('Unable to parse range: ' + a1);
  return i < 0 ? sh.getDataRange() : sh.getRange(a1.slice(i + 1));
}

// Como la API: números tal cual, fechas y horas como se ven, sin filas ni celdas vacías al final.
function leer(r) {
  const v = r.getValues(), d = r.getDisplayValues();
  const out = v.map(function (fila, i) {
    const f = fila.map(function (c, j) { return typeof c === 'number' ? c : (c instanceof Date ? d[i][j] : String(c)); });
    while (f.length && f[f.length - 1] === '') f.pop();
    return f;
  });
  while (out.length && !out[out.length - 1].length) out.pop();
  return out;
}

// null = no tocar esa celda. El texto se interpreta como si lo escribieras ('texto, =fórmula, fechas).
function escribir(r, values) {
  const conNull = values.some(function (f) { return f.some(function (c) { return c === null; }); });
  const ancho = r.getNumColumns();
  if (!conNull) {
    const m = values.map(function (f) { const g = f.slice(); while (g.length < ancho) g.push(''); return g.slice(0, ancho); });
    r.offset(0, 0, m.length, ancho).setValues(m);
    return;
  }
  values.forEach(function (f, i) {
    f.forEach(function (c, j) { if (c !== null) r.getCell(i + 1, j + 1).setValue(c); });
  });
}

// Solo lectura: eventos de todos tus calendarios entre x.desde y x.hasta (AAAA-MM-DD), en hora de Monterrey.
function eventos(x) {
  const desde = new Date(x.desde + 'T00:00:00-06:00'), hasta = new Date(x.hasta + 'T00:00:00-06:00');
  const z = 'America/Monterrey', f = function (d) { return Utilities.formatDate(d, z, "yyyy-MM-dd'T'HH:mm"); };
  const out = [];
  CalendarApp.getAllCalendars().forEach(function (cal) {
    cal.getEvents(desde, hasta).forEach(function (ev) {
      out.push({ t: ev.getTitle(), i: f(ev.getStartTime()), f: f(ev.getEndTime()), dia: ev.isAllDayEvent(),
                 l: ev.getLocation() || '', c: cal.getName().trim(), col: cal.getColor(),
                 id: ev.getId(), cid: cal.getId(), d: (ev.getDescription() || '').slice(0, 500), ro: /#holiday|#contacts|#weather/.test(cal.getId()), rec: ev.getPopupReminders() });
    });
  });
  return { eventos: out };
}

// Cambiar o borrar un evento desde JLP. x = { accion:'editar'|'borrar', cid, id, dia0 (AAAA-MM-DD donde está hoy), t, l, d, todo, fecha, ini, fin (HH:MM) }.
// Se busca en ese día por id (así funciona también con una sola fecha de un evento que se repite).
function evento(x) {
  if (x.accion === 'tareas') return tareasCal(x);   // pendientes con fecha → calendario «JLP Pendientes»
  const cal = CalendarApp.getCalendarById(x.cid);
  if (!cal) throw new Error('Calendario no encontrado');
  const z = '-06:00', d0 = new Date(x.dia0 + 'T00:00:00' + z), d1 = new Date(d0.getTime() + 864e5);
  const ev = cal.getEvents(d0, d1).filter(function (e) { return e.getId() === x.id; })[0];
  if (!ev) throw new Error('No encontré el evento ese día');
  if (x.accion === 'borrar') { ev.deleteEvent(); return { ok: true }; }
  if (x.t != null) ev.setTitle(String(x.t));
  if (x.l != null) ev.setLocation(String(x.l));
  if (x.d != null) ev.setDescription(String(x.d));
  if (x.fecha) {
    if (x.todo) ev.setAllDayDate(new Date(x.fecha + 'T00:00:00' + z));
    else ev.setTime(new Date(x.fecha + 'T' + x.ini + ':00' + z), new Date(x.fecha + 'T' + x.fin + ':00' + z));
  }
  // avisos: solo llegan si se tocaron en JLP (si no, se quedan los del calendario)
  if (x.rec) { ev.removeAllReminders(); x.rec.forEach(function (m) { ev.addPopupReminder(Number(m)); }); }
  // mover a otro calendario: Google no deja moverlo, así que se crea igual en el otro y se borra el original
  if (x.cid2 && x.cid2 !== x.cid) {
    if (ev.isRecurringEvent()) throw new Error('Un evento que se repite no se puede cambiar de calendario desde aquí');
    const otro = CalendarApp.getCalendarById(x.cid2);
    if (!otro) throw new Error('Calendario destino no encontrado');
    const op = { description: ev.getDescription(), location: ev.getLocation() }, rec = ev.getPopupReminders();
    const nuevo = ev.isAllDayEvent()
      ? otro.createAllDayEvent(ev.getTitle(), ev.getAllDayStartDate(), ev.getAllDayEndDate(), op)
      : otro.createEvent(ev.getTitle(), ev.getStartTime(), ev.getEndTime(), op);
    if (rec.length) { nuevo.removeAllReminders(); rec.forEach(function (m) { nuevo.addPopupReminder(m); }); }
    ev.deleteEvent();
  }
  return { ok: true };
}

// Tus pendientes con fecha (tareas de JLP y de Condotec) como eventos de todo el día en el calendario «JLP Pendientes».
// x.tareas = [{ id, t, fecha:'AAAA-MM-DD' }] = lo que DEBE estar. Lo que sobra (hecho o sin fecha) se borra; lo que cambió se corrige.
// Cada evento lleva "jlp:<id>" en la descripción para encontrarlo. JLP no muestra este calendario (ya pinta las tareas él mismo).
function tareasCal(x) {
  const NOMBRE = 'JLP Pendientes', z = '-06:00';
  let cal = CalendarApp.getCalendarsByName(NOMBRE)[0];
  if (!cal) { cal = CalendarApp.createCalendar(NOMBRE, { color: CalendarApp.Color.YELLOW }); }
  const hoy = new Date(), desde = new Date(hoy.getTime() - 120 * 864e5), hasta = new Date(hoy.getTime() + 400 * 864e5);
  const hay = {};
  cal.getEvents(desde, hasta).forEach(function (ev) {
    const m = /jlp:(\S+)/.exec(ev.getDescription() || '');
    if (!m || hay[m[1]]) { ev.deleteEvent(); return; }   // sin etiqueta o repetido: fuera
    hay[m[1]] = ev;
  });
  const quiero = {};
  (x.tareas || []).forEach(function (t) { if (t && t.id && /^\d{4}-\d{2}-\d{2}$/.test(t.fecha || '')) quiero[t.id] = t; });
  let creados = 0, cambiados = 0, borrados = 0;
  Object.keys(hay).forEach(function (id) { if (!quiero[id]) { hay[id].deleteEvent(); borrados++; } });
  Object.keys(quiero).forEach(function (id) {
    const t = quiero[id], dia = new Date(t.fecha + 'T00:00:00' + z), titulo = String(t.t).slice(0, 250);
    const ev = hay[id];
    if (!ev) { cal.createAllDayEvent(titulo, dia, { description: 'jlp:' + id + '\nSe maneja desde JLP (jlpog.app).' }); creados++; return; }
    const f = Utilities.formatDate(ev.getAllDayStartDate(), 'America/Monterrey', 'yyyy-MM-dd');
    if (ev.getTitle() !== titulo) { ev.setTitle(titulo); cambiados++; }
    if (f !== t.fecha) { ev.setAllDayDate(dia); cambiados++; }
  });
  return { creados: creados, cambiados: cambiados, borrados: borrados };
}
