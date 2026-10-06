# RITC video and reels lane

Version 0.1.0, 2026-09-14. Drafted against the published DaVinci Resolve 21.1
MCP tool inventory, not against a live listing. The first live session
reconciles it; see step 0.

Scope: Instagram reels and feed video for the club, cut and rendered in
DaVinci Resolve Studio, driven by Claude Code through Resolve's MCP server.
Everything visual comes from `brand/tokens.json` (the `video` block) and the
existing story template. The graphics system frames the footage; the footage
is the post.

## What this lane produces

One reel per intake. Title card, footage, captions when there is speech, a
persistent badge, an end card, one H.264 at 1080x1920, plus a caption in the
club voice and a row in `video/log.csv`. Feed (4:5) and square (1:1) variants
come from the same timeline through a second render preset when asked for.

## Files

```
video/README.md               this file
video/resolve-config.json     bins, cameras, canvas, fps, render presets
video/resolve-mcp.example.json shape of the MCP registration; replaced by
                               a real .mcp.json after Setup AI Assistants runs
video/resolve-tools.md        live tool inventory, written on first connection
video/log.csv                 one row per reel
exports/video/                renders, gitignored
```

## The pipeline

Each step names the resource that verifies it. A step is done when the
resource shows the change, not when the tool returns.

### 0. Reconcile (once per Resolve version)

List tools and resources. Write them to `video/resolve-tools.md` with the
Resolve version at the top. Diff the step names below against the live
names. Where a name differs, edit this file. Where a capability is missing,
mark the step "manual" here and say so in the session. The tool names below
are the published ones for the 21.x scripting-API surface; Blackmagic's
native server may spell them differently.

### 1. Intake

Before touching Resolve, have all of these in hand or stop and ask:

- Post type: workout-announcement, event-promo, member-spotlight,
  quote-card, race-recap. Sets the frame policy, duration range, and layer.
- Footage path on local disk or the archive. Never an iCloud path.
- Who is in it, whether they gave permission to be named, whether anyone
  under 18 appears and whether a release exists.
- The facts: what, where, when, result. Street, track, bridge, time.
- Which camera(s). Sets the bin and the conversion LUT.

### 2. Cards

Fill `templates/story.html` `POST` for the title card: layer per the post
type, `frame: 'hem'`, eyebrow and headline from the intake, no photo unless
one is supplied. Export: `node scripts/export.mjs story`. Rename the PNG to
`exports/<slug>-title.png`. Repeat with `cta` set and headline changed for
the end card, `exports/<slug>-end.png`. Both are 2160x3840; Resolve scales
them onto the 1080x1920 timeline cleanly.

Verify: open both PNGs, badge uncropped, no forbidden pairing.

### 3. Project

- `resolve://system/status`: Studio build, scripting on, version noted.
- `create_project` named `RITC-{date}-{slug}`. Then `resolve://project/current`.
- `set_project_setting` for timeline resolution 1080x1920 and frame rate from
  `resolve-config.json`. Color science DaVinci YRGB Color Managed v2.
- `create_bin` for each entry in `bins`. Then `resolve://mediapool/folders`.
- `save_project`.

### 4. Import

- `import_media_to_bin` footage into its camera bin. Cards into
  `Graphics/Cards`. `assets/logo/ritc-badge-512.png` into `Graphics/Logo`.
- `set_clip_color` per camera from the config.
- Verify with `resolve://mediapool/clips` per folder. Count matches intake.
- `save_project`.

### 5. Timeline

- `create_empty_timeline` at the canvas size. Then
  `resolve://timeline/current`.
- `append_clips_to_timeline`: title card, footage in intake order, end card.
  Card holds from `tokens.video.titleCard.holdSeconds` and
  `endCard.holdSeconds`.
- Verify with `resolve://timeline/items`. Item count = clips + 2.
- **Reframing is manual.** The published inventory has no clip reposition
  or transform tool. Vertical reframe of horizontal footage is a per-clip
  Inspector step Isaac does in the Edit page before step 7. Note it in the
  session and wait.
- `add_timeline_marker` at each cut with the clip's source note, so the
  manual pass has a map.
- `save_project`.

### 6. Captions

Only when there is speech.

- `transcribe_audio` on the timeline clips with speaker detection off (one
  voice, usually).
- Read the transcript back through the media pool clip transcription data.
  Fix names against the intake. Break into lines at
  `tokens.video.subtitle.maxCharsPerLine`, two lines max.
- Write an SRT to `exports/video/<slug>.srt`. Import it onto a subtitle
  track. Verify with `resolve://timeline/tracks`.
- **Styling is manual.** The API does not style subtitles. A Resolve
  subtitle preset named `RITC Subtitle` carries the look from
  `tokens.video.subtitle` (Archivo 500, 44px, white on the navy band, lower
  third above the safe zone). It is created once by hand and applied by
  hand. If it does not exist on this machine, say so and stop here.

### 7. Badge and grade

- Badge: a video track above the footage with `ritc-badge-512.png` for the
  full footage duration, scaled to `tokens.video.badge.sizePx`, at the
  corner and inset from the tokens. Cards already carry their own badge;
  the watermark track starts after the title card and ends before the end
  card, or the badge doubles.
- Grade: `set_lut` per camera bin for the conversion to Rec.709 (paths from
  the toolkit's `production/resolve-config.json` and the BRAW grading note
  in the corpus). No creative look exists yet; `tokens.video.grade.look` is
  null. Do not add one. The singlet teal is the brand and survives untouched.
- `save_project`.

### 8. Render

- `load_render_preset` or `set_render_settings` from the `reel` preset.
  Output to `exports/video/`, filename `<slug>_reel.mp4`.
- `add_render_job`, then `resolve://render/jobs` shows it.
- `start_render`, `wait_for_render`.
- Verify: `ffprobe -v error -show_entries stream=width,height,r_frame_rate,codec_type:format=duration -of default=nw=1 <file>`.
  1080x1920, declared fps, video and audio streams, duration inside the post
  type's range. Extract first and last frames with `ffmpeg -ss 0 -frames:v 1`
  and `-sseof -0.1`; both must be the brand cards.
- `save_project`. `export_project` to `exports/video/<slug>.drp` as the
  archive of the cut.

### 9. Caption and log

- Draft the Instagram caption per `brand/BRAND.md` section 6. Name the
  specific thing. Say where. Names only with permission. No em dashes.
  Count the exclamation marks; the answer is usually zero.
- Append a row to `video/log.csv`. `verified_by` is the ffprobe line and
  the frame check, not the word "yes".
- Hand Isaac the file path, the caption, and the log row. Posting is his.

## Fallback without the MCP

Same config, same steps, through the toolkit CLI:

```
cd ~/rubinstein-productions-toolkit/production
CFG=~/ritc-brand/video/resolve-config.json
python3 resolve_workflow.py --config $CFG new-project RITC-2026-09-16-tuesday-800s
python3 resolve_workflow.py --config $CFG import-media /Volumes/Archive/RITC/2026-09-16 --camera gh7
python3 resolve_workflow.py --config $CFG import-media ~/ritc-brand/exports/tuesday-800s-title.png ~/ritc-brand/exports/tuesday-800s-end.png --bin Graphics/Cards
python3 resolve_workflow.py --config $CFG build-timeline tuesday-800s --intro ~/ritc-brand/exports/tuesday-800s-title.png --outro ~/ritc-brand/exports/tuesday-800s-end.png --intro-duration 1.5
python3 resolve_workflow.py --config $CFG render reel --name tuesday-800s
```

Verified against the toolkit's argparse on 2026-09-14: `--config` is a
global flag and goes before the subcommand; project, timeline, and preset
names are positional. Unknown top-level keys in the config are tolerated.

## Named gaps

Same discipline as `brand/BRAND.md` section 8.

1. **Tool names are unverified.** Step 0 exists because of this. Until
   `video/resolve-tools.md` is written from a live session, every tool name
   above is a published name, not a confirmed one.
2. **No reframe tool.** Vertical reframing is manual. If Resolve's native
   server exposes a transform or Smart Reframe call, step 5 changes.
3. **No subtitle styling through the API.** The `RITC Subtitle` preset has
   to be made by hand once. It does not exist yet.
4. **No RITC grade.** `tokens.video.grade.look` is null. Conversion LUTs
   only.
5. **Reels safe zone is a floor, not a measurement.** `safe.reelBottom` is
   inherited from stories at 320px. Measure on a published reel and correct
   the token.
6. **Which cameras shoot RITC is unconfirmed.** The config lists the
   toolkit's four bodies. Delete the ones that never appear.
7. **The standing workout line is a placeholder.** `endCard.cta` is
   `{{STANDING_WORKOUT_LINE}}` until the club confirms day, time, and
   place.
8. **The client-facing post log lives in a workbook on iCloud Desktop**
   (`RITC-Social-Media-Tracking-System.xlsx`), outside this repo.
   `video/log.csv` is the working record; reconciling the two is a separate
   task.
9. **Two servers, one socket.** If the community `davinci-resolve-mcp`
   bridge is ever installed alongside the native server, only one may be
   registered at a time.

## Kickoff prompt

Paste this into a fresh Claude Code session opened in `~/ritc-brand` with
Resolve Studio running on the project's machine.

```
Read CLAUDE.md, brand/BRAND.md sections 1 to 6, brand/tokens.json, and
video/README.md. Then run video/README.md step 0: list the Resolve MCP
tools and resources, write video/resolve-tools.md, and tell me which steps
in the README name a tool the live server does not expose. Do not create,
import, or render anything yet. Stop after the reconciliation report.
```

Once step 0 is clean, the per-reel prompt is the intake block from step 1,
filled in, followed by: "Run video/README.md steps 2 through 9. Stop and ask
at any step marked manual, at any delete, and before the render."
