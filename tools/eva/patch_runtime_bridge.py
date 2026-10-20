# -*- coding: utf-8 -*-
"""Expone un puente minimo del runtime ADT para que la interfaz del kit pueda
leer y cambiar ajustes sin depender del DOM interno, y para que las actividades
puedan reproducir un audio suelto con la voz activa.

Anade `window.__adtKit` con:
  get()        -> {easyRead, readAloud, autoplay, describeImages, highlight,
                    voice, speed, hideMenus, playing}
  set(k, v)    -> cambia el ajuste correspondiente (mismo store que usa el runtime)
  click(label) -> dispara un boton del runtime por su nombre accesible
  disabled(label) -> si ese boton esta deshabilitado
  playText(id) -> reproduce el audio de esa id con la voz, velocidad y volumen
                  activos; devuelve false si no hay audio mapeado
  stopText()   -> detiene ese audio suelto

Idempotente. Uso: python tools/eva/patch_runtime_bridge.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "assets" / "base.bundle.local.js"
ANCHOR = "function adtVoiceDropdown(){"

SNIPPET = (
    'window.__adtKit={'
    'get(){let g=k=>xe().get(k);return{'
    'easyRead:g(dr),readAloud:g(ei),autoplay:g(Qy),describeImages:g(ex),'
    'highlight:g(Jy),voice:g(Fy),speed:g(tx),hideMenus:g(ub),reduceMotion:g(Ya),playing:g(YN)}},'
    'set(k,v){let m={easyRead:dr,readAloud:ei,autoplay:Qy,describeImages:ex,'
    'highlight:Jy,voice:Fy,speed:tx,hideMenus:ub,reduceMotion:Ya};if(m[k])xe().set(m[k],v)},'
    'click(label){let b=document.querySelector(\'#interface-container button[aria-label="\'+label+\'"]\')'
    '||document.querySelector(\'button[aria-label="\'+label+\'"]\');if(!b)return false;b.click();return !b.disabled},'
    'disabled(label){let b=document.querySelector(\'button[aria-label="\'+label+\'"]\');return !b||b.disabled}};'
)

EXTRAS = """window.__adtKit.playText=function(id){
  try{
    var audios=xe().get(_y)||{};
    var voices=xe().get(_d);
    var voice=xe().get(Fy);
    var map=voices&&voices.voices&&voices.voices[voice]&&voices.voices[voice].audios;
    if(!map||!Object.keys(map).length)map=audios;
    var filename=map[id]||audios[id];
    if(!filename)return false;
    var a=window.__adtTextAudio;
    if(!a){a=window.__adtTextAudio=new Audio();a.preload="auto";}
    try{a.pause();}catch(e){}
    try{a.currentTime=0;}catch(e){}
    a.src="./content/i18n/"+xe().get(wa)+"/audio/"+filename;
    a.playbackRate=xe().get(tx)||1;
    var vol=xe().get(ox);
    a.volume=Math.max(0,Math.min(1,vol==null?1:vol));
    var p=a.play();
    if(p&&p.catch)p.catch(function(){});
    return true;
  }catch(e){return false;}
};
window.__adtKit.stopText=function(){
  var a=window.__adtTextAudio;
  if(a){try{a.pause();a.currentTime=0;}catch(e){}}
};"""


def main():
    src = BUNDLE.read_bytes().decode("utf-8")
    if "playText" in src:
        print("playText ya aplicado")
        return
    if src.count(ANCHOR) != 1:
        raise SystemExit(f"ancla inesperada: {src.count(ANCHOR)}")
    if "__adtKit" in src:
        # El puente base ya existe: solo se agregan los metodos de audio.
        out = src.replace(ANCHOR, EXTRAS + "\n" + ANCHOR, 1)
    else:
        out = src.replace(ANCHOR, SNIPPET + "\n" + EXTRAS + "\n" + ANCHOR, 1)
    BUNDLE.write_bytes(out.encode("utf-8"))
    print("puente aplicado:", len(src.encode('utf-8')), "->", len(out.encode('utf-8')), "bytes")


if __name__ == "__main__":
    main()
