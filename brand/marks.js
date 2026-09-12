/* RITC marks. Renders the badge, the anchor, the star, and the star column.
   Every mark looks for a real file in assets/logo/ first and falls back to a
   labeled placeholder, so nothing ships looking finished when it is not.

   No hardcoded colors here. Marks inherit currentColor or read a token. */

const RITC_LOGO_DIR = 'assets/logo/';

/* The circular badge. Returns an element. Pass the diameter in px. */
function ritcBadge(diameter = 140) {
  const wrap = document.createElement('div');
  wrap.className = 'ritc-badge';
  wrap.style.width = diameter + 'px';
  wrap.style.height = diameter + 'px';

  const img = document.createElement('img');
  img.alt = 'Rhode Island Track Club';
  img.src = RITC_LOGO_DIR + 'ritc-badge.svg';

  const placeholder = document.createElement('div');
  placeholder.className = 'ritc-badge__placeholder';
  placeholder.innerHTML =
    '<span>BADGE</span><span>PLACEHOLDER</span><span class="ritc-badge__note">assets/logo/</span>';
  placeholder.hidden = true;

  /* Try SVG, then PNG, then show the placeholder. */
  let tried = 0;
  img.onerror = () => {
    tried += 1;
    if (tried === 1) { img.src = RITC_LOGO_DIR + 'ritc-badge.png'; return; }
    img.hidden = true;
    placeholder.hidden = false;
  };

  wrap.append(img, placeholder);
  return wrap;
}

/* One five point star as inline SVG, inheriting currentColor. */
function ritcStar(size = 28) {
  const ns = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(ns, 'svg');
  svg.setAttribute('viewBox', '0 0 100 95');
  svg.setAttribute('width', size);
  svg.setAttribute('height', Math.round(size * 0.95));
  svg.setAttribute('aria-hidden', 'true');
  const path = document.createElementNS(ns, 'path');
  path.setAttribute('fill', 'currentColor');
  path.setAttribute('d', 'M50 0 L61.8 34.5 L98.8 34.5 L68.9 56 L80.5 90.5 L50 69 L19.5 90.5 L31.1 56 L1.2 34.5 L38.2 34.5 Z');
  svg.appendChild(path);
  return svg;
}

/* The repeating star column from the singlet's front seam.
   An inner-layer element. Fills its container's height. */
function ritcStarColumn(container, starSize = 26) {
  const height = container.clientHeight;
  const pitch = starSize * 2.6;
  const count = Math.max(1, Math.floor(height / pitch));
  container.innerHTML = '';
  for (let i = 0; i < count; i += 1) container.appendChild(ritcStar(starSize));
  return count;
}

/* Paint every mark slot on the page. Call once after layout settles. */
function ritcPaintMarks() {
  document.querySelectorAll('[data-ritc-badge]').forEach((el) => {
    const d = Number(el.getAttribute('data-ritc-badge')) || 140;
    el.replaceChildren(ritcBadge(d));
  });
  document.querySelectorAll('[data-ritc-star-column]').forEach((el) => {
    const s = Number(el.getAttribute('data-ritc-star-column')) || 26;
    ritcStarColumn(el, s);
  });
}

/* ---------------------------------------------------------------------------
   Headline auto-fit.

   A display headline is set at --fs-display, which fits a short race name and
   overflows a long one. Rather than asking the editor to guess a size, shrink
   to fit.

   Line counting is done with Range client rects, one rect per line box, not
   by dividing scrollHeight by line-height. The display scale runs a
   line-height below 1, so scrollHeight always exceeds clientHeight even on a
   single line, and a height-based count reports 1 line for everything.

   Returns the size landed on. */
function ritcCountLines(el) {
  const range = document.createRange();
  range.selectNodeContents(el);
  const rects = Array.from(range.getClientRects()).filter((r) => r.height > 0);
  if (!rects.length) return 0;
  // Rects can split mid-line across text nodes, so group by top edge.
  const tops = new Set(rects.map((r) => Math.round(r.top)));
  return tops.size;
}

function ritcFitText(el, { maxLines = 3, min = 44, step = 2, maxHeight = null } = {}) {
  const limit = maxHeight ?? el.parentElement.clientHeight;
  let size = parseFloat(getComputedStyle(el).fontSize);

  const overflows = () =>
    el.scrollWidth > el.clientWidth + 1 ||
    ritcCountLines(el) > maxLines ||
    el.getBoundingClientRect().height > limit;

  while (size > min && overflows()) {
    size -= step;
    el.style.fontSize = size + 'px';
  }
  return size;
}

/* Long single tokens like a placeholder or a hyphenless race name must be
   allowed to break, or no font size is small enough. */
function ritcAllowBreak(el) {
  el.style.overflowWrap = 'break-word';
  el.style.wordBreak = 'break-word';
}
