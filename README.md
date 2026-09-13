# ritc-brand

Rhode Island Track Club internal repository for brand, graphics and social
media.

The first system in it is the Instagram graphics set: self contained HTML
templates rendering at exact Instagram dimensions, driven by one set of brand
tokens, exported to PNG at 2x.

No build step. No framework. Open a template in a browser and it renders.

## Layout

```
brand/BRAND.md      the guide: color, structure, type, marks, voice, gaps
brand/tokens.css    single source of truth, imported by every template
brand/tokens.json   the same values for scripts and tooling
assets/logo/        logo files (not yet supplied, see its README)
templates/          one self contained HTML file per post type
index.html          gallery, every template side by side
assets/fonts/       Oswald and Archivo, vendored so exports never fall back
scripts/            PNG export and the Chromium resolver
exports/            output, gitignored
```

## Exporting

```
npm install          once, for Playwright
npm run export       every template to exports/ at 2x
node scripts/export.mjs workout-announcement    one template
node scripts/export.mjs --scale 1               other scale
```

The screenshot is clipped to the canvas element, not the viewport, so a
1080x1350 template always writes a 2160x2700 file.

## Editing a post

Each template carries a plain data object at the top of the file. Edit the copy
there. Do not touch the layout below it.

## The one rule

No hardcoded hex values, font stacks, or type sizes outside `brand/tokens.css`
and `brand/tokens.json`. If a value is missing, add it to both.

## Status

All six templates are built, plus the gallery and the export pipeline.

| Template | Size | Frame case |
|---|---|---|
| Workout announcement | 1080x1350 | Full frame |
| Event promo | 1080x1350 | Full frame |
| Member spotlight | 1080x1350 | Hem bands |
| Race recap | 1080x1350 | No frame |
| Quote card | 1080x1080 | Hem bands |
| Story | 1080x1920 | Hem bands or none |

Open `index.html` to see all six side by side at true size, rendered live from
the same files the export script uses.

### Still outstanding

These need a person, not more code:

- **A decision on the badge palette.** The 2020 badge is bright blue and
  yellow; the 2026 kit is navy and teal. Both work as they stand, but they are
  two colour systems. `docs/LOGO-DESIGN-BRIEF.md` states the choice.
- **Vector source for the badge, and a drawn standalone anchor.** Everything in
  `assets/logo/` is derived from a 1025px raster. The extracted anchor is clean
  under about 120px and shows artifacts above that.
- **Confirmation on the maple leaf** at the badge's crown.
- **A real race photo** to check the scrim against. The templates have only
  been tested against a synthetic stand-in.
- **CMYK values for Sand and Ebony**, which are screen-sampled rather than read
  from a print file. Do not send them to a printer as they stand.
