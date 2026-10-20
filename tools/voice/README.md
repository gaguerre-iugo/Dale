# Dos voces en el Cuadernillo Juegos

Integración de dos narradores para el libro, con el mismo comportamiento que
**1930: El viaje**: voz seleccionable desde Herramientas/Configuración y desde
el dock de reproducción, persistente entre páginas y recargadas.

| Clave | Voz | Etiqueta en la UI | Perfil del catálogo |
|---|---|---|---|
| `primary` | `es-419-techagent-3` | **Asesora** | Asesora técnica, 48 años |
| `secondary` | `es-419-commercial-10` | **Consultor** | Consultor de moda, 49 años |

Modelo: `gemini-3.8-flash-tts` (Interactions API), style adulto rioplatense con
sheísmo. Ver `voices test/README.md` para la comparación de voces.

---

## Estructura

```
content/i18n/es-UY/
├── audio/                         # voz histórica del libro (688 mp3)
├── audio_voices.json              # mapa de las dos voces nuevas (688 ids c/u)
└── voices/
    ├── asesora/audio/*.mp3        # 21 archivos (páginas 1 y 2)
    └── consultor/audio/*.mp3      # 21 archivos (páginas 1 y 2)
```

`audio_voices.json` tiene **688 entradas por voz** a propósito: el runtime elige
el mapa completo de la voz activa, no hace fallback por id. Los 21 ids de las
páginas 1 y 2 apuntan a `../voices/<voz>/audio/<id>.mp3`; el resto sigue
apuntando al MP3 histórico. Así ninguna página queda muda mientras la
conversión avanza.

El runtime arma la URL como `./content/i18n/<lang>/audio/<filename>`, por eso el
`../` del mapa: sale de `audio/` y entra en `voices/`.

## Piezas de la integración

| Archivo | Qué hace |
|---|---|
| `content/i18n/es-UY/audio_voices.json` | Declara las dos voces y sus mapas. Con esto el runtime muestra solo el select de Configuración. |
| `assets/voice-ui.css` | Ajusta el ancho del dock (antes el volumen quedaba fuera de pantalla) y permite que la fila de voz del panel envuelva. Se carga desde las 19 páginas. |
| `assets/base.bundle.local.js` | Parcheado para agregar el desplegable de voz al dock flotante. El resto del bundle no cambió. |
| `assets/offline-preloader.js` | Ampliado en runtime con `audio_voices.json` para que las voces funcionen desde `file://`. |

La UI visible de voces es el **panel de Herramientas y el reproductor del eva-kit** (`tools/eva/`): el adaptador monta el selector con las dos voces y el dock nativo queda oculto. El desplegable `adtVoiceDropdown` sigue en el bundle como respaldo por si el adaptador no carga.

El parche del bundle es chico y reversible:

```bash
python tools/voice/patch_dock_voice.py   # idempotente; guarda .orig la primera vez
python tools/voice/patch_preloader.py    # idempotente
```

- Insertar `adtVoiceDropdown` antes de `function Tz(){`.
- Agregar `(0,Fn.jsx)(adtVoiceDropdown,{})` a los hijos de la barra.

El componente reutiliza los mismos primitivos que el resto del runtime
(`We(Fy)`, `le(_d)`, DropdownMenu, RadioGroup), así que respeta tema, foco y
teclado sin CSS extra.

## Generar / regenerar audios

```bash
python tools/voice/generar_paginas.py            # páginas 1 y 2, ambas voces
python tools/voice/generar_paginas.py --force    # regenera lo existente
python tools/voice/build_voice_catalog.py        # reconstruye audio_voices.json
```

- Lee el texto de `speech_texts.json` (no de `texts.json`): respeta la
  preparación para lectura en voz alta (ISBN deletreado, etc.).
- Salida MP3 mono 24 kHz, 96 kbps, `loudnorm` a **−27,5 LUFS** para emparejar
  con el corpus histórico (que mide entre −26 y −32 LUFS). Cuando se convierta
  el libro completo conviene subir todo a −16 LUFS en una sola pasada.
- La API limita a 10 pedidos/minuto: 42 audios ≈ 5 minutos.

## Comportamiento verificado

Con Playwright sobre el libro servido en HTTP y desde `file://`:

- Herramientas → **Voz del narrador** muestra Asesora / Consultor y refleja la
  voz activa.
- Dock de reproducción → desplegable de voz; al cambiar, el reproductor se
  reinicia y el siguiente audio sale de `voices/consultor/…` (HTTP 200).
- El cambio hecho en Herramientas se refleja en el dock y viceversa.
- La elección persiste (`localStorage.narratorVoice`) entre páginas y recargas.
- En páginas sin convertir (ej. pg006) el audio sale del corpus histórico, sin
  silencios ni 404.
- Las 19 páginas cargan sin errores de JS ni desborde horizontal.

## Pendiente

- Convertir el resto de los 688 audios (el mapa ya está preparado).
- Normalización global de volumen cuando esté todo convertido.
- El resaltado palabra por palabra queda fuera del dock porque este libro tiene
  `features.highlight=false` (1930 lo tiene activo y por eso lo muestra).
