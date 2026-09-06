# Architecture quick reference

This is a source inspection of the current checkout, not a runtime certification. Paths below are relative to this document. Start with the relevant cookbook; the engine is too large to read indiscriminately.

## Where things live

| Concern | Entry points and responsibility |
| --- | --- |
| Build/resource tree/constants | [ZALiA.project.gmx](../../ZALiA.project.gmx), [Default config](../../Configs/Default.config.gmx); IDE groups are largely logical, while most scripts are flat files |
| Startup | [obj_start_Create](../../scripts/obj_start_Create.gml) creates `RoomData`, then `GameObjectData`; [g_Create](../../scripts/g_Create.gml) initializes central state, maps, tilesets and options |
| Central game loop | [g_Step](../../scripts/g_Step.gml), [update_GameObjectMgr](../../scripts/update_GameObjectMgr.gml); `g` owns game state and manager references |
| Player/save/palette | `global.pc` is the player instance; `f` holds file/quest state, `p` palette state. See [PC_init](../../scripts/PC_init.gml), [file_load](../../scripts/file_load.gml), [p_init](../../scripts/p_init.gml) |
| Content tables | [GameObjectData_Create](../../scripts/GameObjectData_Create.gml), `g.dm_go_prop`, `g.dm_go_scr`; per-scene placement is separate in `g.dm_spawn` |
| Scene loading | [RoomData_Create](../../scripts/RoomData_Create.gml), [g_Room_Start](../../scripts/g_Room_Start.gml), [maps](maps.md) |
| Graphics/audio | Sprite/background resources, palette scripts and shaders; [Audio_Create](../../scripts/Audio_Create.gml); follow an existing `get_audio_theme_track` caller for theme integration |

## Callback contract and lifecycle

The concrete [MoblA object](../../objects/MoblA.object.gmx) has a Create event containing comments, not its AI. Its parent chain is `Enemy -> GOB1 -> GameObjectB -> GameObject`. `Bot_A -> Bot -> Enemy` adds another identity layer. `Horsehead01` and `Carock01` inherit `Boss -> Enemy`; `Spear` and `Fireball1` inherit `ProjectileHostile -> GameObjectC -> GameObject`. Inspect parent GMX files when choosing a sibling.

1. [data_go_prop1](../../scripts/data_go_prop1.gml) registers **object name** to asset index, display name, placement sprite and dimensions. Its signature comment is stale: the implementation accepts three arguments, not a separate GO ID.
2. [data_go_prop2](../../scripts/data_go_prop2.gml) registers **object name + `hex_str(ver)`** properties: palette, body-hitbox ID, collision-offset ID, HP index, attack level, XP index, respawn, drops, sword/projectile/THUNDER/SPELL reactions, XP drain, brightness. Negative/omitted arguments do not write a property; zero is a real value. HP/XP are table indices, not literal amounts.
3. [data_go_prop3](../../scripts/data_go_prop3.gml) adds body/shield reaction data, chiefly for projectiles.
4. [data_go_scr](../../scripts/data_go_scr.gml) registers positional callbacks by **object name**: `init1, init2, update, udp, draw, instance-end, destroy, room-end`. Zero/omitted entries are not written. It does not register a Step event or inherit a parent's callback record automatically.
5. [GameObject_create](../../scripts/GameObject_create.gml) calls `instance_create`, then [GameObject_create_1a](../../scripts/GameObject_create_1a.gml), which initializes variables and executes init1 **before setting the requested version**. Next come version/spawn key, [GO_set_prop_values](../../scripts/GO_set_prop_values.gml), placement/palette, spawn position, manager membership, init2, spawn overrides and coordinate/hitbox finalization. Put version- or placement-dependent setup in the appropriate later stage. `scr_init3` exists as a final hook but is not a `data_go_scr` argument.
6. [GameObjectB_init](../../scripts/GameObjectB_init.gml) installs `GameObjectB_step`. The manager executes `scr_step`; [GameObjectB_step](../../scripts/GameObjectB_step.gml) selects normal/update versus explosion/drop states. It handles shared boss-key/drop behavior too. Manager code decrements `timer` for relevant lists: do not blindly decrement it again in AI.
7. `udp` updates presentation data, not network packets. [update_EF11](../../scripts/update_EF11.gml) executes it and handles draw/palette/hitbox work. Projectile presentation uses [Projectile_udd](../../scripts/Projectile_udd.gml). Follow the helper call chain; merely registering `udp` does not ensure your custom update invokes it.
8. [GameObject.object.gmx](../../objects/GameObject.object.gmx) dispatches drawing and cleanup. [GO_instance_end](../../scripts/GO_instance_end.gml) can run from Destroy, Room End, and Game End. Cleanup must tolerate repeat calls and already-released DS resources.

Hostile projectiles use [GOC1_create](../../scripts/GOC1_create.gml), not the normal enemy constructor; see [projectiles](projectiles.md).

## Conventions and ambiguities

- [hex_str](../../scripts/hex_str.gml) emits uppercase hexadecimal with even-digit padding by default: version 1 is `01`. `MoblA01` means object `MoblA`, version 1; `Horsehead0101` means object `Horsehead01`, version 1. Digits already in an asset name are not the runtime version.
- `hspd`/`vspd` often use byte-wrapped values, sign bits and fractional carries. [updateX](../../scripts/updateX.gml), [updateY](../../scripts/updateY.gml), and [set_xy](../../scripts/set_xy.gml) maintain engine coordinates. Native GameMaker `speed`/`hspeed`, or direct `x/y` edits, are not equivalent.
- `xl/yt` are top-left coordinates; sprite origin, `ww/hh`, body hitbox and tile collision offsets are distinct. Use `GO_sprite_init`, `GO_set_sprite`, `set_xy`/`set_xlyt`, `GO_update_cs` as the example does.
- Contribution guidance requests snake_case functions and camelCase variables, but existing callback/resource names use several older styles (`Bot_init2`, `init_Spear`, `usd_Spear`, `_udp`). Retain existing names, follow local families, and do not infer semantics from a suffix alone. `Old1` scripts and commented assembly translations are not evidence of active behavior; trace registrations.
- `data_go_prop2` tries to populate `dl_Enemy_OBJVER` using an OBJVER asset-index key, whereas `data_go_prop1` writes that key at object-name scope. This mismatch is visible in source; do not assume automatic enumeration works or repair it during unrelated content work. Verify any consumer needed by your feature.

## Current platform dependencies

[GMSched.extension.gmx](../../extensions/GMSched.extension.gmx) registers version 1.0.0, `gmsched.dll`, auto-init `gmsched_init`, and scheduler resolution getter/setter functions. The bundled binary is [extensions/GMSched/gmsched.dll](../../extensions/GMSched/gmsched.dll). There are no proxy files or Mac source/linker entries in this extension descriptor.

[g_Step](../../scripts/g_Step.gml) unconditionally gets the scheduler resolution and sets it to 1 when needed. Its comment explicitly ties this to Windows Sleep Margin and smooth frame pacing; Default config sets Windows sleep margin to 1. This is an active Windows DLL dependency, not just an unused import. A modern Mac export cannot be assumed to provide these functions. No substitute or portability behavior has been tested here; the numeric export masks alone do not establish compatibility.

Other relevant constraints: GMX/GMS 1.4 resource APIs (backgrounds, surfaces, shaders), palette shader/GPU assumptions noted in CONTRIBUTING, window/input handling in `g_Step`, and sandbox/local-file behavior (startup explicitly mentions `%localappdata%`). Config contains Mac settings, including placeholder signing fields, which are not evidence of a successful Mac build. Serialized DS payloads and resource indices also deserve preservation when changing toolchains. These are current dependencies to remember, not a migration plan.
