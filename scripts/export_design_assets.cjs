// Build-time only: SVG sources remain editable in the designer handoff.
const fs = require('node:fs/promises');
const path = require('node:path');
const sharp = require('sharp');
(async () => {
  const root = path.resolve(__dirname, '..');
  const iconset = path.join(root, 'build', 'Cauces.iconset');
  await fs.mkdir(iconset, { recursive: true });
  const icon = path.join(root, 'design/cauces-v1/proposal/app-icon-concept.svg');
  for (const size of [16, 32, 128, 256, 512]) {
    for (const scale of [1, 2]) {
      await sharp(icon).resize(size * scale, size * scale).png().toFile(path.join(iconset, `icon_${size}x${size}${scale === 2 ? '@2x' : ''}.png`));
    }
  }
  for (const scale of [1, 2]) {
    await sharp(path.join(root, 'design/cauces-v1/assets/brand/flow-hero-dark.svg'))
      .resize(500 * scale, 175 * scale).png()
      .toFile(path.join(root, `resources/FlowArtwork${scale === 2 ? '@2x' : ''}.png`));
  }
  console.log('Flow artwork and macOS iconset exported');
})().catch(error => { console.error(error); process.exit(1); });
