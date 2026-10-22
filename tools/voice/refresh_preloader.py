# -*- coding: utf-8 -*-
"""Sincroniza el objeto INLINE de offline-preloader.js con los archivos del libro.

El preloader es generado. Cuando se edita una pagina o un JSON que ya esta
incrustado, hay que volver a leerlo; si no, la version file:// sirve contenido
viejo. Este script actualiza cada clave existente desde su archivo, elimina las
claves cuyo archivo ya no existe y deja el resto del preloader intacto.

Uso: python tools/voice/refresh_preloader.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRE = ROOT / "assets" / "offline-preloader.js"
START = "var INLINE = "
END = ";\n  var BASE_DIR"


def local_path(key):
    clean = key[2:] if key.startswith("./") else key
    return ROOT / clean


def same(old, new):
    if isinstance(old, str) and isinstance(new, str):
        return old.replace("\r\n", "\n") == new.replace("\r\n", "\n")
    return old == new


def main():
    src = PRE.read_text(encoding="utf-8")
    if src.count(START) != 1 or src.count(END) != 1:
        raise SystemExit("no se encontro el objeto INLINE")
    begin = src.index(START) + len(START)
    end = src.index(END, begin)
    data = json.loads(src[begin:end])

    changed = []
    for key in list(data):
        path = local_path(key)
        if not path.is_file():
            del data[key]
            changed.append(key + " (archivo eliminado)")
            continue
        if path.suffix.lower() == ".json":
            value = json.loads(path.read_text(encoding="utf-8"))
        else:
            value = path.read_text(encoding="utf-8")
        if data[key] != value:
            if same(data[key], value):
                continue
            data[key] = value
            changed.append(key)

    new = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    out = src[:begin] + new + src[end:]
    if out == src:
        print("preloader ya sincronizado: nada que hacer")
        return
    PRE.write_bytes(out.encode("utf-8"))
    print(f"preloader sincronizado: {len(changed)} claves")
    for key in changed:
        print("  ", key)


if __name__ == "__main__":
    main()
