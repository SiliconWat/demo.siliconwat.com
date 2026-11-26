#!/usr/bin/env python3
"""Write passages.json: the real typed pages the drawings quote (CC0, the Buddhist Institute edition as typed by Se Mong Ly).

    python3 pick-passages.py      # reads the released dataset; run only when the picks change

Each pick is a page (volume, scan opening) and the sentence a search would highlight on it. The sentence is found by its
words, never typed here, so what the drawing highlights is EXACTLY what the page says (zero-width spaces and all). The
units are the finder's own: a Khmer page is typed as paragraphs, so a paragraph is split after each ។ or ៕.
"""
import io, json, os, re

DATA = os.environ.get("TIPITAKA_DATA", os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../tipitaka-khmer/data/release/khmer-tipitaka-transcription/data"))
HERE = os.path.dirname(os.path.abspath(__file__))
# (volume, scan opening, a few words of the sentence to highlight, basket)
PICKS = [(18, 93, "ជាអ្នកមិនក្រោធ មិនចងសេចក្តីក្រោធទុក។", "sutta"),
         (65, 63, "ជួនកាល សេចក្តីក្រោធ", "sutta"),
         (13, 183, "សេចក្តីមិនក្រោធចំពោះអ្នកចោទ", "vinaya"),
         (83, 216, "បុគ្គលមិនចងសេចក្តីក្រោធទុក", "abhidhamma")]
ZW = "​"


def units(text):
    out = []
    for para in text.split("\n"):
        t = para.strip()
        if t:
            out += [u.strip() for u in re.findall(r"[^។៕]+[។៕]*|[។៕]+", t) if u.strip()]
    return out


def page(volume, scan, leaf):
    for line in io.open(os.path.join(DATA, "vol-%03d.jsonl" % volume), encoding="utf-8"):
        r = json.loads(line)
        if r["page"] == scan and r["leaf"] == leaf:
            return r["text"]
    return None


out = []
for volume, scan, words, basket in PICKS:
    km = page(volume, scan, "khmer")
    us = units(km)
    hit = [i for i, u in enumerate(us) if words in u.replace(ZW, "")]
    assert len(hit) >= 1, (volume, scan, words)
    u = us[hit[0]]
    assert u in km, "a unit must be an exact substring of the page"
    heading = us[1] if len(us) > 1 and not re.search(r"[។៕]$", us[1]) and len(us[1]) < 90 else None
    out.append({"volume": volume, "scan": scan, "basket": basket, "printed": us[0], "heading": heading, "unit": hit[0] + 1,
                "sentence": u, "khmer": km, "pali": page(volume, scan, "pali")})
    print("v%d p%d (printed %s) · unit %d · %s" % (volume, scan, us[0], hit[0] + 1, (heading or "")[:40]))
io.open(os.path.join(HERE, "passages.json"), "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
print("passages.json: %d pages" % len(out))
