"""Caption text with the music credit appended. One place, used by post_ig.py and feed.py.
No music_credit in the reel's meta: the caption is returned unchanged. Never added twice."""


def with_credit(meta):
    cap = (meta.get("caption") or "").rstrip()
    credit = (meta.get("music_credit") or "").strip()
    if not credit or credit in cap:
        return cap
    return cap + "\n\n" + credit
