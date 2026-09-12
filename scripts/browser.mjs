/* Resolve a Chromium executable.

   The image ships Chromium under PLAYWRIGHT_BROWSERS_PATH, but the npm
   playwright version may expect a different build number than the one
   installed. Rather than downloading a second copy, find what is here.
   Returns an options object for chromium.launch(). */

import { existsSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

const CANDIDATE_SUFFIXES = [
  'chrome-linux/chrome',
  'chrome-linux/headless_shell',
  'chrome-headless-shell-linux64/chrome-headless-shell',
  'Chromium.app/Contents/MacOS/Chromium',
];

export function chromiumLaunchOptions() {
  const root = process.env.PLAYWRIGHT_BROWSERS_PATH;
  if (!root || !existsSync(root)) return {};

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
  return {};
}
