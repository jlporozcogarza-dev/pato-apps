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
    if (HOJAS.indexOf(x.spreadsheetId) < 0) throw new Error('Hoja no permitida');
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
