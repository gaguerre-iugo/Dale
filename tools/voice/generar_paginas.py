# -*- coding: utf-8 -*-
"""
Genera los audios de las paginas 1 y 2 en las dos voces elegidas.

Voces:
  asesora    -> es-419-techagent-3   (Asesora tecnica, 48)
  consultor  -> es-419-commercial-10 (Consultor de moda, 49)

Salida:
  content/i18n/es-UY/voices/asesora/audio/<id>.mp3
  content/i18n/es-UY/voices/consultor/audio/<id>.mp3

Formato: MP3 mono 24 kHz, 96 kbps, normalizado a -27,5 LUFS para emparejar
con el corpus actual del libro (que mide entre -26 y -32 LUFS).

Uso:
  python tools/voice/generar_paginas.py            # paginas 1 y 2
  python tools/voice/generar_paginas.py --dry-run  # solo lista
"""
import argparse
import base64
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
I18N = ROOT / "content" / "i18n" / "es-UY"
MODEL = "gemini-3.8-flash-tts"
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/interactions"
PAGES = ["pg001_sec001.html", "pg002_sec001.html"]

VOICES = {
    "asesora": {"id": "es-419-techagent-3", "label": "Asesora"},
    "consultor": {"id": "es-419-commercial-10", "label": "Consultor"},
}

STYLE = ("Voz adulta y natural, como una persona real explicando algo con calma. "
         "Acento rioplatense uruguayo con she\u00edsmo marcado: la \u00abll\u00bb y la \u00aby\u00bb suenan como \u00absh\u00bb. "
         "Ritmo normal, sin alargar las vocales ni exagerar la alegr\u00eda.")


def api_key():
    if os.environ.get("GEMINI_API_KEY"):
        return os.environ["GEMINI_API_KEY"].strip()
    return (Path.home() / "Desktop" / "api_key_gemini.txt").read_text(encoding="utf-8").strip()


def page_ids():
    ids = []
    for page in PAGES:
        html = (ROOT / page).read_text(encoding="utf-8")
        for tid in re.findall(r'data-id="([^"]+)"', html):
            if tid not in ids:
                ids.append(tid)
    return ids


def synth(texto, voice, dest_wav, key, intentos=6):
    body = {
        "model": MODEL,
        "input": [{"type": "user_input", "content": [{
            "type": "text", "text": texto,
            "annotations": [{"type": "speech_metadata", "style": STYLE}]}]}],
        "response_format": {"type": "audio"},
        "generation_config": {"speech_config": [{"voice": voice}]},
    }
    data = json.dumps(body).encode("utf-8")
    for n in range(intentos):
        req = urllib.request.Request(
            ENDPOINT, data=data,
            headers={"x-goog-api-key": key, "Content-Type": "application/json"},
            method="POST")
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                resp = json.loads(r.read().decode("utf-8"))
            audio = None
            for step in resp.get("steps", []):
                if step.get("type") == "model_output":
                    for c in step.get("content", []):
                        if c.get("type") == "audio":
                            audio = c.get("data")
            if not audio:
                raise RuntimeError("respuesta sin audio")
            dest_wav.write_bytes(base64.b64decode(audio))
            return True
        except urllib.error.HTTPError as e:
            detalle = e.read().decode("utf-8", "replace")
            if e.code == 429:
                espera = 35 + n * 15
                print(f"    429; espero {espera}s", flush=True)
                time.sleep(espera)
                continue
            print(f"    HTTP {e.code}: {detalle[:200]}", flush=True)
            return False
    return False


def to_mp3(wav, mp3):
    mp3.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-v", "error", "-i", str(wav),
        "-af", "loudnorm=I=-27.5:TP=-2:LRA=7",
        "-ar", "24000", "-ac", "1", "-codec:a", "libmp3lame", "-b:a", "96k",
        str(mp3),
    ]
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    speech = json.loads((I18N / "speech_texts.json").read_text(encoding="utf-8"))
    ids = [i for i in page_ids() if i in speech]
    missing = [i for i in page_ids() if i not in speech]
    print(f"{len(ids)} ids con texto; {len(missing)} sin texto: {missing}")
    if args.dry_run:
        for i in ids:
            print(f"  {i}: {speech[i][:70]!r}")
        return

    key = api_key()
    total = len(ids) * len(VOICES)
    n = 0
    fallos = []
    with tempfile.TemporaryDirectory() as tmp:
        for slug, cfg in VOICES.items():
            for tid in ids:
                n += 1
                mp3 = I18N / "voices" / slug / "audio" / f"{tid}.mp3"
                if mp3.exists() and not args.force:
                    print(f"[{n}/{total}] {slug}/{tid} ya existe", flush=True)
                    continue
                print(f"[{n}/{total}] {slug}/{tid}", flush=True)
                wav = Path(tmp) / f"{slug}_{tid}.wav"
                if not synth(speech[tid], cfg["id"], wav, key):
                    fallos.append(f"{slug}/{tid}")
                    continue
                to_mp3(wav, mp3)
                time.sleep(6.5)
    print(f"listo. fallos: {fallos or 'ninguno'}")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
