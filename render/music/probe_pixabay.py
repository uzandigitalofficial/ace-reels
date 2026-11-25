"""Check whether Pixabay music pages expose a direct CDN MP3 without a login."""
import re
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
for u in ["https://pixabay.com/music/modern-classical-chill-piano-637122/",
          "https://pixabay.com/music/search/calm%20piano/"]:
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=20)
        h = r.read().decode("utf8", "ignore")
        print(u, r.status, len(h), sorted(set(re.findall(r"https://cdn\.pixabay\.com/[^\"'\s]+?\.mp3", h)))[:6])
    except Exception as e:
        print(u, "ERR", e)
