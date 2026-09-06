# Boss cookbook

Bosses use the same property/callback engine as enemies, with battle lifecycle, arena and progression coupling. A large enemy is not automatically a boss, and `BoBoA` (BossBot) is not the model for palace-boss integration.

## Two inspected implementations

- **Horsehead:** [object](../../objects/Horsehead01.object.gmx), [init1](../../scripts/Horsehead_init1.gml), [init2](../../scripts/Horsehead_init2.gml), [update](../../scripts/Horsehead_update.gml), [udp](../../scripts/Horsehead_udp.gml), [draw](../../scripts/Horsehead_draw.gml), [end](../../scripts/Horsehead_end.gml). Multipart body/arm/head rendering, melee states, second-quest Mace1 attack, area/quest stat adjustments. Its init1 calls `Boss_init_1` and sets battle music; init2 calls `Boss_init_2` and `Boss_init_2b`.
- **Carock:** [object](../../objects/Carock01.object.gmx), [init2](../../scripts/Carock_init2.gml), [update](../../scripts/Carock_update.gml), [udp](../../scripts/Carock_udp.gml), [draw](../../scripts/Carock_draw.gml), [end](../../scripts/Carock_end.gml). Registers `Boss_init_1` directly, then configures teleport/attack substates, SoundWave/Flame1 attacks and a grid for attacks. Version 2 is the pendant encounter, not just a tougher palette swap.

Their callback/property blocks are in [GameObjectData_Create](../../scripts/GameObjectData_Create.gml). Both inherit `Boss`. Horsehead's runtime version-1 key is `Horsehead0101`; Carock's are `Carock0101` and `Carock0102`.

## Files and integration

**Create for a new boss:** object GMX; necessary init/update/udp/draw scripts; sprite assets; guarded cleanup for owned resources. **Modify:** project resource tree and `GameObjectData_Create`, then the relevant `rm_data_init_*` scene definitions and generated metadata. Existing-boss modifications usually stay within those scripts and property rows. Shared Boss scripts need changes only if the requested behavior actually requires changing their existing policy.

Mandatory for the demonstrated palace pattern:

1. Use `Boss_init_1` directly or through a local init1; it installs common enemy infrastructure and initializes battle variables. Use `Boss_init_2` after placement/properties exist. It derives arena geometry, ground and HP-bar placement, and creates `ArenaGateA` except for explicit boss-family exclusions. `Boss_init_2b` selects the starting side in both examples.
2. Preserve qualification/death dispatch through [Boss_update_1](../../scripts/Boss_update_1.gml) and its [start](../../scripts/Boss_update_start.gml)/[end](../../scripts/Boss_update_end.gml) helpers, HP-bar updates, gate checks (`Boss_update_4`) and start delay. Horsehead uses `Boss_update_2/3` for melee movement/collision; Carock uses `Boss_update_5` and its own state machine. These are alternatives, not a universal list to call every frame.
3. Define a spawn and usable arena. [rm_data_init_Palc_A](../../scripts/rm_data_init_Palc_A.gml), section `0D`, maps Horsehead to tile file `PalcA_012`, uses `STR_PRIO`, supplies `STR_Arena+'_x'+hex_str(...)`, places a crystal holder, and records boss scene/entrance/dungeon-exit keys. Compare Carock's boss sections in [rm_data_init_Palc_D](../../scripts/rm_data_init_Palc_D.gml). Those dungeon keys are necessary when taking the corresponding progression role; do not assign an unrelated encounter to a palace by copying them blindly.
4. Follow [map metadata regeneration](maps.md#generated-metadata-is-part-of-integration) after scene/spawn changes. A registered boss with no reachable spawn is not integrated.

Conditional points: new music/theme resources (existing `Boss_set_MusicBattle_props` may suffice), projectiles, roar, custom hitboxes, multipart drawing, special quest rewards and randomizer logic. Inspect [GameObjectB_step](../../scripts/GameObjectB_step.gml) before custom rewards: its boss drop path handles keys, camera unlock and a specific `Carock01` version-2 reward branch.

## Failure modes and checklist

Arena geometry comes from scene collision/viewport data and spawn overrides; copying a boss into arbitrary terrain can misplace gates, ground or attacks. `g.view_lock_boss` is shared battle state. A death sequence skipped by custom updates can leave the camera/gates/music locked. Horsehead's second-quest and dungeon checks override base HP/XP. Carock's `behavior` is read by SoundWave-related combat; renaming/reusing that projectile requires inspecting its source-instance coupling.

Horsehead owns `dl_Arm_SPRITES`; Carock owns `dg_Attack3`. Their end scripts guard resource existence, release their data, and call `Boss_end`; generic `GO_instance_end` handles additional common lists. Do not duplicate unguarded cleanup across end/destroy callbacks.

- [ ] Choose melee/multipart Horsehead or state/projectile Carock; inspect both lifecycle wrappers.
- [ ] Register object, version rows, callbacks and assets; verify base init and later overrides.
- [ ] Integrate arena, exits, spawn and applicable progression keys; rebuild metadata.
- [ ] Check health bar, music, gate closure, first attack delay and both facing directions.
- [ ] Test defeat, reward, camera unlock, leaving/re-entering, reload and applicable quests/mods.
- [ ] Verify spawned attacks and repeat-safe cleanup; record runtime evidence or blocker.
