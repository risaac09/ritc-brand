# Rhode Island Track Club: brand guide for social graphics

Scope: Instagram and the graphics system in this repo. Version 1.0.0, 2026-09-12.

This is not the club's full brand book. No canonical brand book exists. What is
here was derived from the print-ready 2026 singlet file, the singlet colorway
sheet, and the Larana Studio outers lookbook. Where a value is unverified, it
says so.

---

## 1. Color

### The rule that matters most

**Hex is for screens. CMYK is for print. Never convert between them.**

A hex-to-CMYK conversion in a print dialog will not land on the values below. It
will land somewhere near them, and near is how a navy singlet and a navy poster
end up not matching in the same photo. When a printer asks for color, give them
the CMYK numbers from this table or from `tokens.json`. Do not give them the hex.

### Primary palette

Verified against the print-ready singlet file.

| Name | Hex (digital) | CMYK (print) | Role |
|---|---|---|---|
| Baby Ocean Blue | `#A2C9CF` | C36 M9 Y16 K0 | Fill and field only |
| Deep Navy | `#011E3D` | C99.6 M83.8 Y39.2 K57 | Ground and text |
| White | `#FFFFFF` | C0 M0 Y0 K0 | Ground and text |

### Secondary palette

The outers: warmups, the On Focus T, the Larana Studio apparel line. These are
screen-sampled from the colorway sheet, **not** verified against a print file,
and they carry no CMYK values yet. Treat them as valid for digital, and get real
print values before any print job uses them.

| Name | Hex (digital) | CMYK (print) | Role |
|---|---|---|---|
| Sand | `#C6B79B` | not yet specified | Fill only, outers context |
| Ebony | `#1C1C1C` | not yet specified | Ground and text, outers context |

Sand and Ebony are not an alternate palette and they are not there for variety.
They have a structural job, described in section 2.

### Background and foreground

Baby Ocean Blue is a fill. It is the ocean, the field, the stripe, the shape
behind something. It is almost never the text.

Deep Navy and White are the two grounds and the two text colors. Every graphic
in this system resolves to one of two states:

- **Navy ground.** White headlines, Baby Ocean Blue for eyebrows, rules, and
  secondary type. This is the default and it is what the badge sits on natively.
- **White ground.** Navy headlines and navy body. Baby Ocean Blue for fills,
  bars, and shapes, never for type.

A photograph is a third ground, and it is always navy underneath: every photo
slot carries a navy gradient scrim so white type stays readable no matter what
the picture does.

### Contrast, measured

WCAG 2.1 relative luminance, computed 2026-09-12. AA body text needs 4.5:1. AA
large text (24px and up at bold, or 30px and up) needs 3:1.

**Approved pairings**

| Foreground on background | Ratio | AA body |
|---|---|---|
| White on Ebony | 17.04 | pass |
| Deep Navy on White | 16.74 | pass |
| White on Deep Navy | 16.74 | pass |
| Baby Ocean Blue on Ebony | 9.57 | pass |
| Baby Ocean Blue on Deep Navy | 9.40 | pass |
| Sand on Ebony | 8.64 | pass |
| Deep Navy on Sand | 8.49 | pass |

**Forbidden pairings**

| Foreground on background | Ratio | Why |
|---|---|---|
| White on Sand | 1.97 | Fill against fill. Illegible. |
| Baby Ocean Blue on White | 1.78 | This is the one people reach for. It fails badly. |
| Deep Navy on Ebony | 1.02 | Effectively the same value. Invisible. |

### When navy on teal is allowed

Always. Deep Navy on Baby Ocean Blue measures 9.40:1, which clears AA body text
twice over and clears AAA. It is the strongest pairing available on a light
ground and it is the signature look of the system: navy type inside a teal
block. Use it for callout panels, workout day tags, and result blocks.

The inverse, Baby Ocean Blue type on a navy ground, is the same 9.40:1 and is
equally safe. Use it for eyebrows and secondary lines where white would compete
with the headline.

What is not allowed is Baby Ocean Blue type on white. Same teal, different
ground, and it drops to 1.78:1.

---

## 2. Structure: the warmups go over the singlet

This is the organizing principle of the whole system. Every layout decision
resolves to it.

A runner at a Tuesday workout is wearing two layers. The Sand and Ebony warmups
are on the outside. The Baby Ocean Blue and Navy singlet is underneath. That
physical fact is the structure.

**The outer layer frames. The inner layer fills.**

- **Sand and Ebony are the outer layer.** Frames, edge bands, margin fields,
  headers and hems, the surface the graphic sits on. They are chrome. They hold
  the thing, they are not the thing.
- **Baby Ocean Blue, Deep Navy, and White are the inner layer.** The field, the
  photograph, the headline, the result, the runner. Everything the post is
  actually about lives in the singlet palette.

So the answer to which color is background and which is foreground is not a
preference. The outer is the ground. The inner is the field. A graphic is a
warm band with a singlet-colored field inside it, and the content is in the
field.

### The strip

Warmups come off at the start line. That is the second half of the metaphor and
it is what keeps the feed from looking like one repeated template.

The more a graphic is about competing, the less frame it has.

| Post type | Frame | Reasoning |
|---|---|---|
| Workout announcement | Full frame | Pre-race. Logistics. Warmups on. |
| Event or race promo | Full frame | Pre-race. Warmups on. |
| Member spotlight | Hem bands, top and bottom | Partly stripped. The person is the field. |
| Quote or motto card | Hem bands | The club talking, not the club racing. |
| Story | Hem bands, or none | Depends what is in it. |
| Race recap and results | **No frame.** Full bleed singlet palette. | This is the race. Warmups are off. |

A race recap with a Sand border on it is a runner who forgot to take their
jacket off. Do not do it.

### The two legal layer pairs

The outer and inner colors have to separate at the boundary or the frame reads
as mud. Measured, only two of the six combinations work.

| Outer frame | Inner field | Ratio | Verdict |
|---|---|---|---|
| Ebony | White | 17.04 | Legal |
| **Ebony** | **Baby Ocean Blue** | **9.57** | **Legal** |
| **Sand** | **Deep Navy** | **8.49** | **Legal** |
| White | Sand | 1.97 | Edge disappears |
| Sand | Baby Ocean Blue | 1.11 | Edge disappears |
| Ebony | Deep Navy | 1.02 | Edge disappears |

The rule in one line: **the warm outer takes the dark inner, the dark outer
takes the light inner.**

Sand frame, navy field. Ebony frame, teal or white field. Nothing else. If a
layout seems to need Sand around a teal field, the layout is wrong, not the rule.

### Frame geometry

- **Full frame.** Sand or Ebony on all four sides, `--frame-band` wide (56px),
  with the inner field inset inside it. The badge sits in the frame, not the
  field, which is where a logo sits on a jacket.
- **Hem bands.** The same band on the top and bottom edges only, left and right
  running full bleed. Reads as a collar and a cuff. Use when the photograph
  needs the width.
- **No frame.** The field bleeds to all four edges. Race day.

### Where the star column goes

The star column is stitched down the front seam of the singlet, so it belongs to
the inner layer. Run it inside the field, never across the frame, and never as
the frame itself. It is the one element that says which layer you are looking at.

---

## 3. Typography

Both faces are on Google Fonts under the SIL Open Font License, so they are free
to use, free to embed, and free to hand to a printer or a volunteer.

### Headlines: Oswald

Oswald is a condensed grotesque reworked from the Alternate Gothic tradition,
the compressed American sans that has been on team uniforms and meet posters for
a century. The badge lockup sets RHODE ISLAND over TRACK CLUB in condensed caps,
and Oswald is the closest free face to that compression. It holds its counters
at large sizes, it stacks cleanly in two and three line headlines, and it does
not get chatty.

Weights in use: 500 and 600. Do not use 700 at display sizes, it closes up.

### Body: Archivo

Archivo is a neutral grotesque built for the awkward middle where a face has to
work in print and on a phone screen at the same time. It has a large x-height,
which matters when Instagram compresses a 21px caption, and it is quiet enough
that it does not fight Oswald. Same designer family logic as Oswald's ancestor,
different job.

The pairing is deliberate: one face carries the shout, the other carries the
information. If both faces were condensed the graphic would read as a sports
poster, which is the corporate-slick direction this club does not want.

### Type scale

Sizes are px on the 1x canvas at 1080 wide. Export renders at 2x.

| Token | Size | Line height | Tracking | Face | Case |
|---|---|---|---|---|---|
| `display` | 96 | 0.92 | -0.01em | Oswald 600 | caps |
| `h1` | 72 | 0.95 | -0.005em | Oswald 600 | caps |
| `h2` | 54 | 1.0 | 0 | Oswald 500 | caps |
| `h3` | 40 | 1.1 | 0 | Oswald 500 | caps |
| `eyebrow` | 20 | 1.2 | 0.18em | Oswald 500 | caps |
| `bodyLarge` | 32 | 1.35 | 0 | Archivo 400 | sentence |
| `body` | 26 | 1.45 | 0 | Archivo 400 | sentence |
| `caption` | 21 | 1.4 | 0.02em | Archivo 500 | sentence |
| `data` | 44 | 1.0 | 0 | Archivo 700 tabular | as needed |

Nothing smaller than 21px. A caption below that disappears in the feed.

`data` uses tabular figures so a column of race times lines up.

---

## 4. The marks

### Primary mark: the circular badge

Circular badge, navy field, white rope border, white anchor with an RI-style
emblem at the crown, RHODE ISLAND above TRACK CLUB in white condensed caps.
Original master files date to 2020 and predate the 2026 kit refresh.

**Clear space.** 25 percent of the badge diameter, on all four sides. At a 200px
badge that is 50px of nothing. No type, no photo edge, no other mark inside it.

**Minimum size.** 96px diameter on screen. 0.75 inch in print. Below that the
rope border fills in and the wordmark closes up.

**Kit placement, for reference.** Chest 3 inches wide, left chest, USATF
compliant. Back 2.25 to 2.5 inches, centered top. These are the apparel specs,
not social specs, but they are the reason the badge is drawn to survive small.

**Ground.** The badge has a navy field of its own, so it sits on white, on Baby
Ocean Blue, and on a photograph without a container. On a navy ground it needs
either the white rope border to carry the edge or a small amount of separation.
Do not put a navy badge on navy and hope.

### Secondary marks

From the singlet.

- **Solid navy anchor**, standalone. The quiet mark. Use where the full badge
  would be too much, or at very small sizes.
- **Five-point navy star.** Single, as an accent or a divider.
- **Repeating star column.** A vertical stripe of stars, taken from the front
  seam of the singlet, which itself echoes the thirteen stars of the state flag.
  This is the system's best structural device: run it down an edge and the
  graphic is recognizably RITC before anyone reads a word.
- **HOPE**, the state motto, in spaced-out caps. The club's line is "Hope is our
  anchor." Set it in Oswald 500 with 0.18em tracking or wider. It is a motto, not
  a headline, so it goes small and confident rather than large.

### Do

- Give the badge its clear space, every time.
- Use the star column as a vertical edge element, full bleed top to bottom.
- Put the badge bottom-left or bottom-right, consistently, so the feed has a rhythm.
- Let the anchor stand alone when the badge would crowd.
- Keep HOPE small and widely tracked.
- Scale the badge proportionally. Always.

### Don't

- Do not recolor the badge. It is navy and white. There is no teal version, no
  one-color knockout, no inverted version, until the designer draws one.
- Do not put the badge on a busy part of a photograph. Scrim it or move it.
- Do not stretch, skew, rotate, or arc any mark.
- Do not add a drop shadow, an outer glow, or a stroke to the badge.
- Do not set the badge inside a white circle or box to force it onto a dark
  ground. Move it to a clean area instead.
- Do not crop the badge, and do not let a canvas edge crop it.
- Do not use the anchor and the full badge in the same graphic. Pick one.
- Do not typeset RHODE ISLAND TRACK CLUB in Oswald as a substitute wordmark. The
  badge is the wordmark.

---

## 5. Photography

Photography carries this account. The graphics system exists to frame it, not to
replace it.

- Every photo slot crops with `object-fit: cover`, so the image fills the frame
  and never distorts.
- Every photo slot gets a navy gradient scrim, transparent at the top to 88
  percent navy at the bottom. White type then reads over a bright singlet, a wet
  road, or a blown-out sky without anyone checking each time.
- Faces near the bottom edge will land under the scrim. Compose for it, or use a
  full-field scrim at lower opacity.
- Do not put text over the middle of a face.
- Do not add a filter that shifts the singlet's teal. The kit color is the brand.

---

## 6. Voice

Community first, local, not corporate-slick.

**What that means in practice**

- Write the way a member talks to another member. The audience is people who
  showed up Tuesday, plus the people deciding whether to show up next Tuesday.
- Name the specific thing. "Six by 800 at the track, 6pm Tuesday" beats "join us
  for an unforgettable session."
- Say where. Providence is the point. Street names, the track, the bridge, the
  hill. Local is the differentiator and it costs nothing to use.
- Credit people by name when you have permission, and only then.
- Celebrate the back of the pack the same way you celebrate the win. A 501(c)(3)
  club that only posts podiums is a team, not a club.

**What to avoid**

- No em dashes. Commas or periods.
- No promotional verbs. Nothing leverages, empowers, transforms, or unlocks.
- No hype adverbs. Not "absolutely crushed it," just "crushed it," or better,
  the actual time.
- No corporate encouragement voice. "We are so proud of our incredible
  community" is what a brand says. Say what happened instead.
- No invented history. This club has real history and none of it should be
  guessed at in a caption.
- No exclamation stacking. One is plenty. Usually zero.

**The club's own lines**, from the kit lookbook, safe to use:

- Mission: "To provide committed runners the opportunity to train and compete."
- "Hope is our anchor."
- "Built for Rhode Island. Built for Speed."

---

## 7. Using the tokens

`brand/tokens.css` and `brand/tokens.json` are the single source of truth.

- Every template imports `tokens.css`. No template hardcodes a hex value, a font
  stack, or a type size.
- `tokens.json` is the same values for any script or tool that needs them
  outside CSS.
- If a value is missing, add it to both files. Do not work around it locally.

---

## 8. Named gaps

Honest accounting of what is not settled.

1. **No canonical club brand book.** This document covers social graphics. It is
   not a substitute for guidelines from the club's designer, and it should not
   be cited to the board as one. Worth a direct ask to M. Fox or the designer.
2. **Sand and Ebony have no CMYK values** and their hex values are screen-sampled
   from a colorway sheet, not read from a print file. Do not send them to a
   printer as they stand.
3. **Logo files are not in this repo yet.** `assets/logo/` holds a labeled
   placeholder. Templates render the placeholder until the real files land.
4. **This is the fourth palette decision on this project** (2026-08-23,
   2026-08-24, 2026-09-01, and now). Five documents in the RITC Operations
   Package were built on the 2026-09-01 Sand and Ebony palette and are now off
   the primary palette. They are outside this repo and were not changed here.
5. **Pantone values are unspecified** for every color. If the club orders
   anything screen printed rather than sublimated, someone needs to pick them.
