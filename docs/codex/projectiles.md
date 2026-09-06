# Projectile cookbook

This page covers the demonstrated **hostile projectile** path. Player attacks have separate [spawn_pc_proj](../../scripts/spawn_pc_proj.gml) and [spawn_pc_proj_2a](../../scripts/spawn_pc_proj_2a.gml) paths; do not transplant the hostile contract without inspecting them.

## Two inspected implementations

| Example | Files and behavior |
| --- | --- |
| Spear | [object](../../objects/Spear.object.gmx), [init_Spear](../../scripts/init_Spear.gml), [update_Spear](../../scripts/update_Spear.gml), [usd_Spear](../../scripts/usd_Spear.gml), [draw_Spear](../../scripts/draw_Spear.gml): two sprite pieces, `vspd_adj=2`, palette/facing presentation; fired by [Moblin_update](../../scripts/Moblin_update.gml) |
| Fireball1 | [object](../../objects/Fireball1.object.gmx), [init_Fireball1](../../scripts/init_Fireball1.gml), [update_Fireball1](../../scripts/update_Fireball1.gml), [usd_Fireball1](../../scripts/usd_Fireball1.gml): shared hostile-fire setup/presentation, version-2 fire sound, default drawing |

Both inherit `ProjectileHostile`. Both register `Projectile_init` as init1 in [GameObjectData_Create](../../scripts/GameObjectData_Create.gml). The `usd_*` scripts occupy the **udp** slot. Spear registers a custom draw callback; Fireball1 passes zero there. File numbering (`Fireball1`) and `ver` are separate: `Fireball101` and `Fireball102` are property keys for versions 1 and 2.

## Files and registration

**Normally create:** object GMX, init/update/presentation scripts, needed sprites; custom draw/end only when needed. **Normally modify:** project manifest; `GameObjectData_Create`; firing enemy/boss/spawner init and update. A new variant can reuse the object/callbacks and add version property/behavior branches. A projectile fired by an existing enemy does not normally need a room resource or scene placement record.

Register `data_go_prop1` for placement geometry, `data_go_scr` with the correct positions, `data_go_prop2` for every version (attack level, body hitbox, CS offsets, palette), and `data_go_prop3` for intended PC body/shield reactions. Copy the meanings from the PB/PS definitions and [Projectile_collision_1a](../../scripts/Projectile_collision_1a.gml), not just the short header comment: shield reactions encode action, REFLECT requirements and sound bits. Some registrations change under `g.mod_REFLECT_more_obj`.

The firing path uses [GOC1_create](../../scripts/GOC1_create.gml): `(XL, YT, facing, object, version, source instance, palette index)`. Moblin checks `avail_uidx_goc(MAX_GOC1) != UIDX_NULL`, creates `Spear` version 1 with itself as source and `palidx_def`, then sets wrapped velocities. [Projectile_init](../../scripts/Projectile_init.gml) calls [addToProjectileList](../../scripts/addToProjectileList.gml) and installs `Projectile_step`. A raw `instance_create` bypasses this initialization.

Supply an explicit valid version for a new caller. Existing `GOC1_create` code defaults it to -1 and tests `if (_VER)`, so omission/-1 is not a safe promise to use version 1. Some existing callers pass -1; preserve intentional example behavior but do not invent a universal default.

## Update, collision and lifetime

Both examples call [Projectile_update_3a](../../scripts/Projectile_update_3a.gml), which applies `vspd_adj` then [Projectile_update_1a](../../scripts/Projectile_update_1a.gml). That helper moves with `updateX/updateY`, updates camera state, dispatches presentation, reflected collisions and PC collisions while onscreen, and sets `state=0` when despawn conditions qualify. Adding custom movement without those responsibilities can leave shots invisible, noncolliding or occupying slots.

Reflection has two sides: projectile shield reaction and target vulnerability/source-specific logic. Inspect [Projectile_collision_2a](../../scripts/Projectile_collision_2a.gml) and `data_REFLECT_vuln` target rows before enabling it. Optional existing fire helpers (`HostileFire_init_1`, `Fireball_udp`, `HostileFire_udp_1`) provide Fireball1's presentation; they are not required for Spear-like objects.

The source instance may disappear; any added source access needs the same existence/state discipline as the constructor. Palette override occurs after init2 in `GOC1_create`; cached colors must remain consistent (Spear refreshes them in `usd_Spear`). Manager capacity is finite; the constructor does not provide a general “no capacity, no instance” guarantee. Follow the caller's slot check. Use the shared explosion/state/despawn path; additional owned DS/surfaces need repeat-safe cleanup through the registered lifecycle.

- [ ] Select Spear or Fireball1; decide object versus version and register all assets.
- [ ] Add prop1/prop2/prop3 and callbacks with udp/draw in the right slots.
- [ ] Integrate a real firing caller with explicit version, facing, source, palette and slot policy.
- [ ] Preserve movement/presentation/collision/despawn responsibilities.
- [ ] Test both directions, body/shield/REFLECT outcomes, source death, offscreen travel and saturated slots.
- [ ] Test scene transition cleanup and applicable variants/mod settings; report [validation](validation.md) results.
