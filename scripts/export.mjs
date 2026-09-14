/* Render every template in templates/ to a PNG at 2x.

   Output goes to exports/, which is gitignored. The screenshot is clipped to
   the .ritc-canvas element rather than the viewport, so the file is exactly
   the template's declared size times the scale factor, regardless of the
   window. A viewport-sized screenshot drifts; an element clip does not.

   Usage:
     node scripts/export.mjs                      all templates at 2x
     node scripts/export.mjs workout-announcement one template
     node scripts/export.mjs --scale 1            override the scale factor
*/

import { chromium } from 'playwright';
import { chromiumLaunchOptions } from './browser.mjs';
import { readdirSync, mkdirSync, existsSync } from 'node:fs';
import { join, resolve, basename } from 'node:path';
import { pathToFileURL } from 'node:url';

const REPO = resolve(import.meta.dirname, '..');
const TEMPLATES = join(REPO, 'templates');
const OUT = join(REPO, 'exports');

function parseArgs(argv) {
  const names = [];
  let scale = 2;
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === '--scale') { scale = Number(argv[i + 1]); i += 1; continue; }
    names.push(basename(argv[i], '.html'));
  }
  if (!Number.isFinite(scale) || scale <= 0) throw new Error(`bad --scale: ${scale}`);
  return { names, scale };
}

const { names, scale } = parseArgs(process.argv.slice(2));

if (!existsSync(TEMPLATES)) {
  console.error('No templates/ directory.');
  process.exit(1);
}

let files = readdirSync(TEMPLATES).filter((f) => f.endsWith('.html')).sort();
if (names.length) files = files.filter((f) => names.includes(basename(f, '.html')));

if (!files.length) {
  console.error(names.length ? `No template matched: ${names.join(', ')}` : 'No templates found.');
  process.exit(1);
}

mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch(chromiumLaunchOptions());
let failed = 0;

for (const file of files) {
  const name = basename(file, '.html');
  const page = await browser.newPage({
    deviceScaleFactor: scale,
    // Generous viewport so no canvas is constrained; the clip decides the file.
    viewport: { width: 1200, height: 2000 },
  });

  const problems = [];
  page.on('pageerror', (e) => problems.push(`js: ${e.message}`));
  // Every asset matters now that the logo files exist. A silently missing
  // badge is exactly the failure this is here to catch.
  page.on('requestfailed', (r) => problems.push(`load: ${r.url()}`));

  try {
    await page.goto(pathToFileURL(join(TEMPLATES, file)).href);
    await page.waitForFunction(
      () => document.documentElement.dataset.ritcReady === '1',
      { timeout: 15000 },
    );

    const canvas = page.locator('.ritc-canvas').first();
    const box = await canvas.boundingBox();
    const out = join(OUT, `${name}.png`);
    await canvas.screenshot({ path: out, scale: 'device' });

    // A visible placeholder means a mark did not load. Fail loudly.
    const placeholders = await page.locator('.ritc-badge__placeholder:not([hidden])').count();
    if (placeholders) problems.push(`${placeholders} logo placeholder(s) still visible`);

    const px = `${Math.round(box.width * scale)}x${Math.round(box.height * scale)}`;
    console.log(`  ${name.padEnd(26)} ${px.padEnd(11)} ${problems.length ? 'WARN ' + problems.join('; ') : 'ok'}`);
    if (problems.length) failed += 1;
  } catch (err) {
    console.error(`  ${name.padEnd(26)} FAILED  ${err.message.split('\n')[0]}`);
    failed += 1;
  } finally {
    await page.close();
  }
}

await browser.close();
console.log(`\n${files.length} template(s) at ${scale}x into exports/`);
if (failed) {
  console.error(`${failed} had problems.`);
  process.exit(1);
}
