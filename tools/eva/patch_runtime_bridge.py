# -*- coding: utf-8 -*-
"""Expone un puente minimo del runtime ADT para que la interfaz del kit pueda
leer y cambiar ajustes sin depender del DOM interno.

Anade `window.__adtKit` con:
  get()        -> {easyRead, readAloud, autoplay, describeImages, highlight,
                    voice, speed, hideMenus, playing}
  set(k, v)    -> cambia el ajuste correspondiente (mismo store que usa el runtime)
  click(label) -> dispara un boton del runtime por su nombre accesible
  disabled(label) -> si ese boton esta deshabilitado

Idempotente. Uso: python tools/eva/patch_runtime_bridge.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "assets" / "base.bundle.local.js"
ANCHOR = "function adtVoiceDropdown(){"

SNIPPET = (
    'window.__adtKit={'
    'get(){let g=k=>xe().get(k);return{'
    'easyRead:g(dr),readAloud:g(ei),autoplay:g(Qy),describeImages:g(ex),'
    'highlight:g(Jy),voice:g(Fy),speed:g(tx),hideMenus:g(ub),reduceMotion:g(Ya),playing:g(YN)}},'
    'set(k,v){let m={easyRead:dr,readAloud:ei,autoplay:Qy,describeImages:ex,'
    'highlight:Jy,voice:Fy,speed:tx,hideMenus:ub,reduceMotion:Ya};if(m[k])xe().set(m[k],v)},'
    'click(label){let b=document.querySelector(\'#interface-container button[aria-label="\'+label+\'"]\')'
    '||document.querySelector(\'button[aria-label="\'+label+\'"]\');if(!b)return false;b.click();return !b.disabled},'
    'disabled(label){let b=document.querySelector(\'button[aria-label="\'+label+\'"]\');return !b||b.disabled}};'
)


def main():
    src = BUNDLE.read_bytes().decode("utf-8")
    if "__adtKit" in src:
        print("puente ya aplicado")
        return
    if src.count(ANCHOR) != 1:
        raise SystemExit(f"ancla inesperada: {src.count(ANCHOR)}")
    out = src.replace(ANCHOR, SNIPPET + "\n" + ANCHOR, 1)
    BUNDLE.write_bytes(out.encode("utf-8"))
    print("puente aplicado:", len(out.encode('utf-8')), "bytes")


if __name__ == "__main__":
    main()
