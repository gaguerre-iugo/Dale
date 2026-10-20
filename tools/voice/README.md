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
├── audio/                         # voz histórica del libro (429 mp3)
├── audio_voices.json              # mapa de las dos voces nuevas (429 ids c/u)
└── voices/
    ├── asesora/audio/*.mp3        # 53 archivos (páginas 1-2 + palabras de pg006-008)
    └── consultor/audio/*.mp3      # 53 archivos (páginas 1-2 + palabras de pg006-008)
```

`audio_voices.json` tiene **429 entradas por voz** a propósito: el runtime elige
el mapa completo de la voz activa, no hace fallback por id. Los 53 ids
convertidos apuntan a `../voices/<voz>/audio/<id>.mp3`; el resto sigue
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
- La API limita a ~10 pedidos/minuto: `generar_palabras.py` espacia 7 s entre palabras.

## Comportamiento verificado

Con Playwright sobre el libro servido en HTTP y desde `file://`:

- Herramientas → **Voz del narrador** muestra Asesora / Consultor y refleja la
  voz activa.
- Dock de reproducción → desplegable de voz; al cambiar, el reproductor se
  reinicia y el siguiente audio sale de `voices/consultor/…` (HTTP 200).
- El cambio hecho en Herramientas se refleja en el dock y viceversa.
- La elección persiste (`localStorage.narratorVoice`) entre páginas y recargas.
- En pg006 las 8 palabras de la actividad 1 salen de la voz activa; el resto de
  esa página sigue con el corpus histórico, sin silencios ni 404.
- Las 19 páginas cargan sin errores de JS ni desborde horizontal.

## Pendiente

- Convertir el resto de los 429 audios (el mapa ya está preparado).
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


### Palabras de actividades (tap to play)

Las tarjetas de imagen de `pg006_sec002` (actividad 1) llevan `data-audio-id`
con la palabra que nombran. Al tocarlas, la actividad llama a
`window.__adtKit.playText(id)`: el runtime resuelve la voz activa, arma la misma
URL que el reproductor (`./content/i18n/<lang>/audio/<filename>`) y reproduce un
clip suelto con la velocidad y el volumen configurados. En pg006, tocar una
tarjeta reproduce el nombre incluso antes de elegir la vocal; si no hay ronda
iniciada, además muestra el aviso para empezar. Si el puente no está o la ID no
tiene audio, cae a `speechSynthesis` (voz del navegador).

Las 8 palabras son `text-pg006-53` … `text-pg006-60` (`ola`, `ajo`, `uva`,
`ala`, `oso`, `elefante`, `auto`, `uno`). Primero se probaron una por pedido
(`generar_palabras.py`), pero cada toma traía un timbre y una energía apenas
distintos. Ahora se piden las 8 en **una sola toma por voz**, separadas por
punto, y se cortan por alineación forzada; así comparten micrófono, tono y
volumen:

```bash
python tools/voice/generar_bloques.py --voice consultor \
  --model gemini-3.8-flash-lite-tts --sep ". " --trim --tempo 0.88 \
  --ids text-pg006-53 text-pg006-54 text-pg006-55 text-pg006-56 \
        text-pg006-57 text-pg006-58 text-pg006-59 text-pg006-60
```

- `--sep ". "` lee cada palabra como oración, no como lista.
- `--trim` saca el silencio inicial y final de cada clip.
- `--tempo 0.88` empareja con el ritmo de las páginas 1–2.

La toma entera se normaliza, pero la primera palabra suele salir más fuerte y
las últimas más bajas. `nivelar_clips.py` mide cada clip y lo lleva a −27,5 LUFS
con un limitador:

```bash
python tools/voice/nivelar_clips.py --ids text-pg006-53 text-pg006-54 text-pg006-55 \
  text-pg006-56 text-pg006-57 text-pg006-58 text-pg006-59 text-pg006-60
```

Asesora se generó con **Flash** (la cuota se renovó) y Consultor con **Lite**,
igual que sus páginas 1–2. Se verificó concatenando los 8 clips: la secuencia
transcribe “ola, ajo, uva, ala, oso, elefante, auto, uno” y las duraciones quedan
entre 0,47 y 0,93 s en ambas voces; el volumen queda dentro de ±0,2 LUFS.

`generar_palabras.py` queda para casos de una sola palabra o para comparar tomas
individuales.

La misma estrategia se aplicó a las dos actividades siguientes:

| Página | Actividad | Palabras | IDs |
|---|---|---|---|
| `pg007_sec002` | Armar parejas | 12 | `pg007_word_*` + `text-pg007-41` |
| `pg008_sec002` | ¿Dónde va la imagen? | 12 | `pg008_word_*` |

En pg007 y pg008 Flash se agotó de nuevo, así que **Asesora también salió con
Lite**; cuando se renueve conviene regenerar los dos bloques con
`gemini-3.8-flash-tts`. Los clips quedan nivelados y verificados por secuencia.

`build_voice_catalog.py` ahora arma el mapa mirando qué IDs tienen archivo en
`voices/<voz>/audio/`; no depende de una lista fija de páginas. Después de
cambiar el catálogo o una página, sincronizar el preloader:

```bash
python tools/voice/refresh_preloader.py   # vuelve a leer páginas y JSON
python tools/voice/patch_preloader.py     # actualiza audio_voices.json
```

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

El corte queda tan justo que las dos palabras se pegan. `--gap` agrega silencio
al final de cada item (salvo el ultimo); por defecto 120 ms, que sumado al
silencio natural del corte da una separacion de ~200 ms:

```bash
python tools/voice/generar_frase.py --voice consultor \
  --model gemini-3.8-flash-lite-tts --ids pg001_n0003 pg001_n0004 --gap 0.12
```
