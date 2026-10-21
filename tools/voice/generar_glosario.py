# -*- coding: utf-8 -*-
"""Genera el audio de todas las entradas actuales de glossary.json.

Lee glossary.json, arma la lista glNNN/glNNN_def en orden y genera bloques con
generar_bloques.py. Si un bloque no se puede alinear, reintenta sus items uno
por uno con generar_palabras.py.

Uso:
    python tools/voice/generar_glosario.py --voice asesora --model gemini-3.8-flash-tts
    python tools/voice/generar_glosario.py --voice consultor --model gemini-3.8-flash-lite-tts
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
I18N = ROOT / "content" / "i18n" / "es-UY"
TOOLS = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", required=True, choices=["asesora", "consultor"])
    ap.add_argument("--model", default="gemini-3.8-flash-lite-tts")
    ap.add_argument("--block", type=int, default=10)
    args = ap.parse_args()

    glossary = json.loads((I18N / "glossary.json").read_text(encoding="utf-8"))
    ids = []
    for obj in glossary.values():
        gid = obj.get("id")
        if gid:
            ids.extend([gid, gid + "_def"])

    dest = I18N / "voices" / args.voice / "audio"
    dest.mkdir(parents=True, exist_ok=True)
    print(f"{args.voice}: {len(ids)} ids, bloques de {args.block}", flush=True)

    for bi in range(0, len(ids), args.block):
        chunk = ids[bi:bi + args.block]
        before = {tid: (dest / f"{tid}.mp3").stat().st_mtime
                  if (dest / f"{tid}.mp3").exists() else None for tid in chunk}
        cmd = [sys.executable, str(TOOLS / "generar_bloques.py"),
               "--voice", args.voice, "--model", args.model,
               "--trim", "--tempo", "0.88", "--ids", *chunk]
        res = subprocess.run(cmd, capture_output=True, text=True)
        missing = [tid for tid in chunk
                   if not (dest / f"{tid}.mp3").exists()
                   or (dest / f"{tid}.mp3").stat().st_mtime == before[tid]]
        print(f"  bloque {bi // args.block + 1}: {len(chunk) - len(missing)}/{len(chunk)}"
              f"{' -> fallback ' + ','.join(missing) if missing else ''}", flush=True)
        if missing:
            for tid in missing:
                subprocess.run(
                    [sys.executable, str(TOOLS / "generar_palabras.py"),
                     "--voice", args.voice, "--model", args.model, "--ids", tid],
                    capture_output=True, text=True)
                if not (dest / f"{tid}.mp3").exists():
                    print(f"    fallo {tid}", flush=True)
        time.sleep(2)

    faltan = [tid for tid in ids if not (dest / f"{tid}.mp3").exists()]
    print(f"{args.voice}: faltan {len(faltan)}", faltan, flush=True)


if __name__ == "__main__":
    main()
