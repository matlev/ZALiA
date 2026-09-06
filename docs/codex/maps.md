# Map and scene authoring

## Runtime support versus authoring support

Runtime tile JSON is checked in under [datafiles/rm_tile_data](../../datafiles/rm_tile_data). This checkout does not require the external TMX/TSX files merely to load that JSON through its existing engine. That is a source-level conclusion; this pass did not compile or play the game.

External sources inspected for this pass are at `C:\Users\azure\Downloads\ZALiA_TiledFiles_20250416_01\ZALiA_TiledFiles`, outside the repository. `WestA/WestA_000.tmx` and `PalcA/PalcA_000.tmx` both reference external `../../../../Tilesets/.../*.tsx`; there are no TSX files in that supplied source tree. Those tilesets are currently unavailable. Tiled cannot provide a complete, verified visual editing/export workflow until the matching tileset definitions and referenced images are available. Bundled GameMaker background PNGs alone do not demonstrate a faithful reconstruction of TSX metadata or tile numbering.

The TMX files' saved export targets point into the original author's `Game_Dev/GameMaker/Projects/Z2TAOL_*.gmx` trees. Do not export to those historical destinations. Also do not overwrite newer JSON just because a similarly named TMX is available: PalcA_000's supplied TMX reports Tiled 1.11.0 while its checked-in JSON reports 1.11.2. Compare contents before editing. These version fields are observations, not a mandated Tiled version.

## Two concrete map examples

| Example | Inspected structure and scene integration |
| --- | --- |
| [WestA_000.json](../../datafiles/rm_tile_data/WestA/WestA_000.json) and external `WestA/WestA_000.tmx` | 96 × 32 cells, 8 × 8 pixels; `BG0603`, `BG0502`, `BG0301`, `BG0202`, `BG0101`, `SOLIDS  -1000`, `palette`, `tile_data_system_v.03`. North Castle is registered in the `00` section of [rm_data_init_West_A](../../scripts/rm_data_init_West_A.gml), using `RM_NPALACE_FILE_NAME`, separate torches/Zelda/cutscene spawns and exits |
| [PalcA_000.json](../../datafiles/rm_tile_data/PalcA/PalcA_000.json) and external `PalcA/PalcA_000.tmx` | 128 × 32 cells, 8 × 8 pixels; BG/FG layers with `GRASS01_01`, `STRUCTURE_FGWALL01_01`, `PILLAR01`, `STATUE01`, `GROUND01_01`, plus solids/palette/version and `_Item_Position_Options`. `00` in [rm_data_init_Palc_A](../../scripts/rm_data_init_Palc_A.gml) registers the entrance, elevator, exits, spawner and heart piece |

The inspected maps are finite orthogonal maps with flat tile layers and numeric `data` arrays. Their runtime loader accesses that shape directly. Do not assume infinite-map chunks, grouped layers, embedded tilesets, arbitrary object-layer spawns, compressed strings or every Tiled rotation mode are supported.

## Actual pipeline and naming

1. Tiled TMX references TSX authoring assets; export produces JSON containing tile arrays and `tilesets` records (`firstgid`, `source`). Export location/relative source strings must match the runtime's expectations.
2. [set_rm_data](../../scripts/set_rm_data.gml), [set_rm_data_1a](../../scripts/set_rm_data_1a.gml) and `rm_data_init_*` associate a **logical scene** such as `_WestA_03` with a **tile filename** (`WestA_003` for that scene). Scene suffixes are hex via `hex_str`; tile filenames use their existing three-digit identifiers. They are not interchangeable or necessarily one-to-one. Horsehead's logical palace scene `0D`, for example, uses `PalcA_012`.
3. [get_scene_tile_file_name](../../scripts/get_scene_tile_file_name.gml) selects scene/quest data and allows randomizer overrides. [rm_get_file_data](../../scripts/rm_get_file_data.gml) constructs `rm_tile_data/<first five filename characters>/<filename>.json` and reads that file. [g_Room_Start](../../scripts/g_Room_Start.gml) decodes it, with previous-scene/North-Castle fallbacks on missing data. A fallback scene is not a successful load test.
4. [get_scene_ts_data](../../scripts/get_scene_ts_data.gml) scans each `source` string backwards to extract the tileset basename at `/`, skipping strings containing `palette`. It resolves that name through `g.dm_tileset`, populated in [g_Create](../../scripts/g_Create.gml) from bundled GameMaker background assets and tile dimensions. `firstgid` plus registered tile count defines the GID range. **It does not open the TSX path.** The string is an identifier carrier, but its basename and parsing shape still matter. Renaming a tileset, using only a bare basename without `/`, or changing separators is not necessarily harmless. Unknown names fall back to `ts_tile_marker_1a_8x8`, potentially disguising a registration error.
5. [scene_enter_add_tiles](../../scripts/scene_enter_add_tiles.gml) interprets layer names, GIDs and flip bits, adds runtime tiles, and fills solid/break/liquid/current/spike grids. `BG01`–`BG08`/`FG01`–`FG08` encode depth; following digits select palette. `SOLIDS`, `tile_data_system_v.03` and dynamic-layer tokens are engine data, not decorative labels. It handles horizontal/vertical flip bits explicitly; do not assume diagonal rotation is equivalent.
6. Actors/exits normally come from `g.dm_spawn`/`g.dm_rm`, authored with [data_spawn](../../scripts/data_spawn.gml) and [data_exit](../../scripts/data_exit.gml), not general Tiled object events. [go_spawn_priorities](../../scripts/go_spawn_priorities.gml) and [update_go_spawn_1b](../../scripts/update_go_spawn_1b.gml) construct runtime objects through `GameObject_create`.

The active tile loop has an additional constraint: after subtracting one and masking flip bits, it selects the tileset by `hex_str(_tile_data >> 8)` and local tile by `_tile_data & $FF`. The general firstgid/lastgid range-search alternative is commented out there. Preserve the demonstrated 256-ID blocks, tileset order and `firstgid` spacing (1, 257, 513, ...); merely retaining valid Tiled GIDs does not guarantee correct runtime rendering.

Runtime room dimensions in `g_Room_Start` use 8-pixel cells and round to 256-pixel pages. Palette, collision and hidden/breakable layers can change behavior without changing visible art. Keep the demonstrated page/grid conventions unless a task explicitly extends their support.

## Generated metadata is part of integration

[RoomData_Create](../../scripts/RoomData_Create.gml) sets `_REINITIALIZING=false` and `QUICK_REINITIALIZE=false`. With the included `SceneData01.txt` present, it calls [RoomData_Create_3](../../scripts/RoomData_Create_3.gml) and exits before running the `rm_data_init_*` registrations. That file contains JSON whose values include **serialized GameMaker DS maps/lists/grids**, not an ordinary editable spawn array. `SceneWallData01.txt` separately restores wall metadata.

For an implementation that changes scenes/spawns:

1. Modify the appropriate source registration (`rm_data_init_*`, helpers only if needed). Preserve keys and insertion order where possible: spawn identifiers and save/randomizer data are coupled to registration.
2. In a controlled development build, use the existing full regeneration branch by temporarily setting local `_REINITIALIZING=true`; keep `QUICK_REINITIALIZE=false` when tile-derived data must refresh. `DEV` gates writing generated files. Do not assume the older comment about `global.REINITIALIZE_DATA1` in `g_Create` toggles this local branch—it does not.
3. If tile dimensions changed, inspect [RoomData_Create_2a](../../scripts/RoomData_Create_2a.gml), [dev_automateRoomData2](../../scripts/dev_automateRoomData2.gml) and `set_rm_data_1a`. The generator invocation near the end of `RoomData_Create` is commented out; its output is intended to update the dimension script. New/changed tile geometry also needs applicable wall/layer metadata. Overworld changes require their own data to be updated first, as the source warns.
4. Run in GMS 1.4, inspect CompileForm output and generated files at the runner's `working_directory`/sandbox. The source explicitly says to **move, not copy**, generated `SceneData01.txt` and `SceneWallData01.txt` from `%localappdata%` into their Included Files directory (`datafiles/rm_tile_data`). Inspect/verify the specific output paths and back up originals before replacement; do not remove unrelated saves.
5. Restore temporary regeneration/debug changes and launch again through the normal cached-data path. Verify the intended scene, spawn and exits actually use the updated included data. Until this happens, report metadata integration as unverified.

The broader regeneration notes in `g_Create` also mention `init_tile_layer_data`, palette data, overworld data and `other/TilesetData01.txt`. Some calls are commented out and palette comments admit manual overrides. Determine which products the changed feature consumes; do not promise a single automatic “rebuild all” switch or regenerate everything indiscriminately.

## Created versus modified; checklist

For a **new map**, normally create external TMX (once prerequisites are restored) and its runtime JSON; register the JSON in the project Included Files tree. For an **existing map**, modify the relevant pair only after checking source/export drift. Normally modify area scene definitions for scene mapping, actors and exits, and regenerate affected metadata. Do not create a native GameMaker room for each scene; the action-room infrastructure loads these scenes dynamically.

New tileset artwork is optional: if introduced, add background GMX/PNG resources, manifest entries and matching `g.dm_tileset` data. Animation uses explicit [tile_data_init_1](../../scripts/tile_data_init_1.gml) registration (e.g. `ts_Animation0301` and `ts_Animation0401`), not automatic import of TSX animations. New randomizer eligibility, path conditions, dungeon-map positions and special layers are conditional on the scene's role, but must be maintained when editing a scene already using them.

- [ ] Inspect the two map examples and the destination's own JSON/scene section.
- [ ] Confirm TSX/images and TMX currency before claiming authoring/export is ready.
- [ ] Preserve layer grammar, GIDs, basename mapping, 8-pixel cells and page geometry.
- [ ] Register filename/quest mapping, Included File, exits and intentional spawns.
- [ ] Regenerate only affected metadata, move verified outputs, restore flags, test cached startup.
- [ ] Check visuals/palette, actual collision, special layers, entrances/exits, spawn locations, scene re-entry and applicable quest/randomizer variants.
