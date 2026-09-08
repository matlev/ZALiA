# In-game boss testing

Open **Options → DEV TOOLS → BOSS TESTING** in an action scene. Select the
Quest row to toggle Q1/Q2, then select an encounter. The list scrolls and its
footer identifies the scene/version. `Esc` or the Options hotkey/gamepad chord
ends a test; leaving its room also returns to the checkpoint.

This feature requires `DEV`, like the existing scene warper. **Hero stats** is
the first selector entry; a save with no preferences defaults to everything
enabled and at maximum.

## Encounter coverage

[dev_boss_test_catalog](../../scripts/dev_boss_test_catalog.gml) enumerates the
`Boss` descendants in the `g.dm_go_prop` index registry populated by
`data_go_prop1`, then their loaded `g.dm_spawn` records and quest qualifications.
There is no boss-type allowlist. Each record retains its own scene and version;
the player's defeated-boss data does not filter the catalog. Registered full
names supply default labels, with a few explicit display exceptions. Types
appear in resource-index order, followed by each type's registered spawn order.
The checked-in `SceneData01.txt` currently yields **12 Q1 / 16 Q2 encounters**:

| Encounter | Scene(s) | Notes |
| --- | --- | --- |
| Horsehead | `_PalcA_0D`, `_PalcE_15` | Palace 5 encounter qualifies only for Q2 |
| Helmethead | `_PalcB_14` | Both quests |
| Rebonack | `_PalcC_0E`, `_PalcF_08` | Complete mounted and rider fight |
| Dark Knight | `_PalcF_11` | Rebonack version 2, complete fight |
| Carock | `_PalcD_0D` | Uses the selected quest's map layout |
| Pendant cave Carock | `_EastA_51` | Version 2; its own cave, not the palace room |
| Gooma | `_PalcE_06`, `_PalcG_3A` | Versions 1 and 2 |
| Barba | `_PalcF_16` | Both quests |
| Thunderbird | `_PalcG_35` | Both quests |
| Shadow Link | `_PalcG_36` | Existing quest-specific intro |
| Ganon P1 / P2 / P3 | `_PalcH_1C`, `_PalcH_20`, `_PalcH_22` | Q2 selector only |

The extra Ganon3 `Phase02` spawn in `_PalcH_21` is transit choreography, not
a fourth fight. Ganon's three encounters are intentionally separate tests.
“Both quests” here means the registered qualification, even if access during
normal play has additional conditions. This is not an arbitrary enemy selector;
enemies outside the registered Boss family, such as Kakusu, are not included.

## Hero stats

[Hero stats load](../../scripts/OptionsMenu_BossHero_load.gml),
[update](../../scripts/OptionsMenu_BossHero_update.gml) and
[draw](../../scripts/OptionsMenu_Draw_BossHero.gml) follow the randomizer's
`FileSelect_Create_Rando`, `FileSelect_RandoOTHER_ITEMS_update` and
`FileSelect_Draw_RandoState_OTHER` patterns. They use the same item registry,
sprites, palettes and `draw_pc_skin` stab poses without changing randomizer UI.

- Up/down selects a row; left/right selects an item or stab icon, or adjusts
  a level/spell. Confirm toggles icons or cycles numeric values (MAX wraps to
  minimum). Select also moves to the next row. Back saves and returns.
- The icon row matches the supplied mockup: candle, flute, bait, shield, ring,
  pendant, sword, feather, note, two treasure maps, dolls, hearts and magic.
  Hearts/magic range from **1 to 9**; combat levels from 1 to `STAT_LEVEL_MAX`.
  Dolls use the randomizer's permanent-doll semantics and Q1/Q2 limits (4/3).
  Spare lives are left unchanged; death ends the test immediately.
- Eight spells and down/up stab are individually switchable. Other collectibles,
  Summon, other skills and Cucco upgrades remain enabled by user request.
  The active spell is selected from enabled spells, falling back to Summon.
- [Apply](../../scripts/dev_boss_test_hero_apply.gml) runs after the default
  full build, using normal container-piece strings and item/spell/skill bits.
  Current HP/MP start full for the chosen container counts. It changes only
  temporary test state; the normal checkpoint restores original progression.

[Save](../../scripts/OptionsMenu_BossHero_save.gml) writes the JSON-encoded
`_DevBossTest_HeroStats_v1` preference into the current save with
`set_saved_value`, on Back or closing Options. It does not invoke `file_save`
or save current gameplay progress. Both test quests share this per-save profile.
Missing fields default to maximum; numeric values are clamped on load. Normal
`file_save` preserves the custom key; eliminating the slot removes it normally.
The checkpoint's `dm_save_file_data` snapshot is refreshed after this intentional
preference write, so returning from a test cannot restore a stale encoded cache.
No disk writes are allowed during a fight. Additional controls need registration
in this small menu schema and an intentional application to the temporary build.

## Starting and ending

- Normal encounters put Link at the arena center on the boss's vertical page;
  he may initially fall to the floor. Existing gate/start routines still run.
- Ganon and Shadow Link retain normal entrance/camera placement and their
  existing choreography. Approach the normal trigger if needed. For Ganon P1,
  the tool supplies the blood-bottle flag and Summon-history trigger so the
  existing summoning sequence can run without acquiring prerequisites.
- The default build grants all maximum heart/magic container pieces, full HP/MP,
  maximum attack/magic/life levels, registered equipment/quest item bits,
  the nine menu spells including Summon, normal skills and Cucco upgrades.
  Hero stats then applies the selected overrides.
  Link begins untransformed. Unimplemented item/spell constants are not enabled.
  Invulnerability, developer dash and stab-to-cheat are disabled for the test.
- Rebonack's mounted damage **does not end the test**. His rider's death does.
- Ganon P1 ends at the last floor section's existing `DEFEATED` branch in
  [Ganon1_update_battle](../../scripts/Ganon1_update_battle.gml), before writing
  `f.dm_quests`. Ganon2 and both Ganon3 completion paths have explicit hooks.
- Standard boss death and Shadow Link's lethal hit return before ordinary
  progression/reward handling. Link death and cancellation use the same return.

## Checkpoint ownership and lifecycle

The checkpoint is in memory; it never saves/reloads the player's disk file.
[dev_boss_test_checkpoint](../../scripts/dev_boss_test_checkpoint.gml) captures
Link and progression **before Options opens**. Closing Options without testing
does not roll anything back; the next opening replaces that unused checkpoint.
Returning reloads the original room normally, restores position, facing,
movement, stats/inventory/progression and spell/form state. It does not resume
other actors or Link's exact attack animation frame. References to old room
actors are not retained.

`global.DevBossTest_stage` is private to this tool:

| Stage | Work |
| --- | --- |
| 0 | Ordinary play; all guards fall through |
| 1 | Test requested; original room completes ordinary Room End cleanup |
| 2 | Test room loading with temporary quest/build; normal boss copies suppressed |
| 3 | Selected encounter active, including its intro |
| 4 | Return requested; test room finishes its own cleanup |
| 5 | Original room loading; checkpoint restored before loading, before spawn-grid construction, and after PC spawn |

The explicit checkpoint field lists cover mutable `f` progression maps/scalars,
save-data caches, randomizer settings/HP table, room/exit history, spell history,
relevant player/developer state, overworld position/tiles and cached dungeon maps.
The latter matter: ordinary room entry can reset overworld state and mark map
exploration even when no boss is killed.

`g.dm_spawn` is captured **after original Room End despawns living actors**, so
the original room's actors can respawn. It is restored before original spawn
grids are built, including after the loader's area-reset code. It is never
restored after those actors exist, which would re-enable duplicate spawning.

`GameObject_create` suppresses automatic boss instances during tests, allowing
the selected manual construction and Rebonack's rider. Shadow Link's pre-fight
controller remains enabled; other cutscene constructors, including his
post-fight controller, are suppressed. Other room actors/terrain use the normal
loader. The selected boss uses its registered callbacks and spawn metadata.

Save guards precede all work in `file_save`, `set_saved_value` and
`save_game_pref`. Options is unavailable during a test; its hotkey cancels
instead. This prevents saving the temporary build or changing the real save
through those paths. Closing the application cannot restore an in-memory
checkpoint after process exit; ordinary unsaved gameplay remains unsaved.

New scripts are appended to the manifest's final `BossTesting` group to preserve
existing script resource positions. No scene definitions/cache files, GameMaker
objects, maps, or normal content registrations are changed by this feature.

## Validation and remaining acceptance

Run `python tools/check_boss_testing.py` from the repository. It validates the
manifest, decodes the actual checked-in scene/spawn cache, checks Boss-family
coverage and selected guard placement. **These are static checks, not a GML
compiler or a gameplay simulation.**

The local `GMAssetCompiler.exe` attempts stopped before project compilation with
`Permission Error : Unable to obtain permission to execute`, including outside
the sandbox. The user subsequently compiled and ran the project in the IDE.
The first Q1 Horsehead launch exposed an unqualified `rmA_ACTION` alias in the
OptionsMenu-context launch script; this is now `g.rmA_ACTION` and has a static
regression check. The user then completed a fight-testing pass and reported only
dark arenas and Ganon P1 starting inside the floor. The detailed state-isolation
matrix below has not been individually confirmed.

Test arenas now force maximum brightness during loading and combat only;
normal room lighting resumes on return. This avoids inaccessible, unlit approach
torches (notably Horsehead and Helmethead) without modifying torch data.
Ganon P1 now selects its registered left entrance: its first registered exit is
the floor hole, which is unsuitable as a test entrance. Its normal intro remains
intact. The user confirmed those fixes and automatic boss discovery working.
The user subsequently compiled and tested Hero stats and confirmed everything
working after removal of the invalid `f.lives` assignment. The detailed cases
below remain a regression checklist, not an individually recorded test report.

Hero stats acceptance:

- [ ] Reload project and compile. Hero stats is first; Quest, first/last boss
      and Back still select the correct action in each quest.
- [ ] A save without preferences shows all ON/max. Icons and side-by-side stabs
      fit the window; arrows/confirm can reach and modify every control.
- [ ] Set HP/MP containers to 1 and levels to 1; disable a collectible, spell
      and each stab. Verify the build in combat, including unavailable actions.
- [ ] Back out and re-enter; close with Options hotkey; complete/cancel/die in
      a test; restart the game. Preferences persist and original Link restores.
- [ ] Another save defaults independently. A later normal save preserves the
      preference. Compare saved gameplay fields before/after editing: only the
      Hero stats preference should change, not unsaved current progression.

Manual acceptance in **GameMaker: Studio 1.4.9999**, using this checkout:

- [ ] Compile `ZALiA.project.gmx`; inspect errors and the `BOSS TEST:` debug log.
- [ ] Record original Link position, HP/MP, levels, inventory, XP, lives,
      quest and progression. Open the menu with unsaved progress present.
- [ ] Test an already-defeated Horsehead. Exactly one boss must appear.
- [ ] Kill test Gooma from a file where real Gooma is unbeaten. Return values
      must match the checkpoint; real Gooma must still be present normally.
- [ ] Die to a boss, then cancel another test. Both must return without a
      death screen, lost life, reward, save or progression change.
- [ ] Complete Rebonack and Dark Knight through mounted → rider. Mounted
      damage/dismount must not end either test.
- [ ] Test palace/cave Carock separately, and Q2's alternate floor/platform
      layouts. Check center placement against terrain, particularly Barba.
- [ ] Run Shadow Link Q1/Q2 intros; run all three Ganon intros/fights. P1
      must return at final floor break, and P2/P3 before their exit sequences.
- [ ] Cancel during choreography and cross an arena exit. Confirm controls,
      camera, palette, music and original room actors recover on return.
- [ ] Repeat tests from a randomized file and from fairy/Cucco form. Confirm
      original form/settings, overworld position/tiles and explored maps return.
- [ ] Compare save/settings file hashes before/after tests, before any later
      intentional normal save. Also verify normal boss kills/death still work
      when no test is active.

When adding a normal boss type, use `Boss` ancestry, `data_go_prop1` and the
ordinary callback/property and scene-spawn registrations. Regenerate stale scene
metadata as described in [maps](maps.md). Its eligible encounters then appear
without editing this selector or its expected count. An unplaced type has no
encounters to list. The static check verifies spawned Boss types have property
registrations and validates their scene data; it does not require their names
in the selector source.

Review unusual init/end callers and persistent state changes. Only add selector
exceptions for actual special handling: Rebonack's rider belongs to the mounted
fight, Ganon3's transit spawn is excluded, and Ganon P1 needs its left entrance.
Nonstandard completion/intros may still need test hooks. Do not infer defeat
merely from a phase change or override battle substates to skip initialization.
