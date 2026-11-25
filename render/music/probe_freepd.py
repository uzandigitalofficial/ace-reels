"""List public-domain (CC0) tracks on FreePD with their direct MP3 links."""
import re
import sys
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130.0"
u = sys.argv[1] if len(sys.argv) > 1 else "https://freepd.com/"
h = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=20).read().decode("utf8", "ignore")
print(len(h))
print(sorted(set(re.findall(r"href=\"([^\"]+)\"", h)))[:80])
print(sorted(set(re.findall(r"[^\"'<> ]+\.mp3", h)))[:200])
