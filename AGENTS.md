# Propuesta Dale!: Cuadernillo Juegos — ADT Bundle Reference

This document describes the structure of this Accessible Digital Textbook (ADT) bundle **as it exists in this repository**. Use it to orient yourself before editing anything.

## About This Book

**Propuesta Dale!: Cuadernillo Juegos** — Este cuadernillo de la Propuesta Dale! reúne juegos y actividades para iniciar a niñas y niños en la alfabetización, especialmente en el reconocimiento de vocales, consonantes y sonidos iniciales de palabras. Está dirigido a nivel inicial o primeros años de primaria, con consignas guiadas por una educadora y uso de tarjetas, imágenes, clasificación, parejas y tableros. Fue editado en Montevideo, Uruguay, y está escrito en español; su enfoque es lúdico, oral y progresivo, centrado en la conciencia fonológica y la asociación entre sonidos y letras.

- **Source language**: `es-UY`
- **Available languages in this bundle**: `es-UY`
- **Total pages**: 12 (`pg001_sec001` … `pg013_sec004`)
- **Glossary**: yes (66 entries)
- **Texts / audio**: 437 text IDs, 436 MP3 files

## Quick Overview

An ADT bundle is a self-contained, offline-capable web app for reading a book. It has:

- One HTML file per page/section
- A localization system (`i18n`) for text, audio, and glossary — keyed by stable IDs
- A `pages.json` manifest that defines reading order
- A shared `assets/` directory with the JS runtime, fonts, and UI resources

**This repository is the exported web app, deployed from the repository root.** There is no `adt/` subdirectory, no `qz*.html` quiz files, and no pipeline artifacts (`.db`, `.pdf`, `config.yaml`, raw PDF page renders, source TTS) under version control. Everything committed here is what gets served, so `main` is deployable as-is.

- All 15 content pages are **activities**: the interactive logic is an inline `<script>` at the end of each page section, registered with `window.adtRegisterCustomActivity(section, { validate, reset })`.
- The book is a static site. It can be served by any static server, or published with GitHub Pages from `/` (`.nojekyll` is already present).
- It also opens directly from `file://` because `assets/offline-preloader.js` embeds the pages and JSON (see [Runtime and page loading](#runtime-and-page-loading)).

## Directory Structure

```
Dale/                                  # repository root = the web app
├── index.html                         # Entry point: redirects to pg001_sec001.html
├── cover.png                          # Thumbnail / catalogue cover
├── imsmanifest.xml                    # SCORM 1.2 manifest
├── README.md
├── AGENTS.md
├── .nojekyll                          # Keep GitHub Pages from running Jekyll
├── .gitignore
├── .gitattributes
│
├── pg001_sec001.html                  # One HTML file per page (12 files)
├── pg002_sec001.html
├── pg003_sec001.html
├── pg004005_sec001.html               # Two printed pages in one section
├── pg006_sec002.html                  # Activity pages from here on
├── ...
└── pg013_sec004.html
│
├── images/                            # 96 images referenced by the pages
│   ├── pg001_im001.png                # Full-page / decorative images
│   ├── pg006_im010_crop_v1.png        # Cropped activity images
│   ├── pg009_upload1.png              # Card / tile images used by activities
│   └── ...
│
├── content/
│   ├── pages.json                     # Reading order manifest
│   ├── toc.json                       # Table of contents (10 entries)
│   ├── tailwind_output.css            # Compiled Tailwind CSS
│   ├── navigation/
│   │   └── nav.html                   # Navigation fragment
│   └── i18n/
│       └── es-UY/
│           ├── texts.json             # Display text (textId → string)
│           ├── speech_texts.json      # Prepared read-aloud wording
│           ├── audios.json            # Audio mappings (textId → mp3 filename)
│           ├── audio_voices.json      # Two narrators: Asesora (primary) / Consultor (secondary)
│           ├── voices/                # Per-voice audio: voices/{asesora,consultor}/audio/*.mp3
│           ├── glossary.json          # Glossary (word → object)
│           ├── images.json            # {} placeholder
│           ├── videos.json            # {} placeholder
│           ├── timecode/
│           │   └── timecode_output.json   # {} (no word-level sync for this book)
│           └── audio/                 # 436 MP3 files (base/historic voice)
│
└── assets/
    ├── config.json                    # Title, languages, feature flags
    ├── base.bundle.local.js           # Main JS runtime (patched: voice menu + __adtKit bridge)
    ├── eva.css                        # EVA skin + ported eva-kit panels (loaded by every page)
    ├── eva-ui.js                      # EVA adapter: toolbar, tools panel, player (defer)
    ├── voice-ui.css                   # Legacy layout fixes for the native voice controls
    ├── offline-preloader.js           # Generated: embeds pages + JSON for file://
    ├── scorm.js                       # SCORM 1.2 bridge
    ├── base.bundle.min.js             # Minified runtime copy — NOT loaded
    ├── base.bundle.min.js.map
    ├── activities.bundle.local.js     # Not loaded by any page
    ├── auto-fit.js                    # Not loaded by any page
    ├── tailwind_css.css               # Not loaded (pages use content/tailwind_output.css)
    ├── fonts.css                      # Local @font-face declarations
    ├── fonts/                         # Atkinson Hyperlegible + Merriweather woff2
    ├── libs/fontawesome/              # Icon library (css + webfonts)
    ├── sounds/                        # UI feedback sounds
    ├── favicon_io/                    # Favicons / web manifest
    ├── symbols/                       # Unused PNGs from another book
    └── interface_translations/
        └── es-UY/
            └── interface_translations.json
```

## Runtime and page loading

`index.html` is only a redirect: it sends the reader to `pg001_sec001.html` and preserves `location.search` and `location.hash`.

Every page loads three classic scripts at the end of `<body>`, **in this order**:

```html
<script src="./assets/offline-preloader.js"></script>
<script src="./assets/scorm.js"></script>
<script src="./assets/base.bundle.local.js"></script>
```

- **`offline-preloader.js`** is generated. It holds an inline map of 25 keys — all 12 page HTML files, `index.html`, `assets/config.json`, `content/pages.json`, `content/toc.json`, `content/navigation/nav.html`, the six `content/i18n/es-UY/*.json` files, `content/i18n/es-UY/timecode/timecode_output.json`, and `assets/interface_translations/es-UY/interface_translations.json`. It also carries `audio_voices.json` through an added runtime assignment (`tools/voice/patch_preloader.py`), so the voice menu works from `file://`. It does **not** embed images, audio or CSS. Its purpose is to let the book open from `file://` (where `fetch` of local JSON is blocked). **After editing any of those files, regenerate this preloader**: `python tools/voice/refresh_preloader.py` re-reads pages and JSON from disk, and `python tools/voice/patch_preloader.py` refreshes the embedded `audio_voices.json`; otherwise the `file://` copy serves stale content while the HTTP-served copy shows the edit.
- **`scorm.js`** exposes the SCORM 1.2 API when the bundle runs inside an LMS.
- **`base.bundle.local.js`** is the reader runtime (interface, dock, glossary, read-aloud, easy-read, state). It is patched —not hand-edited— twice: the narrator dropdown in the native dock (`tools/voice/patch_dock_voice.py`) and the `window.__adtKit` bridge that lets the EVA adapter read/change settings and drive playback, and lets activities play a single text with `playText(id)` (`tools/eva/patch_runtime_bridge.py`). A backup of the original bundle is kept by the first script.
- **`eva.css`** is the EVA skin and the ported eva-kit components (toolbar, player, panels). The panel block is appended by `tools/eva/port_kit_css.py`, which rewrites the kit's `url("../icons/…")` to `url("./icons/…")`.
- **`eva-ui.js`** mounts the EVA toolbar, the custom **Herramientas** panel and the kit read-aloud player, and forwards every action to the runtime. It hides the native dock and the native read-aloud toolbar, which stay in the DOM for anchoring and transport. Settings need `window.__adtKit`.
- **`voice-ui.css`** is the legacy layout fix for the native voice controls. The visible UI no longer uses it; kept for the hidden native toolbar.

The page content starts hidden (`#content` has the `opacity-0` class) and the runtime removes it after the interface initialises. On a cold load the fade-in can take a second or two; that is expected.

`<meta name="page-section-id">` is the **1-based index of the page in `pages.json`** (not the printed page number, not the section id). It drives the "N of 19" dock counter, so it must be renumbered whenever the order changes. Identity lives in `<meta name="title-id">`.

Pages also contain a large page-scoped `<style>` block with the "adt-skin" overrides (backgrounds, activity numbering, notepad blocks, image caps). Page styling is therefore split between `content/tailwind_output.css` and those inline blocks — check both before chasing a layout bug.

## The Text ID System

Every piece of displayable text has a unique, stable **text ID**. The same ID can appear:

1. As a `data-id` attribute on HTML elements in page files
2. As a key in `content/i18n/{lang}/texts.json` (the display string)
3. As a key in `content/i18n/{lang}/speech_texts.json` (the prepared read-aloud wording)
4. As a key in `content/i18n/{lang}/audios.json` (the audio filename)

### ID Naming Conventions

| Pattern | What it is | Example |
|---|---|---|
| `pg{NNN}_n{NNNN}` | Page text node (cover, front matter, credits) | `pg001_n0002` |
| `pg{NNN}_im{NNN}` | Full-page image description | `pg001_im001` |
| `pg{NNN}_im{NNN}_crop_v{N}` | Cropped activity image description | `pg006_im010_crop_v1` |
| `pg{NNN}_upload{N}` | Card / tile image description inside an activity | `pg009_upload1` |
| `text-pg{NNN}-{NN}` | Activity instruction or label | `text-pg006-43` |
| `text-pg{NNN}-{NN}-{N}` | Fragment of a long activity text | `text-pg011-43-1` |
| `text-pg{NNN}-{NN}_easy_read` | Easy Read wording of that text (read-aloud only) | `text-pg006-43_easy_read` |
| `pg{NNN}_s{N}` | Activity section root (no text entry by design) | `pg006_s2` |
| `pg{NNN}_sec{NNN}_ans_target-{x}` | Answer-feedback audio for drag activities (audio only) | `pg008_sec002_ans_target-e` |
| `gl{NNN}` / `gl{NNN}_def` | Glossary word / definition | `gl001`, `gl001_def` |

In this book, IDs keep their original pipeline numbering (~`text-pg006-40`, `text-pg013-28`); the numbers do **not** restart at 1 on each page. Do not renumber them: they are the join key across HTML, `texts.json`, `speech_texts.json`, `audios.json`, and the MP3 filenames.

### Three kinds of ID

Not every key in `texts.json` has a `data-id` in the HTML, and not every `data-id` has a text entry. The 437 IDs break down as:

- **232 assigned to DOM elements** — text spans, labels, image descriptions.
- **205 audio-only** — the runtime or the activity code looks them up by a computed name rather than by a `data-id`:
  - `*_easy_read` (67) — the Easy Read variant, played when Easy Read is on.
  - `gl{NNN}` / `gl{NNN}_def` (132) — glossary pronunciation, triggered from the glossary UI.
  - `pg{NNN}_sec{NNN}_ans_target-*` (6) — feedback lines for drag-to-classify activities.
- **17 DOM ids with no text entry**, on purpose:
  - `pg{NNN}_s{N}` — the activity section root; it has no plain text entry, only `{id}_easy_read`, a spoken summary of the whole activity.
  - `text-pg013-29` … `text-pg013-37` — empty `sr-feedback` spans that the activity script fills with "✓", "✗" or "Falta".

### Tap to play en actividades

Una tarjeta o botón puede llevar `data-audio-id="<text id>"`. Al tocarlo, `window.__adtKit.playText(id)` reproduce ese audio con la voz, la velocidad y el volumen activos, sin encolar la lectura de la página; `stopText()` lo detiene. El archivo vive en `voices/<voz>/audio/<id>.mp3` y se declara en `audio_voices.json`. Si el puente no está o la ID no tiene audio, la actividad cae a `speechSynthesis` (voz del navegador). Ejemplo: `pg006_sec002.html`, con 8 tarjetas (`text-pg006-53` … `text-pg006-60`); también `pg007_sec002` (12 parejas, `pg007_word_*` + `text-pg007-41`), `pg008_sec002` (12 tarjetas, `pg008_word_*`) y `pg009`–`pg013` (16, 15, 8, 16 y 9 tarjetas, `pg00{9,10,11,12,13}_word_*`). Para generar las palabras de una actividad en una sola toma por voz y cortarlas: `tools/voice/generar_bloques.py --ids … --sep ". " --trim --tempo 0.88`; `generar_palabras.py` queda para palabras aisladas.

## Key Files in Detail

### `content/pages.json` — Reading Order

An ordered array that defines the navigation spine (19 entries, no quizzes):

```json
[
  { "section_id": "pg001_sec001", "href": "pg001_sec001.html" },
  { "section_id": "pg002_sec001", "href": "pg002_sec001.html" },
  { "section_id": "pg004005_sec001", "href": "pg004005_sec001.html" },
  { "section_id": "pg006_sec002", "href": "pg006_sec002.html" }
]
```

- `section_id` — matches `<meta name="title-id">` in the HTML file
- `href` — path relative to the repository root
- This book's entries carry **no `page_number`** field.
- The order is also duplicated in the `page-section-id` meta tag of each page and in the `imsmanifest.xml` file list; keep the three in sync.

### `content/toc.json` — Table of Contents

Ten entries: the cover, the "CUADERNILLO" section cover, and one per activity. Each has `section_id`, `href`, `title`, `chapter_id`, and `level` (1 = main section, 2 = nested; everything here is level 1, so the index renders a flat list).

Activity titles follow `{N} {kicker}: {title}` — e.g. `1 Vocales: ¿Qué voy a decir?`, without the word "Actividad" so the index stays short. `N` comes from `.adt-head-num` (`data-adt-num`), the kicker from `.adt-head-kicker` and the title from `.adt-head-title`, written in sentence case even though the page renders it in uppercase. `chapter_id` is the `data-id` of that `.adt-head-title`, so the runtime can mark the current chapter. Activity entries also carry `"activity": true`: `eva-ui.js` uses that flag to add the progress label under each entry — **Por hacer**, **Incompleta** (first interaction) or **Completa** (validation passed) — stored in `localStorage.evaActivityProgress`. The index panel lists these entries; the "Lista de páginas" tab still lists `pages.json`.

### `content/i18n/{lang}/texts.json` — All Text Content

A flat `Record<textId, string>` with 437 entries. Example:

```json
{
  "pg001_n0002": "Propuesta Dale!",
  "pg001_im001": "Lápiz rojo afilado, inclinado en diagonal.",
  "gl001": "acertar",
  "gl001_def": "Elegir la respuesta correcta."
}
```

### `content/i18n/{lang}/speech_texts.json` — Prepared Read-Aloud Text

Same 437 keys, same wording by default; 90 entries differ from `texts.json` because numbers, ISBNs and edition data are written out for speech (e.g. `"ISBN: 978-9915-9930-9-6"` → `"i ese be ene: nueve siete ocho guion …"`). Keep display text and speech text independent: change the display value in `texts.json` only when the visible string must change, and `speech_texts.json` only when the pronunciation must change.

### `content/i18n/{lang}/audios.json` — Audio Mappings

Maps each text ID to its MP3 filename in `audio/`:

```json
{
  "pg001_n0002": "pg001_n0002.mp3",
  "gl001": "gl001.mp3"
}
```

Audio files live at `content/i18n/{lang}/audio/{filename}.mp3`. The mapping is 1:1 and complete: 436 keys, 436 files, no orphans.

### `content/i18n/{lang}/audio_voices.json` — Two Narrators

Optional. Declares alternate narrators; the runtime shows a "Voz del narrador" control only when **both** maps are non-empty.

```json
{
  "voices": {
    "primary":   { "label": "Asesora",   "audios": { "pg001_n0002": "../voices/asesora/audio/pg001_n0002.mp3" } },
    "secondary": { "label": "Consultor", "audios": { "pg001_n0002": "../voices/consultor/audio/pg001_n0002.mp3" } }
  }
}
```

The runtime builds `./content/i18n/{lang}/audio/{filename}`, so the `../` is what lets a voice live in `voices/<voz>/audio/`. Each map must cover **all** 688 ids (converted pages point at the voice, the rest fall back to the historical MP3); the runtime picks one whole map, it does not fall back per id. The selection persists in `localStorage.narratorVoice` and is exposed in both the tools panel and the read-aloud dock. See `tools/voice/README.md`.

### `content/i18n/{lang}/glossary.json` — Glossary

Keyed by word (lowercase). 66 entries, each with the word, a simple definition, inflected variations for matching, decorative emoji, and the `gl{NNN}` id that ties it to the audio:

```json
{
  "acertar": {
    "word": "acertar",
    "definition": "Elegir la respuesta correcta.",
    "variations": ["acertar", "acertaste", "acierto"],
    "emoji": "🎯✅",
    "id": "gl001"
  }
}
```

The runtime uses `variations` to match and highlight glossary words anywhere in the page text.

### `assets/config.json` — Feature Flags and Languages

Controls which features the reader UI enables. This book's config:

```json
{
  "title": "Propuesta Dale!: Cuadernillo Juegos",
  "bundleVersion": "1",
  "languages": {
    "available": ["es-UY"],
    "default": "es-UY"
  },
  "features": {
    "signLanguage": false,
    "easyRead": true,
    "glossary": true,
    "eli5": false,
    "readAloud": true,
    "autoplay": true,
    "showTutorial": true,
    "showNavigationControls": true,
    "describeImages": true,
    "notepad": false,
    "state": true,
    "characterDisplay": false,
    "highlight": false,
    "activities": true
  },
  "analytics": {
    "enabled": false,
    "siteId": 0,
    "trackerUrl": "https://unisitetracker.unicef.io/matomo.php",
    "srcUrl": "https://unisitetracker.unicef.io/matomo.js"
  },
  "defaultSettings": {
    "dockLayout": { "width": "full", "position": "bottom", "align": "spread" },
    "theme": "dark",
    "iconSize": "md",
    "reduceMotion": false
  },
  "lockedSettings": ["dockLayout", "theme", "iconSize", "reduceMotion"]
}
```

### `imsmanifest.xml` — SCORM 1.2

Declares one organization and one `webcontent` resource at `index.html`, listing `index.html` plus the 12 page files. It does not list `assets/`, `content/` or `images/`; when packaging for an LMS, those folders still have to be shipped with the SCO. Keep the page list in sync when adding or removing a page.

## Page HTML Structure

Each page is a standalone HTML file at the repository root. Trimmed example:

```html
<!DOCTYPE html>
<html lang="es-UY">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Propuesta Dale!: Cuadernillo Juegos</title>
    <meta name="title-id" content="pg001_sec001" />     <!-- section identity -->
    <meta name="page-section-id" content="1" />          <!-- 1-based index in pages.json -->
    <link href="./content/tailwind_output.css" rel="stylesheet">
    <link href="./assets/libs/fontawesome/css/all.min.css" rel="stylesheet">
    <link href="./assets/fonts.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible&display=swap" rel="stylesheet">
    <style>/* page-scoped "adt-skin" overrides */</style>
</head>
<body>
  <main>
    <div id="content" class="container opacity-0">
      <section data-section-type="front_cover" data-section-id="pg001_sec001">
        <img data-id="pg001_im001" src="images/pg001_im001.png" alt="...">
        <span data-id="pg001_n0002">Propuesta Dale!</span>
      </section>
    </div>
  </main>

  <div class="relative z-50" id="interface-container"></div>
  <div class="relative z-50" id="nav-container"></div>
  <script src="./assets/offline-preloader.js"></script>
  <script src="./assets/scorm.js"></script>
  <script src="./assets/base.bundle.local.js"></script>
</body>
</html>
```

Key conventions:

- **`data-id` on text elements** links to `texts.json`, `speech_texts.json`, and `audios.json` — the runtime keeps the display string from `texts.json` and uses the prepared wording for read-aloud.
- **`data-id` on images** links to the image description text and audio.
- **Images** use relative paths: `images/{filename}`. All 96 files in `images/` are referenced; none are missing.
- **Google Fonts** is a progressive enhancement: `assets/fonts.css` ships the same families locally, so the book still renders offline.
- **`data-section-type`** values in this book: `front_cover`, `inside_cover`, `separator`, `activity_other`, `activity_custom_vowel_rounds`, `activity_custom_multi_select_audio`, `activity_custom_sound_selection`.
- **Activities** keep their state in `data-*` attributes and classes, and expose `validate` / `reset` to the runtime. Read an existing activity page before copying one: the scripts assume specific class names (`letter-btn`, `image-card`, `image-tile`, `sr-feedback`) and attributes (`data-activity-item`, `data-letter-group`, `data-sound-letter`, `data-word`).

## How to Edit Text

To change text content for a given language, update the display text independently from its read-aloud wording:

1. **`texts.json`** — Change the value in `content/i18n/{lang}/texts.json` for the text ID.
2. **The HTML file** — The same text appears inline in the page HTML (as fallback). Update the inner text of the element with the matching `data-id`. Note that the HTML uses numeric character references (`&#xe1;` for `á`); keep that encoding or convert the whole file consistently.
3. **Speech text** (if applicable) — Update `speech_texts.json` only when the pronunciation must change.
4. **Audio** (if applicable) — Replace the MP3 at `content/i18n/{lang}/audio/{textId}.mp3` and keep `audios.json` pointing at that filename.
5. **Regenerate `assets/offline-preloader.js`** — otherwise the `file://` version of the book keeps the old text.

### Editing Glossary

Update both:

- `content/i18n/{lang}/glossary.json` — the entry for the word (including `variations` for matching)
- `content/i18n/{lang}/texts.json` — the `gl{NNN}` and `gl{NNN}_def` entries

## How to Add a New Page

1. **Create the HTML file** — Copy an existing page as a template (a `separator` page for static content, an activity page if it needs interaction). Name it `pg{NNN}_sec{NNN}.html` following the existing numbering. Do not reuse an existing `pg{NNN}` prefix: IDs are global.
2. **Set the meta tags** — `<meta name="title-id" content="pg021_sec001">` and the correct `page-section-id`.
3. **Add text with `data-id` attributes** — Use a new `text-pg{NNN}-{NN}` or `pg{NNN}_n{NNNN}` range that no other page uses.
4. **Add images** — Place the files in `images/` and reference them as `images/{filename}`; give each `<img>` a `data-id` (e.g. `pg021_im001`) so it gets alt text and audio.
5. **Update `pages.json`** — Insert the entry at the correct position in reading order.
6. **Renumber `page-section-id`** — Update the `<meta name="page-section-id">` in every page after the insertion point (it is a 1-based index into `pages.json`).
7. **Update `imsmanifest.xml`** — Add the `<file href="…"/>` line, and `content/toc.json` if the page belongs in the table of contents.
8. **Add i18n entries** — Every `data-id` needs an entry in `texts.json` and `speech_texts.json`; image IDs need a description in `texts.json`.
9. **Add audio entries** — Map each new ID in `audios.json` and put the MP3 in `content/i18n/{lang}/audio/`. For Easy Read support, also add `{id}_easy_read` audio.
10. **Regenerate `assets/offline-preloader.js`** and test both over HTTP and from `file://`.

## How to Add a New Language

1. Create `content/i18n/{lang}/` with all required files:
   - `texts.json` — translated strings for every text ID
   - `speech_texts.json` — read-aloud wording for every text ID
   - `audios.json` — audio filename mappings (the same naming pattern can be reused)
   - `glossary.json` — translated glossary entries
   - `images.json` / `videos.json` — `{}` placeholders
   - `timecode/timecode_output.json` — `{}`
   - `audio/` — MP3 files for each text ID

2. Add the language code to `languages.available` in `assets/config.json`.

3. Add UI translations at `assets/interface_translations/{lang}/interface_translations.json`.

4. Regenerate `assets/offline-preloader.js` (it embeds the i18n JSON it knows about).

## Where to Find Things

| What you need | Where to look |
|---|---|
| Rendered page HTML | `pg{NNN}_sec{NNN}.html` (repository root) |
| Entry point | `index.html` (redirects to the first page) |
| Page images | `images/` |
| All text content | `content/i18n/es-UY/texts.json` |
| Prepared read-aloud text | `content/i18n/es-UY/speech_texts.json` |
| Audio file mappings | `content/i18n/es-UY/audios.json` |
| Audio MP3 files | `content/i18n/es-UY/audio/` |
| Glossary | `content/i18n/es-UY/glossary.json` |
| Reading order | `content/pages.json` |
| Table of contents | `content/toc.json` |
| Book config & features | `assets/config.json` |
| CSS styles | `content/tailwind_output.css` + the inline `<style>` of each page |
| JS runtime | `assets/base.bundle.local.js` |
| Offline copy of pages and JSON | `assets/offline-preloader.js` (generated) |
| SCORM bridge | `assets/scorm.js` |
| UI string translations | `assets/interface_translations/es-UY/interface_translations.json` |
| Cover thumbnail | `cover.png` |
| SCORM manifest | `imsmanifest.xml` |

## Audio Naming Conventions

| Pattern | What it is |
|---|---|
| `pg{NNN}_n{NNNN}.mp3` | Page text node read-aloud |
| `pg{NNN}_im{NNN}.mp3` | Full-page image description |
| `pg{NNN}_im{NNN}_crop_v{N}.mp3` | Activity image description |
| `pg{NNN}_upload{N}.mp3` | Card / tile image description |
| `text-pg{NNN}-{NN}.mp3` | Activity text read-aloud |
| `text-pg{NNN}-{NN}_easy_read.mp3` | Easy Read wording of an activity text |
| `pg{NNN}_s{N}_easy_read.mp3` | Easy Read summary of a whole activity |
| `pg{NNN}_sec{NNN}_ans_target-{x}.mp3` | Answer feedback for drag activities |
| `gl{NNN}.mp3` | Glossary word pronunciation |
| `gl{NNN}_def.mp3` | Glossary definition read-aloud |

Per-voice files keep the same id as the filename but live under `content/i18n/es-UY/voices/{asesora,consultor}/audio/`, and are declared in `audio_voices.json`.

Filenames match their text ID in every case, so `audios.json` can stay a 1:1 map.

## Important: What Not to Edit

- **`assets/base.bundle.local.js`** — compiled JS runtime; do not edit by hand. The dock narrator menu is added by `tools/voice/patch_dock_voice.py` (idempotent, keeps a `.orig` backup). `assets/base.bundle.min.js` and `activities.bundle.local.js` are other builds of the same runtime and are not loaded by any page.
- **`assets/offline-preloader.js`** — generated; regenerate it instead of hand-editing.
- **`assets/libs/`** — vendored third-party libraries (FontAwesome).
- **`assets/fonts/`** and **`assets/fonts.css`** — font files and their declarations.
- **`assets/sounds/`** — UI feedback sounds.
- **`content/tailwind_output.css`** — compiled from all HTML files. If you add new Tailwind classes to HTML, this file must be regenerated (the inline page styles are not part of it).

## Known Loose Ends

Files that exist in the bundle but are not used by it. They are harmless, and removing them is a pending cleanup rather than a bug:

- `assets/symbols/` — 10 PNGs (~1 MB) about ecosystems (biomes, cactus, photosynthesis…); leftovers from another book.
- `assets/auto-fit.js`, `assets/activities.bundle.local.js`, `assets/tailwind_css.css` — never referenced.
- `assets/base.bundle.min.js`, `assets/base.bundle.min.js.map` — unused build of the runtime (~4.5 MB).
- `content/i18n/es-UY/images.json`, `videos.json`, `timecode/timecode_output.json` — empty placeholders (`{}`).
- The runtime requests `content/i18n/es-UY/timecode/timecode_voices.json`, which does not exist; the 404 is expected and handled (no timecoded alternate voice). `audio_voices.json` now exists and is embedded by the preloader patch.
