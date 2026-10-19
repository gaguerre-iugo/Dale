# Voces de lectura

Estado acordado con el equipo editorial (19/10/2026).

- **Un idioma** (es-UY).
- **Dos voces.**
  - **Voz 1** — la que ya tiene audio: es la que suena hoy por defecto.
  - **Voz 2** — **pendiente**. Nombre definitivo: **«Voz 2»** (literal, sin
    adjetivos ni nombres propios hasta que se defina).

## Cuándo se completa

Después de que el contenido esté cerrado: la segunda voz se genera sobre el
texto final, no antes (si el texto cambia, hay que regenerar audio y timecodes).

## Qué hace falta para habilitarla

1. Generar el audio de la Voz 2 para todos los textos con narración.
2. Generar los timecodes (sincronización palabra por palabra) de esa voz.
3. Publicar los catálogos que hoy faltan (por eso el runtime pide y recibe 404):

   ```
   content/i18n/es-UY/audio_voices.json
   content/i18n/es-UY/timecode/timecode_voices.json
   ```

   Hasta que existan, el reproductor usa sólo la Voz 1 y los dos 404 son
   esperados (ver `AGENTS.md` del bundle, «Known Loose Ends»).

Los scripts del repositorio del libro **1930: El viaje** sirven de base:

- `tools/generate_dual_uy_voices.py` — genera el audio de las dos voces.
- `tools/generate_whisper_timecodes.py` — genera los timecodes.
- `tools/normalize_voice_timecodes.py` — normaliza los tiempos.

## Lo que NO cambia con la segunda voz

La interfaz (barra, paneles, estilos EVA de `assets/eva.css`) es la misma: el
selector de voz lo dibuja el runtime cuando encuentra el catálogo.
