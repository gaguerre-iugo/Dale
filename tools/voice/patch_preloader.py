# -*- coding: utf-8 -*-
"""Incrusta audio_voices.json en offline-preloader.js para que el selector de
voces funcione tambien al abrir el libro con file://.

El preloader es generado: no se reescribe el objeto INLINE, se agrega (o
actualiza) una linea idempotente que lo amplia antes de instalar el shim de
fetch.

Uso: python tools/voice/patch_preloader.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRE = ROOT / "assets" / "offline-preloader.js"
CATALOG = ROOT / "content" / "i18n" / "es-UY" / "audio_voices.json"
KEY = "./content/i18n/es-UY/audio_voices.json"
MARK = "/* voice-ui: audio_voices.json */"


def main():
    src = PRE.read_text(encoding="utf-8")
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    block = (f"  {MARK}\n"
             f"  INLINE[{json.dumps(KEY)}] = {payload};\n")

    if MARK in src:
        pattern = re.compile(
            r"  /\* voice-ui: audio_voices\.json \*/\n"
            r"  INLINE\[[^\]]+\] = .*?;\n", re.S)
        if not pattern.search(src):
            raise SystemExit("linea del preloader no encontrada")
        out = pattern.sub(block, src, count=1)
    else:
        anchor = "  var _realFetch = window.fetch.bind(window);"
        if src.count(anchor) != 1:
            raise SystemExit("ancla del preloader no encontrada")
        out = src.replace(anchor, block + anchor, 1)

    if out == src:
        print("preloader ya actualizado: nada que hacer")
        return
    PRE.write_bytes(out.encode("utf-8"))
    print("preloader actualizado:", len(src), "->", len(out), "bytes")


if __name__ == "__main__":
    main()
