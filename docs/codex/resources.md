# GameMaker resource integration

The source of build membership is [ZALiA.project.gmx](../../ZALiA.project.gmx). Files on disk are not enough. Use GameMaker: Studio 1.4.9999's resource creation/import controls when available; if editing GMX manually, make bounded edits and validate XML and referenced files. Avoid a full project reserialization that reorders unrelated resources.

## Two concrete integration trails

- **Moblin:** manifest object `objects\MoblA`, script `scripts\Moblin_init2.gml` and related callbacks, sprite `sprites\spr_Moblin_High_DrawA`. [MoblA.object.gmx](../../objects/MoblA.object.gmx) references `Enemy` and the placement sprite; [spr_Moblin_High_DrawA.sprite.gmx](../../sprites/spr_Moblin_High_DrawA.sprite.gmx) references image frame files. [GameObjectData_Create](../../scripts/GameObjectData_Create.gml) registers `MoblA` separately from this build metadata.
- **Fireball1:** manifest object `objects\Fireball1`, scripts `init_Fireball1`, `update_Fireball1`, `usd_Fireball1`, sprite `spr_Fireball1`. [Fireball1.object.gmx](../../objects/Fireball1.object.gmx) inherits `ProjectileHostile`; [spr_Fireball1.sprite.gmx](../../sprites/spr_Fireball1.sprite.gmx) supplies frame/origin data. The registered custom draw slot is zero, unlike Spear's.

## File conventions and obligations

| Resource | Normally created | Normally modified/integrated |
| --- | --- | --- |
| Script | `scripts/Name.gml` | `<script>scripts\Name.gml</script>` in the appropriate logical manifest group; callback registration or an actual caller |
| Object | `objects/Name.object.gmx` | `<object>objects\Name</object>`; parent, sprite, events as appropriate; content registration and spawn/firing path |
| Sprite | `sprites/Name.sprite.gmx`, required `sprites/images/*` frames | `<sprite>sprites\Name</sprite>`; callbacks/placement registration using it |
| Background/tileset | `background/Name.background.gmx`, referenced image | Manifest `<background>` entry; `g_Create` tileset identity/dimension data if consumed from map JSON |
| Sound | `sound/Name.sound.gmx`, referenced `sound/audio/*` | Manifest `<sound>` entry; existing audio theme/caller data when adding a track |
| Included map/data | `datafiles/rm_tile_data/<area>/<name>.json` or generated metadata | Manifest nested `<datafiles>`/`<datafile>` record, export flags/path; scene filename registration as needed |

Object/sprite manifest references omit `.object.gmx`/`.sprite.gmx`, while script references include `.gml`. Follow actual neighboring entries for other resource types. Keep names/case exact: string-built content and tileset keys depend on them. New runtime versions generally need data rows, not duplicate resource files. Existing callback naming families differ; do not rename unrelated assets to enforce one style.

For Included Files, compare the `WestA/WestA_000.json` and `PalcA/PalcA_000.json` manifest records, including `name`, `filename`, export behavior and ConfigOptions. Maintain the directory hierarchy expected by `rm_get_file_data`, not an arbitrary file in the output root. Generated `SceneData01.txt` and `SceneWallData01.txt` are already included at the `rm_tile_data` level.

Mandatory checks: unique resource names, existing referenced frames/audio, valid parent resource, matching registration key and callback signature. Placement sprite geometry is not automatically the combat hitbox. New draw/cleanup scripts, audio, shaders, backgrounds and native rooms are optional only when the feature requires them; do not create blank hooks or new room infrastructure by habit. Respect CONTRIBUTING's restrictions on new resource categories.

Hidden coupling: resource order may affect numeric IDs, and serialized data can contain runtime values. Do not reorder the resource tree casually or assume a numeric asset ID is a stable authored identifier. Cached scene metadata can outlive source registrations. Renaming requires searching both code and data strings, not just changing the GMX filename.

- [ ] Compare Moblin and Fireball1 resource trails before adding the new resource family.
- [ ] Create only necessary files; register each in the manifest using its demonstrated suffix form.
- [ ] Verify parent, sprite origin/frames, sound/background paths, case and name uniqueness.
- [ ] Add callback/property tables and real callers/spawns separately from manifest entries.
- [ ] Verify Included Files output layout and affected generated metadata.
- [ ] Parse changed XML, check missing references, then compile/run in GMS 1.4; XML validity alone is not engine validation.
