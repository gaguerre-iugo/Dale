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
| `tools/eva/patch_runtime_bridge.py` | Agrega `window.__adtKit` al bundle. |

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
   reenvía el transporte a los botones nativos ocultos.

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
- Persistencia de voz, velocidad, resaltado y lectura fácil al recargar.
- Las 19 páginas cargan sin `pageerror` ni desborde horizontal.

El adaptador es genérico: está copiado en `eva-kit/adapters/adt-runtime.js` con
las instrucciones para aplicarlo a otro libro con runtime ADT.

## Ajustes finos del panel

- **Tamaño de letra** (4 pasos) escala la raíz del documento y se guarda en `localStorage.evaFontSize`.
- Las opciones de **Escuchar** (reproducción automática, voz, velocidad, resaltado) aparecen sólo con la lectura en voz alta activa.
- Los controles segmentados son blancos con borde, como el 1930; el turquesa queda para la opción activa.
- **Reducir movimiento** y **Atajos de teclado** completan la sección Pantalla.
