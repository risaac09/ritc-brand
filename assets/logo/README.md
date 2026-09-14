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

## The badge is not on the 2026 palette, and it stays that way

| Element | Actual master | 2026 kit palette |
|---|---|---|
| Field | `#0E5CC6` bright blue | Deep Navy `#011E3D` |
| Rope and wordmark | `#F5E056` yellow | not in the palette |
| Anchor | `#FFFFFF` white | White |

The 2020 badge and the 2026 singlet are two different colour systems. Settled
2026-09-13: the badge is not being redrawn. It is the club's real mark, and the
maple leaf at the anchor's crown is deliberate, not a stock-template artifact.
An earlier version of this file guessed otherwise; that guess was wrong.

Nothing here recolours the badge, and nothing should.

**It still works on every ground in the system.** The badge's outermost element
is the yellow rope, not the blue field, so the boundary that matters measures
12.50 against Deep Navy. Verified by rendering on Sand, Navy, Baby Ocean Blue
and White at sizes from 170px down to 48px.

## What is faithful

**`ritc-badge.png`** and the `-512` `-256` `-128` sizes. Transparent PNG, the
full colour badge. The white square outside the circle is removed with a
geometric circular mask, supersampled 4x for a clean rim, so no pixel inside
the badge is altered. The mask is positional rather than colour keyed, which is
why the white anchor survives intact.

**`ritc-badge-bw.png`** and its sizes. Same treatment on the black and white
master.

**`ritc-badge.svg`**. A colour trace of the 1024px PNG. Good enough to scale:
the rope and the wordmark both survive down to 48px and up to poster size.
It is a trace, not a redraw, so the rope's twist is approximated.

## What is approximate, and how it fails

**`ritc-anchor*.png` and `ritc-anchor.svg`.** The standalone anchor is lifted
out of the badge by keying the white shape inside the field.

The problem is that the yellow wordmark sits **on top of** the anchor in the
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

1. **Vector source for the badge**, an AI, EPS, or real SVG. Everything here is
   downstream of a 1025px raster. This is the only badge ask left: the mark
   itself is settled, it just needs to exist as vector.
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
`_source/` and re-run.
