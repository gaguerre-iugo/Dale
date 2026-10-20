# -*- coding: utf-8 -*-
"""Construye content/i18n/es-UY/audio_voices.json.

El runtime ADT resuelve cada audio como
    ./content/i18n/<lang>/audio/<filename>
por eso las voces nuevas se referencian con un path relativo que sale de audio/
y entra en voices/<voz>/audio/.

Las paginas ya convertidas apuntan a la voz; el resto del libro sigue usando
audios.json hasta que se regenere (asi ninguna pagina queda muda).
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
I18N = ROOT / "content" / "i18n" / "es-UY"
PAGES = ["pg001_sec001.html", "pg002_sec001.html"]

VOICES = {
    "primary": {"slug": "asesora", "label": "Asesora"},
    "secondary": {"slug": "consultor", "label": "Consultor"},
}


def page_ids():
    ids = []
    for page in PAGES:
        html = (ROOT / page).read_text(encoding="utf-8")
        for tid in re.findall(r'data-id="([^"]+)"', html):
            if tid not in ids:
                ids.append(tid)
    return ids


def main():
    audios = json.loads((I18N / "audios.json").read_text(encoding="utf-8"))
    converted = set(page_ids())

    voices = {}
    for key, cfg in VOICES.items():
        mapping = {}
        for tid, filename in audios.items():
            if tid in converted:
                mapping[tid] = f"../voices/{cfg['slug']}/audio/{tid}.mp3"
            else:
                mapping[tid] = filename
        voices[key] = {"label": cfg["label"], "audios": mapping}

    out = {"voices": voices}
    path = I18N / "audio_voices.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{path} -> {len(voices)} voces, {len(voices['primary']['audios'])} ids cada una, "
          f"{len(converted)} convertidos a voz propia")


if __name__ == "__main__":
    main()
