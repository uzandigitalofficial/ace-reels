"""Write the gallery page: newest reels first, each with its caption and a copy button (for posting by hand until Instagram is connected)."""
import glob, html, json, os, sys

from credit import with_credit

site = sys.argv[1]
items = [json.load(open(p, encoding="utf-8")) for p in glob.glob(os.path.join(site, "reels", "*.json"))]
items.sort(key=lambda m: m["made"], reverse=True)
cards = []
for m in items:
    cap = html.escape(with_credit(m))
    cards.append(f"""<article><video src="reels/{m['file']}" poster="reels/{m['file'][:-4]}.jpg" controls preload="none" playsinline></video>
<div class="meta"><b>{html.escape(m['id'])}</b> · {m['seconds']}s · {m['made']} UTC · <a href="reels/{m['file']}" download>download</a></div>
<pre>{cap}</pre><button onclick="navigator.clipboard.writeText(this.previousElementSibling.textContent);this.textContent='Copied'">Copy caption</button></article>""")
page = f"""<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ACE Reels</title>
<style>body{{margin:0;background:#07080b;color:#f1ece2;font:15px/1.5 system-ui,sans-serif}}h1{{font:500 34px Georgia,serif;text-align:center;margin:28px}}
main{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:22px;padding:0 22px 40px;max-width:1300px;margin:auto}}
article{{background:#111318;border:1px solid #23262d;border-radius:14px;padding:12px}}video{{width:100%;aspect-ratio:9/16;border-radius:10px;background:#000}}
.meta{{color:#9aa;font-size:13px;margin:8px 0}}a{{color:#9fd3bf}}pre{{white-space:pre-wrap;font:13px/1.45 system-ui;color:#cfc6b6;max-height:150px;overflow:auto}}
button{{background:#9fd3bf;color:#07080b;border:0;border-radius:8px;padding:8px 12px;font-weight:600;cursor:pointer}}</style>
<h1>ACE Reels</h1><main>{''.join(cards) or '<p>No reels yet.</p>'}</main>"""
open(os.path.join(site, "index.html"), "w", encoding="utf-8").write(page)
