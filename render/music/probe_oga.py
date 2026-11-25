"""List downloadable files and the licence line on OpenGameArt pages (CC0 paper sounds)."""
import re
import sys
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
for u in sys.argv[1:] or ["https://opengameart.org/node/123492", "https://opengameart.org/node/127323",
                          "https://opengameart.org/content/rpg-sound-pack", "https://opengameart.org/content/50-rpg-sound-effects"]:
    try:
        h = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=30).read().decode("utf8", "ignore")
        title = re.search(r"<title>(.*?)</title>", h)
        lic = sorted(set(re.findall(r"(CC0|CC-BY[^<\"]{0,12}|GPL[^<\"]{0,8}|OGA-BY[^<\"]{0,6})", h)))
        files = sorted(set(re.findall(r"https://opengameart\.org/sites/default/files/[^\"'<> ]+", h)))
        print("==", u, title.group(1) if title else "", lic)
        for f in files:
            if not f.endswith((".png", ".jpg", ".gif")):
                print("  ", f)
    except Exception as e:
        print(u, "ERR", e)
