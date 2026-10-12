#!/usr/bin/env python3
"""Fail on any retired colour or the retired 2020 badge.

The retired list lives in brand/tokens.json under `deprecated`. This script
holds no colour values of its own, so retiring another colour is a tokens edit.

    scripts/check-brand.py               the repo: every text file, every image
                                         under assets/ (not _source/) and exports/
    scripts/check-brand.py PATH ...      images, videos, or folders of them, for
                                         renders made outside the repo (a reel,
                                         a Resolve export, a carousel)

Two checks:

  Text. Any #RRGGBB or rgb(r, g, b) in a text file that matches a retired
  colour, exactly or within its tolerance. brand/tokens.json is the one file
  allowed to name them.

  Pixels. The 2020 badge has a signature: its blue field and its yellow rope in
  the same region, the yellow touching the blue. Either colour alone can be a
  sky or a race sign, so a region fails only when both pass their minimum share. Each image is checked whole and
  in a 4 by 4 grid, so a small watermark is found wherever it sits. A video is sampled every
  two seconds.

Exit 0 when clean, 1 when anything is found, 2 on a usage or tooling error.
Needs Pillow and numpy; videos also need ffmpeg on PATH.
"""

import json, re, shutil, subprocess, sys, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TOKENS_PATH = REPO / 'brand/tokens.json'
IMAGE_EXT = {'.png', '.jpg', '.jpeg', '.webp', '.tif', '.tiff'}
VIDEO_EXT = {'.mp4', '.mov', '.m4v', '.mkv', '.webm'}
TEXT_EXT = {'.html', '.css', '.js', '.mjs', '.json', '.md', '.svg', '.py',
            '.sh', '.yml', '.yaml', '.txt', '.csv', '.fcpxml', '.xml', '.drx'}
SKIP_DIRS = {'.git', 'node_modules', '_source'}
VIDEO_STEP_S = 2
VIDEO_MAX_FRAMES = 150
ADJ_PX = 2  # how close, at check resolution, rope colour must sit to field colour

HEX_RE = re.compile(r'#([0-9A-Fa-f]{6})\b')
RGB_RE = re.compile(r'rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})')


def hex_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def load_rules():
    dep = json.loads(TOKENS_PATH.read_text())['deprecated']
    colors = [dict(c, rgb=hex_rgb(c['hex'])) for c in dep['colors']]
    sig = dep['rasterSignature']
    return colors, [hex_rgb(h) for h in sig['colors']], sig['minFraction']


def matches(rgb, rule):
    if rule.get('match') == 'exact':
        return tuple(rgb) == rule['rgb']
    d = sum((a - b) ** 2 for a, b in zip(rgb, rule['rgb'])) ** 0.5
    return d <= rule.get('tolerance', 0)


def check_text(path, colors, rel):
    hits = []
    try:
        lines = path.read_text(errors='ignore').splitlines()
    except OSError:
        return hits
    for n, line in enumerate(lines, 1):
        found = [hex_rgb(m.group(1)) for m in HEX_RE.finditer(line)]
        found += [tuple(int(v) for v in m.groups()) for m in RGB_RE.finditer(line)]
        for rgb in found:
            for rule in colors:
                if matches(rgb, rule):
                    hits.append(f'{rel}:{n}: {rule["name"]} ({rule["hex"]}, retired '
                                f'{rule["retired"]}). {rule["why"]}')
                    break
    return hits


def regions(h, w):
    """The whole frame plus a 4 by 4 grid. A small badge is a small share of a
    whole frame, so the grid is what finds it wherever it sits."""
    rows = ('top', 'upper', 'lower', 'bottom')
    cols = ('left', 'left-centre', 'right-centre', 'right')
    out = {'whole': (0, h, 0, w)}
    for i, rn in enumerate(rows):
        for j, cn in enumerate(cols):
            out[f'{rn} {cn}'] = (h * i // 4, h * (i + 1) // 4, w * j // 4, w * (j + 1) // 4)
    return out


def badge_regions(img, sig_rgb, min_frac, tol):
    """Names of the regions where both badge colours pass their minimum share."""
    import numpy as np
    a = np.asarray(img.convert('RGBA')).astype(np.int32)
    rgb, opaque = a[..., :3], a[..., 3] >= 128
    near = [((rgb - np.array(c)) ** 2).sum(axis=2) <= tol * tol for c in sig_rgb]
    # On the badge the rope sits on the field, so count only rope-colour
    # pixels that touch field colour. A blue stripe beside yellow leaves on a
    # pavement has both colours but not touching; this is what tells them apart.
    field = near[0]
    grown = field.copy()
    for dy in range(-ADJ_PX, ADJ_PX + 1):
        for dx in range(-ADJ_PX, ADJ_PX + 1):
            grown |= np.roll(np.roll(field, dy, axis=0), dx, axis=1)
    near[1] = near[1] & grown
    out = []
    for name, (y0, y1, x0, x1) in regions(*opaque.shape).items():
        n = int(opaque[y0:y1, x0:x1].sum())
        if n == 0:
            continue
        fr = [int((m[y0:y1, x0:x1] & opaque[y0:y1, x0:x1]).sum()) / n for m in near]
        if all(f >= t for f, t in zip(fr, min_frac)):
            out.append(name)
    return out


def check_image(path, rel, sig, min_frac, tol, label=None):
    from PIL import Image
    try:
        img = Image.open(path)
        img.thumbnail((1440, 1440))
    except Exception as e:  # noqa: BLE001 - report and move on
        return [f'{rel}: could not read image ({e})']
    found = badge_regions(img, sig, min_frac, tol)
    if found:
        where = ', '.join(found)
        return [f'{label or rel}: the retired 2020 badge colours ({where}). '
                f'Rebuild with the current badge from assets/logo/.']
    return []


def check_video(path, rel, sig, min_frac, tol):
    if not shutil.which('ffmpeg'):
        print('check-brand: ffmpeg is not on PATH, cannot check video', file=sys.stderr)
        sys.exit(2)
    hits = []
    with tempfile.TemporaryDirectory() as tmp:
        run = subprocess.run(
            ['ffmpeg', '-loglevel', 'error', '-i', str(path),
             '-vf', f'fps=1/{VIDEO_STEP_S},scale=1080:-2',
             '-frames:v', str(VIDEO_MAX_FRAMES), f'{tmp}/f%04d.png'],
            capture_output=True, text=True)
        if run.returncode != 0:
            # An unchecked video is not a clean one, so it counts as a finding.
            err = (run.stderr.strip().splitlines() or ['no output'])[-1]
            return [f'{rel}: could not read video, so it was not checked ({err})']
        frames = sorted(Path(tmp).glob('f*.png'))
        bad = []
        for i, f in enumerate(frames):
            if check_image(f, rel, sig, min_frac, tol):
                bad.append(i * VIDEO_STEP_S)
        if bad:
            shown = ', '.join(f'{t // 60}:{t % 60:02d}' for t in bad[:12])
            more = f' and {len(bad) - 12} more' if len(bad) > 12 else ''
            hits.append(f'{rel}: the retired 2020 badge colours in {len(bad)} of '
                        f'{len(frames)} sampled frames, at {shown}{more}. Re-render '
                        f'with the current badge from assets/logo/.')
    return hits


def walk(root):
    if root.is_file():
        yield root
        return
    for p in sorted(root.rglob('*')):
        if p.is_file() and not (SKIP_DIRS & set(p.relative_to(root).parts)):
            yield p


def repo_files():
    """Tracked plus untracked-but-not-ignored files, so a new file is checked
    before it is ever committed."""
    out = subprocess.run(['git', '-C', str(REPO), 'ls-files', '-co', '--exclude-standard'],
                         capture_output=True, text=True, check=True).stdout.split()
    return [REPO / p for p in out if (REPO / p).is_file()]


def main(argv):
    colors, sig, min_frac = load_rules()
    tol = max(c.get('tolerance', 0) for c in colors if c.get('match') == 'near')
    hits = []
    if argv:
        targets = [Path(a).expanduser() for a in argv]
        for t in targets:
            if not t.exists():
                print(f'check-brand: no such path: {t}', file=sys.stderr)
                return 2
        files = [f for t in targets for f in walk(t)]
    else:
        files = repo_files()
        exports = REPO / 'exports'
        if exports.is_dir():
            files += [f for f in walk(exports)]
    for f in files:
        try:
            rel = f.relative_to(REPO)
        except ValueError:
            rel = f
        ext = f.suffix.lower()
        in_source = '_source' in f.parts
        if ext in IMAGE_EXT and not in_source:
            hits += check_image(f, rel, sig, min_frac, tol)
        elif ext in VIDEO_EXT:
            hits += check_video(f, rel, sig, min_frac, tol)
        elif ext in TEXT_EXT and f.resolve() != TOKENS_PATH and not in_source:
            hits += check_text(f, colors, rel)
    for h in hits:
        print(h)
    if hits:
        print(f'\ncheck-brand: {len(hits)} finding(s). Retired colours are listed in '
              f'brand/tokens.json under deprecated.', file=sys.stderr)
        return 1
    print(f'check-brand: clean ({len(files)} files checked).')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
