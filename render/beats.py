"""Beat grid for the music under a reel, and the helpers that sync the edit to it.

grid(src)            beat times, tempo, strong beats and phrase changes of a track (librosa, cached in assets/music_beats.json
                     keyed by URL or file hash, so GitHub only analyses a track once per cache hit)
choose_offset(...)   where to start the track so a strong beat lands on frame 1 and a drop or phrase change lands near the CTA
in_reel(...)         beat times shifted into reel time
snap_cuts(...)       move each scene cut onto the nearest beat within SNAP seconds, never before the last word of the previous beat
python render/beats.py <file or url> [...]   prints the grid of each track
"""
import hashlib, json, pathlib, sys, urllib.request

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "assets" / "music_beats.json"
SNAP = 0.12          # a cut moves onto a beat only when one is this close to the voice cue
CUT_LEAD = 0.12      # Reel.tsx shows a new scene this long before its first word
VERSION = 2          # bump when the analysis changes, so stale cache entries are redone


def _key(src):
    s = str(src)
    if s.startswith("http"):
        return s
    return "sha1:" + hashlib.sha1(pathlib.Path(s).read_bytes()).hexdigest()[:16]


def _load_cache():
    try:
        return json.loads(CACHE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _fetch(src, dst=None):
    s = str(src)
    if not s.startswith("http"):
        return pathlib.Path(s)
    dst = pathlib.Path(dst or ROOT / "tmp" / "music" / (hashlib.sha1(s.encode()).hexdigest()[:12] + pathlib.Path(s).suffix))
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists():
        urllib.request.urlretrieve(s, dst)
    return dst


def analyse(path):
    """librosa beat tracking plus a coarse energy curve. Strong beats = the bar phase (every 4th beat) with the most onset
    energy; phrase changes = strong beats where the energy of the next 4 beats jumps over the previous 4 (drops, entries)."""
    import librosa
    y, sr = librosa.load(str(path), sr=22050, mono=True)
    dur = len(y) / sr
    hop = 512
    env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
    tempo, fr = librosa.beat.beat_track(onset_envelope=env, sr=sr, hop_length=hop, units="frames")
    tempo = float(np.atleast_1d(tempo)[0])
    beats = librosa.frames_to_time(fr, sr=sr, hop_length=hop)
    if len(beats) < 8:
        return {"v": VERSION, "dur": round(dur, 3), "tempo": round(tempo, 2), "beats": [round(float(b), 3) for b in beats], "strong": [], "phrase": []}
    ons = env[np.clip(fr, 0, len(env) - 1)]
    phase = int(np.argmax([ons[k::4].mean() for k in range(4)]))
    strong = beats[phase::4]
    rms = librosa.feature.rms(y=y, hop_length=hop)[0]
    rt = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop)
    per = 60 / max(tempo, 1e-6)

    def energy(a, b):
        m = (rt >= a) & (rt < b)
        return float(rms[m].mean()) if m.any() else 0.0

    phrase = []
    for t in strong:
        pre, post = energy(t - 4 * per, t), energy(t, t + 4 * per)
        if t > 4 * per and post > 1e-4 and post / max(pre, 1e-4) > 1.25:
            phrase.append([round(float(t), 3), round(post / max(pre, 1e-4), 2)])
    return {"v": VERSION, "dur": round(dur, 3), "tempo": round(tempo, 2), "beats": [round(float(b), 3) for b in beats],
            "strong": [round(float(b), 3) for b in strong], "phrase": phrase}


def grid(src, local=None):
    """Cached beat grid of a track (URL or file). `local` = an already downloaded copy of a URL."""
    key = _key(src)
    cache = _load_cache()
    g = cache.get(key)
    if g and g.get("v") == VERSION:
        return g
    g = analyse(local or _fetch(src))
    cache = _load_cache()  # re-read: another process may have written meanwhile
    cache[key] = g
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache, indent=0, sort_keys=True), encoding="utf-8")
    return g


def windows(segs, snap=SNAP):
    """For every seg after the first: (voice cue, earliest, latest) time its scene may appear. Earliest = the previous beat's
    last word has ended; latest = this beat's first word; both within `snap` of the cue."""
    out = []
    for i in range(1, len(segs)):
        s, prev = segs[i], segs[i - 1]
        cue = s["start"] - CUT_LEAD
        lo = max(cue - snap, (prev["words"][-1]["end"] if prev.get("words") else prev["end"]) + 0.02)
        hi = min(cue + snap, s["start"] + 0.02)
        out.append((cue, lo, hi))
    return out


def choose_offset(g, total, cta_at, segs=None):
    """Track start (seconds) so a strong beat is on frame 1, the strongest nearby phrase change lands on the CTA cut and as
    many scene cuts as possible can sit on a beat. Only offsets that leave the whole reel inside the track are tried."""
    win = windows(segs) if segs else []
    beats = np.asarray(g.get("beats", []))
    strong = [t for t in g.get("strong", []) if t + total <= g["dur"] - 0.3] or [t for t in g.get("beats", []) if t + total <= g["dur"] - 0.3]
    if not strong:
        return 0.0, None
    per = 60 / max(g.get("tempo") or 120, 1e-6)
    best, best_cost, hit = strong[0], 1e9, None
    for o in strong[:200]:
        want = o + cta_at
        cost, h = 9.0, None
        for t, ratio in g.get("phrase", []):
            d = abs(t - want)
            c = d - 0.25 * min(ratio, 3)
            if d <= 1.5 and c < cost:
                cost, h = c, t
        if h is None:  # no drop near: fall back to the 8-bar phrase grid counted from the start beat
            k = round(cta_at / (32 * per)) or 1
            cost = 2.0 + abs(o + k * 32 * per - want) * 0.5
        if win and len(beats):
            rb = beats - o
            cost -= 0.6 * sum(1 for _, lo, hi in win if ((rb >= lo) & (rb <= hi)).any())
        cost += 0.002 * o  # prefer the earlier of equal options (the intro of the track)
        if cost < best_cost:
            best, best_cost, hit = o, cost, h
    return round(float(best), 3), (round(hit - best, 3) if hit is not None else None)


def in_reel(g, offset, total):
    return [round(b - offset, 3) for b in g.get("beats", []) if -0.001 <= b - offset <= total]


def snap_cuts(segs, beats, snap=SNAP):
    """Give every seg after the first a `cut` time (when its scene appears). Default is CUT_LEAD before its first word; it moves
    onto the nearest beat within `snap`, but never before the previous beat's last word ends and never after this beat's first
    word, so no word is ever cut off. Returns the share of cuts that landed on a beat."""
    if not beats:
        return 0.0
    b = np.asarray(beats)
    hits = 0
    for i, (cue, lo, hi) in enumerate(windows(segs, snap), start=1):
        s = segs[i]
        cand = b[(b >= lo) & (b <= hi)]
        if len(cand):
            s["cut"] = round(float(cand[np.argmin(np.abs(cand - cue))]), 3); hits += 1
        else:
            s["cut"] = round(max(cue, lo), 3)
    return hits / max(1, len(segs) - 1)


if __name__ == "__main__":
    for a in sys.argv[1:]:
        g = grid(a)
        print(a, f"tempo {g['tempo']} dur {g['dur']} beats {len(g['beats'])} strong {len(g['strong'])} phrase {g['phrase'][:6]}")
