"""Write picks/index.html from picks/picks.json: one player per voice, music option and mix, plus a pick bar."""
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "picks"


def card(kind, id_, title, line, file, extra=""):
    e = html.escape
    return f"""<article class="card" data-kind="{kind}" data-id="{e(id_)}">
  <header><span class="tag">{e(id_)}</span><h3>{e(title)}</h3></header>
  <p>{e(line)}</p>{extra}
  <audio controls preload="none" src="{e(file)}"></audio>
  <button class="pick" type="button" aria-pressed="false">Pick {e(id_)}</button>
</article>"""


def main():
    d = json.loads((OUT / "picks.json").read_text(encoding="utf-8"))
    best = json.loads((OUT / "_raw" / "best.json").read_text(encoding="utf-8"))
    voices = "\n".join(card("voice", v["id"], v["engine"], v["line"], v["file"]) for v in d["voices"])
    music = "\n".join(card("music", m["id"], m["title"], m["line"], m["file"],
                           f'<p class="lic">{html.escape(m.get("licence", "Made here, no licence needed") + (" . " + m["artist"] if m.get("artist") else ""))}'
                           f'{(" . <a href=" + chr(34) + html.escape(m["page"]) + chr(34) + ">source</a>") if m.get("page") else ""}</p>')
                      for m in d["music"])
    mixes = "\n".join(card("mix", x["id"], f'{x["voice"]} over {x["music"]}', x.get("line", "Voice on top, music about 24 dB under, light sound design."), x["file"])
                      for x in d["mixes"])
    rec = html.escape(best.get("summary", ""))
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; media-src 'self'; img-src 'self' data:">
<meta http-equiv="X-Content-Type-Options" content="nosniff">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="robots" content="noindex">
<title>Voice and music picks</title>
<style>
:root{{--bg:#0d0c0b;--card:#171513;--line:#2a2622;--text:#f1ece4;--muted:#a59c90;--accent:#e2b866;--ease:cubic-bezier(.2,.8,.2,1)}}
*{{box-sizing:border-box}}html{{-webkit-text-size-adjust:100%}}
body{{margin:0;background:radial-gradient(1200px 600px at 80% -10%,#2a2217 0,transparent 60%),var(--bg);color:var(--text);font:16px/1.5 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;padding:0 0 120px}}
.wrap{{max-width:1100px;margin:0 auto;padding:40px 20px}}
h1{{font:700 clamp(34px,6vw,64px)/1.02 Georgia,"Times New Roman",serif;letter-spacing:-.02em;margin:0 0 12px}}
h2{{font:600 13px/1 ui-sans-serif,system-ui;letter-spacing:.18em;text-transform:uppercase;color:var(--accent);margin:48px 0 16px}}
.lead{{color:var(--muted);max-width:640px;margin:0}}
.rec{{margin-top:24px;padding:16px 18px;border:1px solid #4a3d26;background:linear-gradient(180deg,#221c13,#19150f);border-radius:14px;max-width:760px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}}
.card{{background:linear-gradient(180deg,#1b1916,var(--card));border:1px solid var(--line);border-radius:16px;padding:16px;display:flex;flex-direction:column;gap:10px;transition:transform .35s var(--ease),border-color .35s var(--ease),box-shadow .35s var(--ease)}}
.card:hover{{transform:translateY(-2px);border-color:#3b342c;box-shadow:0 12px 30px rgba(0,0,0,.35)}}
.card.on{{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent) inset}}
.card header{{display:flex;gap:10px;align-items:baseline}}
.tag{{font:700 13px/1 ui-monospace,Consolas,monospace;color:#120f0a;background:var(--accent);padding:5px 7px;border-radius:6px;white-space:nowrap}}
h3{{font-size:16px;margin:0;font-weight:600}}
.card p{{margin:0;color:var(--muted);font-size:14px}}
.card p.lic{{font-size:12px}} .card a{{color:var(--accent)}}
audio{{width:100%;height:40px}}
.pick{{align-self:flex-start;background:transparent;color:var(--text);border:1px solid #4a4239;border-radius:10px;padding:8px 12px;font:600 13px/1 inherit;cursor:pointer;transition:background .25s var(--ease),border-color .25s var(--ease)}}
.pick:hover{{border-color:var(--accent)}} .pick:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
.pick[aria-pressed=true]{{background:var(--accent);color:#120f0a;border-color:var(--accent)}}
.bar{{position:fixed;left:0;right:0;bottom:0;background:rgba(13,12,11,.86);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border-top:1px solid var(--line);padding:12px 20px;display:flex;gap:12px;align-items:center;justify-content:center;flex-wrap:wrap}}
.bar b{{color:var(--accent)}}
.bar button{{background:var(--accent);color:#120f0a;border:0;border-radius:10px;padding:10px 14px;font-weight:700;cursor:pointer}}
.bar button:focus-visible{{outline:2px solid #fff;outline-offset:2px}}
.card{{opacity:0;transform:translateY(10px);animation:in .6s var(--ease) forwards}}
@keyframes in{{to{{opacity:1;transform:none}}}}
@media (prefers-reduced-motion:reduce){{.card{{animation:none;opacity:1;transform:none;transition:none}}}}
</style></head><body>
<main class="wrap">
<h1>Pick a voice<br>and a sound.</h1>
<p class="lead">Every clip reads the same script and plays at the same loudness (-16 LUFS), so you are only comparing the sound. Tap Pick on one voice and one music option, then Copy and send it back.</p>
<div class="rec"><b>Recommendation:</b> {rec}</div>
<h2>Mixes: best 3 voices over the best music</h2>
<section class="grid">{mixes}</section>
<h2>Voices</h2>
<section class="grid">{voices}</section>
<h2>Music and sound</h2>
<section class="grid">{music}</section>
<p class="lead" style="margin-top:40px;font-size:13px">Music: Kevin MacLeod (incompetech.com), Creative Commons Attribution 4.0, credit goes in the caption. Sound effects: Kenney and starninjas (CC0) plus a whoosh and riser made here. <a style="color:var(--accent)" href="LICENCES.md">Every source and licence</a>.</p>
</main>
<div class="bar" role="status" aria-live="polite"><span>Voice: <b id="pv">none</b></span><span>Music: <b id="pm">none</b></span><button id="copy" type="button">Copy my pick</button></div>
<script>
(() => {{
  const picks = {{voice: null, music: null}};
  const show = () => {{ document.getElementById('pv').textContent = picks.voice || 'none'; document.getElementById('pm').textContent = picks.music || 'none'; }};
  document.querySelectorAll('.card').forEach((c, i) => {{
    c.style.animationDelay = Math.min(i * 40, 600) + 'ms';
    const kind = c.dataset.kind === 'mix' ? 'voice' : c.dataset.kind, b = c.querySelector('.pick');
    b.addEventListener('click', () => {{
      document.querySelectorAll('.card[data-kind="' + c.dataset.kind + '"]').forEach(o => {{ o.classList.remove('on'); o.querySelector('.pick').setAttribute('aria-pressed', 'false'); }});
      c.classList.add('on'); b.setAttribute('aria-pressed', 'true'); picks[kind] = c.dataset.id; show();
    }});
  }});
  document.querySelectorAll('audio').forEach(a => a.addEventListener('play', () => document.querySelectorAll('audio').forEach(o => {{ if (o !== a) o.pause(); }})));
  const btn = document.getElementById('copy');
  btn.addEventListener('click', async () => {{
    const t = 'My pick: voice ' + (picks.voice || '?') + ', music ' + (picks.music || '?');
    try {{ await navigator.clipboard.writeText(t); btn.textContent = 'Copied'; }} catch (e) {{ btn.textContent = t; }}
    setTimeout(() => btn.textContent = 'Copy my pick', 1800);
  }});
}})();
</script>
</body></html>"""
    (OUT / "index.html").write_text(page, encoding="utf-8")
    print("wrote", OUT / "index.html")


if __name__ == "__main__":
    main()
