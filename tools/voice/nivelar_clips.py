# -*- coding: utf-8 -*-
"""Empareja el volumen de clips ya generados (por ejemplo, palabras cortadas de
una toma continua).

La toma continua se normaliza entera, pero cada palabra queda a distinto nivel:
la primera suele salir mas fuerte y las ultimas mas bajas. Aca se mide cada clip
y se le aplica la ganancia necesaria para llevarlo al objetivo, con un limitador
para no recortar picos.

Uso:
    python tools/voice/nivelar_clips.py --ids text-pg006-53 text-pg006-54
"""
import argparse
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
I18N = ROOT / "content" / "i18n" / "es-UY"


def lufs(path):
    err = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(path), "-af",
         "loudnorm=print_format=json", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    match = re.search(r'"input_i"\s*:\s*"([-\d.]+)"', err)
    return float(match.group(1)) if match else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", nargs="+", required=True)
    ap.add_argument("--voces", nargs="+", default=["asesora", "consultor"])
    ap.add_argument("--target", type=float, default=-27.5)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for voz in args.voces:
            for tid in args.ids:
                path = I18N / "voices" / voz / "audio" / f"{tid}.mp3"
                if not path.exists():
                    continue
                before = lufs(path)
                if before is None:
                    print(f"  {voz}/{tid}: no se pudo medir")
                    continue
                gain = args.target - before
                print(f"  {voz}/{tid}: {before:.2f} -> {args.target:.2f} LUFS "
                      f"({gain:+.2f} dB)")
                if args.dry_run or abs(gain) < 0.05:
                    continue
                out = tmp / f"{voz}_{tid}.mp3"
                subprocess.run(
                    ["ffmpeg", "-y", "-v", "error", "-i", str(path),
                     "-af", f"volume={gain:.2f}dB,alimiter=limit=-2dB:level=false",
                     "-ar", "24000", "-ac", "1", "-codec:a", "libmp3lame",
                     "-b:a", "128k", str(out)],
                    check=True)
                out.replace(path)


if __name__ == "__main__":
    main()

