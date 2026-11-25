"""Write picks/index.html from picks/picks.json (cream and navy, big play buttons, phone first)."""
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "picks"
SCRIPT = ("Most car buyers choose a dealership before they ever make a call. They search on their phone, and they pick the site "
          "that looks clear and trustworthy. Stolen Valour builds that website for your dealership in seven days. "
          "Message us on WhatsApp tonight, and be the one they find.")
e = html.escape


def card(kind, id_, title, line, file, extra=""):
    return f"""<article class="card" data-kind="{kind}" data-id="{e(id_)}">
  <div class="top"><span class="tag">{e(id_)}</span><h3>{e(title)}</h3></div>
  <p>{e(line)}</p>{extra}
  <div class="row">
    <button class="play" type="button" aria-label="Play {e(id_)}" aria-pressed="false"><svg viewBox="0 0 24 24" aria-hidden="true"><path class="i-play" d="M7 4.5v15l12-7.5z"/><path class="i-pause" d="M6.5 4.5h4v15h-4zM13.5 4.5h4v15h-4z"/></svg></button>
    <div class="meter" aria-hidden="true"><i></i></div>
    <button class="pick" type="button" aria-pressed="false">Pick {e(id_)}</button>
  </div>
  <audio preload="none" src="{e(file)}"></audio>
</article>"""


def main():
    d = json.loads((OUT / "picks.json").read_text(encoding="utf-8"))
    voices = "\n".join(card("voice", v["id"], v["engine"], v["line"], v["file"]) for v in d["voices"])
    music = "\n".join(card("music", m["id"], f'{m["title"]}, {m["artist"]}', m["line"], m["file"],
                           f'<p class="lic"><b>{e(m["licence"])}</b>, free for commercial use. Caption credit needed.<br>'
                           f'<span class="credit">{e(m["attribution"])}</span></p>') for m in d["music"])
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; media-src 'self'; img-src 'self' data:">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="robots" content="noindex">
<title>Pick a voice and a music bed</title>
<style>
:root{{--cream:#f6f0e4;--paper:#fffaf0;--navy:#14213d;--ink:#1c2a4a;--muted:#5d6783;--line:#ded3bd;--gold:#b88a2e;--ease:cubic-bezier(.2,.8,.2,1)}}
*{{box-sizing:border-box}}html{{-webkit-text-size-adjust:100%}}
body{{margin:0;background:var(--cream);color:var(--ink);font:17px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;padding-bottom:110px}}
.wrap{{max-width:1040px;margin:0 auto;padding:32px 18px}}
h1{{font:700 clamp(34px,7vw,64px)/1.03 Georgia,"Times New Roman",serif;color:var(--navy);letter-spacing:-.02em;margin:0 0 14px}}
h2{{font:700 13px/1 system-ui,sans-serif;letter-spacing:.16em;text-transform:uppercase;color:var(--navy);margin:44px 0 6px}}
.lead{{margin:0;max-width:640px;color:var(--muted)}}
.script{{background:var(--navy);color:var(--cream);border-radius:14px;padding:16px 18px;margin:22px 0 0;font:italic 18px/1.5 Georgia,serif;max-width:760px}}
.script b{{display:block;font:700 12px/1 system-ui;letter-spacing:.16em;text-transform:uppercase;color:#e3c27a;margin-bottom:8px;font-style:normal}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:14px;margin-top:16px}}
.card{{background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:16px;display:flex;flex-direction:column;gap:10px;transition:border-color .3s var(--ease),box-shadow .3s var(--ease)}}
.card.on{{border-color:var(--navy);box-shadow:0 0 0 2px var(--navy) inset}}
.top{{display:flex;gap:10px;align-items:center}}
.tag{{font:700 15px/1 ui-monospace,Consolas,monospace;background:var(--navy);color:var(--cream);padding:6px 9px;border-radius:7px}}
h3{{font-size:17px;margin:0;color:var(--navy)}}
.card p{{margin:0;color:var(--muted);font-size:15px}}
.lic{{font-size:13px!important}}.lic b{{color:var(--navy)}}.credit{{font-size:12px;color:#7b8399}}
.row{{display:flex;align-items:center;gap:12px;margin-top:4px}}
.play{{flex:none;width:64px;height:64px;border-radius:50%;border:0;background:var(--navy);color:var(--cream);cursor:pointer;display:grid;place-items:center;transition:transform .25s var(--ease),background .25s var(--ease)}}
.play:active{{transform:scale(.94)}}.play svg{{width:30px;height:30px;fill:currentColor}}.i-pause{{display:none}}
.play[aria-pressed=true]{{background:var(--gold)}}.play[aria-pressed=true] .i-play{{display:none}}.play[aria-pressed=true] .i-pause{{display:block}}
.meter{{flex:1;height:6px;background:#e6dcc6;border-radius:3px;overflow:hidden}}.meter i{{display:block;height:100%;width:0;background:var(--navy)}}
.pick{{flex:none;min-height:44px;background:transparent;color:var(--navy);border:2px solid var(--navy);border-radius:10px;padding:0 14px;font:700 14px system-ui;cursor:pointer}}
.pick[aria-pressed=true]{{background:var(--navy);color:var(--cream)}}
button:focus-visible{{outline:3px solid var(--gold);outline-offset:2px}}
.bar{{position:fixed;left:0;right:0;bottom:0;background:var(--navy);color:var(--cream);padding:12px 16px;display:flex;gap:14px;align-items:center;justify-content:center;flex-wrap:wrap}}
.bar b{{color:#e3c27a}}.bar button{{min-height:44px;background:var(--cream);color:var(--navy);border:0;border-radius:10px;padding:0 16px;font:700 15px system-ui;cursor:pointer}}
.foot{{margin-top:36px;font-size:13px;color:var(--muted);max-width:720px}}
.card{{opacity:0;transform:translateY(8px);animation:in .55s var(--ease) forwards}}@keyframes in{{to{{opacity:1;transform:none}}}}
@media (prefers-reduced-motion:reduce){{.card{{animation:none;opacity:1;transform:none}}*{{transition:none!important}}}}
</style></head><body>
<main class="wrap">
<h1>Pick a voice<br>and a music bed.</h1>
<p class="lead">Every voice reads the same script at the same loudness, so you are only comparing the sound. Tap play, then tap Pick on one voice and one music bed, and send the two codes back.</p>
<div class="script"><b>The script</b>{e(SCRIPT)}</div>
<h2>Voices</h2>
<section class="grid">{voices}</section>
<h2>Music beds</h2>
<p class="lead">About 28 seconds each, played at full level here. In a reel the music sits well under the voice. All six are free for commercial use and all six need a credit line in the caption.</p>
<section class="grid">{music}</section>
<p class="foot">Music by Kevin MacLeod (incompetech.com), licensed under Creative Commons Attribution 4.0. Full sources and licences: <a href="LICENCES.md">LICENCES.md</a>.</p>
</main>
<div class="bar" role="status" aria-live="polite"><span>Voice: <b id="pv">none</b></span><span>Music: <b id="pm">none</b></span><button id="copy" type="button">Copy my pick</button></div>
<script>
(() => {{
  const picks = {{voice: null, music: null}}, all = [...document.querySelectorAll('audio')];
  const show = () => {{ pv.textContent = picks.voice || 'none'; pm.textContent = picks.music || 'none'; }};
  document.querySelectorAll('.card').forEach((c, i) => {{
    c.style.animationDelay = Math.min(i * 50, 500) + 'ms';
    const a = c.querySelector('audio'), p = c.querySelector('.play'), m = c.querySelector('.meter i'), b = c.querySelector('.pick');
    p.addEventListener('click', () => {{ if (a.paused) {{ all.forEach(o => o.pause()); a.play(); }} else a.pause(); }});
    a.addEventListener('play', () => p.setAttribute('aria-pressed', 'true'));
    ['pause', 'ended'].forEach(ev => a.addEventListener(ev, () => p.setAttribute('aria-pressed', 'false')));
    a.addEventListener('timeupdate', () => {{ m.style.width = (a.duration ? a.currentTime / a.duration * 100 : 0) + '%'; }});
    b.addEventListener('click', () => {{
      document.querySelectorAll('.card[data-kind="' + c.dataset.kind + '"]').forEach(o => {{ o.classList.remove('on'); o.querySelector('.pick').setAttribute('aria-pressed', 'false'); }});
      c.classList.add('on'); b.setAttribute('aria-pressed', 'true'); picks[c.dataset.kind] = c.dataset.id; show();
    }});
  }});
  copy.addEventListener('click', async () => {{
    const t = 'My pick: voice ' + (picks.voice || '?') + ', music ' + (picks.music || '?');
    try {{ await navigator.clipboard.writeText(t); copy.textContent = 'Copied'; }} catch (e) {{ copy.textContent = t; }}
    setTimeout(() => copy.textContent = 'Copy my pick', 1800);
  }});
}})();
</script>
</body></html>"""
    (OUT / "index.html").write_text(page, encoding="utf-8")
    print("wrote", OUT / "index.html")


if __name__ == "__main__":
    main()
