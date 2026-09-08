/* Optional browser integration test. Requires Playwright and an installed Chromium browser.
   Set NODE_PATH for Playwright if needed; pass --browser C:/path/to/chrome.exe.
   Screenshots/downloads stay in ignored dev/generated/catalog-qa/. */
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const {pathToFileURL} = require('node:url');
const root = path.resolve(__dirname, '../..');
const qa = path.join(root, 'dev/generated/catalog-qa');
const browserArg = process.argv.indexOf('--browser');
(async () => {
  fs.mkdirSync(qa, {recursive:true});
  const browser = await chromium.launch({headless:true,
    ...(browserArg >= 0 ? {executablePath:process.argv[browserArg+1]} : {})});
  try {
    const page = await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});
    const errors = []; page.on('pageerror', error => errors.push(error.message));
    await page.goto(pathToFileURL(path.join(root,'dev/generated/asset-catalog/index.html')).href);
    await page.waitForSelector('.card');
    assert.equal(await page.locator('.card').count(), 48);
    await page.locator('#search').fill('Moblin');
    await page.getByRole('button',{name:'Inspect spr_Moblin_High_DrawA',exact:true}).click();
    await page.waitForFunction(() => document.querySelector('#preview').width === 64 && previewImage !== null);
    assert.equal(await page.locator('#inspector .inspect-name').textContent(),'spr_Moblin_High_DrawA');
    assert.deepEqual(await page.locator('#variant option').evaluateAll(nodes => nodes.map(n => n.value)), ['', 'MoblA01', 'MoblA02', 'MoblA03']);
    await page.getByLabel('Origin',{exact:true}).uncheck();
    const rawPixels = await page.locator('#preview').evaluate(c => Array.from(c.getContext('2d').getImageData(0,0,c.width,c.height).data));
    await page.locator('#variant').selectOption('MoblA01');
    assert.equal(await page.locator('#palette').inputValue(), 'PAL_MOB_ORG1');
    const orangePixels = await page.locator('#preview').evaluate(c => Array.from(c.getContext('2d').getImageData(0,0,c.width,c.height).data));
    assert.notDeepEqual(orangePixels,rawPixels);
    // Independent expected RGB values from p_init/build_pal, including second quartet aliases.
    const expected = rawPixels.slice();
    const swaps = new Map([['255,255,255','252,252,252'],['255,0,0','252,152,56'],['0,0,255','216,40,0'],['0,255,0','1,1,1'],['255,255,0','252,252,252'],['255,0,255','252,152,56'],['0,0,0','216,40,0'],['0,255,255','1,1,1']]);
    for(let i=0;i<expected.length;i+=4) {
      const rgb=expected.slice(i,i+3).join(',');
      if(rgb==='127,127,127') expected.splice(i,4,0,0,0,0);
      else if(expected[i+3]===255 && swaps.has(rgb)) expected.splice(i,3,...swaps.get(rgb).split(',').map(Number));
    }
    assert.deepEqual(orangePixels,expected);
    await page.locator('#variant').selectOption('MoblA03');
    assert.equal(await page.locator('#palette').inputValue(), 'PAL_MOB_BLU1');
    const blue1 = await page.locator('#preview').evaluate(c => c.toDataURL());
    await page.locator('#palette').selectOption('PAL_MOB_BLU2');
    assert.notEqual(await page.locator('#preview').evaluate(c => c.toDataURL()),blue1);
    // Every extracted preset can be selected without canvas taint, including file://.
    for(const value of await page.locator('#palette option').evaluateAll(nodes => nodes.map(n=>n.value))) await page.locator('#palette').selectOption(value);
    await page.locator('#palette').selectOption('');
    assert.deepEqual(await page.locator('#preview').evaluate(c => Array.from(c.getContext('2d').getImageData(0,0,c.width,c.height).data)),rawPixels);
    await page.locator('#palette').selectOption('PAL_MOB_BLU2');
    await page.getByRole('button',{name:'+ Add to brief',exact:true}).click();
    await page.screenshot({path:path.join(qa,'catalog-desktop.png'),fullPage:true});
    await page.locator('#search').fill('spr_Item_Bottle');
    await page.getByRole('button',{name:'Inspect spr_Item_Bottle',exact:true}).click();
    await page.waitForFunction(() => previewImage !== null);
    await page.locator('#variant').selectOption('ItmE001');
    assert.equal(await page.locator('#palette').inputValue(),'PAL_MOB_RED1');
    const redJar = await page.locator('#preview').evaluate(c => c.toDataURL());
    await page.locator('#variant').selectOption('ItmE002');
    assert.equal(await page.locator('#palette').inputValue(),'PAL_MOB_BLU1');
    assert.notEqual(await page.locator('#preview').evaluate(c=>c.toDataURL()),redJar);
    await page.locator('#search').fill('zz-no-such-asset');
    assert.match(await page.locator('#results').textContent(),/^0 matches/);
    await page.locator('#search').fill('');
    await page.locator('#kind').selectOption('background');
    await page.locator('#search').fill('ts_tile_marker_1a_8x8');
    await page.getByRole('button',{name:'Inspect ts_tile_marker_1a_8x8',exact:true}).click();
    await page.waitForFunction(() => previewImage !== null);
    await page.locator('#preview').click({position:{x:20,y:20}});
    assert.match(await page.locator('#tile-readout').textContent(),/tile 17 /);
    await page.getByRole('button',{name:'+ Add to brief',exact:true}).click();
    await page.getByRole('button',{name:/Reference brief/}).click();
    await page.locator('#brief-title').fill('Moblin courtyard');
    await page.locator('#brief-desired').fill('Use a wider jump gap and two patrols.');
    await page.locator('#brief-scene').fill('_WestA_03');
    await page.getByText('Annotate a screenshot or sketch',{exact:true}).click();
    await page.locator('#reference-image').setInputFiles(path.join(qa,'catalog-desktop.png'));
    await page.waitForFunction(() => !document.querySelector('#reference-canvas').hidden);
    await page.locator('#reference-canvas').scrollIntoViewIfNeeded();
    const unmarked = await page.locator('#reference-canvas').evaluate(c => c.toDataURL());
    const visible = await page.locator('#reference-canvas').boundingBox();
    await page.mouse.move(visible.x+25,visible.y+25); await page.mouse.down();
    await page.mouse.move(visible.x+125,visible.y+75); await page.mouse.up();
    assert.equal(await page.locator('#undo-mark').isDisabled(),false);
    assert.notEqual(await page.locator('#reference-canvas').evaluate(c => c.toDataURL()),unmarked);
    await page.locator('#undo-mark').click();
    assert.equal(await page.locator('#reference-canvas').evaluate(c => c.toDataURL()),unmarked);
    await page.locator('#mark-tool').selectOption('text');
    await page.locator('#mark-label').fill('Wider gap');
    await page.locator('#reference-canvas').click({position:{x:60,y:40}});
    assert.notEqual(await page.locator('#reference-canvas').evaluate(c => c.toDataURL()),unmarked);
    const pngDownload = page.waitForEvent('download');
    await page.locator('#export-image').click();
    await (await pngDownload).saveAs(path.join(qa,'annotated-reference.png'));
    assert.ok(fs.statSync(path.join(qa,'annotated-reference.png')).size > 1000);
    const png = fs.readFileSync(path.join(qa,'annotated-reference.png'));
    const original = fs.readFileSync(path.join(qa,'catalog-desktop.png'));
    assert.equal(png.readUInt32BE(20), original.readUInt32BE(20)+112);
    const download = page.waitForEvent('download'); await page.locator('#download').click();
    await (await download).saveAs(path.join(qa,'request.md'));
    const brief = fs.readFileSync(path.join(qa,'request.md'),'utf8');
    assert.ok(brief.includes('spr_Moblin_High_DrawA') && brief.includes('tile 17'));
    assert.ok(brief.includes('_WestA_03') && brief.includes('annotated-reference.png'));
    assert.ok(brief.includes('PAL_MOB_BLU2') && brief.includes('MoblA03'));
    await page.getByRole('button',{name:'Close reference brief',exact:true}).click();
    // A non-default group and pagination must both filter without breaking selection.
    await page.locator('#search').fill(''); await page.locator('#kind').selectOption('');
    await page.locator('#group').selectOption({index:1});
    assert.ok(await page.locator('.card').count() > 0);
    await page.locator('#group').selectOption(''); await page.locator('#next').click();
    assert.match(await page.locator('#page').textContent(),/Page 2 /);
    // Resource multi-frame playback and frame selection (not game animation).
    const multi = await page.evaluate(() => window.CATALOG.assets.find(a => a.frames.length > 1).name);
    await page.locator('#search').fill(multi);
    await page.getByRole('button',{name:'Inspect '+multi,exact:true}).click();
    await page.locator('#palette').selectOption('PAL_MOB_ORG1');
    await page.getByRole('button',{name:'Play frames',exact:true}).click();
    await page.waitForFunction(() => frame !== 0);
    await page.getByRole('button',{name:'Pause',exact:true}).click();
    await page.getByRole('button',{name:'Frame 0',exact:true}).click();
    await page.waitForFunction(() => previewImage !== null);
    assert.equal(await page.locator('#palette').inputValue(),'PAL_MOB_ORG1');
    assert.equal(await page.locator('.frame-button[aria-pressed=true]').textContent(),'0');
    await page.locator('#search').fill('Moblin');
    await page.getByRole('button',{name:'Inspect spr_Moblin_High_DrawA',exact:true}).click();
    assert.equal(await page.locator('#palette').inputValue(),'PAL_MOB_BLU2');
    await page.locator('#inspector').screenshot({path:path.join(qa,'palette-inspector.png')});
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth),false);
    assert.deepEqual(errors,[]);
    console.log('PASS: file:// load, palette pixels/presets, enemy/item versions, search, filters, pagination, inspector, tiles, colored playback, brief/PNG downloads, desktop layout; no JS errors.');
  } finally { await browser.close(); }
})().catch(error => {console.error(error);process.exitCode=1;});
