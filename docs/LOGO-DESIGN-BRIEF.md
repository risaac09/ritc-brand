# RITC logo: designer brief

Written from the actual 2020 master files and the 2026 kit, not from a
wordmark-from-scratch assumption. Evidence and measurements in
`assets/logo/README.md` and `brand/BRAND.md` section 3.

## What exists, and what is settled

The club has a working badge. Two 2020 master JPGs, CMYK, 1025x1026:

- Circular badge, a rope border, white anchor, **maple leaf** at the crown.
- RHODE ISLAND above TRACK CLUB, condensed caps.
- A black-and-white master also exists.

The 2020 masters are drawn in a bright blue and a yellow. **Those colours are
retired (2026-10-12).** The badge now runs in the 2026 kit palette: Deep Navy
`#011E3D` field, Sand `#C6B79B` rope, wordmark and leaf, White anchor, with
Baby Ocean Blue `#A2C9CF` and Ebony `#1C1C1C` variants. The repository builds
those from the masters by remapping colour, pixel by pixel. The drawing itself
is the club's real mark and is not being redesigned.

So this is not a redesign job. It is a file-format job.

## What is actually needed

1. **Vector source for the badge.** AI, EPS, or a real SVG with organized
   layers. Every badge asset in this repository is machine-derived from a
   1025px raster JPG, which is why the rope's twist is an approximation rather
   than the real geometry. The mark and its colours are settled; it just
   needs to exist as vector, in the 2026 colours above, with the default,
   ocean and ebony colourways as separate artboards or layers.

2. **The four singlet marks as drawn**, in vector: the anchor, the five-point
   star, the star column from the front seam, and HOPE as set. These are the
   designer's own work on the 2026 kit. Currently the star is plain geometry
   drawn as a stand-in, and the anchor is extracted out of the badge, where the
   wordmark crosses it and takes letter-shaped gaps out of the shank and the
   flukes. That extraction reads cleanly at about 120px and below and shows the
   damage above it. Requested in `docs/email-moriah-asset-request.md`.

3. **Colour variants of the badge**, if convenient: full colour, a white
   knockout, and a single-colour version, as transparent PNG and SVG. Not
   urgent, since the full-colour badge already sits on every ground in the
   system.

## Delivery

Drop files in `assets/logo/`, following the existing naming
(`ritc-badge.svg`, `ritc-anchor.svg`, and so on; that folder's README lists the
current set) so templates pick them up without an edit. If a better badge
master replaces the 2020 JPGs, drop it in `assets/logo/_source/` and re-run
`python3 scripts/build-logo-assets.py` to regenerate the derived sizes and
traces from it.

## Still open, and not the designer's call

CMYK values for Sand and Ebony. Those two are screen-sampled from a colourway
sheet rather than read from a print file, so they should not go to a printer as
they stand. That is a committee question.
