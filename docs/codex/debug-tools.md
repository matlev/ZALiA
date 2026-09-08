# Existing developer controls

This is a source-verified access guide, not a claim that each control was exercised in a running build. Use a development save and record quest/settings when collecting evidence.

## Options → Dev Tools

During an action scene with no other GUI open, press **O** to request the options menu, then select **DEV TOOLS**. The equivalent default-commented gamepad chord is both bumpers + Xbox Y; actual action bindings are remappable. Sources: [OptionsMenu_Create](../../scripts/OptionsMenu_Create.gml) sets `OpenClose_Key_KEY=ord("O")`; [update_OptionsMenu](../../scripts/update_OptionsMenu.gml) checks GUI/room state and the chord; [OptionsMenu_Main_update](../../scripts/OptionsMenu_Main_update.gml) opens Dev Tools. Use configured directions/confirm; the main menu also accepts Enter/Space. Escape/Backspace or the configured back action backs out.

The menu already exposes a master Dev Tools state, defaults, performance display, hitboxes, solid collision points, coordinate points, original camera outline, entity HP, sprite outlines, frame count, dash and palette/background controls. Do not build another menu to duplicate these.

Availability is explicitly controlled in [OptionsMenu_option_is_avail](../../scripts/OptionsMenu_option_is_avail.gml): exits, solid/unique tiles, dungeon map and add-items controls require `DEV`; several other entries return true. The menu's invulnerability and double-jump availability entries are commented out, and their update cases are also commented out. Keyboard invulnerability still exists. “ADD ITEMS” toggles `g.use_StabToCheat`; it is not a direct grant-all-items button. See [OptionsMenu_DevTools_update](../../scripts/OptionsMenu_DevTools_update.gml) for exact actions.

Some actions call `save_game_pref`, so toggles can persist across sessions. Use the existing default/reset action deliberately; it changes multiple settings. Before validating damage or movement, check whether cheats or dash are enabled.

## Unmodified DEV keyboard shortcuts

[Input_GameTesting](../../scripts/Input_GameTesting.gml) checks `DEV` and requires Control, Shift and Alt all **not held** for this block:

| Key | Action / state |
| --- | --- |
| I | Cycle `g.dev_invState` invulnerability modes |
| K | Cycle sprite outlines (`g.canDrawSprOutline`) |
| J | Toggle object coordinate points (`g.canDraw_ogXY`) |
| L | Toggle original camera outline |
| H | Toggle solid collision-side points |
| R | Toggle hitbox drawing |
| Z | Toggle highlighted solid tiles |
| E | Toggle exit hitboxes |
| U | Toggle GameMaker debug overlay; writes game preferences |
| V | Toggle entity HP drawing |

These actions also enable `g.DevTools_state`. A display toggle does not enable a new collision system; compare the overlay to actual gameplay interactions. Record which overlays were active in screenshots. The checked-in manifest currently defines `DEV=true`; do not assume a “release” name disables this block.

## Scene warper

The existing [Dev_RmWarper_Step](../../scripts/Dev_RmWarper_Step.gml) requires an action scene with `g.gui_state_PAUSE`. While paused, hold **SELECT** and press the **Xbox Y / GP_Face4** binding to request the warper. Its original `DEV`/`DevTools_state` gate is commented out with a note that anyone can use it for custom content.

The warper has area, room and exit selection states. Use the current input bindings; inspect its [destination update](../../scripts/Dev_RmWarper_update_3a.gml) when diagnosing a wrong arrival. This is a useful way to reach a registered scene quickly, not an arbitrary JSON-file loader. Logical scene names and tile filenames differ. The same tile layout may support multiple scene/quest contexts.

Warping does not guarantee a clean reset of saved progression, enemies, items or randomizer state. For acceptance tests record the destination/exit, save conditions and quest; use a known save/relaunch when clean state matters. A new spawn still requires the documented [scene metadata regeneration](maps.md#generated-metadata-is-part-of-integration).

## Captures and further tooling

For now, use normal screenshots plus the atlas [reference workflow](visual-workflow.md). Enter scene ID, tile filename, object/version and settings into the brief; the annotation export prints that context in its footer. It does not detect the running game or capture it automatically.

The [preview_scene](../../scripts/preview_scene.gml) call is commented out in [Surface_Draw_End](../../scripts/Surface_Draw_End.gml). It resizes the application surface and alters view state; some restore assignments are commented. Do not enable it as a shortcut to reliable whole-map screenshots.

For new in-game tooling, preserve the existing feature availability policy unless a task explicitly changes it. Define and test a gate for the **new** feature, both enabled and disabled. `DEV=true`, runtime Dev Tools state, and existing publicly available warping are distinct facts. Native capture, repeatable restart and spawn menus are not implemented by this documentation or the external atlas.
