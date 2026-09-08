# Visual development workflow

The asset atlas targets desktop use in Chrome/Edge. Mobile/tablet-specific design and testing are not required; preserve existing responsive CSS unless desktop work needs a change.

## Start the asset atlas

From a PowerShell terminal at the repository root:

```powershell
.\tools\Open-AssetCatalog.ps1
```

The launcher uses the bundled Codex Python when available, otherwise `py -3` or `python`. You can provide `-PythonExecutable 'C:\path\to\python.exe'`. If local PowerShell policy blocks the launcher, run the generator directly with Python 3.9 or newer:

```text
python tools/generate_asset_catalog.py
```

Open [the generated catalog](../../dev/generated/asset-catalog/index.html) in Chrome or Edge after generation. This link becomes valid after running the generator; generated files are deliberately not committed. The catalog uses standard-library Python and local HTML/CSS/JS, with no server, package install, internet connection or game build required. Re-run after asset changes. Keep it in this checkout: links target original image/source files. Preview PNGs are also embedded in generated data so browsers allow canvas pixel reads from `file://` without security flags or a server.

## Find and discuss assets

Search names or project resource groups; filter sprites versus backgrounds; click an asset to inspect it. Pagination limits the number of cards loaded at once. Card zoom fits large assets within the card; the inspector provides explicit zoom with scrolling. Source images use pixelated enlargement.

The inspector provides:

- Copyable resource name, dimensions, origin and GMX sprite bounds.
- Frame strip and a 5-fps resource-frame preview. This is convenient inspection timing, not the game's animation timing.
- Original PNG/GMX links, direct object sprite/mask references, and GML text mentions with line numbers. Mentions include comments/inactive code and are not proof of runtime behavior.
- For backgrounds, optional grid and clickable tile coordinates/index based on GMX dimensions, offset and spacing. These are zero-based local indices, **not Tiled GIDs**; verify `g.dm_tileset` and the [map loader](maps.md) before using them in game data.
- A URL fragment containing the selected resource name. Resource names and repo-relative source paths also appear in downloaded briefs.

The default list contains resources registered in `ZALiA.project.gmx`; an option exposes unregistered files on disk. The generator reports malformed resources and missing images in the page and `diagnostics.json`. It rejects image references outside the checkout. It does not modify resources or the manifest.

**Visual limits:** many enemies switch between separate sprite resources in callbacks; combat hitboxes are separate from GMX sprite bounds. The atlas provides static palette previews, not a scene editor or simulation of AI.

## Preview colors and versions

Select an asset, then use **Colors & versions** in the inspector:

1. Choose a **Source-linked object version** when available. For example, `spr_Moblin_High_DrawA` offers `MoblA01/02/03` with orange/red/blue slots; `spr_Item_Bottle` offers `ItmE001/02/03/04` with red/blue jar slots. `spr_Bot_Norm` includes Bot versions and Capper registrations that share its placement sprite.
2. The **Palette preview** selector chooses a named source preset for that slot. Switch between alternatives such as `MOB BLU1` (non-dungeon) and `MOB BLU2` (dungeon), or choose **Original source colors** to compare. The full preset list also allows manual experiments on any sprite or background, including resources with no resolved version link.
3. The enlarged preview and resource playback use the chosen palette. Cards, frame thumbnails and original PNG links remain raw source images. The swatches show replacements for the eight base colors. Registration/preset links include source line numbers.
4. Choices are remembered per asset for this page session and included in downloaded briefs for selected assets. They do not change game resources, game versions or save data.

The generator extracts literal `C_*` colors, simple color aliases, supported named `build_pal` definitions, palette aliases and the observed `strReplaceAt` color replacements from [p_init.gml](../../scripts/p_init.gml). It follows [build_pal.gml](../../scripts/build_pal.gml), including omitted/`-1` arguments and `-2` second-quartet aliases. GML color integers are BGR; the browser converts them to RGBA. The canvas reproduces [shd_pal_swapper.shader](../../shaders/shd_pal_swapper.shader)'s exact RGBA matching and `$7F7F7F` transparency cutout. Unmatched colors remain unchanged. This models the palette swap before draw tint/brightness, not the entire draw pipeline.

Version links inspect literal `o_name`/`data_go_prop2` blocks in [GameObjectData_Create.gml](../../scripts/GameObjectData_Create.gml), placement sprite references, direct registered callback sprite mentions, and item `_obj`/`_spr` assignments in [g_Create.gml](../../scripts/g_Create.gml). Source comments are excluded. These links are candidates for shared artwork, not proof that every version uses the selected sprite in every state. Computed object keys, transitive helper references and runtime overrides are not resolved. Missing links do not mean an asset is unused or has no variants.

The tool does not execute GML or resolve current scenes, serialized palette metadata, randomizer palettes, player settings, flashing or custom draw overrides. Unsupported named palette expressions are omitted and listed in diagnostics. The current extraction provides 36 named presets; scene-dependent slots such as `PI_BGR1` require manual selection rather than an invented default. Use the source links and game validation when exact runtime appearance matters.

## Build a reference package

1. Use **Add to brief** on relevant assets. Click a tileset pixel/tile if its precise location matters; the latest clicked location for that asset is retained for this page session.
2. Open **Reference brief**. Enter the desired change and known scene/tile/object/version/quest context. Unknown values stay unknown.
3. Optionally expand **Annotate a screenshot or sketch**, load a PNG/JPEG/WebP, and draw arrows/boxes or click to place a text label. Undo removes the last mark. Loading a new image starts a new annotation; your original file is unchanged.
4. Download the annotated PNG and `request.md` separately. The PNG footer includes the context fields entered above; metadata is entered by you, not automatically read from the running game. Images above 20 megapixels are rejected to bound browser canvas memory.
5. Put both downloads, your original and any additional sketches in `dev/references/<concept>/`, then ask the implementation agent to read that folder's `request.md`. Resolve duplicated browser download names before referring to them. Explain which images show current versus desired behavior.

Nothing is uploaded. Selected asset names are saved to browser local storage where permitted; form text, images, tile-click notes and annotations are only kept in the current page. Download work before closing/reloading it. A [plain Markdown template](../../dev/templates/request.md) is available if you prefer a text editor. Both `dev/references` and `dev/generated` are gitignored working material; deliberately curated references can be committed elsewhere later.

## Inspect the game using existing tools

Use the [existing controls guide](debug-tools.md) to open Dev Tools, display hitboxes and warp to registered scenes. Capture the game using your normal screenshot method, then annotate locally in the atlas. Keep a clean screenshot and an annotated copy when practical.

Do not interpret a successful browser preview as a successful game build/test. The full [validation workflow](validation.md) and scene metadata requirements still apply.

## Maintenance and checks

Source: [generator](../../tools/generate_asset_catalog.py), [UI files](../../tools/asset_catalog), [Windows launcher](../../tools/Open-AssetCatalog.ps1). The optional `--root` and `--output` generator arguments support other checkouts/output locations; moving an output afterward invalidates relative links. No old output directory is recursively deleted during generation.

```text
python -m unittest discover -s tools/tests -v
node --check tools/asset_catalog/catalog.js
node --check tools/asset_catalog/annotate.js
node --check tools/asset_catalog/palettes.js
node tools/tests/check_asset_catalog.cjs --browser "C:/path/to/chrome.exe"
```

The browser check is optional tooling validation and requires Playwright resolvable by Node (installed locally or via `NODE_PATH`). Normal catalog use does not require Node or Playwright. Browser checks write screenshots/downloads to ignored `dev/generated/catalog-qa`.

Verified in this pass: 778 registered resources (727 sprites, 51 backgrounds), zero resource warnings; six fixture tests; file-URL loading in headless Chrome; exact orange palette output pixels, blue scene-preset differences, enemy/jar version switching, all extracted preset selections, filters, pagination, sprite/frame/tile inspection, reference selection, annotation and Markdown/PNG downloads; desktop layout with no JavaScript errors. Counts reflect this checkout, not future invariants. No GMS build or gameplay test was performed.

## Next boundary

The next meaningful game-side increment would be a verified capture/context overlay or targeted spawn tool using the existing menu. Before that work, establish an available GMS 1.4.9999 build/run loop and an explicit enable/disable policy: existing `DEV` and `g.DevTools_state` are not interchangeable. No production scripts, resources, save data or existing accessibility policy were changed for this toolkit.

Whole-scene previews remain separate work: `preview_scene` is dormant, changes camera/application-surface state, and has partly commented restoration. Missing TSX still blocks verified Tiled authoring; these tools neither restore TSX nor claim to make arbitrary boss spawning safe.
