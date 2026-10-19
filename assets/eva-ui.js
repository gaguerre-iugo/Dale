/* ============================================================================
   Interfaz EVA del libro — puente con el runtime ADT.
   ----------------------------------------------------------------------------
   No modifica el runtime ni el contenido: monta la barra y el reproductor del
   kit (#reflow-pagination / #reflow-tts-player), oculta el dock nativo y
   reenvía cada acción a los botones del runtime por su nombre accesible.

   Se carga con `defer` en cada página; espera a que el runtime monte el dock.
   ========================================================================== */
(function () {
  "use strict";

  /* ── Correcciones de texto del panel (literales en inglés del runtime) ── */
  var TRADUCCIONES = {
    "Reading": "Lectura",
    "Behavior": "Comportamiento"
  };

  function traducirTitulos() {
    document.querySelectorAll("[role='dialog'] h3").forEach(function (titulo) {
      var texto = (titulo.textContent || "").trim();
      if (TRADUCCIONES[texto]) titulo.textContent = TRADUCCIONES[texto];
    });
  }

  /* Un solo idioma: la fila «Abrir idioma» de los atajos no aplica. */
  function quitarAtajoIdioma() {
    document.querySelectorAll("[role='dialog'] span").forEach(function (span) {
      if ((span.textContent || "").trim() !== "Abrir idioma") return;
      var fila = span.parentElement;
      if (!fila || !fila.querySelector("kbd")) return;
      if ((fila.textContent || "").replace(/\s+/g, "") === "AbriridiomaL") fila.remove();
    });
  }

  /* ── Acceso a los controles del runtime ─────────────────────────────────── */
  function botonRuntime(etiqueta) {
    return document.querySelector(
      "#nav-container button[aria-label=\"" + etiqueta + "\"], " +
      "#interface-container button[aria-label=\"" + etiqueta + "\"]"
    );
  }

  function accion(etiquetas) {
    for (var i = 0; i < etiquetas.length; i += 1) {
      var b = botonRuntime(etiquetas[i]);
      if (b && !b.disabled) { b.click(); return true; }
    }
    return false;
  }

  function estadoPagina() {
    var grupo = document.querySelector("#nav-container [role='group']");
    /* textContent y no innerText: el dock está oculto con `visibility: hidden`
       y `innerText` devuelve vacío en ese caso. */
    var m = grupo && (grupo.textContent || "").match(/(\d+)\s*\/\s*(\d+)/);
    return m ? { actual: +m[1], total: +m[2] } : null;
  }

  function lecturaActiva() {
    return Boolean(
      botonRuntime("Desactivar texto a voz") ||
      botonRuntime("Desactivar lectura en voz alta")
    );
  }

  /* ── Barra de navegación del kit ───────────────────────────────────────── */
  function montarBarra() {
    if (document.getElementById("reflow-pagination")) return;
    var barra = document.createElement("nav");
    barra.id = "reflow-pagination";
    barra.setAttribute("role", "navigation");
    barra.setAttribute("aria-label", "Controles de lectura");
    barra.innerHTML =
      '<button id="reflow-index" class="reflow-toolbar-action" type="button" ' +
        'aria-label="Índice" aria-haspopup="dialog" aria-expanded="false">' +
        '<span class="reflow-toolbar-icon" data-eva-icon="menu" aria-hidden="true"></span>' +
        '<span class="reflow-toolbar-label">Índice</span>' +
      '</button>' +
      '<button id="reflow-previous" class="reflow-toolbar-action reflow-toolbar-primary" type="button" ' +
        'aria-label="Página anterior">' +
        '<span class="reflow-toolbar-icon" data-eva-icon="left" aria-hidden="true"></span>' +
        '<span class="reflow-toolbar-label">Anterior</span>' +
      '</button>' +
      '<output id="reflow-page-status" aria-live="off" aria-label="Página">' +
        '<span id="reflow-progress-long">pág. 1 de 1</span>' +
        '<span id="reflow-progress-short">1/1</span>' +
        '<span id="reflow-progress-minimal">1/1</span>' +
      '</output>' +
      '<button id="reflow-next" class="reflow-toolbar-action reflow-toolbar-primary" type="button" ' +
        'aria-label="Página siguiente">' +
        '<span class="reflow-toolbar-icon" data-eva-icon="right" aria-hidden="true"></span>' +
        '<span class="reflow-toolbar-label">Siguiente</span>' +
      '</button>' +
      '<button id="reflow-glossary" class="reflow-toolbar-action" type="button" ' +
        'aria-label="Glosario" aria-haspopup="dialog" aria-expanded="false">' +
        '<span class="reflow-toolbar-icon" data-eva-icon="glossary" aria-hidden="true"></span>' +
        '<span class="reflow-toolbar-label">Glosario</span>' +
      '</button>' +
      '<button id="reflow-tools" class="reflow-toolbar-action" type="button" ' +
        'aria-label="Herramientas" aria-haspopup="dialog" aria-expanded="false">' +
        '<span class="reflow-toolbar-icon" data-eva-icon="gear" aria-hidden="true"></span>' +
        '<span class="reflow-toolbar-label">Herramientas</span>' +
      '</button>';
    document.body.appendChild(barra);

    barra.querySelector("#reflow-index").addEventListener("click", function () {
      accion(["Menú principal", "Main Menu"]);
    });
    barra.querySelector("#reflow-previous").addEventListener("click", function () {
      accion(["Página anterior", "Previous page"]);
    });
    barra.querySelector("#reflow-next").addEventListener("click", function () {
      accion(["Página siguiente", "Next page"]);
    });
    barra.querySelector("#reflow-glossary").addEventListener("click", function () {
      accion(["Glosario", "Glossary"]);
    });
    barra.querySelector("#reflow-tools").addEventListener("click", function () {
      accion(["Configuración", "Settings"]);
    });
  }

  /* ── Reproductor del kit ────────────────────────────────────────────────── */
  function montarReproductor() {
    if (document.getElementById("reflow-tts-player")) return;
    var reproductor = document.createElement("section");
    reproductor.id = "reflow-tts-player";
    reproductor.setAttribute("role", "region");
    reproductor.setAttribute("aria-label", "Controles de lectura en voz alta");
    reproductor.hidden = true;
    reproductor.innerHTML =
      '<div class="reflow-tts-player-main" id="reflow-tts-player-main">' +
        '<button id="reflow-tts-toggle" type="button" aria-label="Reproducir" aria-pressed="false">' +
          '<span class="reflow-tts-player-icon" data-eva-icon="play" aria-hidden="true"></span>' +
          '<span class="reflow-tts-player-label">Reproducir</span>' +
        '</button>' +
        '<button id="reflow-tts-options" type="button" aria-label="Opciones de voz y velocidad">' +
          '<span class="reflow-tts-player-icon" data-eva-icon="gear" aria-hidden="true"></span>' +
          '<span class="reflow-tts-player-label">Opciones</span>' +
        '</button>' +
      '</div>';
    document.body.appendChild(reproductor);

    reproductor.querySelector("#reflow-tts-toggle").addEventListener("click", function () {
      if (lecturaActiva()) accion(["Desactivar texto a voz", "Desactivar lectura en voz alta"]);
      else accion(["Activar texto a voz", "Activar lectura en voz alta"]);
    });
    reproductor.querySelector("#reflow-tts-options").addEventListener("click", function () {
      accion(["Configuración", "Settings"]);
    });
  }

  /* ── Sincronización con el estado del runtime ──────────────────────────── */
  function sincronizar() {
    var datos = estadoPagina();
    var status = document.getElementById("reflow-page-status");
    if (datos && status) {
      var largo = document.getElementById("reflow-progress-long");
      var corto = document.getElementById("reflow-progress-short");
      var mini = document.getElementById("reflow-progress-minimal");
      var textoLargo = "pág. " + datos.actual + " de " + datos.total;
      var textoCorto = datos.actual + "/" + datos.total;
      if (largo && largo.textContent !== textoLargo) largo.textContent = textoLargo;
      if (corto && corto.textContent !== textoCorto) corto.textContent = textoCorto;
      if (mini && mini.textContent !== textoCorto) mini.textContent = textoCorto;
      status.setAttribute("aria-label", "Página " + datos.actual + " de " + datos.total);
      var prev = document.getElementById("reflow-previous");
      var next = document.getElementById("reflow-next");
      if (prev) prev.disabled = datos.actual <= 1;
      if (next) next.disabled = datos.actual >= datos.total;
    }

    var activa = lecturaActiva();
    var reproductor = document.getElementById("reflow-tts-player");
    var alternar = document.getElementById("reflow-tts-toggle");
    if (reproductor && alternar) {
      reproductor.hidden = !activa;
      var etiqueta = activa ? "Detener" : "Reproducir";
      var icono = activa ? "stop" : "play";
      if (alternar.getAttribute("aria-label") !== etiqueta) {
        alternar.setAttribute("aria-label", etiqueta);
        alternar.setAttribute("aria-pressed", String(activa));
        var texto = alternar.querySelector(".reflow-tts-player-label");
        if (texto) texto.textContent = etiqueta;
        var spanIcono = alternar.querySelector(".reflow-tts-player-icon");
        if (spanIcono) spanIcono.setAttribute("data-eva-icon", icono);
      }
    }
  }

  /* ── Arranque ──────────────────────────────────────────────────────────── */
  function arreglar() {
    traducirTitulos();
    quitarAtajoIdioma();
  }

  var pendiente = false;
  function programar() {
    if (pendiente) return;
    pendiente = true;
    requestAnimationFrame(function () {
      pendiente = false;
      arreglar();
      if (!document.querySelector("#nav-container [role='group']")) return;
      document.body.classList.add("reflow-book");
      montarBarra();
      /* El reproductor propio no se monta: el runtime ya trae uno con transporte
         completo (anterior / pausa / siguiente / detener / velocidad) y
         eva.css lo viste con la estética EVA. */
      sincronizar();
    });
  }

  new MutationObserver(programar).observe(document.body, {
    childList: true,
    subtree: true,
    characterData: true
  });
  programar();
})();
