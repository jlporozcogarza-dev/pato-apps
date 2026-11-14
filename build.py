"""Genera las apps instalables (tracker/ y finanzas/) a partir de src/*.html.
src/ es el mismo HTML que se publica como artefacto en Claude; aquí solo se le agrega
el icono, el modo pantalla completa y un puente a Google Sheets para cuando no corre dentro de Claude.
Uso: python build.py"""
import json, pathlib
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).parent
APPS = {
    "tracker":  {"src": "tracker.html",  "name": "Tracker de hábitos", "short": "Tracker"},
    "finanzas": {"src": "finanzas.html", "name": "Finanzas de Pato",   "short": "Finanzas"},
}
BG_LIGHT, BG_DARK, CORAL, INK = "#F6F3F2", "#131012", (238, 102, 86), (27, 20, 24)

SHIM = """<script>
/* Fuera de Claude la app habla con tus Google Sheets por el puente de Apps Script.
   La configuración (u = id del puente, k = clave) llega en el link y se guarda en este dispositivo. */
(function(){
  if (window.claude) return;
  var LS = "pato-puente";
  function save(c){ try{ localStorage.setItem(LS, JSON.stringify(c)); }catch(e){} }
  function fromParams(p){ return p.get("u") && p.get("k") ? { u:p.get("u"), k:p.get("k") } : null; }
  function load(){
    var c = fromParams(new URLSearchParams(location.search));
    if (c){ save(c); return c; }
    try{ c = JSON.parse(localStorage.getItem(LS) || "null"); }catch(e){ c = null; }
    if (c) return c;
    var s = window.prompt("Pega el link de configuración que te mandó Claude");
    try{ c = s ? fromParams(new URL(s.trim()).searchParams) : null; }catch(e){ c = null; }
    if (c) save(c);
    return c;
  }
  window.claude = { use: async function(cap){
    if (cap !== "mcp") return null;
    var c = load(); if (!c) return null;
    var url = "https://script.google.com/macros/s/" + encodeURIComponent(c.u) + "/exec";
    return { callTool: async function(server, tool, input){
      var res, j;
      try{ res = await fetch(url, { method:"POST", headers:{ "Content-Type":"text/plain;charset=utf-8" }, body:JSON.stringify({ k:c.k, tool:tool, input:input }) }); }
      catch(e){ throw { code:"server_unavailable", message:String(e) }; }
      try{ j = await res.json(); }catch(e){ throw { code:"server_unavailable", message:"Respuesta inválida del puente" }; }
      if (j.error) throw { code:"tool_error", message:j.error };
      return { payload:j.result };
    } };
  } };
})();
</script>
"""

def head(short):
    return (f'<link rel="manifest" href="manifest.webmanifest">\n'
            f'<link rel="apple-touch-icon" href="icon-180.png">\n'
            f'<link rel="icon" href="icon-192.png">\n'
            f'<meta name="apple-mobile-web-app-capable" content="yes">\n'
            f'<meta name="mobile-web-app-capable" content="yes">\n'
            f'<meta name="apple-mobile-web-app-status-bar-style" content="default">\n'
            f'<meta name="apple-mobile-web-app-title" content="{short}">\n'
            f'<meta name="theme-color" content="{BG_LIGHT}" media="(prefers-color-scheme: light)">\n'
            f'<meta name="theme-color" content="{BG_DARK}" media="(prefers-color-scheme: dark)">\n'
            f'<meta name="referrer" content="no-referrer">\n')

def icon(kind, size):
    S = 1024
    im = Image.new("RGB", (S, S), INK)
    d = ImageDraw.Draw(im)
    if kind == "tracker":
        box = (232, 232, 792, 792)
        d.arc(box, 0, 360, fill=(58, 46, 52), width=96)
        d.arc(box, -90, 200, fill=CORAL, width=96)
    else:
        for i, h in enumerate((300, 470, 380, 600)):
            x = 222 + i * 150
            d.rounded_rectangle((x, 812 - h, x + 96, 812), radius=40, fill=CORAL if i == 3 else (240, 232, 230))
    return im.resize((size, size), Image.LANCZOS)

def sub(t, old, new):
    assert t.count(old) == 1, old
    return t.replace(old, new)

for key, a in APPS.items():
    out = ROOT / key
    out.mkdir(exist_ok=True)
    t = (ROOT / "src" / a["src"]).read_text(encoding="utf-8")
    title = t[t.index("<title>"):t.index("</title>") + 8]
    t = sub(t, title, title + "\n" + head(a["short"]))
    t = sub(t, "<script>\n(function(){", SHIM + "<script>\n(function(){")
    (out / "index.html").write_text(t, encoding="utf-8", newline="")
    for s in (180, 192, 512):
        icon(key, s).save(out / f"icon-{s}.png", optimize=True)
    (out / "manifest.webmanifest").write_text(json.dumps({
        "name": a["name"], "short_name": a["short"], "display": "standalone",
        "background_color": BG_LIGHT, "theme_color": BG_LIGHT,
        "icons": [{"src": f"icon-{s}.png", "sizes": f"{s}x{s}", "type": "image/png"} for s in (192, 512)],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(key, "ok")
