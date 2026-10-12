#!/usr/bin/env python3
"""Fail on any retired colour or the retired 2020 badge.

The retired list lives in brand/tokens.json under `deprecated`. This script
holds no colour values of its own, so retiring another colour is a tokens edit.

    scripts/check-brand.py               the repo: every text file, every image
                                         under assets/ (not _source/) and exports/
    scripts/check-brand.py --staged      what is staged for commit (the hook)
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
  in an 8 by 8 grid, so a small watermark is found wherever it sits. A video is sampled every
  two seconds, or at 150 points spread end to end on a long one.

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
GRID = 8
CHECK_PX = 2160  # images are checked at this long edge, no smaller
ADJ_PX = 2  # how close, at check resolution, rope colour must sit to field colour

HEX_RE = re.compile(r'#([0-9A-Fa-f]{6})(?:[0-9A-Fa-f]{2})?(?![0-9A-Fa-f])')
RGB_RE = re.compile(r'rgba?\(\s*(\d{1,3})[\s,]+(\d{1,3})[\s,]+(\d{1,3})')


def hex_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def load_rules():
    dep = json.loads(TOKENS_PATH.read_text())['deprecated']
    colors = [dict(c, rgb=hex_rgb(c['hex'])) for c in dep['colors']]
    sig = dep['rasterSignature']
    return colors, [hex_rgb(h) for h in sig['colors']], sig['minFraction'], sig['tolerance']


def matches(rgb, rule):
    if rule.get('match') == 'exact':
        return tuple(rgb) == rule['rgb']
    d = sum((a - b) ** 2 for a, b in zip(rgb, rule['rgb'])) ** 0.5
    return d <= rule.get('tolerance', 0)


def text_lines(path, rel):
    """The lines to check. tokens.json is checked too, with its deprecated
    block removed, because that block is the one place a retired value may
    appear and nowhere else in the file may."""
    text = path.read_text(errors='ignore')
    if str(rel) == 'brand/tokens.json':
        t = json.loads(text)
        t.pop('deprecated', None)
        text = json.dumps(t, indent=2)
    return text.splitlines()


def check_text(path, colors, rel):
    hits = []
    try:
        lines = text_lines(path, rel)
    except (OSError, ValueError) as e:
        return [f'{rel}: could not read ({e})']
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
    """The whole frame plus an 8 by 8 grid. A small badge is a small share of
    a whole frame, so the grid is what finds it wherever it sits."""
    out = {'whole': (0, h, 0, w)}
    for i in range(GRID):
        for j in range(GRID):
            out[f'row {i + 1} col {j + 1} of {GRID}'] = (
                h * i // GRID, h * (i + 1) // GRID, w * j // GRID, w * (j + 1) // GRID)
    return out


def dilate(mask, r):
    """Grow a boolean mask by r pixels. Padded, so nothing wraps round the
    frame edge the way np.roll would."""
    import numpy as np
    h, w = mask.shape
    p = np.pad(mask, r)
    out = np.zeros_like(mask)
    for dy in range(2 * r + 1):
        for dx in range(2 * r + 1):
            out |= p[dy:dy + h, dx:dx + w]
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
    near[1] = near[1] & dilate(near[0], ADJ_PX)
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
        img.thumbnail((CHECK_PX, CHECK_PX))
    except Exception as e:  # noqa: BLE001 - report and move on
        return [f'{rel}: could not read image ({e})']
    found = badge_regions(img, sig, min_frac, tol)
    if found:
        if 'whole' in found:
            where = 'across the whole image'
        else:
            where = ', '.join(found[:3]) + (f' and {len(found) - 3} more cells' if len(found) > 3 else '')
        return [f'{label or rel}: the retired 2020 badge colours ({where}). '
                f'Rebuild with the current badge from assets/logo/.']
    return []


def check_video(path, rel, sig, min_frac, tol):
    if not shutil.which('ffmpeg'):
        print('check-brand: ffmpeg is not on PATH, cannot check video', file=sys.stderr)
        sys.exit(2)
    hits = []
    with tempfile.TemporaryDirectory() as tmp:
        # Sample the whole video: every VIDEO_STEP_S seconds, or wider on a
        # long one so the samples still reach the end. Never stop early.
        probe = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'csv=p=0', str(path)], capture_output=True, text=True)
        try:
            duration = float(probe.stdout.strip())
        except ValueError:
            return [f'{rel}: could not read video duration, so it was not checked']
        step = max(VIDEO_STEP_S, duration / VIDEO_MAX_FRAMES)
        run = subprocess.run(
            ['ffmpeg', '-loglevel', 'error', '-i', str(path),
             '-vf', f'fps=1/{step:.3f},scale=1080:-2', f'{tmp}/f%04d.png'],
            capture_output=True, text=True)
        if run.returncode != 0:
            # An unchecked video is not a clean one, so it counts as a finding.
            err = (run.stderr.strip().splitlines() or ['no output'])[-1]
            return [f'{rel}: could not read video, so it was not checked ({err})']
        frames = sorted(Path(tmp).glob('f*.png'))
        bad = []
        for i, f in enumerate(frames):
            if check_image(f, rel, sig, min_frac, tol):
                bad.append(int(i * step))
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
    out = subprocess.run(['git', '-C', str(REPO), 'ls-files', '-z', '-co', '--exclude-standard'],
                         capture_output=True, check=True).stdout.decode().split('\0')
    return [REPO / p for p in out if p and (REPO / p).is_file()]


def staged_files(tmp):
    """Copy the staged version of every added or changed file into tmp, so the
    pre-commit hook checks what is about to be committed, not the working tree.
    Returns (copy, repo-relative path) pairs."""
    names = subprocess.run(
        ['git', '-C', str(REPO), 'diff', '--cached', '--name-only', '-z', '--diff-filter=ACMR'],
        capture_output=True, check=True).stdout.decode().split('\0')
    out = []
    for name in filter(None, names):
        dst = Path(tmp) / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(subprocess.run(['git', '-C', str(REPO), 'show', f':{name}'],
                                       capture_output=True, check=True).stdout)
        out.append((dst, Path(name)))
    return out


def check_one(f, rel, colors, sig, min_frac, tol):
    ext = f.suffix.lower()
    in_source = '_source' in Path(rel).parts
    if ext in IMAGE_EXT and not in_source:
        return check_image(f, rel, sig, min_frac, tol)
    if ext in VIDEO_EXT:
        return check_video(f, rel, sig, min_frac, tol)
    if ext in TEXT_EXT and not in_source:
        return check_text(f, colors, rel)
    return []


def main(argv):
    colors, sig, min_frac, tol = load_rules()
    hits = []
    if argv == ['--staged']:
        with tempfile.TemporaryDirectory() as tmp:
            pairs = staged_files(tmp)
            for f, rel in pairs:
                hits += check_one(f, rel, colors, sig, min_frac, tol)
        return report(hits, len(pairs))
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
            seen = set(files)
            files += [f for f in walk(exports) if f not in seen]
    for f in files:
        try:
            rel = f.relative_to(REPO)
        except ValueError:
            rel = f
        hits += check_one(f, rel, colors, sig, min_frac, tol)
    return report(hits, len(files))


def report(hits, n):
    for h in hits:
        print(h)
    if hits:
        print(f'\ncheck-brand: {len(hits)} finding(s). Retired colours are listed in '
              f'brand/tokens.json under deprecated.', file=sys.stderr)
        return 1
    print(f'check-brand: clean ({n} files checked).')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
