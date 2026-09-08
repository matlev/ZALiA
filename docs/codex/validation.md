# Validation and fresh-agent acceptance

For the in-game boss tester, use the [specific acceptance checklist](boss-testing.md#validation-and-remaining-acceptance)
and `python tools/check_boss_testing.py`. Its cache/resource checks do not replace
GML compilation or testing state restoration in the running game.

## Evidence levels

No automated CLI gameplay test suite or CI build workflow was found in this checkout. [Tester1.object.gmx](../../objects/Tester1.object.gmx), [db_test_various_1a](../../scripts/db_test_various_1a.gml) and developer scripts are ad hoc tools, not a documented headless test runner. Do not execute arbitrary `dev_*` scripts without reading them: some generate or replace data.

Use these separate claims in an implementation report:

1. **Static checks:** changed XML/JSON parses, referenced files and registrations exist, diff scope/whitespace are correct.
2. **IDE build:** project opened and compiled with GMS 1.4.9999; record target/config and errors or warnings.
3. **Runtime behavior:** identify the scene, object/version, quest/mod/save conditions and observed outcomes.
4. **Authoring/export:** matching TMX/TSX/images opened and exported successfully, with the resulting JSON verified in game. Missing TSX blocks this claim even when an existing JSON scene runs.

## Bounded workflow

- Start with `git status --short`; preserve existing work. If this Windows checkout triggers Git's ownership warning, `git --git-dir=.git --work-tree=. status --short` and the same explicit-path form for `diff` worked during this pass without changing global Git configuration.
- Read the cookbook and nearest two examples; record intended files and acceptance cases before changing content.
- Parse each changed `.gmx` as XML and changed map JSON as JSON. In PowerShell: `[xml](Get-Content -LiteralPath 'objects/Name.object.gmx' -Raw)` and `Get-Content -LiteralPath 'datafiles/rm_tile_data/AreaX/AreaX_000.json' -Raw | ConvertFrom-Json`. Substitute real changed paths. This checks syntax only.
- Verify manifest membership, parent/sprite/frame references, callback registration order, exact OBJVER keys, and all used table indices. Search source as well as registration: init2 may override properties, and helper switches may only recognize old object names.
- Open [ZALiA.project.gmx](../../ZALiA.project.gmx) in the required IDE and build the intended target. Keep a separate development save or backup; preserve unrelated saves/preferences. Do not invent a command-line compiler invocation if the legacy toolchain is unavailable.
- If scene/spawn data changed, complete the [metadata workflow](maps.md#generated-metadata-is-part-of-integration), restore temporary flags, and test another launch using the normal included cache. Confirm the target scene identity; fallback to North Castle is a load failure.
- Finish with `git diff --check`, diff review and status. Revert only your temporary testing changes. Report exactly which gameplay cases ran and which remain blocked.

## Existing developer tools

For the complete source-verified controls and menu gates, use [Existing developer controls](debug-tools.md). The external [asset atlas and annotation workflow](visual-workflow.md) can produce visual reference packages without modifying gameplay.

The project currently defines `DEV=true` and `ROOM_SPEED_BASE=60` in its manifest; inspect rather than assume these values in future builds. [obj_start_Create](../../scripts/obj_start_Create.gml) defaults to a fixed `RUN_RANDOMIZATION_SEED` unless `global.randomized` is enabled. Saved/randomizer state still affects reproducibility.

[Dev_RmWarper_Step](../../scripts/Dev_RmWarper_Step.gml) operates in action-room pause state and requests opening with `Input.GP_Select_held && Input.GP_Face4_pressed` (commented as hold SELECT + press Xbox Y). Inspect current input bindings and [Dev_RmWarper_update_3a](../../scripts/Dev_RmWarper_update_3a.gml) for destination/exit selection. This uses registered scenes; it cannot fix a missing registration.

[Input_GameTesting](../../scripts/Input_GameTesting.gml) has DEV-gated keys, including unmodified `I` to cycle invulnerability and `K` for sprite outlines. Read the gate and binding before use; disable cheats for damage acceptance. [db_GO_create_1a](../../scripts/db_GO_create_1a.gml) provides spawn diagnostics from the normal constructor in DEV builds. Hitbox/draw helpers can aid inspection, but visible outlines are not collision tests.

## Minimum runtime matrix for content work

| Change | Cases to observe |
| --- | --- |
| Enemy | Correct object/version and area stats; walking/jumping in both directions; ground/walls; body/sword/projectile damage; intended spells; death/drop; offscreen respawn and room re-entry |
| Boss | Arena/gates/camera/music, attack delay and phases, HP bar, projectile interactions, death/reward/unlock, leave/re-enter and reload; relevant quest and special encounter variants |
| Projectile | Real firing caller, both facings, body/shield/REFLECT, source death, offscreen lifetime, slot saturation, room transition |
| Scene | Exact filename/quest selection, visible palette/layers and collision separately, special tiles, entrance/exit coordinates and destination, actors, re-entry, applicable randomizer behavior |

## Archaeology pass result and onboarding review

This documentation pass changed only root `AGENTS.md` and `docs/codex/`. It inspected both Bot/Moblin, Horsehead/Carock, Spear/Fireball1, and WestA_000/PalcA_000 map/export pairs. No production refactor, data regeneration, compilation, gameplay run or Tiled export was performed. GMSched runtime portability and missing-TSX authoring remain unverified/blocked concerns, not validated capabilities.

Static acceptance: all 155 local documentation links and linked anchors resolved; the eight Markdown files passed a trailing-whitespace check; ten cited project/object/sprite/extension GMX files parsed as XML; both example JSON maps parsed and all tile-layer array lengths matched their dimensions. Git reported no tracked-file changes, and `git diff --check` was clean. Pre-existing untracked `Configs/Default/HTML5/` and `Configs/Default/iOS/` directories were preserved. These checks do not establish build or gameplay correctness.

Fresh-session exercise: “Add a new enemy to ZALiA.” Starting at root AGENTS, the agent can follow **Normal enemies** to Bot for walking/jumping or Moblin for weapon attacks; find `GameObjectData_Create` property/callback rows; inspect exact-identity limitations in `Enemy_update_1`; create a registered resource or version; place it with `data_spawn` in `rm_data_init_West_A`; follow the local `_REINITIALIZING` path to update `SceneData01.txt`; then run the matrix above. No rediscovery of the whole engine is needed. A behavior-only change does not need map authoring, while a new spawn still needs metadata integration even if tile JSON is unchanged.
