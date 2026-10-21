/* ============================================================================
   Interfaz EVA del libro — puente con el runtime ADT.
   ----------------------------------------------------------------------------
   Monta la barra, el panel de Herramientas y el reproductor con el marcado del
   eva-kit, y reenvía cada acción al runtime:
     · ajustes  -> window.__adtKit (store del runtime)
     · transporte -> botones del runtime por nombre accesible
   No reescribe el runtime ni el contenido.
   ========================================================================== */
(function () {
  "use strict";

  var VOICES = [
    { key: "primary", label: "Asesora" },
    { key: "secondary", label: "Consultor" }
  ];
  var SPEEDS = [
    { value: 0.5, label: "Lenta" },
    { value: 1, label: "Normal" },
    { value: 1.5, label: "Rápida" },
    { value: 2, label: "Muy rápida" }
  ];

  var ICONS = {
    close: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M5.946 18.826 C5.172 18.406 4.800 17.788 4.800 16.920 C4.800 15.982 5.168 15.409 6.921 13.620 L8.507 12.000 L6.921 10.380 C5.172 8.594 4.800 8.017 4.800 7.087 C4.800 5.726 6.277 4.582 7.615 4.907 C7.981 4.996 9.114 5.894 10.134 6.903 L11.988 8.737 L14.005 6.768 C16.170 4.655 16.651 4.462 18.005 5.162 C18.880 5.615 19.200 6.198 19.200 7.340 C19.200 8.137 18.996 8.433 17.267 10.136 L15.335 12.040 L16.916 13.490 C18.537 14.975 19.200 15.929 19.200 16.777 C19.200 17.588 18.660 18.499 17.965 18.858 C16.697 19.514 16.203 19.316 14.003 17.273 L11.928 15.345 L9.953 17.273 C7.831 19.344 7.288 19.554 5.946 18.826 Z"/></svg>',
    prev: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M20.64 5.28 L7.44 12 L20.64 18.72 Z M3.84 5.28 H5.76 V18.72 H3.84 Z"/></svg>',
    next: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M3.36 5.28 L16.56 12 L3.36 18.72 Z M18.24 5.28 H20.16 V18.72 H18.24 Z"/></svg>',
    play: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M4.629 20.215 C3.493 19.327 3.359 18.457 3.374 12.068 C3.383 8.110 3.483 5.847 3.674 5.302 C4.041 4.252 5.060 3.497 6.061 3.532 C6.529 3.549 9.397 4.806 13.244 6.681 C20.224 10.083 20.400 10.219 20.400 12.196 C20.400 13.817 19.863 14.211 13.110 17.551 C6.547 20.796 5.710 21.059 4.629 20.215 Z"/></svg>',
    pause: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="6.6" y="4.2" width="3.6" height="15.6" rx="0.8"/><rect x="13.8" y="4.2" width="3.6" height="15.6" rx="0.8"/></svg>',
    gear: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M10.859 21.060 C10.727 20.895 10.551 20.544 10.468 20.280 C10.371 19.972 9.804 19.603 8.886 19.250 C7.534 18.731 7.420 18.722 6.849 19.096 C6.259 19.483 6.223 19.471 5.376 18.624 C4.523 17.771 4.515 17.745 4.912 17.138 C5.300 16.546 5.290 16.456 4.663 14.980 C4.218 13.934 3.875 13.440 3.593 13.440 C2.944 13.440 2.602 12.836 2.685 11.837 C2.747 11.083 2.888 10.863 3.480 10.601 C4.029 10.357 4.330 9.946 4.750 8.868 C5.269 7.533 5.278 7.420 4.904 6.849 C4.517 6.259 4.529 6.223 5.376 5.376 C6.229 4.523 6.255 4.515 6.862 4.912 C7.454 5.300 7.544 5.290 9.020 4.663 C10.066 4.218 10.560 3.875 10.560 3.593 C10.560 2.944 11.164 2.602 12.163 2.685 C12.917 2.747 13.137 2.888 13.399 3.480 C13.643 4.029 14.054 4.330 15.132 4.750 C16.467 5.269 16.580 5.278 17.151 4.904 C17.741 4.517 17.777 4.529 18.624 5.376 C19.477 6.229 19.485 6.255 19.088 6.862 C18.700 7.454 18.710 7.544 19.337 9.020 C19.782 10.066 20.125 10.560 20.407 10.560 C21.056 10.560 21.398 11.164 21.315 12.163 C21.253 12.917 21.112 13.137 20.520 13.399 C19.971 13.643 19.670 14.054 19.250 15.132 C18.731 16.467 18.722 16.580 19.096 17.151 C19.483 17.741 19.471 17.777 18.624 18.624 C17.771 19.477 17.745 19.485 17.138 19.088 C16.546 18.700 16.456 18.710 14.980 19.337 C13.934 19.782 13.440 20.125 13.440 20.407 C13.440 21.056 12.836 21.398 11.837 21.315 C11.083 21.253 10.863 21.112 10.601 20.520 Z M12 15.6 A3.6 3.6 0 1 0 12 8.4 A3.6 3.6 0 0 0 12 15.6 Z"/></svg>',
    chevron: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9.5 12 15.5 18 9.5"/></svg>',
    fab: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 14.5 12 8.5 18 14.5"/></svg>'
  };


  /* Estilos que el adaptador necesita. Se inyectan para que el kit funcione en
     cualquier libro ADT sin copiar reglas a mano. */
  var STYLE = [
    'div:has(> [role="group"][aria-label="Controles de lectura en voz alta"]){display:none!important}',
    '#nav-container [role="group"]{visibility:hidden!important;pointer-events:none!important}',
    '[data-eva-tools]{width:min(18.75rem,100vw)!important;max-width:min(18.75rem,100vw)!important;border-radius:var(--ceibal-radius-md)!important}',
    '[data-eva-tools]>.eva-tools-shell{width:100%!important;max-width:none!important;height:min(46rem,calc(100dvh - 4rem))!important;padding:1rem!important;gap:.5rem!important;display:flex!important;flex-direction:column!important;overflow:hidden!important}',
    '[data-eva-tools] .reflow-settings-list{flex:1 1 auto;min-height:0;overflow-y:auto;padding-right:.25rem}',
    '[data-eva-tools] .reflow-panel-control-header{flex:0 0 auto}',
    'body.reflow-book [data-eva-tools] .reflow-setting-row{display:flex!important;flex-wrap:nowrap;align-items:center;justify-content:space-between;gap:.5rem 1rem;padding-block:.2rem!important;min-height:0!important}',
    '[data-eva-tools] .reflow-setting-row>.reflow-setting-label{flex:1 1 auto;min-width:0}',
    '[data-eva-tools] .reflow-setting-row>[role="switch"]{flex:0 0 auto}',
    '[data-eva-tools] .reflow-setting-row:has(>[role="radiogroup"]){flex-direction:column;align-items:stretch}',
    '[data-eva-tools] .reflow-setting-row>[role="radiogroup"]{width:100%}',
    'body.reflow-book [data-eva-tools] .reflow-setting-row.reflow-setting-tts-hidden{display:none!important}',
    'body.reflow-book #reflow-tts-player .reflow-tts-voice-options,body.reflow-book #reflow-tts-player .reflow-tts-speed-options,body.reflow-book #reflow-tts-player .reflow-tts-highlight-options{background:var(--ui-surface)!important;border:1px solid var(--ui-border);border-radius:.6rem}',
    'body.reflow-book [data-eva-tools] .reflow-font-settings-options .reflow-font-size-glyph{font-size:1rem!important}',
    'body.reflow-book [data-eva-tools] .reflow-font-settings-options button[data-reflow-font-size="large"] .reflow-font-size-glyph{font-size:1.3rem!important}',
    'body.reflow-book [data-eva-tools] .reflow-font-settings-options button[data-reflow-font-size="xlarge"] .reflow-font-size-glyph{font-size:1.62rem!important}',
    'body.reflow-book [data-eva-tools] .reflow-font-settings-options button[data-reflow-font-size="xxlarge"] .reflow-font-size-glyph{font-size:1.95rem!important}',
    '[data-eva-tools] .reflow-tts-voice-options,[data-eva-tools] .reflow-tts-speed-options,[data-eva-tools] .reflow-tts-highlight-options{background:var(--ui-surface)!important;border:1px solid var(--ui-border);border-radius:.6rem}',
    '[data-eva-tools] .reflow-tts-voice-options button,[data-eva-tools] .reflow-tts-speed-options button{min-height:2.5rem!important;color:var(--ui-text)!important;font-size:.95rem!important}',
    '[data-eva-tools] .reflow-tts-voice-options button[aria-checked="true"],[data-eva-tools] .reflow-tts-speed-options button[aria-checked="true"]{border-color:var(--ui-accent)!important;color:var(--ui-on-accent)!important;background:var(--ui-accent)!important}',
    '[data-eva-tools] .reflow-tts-highlight-options button[aria-checked="true"]{border-color:var(--ui-accent)!important;color:var(--ui-on-accent)!important;background:var(--ui-accent)!important}',
    '[data-eva-tools] .reflow-shortcuts-link{display:flex;align-items:center;justify-content:space-between;gap:1rem;margin:0;padding:.85rem 0 0;border-top:1px solid var(--ui-border);font-size:1rem}',
    '[data-eva-tools] .reflow-shortcuts-link kbd{background:var(--ui-surface)!important;border:1px solid var(--ui-border)!important;border-radius:.45rem!important;padding:.15rem .45rem!important;font-weight:700;color:var(--ui-text)!important}',
    'body.reflow-book [data-eva-tools] .reflow-settings-block-title{margin:.5rem 0 .125rem!important;font-size:1rem!important;color:var(--ceibal-institutional-600)!important}',
    'body.reflow-book [data-eva-tools] .reflow-panel-control-header button{border:2px solid var(--ceibal-institutional-500)!important;border-radius:.45rem!important;color:var(--ceibal-institutional-700)!important}',
    'body.reflow-book #reflow-tts-player .reflow-tts-fab{background:var(--ceibal-institutional-600)!important;border-color:var(--ceibal-institutional-600)!important;color:#fff!important}',
    /* Ayuda de atajos: fila del panel de Herramientas y modal. */
    '[data-eva-tools] button.reflow-shortcuts-link{display:flex;align-items:center;justify-content:space-between;gap:.75rem;width:100%;margin:.35rem 0 0;padding:.65rem 0 .5rem;border:0!important;border-top:1px solid var(--ui-border)!important;border-radius:.55rem;background:transparent!important;font:inherit;color:inherit;text-align:left;cursor:pointer;transition:color .15s ease}',
    '[data-eva-tools] button.reflow-shortcuts-link kbd{flex:0 0 auto;min-width:4.25rem;padding:.3rem .5rem!important;font-size:.9375rem!important;transition:border-color .15s ease,color .15s ease}',
    /* Sin fondo al pasar el mouse: la fila se lee como el resto de la lista y
       el aviso es el color del texto y del recuadro de la tecla. */
    'body.reflow-book [data-eva-tools] button.reflow-shortcuts-link:hover,body.reflow-book [data-eva-tools] button.reflow-shortcuts-link:active{background:transparent!important;color:var(--ceibal-institutional-700)}',
    'body.reflow-book [data-eva-tools] button.reflow-shortcuts-link:hover kbd{border-color:var(--ceibal-institutional-500)!important;color:var(--ceibal-institutional-700)!important}',
    'body.reflow-book [data-eva-tools] button.reflow-shortcuts-link:focus-visible{outline:3px solid var(--ui-accent);outline-offset:2px;border-radius:.55rem}',
    '.eva-shortcuts{position:fixed;inset:0;z-index:300;display:flex;align-items:center;justify-content:center;padding:1.5rem}',
    '.eva-shortcuts[hidden]{display:none!important}',
    '.eva-shortcuts-backdrop{position:absolute;inset:0;background:rgba(14,24,27,.45)}',
    /* La piel acota todo [role="dialog"] a 18.75rem (el riel del dock), así que
       la ayuda fija su propio ancho y superficie con el id por delante. */
    '#eva-shortcuts .eva-shortcuts-dialog{position:relative;width:min(36rem,100%)!important;max-width:min(36rem,100%)!important;max-height:calc(100dvh - 3rem);overflow-y:auto;background:#edf1f3!important;border:0!important;border-radius:1rem!important;padding:1.5rem 1.75rem 1.75rem!important;box-shadow:0 24px 60px rgba(0,0,0,.28);color:#17313a}',
    '#eva-shortcuts .eva-shortcuts-head{display:flex;align-items:flex-start;justify-content:space-between;gap:1rem;margin-bottom:1.35rem}',
    '#eva-shortcuts .eva-shortcuts-title{margin:0;font-size:1.25rem;font-weight:700;line-height:1.2;color:#15323c}',
    '#eva-shortcuts .eva-shortcuts-close{flex:0 0 auto;display:inline-flex;align-items:center;justify-content:center;width:2.75rem;height:2.75rem;padding:0;border:1px solid #9dbcb7!important;border-radius:.65rem!important;background:#d9e9e6!important;color:#0f4d4a;cursor:pointer}',
    '#eva-shortcuts .eva-shortcuts-close svg{width:1.15rem;height:1.15rem}',
    '#eva-shortcuts .eva-shortcuts-close:hover{background:#cbe2de!important}',
    '#eva-shortcuts .eva-shortcuts-close:focus-visible{outline:3px solid #008078;outline-offset:2px}',
    '#eva-shortcuts .eva-shortcuts-list{margin:0;display:flex;flex-direction:column;gap:.85rem;width:auto!important;max-width:none!important}',
    '#eva-shortcuts .eva-shortcuts-row{display:flex;align-items:center;justify-content:space-between;gap:1.5rem;width:auto!important;max-width:none!important}',
    '#eva-shortcuts .eva-shortcuts-row dt{margin:0;font-size:1.0625rem;line-height:1.3;color:#243b44}',
    '#eva-shortcuts .eva-shortcuts-row dd{margin:0;flex:0 0 auto;width:auto!important}',
    '#eva-shortcuts .eva-shortcuts-row kbd{display:inline-block;min-width:5.5rem;padding:.35rem .7rem;border:1px solid #8d9aa1;border-radius:.4rem;background:#fff;font:inherit;font-size:.9375rem;font-weight:700;text-align:center;color:#1f2f36;box-shadow:0 1px 0 rgba(0,0,0,.08)}',
    'body.eva-shortcuts-open{overflow:hidden}',
    '@media (max-width:30rem){#eva-shortcuts .eva-shortcuts-dialog{padding:1.25rem!important}#eva-shortcuts .eva-shortcuts-row{gap:1rem}#eva-shortcuts .eva-shortcuts-row kbd{min-width:4.5rem;padding:.3rem .5rem}}'
  ].join("\n");

  function ensureStyles() {
    if (document.getElementById("eva-adt-style")) return;
    var st = document.createElement("style");
    st.id = "eva-adt-style";
    st.textContent = STYLE;
    document.head.appendChild(st);
  }

  function kit() { return window.__adtKit || null; }
  function state() { var k = kit(); return k ? k.get() : null; }

  function clickRuntime(labels) {
    var k = kit();
    for (var i = 0; i < labels.length; i += 1) {
      if (k ? k.click(labels[i]) : false) return true;
    }
    return false;
  }

  function isDisabled(label) {
    var k = kit();
    return k ? k.disabled(label) : true;
  }

  function esc(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  /* ── Barra de navegación ───────────────────────────────────────────────── */
  function mountToolbar() {
    if (document.getElementById("reflow-pagination")) return;
    var barra = document.createElement("nav");
    barra.id = "reflow-pagination";
    barra.setAttribute("role", "navigation");
    barra.setAttribute("aria-label", "Controles de lectura");
    barra.innerHTML =
      '<button id="reflow-index" class="reflow-toolbar-action" type="button" aria-label="Índice" aria-haspopup="dialog" aria-expanded="false">' +
        '<span class="reflow-toolbar-icon" data-eva-icon="menu" aria-hidden="true"></span><span class="reflow-toolbar-label">Índice</span></button>' +
      '<button id="reflow-previous" class="reflow-toolbar-action reflow-toolbar-primary" type="button" aria-label="Página anterior">' +
        '<span class="reflow-toolbar-icon" data-eva-icon="left" aria-hidden="true"></span><span class="reflow-toolbar-label">Anterior</span></button>' +
      '<output id="reflow-page-status" aria-live="off" aria-label="Página">' +
        '<span id="reflow-progress-long">pág. 1 de 1</span><span id="reflow-progress-short">1/1</span><span id="reflow-progress-minimal">1/1</span></output>' +
      '<button id="reflow-next" class="reflow-toolbar-action reflow-toolbar-primary" type="button" aria-label="Página siguiente">' +
        '<span class="reflow-toolbar-icon" data-eva-icon="right" aria-hidden="true"></span><span class="reflow-toolbar-label">Siguiente</span></button>' +
      '<button id="reflow-glossary" class="reflow-toolbar-action" type="button" aria-label="Glosario" aria-haspopup="dialog" aria-expanded="false">' +
        '<span class="reflow-toolbar-icon" data-eva-icon="glossary" aria-hidden="true"></span><span class="reflow-toolbar-label">Glosario</span></button>' +
      '<button id="reflow-tools" class="reflow-toolbar-action" type="button" aria-label="Herramientas" aria-haspopup="dialog" aria-expanded="false">' +
        '<span class="reflow-toolbar-icon" data-eva-icon="gear" aria-hidden="true"></span><span class="reflow-toolbar-label">Herramientas</span></button>';
    document.body.appendChild(barra);

    barra.querySelector("#reflow-index").addEventListener("click", function () { clickRuntime(["Menú principal", "Main Menu"]); });
    barra.querySelector("#reflow-previous").addEventListener("click", function () { clickRuntime(["Página anterior", "Previous page"]); });
    barra.querySelector("#reflow-next").addEventListener("click", function () { clickRuntime(["Página siguiente", "Next page"]); });
    barra.querySelector("#reflow-glossary").addEventListener("click", function () { clickRuntime(["Glosario", "Glossary"]); });
    barra.querySelector("#reflow-tools").addEventListener("click", function () {
      var dlg = findSettingsDialog();
      if (dlg) { closeNativeDialog(); return; }
      clickRuntime(["Configuración", "Settings"]);
    });
  }

  /* ── Panel de Herramientas ─────────────────────────────────────────────── */
  function findSettingsDialog() {
    var ds = document.querySelectorAll("[role='dialog'][data-dock-panel]");
    for (var i = 0; i < ds.length; i += 1) {
      if ((ds[i].textContent || "").indexOf("Configuración") >= 0 || ds[i].getAttribute("data-eva-tools") === "1") return ds[i];
    }
    return null;
  }

  function closeNativeDialog() {
    document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", code: "Escape", keyCode: 27, which: 27, bubbles: true }));
  }

  /* ── Atajos de teclado ─────────────────────────────────────────────────── */
  var SHORTCUTS = [
    { keys: "Alt+I", label: "Abrir el índice", action: "index" },
    { keys: "Alt+H", label: "Abrir Herramientas", action: "tools" },
    { keys: "Alt+G", label: "Abrir el glosario", action: "glossary" },
    { keys: "Alt+A", label: "Mostrar u ocultar esta ayuda", action: "help" },
    { keys: "Esc", label: "Cerrar el panel abierto", action: "close" }
  ];

  var shortcutsReturnFocus = null;

  function shortcutsDialog() {
    return document.getElementById("eva-shortcuts");
  }

  function mountShortcuts() {
    if (shortcutsDialog()) return;
    var wrap = document.createElement("div");
    wrap.id = "eva-shortcuts";
    wrap.className = "eva-shortcuts";
    wrap.hidden = true;
    wrap.innerHTML =
      '<div class="eva-shortcuts-backdrop" data-shortcuts-dismiss="1"></div>' +
      '<div class="eva-shortcuts-dialog" role="dialog" aria-modal="true" aria-labelledby="eva-shortcuts-title">' +
        '<div class="eva-shortcuts-head">' +
          '<h2 class="eva-shortcuts-title" id="eva-shortcuts-title">Atajos de teclado</h2>' +
          '<button type="button" class="eva-shortcuts-close" data-shortcuts-dismiss="1" aria-label="Cerrar">' + ICONS.close + '</button>' +
        '</div>' +
        '<dl class="eva-shortcuts-list">' +
          SHORTCUTS.map(function (s) {
            return '<div class="eva-shortcuts-row"><dt>' + s.label + '</dt><dd><kbd>' + s.keys + '</kbd></dd></div>';
          }).join("") +
        '</dl>' +
      '</div>';
    document.body.appendChild(wrap);
    wrap.addEventListener("click", function (ev) {
      var target = ev.target && ev.target.closest ? ev.target.closest("[data-shortcuts-dismiss]") : null;
      if (target) closeShortcuts();
    });
  }

  function openShortcuts() {
    mountShortcuts();
    var wrap = shortcutsDialog();
    if (!wrap) return;
    shortcutsReturnFocus = document.activeElement;
    wrap.hidden = false;
    /* Defensa: si el panel de Herramientas llegó a marcar aria-hidden en sus
       hermanos, la ayuda tiene que quedar visible para lectores de pantalla. */
    wrap.removeAttribute("aria-hidden");
    document.body.classList.add("eva-shortcuts-open");
    var cerrar = wrap.querySelector(".eva-shortcuts-close");
    if (cerrar) cerrar.focus();
  }

  function closeShortcuts() {
    var wrap = shortcutsDialog();
    if (!wrap || wrap.hidden) return;
    /* Se retira del DOM: así el diálogo modal del runtime nunca lo deja con
       aria-hidden ni con el foco atrapado cuando vuelve a abrirse. */
    wrap.remove();
    document.body.classList.remove("eva-shortcuts-open");
    var volver = shortcutsReturnFocus;
    shortcutsReturnFocus = null;
    if (volver && typeof volver.focus === "function") {
      try { volver.focus(); } catch (_e) {}
    }
  }

  function toggleShortcuts() {
    var wrap = shortcutsDialog();
    if (wrap && !wrap.hidden) closeShortcuts();
    else openShortcuts();
  }

  /* El panel de Herramientas es un diálogo modal del runtime: atrapa el foco y
     deja el resto del documento con aria-hidden. Por eso se cierra antes de
     mostrar la ayuda, y la ayuda se abre sola como diálogo. */
  function openShortcutsFromTools() {
    closeNativeDialog();
    setTimeout(openShortcuts, 250);
  }

  function runShortcut(action) {
    if (action === "help") { toggleShortcuts(); return; }
    var wrap = shortcutsDialog();
    if (wrap && !wrap.hidden) closeShortcuts();
    if (action === "index") {
      var indice = document.getElementById("reflow-index");
      if (indice) indice.click();
      return;
    }
    if (action === "tools") {
      var herramientas = document.getElementById("reflow-tools");
      if (herramientas) herramientas.click();
      return;
    }
    if (action === "glossary") {
      var glosario = document.getElementById("reflow-glossary");
      if (glosario) glosario.click();
    }
  }

  function isEditable(el) {
    if (!el || !el.tagName) return false;
    var tag = el.tagName;
    return tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || el.isContentEditable === true;
  }

  var SHORTCUT_ACTIONS = { KeyI: "index", KeyH: "tools", KeyG: "glossary", KeyA: "help" };

  function onShortcutKey(ev) {
    var wrap = shortcutsDialog();
    var abierta = Boolean(wrap) && !wrap.hidden;

    if (ev.key === "Escape" || ev.code === "Escape") {
      if (abierta) {
        ev.preventDefault();
        ev.stopPropagation();
        closeShortcuts();
      }
      /* Sin la ayuda abierta no se intercepta: el runtime ya cierra sus
         paneles con Escape. */
      return;
    }

    if (abierta && ev.key === "Tab") {
      /* La ayuda tiene un solo control: el foco no sale del diálogo. */
      ev.preventDefault();
      var cerrar = wrap.querySelector(".eva-shortcuts-close");
      if (cerrar) cerrar.focus();
      return;
    }

    if (!ev.altKey || ev.ctrlKey || ev.metaKey || ev.shiftKey || isEditable(ev.target)) return;
    var action = SHORTCUT_ACTIONS[ev.code];
    if (!action) return;
    ev.preventDefault();
    ev.stopPropagation();
    runShortcut(action);
  }

  document.addEventListener("keydown", onShortcutKey, true);

  /* ── Estado de las actividades en el índice ──────────────────────────────
     «Por hacer» / «Incompleta» / «Completa» debajo de cada actividad, como en
     el 1930. El progreso se guarda por sección en localStorage:

       · empieza en «Por hacer»;
       · pasa a «Incompleta» con la primera interacción dentro de la actividad;
       · pasa a «Completa» cuando el botón de validar del runtime deja de decir
         «Enviar» y pasa a «Siguiente»: es la señal que da el runtime cuando
         todas las validaciones devolvieron true. */
  var ACTIVITY_KEY = "evaActivityProgress";
  var EVALUAR = { pending: "Por hacer", started: "Incompleta", complete: "Completa" };
  var tocEntries = null;

  function activityProgress() {
    try {
      var raw = localStorage.getItem(ACTIVITY_KEY);
      var data = raw ? JSON.parse(raw) : null;
      return data && typeof data === "object" ? data : {};
    } catch (_e) { return {}; }
  }

  function saveActivityProgress(all) {
    try { localStorage.setItem(ACTIVITY_KEY, JSON.stringify(all)); } catch (_e) {}
  }

  function currentSectionId() {
    var meta = document.querySelector('meta[name="title-id"]');
    return meta ? meta.getAttribute("content") : null;
  }

  function isActivityPage() {
    return Boolean(document.querySelector('#content section[data-section-type^="activity"]'));
  }

  function markActivity(id, state) {
    if (!id) return;
    var all = activityProgress();
    if (all[id] === "complete") return;
    if (all[id] === state) return;
    all[id] = state;
    saveActivityProgress(all);
  }

  function loadToc() {
    if (!tocEntries) {
      tocEntries = fetch("./content/toc.json")
        .then(function (res) { return res.ok ? res.json() : []; })
        .catch(function () { return []; });
    }
    return tocEntries;
  }

  function decorateActivityEntry(btn, state) {
    var label = EVALUAR[state] || EVALUAR.pending;
    if (!btn.classList.contains("eva-toc-entry")) btn.classList.add("eva-toc-entry");
    if (state) btn.setAttribute("data-eva-activity-status", state);
    else btn.removeAttribute("data-eva-activity-status");
    var titulo = btn.querySelector(".eva-toc-title");
    if (!titulo) {
      titulo = document.createElement("span");
      titulo.className = "eva-toc-title";
      while (btn.firstChild) titulo.appendChild(btn.firstChild);
      btn.appendChild(titulo);
    }
    var status = btn.querySelector(".eva-toc-status");
    if (!status) {
      status = document.createElement("span");
      status.className = "eva-toc-status";
      btn.appendChild(status);
    }
    if (status.textContent !== label) status.textContent = label;
  }

  function refreshActivityStatus() {
    var buttons = document.querySelectorAll('[role="dialog"] button[title]');
    if (!buttons.length) return;
    loadToc().then(function (entries) {
      var actividades = entries.filter(function (entry) { return entry.activity; });
      if (!actividades.length) return;
      var progress = activityProgress();
      actividades.forEach(function (entry) {
        for (var i = 0; i < buttons.length; i += 1) {
          if (buttons[i].getAttribute("title") === entry.title) {
            decorateActivityEntry(buttons[i], progress[entry.section_id] || "");
            break;
          }
        }
      });
    });
  }

  function syncActivityCompletion() {
    if (!isActivityPage()) return;
    var boton = document.querySelector('#nav-container button[title="Siguiente"]');
    if (boton) markActivity(currentSectionId(), "complete");
  }

  function onActivityUse(ev) {
    if (!isActivityPage()) return;
    var target = ev.target;
    if (!target || typeof target.closest !== "function") return;
    if (!target.closest('#content section[data-section-type^="activity"]')) return;
    markActivity(currentSectionId(), "started");
  }

  document.addEventListener("click", onActivityUse, true);
  document.addEventListener("keydown", onActivityUse, true);

  var FONT_SIZES = [16, 17.5, 19, 20.5];
  var FONT_LABELS = ["Normal", "Grande", "Extra grande", "Máximo"];
  var FONT_KEYS = ["normal", "large", "xlarge", "xxlarge"];

  function applyFontSize(step) {
    step = Math.max(0, Math.min(FONT_SIZES.length - 1, Number(step) || 0));
    document.documentElement.style.fontSize = FONT_SIZES[step] + "px";
    try { localStorage.setItem("evaFontSize", String(step)); } catch (_e) {}
  }

  function storedFontSize() {
    try { return Number(localStorage.getItem("evaFontSize") || 0); } catch (_e) { return 0; }
  }

  function switchRow(key, label, description, ttsOnly) {
    return '<div class="reflow-setting-row" data-row="' + key + '"' + (ttsOnly ? ' data-tts-only="1"' : "") + '>' +
      '<span class="reflow-setting-label">' + label +
        (description ? '<span class="reflow-setting-description">' + description + '</span>' : "") +
      '</span>' +
      '<button type="button" role="switch" aria-checked="false" aria-label="' + esc(label) + '" data-switch="' + key + '">' +
        '<span class="reflow-custom-switch-thumb" aria-hidden="true"></span></button></div>';
  }

  function segmented(key, label, options, ttsOnly) {
    return '<div class="reflow-setting-row" data-row="' + key + '"' + (ttsOnly ? ' data-tts-only="1"' : "") + '>' +
      '<span class="reflow-setting-label">' + label + '</span>' +
      '<div class="reflow-tts-' + key + '-options" role="radiogroup" aria-label="' + esc(label) + '">' +
      options.map(function (o) {
        return '<button type="button" role="radio" data-' + key + '="' + o.value + '" aria-checked="false">' + o.label + '</button>';
      }).join("") + '</div></div>';
  }

  function fontRow() {
    return '<div class="reflow-setting-row" data-row="fontSize">' +
      '<span class="reflow-setting-label">Tamaño de letra</span>' +
      '<div class="reflow-font-settings-options" role="radiogroup" aria-label="Tamaño de letra">' +
      FONT_SIZES.map(function (_px, i) {
        return '<button type="button" role="radio" data-font-size="' + i + '" data-reflow-font-size="' + FONT_KEYS[i] + '" aria-checked="false" aria-pressed="false" aria-label="' + FONT_LABELS[i] + '">' +
          '<span class="reflow-font-size-glyph" aria-hidden="true">A</span></button>';
      }).join("") + '</div></div>';
  }

  function renderTools(dlg) {
    var shell = dlg.querySelector(":scope > div");
    if (!shell) return;
    if (dlg.getAttribute("data-eva-tools") === "1") return;
    dlg.setAttribute("data-eva-tools", "1");
    dlg.classList.add("reflow-reader-panel", "reflow-reader-panel-tall", "reflow-accessibility-panel");
    shell.classList.add("eva-tools-shell");
    shell.innerHTML =
      '<div class="reflow-panel-control-header">' +
        '<h2 class="reflow-panel-control-title">Herramientas</h2>' +
        '<button class="reflow-panel-close" type="button" aria-label="Cerrar">' + ICONS.close + '</button>' +
      '</div>' +
      '<div class="reflow-settings-list reflow-settings-organized">' +
        '<p class="reflow-settings-block-title">Leer</p>' +
        fontRow() +
        switchRow("easyRead", "Lectura fácil", "") +
        switchRow("describeImages", "Descripción de imágenes", "") +
        '<p class="reflow-settings-block-title">Escuchar</p>' +
        switchRow("readAloud", "Activar lectura en voz alta", "Habilitá el modo. Usá Reproducir para comenzar.") +
        switchRow("autoplay", "Reproducción automática", "", true) +
        segmented("voice", "Voz del narrador", VOICES.map(function (v) { return { value: v.key, label: v.label }; }), true) +
        segmented("speed", "Velocidad", SPEEDS.map(function (s) { return { value: s.value, label: s.label }; }), true) +
        segmented("highlight", "Resaltado", [{ value: "word", label: "Palabra" }, { value: "sentence", label: "Oración" }], true) +
        '<p class="reflow-settings-block-title">Pantalla</p>' +
        switchRow("reduceMotion", "Reducir movimiento", "Sigue la configuración del sistema: movimiento reducido desactivado.") +
        switchRow("hideMenus", "Ocultar menús automáticamente", "") +
        '<button type="button" class="reflow-shortcuts-link" data-shortcuts-open="1" aria-haspopup="dialog">' +
          '<span>Atajos de teclado</span><kbd>Alt+A</kbd></button>' +
      '</div>';

    shell.querySelector(".reflow-panel-close").addEventListener("click", closeNativeDialog);
    shell.querySelectorAll("[data-switch]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var key = btn.getAttribute("data-switch");
        var st = state();
        if (!st) return;
        kit().set(key, !st[key]);
        syncTools(shell);
      });
    });
    shell.querySelectorAll("[data-voice]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        kit().set("voice", btn.getAttribute("data-voice"));
        syncTools(shell);
      });
    });
    shell.querySelectorAll("[data-speed]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        kit().set("speed", parseFloat(btn.getAttribute("data-speed")));
        syncTools(shell);
      });
    });
    shell.querySelectorAll("[data-highlight]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        kit().set("highlight", btn.getAttribute("data-highlight") === "word");
        syncTools(shell);
      });
    });
    shell.querySelectorAll("[data-font-size]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        applyFontSize(btn.getAttribute("data-font-size"));
        syncTools(shell);
      });
    });
    var atajos = shell.querySelector("[data-shortcuts-open]");
    if (atajos) atajos.addEventListener("click", openShortcutsFromTools);
    syncTools(shell);
  }

  function syncTools(shell) {
    var st = state();
    if (!st || !shell) return;
    shell.querySelectorAll("[data-switch]").forEach(function (btn) {
      var key = btn.getAttribute("data-switch");
      btn.setAttribute("aria-checked", String(Boolean(st[key])));
    });
    shell.querySelectorAll("[data-voice]").forEach(function (btn) {
      btn.setAttribute("aria-checked", String(st.voice === btn.getAttribute("data-voice")));
    });
    shell.querySelectorAll("[data-speed]").forEach(function (btn) {
      btn.setAttribute("aria-checked", String(Number(st.speed) === Number(btn.getAttribute("data-speed"))));
    });
    shell.querySelectorAll("[data-highlight]").forEach(function (btn) {
      btn.setAttribute("aria-checked", String(Boolean(st.highlight) === (btn.getAttribute("data-highlight") === "word")));
    });
    var step = storedFontSize();
    shell.querySelectorAll("[data-font-size]").forEach(function (btn) {
      var on = String(step) === btn.getAttribute("data-font-size");
      btn.setAttribute("aria-checked", String(on));
      btn.setAttribute("aria-pressed", String(on));
    });
    shell.querySelectorAll("[data-tts-only]").forEach(function (row) {
      row.classList.toggle("reflow-setting-tts-hidden", !st.readAloud);
    });
  }

  /* ── Reproductor ───────────────────────────────────────────────────────── */
  function mountPlayer() {
    if (document.getElementById("reflow-tts-player")) return;
    var s = document.createElement("section");
    s.id = "reflow-tts-player";
    s.setAttribute("role", "region");
    s.setAttribute("aria-label", "Controles de lectura en voz alta");
    s.hidden = true;
    s.innerHTML =
      '<div class="reflow-tts-player-main" id="reflow-tts-player-main">' +
        '<button id="reflow-tts-previous" type="button" aria-label="Audio anterior">' + ICONS.prev + '<span class="reflow-tts-player-label">Anterior</span></button>' +
        '<button id="reflow-tts-toggle" type="button" aria-label="Reproducir" aria-pressed="false">' +
          '<span class="reflow-tts-player-icon" data-icon="play">' + ICONS.play + '</span><span class="reflow-tts-player-label">Reproducir</span></button>' +
        '<button id="reflow-tts-next" type="button" aria-label="Audio siguiente">' + ICONS.next + '<span class="reflow-tts-player-label">Siguiente</span></button>' +
        '<button id="reflow-tts-options" type="button" aria-label="Opciones de voz y velocidad" aria-expanded="false" aria-controls="reflow-tts-options-panel">' +
          ICONS.gear + '<span class="reflow-tts-player-label">Opciones</span></button>' +
        '<button id="reflow-tts-minimize" type="button" aria-label="Minimizar reproductor" aria-expanded="false">' +
          ICONS.chevron + '<span class="reflow-tts-player-label">Minimizar</span></button>' +
        '<button id="reflow-tts-stop" type="button" aria-label="Cerrar lectura en voz alta">' + ICONS.close + '<span class="reflow-tts-player-label">Cerrar</span></button>' +
      '</div>' +
      '<div class="reflow-tts-player-options" id="reflow-tts-options-panel" role="group" aria-label="Voz y velocidad" hidden>' +
        '<span class="reflow-tts-player-options-title" id="reflow-tts-player-voice-label">Voz del narrador</span>' +
        '<div class="reflow-tts-voice-options" role="radiogroup" aria-labelledby="reflow-tts-player-voice-label">' +
          VOICES.map(function (v) { return '<button type="button" role="radio" data-voice="' + v.key + '" aria-checked="false">' + v.label + '</button>'; }).join("") + '</div>' +
        '<span class="reflow-tts-player-options-title" id="reflow-tts-player-speed-label">Velocidad</span>' +
        '<div class="reflow-tts-speed-options" role="radiogroup" aria-labelledby="reflow-tts-player-speed-label">' +
          SPEEDS.map(function (s) { return '<button type="button" role="radio" data-speed="' + s.value + '" aria-checked="false">' + s.label + '</button>'; }).join("") + '</div>' +
        '<span class="reflow-tts-player-options-title" id="reflow-tts-player-highlight-label">Resaltado</span>' +
        '<div class="reflow-tts-highlight-options" role="radiogroup" aria-labelledby="reflow-tts-player-highlight-label">' +
          '<button type="button" role="radio" data-highlight="word" aria-checked="true">Palabra</button>' +
          '<button type="button" role="radio" data-highlight="sentence" aria-checked="false">Oración</button></div>' +
      '</div>' +
      '<button id="reflow-tts-fab" class="reflow-tts-fab" type="button" aria-label="Mostrar controles de lectura" aria-expanded="true">' + ICONS.fab + '</button>';
    document.body.appendChild(s);

    s.querySelector("#reflow-tts-previous").addEventListener("click", function () { clickRuntime(["previous-audio"]); });
    s.querySelector("#reflow-tts-next").addEventListener("click", function () { clickRuntime(["next-audio"]); });
    s.querySelector("#reflow-tts-toggle").addEventListener("click", function () {
      /* Se usa el reproductor real del runtime, no un clic por etiqueta: asi el
         boton no se puede desincronizar ni clickear a si mismo. */
      var k = kit();
      if (k && k.togglePlay && k.hasItems && k.hasItems()) { k.togglePlay(); return; }
      if (!clickRuntime(["Pausa"])) clickRuntime(["Reproducir"]);
    });
    s.querySelector("#reflow-tts-stop").addEventListener("click", function () {
      /* Cerrar la lectura detiene el audio pero conserva el texto y el punto de
         escucha: al reactivar el modo, Reproducir continua donde iba. */
      var k = kit();
      if (!(k && k.stopKeep && k.stopKeep())) clickRuntime(["Detener"]);
      if (k) k.set("readAloud", false);
    });
    s.querySelector("#reflow-tts-options").addEventListener("click", function () {
      var panel = s.querySelector("#reflow-tts-options-panel");
      panel.hidden = !panel.hidden;
      s.querySelector("#reflow-tts-options").setAttribute("aria-expanded", String(!panel.hidden));
    });
    s.querySelector("#reflow-tts-minimize").addEventListener("click", function () {
      var min = !s.classList.contains("reflow-tts-player-minimized");
      s.classList.toggle("reflow-tts-player-minimized", min);
      s.querySelector("#reflow-tts-minimize").setAttribute("aria-expanded", String(min));
    });
    s.querySelector("#reflow-tts-fab").addEventListener("click", function () {
      s.classList.remove("reflow-tts-player-minimized");
      s.querySelector("#reflow-tts-minimize").setAttribute("aria-expanded", "false");
    });
    s.querySelectorAll("[data-voice]").forEach(function (b) {
      b.addEventListener("click", function () { kit().set("voice", b.getAttribute("data-voice")); syncPlayer(); });
    });
    s.querySelectorAll("[data-speed]").forEach(function (b) {
      b.addEventListener("click", function () { kit().set("speed", parseFloat(b.getAttribute("data-speed"))); syncPlayer(); });
    });
    s.querySelectorAll("[data-highlight]").forEach(function (b) {
      b.addEventListener("click", function () { kit().set("highlight", b.getAttribute("data-highlight") === "word"); syncPlayer(); });
    });
  }

  function syncPlayer() {
    var s = document.getElementById("reflow-tts-player");
    var st = state();
    if (!s || !st) return;
    s.hidden = !st.readAloud;
    if (!st.readAloud) {
      /* Al cerrar, el boton queda listo para la proxima sesion: no debe seguir
         mostrando "Pausa" mientras el reproductor esta oculto. */
      var offToggle = s.querySelector("#reflow-tts-toggle");
      if (offToggle) {
        offToggle.setAttribute("aria-pressed", "false");
        offToggle.setAttribute("aria-label", "Reproducir");
        offToggle.querySelector(".reflow-tts-player-label").textContent = "Reproducir";
        offToggle.querySelector(".reflow-tts-player-icon").innerHTML = ICONS.play;
      }
      s.classList.remove("reflow-tts-player-minimized");
      return;
    }
    var toggle = s.querySelector("#reflow-tts-toggle");
    var k = kit();
    var playing = k && k.playingReal ? k.playingReal() : Boolean(st.playing);
    toggle.setAttribute("aria-pressed", String(playing));
    toggle.setAttribute("aria-label", playing ? "Pausa" : "Reproducir");
    toggle.querySelector(".reflow-tts-player-label").textContent = playing ? "Pausa" : "Reproducir";
    toggle.querySelector(".reflow-tts-player-icon").innerHTML = playing ? ICONS.pause : ICONS.play;
    /* Sin textos con audio el boton no tiene nada que hacer: se deshabilita en
       lugar de fallar en silencio. */
    toggle.disabled = k && k.hasItems ? !k.hasItems() : false;
    s.querySelector("#reflow-tts-previous").disabled = isDisabled("previous-audio");
    s.querySelector("#reflow-tts-next").disabled = isDisabled("next-audio");
    s.querySelectorAll("[data-voice]").forEach(function (b) {
      b.setAttribute("aria-checked", String(st.voice === b.getAttribute("data-voice")));
    });
    s.querySelectorAll("[data-speed]").forEach(function (b) {
      b.setAttribute("aria-checked", String(Number(st.speed) === Number(b.getAttribute("data-speed"))));
    });
    s.querySelectorAll("[data-highlight]").forEach(function (b) {
      b.setAttribute("aria-checked", String(Boolean(st.highlight) === (b.getAttribute("data-highlight") === "word")));
    });
  }

  /* ── Barra: estado de página ─────────────────────────────────────────────
     El total sale de content/pages.json. Antes se deducía del texto del dock
     nativo («5 /12» seguido del número de la actividad) y ese número se pegaba
     al total: daba 121, 122… */
  var totalPaginas = null;

  function loadTotalPages() {
    if (totalPaginas !== null) return;
    totalPaginas = 0;
    fetch("./content/pages.json")
      .then(function (res) { return res.ok ? res.json() : []; })
      .then(function (lista) {
        totalPaginas = Array.isArray(lista) ? lista.length : 0;
        syncToolbar();
      })
      .catch(function () {});
  }

  function totalPages() {
    return totalPaginas && totalPaginas > 0 ? totalPaginas : null;
  }

  function syncToolbar() {
    var meta = document.querySelector('meta[name="page-section-id"]');
    var actual = meta ? Number(meta.getAttribute("content")) : NaN;
    var total = totalPages();
    var status = document.getElementById("reflow-page-status");
    if (status && Number.isFinite(actual)) {
      var largo = document.getElementById("reflow-progress-long");
      var corto = document.getElementById("reflow-progress-short");
      var mini = document.getElementById("reflow-progress-minimal");
      var tl = "pág. " + actual + (total ? " de " + total : "");
      var tc = actual + (total ? "/" + total : "");
      if (largo && largo.textContent !== tl) largo.textContent = tl;
      if (corto && corto.textContent !== tc) corto.textContent = tc;
      if (mini && mini.textContent !== tc) mini.textContent = tc;
      status.setAttribute("aria-label", "Página " + actual + (total ? " de " + total : ""));
      var prev = document.getElementById("reflow-previous");
      var next = document.getElementById("reflow-next");
      if (prev) prev.disabled = actual <= 1;
      if (next && total) next.disabled = actual >= total;
    }
  }

  /* ── Arranque ──────────────────────────────────────────────────────────── */
  var pendiente = false;

  function tick() {
    document.body.classList.add("reflow-book");
    ensureStyles();
    if (!window.__evaFontApplied) { window.__evaFontApplied = true; applyFontSize(storedFontSize()); }
    mountToolbar();
    mountPlayer();
    loadTotalPages();
    var dlg = findSettingsDialog();
    if (dlg) renderTools(dlg);
    syncToolbar();
    syncPlayer();
    syncActivityCompletion();
    refreshActivityStatus();
    var shell = document.querySelector(".eva-tools-shell");
    if (shell) syncTools(shell);
  }

  function programar() {
    if (pendiente) return;
    pendiente = true;
    requestAnimationFrame(function () {
      pendiente = false;
      tick();
    });
  }

  new MutationObserver(programar).observe(document.body, {
    childList: true, subtree: true, characterData: true
  });
  setInterval(tick, 400);
  programar();
})();
