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
| P8 | Impresora 3D fuera del cuarto: arrancar impresiones desde el app, cámara que la vigile y la IA avise o pause si sale mal (19 nov) | Modelo de impresora y dónde queda respecto al server | — |
| P9 | Persiana motorizada (domingo 22 nov): plan en PDF mandado por WhatsApp. Claude debe diseñar placa motor + soporte + tapones (STL), programa del ESP32 (GPIO 25 STEP, 26 DIR, 27 EN, 32/33 finales) y botón Persiana en JLP | Ancho de la ventana y si se atornilla a techo o pared | 60 min |
| P10 | Cyberdeck propio para las vacaciones de invierno: Raspberry Pi 5 + pantalla 7" + batería USB-C + caja impresa en 3D; radio con RTL-SDR y ESP32 (CC1101 + IR). Ya se vio uConsole como alternativa armada | Que llegue invierno; luego armar lista con links y precios | — |

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
| C6 | **HECHA 20 nov:** Pestaña Cam funcionando. camara.pyw arranca con Windows (acceso directo «Pato cam JLP» en Inicio); probado con cuadro real | — |
| C7 | Fede rápido para cosas fáciles: cerebro rápido (Haiku por API o modelo local) además del Sonnet con manos. Medido 19 nov: cerebro 1.5–5.5 s, ElevenLabs flash 0.3 s, v3 2.7 s por frase | 30 min (espera decisión de Pato) |
| C8 | **HECHA 19 nov (commit 1c45294):** Condotec › Edificio: al tocar un depa se abre su ficha con inquilino y responsable de pago (tocar el nombre abre su WhatsApp; si no hay teléfono, dice «Faltante»), renta, día de pago, entrada, salida, meses pagados, meses que faltan y la lista de pendientes de ese depa (19 nov) | 25 min |

#### C6 — Cam en vivo
- **Pasos:**
  1. `puente.py`: herramientas `cam_ver` (el app pide el último cuadro y marca «alguien está viendo»), `cam_subir` (la laptop manda el cuadro) y `cam_estado`. Todo en memoria y con la clave de siempre.
  2. `../fede/camara.pyw`: pregunta cada 2 s si alguien ve. Si sí, prende ffmpeg (dshow «Integrated Camera», 640 px, unos 4 cuadros por segundo) y sube el último cuadro. Si nadie ve por 8 s, apaga la cámara.
  3. Arranque con Windows (acceso directo en Inicio).
  4. `index.html`: pestaña Cam con la imagen en vivo y un aviso de «laptop apagada» cuando no llegan cuadros.
- **Probar:** abrir la pestaña Cam en el navegador y ver que la imagen cambia. Al cerrarla, la luz de la cámara se apaga en unos 10 s.
- **Cuidado:** solo con la clave. No se guarda ningún cuadro en disco. La cámara solo se prende mientras alguien está viendo.

#### C8 — Ficha del depa en Edificio
Hoy, al tocar un depa, solo cambia el cuadrito de abajo (`detalleUni` en `index.html`), que muestra el inquilino, la renta y la fecha del contrato. La hoja `hojaUni` es solo para editar.
- **Pasos:**
  1. **Hoja Inquilinos Condotec, pestaña Depas:** hoy tiene las columnas Depa, Estado, Inquilino, Renta mensual, Día de pago, Entrada y Salida. **No hay teléfonos ni responsable de pago.** Con el conector de Google Sheets, agrega al final las columnas «Teléfono», «Responsable de pago» y «Tel. responsable», vacías. No muevas las que ya están.
  2. **`../servidor-casa/puente/puente.py`, `unidades()`:** hoy usa `armar_panel.leer_depas`, que solo lee 5 columnas. Lee además, con `armar_panel.columnas`, las columnas «Día de pago», «Entrada», «Teléfono», «Responsable de pago» y «Tel. responsable», igual que lo hace `armar_mapa` en `../fede/buzon/armar_panel.py`. Por cada depa, agrega `p` = lista de `{nombre, tel, resp, tel_resp, dia, entrada, salida, renta}`, una por inquilino. Deja `q`, `r` y `s` como están, porque `aplicarUni` y `confirmarUni` los usan. Súbelo con `bash subir_puente.sh`.
  3. **`index.html`:** al tocar un depa (el listener de `[data-uni]`, cerca de la línea 1540), abre una hoja nueva, `hojaDepa`. Cópiala de `hojaUni`: misma `.hoja`, misma asa y mismo ✕, y se abre con `hoja(el, true)`. Deja el cuadrito de abajo como está.
     - Por cada inquilino muestra su nombre y su responsable de pago. Si hay teléfono, cada nombre es un `<a href="https://wa.me/52XXXXXXXXXX">`: quita todo lo que no sea número y pon 52 adelante si el número tiene 10 dígitos. Si no hay teléfono, junto al nombre va «Faltante» en gris.
     - Muestra también la renta, el día de pago, la entrada y la salida.
  4. **Meses pagados y meses que faltan:** calcúlalos en el cliente.
     - Meses pagados = meses entre la Entrada y hoy, contando el mes actual solo si el depa está en `pagos.json` (no le llega al app; ver la duda).
     - Meses que faltan = meses entre hoy y la Salida.
     - Si falta la fecha, pon «—».
  5. **Pendientes del depa:** filtra `AG.pendientes` (viene de la herramienta `agenda`, ya cargada) por los que mencionan ese depa en `depas`. Compara con `rotuloUni` y sin acentos, para que «Loft 3» no cuente como «Loft 13». Si no hay, pon «Sin pendientes». Al tocar uno, abre lo mismo que se abre al tocarlo en la pestaña Pendientes.
  6. En la ficha, deja el botón «Cambiar info o estado», que llama a `abrirUni(d)`, y también la pregunta «¿la info está bien?» de los depas por confirmar.
- **Probar:**
  - `servidor.llamar("panel", {"hoy": "2026-11-19"})`: cada unidad trae `p` con `dia`, `entrada` y las claves de teléfono.
  - En el navegador: toca el Loft 3, se abre la ficha y el nombre sin teléfono dice «Faltante». Pon un teléfono de prueba en la hoja, espera la copia de 5 min y revisa que el enlace sea `wa.me/52…`.
  - En el iPhone: tocar el nombre abre WhatsApp en ese chat.
- **Cuidado:**
  - La hoja es de Adrián. Solo agrega columnas al final; no reordenes ni borres filas.
  - En el server, la hoja es de solo lectura.
  - Los teléfonos son datos personales: no los pongas en logs ni en `fede_orden`.
  - Si `unidades()` truena, se cae toda la pestaña Condotec. Si la columna no existe, `columnas` debe regresar «vacío», no un error.
  - No necesita `python build.py`, porque es solo `index.html`.

## Plan (orden propuesto)

1. **Hoy, rápido y de alto riesgo:** P1 (Cloudflare). Si se cae el dominio, se cae todo el app.
2. **Respuestas de Pato que destraban trabajo corto:** P3, P2 y P4. Juntas son unos 15 min míos.
3. **Ronda de pruebas en el iPhone.** Pato abre el app y manda capturas de lo que se vea mal. Eso va antes de agregar cosas nuevas.
4. **Para Claude, de más útil a menos:** C1 → C8 → C2 → C3 → C4 → C5.
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
- 20 nov: WHOOP se copia cada 15 min (antes cada hora); Cam arranca sola con Windows; Cam en grande con zoom de pellizco y HD (1280 px) mientras está en grande.
- 20 nov: **Vigilancia en Cam**: la laptop detecta movimiento (OpenCV, `fede/camara.pyw`), Claude Haiku (`claude -p --model haiku`) dice si es persona, aviso por Web Push (`sw.js`, llaves en `fede/cam_vapid.json`, suscripciones en `/opt/pato-puente/cam.json`). Cajas naranja neón siguen lo que se mueve. Silenciar con rueda de horas/min. Máx. 1 aviso cada 2 min y 1 revisión de IA por minuto. Herramientas del puente: cam_vig, cam_evento, cam_aviso_foto, cam_sub_quitar.
- 20 nov: tocar una tarea en Pendientes abre su ficha con el texto completo y enlaces de dónde revisarlo (chat de WhatsApp, pedido y pagos de Amazon, Gmail, Cloudflare, BBVA, Canvas, pestaña del app…). Dejar picada sigue siendo la fecha.
- Suscripciones investigadas: unos $6,079 al mes en total (falta P2).
