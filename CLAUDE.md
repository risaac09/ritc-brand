# ritc-brand: orientation for Claude

Rhode Island Track Club internal repo for brand, graphics, and social media.
Isaac Rubinstein is the club's social media manager and photographer. Every
file here is client work for a 501(c)(3) running club in Providence, not
Rubinstein Productions material. Do not import RP or Say Why voice, palette,
or intro cards into anything in this repo.

Read `brand/BRAND.md` before touching a template, a caption, or a video. It
is the guide. This file only tells you how to work inside it.

## Sources of truth, in order

1. `brand/tokens.json` and `brand/tokens.css`. Same values, two formats. No
   template, script, caption spec, or video spec hardcodes a hex, a font, or a
   size. If a value is missing, add it to both files and bump the version.
2. `brand/BRAND.md`. Color, layer structure, type, marks, photography, voice,
   named gaps. Sections 1 through 6 are rules. Section 8 is the honest list of
   what is not settled; do not resolve a named gap by guessing.
3. `video/README.md`. The reel and video lane, built on the same tokens.
4. `assets/logo/README.md`. Which logo files are trustworthy at which size.

`stack-data/context/rhode-island-track-club-brand.md` is older than this repo
and carries a superseded palette. Where they disagree, this repo wins.

## Constraints that are not preferences

- No build step, no framework. A template is one HTML file that renders when
  opened. Exports go through Playwright in `scripts/export.mjs` and land in
  `exports/`, which is gitignored.
- The badge is blue and yellow and is never recolored. The maple leaf is
  deliberate. It is the club's real mark.
- Sand and Ebony frame. Baby Ocean Blue, Deep Navy, and White fill. Only two
  layer pairs are legal: Sand over Navy, Ebony over Baby Ocean Blue or White.
- Baby Ocean Blue is never type on white. White is never type on Sand.
- Race recaps have no frame. Warmups come off at the start line.
- Nothing readable below 21px on a 1080 canvas. Subtitles in video have their
  own floor in `tokens.json` under `video`.
- Voice per BRAND.md section 6: member to member, name the specific thing, say
  where, no em dashes, no promotional verbs, no hype adverbs, no invented
  history, at most one exclamation mark and usually none.
- Credit people by name only with permission. If the intake does not say
  permission was given, leave the name out and say so.
- Photos of minors: none in any post or reel without a written release noted
  in the intake. The club trains adults, but events draw families.

## The three lanes

**Static graphics.** `templates/*.html`, one per post type. Edit the `POST`
object at the top of the file, nothing below it. Export with
`node scripts/export.mjs <name>`. Frame policy per post type is in
`tokens.json` under `layer.framePolicy`; do not override it in a template.

**Video and reels.** `video/README.md`. The story template doubles as the
title and end card. DaVinci Resolve Studio does the cut, captions, and render,
driven through its MCP server when connected and through
`rubinstein-productions-toolkit/production/resolve_workflow.py --config
video/resolve-config.json` when it is not. Both read the same config.

**Captions and logging.** Every exported graphic or reel gets a caption drafted
in the club voice and a row appended to `video/log.csv` (reels) or the post
log in the tracking workbook (graphics), with the export path, the post type,
the layer, the people credited, and the permission basis.

## Working with the DaVinci Resolve MCP

The MCP is Blackmagic's native server in Resolve Studio 21.1 and later,
enabled with Preferences > System > General > External scripting = Local and
registered through File > Setup AI Assistants. The tool inventory this file
was drafted against is the published one, not a live listing from Isaac's
machine. So:

1. **First connection in any session: list the tools and resources.** Write
   the live inventory to `video/resolve-tools.md` if it does not exist or if
   the Resolve version changed. Reconcile `video/README.md` step names against
   it before running anything. Where a step names a tool the server does not
   expose, say so and stop at that step rather than improvising.
2. **Read before write.** Start from `resolve://system/status` and
   `resolve://project/current`. Confirm Resolve is on the project you expect
   before any mutating call.
3. **Verify every mutation through a resource, not through the tool's own
   return value.** Import, then read `resolve://mediapool/clips`. Append clips,
   then read `resolve://timeline/items`. Queue a render, then read
   `resolve://render/jobs`. A tool that returns success and a resource that
   shows nothing changed is a failed step.
4. **Save at each phase boundary** with `save_project`. Resolve does not
   autosave on an agent's behalf.
5. **Ask before any of these:** `delete_clips`, `delete_timeline`,
   `delete_track`, `reset_grades`, `close_project` on an unsaved project,
   `delete_render_jobs` on a queue you did not build, or any `execute_python`
   or `execute_lua` call. The last two are escape hatches for a missing tool,
   named as such in the log, never a first choice.
6. **Never render into the repo tree** except `exports/video/`, which is
   gitignored. Never import media from iCloud Desktop or Documents paths;
   stage footage on local disk or the external archive first.
7. **The API cannot create color nodes and cannot style subtitles.** Grade
   through `apply_drx_grade` or a LUT onto nodes that already exist. Caption
   styling is a saved Resolve subtitle preset applied by hand once per
   project; the agent places the track and the text, not the look.
8. **Free Resolve has no scripting and no MCP as of 21.1.** If
   `resolve://system/status` reports a non-Studio build, stop and say so.

## Verification before you say a thing is done

- A graphic: open the export, confirm the canvas size is exactly the
  template's declared size times the scale, confirm the badge is not cropped
  and has its clear space, confirm no text sits in a forbidden pairing.
- A reel: `ffprobe` the file. Confirm 1080x1920 (or the declared canvas),
  the declared frame rate, duration within the post type's range in
  `video/README.md`, an audio stream present. Pull the first and last frames
  and confirm the title and end cards are the brand's, not Resolve's default
  black.
- A caption: run it against BRAND.md section 6 by hand. Count exclamation
  marks. Search for em dashes. Check every name against the permission note.

State what was verified and how. If a step could not be verified, say that,
do not round it up to done.

## Git

One session, one branch, merged or deleted before wrap. Do not commit
`exports/`, `node_modules/`, or any footage. Do not push without an
adversarial self-review of the diff. Secret-scan hook applies; there should be
nothing secret here in the first place.
