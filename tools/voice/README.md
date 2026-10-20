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


## Fluidez: lectura por bloques

Generar cada texto por separado hace que la tapa y los creditos suenen a lista:
cada clip trae su propia entonacion y sus silencios. `generar_bloques.py` pide
**una toma continua por bloque de items cortos** y la corta en los limites
reales de cada item.

- La alineacion es forzada: faster-whisper (`base`, CPU int8) da timestamps por
  palabra y se alinean contra `speech_texts.json` con Needleman-Wunsch. No
  depende de que el modelo respete pausas: pedir `<long pause>` daba conteos
  distintos en cada toma.
- Solo agrupa items cortos (tapa, creditos). Los textos largos o con numeros
  deletreados (ISBN, datos de edicion) siguen generandose por item: ahi el
  propio texto tiene pausas internas y la alineacion de numeros es fragil.
- Requisito: `faster-whisper` ademas de `ffmpeg`.

Estado actual: **las dos voces** usan bloques en las paginas 1 y 2 (5 + 10
items). Asesora se genero con `gemini-3.8-flash-tts` y Consultor con
`gemini-3.8-flash-lite-tts`, porque la cuota diaria del modelo Flash (100
pedidos/dia en Tier 1) se agoto. La cuota es por proyecto y por modelo: el
mismo API key tiene una cuota distinta para Lite. Cuando se renueve Flash,
Consultor se puede regenerar con el modelo grande:

```bash
python tools/voice/generar_bloques.py --voice consultor
```

Cada segmento se verifico por transcripcion (faster-whisper).

### Ritmo

Los audios de las paginas 1 y 2 se bajaron un 12% con `atempo` (preserva el
tono) porque la toma continua salia mas rapida que la generacion item por item:

```bash
python tools/voice/ajustar_tempo.py --factor 0.88 --paginas pg001 pg002
```

No es idempotente: correrlo dos veces vuelve a frenar. Si 0.88 sigue rapido,
probá 0.85; para volver atras, `git checkout` de los MP3.


### Frases que en el libro son dos items

En la tapa, "CUADERNILLO" y "JUEGOS" son dos `data-id` distintos. Generados por
separado suenan a dos palabras sueltas: la primera cae como final de frase y la
segunda arranca de cero. `generar_frase.py` los pide juntos ("Cuadernillo
Juegos"), los corta en el punto medio entre las dos palabras y conserva la
entonacion continua. Verificado con F0: la primera termina en 158 Hz y la
segunda arranca en 158 Hz y cae a 133 (antes terminaba en 75 y reiniciaba en
100).

```bash
python tools/voice/generar_frase.py --voice consultor \
  --model gemini-3.8-flash-lite-tts --ids pg001_n0003 pg001_n0004
```

Aplicado a Consultor. Asesora conserva la version por bloques hasta que se
renueve la cuota de Flash; ahi conviene regenerar la misma frase con el modelo
grande para no mezclar timbres.
