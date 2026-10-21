# Interfaz EVA en el Cuadernillo Juegos

El libro usa el **eva-kit** (`C:\Users\germa\Desktop\eva-kit`) para que la barra,
el panel de Herramientas y el reproductor se vean como **1930: El viaje**. El
runtime sigue siendo el ADT (`base.bundle.local.js`): el kit aporta el marcado y
el CSS, y un adaptador conecta la interfaz con el runtime.

| Archivo | Rol |
|---|---|
| `assets/eva.css` | Piel EVA + componentes del kit. Incluye el bloque `eva-kit:panels (portado)`. |
| `assets/eva-ui.js` | Adaptador: barra, panel de Herramientas y reproductor. |
| `assets/voice-ui.css` | Arreglos legacy de los controles nativos (hoy ocultos). |
| `tools/eva/port_kit_css.py` | Concatena `components/eva-panels.css` en `eva.css` y corrige rutas. |
| `tools/eva/patch_runtime_bridge.py` | Agrega `window.__adtKit` (ajustes, reproducción real y `playText`/`stopText`) y publica `window.__adtPlayer` en el bundle. |

## Qué se corrigió respecto de la aplicación anterior

1. **Faltaba el CSS de paneles.** `eva.css` tenía barra, reproductor y dock, pero
   no `eva-panels.css`; el panel se veía nativo. Se portó completo.
2. **Rutas relativas.** El kit referencia `../icons/eva-switch-*.svg`. Al vivir
   dentro de `assets/`, la ruta correcta es `./icons/…`. Sin eso los interruptores
   eran círculos vacíos.
3. **Charset.** Se agregó `@charset "UTF-8";` al inicio de `eva.css` para que los
   checks (`✓`) no se vean como `âœ“`.
4. **El panel nativo no daba el look.** El adaptador reemplaza el contenido del
   popover de Configuración por el marcado del kit (`Herramientas`, `Leer`,
   `Escuchar`, `Pantalla`) y sincroniza los ajustes por el puente.
5. **El reproductor nativo no era el del kit.** El adaptador monta la píldora de
   1930 (anterior / reproducir / siguiente / opciones / minimizar / cerrar) y
   reenvía el transporte al reproductor real del runtime por su API, no por
   clics sobre etiquetas.

## Regenerar

```bash
python tools/eva/port_kit_css.py
python tools/eva/patch_runtime_bridge.py
```

`port_kit_css.py` es idempotente: reemplaza el bloque marcado. Volvé a correrlo
cada vez que actualices el eva-kit.

## Verificación

- Panel: títulos turquesa, filas con separador, interruptores con píldora,
  X con recuadro, sin scroll a 1440×900.
- Reproductor: píldora blanca con seis iconos; opciones con voz, velocidad y
  resaltado; minimizado deja el FAB turquesa.
- Cambio de voz: pide `voices/consultor/audio/…` (200).
- Tap to play: las tarjetas de `pg006_sec002`–`pg013_sec004` piden sus IDs a la voz activa (`text-pg006-*`, `pg00*_word_*`) y reproducen el clip; sin puente caen a `speechSynthesis`.
- Índice: pegado al borde izquierdo, con X, toggle desde la barra y sin apertura automática al cargar.
- Glosario: pegado al borde derecho, por encima del dock, cierra con su botón o clic afuera.
- Persistencia de voz, velocidad, resaltado y lectura fácil al recargar.
- Las 19 páginas cargan sin `pageerror` ni desborde horizontal.

El adaptador es genérico: está copiado en `eva-kit/adapters/adt-runtime.js` con
las instrucciones para aplicarlo a otro libro con runtime ADT.

## Ajustes finos del panel

- **Tamaño de letra** (4 pasos) escala la raíz del documento y se guarda en `localStorage.evaFontSize`.
- Las opciones de **Escuchar** (reproducción automática, voz, velocidad, resaltado) aparecen sólo con la lectura en voz alta activa.
- Los controles segmentados son blancos con borde, como el 1930; el turquesa queda para la opción activa.
- **Reducir movimiento** y **Atajos de teclado** completan la sección Pantalla.

## Reproductor

El hook de audio del runtime publica su API en `window.__adtPlayer` en cada
render, y el puente la expone para que la píldora del kit no dependa de buscar
botones por nombre accesible:

| Método | Qué hace |
|---|---|
| `__adtKit.hasItems()` | Si la página tiene textos con audio. |
| `__adtKit.playingReal()` | Si el audio está sonando de verdad (mira el elemento, no el estado de React). |
| `__adtKit.play()` / `.pause()` / `.togglePlay()` | Reproducir, pausar, alternar. |
| `__adtKit.stopKeep()` | Detiene sin perder el texto ni el punto de escucha. |

Pausar o cerrar también **corta las otras fuentes de audio** de la página:
`speechSynthesis` (las consignas y refuerzos que hablan las actividades) y el
clip suelto de una tarjeta (`__adtTextAudio`). Sin eso, la voz sintética sigue
hablando después de pulsar Pausa y parece que el botón no responde. Reproducir
cancela cualquier voz sintética pendiente antes de retomar la lectura.

Cerrar la lectura (X) ahora **pausa y apaga el modo**, sin borrar el audio ni
volver al índice 0: al reactivar la lectura en Herramientas, Reproducir continúa
en el mismo texto y segundo. Reproducir/Pausa se decide con `playingReal()`, así
que un doble clic ya no deja el botón invertido, y el botón se deshabilita si la
página no tiene audio.

`click(label)` acota la búsqueda a `#interface-container` y descarta los botones
del propio reproductor del kit, que usan las mismas etiquetas.

## Audio suelto para actividades

`window.__adtKit.playText(id)` reproduce el audio de una `data-id` con la voz,
la velocidad y el volumen activos, sin encolar la lectura de la página.
`stopText()` lo detiene. Las actividades lo usan para el tap-to-play de las
tarjetas (`data-audio-id`), con `speechSynthesis` como respaldo.
