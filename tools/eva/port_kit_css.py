# -*- coding: utf-8 -*-
"""Porta componentes del eva-kit al CSS del libro, corrigiendo las rutas
relativas (el kit vive en components/, el libro carga assets/eva.css, asi que
url("../icons/...") tiene que pasar a url("./icons/...")).

Uso: python tools/eva/port_kit_css.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KIT = Path(r"C:\Users\germa\Desktop\eva-kit")
EVA = ROOT / "assets" / "eva.css"
BEGIN = "/* === eva-kit:panels (portado) === */"
END = "/* === /eva-kit:panels === */"

COMPONENTS = ["components/eva-panels.css"]


def fix_urls(css: str) -> str:
    return (css.replace('url("../icons/', 'url("./icons/')
               .replace("url('../icons/", "url('./icons/")
               .replace('url("../fonts/', 'url("./fonts/')
               .replace("url('../fonts/", "url('./fonts/"))


def main():
    css = "\n".join((KIT / c).read_text(encoding="utf-8") for c in COMPONENTS)
    css = fix_urls(css)
    block = f"{BEGIN}\n{css}\n{END}\n"
    src = EVA.read_text(encoding="utf-8")
    if BEGIN in src and END in src:
        pre = src.split(BEGIN)[0]
        post = src.split(END, 1)[1]
        src = pre + block + post
    else:
        src = src.rstrip() + "\n\n" + block
    EVA.write_bytes(src.encode("utf-8"))
    print("eva.css ->", len(src.encode("utf-8")), "bytes")


if __name__ == "__main__":
    main()
