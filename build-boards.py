#!/usr/bin/env python3
"""Generate the siliconwat.com artboards (v1: the finder) and canvas.json.

    python3 build-boards.py && python3 build-index.py && python3 build-wall.py

The spec is private (SW/siliconwat.com/siliconwat.com/SPEC.md); these drawings follow it. The neutrals are READ from the vendored
brand layer (brand.py, guarded by scripts/check-brand.mjs); this surface's own colors are the one marked block in brand.py.

A Silicon Wat surface: no B-Emblem and no heart anywhere (the emblem stands for the B in HeartBank), and the icon is a PLACEHOLDER
until Silicon Wat's own mark is settled. Not an H3 surface, so no not-a-chartered-bank footer.

⛔ v1 shows NO GENERATED TEXT (founder 2026-11-24: "1: A in v1"): every passage on these boards is the Tipiṭaka AS TYPED, quoted
from passages.json (pick-passages.py reads the CC0 release; the highlighted sentence is an exact substring of its page). The
QUESTIONS are made up, and the counts in a summary are illustrative and say so. The build refuses, in the rendered text of every
board: "sign in", the regulated words, a progress figure, a countdown, an AI model or vendor named, the heart, and any line that
puts words in the Buddha's mouth. The Khmer is OURS and UNREVIEWED; every Khmer board says so.
"""
import hashlib, html, io, json, os, re
from brand import fill, icon_svg, ACCENT

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, DW, DH = 390, 844, 1280, 800
CSS = io.open(os.path.join(HERE, "board.base.css"), encoding="utf-8").read()
FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500'
         '&family=Noto+Sans+Khmer:wght@400;500;600&family=Noto+Serif+Khmer:wght@400;500&display=swap">')
P = json.load(io.open(os.path.join(HERE, "passages.json"), encoding="utf-8"))

BARRED = [r"\bsign[\s-]?in\b", r"\bdeposit", r"\bsavings\b", r"\binterest\b", r"\byield\b", r"\bbank\b", r"chartered",
          r"\bremaining\b", r"\bseconds? left\b", r"\bminutes? left\b", r"\bstreak", r"\brank", r"\bclaude\b", r"\bgpt", r"chatgpt",
          r"\bgemini\b", r"\bopenai\b", r"\banthropic\b", r"\bllama\b", r"\bheart\b", r"♥", r"❤",
          r"\bbuddha (says|said|teaches|tells)\b", r"\bthe buddha'?s answer\b", r"ព្រះពុទ្ធ\S*\s*មានព្រះបន្ទូល"]
EMBLEM_SIG = "M3.9743 20.0257"  # the first move of the B-Emblem path: it must appear in no board


def ar_num(k):
    """A printed page number, typed in Khmer numerals, in Arabic numerals (the English boards)."""
    return k.translate(str.maketrans("០១២៣៤៥៦៧៨៩", "0123456789"))


def km_num(n):
    return str(n).translate(str.maketrans("0123456789", "០១២៣៤៥៦៧៨៩"))


def ic(d, size=16):
    return ('<svg width="%d" height="%d" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true">%s</svg>' % (size, size, d))


SHARE = ic('<path d="M12 15V3m0 0L7 8m5-5 5 5"/><path d="M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-7"/>')
COPY = ic('<rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/>')
SPEAK = ic('<path d="M11 5 6 9H3v6h3l5 4z"/><path d="M15.5 8.5a5 5 0 0 1 0 7M18.5 5.5a9 9 0 0 1 0 13"/>')
ASK = ic('<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/><path d="M9.8 9.6a2.3 2.3 0 0 1 4.4.9c0 1.5-2.2 2-2.2 2M12 15.5h.01"/>')
EXT = ic('<path d="M14 4h6v6M20 4l-9 9"/><path d="M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>')
SEARCH = ic('<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>', 20)
CLOCK = ic('<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>', 15)
TRASH = ic('<path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13"/>', 16)
DOWN = ic('<path d="M12 3v12m0 0-5-5m5 5 5-5"/><path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2"/>')
BACK = ic('<path d="M15 5 8 12l7 7"/>', 18)
DEVICE = ic('<rect x="7" y="2.5" width="10" height="19" rx="2.5"/><path d="M11 18.5h2"/>', 18)
PLAY = '<svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z" fill="currentColor"/></svg>'

BASKET = {"vinaya": ("Vinaya", "វិន័យបិដក"), "sutta": ("Sutta", "សុត្តន្តបិដក"), "abhidhamma": ("Abhidhamma", "អភិធម្មបិដក")}
Q_ANGER = ("How do I let go of anger?", "តើខ្ញុំអាចលះបង់សេចក្តីក្រោធដោយរបៀបណា?")
Q_PHONE = ("What does the Tipiṭaka say about smartphones?", "តើព្រះត្រៃបិដកនិយាយអ្វីខ្លះអំពីទូរសព្ទដៃ?")
EXAMPLES = [("What helps when someone I love dies?", "តើអ្វីជួយបាន នៅពេលមនុស្សជាទីស្រឡាញ់ស្លាប់?"),
            ("How should monks share their food?", "តើព្រះសង្ឃគួរចែករំលែកចង្ហាន់យ៉ាងដូចម្តេច?"),
            ("What is mindfulness of breathing?", "តើអានាបានស្សតិ ជាអ្វី?")]
RECENT = [(Q_ANGER, ("Today", "ថ្ងៃនេះ")), (("Is it wrong to eat meat?", "តើការបរិភោគសាច់ ខុសឬទេ?"), ("Yesterday", "ម្សិលមិញ"))]


# ── the walkthrough's wiring. build-walk.py sets WALK: the walkthrough is built from these SAME screens, so its words cannot
#    drift from the drawings'; with WALK off every hook is empty and the boards are byte for byte what they were.
WALK = False
WALK_GO = {Q_ANGER[0]: "S2", Q_PHONE[0]: "S4"}


def go(v):
    return ' data-go="%s"' % v if WALK else ""


def act(a, msg=None, copy=None):
    if not WALK:
        return ""
    return ' data-act="%s"%s%s' % (a, ' data-msg="%s"' % html.escape(msg) if msg else "", ' data-copy="%s"' % html.escape(copy) if copy else "")


def key(q):
    return ' data-key="%s"' % html.escape(q[0]) if WALK else ""


def stub(t):
    return act("stub", t("Not in this walkthrough: it shows one fixed example and searches nothing.",
                         "មិនមាននៅក្នុងការបង្ហាញនេះទេ៖ វាបង្ហាញឧទាហរណ៍ថេរមួយ ហើយមិនស្វែងរកអ្វីទេ។"))


def esc(s):
    return html.escape(s, quote=False)


def marked(text, sentence):
    """The page as typed, escaped, its highlighted sentence wrapped in <mark>. The sentence MUST be an exact substring."""
    e, s = esc(text), esc(sentence)
    assert e.count(s) >= 1, "a highlight must be an exact span of the typed page"
    return e.replace(s, "<mark>%s</mark>" % s, 1)


def where(t, p):
    b = BASKET[p["basket"]]
    return t("%s · Volume %d · page %s" % (b[0], p["volume"], ar_num(p["printed"])),
             "%s · ភាគ %s · ទំព័រ %s" % (b[1], km_num(p["volume"]), p["printed"]))


def spot(kind):
    d = {"page": '<rect class="sf" x="14" y="2" width="28" height="36" rx="3"/><path class="ss" d="M20 11h16M20 18h16M20 25h10"/>',
         "device": '<rect class="sf" x="18" y="3" width="20" height="34" rx="4"/><path class="ss" d="M24 14h8M24 20h8M24 26h5"/>',
         "none": '<rect class="sf" x="10" y="6" width="24" height="30" rx="3"/><path class="sk" d="M16 15h12M16 21h12M16 27h7"/><path class="ss" d="M38 10l8 8m0-8-8 8"/>',
         "hand": '<path class="sf" d="M14 6h28v28H14z"/><path class="ss" d="M20 14h16M20 20h16M20 26h9"/><circle class="sa" cx="44" cy="32" r="6"/>'}[kind]
    return '<svg class="spot" width="56" height="40" viewBox="0 0 56 40" aria-hidden="true">%s</svg>' % d


def card(sp, h, *ps):
    return '<div class="card">%s<h2>%s</h2>%s</div>' % (spot(sp) if sp else "", h, "".join("<p>%s</p>" % p for p in ps))


def askbox(t, q=None, desk=False):
    if WALK and q is None:   # a real input: typing explains the fixed example rather than pretending to search
        return ('<form class="askbox%s" data-act="find">%s<input class="q" id="ask" type="search" autocomplete="off" placeholder="%s" aria-label="%s">'
                '<button class="go" type="submit">%s</button></form><p class="stubline" hidden>%s</p>'
                % (" desk" if desk else "", SEARCH, t("Ask in your own words…", "សួរជាពាក្យរបស់អ្នកផ្ទាល់…"), t("Your question", "សំណួររបស់អ្នក"),
                   t("Find", "ស្វែងរក"), t("This walkthrough has two example questions: tap one below. The real finder will search whatever you ask.",
                                         "ការបង្ហាញនេះមានសំណួរឧទាហរណ៍ពីរ៖ សូមចុចមួយខាងក្រោម។ កម្មវិធីស្វែងរកពិតប្រាកដ នឹងស្វែងរកអ្វីក៏ដោយដែលអ្នកសួរ។")))
    text = ('<span class="q">%s</span>' % t(*q)) if q else ('<span class="ph">%s</span>' % t("Ask in your own words…", "សួរជាពាក្យរបស់អ្នកផ្ទាល់…"))
    return '<div class="askbox%s">%s%s<span class="go">%s</span></div>' % (" desk" if desk else "", SEARCH, text, t("Find", "ស្វែងរក"))


def examples(t):
    exs = ([Q_ANGER, Q_PHONE] + EXAMPLES) if WALK else EXAMPLES
    chip = lambda e: '<span class="chip"%s>%s</span>' % (go(WALK_GO[e[0]]) if e[0] in WALK_GO else stub(t), t(*e))
    return ('<p class="sh">%s</p><div class="chips">%s</div>' % (t("Examples", "ឧទាហរណ៍"), "".join(chip(e) for e in exs)))


def recent(t):
    rows = "".join('<li%s%s>%s<span class="rq">%s</span><span class="rw">%s</span></li>' % (
        key(q), go(WALK_GO[q[0]]) if q[0] in WALK_GO else stub(t), CLOCK, t(*q), t(*w)) for q, w in RECENT)
    return (('<div class="recentblock">' if WALK else "") + '<p class="sh">%s</p><ul class="recent">%s</ul><p class="fine" style="margin-top:4px">%s</p>'
            % (t("Your recent questions", "សំណួររបស់អ្នកថ្មីៗ"), rows, t("Kept only on this device.", "រក្សាទុកតែនៅលើឧបករណ៍នេះប៉ុណ្ណោះ។"))
            + ("</div>" if WALK else ""))


def explainer(t):
    still = ('<svg class="still" viewBox="0 0 320 150" aria-hidden="true">'
             '<rect class="sf" x="12" y="40" width="96" height="44" rx="14"/><path class="ss" d="M28 56h64M28 68h42"/>'
             '<path class="sk" d="M116 62h26m-8-8 8 8-8 8"/>'
             '<rect class="pp" x="152" y="14" width="66" height="92" rx="4" stroke="var(--line-strong)"/><rect class="pp" x="226" y="14" width="66" height="92" rx="4" stroke="var(--line-strong)"/>'
             '<path class="sk" d="M162 30h46M162 42h46M162 54h40M162 78h46M236 30h46M236 42h46M236 54h30M236 66h46M236 90h36"/>'
             '<rect class="hlbar" x="159" y="61" width="52" height="10" rx="3"/><path class="ss" d="M162 66h46"/>'
             '<text x="185" y="128" text-anchor="middle" class="stc">%s</text><text x="60" y="104" text-anchor="middle" class="stc">%s</text></svg>'
             % (t("the page, the line", "ទំព័រ និងបន្ទាត់"), t("your question", "សំណួររបស់អ្នក")))
    return ('<div class="explainer"><span class="tag">[ EXPLAINER · drawn with /motion later ]</span>%s<span class="play"%s>%s</span>'
            '<div class="xcap"><b>%s</b><span>%s</span></div></div>'
            % (still, act("stub", t("The explainer is still to be made. This is its first frame.", "វីដេអូពន្យល់ មិនទាន់បានធ្វើនៅឡើយទេ។ នេះជាស៊ុមដំបូងរបស់វា។")), PLAY,
               t("How the finder works", "របៀបដែលកម្មវិធីស្វែងរកដំណើរការ"),
               t("It plays when you tap it. The sound stays off until you turn it on.", "វាចាក់ នៅពេលអ្នកចុចលើវា។ សំឡេងនៅបិទ រហូតដល់អ្នកបើកវា។")))


def summary(t):
    chips = [t("Sutta 8", "សុត្តន្តបិដក ៨"), t("Vinaya 2", "វិន័យបិដក ២"), t("Abhidhamma 2", "អភិធម្មបិដក ២"), t("in 9 volumes", "ក្នុង ៩ ភាគ")]
    return ('<div class="sum"><b>%s</b><span class="chips">%s</span><span class="tag">[ illustrative counts ]</span></div>'
            % (t("12 passages", "អត្ថបទ ១២"), "".join('<span class="chip sm2">%s</span>' % c for c in chips)))


def result(t, p, dim=False):
    head = ('<div class="rh">%s</div>' % esc(p["heading"])) if p.get("heading") else ""
    return ('<div class="res%s"><div class="where">%s</div>%s<p class="said">%s</p><span class="open"%s>%s</span></div>'
            % (" dim2" if dim else "", where(t, p), head, "<mark>%s</mark>" % esc(p["sentence"]), go("page-%d" % P.index(p)), t("Open the page →", "បើកទំព័រ →")))


def typed(text, sentence):
    """A typed page as the finder shows it: its printed number centred, its paragraphs, the highlight kept."""
    lines = [l for l in text.split("\n") if l.strip()]
    first, rest = lines[0], "\n".join(lines[1:])
    body = marked(rest, sentence) if sentence and sentence in rest else esc(rest)
    paras = [x for x in body.split("\n") if x.strip()]
    return '<div class="typed"><div class="pn">%s</div>%s</div>' % (esc(first), "".join("<p>%s</p>" % x for x in paras))


# ── screens ────────────────────────────────────────────────────────────────────────────────────────────────────────
def S1(t):
    return ('<span class="tag">[ PLACEHOLDER ICON ]</span><h1>%s</h1><p class="lede">%s</p>' % (
        t("Find it in the Tipiṭaka", "ស្វែងរកក្នុងព្រះត្រៃបិដក"),
        t("Ask in your own words, in Khmer or English. You get the pages of the Khmer Tipiṭaka that may answer, with the lines highlighted.",
          "សួរជាពាក្យរបស់អ្នកផ្ទាល់ ជាភាសាខ្មែរ ឬអង់គ្លេស។ អ្នកនឹងឃើញទំព័រព្រះត្រៃបិដកខ្មែរ ដែលអាចឆ្លើយបាន ដោយមានបន្ទាត់ដែលបានគូសពណ៌។"))
        + askbox(t) + examples(t) + recent(t) + explainer(t))


def S2(t):
    return ('<div class="back"%s>%s<span>%s</span></div>' % (go("S1"), BACK, t("New question", "សំណួរថ្មី")) + askbox(t, Q_ANGER)
            + '<h1 class="h1s">%s</h1>' % t("Pages that may answer this", "ទំព័រដែលអាចឆ្លើយសំណួរនេះ") + summary(t)
            + "".join(result(t, p) for p in P)
            + '<p class="fine">%s</p>' % t("Every word here is the Tipiṭaka as typed. The finder writes nothing of its own.",
                                           "ពាក្យទាំងអស់នៅទីនេះ គឺជាព្រះត្រៃបិដក ដូចដែលបានវាយ។ កម្មវិធីស្វែងរក មិនសរសេរអ្វីដោយខ្លួនឯងទេ។"))


def cite(t, p):
    return t("The Buddhist Institute edition of the Tipiṭaka (Phnom Penh, 1927–69), volume %d, page %s. Typed by Se Mong Ly." % (p["volume"], ar_num(p["printed"])),
             "ព្រះត្រៃបិដក បោះពុម្ពរបស់ពុទ្ធសាសនបណ្ឌិត្យ (ភ្នំពេញ ១៩២៧–១៩៦៩) ភាគ %s ទំព័រ %s។ វាយដោយ លី ម៉ុង សែ។" % (km_num(p["volume"]), p["printed"]))


def tools(t, p=None):
    p = p or P[0]
    return ('<div class="tools">%s</div>' % "".join('<span class="tool"%s>%s%s</span>' % x for x in (
        (act("copy", t("Citation copied", "បានចម្លងឯកសារយោង"), cite(t, p)), COPY, t("Copy the citation", "ចម្លងឯកសារយោង")),
        (act("stub", t("Listen reads a passage you select aloud. Not in this walkthrough.", "ស្តាប់ អានអត្ថបទដែលអ្នកជ្រើសឲ្យឮ។ មិនមាននៅក្នុងការបង្ហាញនេះទេ។")), SPEAK, t("Listen", "ស្តាប់")),
        (go("ask-%d" % P.index(p)), ASK, t("Ask an AI", "សួរ AI")),
        (act("share", t("Link copied", "បានចម្លងតំណ")), SHARE, t("Share the page", "ចែករំលែកទំព័រ")))))


def pageview(t, p, leaf="khmer"):
    text = p[leaf] if p.get(leaf) else p["khmer"]
    i = P.index(p)
    # a switch only where the facing leaf is typed: the page shows what IS, never a leaf that is missing
    seg = ('<span class="seg lf"><span%s%s>%s</span><span%s%s>%s</span></span>' % (
        ' class="on"' if leaf == "khmer" else "", go("page-%d" % i), t("Khmer", "ខ្មែរ"), ' class="on"' if leaf == "pali" else "", go("pali-%d" % i), t("Pāli", "បាលី"))
           if p.get("pali") else "")
    return ('<div class="where big">%s</div><div class="leafrow"><span class="k">%s</span>%s</div>' % (where(t, p), t("This opening", "ទំព័របើកនេះ"), seg)
            + typed(text, p["sentence"] if leaf == "khmer" else None)
            + '<p class="cite">%s</p>' % cite(t, p))


def S3(t, p=None):
    p = p or P[0]
    return ('<div class="back"%s>%s<span>%s</span></div>' % (go("S2"), BACK, t("Back to the results", "ត្រឡប់ទៅលទ្ធផល")) + pageview(t, p) + tools(t, p)
            + '<p class="fine">%s</p>' % t("Tap a word for its meaning in Samdech Chuon Nath's dictionary.", "ចុចលើពាក្យមួយ ដើម្បីមើលន័យក្នុងវចនានុក្រមសម្តេចព្រះសង្ឃរាជ ជួន ណាត។"))


def S3p(t, p=None):
    p = p or P[0]
    return ('<div class="back"%s>%s<span>%s</span></div>' % (go("S2"), BACK, t("Back to the results", "ត្រឡប់ទៅលទ្ធផល")) + pageview(t, p, "pali") + tools(t, p)
            + '<p class="fine">%s</p>' % t("The facing page: the Pāli, in Khmer script, as the edition prints it beside the Khmer.",
                                           "ទំព័រទល់មុខ៖ បាលី ជាអក្សរខ្មែរ ដូចការបោះពុម្ព ដាក់ក្បែរភាសាខ្មែរ។"))


def S4(t):
    return ('<div class="back"%s>%s<span>%s</span></div>' % (go("S1"), BACK, t("New question", "សំណួរថ្មី")) + askbox(t, Q_PHONE)
            + '<div class="nomatch">%s<div><h1 class="h1s">%s</h1><p class="lede">%s</p></div></div>' % (spot("none"),
                t("No page matches this closely", "គ្មានទំព័រណាត្រូវនឹងសំណួរនេះយ៉ាងជិតស្និទ្ធទេ"),
                t("These are the closest. Other words may find more.", "ទាំងនេះគឺជិតជាងគេ។ ពាក្យផ្សេងទៀត អាចរកឃើញច្រើនជាងនេះ។"))
            + result(t, P[1], dim=True) + result(t, P[3], dim=True)
            + '<div class="btnrow"><div class="btn ghost"%s>%s</div><div class="btn ghost"%s>%s%s</div></div>' % (go("S1"), t("Try other words", "សាកពាក្យផ្សេង"), go("ask-phone"), ASK, t("Ask an AI", "សួរ AI")))


def S5(t):
    rows = [(Q_ANGER, ("Today", "ថ្ងៃនេះ")), (("Is it wrong to eat meat?", "តើការបរិភោគសាច់ ខុសឬទេ?"), ("Yesterday", "ម្សិលមិញ")),
            (EXAMPLES[2], ("20 November", "២០ វិច្ឆិកា")), (EXAMPLES[0], ("18 November", "១៨ វិច្ឆិកា"))]
    lis = "".join('<li%s><div><span class="rq">%s</span><span class="rw">%s</span></div><span class="del" aria-label="%s"%s>%s</span></li>'
                  % (key(q), t(*q), t(*w), t("Delete", "លុប"), act("del", t("Deleted", "បានលុប")), TRASH) for q, w in rows)
    return ('<h1>%s</h1>' % t("Your questions", "សំណួររបស់អ្នក")
            + '<div class="note" style="display:flex;gap:10px;align-items:flex-start">%s<span>%s</span></div>' % (DEVICE,
                t("Kept only on this device. Nothing is sent anywhere, and no account is needed.", "រក្សាទុកតែនៅលើឧបករណ៍នេះ។ គ្មានអ្វីត្រូវបានផ្ញើទៅកន្លែងណាទេ ហើយមិនត្រូវការគណនីទេ។"))
            + '<ul class="hist">%s</ul>' % lis
            + '<div class="btnrow"><div class="btn ghost"%s>%s%s</div><div class="btn ghost"%s>%s</div></div>' % (
                act("save", t("Saved as a file", "បានរក្សាទុកជាឯកសារ")), DOWN, t("Save as a file", "រក្សាទុកជាឯកសារ"), act("delall"), t("Delete all", "លុបទាំងអស់"))
            + (('<div class="confirm" hidden><p>%s</p><div class="btnrow"><div class="btn"%s>%s</div><div class="btn ghost"%s>%s</div></div></div>'
                '<p class="empty" hidden>%s</p>') % (t("Delete all your questions from this device?", "លុបសំណួរទាំងអស់របស់អ្នក ពីឧបករណ៍នេះ?"),
                act("delall-yes", t("Deleted", "បានលុប")), t("Delete all", "លុបទាំងអស់"), act("delall-no"), t("Keep them", "រក្សាទុកវា"),
                t("No questions kept on this device.", "គ្មានសំណួរដែលរក្សាទុកនៅលើឧបករណ៍នេះទេ។")) if WALK else "")
            + '<p class="fine">%s</p>' % t("Safari may clear this after a week without a visit, unless the site is on your Home Screen. A saved file keeps it.",
                                           "Safari អាចលុបវា បន្ទាប់ពីមួយសប្តាហ៍ដែលមិនបានចូលមើល លុះត្រាតែគេហទំព័រនៅលើអេក្រង់ដើមរបស់អ្នក។ ឯកសារដែលបានរក្សាទុក រក្សាវាបាន។"))


def S6(t, p=None, q=None, back=None):
    p, q = p or P[0], q or Q_ANGER
    opt = '<div class="radio%s"%s><i></i><div><div class="t">%s</div><div class="s">%s</div></div></div>'
    copied = "%s\n\n%s\n\n%s" % (p["sentence"].replace("\u200b", ""), cite(t, p), t(*q))
    return (pageview(t, p) + '<div class="scrim"%s></div>' % go(back or "page-%d" % P.index(p))
            + '<div class="sheet" style="margin-top:-260px"><div class="grab"></div><h2>%s</h2><div class="quote">%s</div>'
            % (t("Ask an AI about this passage", "សួរ AI អំពីអត្ថបទនេះ"), esc(p["sentence"]))
            + '<div class="field area"><span class="k">%s</span>%s</div>' % (t("Your question", "សំណួររបស់អ្នក"), t(*q))
            + '<p class="sh">%s</p><div class="card">%s%s%s</div>' % (t("Ask in", "សួរនៅ"),
                opt % (" on", act("radio"), t("Just copy it", "ចម្លងប៉ុណ្ណោះ"), t("The passage, its place and your question, ready to paste anywhere", "អត្ថបទ ទីតាំងរបស់វា និងសំណួររបស់អ្នក រួចរាល់សម្រាប់បិទភ្ជាប់គ្រប់ទីកន្លែង")),
                opt % ("", act("radio"), "[ Assistant name ]", t("Copied, then it opens in a new tab", "ចម្លង រួចបើកក្នុងផ្ទាំងថ្មី")),
                opt % ("", act("radio"), "[ Assistant name ]", t("Copied, then it opens in a new tab", "ចម្លង រួចបើកក្នុងផ្ទាំងថ្មី")))
            + '<div class="note">%s</div>' % t("AI assistants may assume a different edition's wording, and may be wrong. Check what it says against the page.",
                                               "ជំនួយការ AI អាចសន្មតយកពាក្យពេចន៍នៃការបោះពុម្ពផ្សេង ហើយអាចខុស។ សូមផ្ទៀងផ្ទាត់អ្វីដែលវានិយាយ ជាមួយទំព័រនេះ។")
            + '<div class="btn"%s>%s%s</div><p class="fine">%s</p></div>' % (act("copy", t("Copied. Paste it where you like.", "បានចម្លង។ បិទភ្ជាប់វានៅកន្លែងដែលអ្នកចង់បាន។"), copied),
                COPY, t("Copy", "ចម្លង"), t("Nothing leaves this page until you press.", "គ្មានអ្វីចេញពីទំព័រនេះទេ រហូតដល់អ្នកចុច។")))


CREDITS = [(("The text", "អត្ថបទ"), ("The Buddhist Institute edition of the Tipiṭaka (Phnom Penh, 1927–69)", "ព្រះត្រៃបិដក បោះពុម្ពរបស់ពុទ្ធសាសនបណ្ឌិត្យ (ភ្នំពេញ ១៩២៧–១៩៦៩)")),
           (("The typing", "ការវាយ"), ("Se Mong Ly (លី ម៉ុង សែ), given to everyone (CC0)", "លី ម៉ុង សែ ជាអំណោយដល់មនុស្សគ្រប់គ្នា (CC0)")),
           (("Made by", "បង្កើតដោយ"), ("Silicon Wat ℠, with Miss Aquarius ℠ (AI collaboration, disclosed)", "Silicon Wat ℠ ជាមួយ Miss Aquarius ℠ (ការសហការជាមួយ AI ដែលបានបង្ហាញ)"))]


def S7(t):
    return ('<h1>%s</h1>' % t("About the finder", "អំពីកម្មវិធីស្វែងរក")
            + '<div class="iconrow">%s<span class="tag">[ PLACEHOLDER ICON ] Silicon Wat\'s own mark is not settled</span></div>' % icon_svg(ACCENT, 40, "ico")
            + card("page", t("What it does", "អ្វីដែលវាធ្វើ"),
                   t("You ask in your own words, in Khmer or English. It shows the typed pages of the Khmer Tipiṭaka that may answer, with the lines highlighted, and where each one is: basket, volume and page.",
                     "អ្នកសួរជាពាក្យរបស់អ្នកផ្ទាល់ ជាភាសាខ្មែរ ឬអង់គ្លេស។ វាបង្ហាញទំព័រព្រះត្រៃបិដកខ្មែរដែលបានវាយ ដែលអាចឆ្លើយបាន ដោយមានបន្ទាត់ដែលបានគូសពណ៌ និងទីតាំងរបស់ទំព័រនីមួយៗ៖ បិដក ភាគ និងទំព័រ។"))
            + card("none", t("What it does not do", "អ្វីដែលវាមិនធ្វើ"),
                   t("It writes no answers and no summaries. Every word on a result is the Tipiṭaka as typed. To talk a passage over, Ask an AI copies it for you, and you choose where.",
                     "វាមិនសរសេរចម្លើយ ឬសេចក្តីសង្ខេបទេ។ ពាក្យទាំងអស់នៅលើលទ្ធផល គឺជាព្រះត្រៃបិដក ដូចដែលបានវាយ។ ដើម្បីពិភាក្សាអំពីអត្ថបទមួយ មុខងារ សួរ AI ចម្លងវាជូនអ្នក ហើយអ្នកជ្រើសរើសកន្លែង។"))
            + card("hand", t("How everyday words find a page", "របៀបដែលពាក្យប្រចាំថ្ងៃរកឃើញទំព័រ"),
                   t("Behind the search, a computer wrote down once, in Khmer and English, the questions each page may answer, so that a question in everyday words can find it. Those questions are never shown on the site.",
                     "នៅពីក្រោយការស្វែងរក កុំព្យូទ័របានសរសេរម្តង ជាភាសាខ្មែរ និងអង់គ្លេស នូវសំណួរដែលទំព័រនីមួយៗអាចឆ្លើយបាន ដើម្បីឲ្យសំណួរជាពាក្យប្រចាំថ្ងៃអាចរកឃើញវា។ សំណួរទាំងនោះ មិនដែលបង្ហាញនៅលើគេហទំព័រទេ។"))
            + card("device", t("Your privacy", "ឯកជនភាពរបស់អ្នក"),
                   t("Your question is searched on this device, and your questions are kept only on it. Visits are counted without cookies, and the count never sees a question.",
                     "សំណួររបស់អ្នក ត្រូវបានស្វែងរកនៅលើឧបករណ៍នេះ ហើយសំណួររបស់អ្នក រក្សាទុកតែនៅលើវាប៉ុណ្ណោះ។ ការចូលមើលត្រូវបានរាប់ដោយគ្មានខូគី ហើយការរាប់នោះ មិនដែលឃើញសំណួរទេ។"))
            + '<div class="note">%s</div>' % t("So far 36,211 Khmer pages and 13,921 Pāli pages of the edition are typed. The typing continues.",
                                               "រហូតមកដល់ពេលនេះ ទំព័រខ្មែរ ៣៦.២១១ និងទំព័របាលី ១៣.៩២១ នៃការបោះពុម្ពនេះ ត្រូវបានវាយរួច។ ការវាយនៅបន្ត។")
            + '<p class="sh">%s</p><div class="card"><ul class="cr">%s</ul></div>' % (t("Credits", "ការទទួលស្គាល់"),
                "".join("<li><b>%s</b>%s</li>" % (t(*a), t(*b)) for a, b in CREDITS))
            + '<div class="card" style="text-align:center"><div class="pali">សព្វទានំ ធម្មទានំ ជិនាតិ</div><p>%s</p></div>'
            % t("The gift of the Dhamma surpasses every gift. Dhammapada 354", "ធម្មទាន ឈ្នះទានទាំងពួង។ ធម្មបទ ៣៥៤"))


def S8(t):
    """An address that opens no typed page (2026-11-27). It names the address, never the reader; how much is typed is said once,
    on About, never per page (SPEC), so this board points there instead of saying it again."""
    return ('<div class="back"%s>%s<span>%s</span></div>' % (go("S1"), BACK, t("New question", "សំណួរថ្មី"))
            + '<div class="nomatch">%s<div><h1 class="h1s">%s</h1><p class="lede">%s</p></div></div>' % (spot("none"),
                t("No typed page at this address", "គ្មានទំព័រដែលបានវាយ នៅអាសយដ្ឋាននេះទេ"),
                t("About says how much of the edition is typed so far.", "ទំព័រអំពី ប្រាប់ថា ការបោះពុម្ពនេះ ត្រូវបានវាយរួចប៉ុណ្ណាហើយ។"))
            + '<div class="btnrow"><div class="btn ghost"%s>%s</div><div class="btn ghost"%s>%s</div></div>' % (go("S1"), t("New question", "សំណួរថ្មី"), go("S7"), t("About", "អំពី")))


# ── desktop, English only ──────────────────────────────────────────────────────────────────────────────────────────
def D1(t):
    return ('<span class="tag">[ PLACEHOLDER ICON ]</span><div class="cols"><div><h1>%s</h1><p class="lede" style="font-size:17px">%s</p>%s%s%s</div><div style="margin-top:22px">%s%s</div></div>'
            % (t("Find it in the Tipiṭaka", ""), t("Ask in your own words, in Khmer or English. You get the pages of the Khmer Tipiṭaka that may answer, with the lines highlighted.", ""),
               askbox(t, desk=True), examples(t), recent(t), explainer(t),
               card("none", t("It writes no answers", "វាមិនសរសេរចម្លើយទេ"), t("Every word on a result is the Tipiṭaka as typed.", "ពាក្យទាំងអស់នៅលើលទ្ធផល គឺជាព្រះត្រៃបិដក ដូចដែលបានវាយ។"))))


def D2(t):
    return ('%s<div class="cols"><div><h1 class="h1s">%s</h1>%s%s</div><div style="margin-top:14px">%s%s</div></div>'
            % (askbox(t, Q_ANGER, desk=True), t("Pages that may answer this", ""), summary(t), "".join(result(t, p) for p in P[:3]),
               pageview(t, P[0]), tools(t)))


SCREENS = [("1", "The finder", S1), ("2", "Results", S2), ("3", "A page, Khmer", S3), ("3p", "A page, the facing Pāli", S3p),
           ("4", "No close match", S4), ("5", "Your questions (this device)", S5), ("6", "Ask an AI", S6), ("7", "About the finder", S7),
           ("8", "An address with no typed page", S8)]
NOFOOT = {"6"}


def page(sid, render, lang, dark=False, desk=False):
    km = lang == "km"
    t = (lambda e, k: k) if km else (lambda e, k: e)
    body = check(sid, lang, render(t).replace("℠", '<span class="sm">℠</span>'))
    return frame(sid, lang, body, t, km, dark, desk)


def check(sid, lang, body):
    """The build's refusals, run on every board AND on every walkthrough view (build-walk.py)."""
    km = lang == "km"
    plain = re.sub(r"<[^>]+>", " ", body)
    for pat in BARRED + ([r"ធនាគារ"] if km else []):
        assert not re.search(pat, plain, re.I), "%s/%s: barred %r" % (sid, lang, pat)
    if sid != "7":
        assert not re.search(r"\d\s*%|[០-៩]\s*%", plain), "%s/%s: a percentage outside About (a progress figure?)" % (sid, lang)
    assert EMBLEM_SIG not in body, "%s: the B-Emblem path is in a Silicon Wat board" % sid
    for p in P:   # every highlight shown is an exact span of its typed page
        for m in re.findall(r"<mark>(.*?)</mark>", body, re.S):
            assert any(html.unescape(m) in q["khmer"] for q in P), "%s: a highlight that is not on any typed page" % sid
    return body


def frame(sid, lang, body, t, km, dark, desk):
    band = ("Khmer: our draft, not yet reviewed · ភាសាខ្មែរ៖ សេចក្តីព្រាងរបស់យើង មិនទាន់បានពិនិត្យ" if km else "")
    themes = "".join('<span%s>%s</span>' % (' class="on"' if i == (2 if dark else 0) else "", x) for i, x in enumerate(t(("System", "Light", "Dark"), ("ប្រព័ន្ធ", "ភ្លឺ", "ងងឹត"))))
    langs = "".join('<span%s>%s</span>' % (' class="on"' if (i == 0) == (not km) else "", x) for i, x in enumerate(("EN", "ខ្មែរ")))
    foot = '<footer><span><a>%s</a> · <a>%s</a> · %s</span><span class="seg">%s</span></footer>' % (
        t("About", "អំពី"), t("Your questions", "សំណួររបស់អ្នក"), t("Visits are counted without cookies.", "ការចូលមើលត្រូវបានរាប់ដោយគ្មានខូគី។"), themes)
    share = '<span class="sharebtn" aria-label="%s">%s</span>' % (t("Share", "ចែករំលែក"), SHARE)
    cls = " ".join(c for c in (lang, "dark" if dark else "", "desk" if desk else "") if c)
    return """<!doctype html>
<html lang="%s" class="%s">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=%d">
<meta name="googlebot" content="noindex,nofollow"><meta name="bingbot" content="noindex,nofollow">
<meta name="slurp" content="noindex,nofollow"><meta name="yandex" content="noindex,nofollow">
<title>siliconwat.com drawings · %s</title>
<link rel="icon" type="image/svg+xml" href="favicon.svg">
<style>[hidden]{display:none!important}</style>
%s
<link rel="stylesheet" href="board.css?v=@CSSV@">
</head>
<body>
%s<div class="app">
<header><span class="hl">%s<span class="wm">siliconwat.com</span></span><span class="hr"><span class="seg">%s</span>%s</span></header>
%s
%s
</div>
</body>
</html>
""" % (lang, cls, DW if desk else W, sid, FONTS, '<div class="band">%s</div>' % band if band else "", icon_svg(ACCENT, 26), langs, share, body,
       "" if sid in NOFOOT else '<div class="grow"></div>' + foot)


def main():
    css = fill(CSS)
    io.open(os.path.join(HERE, "board.css"), "w", encoding="utf-8").write(css)
    cssv = hashlib.sha256(css.encode()).hexdigest()[:8]
    hpath = os.path.join(HERE, "heights.json")
    hts = json.load(io.open(hpath)) if os.path.exists(hpath) else {}
    hh = lambda f, base=H: max(base, int(hts.get(f, base)))
    tall = lambda sfx: max([H] + [int(v) for k, v in hts.items() if k.endswith(sfx) and not k.startswith("D")])
    pages = [{"id": "finder", "name": "siliconwat.com · the finder"}]
    boards = []
    y_km = tall(".html") + 160
    for i, (sid, title, render) in enumerate(SCREENS):
        for lang, y in (("en", 0), ("km", y_km)):
            f = "S%s%s.html" % (sid, "" if lang == "en" else "Km")
            io.open(os.path.join(HERE, f), "w", encoding="utf-8").write(page(sid, render, lang).replace("@CSSV@", cssv))
            boards.append({"file": f, "page": "finder", "title": "%s · %s, %s, phone" % (sid, title, "English" if lang == "en" else "Khmer"),
                           "w": W, "h": hh(f), "x": i * (W + 80), "y": y})
    y3 = y_km + max([H] + [int(v) for k, v in hts.items() if k.endswith("Km.html")]) + 160
    x = 0
    for f, sid, render, title, dark, desk in (("D1.html", "1", D1, "1 · The finder, English, desktop", False, True),
                                               ("D2.html", "2", D2, "2 · Results beside the page, English, desktop", False, True),
                                               ("S1Dark.html", "1", S1, "1 · The finder, dark pass, English, phone", True, False),
                                               ("S2Dark.html", "2", S2, "2 · Results, dark pass, English, phone", True, False)):
        io.open(os.path.join(HERE, f), "w", encoding="utf-8").write(page(sid, render, "en", dark=dark, desk=desk).replace("@CSSV@", cssv))
        w = DW if desk else W
        boards.append({"file": f, "page": "finder", "title": title, "w": w, "h": hh(f, DH if desk else H), "x": x, "y": y3})
        x += w + 80
    canvas = {"pages": pages, "artboards": boards, "annotations": [], "launch": {"page": "finder", "view": "canvas"}}
    io.open(os.path.join(HERE, "canvas.json"), "w", encoding="utf-8").write(json.dumps(canvas, ensure_ascii=False, indent=1))
    print("%d artboards written · board.css v=%s" % (len(boards), cssv))


if __name__ == "__main__":
    main()
