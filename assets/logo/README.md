# Logo assets

Derived from the club's two 2020 master files on 2026-09-12. Read this before
using any of them, because what is here is not all of equal quality.

## Where these came from

The masters live in the club's Drive folder, owned by an on-running.com
address, both dated 2020-09-29. They are **CMYK JPEGs, 1025x1026, on a solid
white square**, with no alpha and no vector source. Everything in this folder
is derived from those two files and inherits their limits.

Originals are kept in `_source/` so the derivation can be re-run or checked.
Regenerate everything with:

```
python3 scripts/build-logo-assets.py
```

## The badge is built in the 2026 palette

Recoloured 2026-10-12 on Isaac's call. The 2020 masters are drawn in a bright
blue and a yellow that are now retired (`brand/tokens.json`, `deprecated`).
`build-logo-assets.py` repaints them from the palette names in
`tokens.json` under `mark.variants`, so no file here carries the 2020 colours.
The masters in `_source/` are the only place they survive, as build input.

| Element | 2020 master | Default badge now |
|---|---|---|
| Field | retired blue | Deep Navy |
| Rope, wordmark, maple leaf | retired yellow | Sand |
| Anchor | white | White |

Variants: `ritc-badge` (default), `ritc-badge-ocean` (Baby Ocean Blue rope),
`ritc-badge-ebony` (Ebony field), `ritc-badge-bw` (Ebony and White). See
`brand/BRAND.md` section 4 for which goes where.

## What is faithful

**`ritc-badge.png`**, the `-ocean` and `-ebony` versions, and the `-512` `-256`
`-128` sizes. Transparent PNG. The white square outside the circle is removed
with a geometric circular mask, supersampled 4x for a clean rim. The mask is
positional rather than colour keyed, which is why the white anchor survives
intact. Colour is then remapped pixel by pixel: each pixel's share of field,
rope and anchor in the master is kept and repainted, so edges keep their blend.
The outermost 2.5 percent of the radius has its white share handed to the
field, because there the white is the master's background bleeding in and
would otherwise show as a light hairline on dark grounds.

**`ritc-badge-bw.png`** and its sizes. Same treatment on the black and white
master, repainted Ebony to White by luminance.

**`ritc-badge.svg`**, `-ocean.svg`, `-ebony.svg`. The committed colour trace of
the 2020 PNG lives in `_source/ritc-badge-2020-trace.svg`; each fill is
repainted with the same remap, so no tracer is needed to rebuild them. Good
enough to scale: the rope and the wordmark survive down to 48px and up to
poster size. It is a trace, not a redraw, so the rope's twist is approximated.

## What is approximate, and how it fails

**`ritc-anchor*.png` and `ritc-anchor.svg`.** The standalone anchor is lifted
out of the badge by keying the white shape inside the field.

The problem is that the wordmark sits **on top of** the anchor in the
badge, so lifting the white shape leaves letter shaped holes where RHODE ISLAND
and TRACK CLUB cross it. A morphological closing heals the shackle ring and the
small nicks. It does not heal the notch in the shank or the cuts through the
flukes, because that geometry is genuinely absent from the source, not merely
broken. Larger kernels fuse the ring into a blob without fixing either.

Practical limit: **the anchor reads cleanly at about 120px and below.** Above
that the artifacts are visible. Use it small, or get the real file.

The SVG is a single path with `fill="currentColor"`, so one file recolours in
CSS instead of needing a PNG per colour. The PNG variants (`-navy`, `-white`,
`-teal`) exist for contexts that cannot inline an SVG.

## Still needed from the designer

1. **Vector source for the badge**, an AI, EPS, or real SVG, in the 2026
   colours above. Everything here is downstream of a 1025px raster. The mark
   and its colours are settled; it just needs to exist as vector.
2. **The pennant.** The navy burgee on the left chest of the Sand tee,
   confirmed official 2026-09-13. There is no file for it here at all, only an
   observation from a photograph, so no template uses it. Vector or transparent
   PNG. Whoever holds the apparel artwork is the place to start; it is not one
   of the singlet marks.

3. **The four singlet marks as the designer drew them**: the anchor, the five
   point star, the star column, and HOPE. The star currently in
   `brand/marks.js` is drawn from geometry rather than from a club file, and
   the anchor here is extracted from the badge rather than drawn, for the
   reasons above. Requested in `docs/email-moriah-asset-request.md`.

## A note on the tooling

`build-logo-assets.py` is committed so this is reproducible rather than a set
of files someone made once by hand. If a better master arrives, drop it in
`_source/` and re-run. It needs Pillow and numpy; the anchor SVG also needs
`vtracer`, and is left as committed when that is missing (it holds no colour).
After any rebuild, run `scripts/check-brand.py`.
