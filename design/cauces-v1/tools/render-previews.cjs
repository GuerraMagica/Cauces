// Optional design export tool. Uses an existing sharp installation; no downloads.
const fs = require('node:fs/promises');
const path = require('node:path');
const sharp = require('sharp');
const root = path.resolve(__dirname, '..');
(async () => {
  for (const theme of ['proposal','templates']) {
    for (const name of ['empty','ready','processing','review','exported','error','empty-compact','control-states']) {
      const input = path.join(root, theme, name+'.svg');
      const metadata = await sharp(input).metadata();
      await sharp(input).resize(metadata.width*2,metadata.height*2).png().toFile(path.join(root,'previews',theme+'-'+name+'@2x.png'));
    }
  }
  for (const name of ['design-board','app-icon-concept']) {
    await sharp(path.join(root,'proposal',name+'.svg')).png().toFile(path.join(root,'previews',name+'.png'));
  }
  for (const name of ['flow-mark-color','flow-mark-mono']) {
    await sharp(path.join(root,'assets/brand',name+'.svg')).resize(192,192).png().toFile(path.join(root,'previews',name+'@2x.png'));
  }
  console.log('20 PNG previews exported locally.');
})().catch(error => {console.error(error.message);process.exit(1)});
