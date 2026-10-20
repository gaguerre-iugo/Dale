# -*- coding: utf-8 -*-
"""Baja la velocidad de los audios de una pagina sin cambiar el tono.

Usa `atempo` de ffmpeg (preserva el pitch). No es idempotente: correrlo dos
veces con el mismo factor acelera/retrasa dos veces.

Uso:
    python tools/voice/ajustar_tempo.py --factor 0.88 --paginas pg001 pg002
    python tools/voice/ajustar_tempo.py --factor 0.88 --dry-run
"""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
I18N = ROOT / "content" / "i18n" / "es-UY"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--factor", type=float, required=True,
                    help="0.88 = 12%% mas lento (debe estar entre 0.5 y 1)")
    ap.add_argument("--paginas", nargs="+", default=["pg001", "pg002"])
    ap.add_argument("--voces", nargs="+", default=["asesora", "consultor"])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not 0.5 <= args.factor <= 1.0:
        raise SystemExit("factor fuera de rango")

    audios = json.loads((I18N / "audios.json").read_text(encoding="utf-8"))
    ids = [tid for tid in audios if any(tid.startswith(p + "_") for p in args.paginas)]
    print(f"{len(ids)} ids de {', '.join(args.paginas)}")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for voz in args.voces:
            for tid in ids:
                src = I18N / "voices" / voz / "audio" / f"{tid}.mp3"
                if not src.exists():
                    continue
                print(f"  {voz}/{tid}", flush=True)
                if args.dry_run:
                    continue
                out = tmp / f"{voz}_{tid}.mp3"
                subprocess.run(
                    ["ffmpeg", "-y", "-v", "error", "-i", str(src),
                     "-af", f"atempo={args.factor}",
                     "-ar", "24000", "-ac", "1", "-codec:a", "libmp3lame",
                     "-b:a", "128k", str(out)],
                    check=True)
                out.replace(src)


if __name__ == "__main__":
    main()
