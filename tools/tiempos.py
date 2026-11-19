"""Cuánto tardó Claude en cada pedido de Pato, leído del historial de Claude Code (archivos .jsonl).

Uso:
  python tools/tiempos.py                 # la sesión más reciente que tocó pato-apps
  python tools/tiempos.py RUTA.jsonl ...  # sesiones específicas
  python tools/tiempos.py --desde 2026-11-19 --respuestas

Un pedido = un mensaje tuyo. Su tiempo va de ese mensaje a la última actividad de Claude antes del siguiente
mensaje tuyo (si mandas otro mientras trabaja, el tiempo se parte ahí). "activo" suma solo los ratos con
actividad: un hueco de más de 5 min sin nada (esperándote a ti o a un proceso) cuenta como 5. Horas de Monterrey (UTC-6).
"""
import argparse, glob, json, os, sys
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding="utf-8")
MTY = timedelta(hours=-6)
HUECO = 5  # min
PROY = os.path.expanduser("~/.claude/projects")


def texto_usuario(d):
    if d.get("type") != "user" or d.get("isMeta") or d.get("isCompactSummary"):
        return None
    c = d.get("message", {}).get("content")
    if isinstance(c, list):
        if any(x.get("type") == "tool_result" for x in c):
            return None
        c = " ".join(x.get("text", "") for x in c if x.get("type") == "text")
    t = (c or "").strip()
    return t if t and not t.startswith("<") and not t.startswith("[Request interrupted") else None


def hora(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=None) + MTY


def pedidos(ruta):
    out, cur = [], None
    for linea in open(ruta, encoding="utf-8"):
        try:
            d = json.loads(linea)
        except ValueError:
            continue
        ts = d.get("timestamp")
        if not ts:
            continue
        t = texto_usuario(d)
        if t:
            if cur:
                out.append(cur)
            cur = {"inicio": hora(ts), "fin": hora(ts), "pedido": t, "respuesta": "", "activo": 0.0}
        elif cur:
            cur["activo"] += min(mins(hora(ts) - cur["fin"]), HUECO)
            cur["fin"] = hora(ts)
            if d.get("type") == "assistant":
                for x in d["message"].get("content", []):
                    if x.get("type") == "text" and x["text"].strip():
                        cur["respuesta"] = x["text"].strip()
    if cur:
        out.append(cur)
    return out


def sesion_reciente():
    cands = [p for p in glob.glob(os.path.join(PROY, "*", "*.jsonl")) if os.path.getsize(p) > 0]
    cands.sort(key=os.path.getmtime, reverse=True)
    for p in cands[:40]:
        with open(p, encoding="utf-8", errors="ignore") as f:
            if "pato-apps" in f.read(2_000_000):
                return p
    sys.exit("No encontré una sesión que toque pato-apps")


def mins(td):
    return td.total_seconds() / 60


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("rutas", nargs="*")
    ap.add_argument("--desde", help="AAAA-MM-DD")
    ap.add_argument("--respuestas", action="store_true", help="muestra el inicio de la última respuesta")
    a = ap.parse_args()
    todos = [x for r in (a.rutas or [sesion_reciente()]) for x in pedidos(r)]
    if a.desde:
        todos = [x for x in todos if x["inicio"].strftime("%Y-%m-%d") >= a.desde]
    total = sum(x["activo"] for x in todos)
    for x in todos:
        print(f'{x["inicio"]:%m-%d %H:%M}  {x["activo"]:5.1f} min  {x["pedido"][:110].replace(chr(10), " ")}')
        if a.respuestas and x["respuesta"]:
            print("      → " + x["respuesta"][:300].replace("\n", " "))
    print(f"\n{len(todos)} pedidos · {total:.0f} min de trabajo ({total / 60:.1f} h) · "
          f"promedio {total / max(len(todos), 1):.1f} min por pedido")
