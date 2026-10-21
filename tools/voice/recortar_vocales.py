# -*- coding: utf-8 -*-
"""Recorta las vocales A/E/O/U a un tramo corto y estable.

Se usa cuando no hay cuota de TTS: toma el centro del audio ya generado, busca
una ventana de ~0,30 s con la menor variación de tono posible y la corta con
fades. No cambia la voz, solo elimina el arrastre y los bordes entonados.

Uso:
    python tools/voice/recortar_vocales.py
"""
import subprocess
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
I18N = ROOT / "content" / "i18n" / "es-UY"
IDS = ["text-pg006-46", "text-pg006-47", "text-pg006-48", "text-pg006-49"]
SR = 16000
WIN = int(0.03 * SR)
HOP = int(0.01 * SR)
CUT = 0.30


def pcm(path):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR),
         "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0


def frames(x):
    rms, f0 = [], []
    for i in range(0, len(x) - WIN, HOP):
        f = x[i:i + WIN]
        r = float(np.sqrt((f * f).mean()))
        rms.append(r)
        if r < 0.012:
            f0.append(None)
            continue
        z = (f - f.mean()) * np.hanning(WIN)
        sp = np.abs(np.fft.rfft(z, 4 * WIN))
        hps = sp.copy()
        for h in (2, 3, 4):
            hps[:len(sp[::h])] *= sp[::h]
        lo, hi = int(70 * 4 * WIN / SR), int(300 * 4 * WIN / SR)
        f0.append((int(np.argmax(hps[lo:hi])) + lo) * SR / (4 * WIN))
    return rms, f0


def best_window(f0, speech):
    n = int(CUT / 0.01)
    best = None
    for i in range(0, max(0, len(f0) - n + 1)):
        seg = f0[i:i + n]
        if any(v is None for v in seg) or not all(speech[i:i + n]):
            continue
        arr = np.array(seg, dtype=float)
        med = float(np.median(arr))
        if med < 70 or med > 300:
            continue
        # Variacion total + penalizacion por alejarse de la mediana global.
        score = float(arr.max() - arr.min()) + abs(float(arr.mean()) - med)
        if best is None or score < best[0]:
            best = (score, i)
    return best[1] if best else None


def main():
    for voz in ("asesora", "consultor"):
        for tid in IDS:
            path = I18N / "voices" / voz / "audio" / f"{tid}.mp3"
            if not path.exists():
                print("falta", path)
                continue
            x = pcm(path)
            rms, f0 = frames(x)
            speech = [r > 0.012 for r in rms]
            idx = best_window(f0, speech)
            if idx is None:
                # Fallback: centro del tramo con voz.
                active = [i for i, s in enumerate(speech) if s]
                if not active:
                    print("sin voz", path)
                    continue
                center = (active[0] + active[-1]) // 2
                idx = max(0, center - int(CUT / 0.02))
            start = idx * 0.01
            end = min(len(x) / SR, start + CUT)
            if end - start < 0.18:
                print("muy corto", path)
                continue
            out = path.with_suffix(".vowel.mp3")
            fade = 0.015
            subprocess.run(
                ["ffmpeg", "-y", "-v", "error", "-ss", f"{start:.3f}",
                 "-to", f"{end:.3f}", "-i", str(path),
                 "-af", f"afade=t=in:st=0:d={fade},afade=t=out:st={end - start - fade:.3f}:d={fade}",
                 "-ar", "24000", "-ac", "1", "-codec:a", "libmp3lame",
                 "-b:a", "128k", str(out)], check=True)
            out.replace(path)
            print(f"{voz}/{tid}: {start:.2f}-{end:.2f}s -> {end - start:.2f}s")


if __name__ == "__main__":
    main()
