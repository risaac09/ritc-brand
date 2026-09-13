# RITC logo: designer brief

For M. Fox or whoever the club works with on the mark. Written from the actual
2020 master files, not from a wordmark-from-scratch assumption. Full detail
and evidence in `assets/logo/README.md` and `brand/BRAND.md` section 3.

## What already exists

The club has a working badge. Two 2020 master JPGs, CMYK, 1025x1026,
originally from an on-running.com account:

- Circular badge, **bright blue field `#0E5CC6`**, **yellow rope border and
  yellow wordmark `#F5E056`**, white anchor, **maple leaf** at the crown.
- RHODE ISLAND above TRACK CLUB, condensed caps.
- A black-and-white master also exists.

This is not a from-scratch logo job. It is a decision plus a redraw.

## The one decision the club needs to make

The badge's blue and yellow are not on the 2026 kit palette (Baby Ocean Blue
`#A2C9CF`, Deep Navy `#011E3D`, White, plus Sand `#C6B79B` and Ebony `#1C1C1C`
for the outers). Two paths:

1. **Redraw the badge on the 2026 colours.** Field becomes Deep Navy, rope and
   wordmark become White or Baby Ocean Blue. Brings the mark and the kit into
   one system.
2. **Keep the badge as is.** Blue and yellow stay the club's mark regardless of
   what the kit does. The graphics system already accommodates this: the
   badge's outermost edge is the yellow rope, which measures 12.5:1 contrast
   against Deep Navy, so it separates cleanly on every ground in the system as
   it stands.

Whichever way this goes, say so explicitly rather than letting a designer
guess, and also ask about the maple leaf: an anchor is already Rhode Island's
own emblem, so a maple leaf at the crown reads as inherited from a stock
template rather than a deliberate choice. Confirm before it goes any further.

## What is actually needed from a designer

1. **Vector source for the badge**, in whichever direction the decision above
   goes. AI, EPS, or a real SVG with organized layers. Every asset in this
   repo right now is machine-derived from a 1025px raster JPG, which is why
   the rope's twist is an approximation and not the real geometry.

2. **A standalone anchor, drawn, not extracted.** The current one is lifted
   out of the badge by keying the white shape, and the yellow wordmark sits on
   top of the anchor in the source, so letters bite real gaps into the shank
   and flukes. It is clean under about 120px and shows artifacts above that.
   A drawn anchor has no such ceiling.

3. **The five-point star and the repeating star column**, if the club has a
   version from the singlet beyond what a generic star shape approximates.
   The one in `brand/marks.js` right now is drawn from geometry, not sourced
   from a club file.

4. **Color variants once the palette decision is made**: full color, white
   knockout, and single-color, each as PNG (transparent) and SVG.

## Delivery

Drop files in `assets/logo/`, following the existing naming (`ritc-badge.svg`,
`ritc-anchor.svg`, etc. — see that folder's README for the current set) so
templates pick them up without an edit. Re-run
`python3 scripts/build-logo-assets.py` if a new master JPG replaces the 2020
ones, so the derived PNG sizes and traces regenerate from it.
