// news-image-20261120 entry (Node 22, standard library only).
//
// The finished artwork ships in this repository as entry.png, next to this
// file. The grader mounts the repository and expects the program to place
// the image at /output/entry.png; this program copies the shipped bytes
// there unchanged, after checking the file exists, carries the PNG magic
// bytes, stays within the 1 MiB cap and has IHDR dimensions no larger
// than 1024x1024. Any failed check throws, so a damaged snapshot fails
// loudly instead of delivering nothing.
//
// Locally, MAKEFUN_OUTPUT_DIR overrides the destination:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const SIZE_CAP = 1_048_576; // 1 MiB, the competition's limit
const DIMENSION_CAP = 1024;
const PNG_MAGIC = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];

const imagePath = fileURLToPath(new URL('./entry.png', import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const outPath = join(outDir, 'entry.png');

let image: Buffer;
try {
  image = readFileSync(imagePath);
} catch {
  throw new Error(`entry.png is missing beside main.ts (looked at ${imagePath})`);
}

const magicOk =
  image.length >= PNG_MAGIC.length &&
  PNG_MAGIC.every((b, i) => image[i] === b);
if (!magicOk) {
  throw new Error('entry.png does not begin with the PNG signature');
}
if (image.length > SIZE_CAP) {
  throw new Error(`entry.png weighs ${image.length} bytes, over the ${SIZE_CAP} cap`);
}

// IHDR is the first chunk: its type sits at bytes 12..16 and its payload
// starts with width and height as big-endian uint32s at bytes 16..24.
if (image.toString('ascii', 12, 16) !== 'IHDR') {
  throw new Error('entry.png has no IHDR chunk at the expected offset');
}
const w = image.readUInt32BE(16);
const h = image.readUInt32BE(20);
if (w > DIMENSION_CAP || h > DIMENSION_CAP) {
  throw new Error(`entry.png is ${w}x${h}, over the ${DIMENSION_CAP}px cap`);
}

mkdirSync(outDir, { recursive: true });
writeFileSync(outPath, image);
console.log(`wrote ${outPath} (${image.length} bytes, ${w}x${h})`);
