#!/usr/bin/env python3
"""Generate finder.html: the walkthrough (/build phase 3), one page a person can drive on a phone.

    python3 build-walk.py          # after build-boards.py; build-index.py links it as "Start here"

⛔ It is built from the SAME screen functions as the drawings (build-boards.py, its WALK hooks on), so the words cannot drift.
⛔ It searches NOTHING (founder 2026-11-25/26): one fixed example (anger) and one no-close-match example (smartphones), with the
   real passages as typed; anything else typed says so in one plain line. A working finder is not shown to the test's writers
   before the freeze (SW/siliconwat.com/siliconwat.com/eval/known-answer/PREREG.md).
⛔ It owns its head (charset, viewport, the [hidden] rule): a page served raw gets no skeleton to lean on (/build phase 2).
The build refuses: a data-go with no view to go to, a view missing in either language, the boards' own refusals on every view,
unbalanced divs, and a script that does not parse (node --check).
"""
import hashlib, html, importlib.util, io, os, re, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("bb", os.path.join(HERE, "build-boards.py"))
bb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bb)
bb.WALK = True
P = bb.P

VIEWS = ([("S1", bb.S1), ("S2", bb.S2)]
         + [("page-%d" % i, (lambda t, p=p: bb.S3(t, p))) for i, p in enumerate(P)]
         + [("pali-%d" % i, (lambda t, p=p: bb.S3p(t, p))) for i, p in enumerate(P) if p.get("pali")]
         + [("S4", bb.S4), ("S5", bb.S5)]
         + [("ask-%d" % i, (lambda t, p=p: bb.S6(t, p))) for i, p in enumerate(P)]
         + [("ask-phone", lambda t: bb.S6(t, P[1], bb.Q_PHONE, back="S4")), ("S7", bb.S7)])

WALK_CSS = """
html.walk body{width:auto;max-width:440px;min-height:100dvh;margin:0 auto}
@media (min-width:600px){html.walk body{margin:28px auto;min-height:0;border:1px solid var(--line);border-radius:28px;overflow:clip}}
html.walk .app{min-height:auto;padding-left:max(20px,env(safe-area-inset-left,0px));padding-right:max(20px,env(safe-area-inset-right,0px))}
html.walk .band{padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
[data-go],[data-act]:not(form){cursor:pointer}
.recent li[data-go]:hover .rq,.open[data-go]:hover,.back[data-go]:hover{text-decoration:underline;text-underline-offset:3px}
.askbox input{flex:1;min-width:0;border:0;background:transparent;font:500 16px var(--font-text);color:var(--ink);outline:none;padding:0}
.km .askbox input{font-family:var(--font-text),var(--font-khmer)}
.askbox input::placeholder{color:var(--ink-faint)}
.askbox button.go{border:0;cursor:pointer;font-family:inherit}
.stubline{font-size:13.5px;color:var(--ink-dim);background:var(--wash);border-radius:12px;padding:9px 12px;margin:8px 0 0}
.confirm{border:1px solid var(--line-strong);border-radius:var(--r);padding:12px 14px;margin-top:12px}
.confirm p{margin:0;font-weight:600}
.empty{color:var(--ink-dim);padding:12px 0}
.radio[data-act]{cursor:pointer}
footer .seg span[data-act],header .seg span[data-act]{cursor:pointer}
#toast{position:fixed;left:50%;bottom:calc(20px + env(safe-area-inset-bottom,0px));transform:translateX(-50%);z-index:30;
  background:var(--ink);color:var(--bg);padding:10px 16px;border-radius:12px;font-size:14px;max-width:calc(100% - 32px);box-shadow:0 8px 24px rgba(0,0,0,.2)}
:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
"""

JS = r"""
(function () {
  var H = document.documentElement, LK = "finder-walk:lang", TK = "finder-walk:theme";
  var FAIL = { en: "Copy did not work in this browser. Select the text instead.", km: "ការចម្លងមិនដំណើរការក្នុងកម្មវិធីរុករកនេះទេ។ សូមជ្រើសអត្ថបទជំនួសវិញ។" };
  var store = { get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
                set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} } };
  var lang = store.get(LK);
  if (lang !== "en" && lang !== "km") {
    lang = (navigator.languages || [navigator.language]).some(function (l) { return /^km\b/i.test(l || ""); }) ? "km" : "en";
    if (lang === "en") { try { if (Intl.DateTimeFormat().resolvedOptions().timeZone === "Asia/Phnom_Penh") lang = "km"; } catch (e) {} }
  }
  var theme = store.get(TK) || "auto";
  var view = location.hash.slice(1) || "S1";
  var exists = function (v) { return !!document.querySelector('section.v[data-v="' + v + '"]'); };
  if (!exists(view)) view = "S1";
  var toast = document.getElementById("toast"), tt = null;
  function say(m) { if (!m) return; toast.textContent = m; toast.hidden = false; clearTimeout(tt); tt = setTimeout(function () { toast.hidden = true; }, 2600); }
  function applyTheme() {
    var dark = theme === "dark" || (theme === "auto" && window.matchMedia && matchMedia("(prefers-color-scheme: dark)").matches);
    H.classList.toggle("dark", dark);
    document.querySelectorAll('[data-act^="theme-"]').forEach(function (b) { b.classList.toggle("on", b.getAttribute("data-act") === "theme-" + theme); });
  }
  function show(top) {
    H.lang = lang; H.classList.toggle("km", lang === "km"); H.classList.toggle("en", lang === "en");
    document.querySelectorAll("section.v").forEach(function (s) { s.hidden = !(s.getAttribute("data-v") === view && s.getAttribute("data-lang") === lang); });
    document.querySelectorAll("[data-lang-only]").forEach(function (b) { b.hidden = b.getAttribute("data-lang-only") !== lang; });
    document.querySelectorAll('[data-act^="lang-"]').forEach(function (b) { b.classList.toggle("on", b.getAttribute("data-act") === "lang-" + lang); });
    if (location.hash.slice(1) !== view) history.replaceState(null, "", "#" + view);
    if (top) window.scrollTo(0, 0);
  }
  function current() { return document.querySelector("section.v:not([hidden])"); }
  function copy(text, done) {
    var fallback = function () {
      var ta = document.createElement("textarea"); ta.value = text; ta.setAttribute("readonly", ""); ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select(); var ok = false; try { ok = document.execCommand("copy"); } catch (e) {} ta.remove(); done(ok);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(function () { done(true); }, fallback); else fallback();
  }
  function refresh() {
    document.querySelectorAll("section.v").forEach(function (s) {
      var e = s.querySelector(".empty"); if (e) e.hidden = !!s.querySelector(".hist li");
      var rb = s.querySelector(".recentblock"); if (rb) rb.hidden = !rb.querySelector("li");
    });
  }
  function confirmShown(on) { document.querySelectorAll(".confirm").forEach(function (c) { c.hidden = !on; }); }
  document.addEventListener("click", function (ev) {
    var g = ev.target.closest("[data-go]");
    if (g) { ev.preventDefault(); view = g.getAttribute("data-go"); show(true); return; }
    var a = ev.target.closest("[data-act]"); if (!a || a.tagName === "FORM") return;
    var k = a.getAttribute("data-act"), msg = (lang === "km" && a.getAttribute("data-msg-km")) || a.getAttribute("data-msg");
    if (k.indexOf("lang-") === 0) { lang = k.slice(5); store.set(LK, lang); show(false); return; }
    if (k.indexOf("theme-") === 0) { theme = k.slice(6); store.set(TK, theme); applyTheme(); return; }
    if (k === "stub") { say(msg); return; }
    if (k === "copy") { copy(a.getAttribute("data-copy"), function (ok) { say(ok ? msg : FAIL[lang]); }); return; }
    if (k === "share") {
      var url = location.href;
      if (navigator.share) { navigator.share({ title: document.title, url: url }).catch(function () {}); return; }
      copy(url, function (ok) { if (ok) say(msg); }); return;
    }
    if (k === "radio") { var box = a.parentNode; box.querySelectorAll(".radio").forEach(function (r) { r.classList.toggle("on", r === a); }); return; }
    if (k === "del") {
      var li = a.closest("li"), key = li && li.getAttribute("data-key");
      document.querySelectorAll("li[data-key]").forEach(function (x) { if (x.getAttribute("data-key") === key) x.remove(); });
      refresh(); say(msg); return;
    }
    if (k === "delall") { confirmShown(true); return; }
    if (k === "delall-no") { confirmShown(false); return; }
    if (k === "delall-yes") { document.querySelectorAll("li[data-key]").forEach(function (x) { x.remove(); }); confirmShown(false); refresh(); say(msg); return; }
    if (k === "save") {
      var qs = []; var s = current(); if (s) s.querySelectorAll(".hist .rq").forEach(function (q) { qs.push(q.textContent); });
      var blob = new Blob([qs.join("\n") + "\n"], { type: "text/plain;charset=utf-8" }), u = URL.createObjectURL(blob), link = document.createElement("a");
      link.href = u; link.download = "my-questions.txt"; document.body.appendChild(link); link.click(); link.remove();
      setTimeout(function () { URL.revokeObjectURL(u); }, 1000); say(msg); return;
    }
  });
  document.addEventListener("submit", function (ev) {
    var f = ev.target.closest('form[data-act="find"]'); if (!f) return; ev.preventDefault();
    var line = f.nextElementSibling; if (line && line.classList.contains("stubline")) line.hidden = false;
  });
  window.addEventListener("hashchange", function () { var v = location.hash.slice(1); if (exists(v) && v !== view) { view = v; show(true); } });
  if (window.matchMedia) { try { matchMedia("(prefers-color-scheme: dark)").addEventListener("change", applyTheme); } catch (e) {} }
  applyTheme(); refresh(); show(false);
})();
"""


def main():
    css = io.open(os.path.join(HERE, "board.css"), encoding="utf-8").read()
    cssv = hashlib.sha256(css.encode()).hexdigest()[:8]
    sections, ids = [], set()
    for lang in ("en", "km"):
        t = (lambda e, k: k) if lang == "km" else (lambda e, k: e)
        for vid, render in VIEWS:
            body = bb.check(vid, lang, render(t).replace("℠", '<span class="sm">℠</span>'))
            sections.append('<section class="v" data-v="%s" data-lang="%s"%s>\n%s\n</section>' % (vid, lang, "" if (vid, lang) == ("S1", "en") else " hidden", body))
            ids.add((vid, lang))
    page_body = "\n".join(sections)
    # every data-go names a view that exists, in both languages
    for target in set(re.findall(r'data-go="([^"]+)"', page_body)):
        assert (target, "en") in ids and (target, "km") in ids, "data-go to a missing view: %s" % target
    for vid, _ in VIEWS:
        assert (vid, "en") in ids and (vid, "km") in ids, vid
    t_en, t_km = (lambda e, k: e), (lambda e, k: k)
    seg = lambda t, cls: "".join('<span data-act="%s-%s">%s</span>' % (cls, v, x) for v, x in v_pairs(t, cls))
    def v_pairs(t, cls):
        return [("en", "EN"), ("km", "ខ្មែរ")] if cls == "lang" else list(zip(("auto", "light", "dark"), t(("System", "Light", "Dark"), ("ប្រព័ន្ធ", "ភ្លឺ", "ងងឹត"))))
    def foot(t, lang):
        return ('<footer data-lang-only="%s"%s><span><a data-go="S7">%s</a> · <a data-go="S5">%s</a> · %s</span><span class="seg">%s</span></footer>'
                % (lang, "" if lang == "en" else " hidden", t("About", "អំពី"), t("Your questions", "សំណួររបស់អ្នក"),
                   t("A walkthrough: it searches nothing and charges nothing. Visits are counted without cookies.",
                     "ការបង្ហាញ៖ វាមិនស្វែងរកអ្វី ហើយមិនគិតថ្លៃអ្វីទេ។ ការចូលមើលត្រូវបានរាប់ដោយគ្មានខូគី។"), seg(t, "theme")))
    band = ('<div class="band" data-lang-only="en">A walkthrough with one fixed example. It searches nothing and charges nothing.</div>'
            '<div class="band" data-lang-only="km" hidden>ការបង្ហាញដោយឧទាហរណ៍ថេរមួយ។ វាមិនស្វែងរកអ្វី ហើយមិនគិតថ្លៃអ្វីទេ។ · ភាសាខ្មែរ៖ សេចក្តីព្រាងរបស់យើង មិនទាន់បានពិនិត្យ</div>')
    desc = "Try the finder for the Khmer Tipiṭaka: ask, see the typed pages that may answer, open one. A walkthrough with one fixed example, in English and Khmer."
    doc = """<!doctype html>
<html lang="en" class="walk en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="googlebot" content="noindex,nofollow"><meta name="bingbot" content="noindex,nofollow">
<meta name="slurp" content="noindex,nofollow"><meta name="yandex" content="noindex,nofollow">
<title>The finder, a walkthrough · siliconwat.com</title>
<meta name="description" content="%(desc)s">
<meta property="og:type" content="website">
<meta property="og:url" content="https://demo.siliconwat.com/finder.html">
<meta property="og:site_name" content="siliconwat.com: drawings">
<meta property="og:title" content="The finder: a walkthrough">
<meta property="og:description" content="%(desc)s">
<meta property="og:image" content="https://demo.siliconwat.com/og-finder.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="The finder for the Khmer Tipiṭaka, on a dark ground, with a line of Pāli in Khmer script.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://demo.siliconwat.com/og-finder.png">
<meta name="theme-color" content="@ACCENT@">
<link rel="icon" type="image/svg+xml" href="favicon.svg">
<link rel="manifest" href="site.webmanifest">
<style>[hidden]{display:none!important}</style>
%(fonts)s
<link rel="stylesheet" href="board.css?v=%(cssv)s">
<style>%(walkcss)s</style>
<script src="./analytics.js"></script>
</head>
<body>
%(band)s
<div class="app">
<header><span class="hl">%(icon)s<span class="wm">siliconwat.com</span></span><span class="hr"><span class="seg">%(langs)s</span><span class="sharebtn" role="button" tabindex="0" aria-label="Share" data-act="share" data-msg="Link copied" data-msg-km="បានចម្លងតំណ">%(share)s</span></span></header>
%(sections)s
<div class="grow"></div>
%(foot_en)s
%(foot_km)s
</div>
<div id="toast" role="status" hidden></div>
<script>%(js)s</script>
</body>
</html>
""" % {"desc": html.escape(desc), "fonts": bb.FONTS, "cssv": cssv, "walkcss": WALK_CSS, "band": band, "icon": bb.icon_svg(bb.ACCENT, 26),
       "langs": seg(t_en, "lang"), "share": bb.SHARE, "sections": page_body, "foot_en": foot(t_en, "en"), "foot_km": foot(t_km, "km"), "js": JS}
    doc = doc.replace("@ACCENT@", bb.ACCENT)
    opens, closes = len(re.findall(r"<div\b", doc)), doc.count("</div>")
    assert opens == closes, "unbalanced divs: %d open, %d close" % (opens, closes)
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(JS); js_path = f.name
    r = subprocess.run(["node", "--check", js_path], capture_output=True, text=True); os.remove(js_path)
    assert r.returncode == 0, "the walkthrough's script does not parse: " + r.stderr[:400]
    io.open(os.path.join(HERE, "finder.html"), "w", encoding="utf-8").write(doc)
    print("finder.html written: %d views × 2 languages, %d bytes; script parses" % (len(VIEWS), len(doc.encode())))


if __name__ == "__main__":
    main()
