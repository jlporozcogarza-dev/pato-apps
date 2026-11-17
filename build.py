"""Genera las apps instalables (tracker/ y finanzas/) a partir de src/*.html.
src/ es el mismo HTML que se publica como artefacto en Claude; aquí solo se le agrega
el icono, el modo pantalla completa y un puente a Google Sheets para cuando no corre dentro de Claude.
Uso: python build.py"""
import json, pathlib
from PIL import Image, ImageDraw, ImageFilter, ImageFont

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
    if (window.top !== window) return null; // dentro de JLP: la clave se pide una sola vez, en el Inicio
    var s = window.prompt("Pega el link de configuración que te mandó Claude");
    try{ c = s ? fromParams(new URL(s.trim()).searchParams) : null; }catch(e){ c = null; }
    if (c) save(c);
    return c;
  }
  window.claude = { use: async function(cap){
    if (cap !== "mcp") return null;
    var c = load(); if (!c) return null;
    // u = URL completa de un puente, o id de Apps Script. Con id: primero el server de la casa (rápido) y,
    // si no contesta, Apps Script directo. Solo se reintenta lo que no duplica datos (leer y sobrescribir).
    var gas = "https://script.google.com/macros/s/" + encodeURIComponent(c.u) + "/exec";
    var server = ["https://api.jlpog.app/"];
    var urls = /^https:/.test(c.u) ? [c.u] : server.concat([gas]);
    return { callTool: async function(srv, tool, input){
      var res, j, body = JSON.stringify({ k:c.k, tool:tool, input:input });
      var lista = (tool === "get_values" || tool === "update_values" || /^https:/.test(c.u)) ? urls : server;
      for (var i = 0; i < lista.length; i++){
        try{
          res = await fetch(lista[i], { method:"POST", headers:{ "Content-Type":"text/plain;charset=utf-8" }, body:body, signal: i < lista.length - 1 && AbortSignal.timeout ? AbortSignal.timeout(6000) : undefined });
          j = await res.json(); break;
        }catch(e){ if (i === lista.length - 1) throw { code:"server_unavailable", message:String(e) }; }
      }
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

# Tema JLP: colores tradicionales japoneses (nippon iro, diccionario de Sanzo Wada) con la regla 60-30-10:
# 60 = fondo, 30 = tarjetas de vidrio, 10 = acento. Son solo el valor inicial: JLP (index.html, PALETAS) los cambia en vivo.
PALETAS = {
    "tracker":  {"c60": "#0D0D0D", "c30": "#9A4D00", "c10": "#E3D3C5"},  # Torinoko: 漆黒 · 琥珀 · 鳥の子
    "finanzas": {"c60": "#0D0D0D", "c30": "#9C8E82", "c10": "#FFA64D"},  # Kanzō: 漆黒 · 白茶 · 萱草
}
VIDRIO = {  # clases que son tarjetas en cada app
    "tracker": ".banner,.hero,.iconbtn,.mday,.rows,.wcard",
    "finanzas": ".banner,.buds,.chart,.hero,.iconbtn,.mc,.saldos,.tot,.txs,.wd",
}

def tema(key):
    """Los colores van en --j60/--j30/--j10: JLP (index.html) los cambia en vivo según la paleta que elijas."""
    p = PALETAS[key]
    m = lambda v, pct: f"color-mix(in srgb,var(--j{v}) {pct}%,transparent)"
    return f"""<script>if (window.top !== window) document.documentElement.classList.add("embed");</script>
<style id="jlp-tema">
/* JLP: oscuro con vidrio, 60-30-10 en colores japoneses. Gana sobre los temas claro/oscuro de la app. */
html:root:root{{--j60:{p["c60"]};--j30:{p["c30"]};--j10:{p["c10"]};color-scheme:dark;--bg:var(--j60);--surface:{m(30, 20)};--surface-2:{m(30, 28)};--line:{m(30, 36)};--track:{m(30, 24)};
  --fg:#F4F1EA;--muted:#B5AEA4;--faint:#7E7870;--accent:var(--j10);--accent-soft:{m(10, 16)};--accent-line:{m(10, 42)};
  --scrim:rgba(0,0,0,.55);--card-shadow:0 18px 40px -22px rgba(0,0,0,.75);
  --font-display:ui-rounded,"SF Pro Rounded",Nunito,system-ui,sans-serif;--font-body:-apple-system,BlinkMacSystemFont,"SF Pro Text",Geist,system-ui,sans-serif}}
body{{-webkit-font-smoothing:antialiased}}
h1{{font-size:38px!important;font-weight:800!important;letter-spacing:-.02em!important;padding-bottom:.12em;
  background:linear-gradient(180deg,var(--fg) 38%,color-mix(in srgb,var(--fg) 46%,var(--j60)));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}}
h2,h3,.sec-head .lbl{{font-weight:700!important}}
/* mismas formas que JLP: tarjetas más redondas, botones de vidrio y acentos que resplandecen */
.hero,.wcard,.rows,.saldos,.txs,.chart,.buds{{border-radius:28px!important}}
.banner,.tot{{border-radius:20px!important}}
.sheet{{border-radius:30px 30px 0 0!important}}
.iconbtn,.navbtn{{background:linear-gradient(150deg,rgba(255,255,255,.14),rgba(255,255,255,.03))!important;border:1px solid rgba(255,255,255,.12)!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.25)!important}}
.btn.primary,.addbtn{{background:linear-gradient(180deg,color-mix(in srgb,var(--j10) 68%,#fff),var(--j10) 58%,color-mix(in srgb,var(--j10) 82%,#000))!important;color:var(--j60)!important;border-color:transparent!important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.7),0 0 22px color-mix(in srgb,var(--j10) 50%,transparent)!important}}
.today-chip{{color:var(--j60)!important}}
.today-chip,.chip[aria-pressed="true"],.seg button[aria-pressed="true"]{{box-shadow:inset 0 1px 0 rgba(255,255,255,.25),0 0 16px color-mix(in srgb,var(--j10) 35%,transparent)!important}}
.bar i{{box-shadow:0 0 10px color-mix(in srgb,var(--j10) 55%,transparent)}}
.ring-big svg{{filter:drop-shadow(0 0 9px color-mix(in srgb,var(--j10) 40%,transparent))}}
.btn,.chip,.iconbtn,.navbtn,.addbtn{{transition:transform .25s cubic-bezier(.34,1.4,.5,1),filter .2s}}
.btn:active,.chip:active,.addbtn:active,.iconbtn:active,.navbtn:active{{transform:scale(.94);filter:brightness(1.15)}}
html{{background:var(--j60)}} html.embed,html.embed body,body{{background:transparent!important}}
html:not(.embed) body{{background:radial-gradient(60% 40% at 90% 0%,{m(10, 16)},transparent 70%),radial-gradient(60% 40% at 0% 60%,{m(30, 22)},transparent 70%),var(--j60)!important;background-attachment:fixed!important}}
html.embed body{{padding-bottom:calc(104px + env(safe-area-inset-bottom))!important}}
html.embed .top-l{{padding-left:66px;min-height:62px}} /* a la izquierda va el anillo de Fede de JLP */
html.embed,html.embed body{{overscroll-behavior:none}} /* sin rebote al jalar: en el iPhone el rebote dentro del iframe se veía blanco */
{VIDRIO[key]}{{-webkit-backdrop-filter:blur(24px) saturate(160%);backdrop-filter:blur(24px) saturate(160%);border-color:rgba(255,255,255,.10)!important;
  background-image:linear-gradient(150deg,rgba(255,255,255,.08),rgba(255,255,255,.02) 40%,transparent)!important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.22),inset 1px 0 0 rgba(255,255,255,.06),inset 0 -1px 0 rgba(0,0,0,.35),var(--card-shadow)!important}}
.sheet{{background:linear-gradient(180deg,{m(30, 30)},color-mix(in srgb,var(--j60) 92%,transparent)),var(--j60)!important;-webkit-backdrop-filter:blur(30px);backdrop-filter:blur(30px);border-top:1px solid {m(30, 45)}}}
/* Al entrar a la pestaña (JLP pone html.entra) los bloques suben uno tras otro */
@keyframes jlpSube{{from{{opacity:0;transform:translateY(16px)}}to{{opacity:1;transform:none}}}}
html.entra #app>*{{animation:jlpSube .55s cubic-bezier(.2,.8,.2,1) both}}
{"".join(f"html.entra #app>:nth-child({i}){{animation-delay:{(i - 1) * 0.05:.2f}s}}" for i in range(1, 10))}
@media (prefers-reduced-motion:reduce){{html.entra #app>*{{animation:none}}}}
</style>
"""

# En jlpog.app los datos salen de la base de datos del server, no de Google Sheets: estos textos cambian
# solo en esta versión (los artefactos de Claude siguen usando Sheets y conservan los suyos).
TEXTOS = {
    "tracker": [
        ('aria-label="Actualizar datos del Sheet"', 'aria-label="Actualizar datos"'),
        ('Tus datos viven en el Google Sheet <a id="sheetLink" target="_blank" rel="noopener">Tracker de hábitos 90 días</a>. WHOOP se sincroniza solo a las 6:47 AM y 9:47 PM; lo que registras a mano siempre manda.',
         'Tus datos viven en tu server<a id="sheetLink" hidden></a>. WHOOP se sincroniza solo cada hora; lo que registras a mano siempre manda.'),
        ('txt.textContent = "Sheet al día"', 'txt.textContent = "Al día"'),
        ('msg:"Vista de ejemplo con datos inventados. Abre la app desde Claude para conectar tu Google Sheet."',
         'msg:"Vista de ejemplo. Toca Conectar mis datos en Inicio para ver los tuyos."'),
    ],
    "finanzas": [
        ('aria-label="Actualizar datos de la hoja"', 'aria-label="Actualizar datos"'),
        ('Tus datos viven en la hoja <a id="sheetLink" target="_blank" rel="noopener">Finanzas Pato</a> de Google Sheets',
         'Tus datos viven en tu server<a id="sheetLink" hidden></a>'),
        ('msg:"Vista de ejemplo con datos inventados. Abre la app desde Claude para conectar tu hoja de finanzas."',
         'msg:"Vista de ejemplo. Toca Conectar mis datos en Inicio para ver los tuyos."'),
        ('t.textContent="Hoja al día"', 't.textContent="Al día"'),
        ("se registran en tu hoja con esa fecha", "se registran con esa fecha"),
        ("Sin cuentas en la hoja.", "Sin cuentas todavía."),
        ('"No encontré ese programado en la hoja."', '"No encontré ese programado."'),
        ('"Pago guardado en tu hoja"', '"Pago guardado"'),
    ],
}
COMUNES = [  # pueden salir varias veces
    ('const SERVER = "Google Sheets";', 'const SERVER = "tu base de datos";'),
    ('"Google Sheets respondió con un error: "', '"Tu base de datos respondió con un error: "'),
    ('"No se pudo conectar con Google Sheets."', '"No se pudo conectar con tu base de datos."'),
    ("Sin conexión con tu hoja.", "Sin conexión con tu base de datos."),
    ("esto no se guarda en tu hoja.", "esto no se guarda."),
    # misma tipografía que JLP: la del sistema de Apple; Geist y Nunito son solo el respaldo fuera del iPhone
    ("family=Plus+Jakarta+Sans:wght@400;500;600;700;800", "family=Geist:wght@400;500;600;700&family=Nunito:wght@600;700;800"),
]

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
    t = sub(t, "</head>", tema(key) + "</head>")
    for old, new in TEXTOS[key]:
        t = sub(t, old, new)
    for old, new in COMUNES:
        assert old in t or key == "tracker", old  # finanzas tiene todos; tracker solo algunos
        t = t.replace(old, new)
    (out / "index.html").write_text(t, encoding="utf-8", newline="")
    for s in (180, 192, 512):
        icon(key, s).save(out / f"icon-{s}.png", optimize=True)
    (out / "manifest.webmanifest").write_text(json.dumps({
        "name": a["name"], "short_name": a["short"], "display": "standalone",
        "background_color": BG_LIGHT, "theme_color": BG_LIGHT,
        "icons": [{"src": f"icon-{s}.png", "sizes": f"{s}x{s}", "type": "image/png"} for s in (192, 512)],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(key, "ok")

# ---------- JLP (index.html): la app que se instala en el cel, con su icono y accesos rápidos ----------
def icono_jlp(size, maskable=False):
    S = 1024
    im = Image.new("RGB", (S, S), (20, 20, 20))
    brillo = Image.new("L", (S, S), 0)  # resplandor Hiwa arriba a la derecha, como el fondo de la app
    ImageDraw.Draw(brillo).ellipse((420, -260, 1240, 520), fill=150)
    im.paste(Image.new("RGB", (S, S), (190, 194, 63)), (0, 0), brillo.filter(ImageFilter.GaussianBlur(170)))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype("C:/Windows/Fonts/georgia.ttf", 330 if maskable else 400)  # serif parecida a Instrument Serif
    d.text((S / 2, S / 2 + 20), "JLP", font=f, fill=(244, 241, 234), anchor="mm")
    return im.resize((size, size), Image.LANCZOS)

for s in (180, 192, 512):
    icono_jlp(s).save(ROOT / f"jlp-{s}.png", optimize=True)
icono_jlp(512, maskable=True).save(ROOT / "jlp-maskable-512.png", optimize=True)
(ROOT / "manifest.webmanifest").write_text(json.dumps({
    "name": "JLP", "short_name": "JLP", "id": "/", "start_url": "./", "scope": "./",
    "display": "standalone", "orientation": "portrait",
    "background_color": "#1C1C1C", "theme_color": "#1C1C1C",
    "icons": [{"src": "jlp-192.png", "sizes": "192x192", "type": "image/png"},
              {"src": "jlp-512.png", "sizes": "512x512", "type": "image/png"},
              {"src": "jlp-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}],
    "shortcuts": [{"name": "Tracker", "url": "./#tracker", "icons": [{"src": "tracker/icon-192.png", "sizes": "192x192"}]},
                  {"name": "Finanzas", "url": "./#finanzas", "icons": [{"src": "finanzas/icon-192.png", "sizes": "192x192"}]}],
}, ensure_ascii=False, indent=2), encoding="utf-8")
print("jlp ok")
