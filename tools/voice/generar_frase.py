# -*- coding: utf-8 -*-
"""Genera una frase que en el libro son dos items y la corta en el espacio.

Caso tipico: la tapa tiene "CUADERNILLO" y "JUEGOS" como dos data-id. Generados
por separado suenan a dos palabras sueltas. Aca se piden juntos, como una sola
frase, y se cortan en el limite entre las dos palabras: la primera conserva la
entonacion continua y la segunda el cierre de la frase.

Uso:
    python tools/voice/generar_frase.py --voice consultor \
        --model gemini-3.8-flash-lite-tts --ids pg001_n0003 pg001_n0004
"""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generar_bloques import (  # noqa: E402
    I18N, VOICES, STYLE, api_key, synth, duration, normalizar, cortar,
    transcribir, alinear,
)
import re  # noqa: E402


def lead_end(path):
    err = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(path), "-af",
         "silencedetect=noise=-45dB:d=0.08", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    if starts and starts[0] < 0.05 and ends:
        return ends[0]
    return 0.0


def add_gap(path, gap):
    """Agrega silencio al final del clip (separacion entre items de la frase)."""
    if gap <= 0:
        return
    out = path.with_suffix(".gap.mp3")
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(path),
         "-af", f"apad=pad_dur={gap:.3f}",
         "-ar", "24000", "-ac", "1", "-codec:a", "libmp3lame", "-b:a", "128k", str(out)],
        check=True)
    out.replace(path)


def tempo(src, factor):
    out = src.with_suffix(".tempo.mp3")
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(src), "-af", f"atempo={factor}",
         "-ar", "24000", "-ac", "1", "-codec:a", "libmp3lame", "-b:a", "128k", str(out)],
        check=True)
    out.replace(src)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", required=True, choices=list(VOICES))
    ap.add_argument("--model", default="gemini-3.8-flash-lite-tts")
    ap.add_argument("--ids", nargs="+", required=True)
    ap.add_argument("--tempo", type=float, default=0.88)
    ap.add_argument("--gap", type=float, default=0.12,
                    help="silencio al final de cada item, salvo el ultimo")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    speech = json.loads((I18N / "speech_texts.json").read_text(encoding="utf-8"))
    textos = [speech[i].strip() for i in args.ids]
    # Las mayusculas sostenidas hacen que el modelo enfatice cada palabra.
    hablados = [t.capitalize() if t.isupper() else t for t in textos]
    frase = " ".join(hablados)
    print("frase:", frase)

    if args.dry_run:
        return

    key = api_key()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        raw = tmp / "frase.wav"
        if not synth(frase, VOICES[args.voice], raw, key, args.model):
            raise SystemExit("fallo la sintesis")
        norm = tmp / "frase_norm.wav"
        normalizar(raw, norm)
        words = transcribir(norm)
        spans = alinear(textos, words)
        if any(s is None for s in spans):
            raise SystemExit(f"no se pudieron alinear todos los items: {spans}")
        total = duration(norm)
        # Un unico limite entre items: el punto medio entre el fin de una palabra
        # y el inicio de la siguiente. Sin solapamiento ni silencio agregado.
        limites = [(spans[k][1] + spans[k + 1][0]) / 2 for k in range(len(spans) - 1)]
        cortes = []
        # Arrancar en el habla real (no en el silencio inicial del modelo) y
        # cerrar un poco despues de la ultima palabra.
        prev = max(0.0, lead_end(norm) - 0.05)
        for b in limites:
            cortes.append((prev, b))
            prev = b
        cortes.append((prev, min(total, spans[-1][1] + 0.06)))
        print("cortes:", [(round(a, 2), round(b, 2)) for a, b in cortes])
        for k, (tid, (a, b)) in enumerate(zip(args.ids, cortes)):
            dest = I18N / "voices" / args.voice / "audio" / f"{tid}.mp3"
            cortar(norm, dest, a, b)
            if args.tempo and args.tempo != 1.0:
                tempo(dest, args.tempo)
            if k < len(cortes) - 1:
                add_gap(dest, args.gap)
            print("  ", tid, round(duration(dest), 2), "s")


if __name__ == "__main__":
    main()
