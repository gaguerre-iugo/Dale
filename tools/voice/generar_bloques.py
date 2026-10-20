# -*- coding: utf-8 -*-
"""Genera audio por bloque continuo y lo corta por item con alineacion forzada.

Problema: generar cada texto por separado (sobre todo palabras sueltas) hace que
la lectura suene a lista: cada clip trae su propia entonacion y silencios.
Solucion: pedir en una sola toma todos los items cortos de una pagina y cortar
el WAV en los limites reales de cada item. La alineacion usa faster-whisper
(timestamps por palabra) contra el texto preparado, asi no depende de que el
modelo respete pausas: pedir pausas largas daba resultados distintos en cada
toma.

Solo se agrupan items cortos (tapa y creditos). Los textos largos o con numeros
deletreados (ISBN, datos de edicion) siguen generandose por item: ahi el propio
texto tiene pausas internas y la alineacion de numeros es fragil.

Uso:
    python tools/voice/generar_bloques.py
    python tools/voice/generar_bloques.py --dry-run
"""
import argparse
import base64
import difflib
import json
import os
import re
import subprocess
import tempfile
import time
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
I18N = ROOT / "content" / "i18n" / "es-UY"
MODEL = "gemini-3.8-flash-tts"
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/interactions"

VOICES = {
    "asesora": "es-419-techagent-3",
    "consultor": "es-419-commercial-10",
}

STYLE = ("Voz adulta y natural, como una persona real explicando algo con calma. "
         "Acento rioplatense uruguayo con she\u00edsmo marcado: la \u00abll\u00bb y la \u00aby\u00bb suenan como \u00absh\u00bb. "
         "Ritmo normal, sin alargar las vocales ni exagerar la alegr\u00eda.")

# Items cortos que se leen como una lista continua.
BLOQUES = [
    ["pg001_n0002", "pg001_n0003", "pg001_n0004", "pg001_n0006", "pg001_n0007"],
    ["pg002_n0002", "pg002_n0003", "pg002_n0005", "pg002_n0006", "pg002_n0007",
     "pg002_n0009", "pg002_n0010", "pg002_n0012", "pg002_n0013", "pg002_n0015"],
]

PAD = 0.08          # respiro a cada lado del habla
GAP_COST = 0.9      # costo de saltear una palabra en la alineacion
DIG = {"0": "cero", "1": "uno", "2": "dos", "3": "tres", "4": "cuatro",
       "5": "cinco", "6": "seis", "7": "siete", "8": "ocho", "9": "nueve"}


def api_key():
    if os.environ.get("GEMINI_API_KEY"):
        return os.environ["GEMINI_API_KEY"].strip()
    return (Path.home() / "Desktop" / "api_key_gemini.txt").read_text(encoding="utf-8").strip()


def norm(word):
    s = unicodedata.normalize("NFD", word.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s)


def synth(texto, voice, dest, key, intentos=6):
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
                raise RuntimeError("sin audio")
            dest.write_bytes(base64.b64decode(audio))
            return True
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(35 + n * 15)
                continue
            print("   HTTP", e.code, e.read().decode("utf-8", "replace")[:200])
            return False
    return False


def duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=True).stdout.strip()
    return float(out)


def normalizar(src, dest):
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(src),
         "-af", "loudnorm=I=-27.5:TP=-2:LRA=7", str(dest)],
        check=True)


def cortar(src, dest, start, end):
    dest.parent.mkdir(parents=True, exist_ok=True)
    dur = max(0.05, end - start)
    fade = 0.012
    af = f"afade=t=in:st=0:d={fade},afade=t=out:st={max(0, dur - fade)}:d={fade}"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-ss", f"{start:.3f}", "-to", f"{end:.3f}",
         "-i", str(src), "-af", af,
         "-ar", "24000", "-ac", "1", "-codec:a", "libmp3lame", "-b:a", "96k", str(dest)],
        check=True)


def transcribir(path):
    from faster_whisper import WhisperModel
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(path), language="es", word_timestamps=True)
    words = []
    for segment in segments:
        for w in (segment.words or []):
            text = w.word.strip()
            if text.isdigit() and len(text) > 1:
                step = (w.end - w.start) / len(text)
                for j, ch in enumerate(text):
                    words.append((norm(DIG[ch]), w.start + j * step, w.start + (j + 1) * step))
            else:
                words.append((norm(text), w.start, w.end))
    return [w for w in words if w[0]]


def alinear(textos, words):
    """Needleman-Wunsch entre las palabras esperadas y las del ASR.

    Devuelve, por item, (inicio, fin) del habla real. Los items sin ninguna
    palabra reconocida se descartan para no cortar a ciegas.
    """
    expected, owner = [], []
    for k, texto in enumerate(textos):
        for w in re.findall(r"\w+", texto, flags=re.UNICODE):
            expected.append(norm(w))
            owner.append(k)
    n, m = len(expected), len(words)
    dp = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        dp[i][0] = i * GAP_COST
    for j in range(1, m + 1):
        dp[0][j] = j * GAP_COST
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            sim = difflib.SequenceMatcher(None, expected[i - 1], words[j - 1][0]).ratio()
            dp[i][j] = min(dp[i - 1][j - 1] + (1 - sim),
                           dp[i - 1][j] + GAP_COST,
                           dp[i][j - 1] + GAP_COST)
    i, j, matched = n, m, {}
    while i > 0 and j > 0:
        sim = difflib.SequenceMatcher(None, expected[i - 1], words[j - 1][0]).ratio()
        if abs(dp[i][j] - (dp[i - 1][j - 1] + (1 - sim))) < 1e-9:
            matched[i - 1] = (words[j - 1][1], words[j - 1][2])
            i -= 1
            j -= 1
        elif dp[i][j] == dp[i - 1][j] + GAP_COST:
            i -= 1
        else:
            j -= 1
    spans = []
    for k in range(len(textos)):
        times = [matched[p] for p in matched if owner[p] == k]
        spans.append((min(t[0] for t in times), max(t[1] for t in times)) if times else None)
    return spans


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    speech = json.loads((I18N / "speech_texts.json").read_text(encoding="utf-8"))
    key = api_key()
    report = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for slug, voice in VOICES.items():
            for bi, ids in enumerate(BLOQUES, 1):
                faltan = [i for i in ids if i not in speech]
                if faltan:
                    print(f"[{slug}] bloque {bi}: faltan textos {faltan}")
                    continue
                textos = [speech[i].strip() for i in ids]
                print(f"[{slug}] bloque {bi}: {len(ids)} items", flush=True)
                if args.dry_run:
                    continue
                raw = tmp / f"{slug}_{bi}.wav"
                if not synth("\n".join(textos), voice, raw, key):
                    print("   fallo la sintesis")
                    report.append({"voz": slug, "bloque": bi, "estado": "sintesis"})
                    continue
                norm_wav = tmp / f"{slug}_{bi}_norm.wav"
                normalizar(raw, norm_wav)
                total = duration(norm_wav)
                words = transcribir(norm_wav)
                spans = alinear(textos, words)
                if any(s is None for s in spans):
                    print("   item sin palabras alineadas; se omite el bloque")
                    report.append({"voz": slug, "bloque": bi, "estado": "alineacion",
                                   "sin_alinear": [ids[k] for k, s in enumerate(spans) if s is None]})
                    continue
                # Recortar desde el habla real con un pequeno respiro.
                cortes = []
                for k, (start, end) in enumerate(spans):
                    a = 0.0 if k == 0 else max(0.0, start - PAD)
                    b = total if k == len(spans) - 1 else min(total, end + PAD)
                    cortes.append((a, b))
                if any(b - a < 0.2 for a, b in cortes) or any(
                        cortes[k + 1][0] < cortes[k][1] for k in range(len(cortes) - 1)):
                    print("   cortes invalidos; se omite el bloque")
                    report.append({"voz": slug, "bloque": bi, "estado": "cortes"})
                    continue
                temporales = []
                for tid, (a, b) in zip(ids, cortes):
                    tmp_mp3 = tmp / f"{slug}_{bi}_{tid}.mp3"
                    cortar(norm_wav, tmp_mp3, a, b)
                    temporales.append((tmp_mp3, tid))
                for tmp_mp3, tid in temporales:
                    tmp_mp3.replace(I18N / "voices" / slug / "audio" / f"{tid}.mp3")
                report.append({"voz": slug, "bloque": bi, "estado": "ok",
                               "total_toma": round(total, 2),
                               "items": [{"id": i, "ini": round(a, 2), "fin": round(b, 2),
                                          "dur": round(b - a, 2)}
                                         for i, (a, b) in zip(ids, cortes)]})
                time.sleep(6.5)
    (Path(__file__).resolve().parent / "bloques_reporte.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=1)[:1500])


if __name__ == "__main__":
    main()
