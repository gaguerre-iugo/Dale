# Propuesta Dale! — Cuadernillo Juegos

Libro digital accesible (ADT) del **Cuadernillo de Juegos** de la Propuesta Dale!,
un cuadernillo de juegos y actividades para iniciar a niñas y niños en la
alfabetización: reconocimiento de vocales, consonantes y sonidos iniciales.

- **Idioma:** español (es-UY)
- **Páginas:** 12
- **Glosario:** 66 palabras
- **Editorial:** Dale, Montevideo, Uruguay (1.ª edición, 2026)
- **Licencia:** CC BY-NC-SA

## Qué hay en este repositorio

Este repositorio es el **bundle exportado**, listo para publicarse como sitio
estático: `index.html` y las páginas `pg*_sec*.html` viven en la raíz, junto con
`assets/`, `content/` e `images/`.

| Ruta | Qué es |
|---|---|
| `index.html` | Punto de entrada; redirige a la primera página |
| `pg{NNN}_sec{NNN}.html` | Una página del libro (incluye actividades autocontenidas) |
| `images/` | Imágenes referenciadas por las páginas |
| `content/pages.json` | Orden de lectura |
| `content/toc.json` | Índice |
| `content/i18n/es-UY/texts.json` | Textos del libro (por `textId`) |
| `content/i18n/es-UY/speech_texts.json` | Texto preparado para lectura en voz alta |
| `content/i18n/es-UY/audios.json` | Mapa `textId` → MP3 |
| `content/i18n/es-UY/audio/` | Locuciones MP3 |
| `content/i18n/es-UY/glossary.json` | Glosario |
| `content/navigation/nav.html` | Panel de navegación |
| `content/tailwind_output.css` | CSS compilado |
| `assets/config.json` | Título, idiomas y funcionalidades activas |
| `assets/base.bundle.min.js` | Motor de lectura (no editar) |
| `imsmanifest.xml` | Manifiesto SCORM 1.2 |
| `cover.png` | Miniatura de portada |
| `AGENTS.md` | Referencia de estructura del bundle para agentes |

## Cómo verlo en local

Las páginas usan rutas relativas, así que conviene servirlas con un servidor
estático (abrirlas con doble clic también funciona, pero el modo offline del
runtime se apoya en el precargador):

```bash
# con Python
python -m http.server 8000

# con Node
npx serve .
```

Luego abrir <http://localhost:8000/>.

## Publicación

El sitio es 100 % estático. Para publicarlo con GitHub Pages: *Settings → Pages →
Deploy from a branch → `main` / `/ (root)`*. El archivo `.nojekyll` evita que
Jekyll ignore rutas del bundle.

## Créditos

Texto y edición: Propuesta Dale! (Beatriz Graciela Diuk).
Esta adaptación digital conserva la licencia CC BY-NC-SA del original.
