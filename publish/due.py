"""Self-healing schedule: renders only if a posting slot is owed today.
Slots (UTC): 05:30, 10:30, 16:30 (SAST 07:30, 12:30, 18:30). Prints run=yes|no and slot=<n> for GITHUB_OUTPUT.
Counts only real reels (the RSS feed holds non-test reels), so test renders never block a post."""
import base64, datetime, email.utils, json, os, urllib.request

SLOTS = [(5, 30), (10, 30), (16, 30)]
now = datetime.datetime.now(datetime.timezone.utc)
due = sum(1 for h, m in SLOTS if (now.hour, now.minute) >= (h, m))
req = urllib.request.Request(
    f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/contents/feed.xml?ref=gh-pages",
    headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}", "Accept": "application/vnd.github+json"})
made = 0
try:
    feed = base64.b64decode(json.load(urllib.request.urlopen(req, timeout=30))["content"]).decode("utf-8")
    for part in feed.split("<pubDate>")[1:]:
        when = email.utils.parsedate_to_datetime(part.split("</pubDate>")[0])
        if when.date() == now.date() and when.hour >= 5:
            made += 1
except Exception as e:
    print(f"note=feed unreadable ({e!r})"[:200])
force = os.environ.get("FORCE") == "true"
print(f"run={'yes' if force or made < due else 'no'}")
print(f"slot={made}")
