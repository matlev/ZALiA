# Visual development workflow

## Start the asset atlas

From a PowerShell terminal at the repository root:

```powershell
.\tools\Open-AssetCatalog.ps1
```

The launcher uses the bundled Codex Python when available, otherwise `py -3` or `python`. You can provide `-PythonExecutable 'C:\path\to\python.exe'`. If local PowerShell policy blocks the launcher, run the generator directly with Python 3.9 or newer:

```text
python tools/generate_asset_catalog.py
```

Open [the generated catalog](../../dev/generated/asset-catalog/index.html) in Chrome or Edge after generation. This link becomes valid after running the generator; generated files are deliberately not committed. The catalog uses standard-library Python and local HTML/CSS/JS, with no server, package install, internet connection or game build required. Re-run after asset changes. Keep it in this checkout: it links to original image/source files rather than copying them.

## Find and discuss assets

Search names or project resource groups; filter sprites versus backgrounds; click an asset to inspect it. Pagination limits the number of cards loaded at once. Card zoom fits large assets within the card; the inspector provides explicit zoom with scrolling. Source images use pixelated enlargement.

The inspector provides:

- Copyable resource name, dimensions, origin and GMX sprite bounds.
- Frame strip and a 5-fps resource-frame preview. This is convenient inspection timing, not the game's animation timing.
- Original PNG/GMX links, direct object sprite/mask references, and GML text mentions with line numbers. Mentions include comments/inactive code and are not proof of runtime behavior.
- For backgrounds, optional grid and clickable tile coordinates/index based on GMX dimensions, offset and spacing. These are zero-based local indices, **not Tiled GIDs**; verify `g.dm_tileset` and the [map loader](maps.md) before using them in game data.
- A URL fragment containing the selected resource name. Resource names and repo-relative source paths also appear in downloaded briefs.

The default list contains resources registered in `ZALiA.project.gmx`; an option exposes unregistered files on disk. The generator reports malformed resources and missing images in the page and `diagnostics.json`. It rejects image references outside the checkout. It does not modify resources or the manifest.

**Visual limits:** palette swapping changes source colors at runtime; many enemies switch between separate sprite resources in callbacks; combat hitboxes are separate from GMX sprite bounds. The atlas intentionally labels those distinctions. It is not a palette renderer, scene editor or simulation of AI.

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
node tools/tests/check_asset_catalog.cjs --browser "C:/path/to/chrome.exe"
```

The browser check is optional tooling validation and requires Playwright resolvable by Node (installed locally or via `NODE_PATH`). Normal catalog use does not require Node or Playwright. Browser checks write screenshots/downloads to ignored `dev/generated/catalog-qa`.

Verified in this pass: 778 registered resources (727 sprites, 51 backgrounds), zero generator warnings; four fixture tests; file-URL loading in headless Chrome; filters, pagination, sprite/frame/tile inspection, reference selection, annotation and Markdown/PNG downloads; desktop/mobile layout with no JavaScript errors. This count reflects this checkout, not a future invariant. No GMS build or gameplay test was performed.

## Next boundary

The next meaningful game-side increment would be a verified capture/context overlay or targeted spawn tool using the existing menu. Before that work, establish an available GMS 1.4.9999 build/run loop and an explicit enable/disable policy: existing `DEV` and `g.DevTools_state` are not interchangeable. No production scripts, resources, save data or existing accessibility policy were changed for this toolkit.

Whole-scene previews remain separate work: `preview_scene` is dormant, changes camera/application-surface state, and has partly commented restoration. Missing TSX still blocks verified Tiled authoring; these tools neither restore TSX nor claim to make arbitrary boss spawning safe.
