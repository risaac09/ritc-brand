/* Resolve a Chromium executable.

   Three cases, in order of preference:

   1. PLAYWRIGHT_BROWSERS_PATH is set (the container image does this). The npm
      playwright version may expect a different build number than the one
      installed there, so find what is actually present rather than letting
      Playwright fail on a version mismatch.
   2. Playwright's own default cache holds a browser. Return empty options and
      let Playwright resolve it itself, which keeps us on the build it expects.
   3. Nothing managed is installed. On a Mac, fall back to Google Chrome so the
      export still runs, and say so, because it is not the same renderer.

   Returns an options object for chromium.launch(). */

import { existsSync, readdirSync } from 'node:fs';
import { homedir } from 'node:os';
import { join } from 'node:path';

const CANDIDATE_SUFFIXES = [
  'chrome-linux/chrome',
  'chrome-linux/headless_shell',
  'chrome-headless-shell-linux64/chrome-headless-shell',
  'Chromium.app/Contents/MacOS/Chromium',
];

/* Where Playwright keeps browsers when PLAYWRIGHT_BROWSERS_PATH is unset. */
function defaultCacheDir() {
  if (process.platform === 'darwin') return join(homedir(), 'Library', 'Caches', 'ms-playwright');
  if (process.platform === 'win32') return join(homedir(), 'AppData', 'Local', 'ms-playwright');
  return join(homedir(), '.cache', 'ms-playwright');
}

function hasManagedChromium(dir) {
  if (!dir || !existsSync(dir)) return false;
  return readdirSync(dir).some((d) => d.startsWith('chromium'));
}

export function chromiumLaunchOptions() {
  const root = process.env.PLAYWRIGHT_BROWSERS_PATH;

  if (root && existsSync(root)) {
    const dirs = readdirSync(root)
      .filter((d) => d.startsWith('chromium'))
      // Prefer a full chromium build over a headless shell.
      .sort((a, b) => (a.includes('headless') ? 1 : 0) - (b.includes('headless') ? 1 : 0));

    for (const dir of dirs) {
      for (const suffix of CANDIDATE_SUFFIXES) {
        const exe = join(root, dir, suffix);
        if (existsSync(exe)) return { executablePath: exe };
      }
    }
  }

  /* Playwright's own cache has a build. Let Playwright pick it, so we stay on
     the version this playwright package expects. */
  if (hasManagedChromium(defaultCacheDir())) return {};

  return macChrome();
}

/* No managed browser anywhere. On a Mac with Google Chrome installed, use it
   rather than failing the export outright.

   This is a fallback, not a preference. Chrome and Chromium do not measure
   text identically, and the templates choose font sizes from measured text,
   so the same source can export at a different size on a machine that has
   Playwright's Chromium installed. Chrome also auto-updates underneath you.
   Say which engine ran so the divergence is visible rather than silent. Run
   `npx playwright install chromium` to get the reproducible one. */
function macChrome() {
  const chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
  if (process.platform === 'darwin' && existsSync(chrome)) {
    console.warn('  renderer: Google Chrome (fallback). Exports may differ from Playwright Chromium.');
    console.warn('  run `npx playwright install chromium` for a reproducible renderer.');
    return { executablePath: chrome };
  }
  return {};
}
