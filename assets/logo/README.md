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

## The badge is not on the 2026 palette

This is the thing to decide before the graphics system ships.

| Element | Actual master | 2026 kit palette |
|---|---|---|
| Field | `#0E5CC6` bright blue | Deep Navy `#011E3D` |
| Rope and wordmark | `#F5E056` yellow | not in the palette |
| Anchor | `#FFFFFF` white | White |

The 2020 badge and the 2026 singlet are two different colour systems. The
badge also carries a **maple leaf** at the anchor's crown, which is worth
raising with the club given that Rhode Island's emblem is an anchor and a
fouled anchor with a maple leaf is an unusual combination. It may be inherited
from a stock template.

Nothing here recolours the badge. Recolouring a club's primary mark is the
designer's call, not this repository's.

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
   downstream of a 1025px raster.
2. **A real standalone anchor**, drawn rather than extracted, for the reasons
   above.
3. **A decision on the palette conflict**: does the badge get redrawn on the
   2026 colours, or does the graphics system carry a blue and yellow badge on
   navy and teal layouts?
4. **The five point star and the HOPE wordmark** as the club draws them. The
   star currently in `brand/marks.js` is drawn from geometry, not from a club
   file, so it is a stand-in.
5. **Confirmation on the maple leaf.**

## A note on the tooling

`build-logo-assets.py` is committed so this is reproducible rather than a set
of files someone made once by hand. If a better master arrives, drop it in
`_source/` and re-run.
