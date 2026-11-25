"""RSS feed of finished reels (newest first). A free poster (Make.com) watches it and publishes each new item to Instagram."""
import datetime, email.utils, glob, json, os, sys
from xml.sax.saxutils import escape

site = sys.argv[1]
repo = os.environ.get("GITHUB_REPOSITORY", "uzandigitalofficial/ace-reels")
owner, name = repo.split("/")
base = f"https://{owner.lower()}.github.io/{name}/"
items = [json.load(open(p, encoding="utf-8")) for p in glob.glob(os.path.join(site, "reels", "*.json"))]
items = [m for m in items if m["made"][9:13] >= "0500"]  # skip overnight test renders
items.sort(key=lambda m: m["made"], reverse=True)
out = []
for m in items:
    when = datetime.datetime.strptime(m["made"], "%Y%m%d-%H%M").replace(tzinfo=datetime.timezone.utc)
    size = os.path.getsize(os.path.join(site, "reels", m["file"]))
    out.append(f"""<item><title>{escape(m['id'])}</title><link>{escape(m['video_url'])}</link><guid isPermaLink="false">{escape(m['file'])}</guid>
<pubDate>{email.utils.format_datetime(when)}</pubDate><description>{escape(m['caption'])}</description>
<enclosure url="{escape(m['video_url'])}" length="{size}" type="video/mp4"/></item>""")
feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>Stolen Valour reels</title><link>{base}</link><description>Finished reels ready to post</description>
{''.join(out)}
</channel></rss>"""
open(os.path.join(site, "feed.xml"), "w", encoding="utf-8").write(feed)
print("feed items:", len(out))
