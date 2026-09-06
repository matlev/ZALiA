# Normal enemy cookbook

For “Add a new enemy,” read this page, the [callback contract](architecture.md), and [resource registration](resources.md). Choose an example by actual behavior, then trace every shared helper it calls.

## Two inspected implementations

| Example | Concrete files and useful pattern |
| --- | --- |
| Bot/Bit/Nyb | [Bot_A.object.gmx](../../objects/Bot_A.object.gmx), [Bot_init2](../../scripts/Bot_init2.gml), [Bot_update](../../scripts/Bot_update.gml), [Bot_udp](../../scripts/Bot_udp.gml), [Bot_draw](../../scripts/Bot_draw.gml), [Bot_end](../../scripts/Bot_end.gml): walking/jumping, sprite selection, version abilities and guarded sprite cleanup |
| Moblin | [MoblA.object.gmx](../../objects/MoblA.object.gmx), [Moblin_init2](../../scripts/Moblin_init2.gml), [Moblin_update](../../scripts/Moblin_update.gml), [Moblin_udp](../../scripts/Moblin_udp.gml), [Moblin_draw](../../scripts/Moblin_draw.gml): attack states, separate weapon hitbox/drawing, Spear creation |

Both have full records in [GameObjectData_Create](../../scripts/GameObjectData_Create.gml); search `object_get_name(Bot_A)` and `object_get_name(MoblA)`. Both use `GameObjectB_init` as init1. Bot versions `01`–`04` have property rows and behavior branches; Moblin has `01`–`03`. Moblin's active update fires for versions 1/3 despite some nearby comments describing variants differently. Trust executable conditions.

## What to create or modify

- **New type:** normally create an object GMX with a demonstrated parent, its necessary init2/update/udp scripts, and sprite GMX/PNG assets if existing art is insufficient. Custom draw and cleanup scripts are conditional, not mandatory empty stubs.
- **Existing variant:** normally modify its property block and relevant version branches. A new numeric version does not require a new GameMaker object or duplicated callbacks.
- **Always integrate a new resource:** update [ZALiA.project.gmx](../../ZALiA.project.gmx). Add object-level `data_go_prop1`, exact callback order in `data_go_scr`, and a complete `data_go_prop2` row for each used version.
- **Make it appear:** modify the intended `rm_data_init_*` script with [data_spawn](../../scripts/data_spawn.gml), or a demonstrated spawner caller. [rm_data_init_West_A](../../scripts/rm_data_init_West_A.gml) contains both Bot and Moblin `rm+STR_PRXM` placements; [rm_data_init_Palc_A](../../scripts/rm_data_init_Palc_A.gml) places Bot too. Use pixel XL/YT (`column<<3`, `row<<3` commonly); preserve established spawn ordering/keys. Scene metadata must then follow [regeneration](maps.md#generated-metadata-is-part-of-integration).
- **Only if needed:** new rows in [init_body_hb_data](../../scripts/init_body_hb_data.gml), [init_cs_points_data](../../scripts/init_cs_points_data.gml) as consumed by [setCSOffsets](../../scripts/setCSOffsets.gml), [init_data_hp](../../scripts/init_data_hp.gml), [init_data_xp](../../scripts/init_data_xp.gml), damage tables, palette/audio assets or projectile registrations. Reuse appropriate existing entries first. `data_REFLECT_vuln` rows are needed only for intended reflected-projectile vulnerability.
- **Randomizer participation is conditional:** [g_Create](../../scripts/g_Create.gml) explicitly builds `dl_RandoEnemy_OBJVER*` lists; [data_spawn_3a](../../scripts/data_spawn_3a.gml) uses those to qualify spawns. It also assigns sequential spawn keys and stores the object name/index/version. A new registration is not automatically eligible, and inserting/reordering old placements can change keys. Inspect these lists when the task includes randomizer support.

## Hidden coupling

Bot init2 overrides palette and some HP/attack/XP/drop values by area/version. Changing its registration alone may not change the effective stats. Its version-2 timing inspects other `Bot_A` instances and their update indices. Copying it to a differently named object changes those branches.

Moblin calls [Enemy_update_1](../../scripts/Enemy_update_1.gml), whose behavior explicitly switches on `MoblA`, `DairA`, and `GoriA` identities (inspect the switch before reuse). It is not a generic plug-in walker. A new type must deliberately use a compatible existing path or bounded behavior in its own callbacks; do not assume inheritance activates those branches. [GOB_update_2](../../scripts/GOB_update_2.gml), tile collision and sword/body collision calls also have ordering effects.

Body hitboxes, weapon hitboxes, sprite dimensions and CS offsets are separate. Correct-looking art does not prove correct collisions. Maintain byte arithmetic and shared state/drop handling instead of adding independent Step/death logic. Check `state`, offscreen behavior and manager capacity when diagnosing an invisible/inert spawn.

Respawn documentation is inconsistent: `data_go_prop2`'s header describes values differently from the `RSPa`–`RSPe` definitions in `GameObjectData_Create` and [GameObjectB_step](../../scripts/GameObjectB_step.gml). The latter describes 0 never, 1 offscreen, 2 area refresh, 3 room refresh, 4 timed. Follow the active path and test the selected mode; do not reproduce the stale header as a specification.

## Implementation checklist

- [ ] Select Bot or Moblin (or a closer registered sibling); inspect init/update/udp/draw and exact-identity branches.
- [ ] Decide new object versus new version; choose a noncolliding object-name + hex-version key.
- [ ] Register assets, callbacks and per-version properties; verify table indices and init2 overrides.
- [ ] Integrate the intended scene/spawner; regenerate scene metadata if placement changed.
- [ ] Include projectile/reflection/custom cleanup hooks only where required by the behavior.
- [ ] Test appearance, both directions, terrain, damage/spells, death/drop, offscreen/respawn and scene re-entry using [validation](validation.md). Report blocked checks.
