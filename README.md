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

Brand, tokens, and the export pipeline are complete. One template built
(workout announcement). The remaining five are pending confirmation of
direction.

Logo files are not yet supplied, so templates render a labeled placeholder.
See `assets/logo/README.md`.
