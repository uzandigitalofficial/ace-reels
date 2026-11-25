"""Scene picking for Reel Engine 6. Each beat names the 2D scene that explains it best.
python render/scenes.py --write   fills a "scene" field on every beat in content/stolenvalour.json that lacks one.
python render/scenes.py --stats   prints the scene mix.
"""
import argparse, collections, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCENES = ["kinetic", "casefile", "checklist", "google", "whatsapp", "sitebuild", "beforeafter", "price", "timeline", "icons", "footage", "cta"]

NICHES = [
    (r"\bspa\b", "spa"), (r"salon|hair|braid", "salon"), (r"barber", "barber"), (r"clinic|doctor|dentist|physio", "clinic"), (r"practice", "practice"),
    (r"workshop|mechanic|panel beat", "workshop"), (r"bakery|baker|cake", "bakery"), (r"\bgym\b|trainer|fitness", "gym"), (r"dealership|showroom|car sales", "dealership"),
    (r"florist|bouquet|flower", "florist"), (r"tutor", "tutor"), (r"restaurant|menu|cafe|coffee", "restaurant"), (r"photograph", "photographer"),
    (r"plumb", "plumber"), (r"electric", "electrician"), (r"nail", "nail bar"), (r"beauty|lash|brow", "beauty studio"), (r"vet\b|grooming|pet", "pet groomer"),
    (r"cleaning|cleaner", "cleaning service"), (r"catering|caterer", "caterer"), (r"guest ?house|b&b|lodge", "guesthouse"), (r"portfolio", "studio"),
]

NEG = r"\b(old way|still|buried|elsewhere|lose|losing|lost|miss|missed|missing|slow|wrong|stuck|chasing|no one|nobody|cannot|can't|give up|gives up|leave|leaves|wait|waiting|mystery|surprise|scroll(s)? past|disappear|outdated|broken|not a website|reprint|nowhere|ignored|unanswered|guess|guessing|confus|hidden|hard to)\b"
POS = r"\b(new way|proper|answers|fix|ready|included|clear|simple|live|yours|in your name|free|fast|easy|one tap|straight away|sorted|built)\b"


def niche_of(text):
    t = text.lower()
    for pat, name in NICHES:
        if re.search(pat, t):
            return name
    return None


def mood_of(text, pillar, kind):
    t = text.lower()
    n, p = len(re.findall(NEG, t)), len(re.findall(POS, t))
    if re.search(r"\bno (setup fee|obligation|minimum|separate bill|jargon|spreadsheets|waiting)|nothing is a mystery|not stuck", t):
        p += 2
    if n == p:
        return "neg" if (kind == "hook" and pillar in ("pain", "niche")) else "pos"
    return "neg" if n > p else "pos"


RULES = [
    ("price", r"\br ?\d|showroom|studio plan|studio site|studio is"),
    ("timeline", r"7 days|seven days|within the week|from first call|day 1 to|live in|a week\b"),
    ("google", r"google|search|find you|found|near me|look(s|ing)? (you )?up|listing|business profile|elsewhere|someone else|competitor|map(s)?\b|look(s)? first|where do .* look|check(s)? you out|before (she|he|they) book"),
    ("whatsapp", r"whatsapp|\bdm|message|chat|repl(y|ies)|enquir|question|answer|\bask"),
    ("beforeafter", r"old way|new way|slow|old site|outdated|facebook page|clutter|instead of|versus|vs\b|heavy pages|printed"),
    ("checklist", r"hosting|changes|report|included|includes|monthly fee|all in\b|every page|checklist|three things|steps"),
    ("sitebuild", r"button|homepage|home page|page|website|site|build|built|domain|price list|menu|headline|layout"),
    ("icons", r"services|book|hours|address|location|trust|photos|reviews|email|padlock|secure|faq"),
]


def candidates(beat, kind):
    if kind == "cta":
        return ["cta"]
    t = (beat["show"] + " " + beat["say"]).lower()
    c = [name for name, pat in RULES if re.search(pat, t)]
    if len(re.split(r",\s+|\s+and\s+", beat["show"])) >= 3 and "checklist" not in c:
        c.insert(1 if c[:1] == ["price"] else 0, "checklist")
    if kind == "hook":
        lead = ["casefile"] if "?" in beat["say"] else ["kinetic"]
        return lead + [x for x in c if x in ("google", "whatsapp", "beforeafter")] + ["kinetic"]
    return c + ["icons", "kinetic", "checklist"]


def assign(script):
    used, out = [], []
    beats = [("hook", script["hook"])] + [("line", x) for x in script["lines"]] + [("cta", script["cta"])]
    for kind, b in beats:
        pick = next((x for x in candidates(b, kind) if x not in used or x in ("cta",)), "kinetic")
        if kind == "line" and pick == "kinetic" and "kinetic" in used:
            pick = next((x for x in ("icons", "checklist", "sitebuild") if x not in used), "icons")
        used.append(pick)
        out.append(pick)
    if script.get("visual") == "site" and "icons" in out[1:4]:
        out[out.index("icons", 1)] = "footage"  # real site footage, inside a pinned polaroid
    return out


def save(path, bank):
    """Same layout as the hand-kept file: one script per line."""
    body = ",\n".join(json.dumps(s, ensure_ascii=False, separators=(",", ":")) for s in bank)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("[\n" + body + "\n]\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", default="stolenvalour"); ap.add_argument("--write", action="store_true"); ap.add_argument("--stats", action="store_true")
    ap.add_argument("--force", action="store_true", help="re-pick scenes even where a beat already has one")
    a = ap.parse_args()
    path = ROOT / "content" / f"{a.brand}.json"
    bank = json.load(open(path, encoding="utf-8"))
    if a.write:
        for s in bank:
            picks = assign(s)
            beats = [s["hook"]] + s["lines"] + [s["cta"]]
            for b, p in zip(beats, picks):
                if (a.force and s.get("pillar") != "teach") or "scene" not in b:  # teach scenes are hand-picked
                    b["scene"] = p
        save(path, bank)
    mix = collections.Counter(b.get("scene", "?") for s in bank for b in [s["hook"]] + s["lines"] + [s["cta"]])
    print(len(bank), "scripts", dict(mix.most_common()))


if __name__ == "__main__":
    main()
