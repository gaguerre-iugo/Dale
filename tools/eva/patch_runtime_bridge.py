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

Y, sobre el reproductor real (window.__adtPlayer, que publica el hook de audio
en cada render):
  hasItems()    -> si la pagina tiene textos con audio
  playingReal() -> si el audio esta sonando de verdad (mira el elemento)
  play() / pause() / togglePlay()
  stopKeep()    -> detiene sin perder el texto ni el punto de escucha

Ademas, el cierre de la lectura en voz alta ya no borra el audio ni reinicia el
indice: solo pausa, asi que al reactivar el modo se puede continuar.

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
    /* eva-pause-lectura: la tarjeta habla y la lectura se pausa */
    try{if(window.__adtKit&&window.__adtKit.pauseReading)window.__adtKit.pauseReading();}catch(e){}
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

# Antes de sonar la palabra de una tarjeta, pausar la lectura (evita dos voces).
PLAYTEXT_OLD = """    var filename=map[id]||audios[id];
    if(!filename)return false;
    var a=window.__adtTextAudio;"""

PLAYTEXT_NEW = """    var filename=map[id]||audios[id];
    if(!filename)return false;
    /* eva-pause-lectura: la tarjeta habla y la lectura se pausa */
    try{if(window.__adtKit&&window.__adtKit.pauseReading)window.__adtKit.pauseReading();}catch(e){}
    var a=window.__adtTextAudio;"""

# Al cambiar de voz, retomar desde el punto donde iba en vez de volver al
# principio de la página: F acepta un tiempo de arranque y un flag de play.
VOICE_FN_OLD = "let F=(0,mt.useCallback)(j=>"
VOICE_FN_NEW = "let F=(0,mt.useCallback)((j,adtSeek,adtPlay)=>"

VOICE_META_OLD = 'ee.onloadedmetadata=()=>{if(t.current&&t.current.mode==="word"&&!w[pe.id])'
VOICE_META_NEW = (
    'ee.onloadedmetadata=()=>{'
    'if(typeof adtSeek==="number"&&isFinite(adtSeek)&&adtSeek>0){'
    'try{ee.currentTime=Math.min(adtSeek,Math.max(0,(ee.duration||adtSeek)-.05))}catch(adtE){}}'
    'if(t.current&&t.current.mode==="word"&&!w[pe.id])'
)

VOICE_PLAY_OLD = (
    'k(pe,ee),s(j),ee.play().then(()=>{Q===n.current&&(u("tts"),r(!0))})'
    '.catch(Z=>{Q===n.current&&(console.warn("[adt-runtime] audio.play() rejected",Z),M(),r(!1))})'
)
VOICE_PLAY_NEW = (
    'k(pe,ee),s(j),adtPlay!==!1&&('
    'typeof adtSeek==="number"&&isFinite(adtSeek)?'
    'ee.addEventListener("loadedmetadata",()=>{ee.play().then(()=>{Q===n.current&&(u("tts"),r(!0))})'
    '.catch(Z=>{Q===n.current&&(console.warn("[adt-runtime] audio.play() rejected",Z),M(),r(!1))})},{once:true}):'
    'ee.play().then(()=>{Q===n.current&&(u("tts"),r(!0))})'
    '.catch(Z=>{Q===n.current&&(console.warn("[adt-runtime] audio.play() rejected",Z),M(),r(!1))}))'
)

VOICE_EFFECT_OLD = (
    "(0,mt.useEffect)(()=>{B.current!==p&&(B.current=p,z(),r(!1),s(0))},[p,s,r,z])"
)
VOICE_EFFECT_NEW = (
    "(0,mt.useEffect)(()=>{if(B.current===p)return;"
    "let adtJ=e.current,adtSeguia=!!(adtJ&&adtJ.src&&!adtJ.paused),"
    "adtT=adtJ&&adtJ.src?adtJ.currentTime:0;"
    "B.current=p;if(!adtJ||!adtJ.src)return;"
    "F(i,adtT,adtSeguia)},[p,i])"
)

# El hook de audio devuelve su API en el ultimo termino del `return` con coma.
# Se publica en window.__adtPlayer y se agregan stopKeep() e isPaused().
PLAYER_OLD = (
    ",{isPlaying:a,hasItems:H.length>0,play:K,pause:q,togglePlayPause:Y,"
    "playNext:G,playPrevious:X,stop:re,playAtIndex:F}}var j_=E($(),1)"
)
PLAYER_NEW = (
    ",(window.__adtPlayer={isPlaying:a,hasItems:H.length>0,play:K,pause:q,togglePlayPause:Y,"
    "playNext:G,playPrevious:X,stop:re,stopKeep:q,"
    "isPaused:()=>{let j=e.current;return !j||j.paused},playAtIndex:F})}var j_=E($(),1)"
)

# Al apagar el modo lectura, antes se borraba el audio y se volvia al indice 0.
# Ahora solo se pausa y se limpia el resaltado: el punto de escucha se conserva.
CLOSE_OLD = "(0,mt.useEffect)(()=>{L||(z(),r(!1),s(0))},[L,z,r,s])"
CLOSE_NEW = "(0,mt.useEffect)(()=>{L||(q(),M(),r(!1))},[L,q,r,M])"

# El fallback por etiqueta puede encontrar los propios botones del reproductor
# del kit (usan los mismos nombres accesibles) y auto-clickearse en recursion.
CLICK_OLD = (
    'click(label){let b=document.querySelector(\'#interface-container button[aria-label="\'+label+\'"]\')'
    '||document.querySelector(\'button[aria-label="\'+label+\'"]\');if(!b)return false;b.click();return !b.disabled}'
)
CLICK_NEW = (
    'click(label){let r=document.getElementById("interface-container"),'
    'b=r&&r.querySelector(\'button[aria-label="\'+label+\'"]\');'
    'if(!b){let l=document.querySelectorAll(\'button[aria-label="\'+label+\'"]\');'
    'for(let i=0;i<l.length;i++){if(!l[i].closest("#reflow-tts-player")){b=l[i];break}}}'
    'if(!b)return false;b.click();return !b.disabled}'
)

# Las actividades hablan con speechSynthesis (consignas, refuerzos) y las
# tarjetas reproducen su palabra con __adtTextAudio. Ninguno de esos audios pasa
# por el reproductor, asi que Pausa tiene que cortarlos: si no, la voz sintetica
# sigue hablando y parece que la pausa no funciona.
PLAYER_METHODS = """/* eva-player-api:start */
function __adtSilenceExtras(){
  try{if(window.speechSynthesis)window.speechSynthesis.cancel();}catch(e){}
  var a=window.__adtTextAudio;
  if(a){try{a.pause();}catch(e){}}
}
window.__adtKit.hasItems=function(){var p=window.__adtPlayer;return !!(p&&p.hasItems)};
window.__adtKit.playingReal=function(){var p=window.__adtPlayer;return !!(p&&p.hasItems&&!p.isPaused())};
window.__adtKit.play=function(){var p=window.__adtPlayer;if(!p||!p.hasItems)return false;__adtSilenceExtras();if(p.isPaused())p.play();return true};
window.__adtKit.pause=function(){var p=window.__adtPlayer;if(!p||!p.hasItems)return false;if(!p.isPaused())p.pause();__adtSilenceExtras();return true};
window.__adtKit.togglePlay=function(){var p=window.__adtPlayer;if(!p||!p.hasItems)return false;if(p.isPaused()){__adtSilenceExtras();p.play();}else{p.pause();__adtSilenceExtras();}return true};
window.__adtKit.stopKeep=function(){var p=window.__adtPlayer;if(!p||!p.hasItems)return false;p.pause();__adtSilenceExtras();return true};
/* Cuando la actividad empieza a hablar (consigna, refuerzo o palabra de una
   tarjeta), la lectura se pausa para que no suenen dos voces a la vez. */
window.__adtKit.pauseReading=function(){var p=window.__adtPlayer;if(p&&p.hasItems&&!p.isPaused()){p.pause();return true}return false};
(function(){
  try{
    var s=window.speechSynthesis;
    if(!s||s.__adtSpeakPatched)return;
    var orig=s.speak;
    s.speak=function(){try{if(window.__adtKit&&window.__adtKit.pauseReading)window.__adtKit.pauseReading();}catch(e){}return orig.apply(s,arguments)};
    s.__adtSpeakPatched=true;
  }catch(e){}
})();
/* eva-player-api:end */
"""


def replace_once(src, old, new, label):
    if src.count(old) != 1:
        raise SystemExit(f"ancla inesperada en {label}: {src.count(old)}")
    return src.replace(old, new, 1)


def main():
    src = BUNDLE.read_bytes().decode("utf-8")
    out = src

    if "__adtKit" not in out:
        out = replace_once(out, ANCHOR, SNIPPET + "\n" + ANCHOR, "puente base")

    if "playText" not in out:
        out = replace_once(out, ANCHOR, EXTRAS + "\n" + ANCHOR, "playText")
        print("audio suelto agregado")

    if "window.__adtPlayer=" not in out:
        out = replace_once(out, PLAYER_OLD, PLAYER_NEW, "API del reproductor")
        out = replace_once(out, CLOSE_OLD, CLOSE_NEW, "cierre sin reinicio")
        print("API del reproductor publicada")

    if "/* eva-player-api:start */" in out:
        begin = out.index("/* eva-player-api:start */")
        end = out.index("/* eva-player-api:end */", begin) + len("/* eva-player-api:end */")
        actual = out[begin:end]
        if actual != PLAYER_METHODS.strip():
            out = out[:begin] + PLAYER_METHODS.strip() + out[end:]
            print("metodos del reproductor actualizados")
    elif "__adtKit.stopKeep=" in out:
        begin = out.index("window.__adtKit.hasItems=function(){")
        cierre = "window.__adtKit.stopKeep=function(){var p=window.__adtPlayer;if(!p||!p.hasItems)return false;p.pause();return true};\n"
        end = out.index(cierre, begin) + len(cierre)
        out = out[:begin] + PLAYER_METHODS + out[end:]
        print("metodos del reproductor actualizados")
    else:
        out = replace_once(out, ANCHOR, PLAYER_METHODS + "\n" + ANCHOR, "metodos de reproduccion")
        print("metodos play/pause/stopKeep agregados")

    if "eva-pause-lectura" not in out:
        out = replace_once(out, PLAYTEXT_OLD, PLAYTEXT_NEW, "pausa al reproducir tarjeta")
        print("playText pausa la lectura")

    if "adtSeek" not in out:
        out = replace_once(out, VOICE_FN_OLD, VOICE_FN_NEW, "firma de F")
        out = replace_once(out, VOICE_META_OLD, VOICE_META_NEW, "seek al cargar metadata")
        out = replace_once(out, VOICE_PLAY_OLD, VOICE_PLAY_NEW, "play condicionado")
        out = replace_once(out, VOICE_EFFECT_OLD, VOICE_EFFECT_NEW, "cambio de voz sin reinicio")
        print("cambio de voz continuo")

    # `F` se declara despues de este efecto: no puede figurar en las deps.
    if "},[p,F,i])" in out:
        out = out.replace("},[p,F,i])", "},[p,i])", 1)
        print("dependencias del efecto de voz corregidas")

    if 'closest("#reflow-tts-player")' not in out:
        out = replace_once(out, CLICK_OLD, CLICK_NEW, "click acotado")
        print("click acotado al runtime")

    if out == src:
        print("puente ya actualizado")
        return

    BUNDLE.write_bytes(out.encode("utf-8"))
    print("bundle parcheado:", len(src.encode("utf-8")), "->", len(out.encode("utf-8")), "bytes")


if __name__ == "__main__":
    main()
