# -*- coding: utf-8 -*-
"""Agrega el selector de voz al dock de reproduccion del runtime ADT.

El bundle ya soporta dos narradores (audio_voices.json + el select de
Configuracion), pero la barra flotante de lectura solo muestra velocidad y
volumen. Este parche inserta un desplegable de voz con los mismos componentes
del runtime (DropdownMenu + RadioGroup), sin recompilar nada.

Idempotente: si el parche ya esta aplicado, no hace nada.
Guarda una copia del original en tools/voice/base.bundle.local.js.orig
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "assets" / "base.bundle.local.js"
BACKUP = Path(__file__).resolve().parent / "base.bundle.local.js.orig"

ANCHOR = "function Tz(){"
TAIL = "(0,Fn.jsx)(rz,{}),(0,Fn.jsx)(wz,{})]})}"

COMPONENT = r'''function adtVoiceDropdown(){let[e,t]=We(Fy),{t:o}=je(),n=le(_d),c=["primary","secondary"].every(u=>Object.keys(n?.voices?.[u]?.audios??{}).length>0),a=n?.voices?.[e]?.label||"Narrator";return c?(0,Fn.jsxs)(ez,{modal:!1,children:[(0,Fn.jsxs)(tz,{className:be("min-w-30 h-10 px-3 rounded-lg","flex items-center gap-1","text-xs font-medium text-foreground","hover:bg-accent hover:text-accent-foreground","transition-colors duration-150","focus:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1","data-[state=open]:bg-accent data-[state=open]:text-accent-foreground"),"aria-label":`${o("narrator-voice-label")||"Narrator voice"}: ${a}`,children:[(0,Fn.jsx)("span",{className:"flex-1 text-start",children:a}),(0,Fn.jsx)(Sp,{className:"size-4 opacity-60","aria-hidden":"true"})]}),(0,Fn.jsx)(oz,{align:"end",sideOffset:8,positionMethod:"fixed",className:"min-w-[8rem]",children:(0,Fn.jsx)(nz,{value:e,onValueChange:u=>t(u),children:["primary","secondary"].map(u=>(0,Fn.jsx)(az,{value:u,children:n?.voices?.[u]?.label||u},u))})})]}):null}'''

NEW_TAIL = "(0,Fn.jsx)(adtVoiceDropdown,{})," + TAIL


def main():
    raw = BUNDLE.read_bytes()
    src = raw.decode("utf-8")
    if "adtVoiceDropdown" in src:
        print("ya parcheado: nada que hacer")
        return
    if src.count(ANCHOR) != 1 or src.count(TAIL) != 1:
        raise SystemExit(f"anclas inesperadas: Tz={src.count(ANCHOR)} tail={src.count(TAIL)}")

    if not BACKUP.exists():
        shutil.copy2(BUNDLE, BACKUP)
        print("backup:", BACKUP)

    out = src.replace(ANCHOR, COMPONENT + "\n" + ANCHOR, 1)
    out = out.replace(TAIL, NEW_TAIL, 1)
    BUNDLE.write_bytes(out.encode("utf-8"))
    print("parche aplicado:", len(raw), "->", len(out.encode("utf-8")), "bytes")


if __name__ == "__main__":
    main()
