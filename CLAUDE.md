# JLP (jlpog.app) — pedidos, estado y plan

Este archivo es la memoria de trabajo del app de Pato. Léelo antes de tocar JLP, Tracker, Finanzas, el puente o Fede.

## Reglas de trabajo (siempre)

1. **Pedido nuevo → agente `pato-pedidos`.** Cada vez que Pato pida algo nuevo del app, llama primero al agente `pato-pedidos` con su mensaje (y capturas si hay). El agente lo anota en «Pendientes» con un ID, los pasos, los archivos que toca y cómo probarlo. Después trabaja siguiendo esos pasos.
2. **Al terminar un pedido:** muévelo a «Hecho» con la fecha y el commit, en una línea.
3. **Agente `pato-progreso`.** Llámalo cuando Pato pregunte «qué falta», «cómo vas» o «qué sigue», o después de cerrar 3 pedidos. Mide el tiempo con `python tools/tiempos.py`, actualiza «Tiempos» y vuelve a ordenar el «Plan».
4. **Contesta en español y corto.** Pato usa el iPhone por Remote Control. Después de publicar, recuérdale cerrar JLP por completo y volver a abrirlo.

## Cómo está armado (lo mínimo para no perderse)

- **JLP** (`index.html`): PWA de una sola página. Tracker y Finanzas son iframes que se generan con `python build.py` desde `src/`.
- **Publicar:** `git commit` → `git push` → `ssh pato@192.168.1.110 'cd ~/apps/pato-apps && git pull -q --ff-only'`.
- **Server** (`../servidor-casa/puente/puente.py`, en `/opt/pato-puente`): se sube con `bash subir_puente.sh`. Copia las hojas y el Google Calendar cada 5 min sin gastar tokens.
- **Puente de Google Apps Script:** proyecto «Proyecto sin título», hoy en la **versión 5**. El `bridge.gs` local **no tiene la clave real**.
  - En el editor, cambia solo funciones (cortando desde `function eventos(`).
  - Apps Script autoguarda lo que pongas con `setValue`.
  - Después: Implementar → Gestionar → lápiz → Versión nueva.
- **Fede** (`../fede/fede.py`): `servidor.llamar(tool, input)` llama al puente desde la laptop.
- **Seguridad:**
  - No escribir claves ni contraseñas.
  - Los permisos de Google los aprueba Pato.
  - No borrar filas de hojas por índice.
  - Mandar WhatsApp solo si lo pide.

## Pendientes

Cada uno lleva quién lo destraba y una estimación de tiempo (sale del promedio medido: ~3 min por cambio chico y 5–9 min por cambio grande).

### Esperan a Pato
| ID | Pendiente | Qué necesito | Est. |
|---|---|---|---|
| P1 | Pago fallido de Cloudflare de jlpog.app | Que Pato lo pague; si no, se puede caer el dominio del app | — |
| P2 | Suscripciones en Finanzas › Programados: agregar las 6 de Amazon y ElevenLabs, Spotify a $139, Starlink el día 13 | Su «sí» | 10 min |
| P3 | Entrega del Tec del 27 sale doble (tarea + evento) | Decidir: borrar la tarea o dejar las dos | 2 min |
| P4 | Tarea del Tec del domingo 22 (tiene puntito en Canvas) | Captura de Canvas | 3 min |
| P5 | Inscripción MR3001B: hora real (puse 9:00 del 14 dic) | Hora, si se la dan | 2 min |
| P6 | Atajo de Wallet/Apple Pay que anota pagos en Finanzas | Que Pato arme la automatización en el iPhone (ya tiene la guía) | — |
| P7 | Alertas de tarjeta de BBVA en sucursal (ya está en Pendientes del app) | Que vaya a sucursal | — |

### Probar en el iPhone (hecho, pero Pato no lo ha confirmado)
- Comida por texto y por foto (Fede calcula y guarda).
- Anillo de Fede: un toque para micrófono on/off, doble toque cancela, «cancela» lo calla.
- Post-its de Ideas: dejar picado mueve, dos toques edita, un toque abre en grande.
- Deslizar para cambiar de pestaña; deslizar hacia abajo para cerrar ventanas.
- Gráficas de déficit y de sueño; cabeceras iguales en todas las pestañas.
- Filtros del calendario y sus puntos de color.
- Editar eventos: calendario, avisos, mover de calendario.
- Acentos neón.

### Para Claude (no esperan a nadie)
| ID | Pendiente | Est. |
|---|---|---|
| C1 | Que las **tareas** que salen en el calendario también se abran al tocarlas (hoy solo se editan desde la lista de Pendientes) | 10 min |
| C2 | Fede por voz no conoce Mis comidas ni las recetas (café, sandwich…): pasárselas en su contexto | 10 min |
| C3 | Revisar «Gastado desde el inicio» = 1520.5 en Config de Finanzas | 10 min |
| C4 | Respaldo de Ideas (post-its) en Sheets; hoy solo viven en el teléfono | 20 min |
| C5 | La lista de calendarios del editor de eventos sale de los eventos copiados; un calendario sin eventos en ±2 meses no aparece (atajo, `index.html` abrirEv) | 10 min |
| C6 | Pestaña **Cam** (HECHA 19 nov, commit ec718c3). Falta: 1) que camara.pyw arranque con Windows (no me dejaron crear el acceso directo en Inicio; Pato decide), 2) la prueba salió en negro: tapa cerrada o tapita de la cámara | 5 min |

#### C6 — Cam en vivo
- **Pasos:**
  1. `puente.py`: herramientas `cam_ver` (el app pide el último cuadro y marca «alguien está viendo»), `cam_subir` (la laptop manda el cuadro) y `cam_estado`. Todo en memoria y con la clave de siempre.
  2. `../fede/camara.pyw`: pregunta cada 2 s si alguien ve. Si sí, prende ffmpeg (dshow «Integrated Camera», 640 px, unos 4 cuadros por segundo) y sube el último cuadro. Si nadie ve por 8 s, apaga la cámara.
  3. Arranque con Windows (acceso directo en Inicio).
  4. `index.html`: pestaña Cam con la imagen en vivo y un aviso de «laptop apagada» cuando no llegan cuadros.
- **Probar:** abrir la pestaña Cam en el navegador y ver que la imagen cambia. Al cerrarla, la luz de la cámara se apaga en unos 10 s.
- **Cuidado:** solo con la clave. No se guarda ningún cuadro en disco. La cámara solo se prende mientras alguien está viendo.

## Plan (orden propuesto)

1. **Hoy, rápido y de alto riesgo:** P1 (Cloudflare). Si se cae el dominio, se cae todo el app.
2. **Respuestas de Pato que destraban trabajo corto:** P3, P2 y P4. Juntas son unos 15 min míos.
3. **Ronda de pruebas en el iPhone.** Pato abre el app y manda capturas de lo que se vea mal. Eso va antes de agregar cosas nuevas.
4. **Para Claude, de más útil a menos:** C1 → C2 → C3 → C4 → C5.
5. **Cuando Pato pueda:** P6 y P7.

## Tiempos (medidos con `tools/tiempos.py`)

- **Sesión del 16 al 19 de nov:** 79 mensajes y unas 4.1 h de trabajo activo, unos 3 min por mensaje.
- **Lo que más tardó:**
  - Calendario de Condotec: 9.3 min.
  - Fede con anillo y audio: 8.9 min.
  - Google Calendar en el app: 8.5 min.
  - Reiniciar el server: 8.1 min.
  - Regla de $500 diarios: 7.7 min.
  - Gestos del anillo: 7.2 min.
  - Confirmar depas: 7.1 min.
- **Lo que más frena no es el código, sino esperar algo de afuera:**
  - el ssh del server trabado (~1 h el 16 nov);
  - el permiso de Calendar (~25 min el 19 nov);
  - conectar la extensión de Chrome.

## Hecho (16–19 nov 2026)

**Inicio y general**
- Anillo de Fede arriba a la izquierda en todas las pestañas, siempre animado. Toque = micrófono on/off, doble toque = cancelar, «cancela» lo calla. Ya no hay pestaña Fede.
- Botón de colores fijo arriba a la derecha. Paleta por pestaña, con favoritos (estrella).
- Barra de pestañas reordenable (dejar picado). Deslizar a los lados cambia de pestaña, también sobre el tablero de Ideas.
- Las ventanas se cierran con ✕ o deslizando hacia abajo (también en Tracker y Finanzas).
- Sin zoom al escribir. Sin rebote blanco al jalar.
- Cabecera estándar en todas las pestañas: fecha chica y nombre de la hoja a 32 px.
- Gráficas de 7 días: pasos (de WHOOP), déficit de calorías y horas de sueño.
- Acentos neón: barrita en títulos, punto en la fecha, rayita en la pestaña activa, brillo en los puntos del calendario.
- Se quitó la pestaña Cámara. Pestaña **Ideas** con post-its de vidrio: mover, editar tamaño/color/capa, abrir en grande.

**Pendientes y calendario**
- Tareas con título y descripción. Fede les pone nivel.
- Grupos plegables: Vencidas, Hoy, Mañana, Próximas, Sin fecha y Hechas.
- Avance del día y avance general.
- Los pendientes de Condotec se marcan Hecho o se cambian texto y fecha. Los que vienen de WhatsApp se cierran en el server.
- Google Calendar sincronizado en los dos sentidos (permiso aprobado el 19 nov), con filtros Personal (verde), Tec (azul) y Condotec (gris).
- Tocar un evento lo edita: nombre, fecha, hora, lugar, notas, calendario y avisos. También lo borra.
- Entrega Evidencia 3 (27 nov) e inscripción de MR3001B (14 dic, avisos 2 días antes y el mismo día) en TEC.

**Condotec**
- Calendario del mes: entradas verdes, salidas rojas, pendientes azules y pagos amarillos. Va abajo de la lista de depas.
- En Atención, cada renglón se puede tocar para actualizar estatus o marcar Resuelto.
- En Edificio, los depas por confirmar preguntan «¿la info está bien?».

**Tracker**
- Proteína: 120 g o más = meta cumplida.
- Comida: meta de déficit de 300 kcal contra lo quemado según WHOOP.
- Pasos desde WHOOP.
- Mis comidas con macros reales: Sandwich fit 166, Ensalada 527, Atún con elote, Saladitas con contador [− 0 +] y Café con Lala Light +Proteína.
- La comida se escribe o se toma foto, y la IA la calcula y la guarda. Ya no hay cajas de kcal ni proteína.
- Suplementos en orden: Magnesio, Creatina, Zinc, Omega.
- Lo de WHOOP sale en tono oscuro y lo editable en claro.

**Finanzas**
- Los correos de BBVA se anotan solos cada 5 min (proyecto «Correos BBVA»).
- Saldos actualizados con las capturas.
- Regla de $500 diarios arrancando de cero; hoy solo cuenta el pádel de $120.
- Izzi $495 anotado, con su pago fijo el día 15.
- Se quitó el calendario semanal.

**Otros**
- Suscripciones investigadas: unos $6,079 al mes en total (falta P2).
