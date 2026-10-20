# -*- coding: utf-8 -*-
"""Genera palabras sueltas, una por pedido, con la voz y el modelo indicados.

A diferencia de `generar_bloques.py` (una toma continua para varios items), aca
cada palabra se pide como una frase independiente: asi lleva entonacion de
palabra aislada y no de lista. Se recorta el silencio inicial, se corta al final
del habla y se aplica el mismo tempo que las paginas 1 y 2.

Uso:
    python tools/voice/generar_palabras.py --voice consultor \
        --model gemini-3.8-flash-lite-tts \
        --ids text-pg006-53 text-pg006-54 text-pg006-55 text-pg006-56 \
              text-pg006-57 text-pg006-58 text-pg006-59 text-pg006-60
"""
import argparse
import json
import tempfile
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generar_bloques import (  # noqa: E402
    I18N, VOICES, api_key, synth, duration, normalizar, cortar,
    transcribir, alinear,
)
from generar_frase import lead_end, tempo  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", required=True, choices=list(VOICES))
    ap.add_argument("--model", default="gemini-3.8-flash-lite-tts")
    ap.add_argument("--ids", nargs="+", required=True)
    ap.add_argument("--tempo", type=float, default=0.88)
    ap.add_argument("--sleep", type=float, default=7.0,
                    help="segundos entre pedidos (limite de la API)")
    args = ap.parse_args()

    speech = json.loads((I18N / "speech_texts.json").read_text(encoding="utf-8"))
    key = api_key()
    dest_dir = I18N / "voices" / args.voice / "audio"
    dest_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for n, tid in enumerate(args.ids):
            texto = speech.get(tid, "").strip()
            if not texto:
                print(f"[{tid}] sin texto; se omite")
                continue
            # Una frase completa (mayuscula y punto) evita que el modelo lea la
            # palabra como fragmento de lista y se la coma.
            hablado = texto[:1].upper() + texto[1:]
            if hablado[-1] not in ".!?":
                hablado += "."
            print(f"[{args.voice}] {tid}: {hablado!r}", flush=True)
            raw = tmp / f"{tid}.wav"
            if not synth(hablado, VOICES[args.voice], raw, key, args.model):
                print("   fallo la sintesis")
                continue
            norm = tmp / f"{tid}_norm.wav"
            normalizar(raw, norm)
            total = duration(norm)
            words = transcribir(norm)
            spans = alinear([texto], words)
            if not spans or spans[0] is None:
                print(f"   no se pudo alinear ({words}); se omite")
                continue
            start = max(0.0, lead_end(norm) - 0.05)
            end = min(total, spans[0][1] + 0.30)
            dest = dest_dir / f"{tid}.mp3"
            cortar(norm, dest, start, end)
            if args.tempo and args.tempo != 1.0:
                tempo(dest, args.tempo)
            print(f"   {start:.2f}-{end:.2f}s -> {duration(dest):.2f}s")
            if n < len(args.ids) - 1:
                time.sleep(max(0.0, args.sleep))


if __name__ == "__main__":
    main()

