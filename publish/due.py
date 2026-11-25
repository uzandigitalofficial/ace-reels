"""Self-healing schedule: GitHub may skip a scheduled run, so the workflow wakes hourly and renders only if a slot is owed.
Slots (UTC): 05:30, 10:30, 16:30 (SAST 07:30, 12:30, 18:30). Prints run=yes|no and slot=<n> for GITHUB_OUTPUT."""
import datetime, json, os, urllib.request

SLOTS = [(5, 30), (10, 30), (16, 30)]
now = datetime.datetime.now(datetime.timezone.utc)
due = sum(1 for h, m in SLOTS if (now.hour, now.minute) >= (h, m))
today = now.strftime("%Y%m%d")
req = urllib.request.Request(f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/contents/reels?ref=gh-pages",
                             headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}", "Accept": "application/vnd.github+json"})
try:
    names = [f["name"] for f in json.load(urllib.request.urlopen(req, timeout=30))]
except Exception as e:
    names = []
made = sum(1 for n in names if n.endswith(".mp4") and n.startswith(today) and n[9:13] >= "0500")
print(f"run={'yes' if made < due else 'no'}")
print(f"slot={made}")
