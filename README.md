# demo.siliconwat.com

Drawings of `siliconwat.com` v1, **the finder**: a free page where a person asks in their own words, in Khmer or English, and
sees the typed pages of the Khmer Tipiṭaka (the Buddhist Institute edition, 1927–69) that may answer, with the lines
highlighted. It writes no answers of its own. Every screen is drawn on a phone in English and Khmer, with two desktop
screens and a dark pass.

**Front door:** <https://demo.siliconwat.com/> · **The wall** (every screen at once): <https://demo.siliconwat.com/wall.html>

## What is real and what is not

- **Real:** every passage, its volume and its printed page. They are quoted from the CC0 transcription by Se Mong Ly
  (លី ម៉ុង សែ), released on Hugging Face as `siliconwat/khmer-tipitaka-transcription`, by `pick-passages.py`; each highlight is
  an exact span of its typed page, and the build refuses one that is not.
- **Made up:** the questions, the recent and saved questions, and the counts in a results summary (marked *illustrative*).
- **Placeholders:** the icon (Silicon Wat's own mark is not settled) and the explainer, drawn as a still until it is made.
- **The Khmer** is our own draft until a native reader approves it; every Khmer board says so.

## The walkthrough

`finder.html` (the front door's *Start here*): one page you can drive on a phone, built by `build-walk.py` from the SAME screen
functions as the drawings (`build-boards.py` with its `WALK` hooks on, which leave every board byte-identical when off). It
searches nothing: one fixed example (anger) and one no-close-match example (smartphones); typing anything else says so.

## Rebuild

```sh
python3 pick-passages.py           # only when the quoted pages change (reads the released dataset)
python3 -m http.server 8333 &      # measure.py reads the boards over HTTP
python3 build-boards.py            # the boards + board.css + canvas.json, from the brand layer
python3 measure.py                 # each board's real height → heights.json
python3 build-boards.py            # again, so canvas.json carries the measured heights
python3 build-walk.py              # the walkthrough, from the same screens
python3 build-index.py && python3 build-wall.py   # the front door and the wall, generated from canvas.json
python3 build-og.py && python3 build-icons.py     # the link-preview card, the icons, the manifest
node scripts/check-brand.mjs       # the vendored brand layer still matches brand.lock
```

⛔ Never hand-edit a generated file (`*.html`, `board.css`, `canvas.json`, `heights.json`, the icons, `og.png`).

## What the build refuses

*Sign in*, the regulated words, a percentage outside the About screen, a countdown, a streak or a ranking, an AI model or
vendor named, the heart, any line that puts words in the Buddha's mouth, and a highlight that is not on a typed page.

These are drawings. They search nothing and charge nothing. Hidden from search by named crawler, shareable by link; there is
deliberately no `robots.txt` (a disallow would break link previews). Visits are counted without cookies.
