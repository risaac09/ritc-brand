#!/usr/bin/env python3
"""Build every logo file in assets/logo/ from the 2020 master JPGs.

The masters are CMYK JPEGs on a solid white square, drawn in the 2020 bright
blue and yellow. Those colours are retired (brand/tokens.json, deprecated). This
script never ships them: it works out, pixel by pixel, how much of each pixel
was field, rope or anchor in the master, then repaints it in the 2026 singlet
palette named in tokens.json under mark.variants. Anti-aliased edges keep their
blend, so the rope and the wordmark stay as crisp as the master.

What is faithful here:
  - The PNGs. The white square outside the badge circle is removed with a
    geometric circular mask, so no pixel inside the badge is moved. Colour is
    remapped, geometry is not.
  - The badge SVG. The committed trace of the 2020 PNG lives in _source/, and
    each fill is repainted with the same remap. No tracer is needed for it.

What is an approximation:
  - The anchor, lifted out of the badge. See assets/logo/README.md.

Colours come from brand/tokens.json only. No hex is written in this file.
"""

import json, re, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / 'assets/logo/_source'
OUT = REPO / 'assets/logo'
COMMITTED = OUT
TOKENS = json.loads((REPO / 'brand/tokens.json').read_text())
SS = 4  # supersample factor for a clean mask edge
SIZES = (1024, 512, 256, 128)
RIM = 0.975  # outside this fraction of the radius, master white is background bleed


def hex_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def palette(name):
    """Look a palette entry up by name in color.primary or color.secondary."""
    for group in ('primary', 'secondary'):
        entry = TOKENS['color'][group].get(name)
        if entry:
            return hex_rgb(entry['hex'])
    sys.exit(f'tokens.json has no palette colour named {name!r}')


SOURCE = {k: hex_rgb(v) for k, v in TOKENS['deprecated']['badgeSource'].items()
          if not k.startswith('$')}
NAVY = palette('deepNavy')
ANCHOR_COLORS = {
    'navy': NAVY,
    'white': palette('white'),
    'teal': palette('babyOceanBlue'),  # file name kept so existing paths hold
}


def unmix(rgb):
    """Weights of (field, rope, anchor) that best rebuild each pixel from the
    master's three colours. Least squares with the weights held to sum to one,
    then clipped and renormalised. rgb is (..., 3) float."""
    m = np.array([SOURCE['field'], SOURCE['rope'], SOURCE['anchor']], float).T
    k = 50.0  # weight of the sum-to-one row
    a = np.vstack([m, k * np.ones((1, 3))])
    shape = rgb.shape[:-1]
    x = rgb.reshape(-1, 3).T
    x = np.vstack([x, k * np.ones((1, x.shape[1]))])
    w, *_ = np.linalg.lstsq(a, x, rcond=None)
    w = np.clip(w, 0, None)
    w /= w.sum(axis=0, keepdims=True) + 1e-9
    return w.T.reshape(*shape, 3)


def remap_badge(src_rgba, variant):
    """Repaint a master-coloured badge in one of mark.variants."""
    a = np.asarray(src_rgba.convert('RGBA')).astype(float)
    w = unmix(a[..., :3])
    # The outer few pixels blend the field with the master's white background.
    # Left alone that white comes back as a light hairline round the badge, so
    # outside RIM any anchor weight is handed to the field.
    h, wd = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:wd]
    rr = np.hypot(xx - (wd - 1) / 2, yy - (h - 1) / 2) / (min(h, wd) / 2)
    rim = rr > RIM
    w[rim, 0] += w[rim, 2]
    w[rim, 2] = 0
    target = np.array([palette(variant['field']), palette(variant['rope']),
                       palette(variant['anchor'])], float)
    rgb = np.clip(np.einsum('...k,kc->...c', w, target), 0, 255)
    out = np.dstack([rgb, a[..., 3]]).astype(np.uint8)
    return Image.fromarray(out)


def remap_bw(src_rgba, variant):
    """The black and white master, repainted dark to light by luminance."""
    a = np.asarray(src_rgba.convert('RGBA')).astype(float)
    lum = np.einsum('...c,c->...', a[..., :3], np.array([0.2126, 0.7152, 0.0722])) / 255.0
    # Same background bleed as the colour master: the rim goes to the dark.
    h, wd = lum.shape
    yy, xx = np.mgrid[0:h, 0:wd]
    lum[np.hypot(xx - (wd - 1) / 2, yy - (h - 1) / 2) / (min(h, wd) / 2) > RIM] = 0.0
    dark, light = np.array(palette(variant['dark']), float), np.array(palette(variant['light']), float)
    rgb = dark + (light - dark) * lum[..., None]
    out = np.dstack([np.clip(rgb, 0, 255), a[..., 3]]).astype(np.uint8)
    return Image.fromarray(out)


def remap_svg(src_svg, dst_svg, variant):
    """Repaint every fill in the 2020 trace with the same remap as the PNGs.

    Each traced path starts at its translate() point, so a path whose start
    sits outside RIM is an edge speck of the master's white background, and
    gets the same rim rule as the PNGs: its anchor share goes to the field."""
    target = np.array([palette(variant['field']), palette(variant['rope']),
                       palette(variant['anchor'])], float)
    view = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', src_svg.read_text())
    vw, vh = float(view.group(1)), float(view.group(2))

    def repl(m):
        tag = m.group(0)
        fill = re.search(r'fill="#([0-9A-Fa-f]{6})"', tag)
        if not fill:
            return tag
        w = unmix(np.array(hex_rgb(fill.group(1)), float)[None, :])[0]
        t = re.search(r'translate\(([-\d.]+),\s*([-\d.]+)\)', tag)
        if t:
            x, y = float(t.group(1)), float(t.group(2))
            if np.hypot(x - vw / 2, y - vh / 2) / (min(vw, vh) / 2) > RIM:
                w = w.copy()
                w[0] += w[2]
                w[2] = 0
        out = np.clip(np.einsum('k,kc->c', w, target), 0, 255).round().astype(int)
        return tag.replace(fill.group(0), f'fill="#{out[0]:02X}{out[1]:02X}{out[2]:02X}"')

    svg = re.sub(r'<path[^>]*>', repl, src_svg.read_text())
    dst_svg.write_text(svg)
    return dst_svg.stat().st_size


def load_rgb(path):
    """CMYK JPEGs from print workflows often come in inverted. Detect by
    checking the corner, which we know is the white background."""
    im = Image.open(path)
    rgb = im.convert('RGB')
    if sum(rgb.getpixel((2, 2))) < 200:  # corner should be near white
        rgb = Image.eval(rgb, lambda v: 255 - v)
    return rgb


def find_circle(rgb, bg_tol=18):
    """Locate the badge circle from the extent of non-background pixels."""
    a = np.asarray(rgb).astype(np.int16)
    non_bg = (np.abs(a - 255).max(axis=2) > bg_tol)
    ys, xs = np.nonzero(non_bg)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    r = (max(x1 - x0, y1 - y0) + 1) / 2.0
    return cx, cy, r


def circular_alpha(size, cx, cy, r, inset=0.5):
    """Supersampled circular alpha mask, so the edge is smooth rather than
    stair stepped. inset pulls the mask in slightly to avoid keeping a hairline
    of the white background at the rim."""
    w, h = size
    big = Image.new('L', (w * SS, h * SS), 0)
    d = ImageDraw.Draw(big)
    rr = (r - inset) * SS
    d.ellipse([cx * SS - rr, cy * SS - rr, cx * SS + rr, cy * SS + rr], fill=255)
    return big.resize((w, h), Image.LANCZOS)


def cut_circle(src_path):
    """The master with the white square outside the circle made transparent,
    cropped tight to the circle. Still in the master's own colours."""
    rgb = load_rgb(src_path)
    cx, cy, r = find_circle(rgb)
    alpha = circular_alpha(rgb.size, cx, cy, r)
    out = rgb.convert('RGBA')
    out.putalpha(alpha)
    pad = 1
    box = (int(cx - r - pad), int(cy - r - pad), int(cx + r + pad), int(cy + r + pad))
    return out.crop(box), (cx, cy, r)


def save_sizes(img, stem):
    made = []
    for px in SIZES:
        name = f'{stem}-{px}.png' if px != 1024 else f'{stem}.png'
        img.resize((px, px), Image.LANCZOS).save(OUT / name, optimize=True)
        made.append((name, px, (OUT / name).stat().st_size))
    return made


def extract_anchor(badge_rgba):
    """The anchor is the white shape inside the field. Lift it by keying
    near-white pixels that sit inside the field of the master, then colour it
    from the palette.

    The wordmark and the rope share one colour in the master, not white, so
    neither is picked up.
    """
    a = np.asarray(badge_rgba).astype(np.int16)
    rgbp, alpha = a[..., :3], a[..., 3]
    h, w = alpha.shape
    cy, cx = h / 2.0, w / 2.0
    yy, xx = np.mgrid[0:h, 0:w]
    # Stay inside the rope border.
    inside = ((xx - cx) ** 2 + (yy - cy) ** 2) < (0.88 * min(h, w) / 2) ** 2
    white = (rgbp.min(axis=2) > 205) & (np.ptp(rgbp, axis=2) < 34)
    mask = (white & inside & (alpha > 128)).astype(np.uint8) * 255
    m = Image.fromarray(mask).filter(ImageFilter.MedianFilter(3))
    # The wordmark sits ON TOP of the white anchor in the badge, so
    # lifting the white shape leaves letter shaped holes. A morphological
    # closing (dilate then erode) heals the shackle ring and the small nicks.
    # It does NOT heal the notch in the shank or the cuts through the flukes,
    # where TRACK and CLUB remove real geometry. Larger kernels fuse the ring
    # into a blob without fixing those, so 15 is where this stops helping.
    m = m.filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.MinFilter(15))
    out = Image.new('RGBA', (w, h), NAVY + (0,))
    out.putalpha(m)
    solid = Image.new('RGBA', (w, h), NAVY + (255,))
    solid.putalpha(m)
    return solid


def add_viewbox(svg_path):
    """VTracer emits width and height but no viewBox, so the SVG has no
    intrinsic aspect ratio and collapses to nothing the moment CSS sets only
    one dimension. Promote the pixel size to a viewBox and drop the fixed
    attributes so the mark scales like a vector should.
    """
    import re as _re
    svg = svg_path.read_text()
    m = _re.search(r'<svg([^>]*)>', svg)
    head = m.group(1)
    w = _re.search(r'width="([\d.]+)"', head)
    h = _re.search(r'height="([\d.]+)"', head)
    if not (w and h) or 'viewBox' in head:
        return svg_path.stat().st_size
    new_head = _re.sub(r'\s*(width|height)="[\d.]+"', '', head)
    new_head += f' viewBox="0 0 {w.group(1)} {h.group(1)}"'
    svg = svg.replace(m.group(0), f'<svg{new_head}>', 1)
    svg_path.write_text(svg)
    return svg_path.stat().st_size


def trace_svg(png_path, svg_path, mode='spline', color_precision=6,
              filter_speckle=6):
    """Colour trace, used for the full badge."""
    import vtracer
    vtracer.convert_image_to_svg_py(
        str(png_path), str(svg_path),
        colormode='color', mode=mode,
        filter_speckle=filter_speckle,
        color_precision=color_precision,
        path_precision=3,
    )
    return add_viewbox(svg_path)


def trace_silhouette(rgba_png, svg_path, upscale=2, speckle=12):
    """Trace a single solid shape into one recolourable path.

    A colour trace of a flat silhouette produces stair stepped edges and breaks
    thin features apart, which is what happened to the anchor's shank on the
    first attempt. Instead: take the alpha channel, upsample it, threshold it
    to hard black on white, and run a binary trace. The result is one path,
    which we then set to fill="currentColor" so a template can recolour it in
    CSS instead of shipping a PNG per colour.
    """
    import vtracer, tempfile, os, re as _re
    im = Image.open(rgba_png).convert('RGBA')
    a = im.getchannel('A').resize(
        (im.width * upscale, im.height * upscale), Image.LANCZOS)
    # Hard threshold, then a light blur/rethreshold to smooth the staircase.
    a = a.point(lambda v: 255 if v > 128 else 0)
    a = a.filter(ImageFilter.GaussianBlur(upscale * 0.6))
    a = a.point(lambda v: 255 if v > 128 else 0)
    flat = Image.new('RGB', a.size, (255, 255, 255))
    flat.paste((0, 0, 0), mask=a)

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as t:
        tmp = t.name
    flat.save(tmp)
    try:
        vtracer.convert_image_to_svg_py(
            tmp, str(svg_path),
            colormode='binary', mode='spline',
            filter_speckle=speckle, path_precision=2,
        )
    finally:
        os.unlink(tmp)

    svg = svg_path.read_text()
    # Drop the white background rect the tracer emits, and make the shape
    # inherit colour from CSS.
    svg = _re.sub(r'<path[^>]*fill="#FFFFFF"[^>]*/>\s*', '', svg, flags=_re.I)
    svg = _re.sub(r'fill="#0{6}"', 'fill="currentColor"', svg, flags=_re.I)
    svg = _re.sub(r'fill="#000"', 'fill="currentColor"', svg, flags=_re.I)
    svg_path.write_text(svg)
    return add_viewbox(svg_path), svg.count('<path')


def main(quiet=False):
    OUT.mkdir(parents=True, exist_ok=True)
    report = []
    variants = TOKENS['mark']['variants']

    master, circle = cut_circle(SRC / 'ritc-badge-color-master.jpg')
    for key, stem in (('default', 'ritc-badge'), ('ocean', 'ritc-badge-ocean'),
                      ('ebony', 'ritc-badge-ebony')):
        report.append((f'badge {key} PNGs', save_sizes(remap_badge(master, variants[key]), stem), circle))

    master_bw, circle_bw = cut_circle(SRC / 'ritc-badge-bw-master.jpg')
    report.append(('badge bw PNGs', save_sizes(remap_bw(master_bw, variants['bw']), 'ritc-badge-bw'), circle_bw))

    anchor = extract_anchor(master)
    anchor = anchor.crop(anchor.getbbox())
    anchor_alpha = anchor.getchannel('A')
    made_anchor = []
    for cname, rgb in ANCHOR_COLORS.items():
        tinted = Image.new('RGBA', anchor.size, rgb + (255,))
        tinted.putalpha(anchor_alpha)
        for px in (1024, 512, 256):
            suffix = '' if px == 1024 else f'-{px}'
            wr = int(px * anchor.width / anchor.height)
            name = f'ritc-anchor-{cname}{suffix}.png'
            tinted.resize((wr, px), Image.LANCZOS).save(OUT / name, optimize=True)
            made_anchor.append(name)
    # Default un-suffixed anchor is navy, so a template can reference it plainly.
    navy_full = Image.new('RGBA', anchor.size, NAVY + (255,))
    navy_full.putalpha(anchor_alpha)
    navy_full.save(OUT / 'ritc-anchor.png', optimize=True)
    report.append(('anchor PNGs', [(f'{len(made_anchor)} files', anchor.size, 0)], None))

    trace = SRC / 'ritc-badge-2020-trace.svg'
    if not trace.exists():
        sys.exit(f'missing {trace}')
    svgs = [('ritc-badge.svg', remap_svg(trace, OUT / 'ritc-badge.svg', variants['default'])),
            ('ritc-badge-ocean.svg', remap_svg(trace, OUT / 'ritc-badge-ocean.svg', variants['ocean'])),
            ('ritc-badge-ebony.svg', remap_svg(trace, OUT / 'ritc-badge-ebony.svg', variants['ebony']))]
    # The anchor SVG is a binary trace and needs vtracer (pip install vtracer).
    # It carries fill="currentColor", so it holds no colour and rarely needs a
    # rebuild; skip it rather than fail when the tracer is missing.
    try:
        import vtracer  # noqa: F401
        if not quiet:
            svgs.append(('ritc-anchor.svg',
                         trace_silhouette(OUT / 'ritc-anchor.png', OUT / 'ritc-anchor.svg')))
    except ImportError:
        svgs.append(('ritc-anchor.svg', 'kept as committed (vtracer not installed)'))
    report.append(('SVGs', svgs, None))

    for title, items, circle in ([] if quiet else report):
        print(f'\n{title}:')
        for it in items:
            print('   ', it)
        if circle:
            print(f'    circle center=({circle[0]:.1f},{circle[1]:.1f}) r={circle[2]:.1f}')


def verify():
    """Rebuild into a scratch folder and compare with the committed files, so
    CI can prove every badge file still comes out of tokens.json. PNGs are
    compared by pixel, not by byte, because encoders differ between Pillow
    versions. Exit 1 on any difference."""
    global OUT
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        OUT = Path(tmp)
        main(quiet=True)
        bad = []
        for built in sorted(OUT.iterdir()):
            committed = COMMITTED / built.name
            if built.name == 'ritc-anchor.svg':
                continue  # needs vtracer; holds no colour
            if not committed.exists():
                bad.append(f'{built.name}: built but not committed')
            elif built.suffix == '.png':
                a = np.asarray(Image.open(built).convert('RGBA')).astype(int)
                b = np.asarray(Image.open(committed).convert('RGBA')).astype(int)
                if a.shape != b.shape or np.abs(a - b).max() > 1:
                    bad.append(f'{built.name}: committed pixels differ from the build')
            elif built.read_bytes() != committed.read_bytes():
                bad.append(f'{built.name}: committed file differs from the build')
    for b in bad:
        print(b)
    if bad:
        print('\nRun scripts/build-logo-assets.py and commit the result.', file=sys.stderr)
        sys.exit(1)
    print('build-logo-assets: committed files match tokens.json.')


if __name__ == '__main__':
    verify() if '--verify' in sys.argv[1:] else main()
