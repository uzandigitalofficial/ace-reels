"""Post the newest rendered reel to Instagram through the official Graph API.
Needs repo secrets IG_TOKEN and IG_USER_ID. Without them it exits cleanly (reel stays on the Pages gallery).
IG_GRAPH_HOST: graph.instagram.com (Instagram Login, default) or graph.facebook.com (Facebook Login)."""
import glob, json, os, sys, time, urllib.error, urllib.parse, urllib.request

tok, uid = os.environ.get("IG_TOKEN", "").strip(), os.environ.get("IG_USER_ID", "").strip()
metas = sorted(glob.glob("out/*.json"))
if not metas:
    sys.exit("no reel rendered")
meta = json.load(open(metas[-1], encoding="utf-8"))
if not tok or not uid:
    print("Instagram not connected yet (IG_TOKEN / IG_USER_ID secrets missing). Reel is on the gallery:", meta["video_url"])
    sys.exit(0)
host = os.environ.get("IG_GRAPH_HOST", "").strip() or "graph.instagram.com"
API = f"https://{host}/v21.0"


def call(method, path, params):
    params = dict(params, access_token=tok)
    data = urllib.parse.urlencode(params).encode()
    url = f"{API}{path}" + ("" if method == "POST" else "?" + data.decode())
    req = urllib.request.Request(url, data=data if method == "POST" else None, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace").replace(tok, "***")
        sys.exit(f"Graph API {e.code} on {path}: {body}")


for i in range(60):  # wait for GitHub Pages to serve the file
    try:
        with urllib.request.urlopen(urllib.request.Request(meta["video_url"], method="HEAD"), timeout=20) as r:
            if r.status == 200:
                break
    except Exception:
        pass
    time.sleep(10)
else:
    sys.exit("video never became public on Pages")

c = call("POST", f"/{uid}/media", {"media_type": "REELS", "video_url": meta["video_url"], "caption": meta["caption"],
                                    "share_to_feed": "true", "cover_url": meta["cover_url"]})
cid = c["id"]
for i in range(60):
    st = call("GET", f"/{cid}", {"fields": "status_code"}).get("status_code")
    if st == "FINISHED":
        break
    if st in ("ERROR", "EXPIRED"):
        sys.exit(f"container {st}")
    time.sleep(10)
else:
    sys.exit("container not ready after 10 minutes")
r = call("POST", f"/{uid}/media_publish", {"creation_id": cid})
print("published", meta["id"], "media", r.get("id"))
