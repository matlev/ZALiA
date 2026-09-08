# Working on ZALiA

- Target **GameMaker: Studio 1.4.9999** and `ZALiA.project.gmx`. Use compatible GML scripts/GMX resources, not GMS 2 structs, methods, sequences, or room layers.
- Read [LICENSE](LICENSE) and [CONTRIBUTING.md](CONTRIBUTING.md). Preserve unrelated work. Keep content changes focused; do not redesign shared systems or normalize old code incidentally.
- Behavior is registered in `scripts/GameObjectData_Create.gml` using `data_go_prop1/2/3` and `data_go_scr`. Inspect the registered callbacks and actual callers before editing object events or copying a helper.
- Follow the nearest working implementation. Preserve byte arithmetic, coordinate helpers, update ordering, palette handling, and object/version keys. Some shared helpers branch on exact object identities.
- Add resources to the project manifest as well as disk. A new enemy normally needs callbacks, property registration, and an intentional spawn integration—not a new GameMaker room.
- Runtime maps are JSON in `datafiles/rm_tile_data`. External TMX sources exist separately but their TSX tilesets are missing. Existing JSON runtime support does not imply working Tiled authoring.
- Scene/spawn changes may be bypassed by `SceneData01.txt`; follow the documented regeneration path. Never call JSON parsing or static checks a gameplay test. Report missing IDE/runtime/authoring prerequisites explicitly.

## Find the right starting point

- [Architecture and callback lifecycle](docs/codex/architecture.md)
- [Normal enemies: Bot and Moblin](docs/codex/enemies.md)
- [Bosses: Horsehead and Carock](docs/codex/bosses.md)
- [Projectiles: Spear and Fireball1](docs/codex/projectiles.md)
- [Maps, scenes, Tiled, and generated metadata](docs/codex/maps.md)
- [GameMaker resource registration](docs/codex/resources.md)
- [Validation and onboarding acceptance](docs/codex/validation.md)
- [Visual asset atlas and reference packages](docs/codex/visual-workflow.md)
- [Existing Dev Tools menu and scene warper](docs/codex/debug-tools.md)
