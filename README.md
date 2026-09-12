# RITC Instagram graphics

A reusable graphics system for @rhodeislandtrackclub. Self contained HTML
templates rendering at exact Instagram dimensions, driven by one set of brand
tokens, exported to PNG at 2x.

No build step. No framework. Open a template in a browser and it renders.

## Layout

```
brand/BRAND.md      the guide: color, type, marks, voice, named gaps
brand/tokens.css    single source of truth, imported by every template
brand/tokens.json   the same values for scripts and tooling
assets/logo/        logo files (not yet supplied, see its README)
templates/          one self contained HTML file per post type
index.html          gallery, every template side by side
scripts/            PNG export
exports/            output, gitignored
```

## Editing a post

Each template carries a plain data object at the top of the file. Edit the copy
there. Do not touch the layout below it.

## The one rule

No hardcoded hex values, font stacks, or type sizes outside `brand/tokens.css`
and `brand/tokens.json`. If a value is missing, add it to both.

## Status

Brand and tokens complete, including the layer structure. Templates pending
review of direction.
