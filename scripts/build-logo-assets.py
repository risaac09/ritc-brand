#!/usr/bin/env python3
"""Build transparent PNGs and traced SVGs from the 2020 master badge JPGs.

The masters are CMYK JPEGs on a solid white square. They are raster, they have
no alpha, and they predate the 2026 kit. Everything this script produces is
derived from them, so it inherits their limits. Read assets/logo/README.md
before using any of it.

What is faithful here:
  - The transparent PNGs. The white square outside the badge circle is removed
    with a geometric circular mask, so no pixel inside the badge is touched.
    The white anchor survives because the mask is positional, not color keyed.

What is an approximation:
  - The SVGs. They are machine traces of a 1025px raster, not a redraw. The
    rope border and the wordmark will not survive scrutiny at large sizes.
"""

import subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / 'assets/logo/_source'
OUT = REPO / 'assets/logo'
SS = 4  # supersample factor for a clean mask edge

BADGE_BLUE = (14, 92, 198)
BADGE_YELLOW = (245, 224, 86)
NAVY = (1, 30, 61)
ANCHOR_COLORS = {
    'navy': NAVY,
    'white': (255, 255, 255),
    'teal': (162, 201, 207),
}


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


def build_transparent(src_path, stem):
    rgb = load_rgb(src_path)
    cx, cy, r = find_circle(rgb)
    alpha = circular_alpha(rgb.size, cx, cy, r)
    out = rgb.convert('RGBA')
    out.putalpha(alpha)
    # Crop tight to the circle so the asset has no dead margin.
    pad = 1
    box = (int(cx - r - pad), int(cy - r - pad), int(cx + r + pad), int(cy + r + pad))
    out = out.crop(box)
    made = []
    for px in (1024, 512, 256, 128):
        name = f'{stem}-{px}.png' if px != 1024 else f'{stem}.png'
        im = out.resize((px, px), Image.LANCZOS)
        im.save(OUT / name, optimize=True)
        made.append((name, px, (OUT / name).stat().st_size))
    return made, (cx, cy, r), out


def extract_anchor(badge_rgba):
    """The anchor is the white shape inside the blue field. Lift it by keying
    near-white pixels that sit inside the field, then recolor to navy so the
    standalone mark matches the 2026 palette rather than the 2020 one.

    The wordmark is yellow and the rope is yellow, so neither is picked up.
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
    m = Image.fromarray(mask, 'L').filter(ImageFilter.MedianFilter(3))
    # The yellow wordmark sits ON TOP of the white anchor in the badge, so
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


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report = []

    color_src = SRC / 'ritc-badge-color-master.jpg'
    bw_src = SRC / 'ritc-badge-bw-master.jpg'

    made, circle, badge = build_transparent(color_src, 'ritc-badge')
    report.append(('badge color PNGs', made, circle))

    made_bw, circle_bw, _ = build_transparent(bw_src, 'ritc-badge-bw')
    report.append(('badge bw PNGs', made_bw, circle_bw))

    anchor = extract_anchor(badge)
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

    svgs = []
    # Badge: colour trace off the largest PNG so the rope survives.
    svgs.append(('ritc-badge.svg',
                 trace_svg(OUT / 'ritc-badge.png', OUT / 'ritc-badge.svg',
                           color_precision=6, filter_speckle=8)))
    # Anchor: one recolourable path.
    svgs.append(('ritc-anchor.svg',
                 trace_silhouette(OUT / 'ritc-anchor.png', OUT / 'ritc-anchor.svg')))
    report.append(('SVG traces', svgs, None))

    for title, items, circle in report:
        print(f'\n{title}:')
        for it in items:
            print('   ', it)
        if circle:
            print(f'    circle center=({circle[0]:.1f},{circle[1]:.1f}) r={circle[2]:.1f}')


if __name__ == '__main__':
    main()
