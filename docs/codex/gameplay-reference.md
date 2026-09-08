# Gameplay and visual reference

The user supplied **Z2Adventuresome Guide** to help convey the spirit of ZALiA when discussing new content. Use it for player-facing context alongside the implementation cookbooks, particularly for exploration, progression, encounter placement and the purpose of a room.

## Location and scope

Local external folder: `C:\Users\azure\Downloads\Z2Adventuresome Guide`. Start with `home.html`; pages link to local `images/` files. If this folder is unavailable in a future environment, ask for its current location rather than assuming it is part of Git. No internet copy is needed when these files are available.

Inspected inventory: 17 HTML pages and 185 image files; all 184 local HTML image references resolve. The guide credits **FranckKnight** and requests permission for use of its material. Keep the original guide and screenshots external; this repository contains only reference notes, not a redistribution of that material.

This is a historical walkthrough, not a specification of the current build. `DeathMountain.html` distinguishes P00/P03 exit/elevator behavior; `SecondQuest.html` mentions a P03 thrust-retention bug. The guide sometimes expresses uncertainty or gives player strategies rather than design intent. Confirm mechanics against the current scripts and runtime before implementing a change.

## Where to look

All filenames below are relative to the external guide folder.

| Design question | Useful pages and images |
| --- | --- |
| Starting experience, village services, hints and early rewards | `home.html`, `NorthPalace.html`, `images/RauruMap.png` |
| First dungeon: keys, branches, roof detour, Candle, boss, optional return | `ParapaPalace.html`, `images/ParapaPalaceMap.png`, `images/Parapa-Path1.png` through `Parapa-Path6.png` |
| Cave connections, traversal variety and revisiting earlier landmarks | `DeathMountain.html`, `images/Ch4-DeathMountain.png`, `images/Ch4-HammerCave.png` |
| Upgrade-enabled exploration across previously visited regions | `TreasureHunt.html`, `images/WorldMap.png`, `images/WorldMap-Final.png` |
| Late dungeon loops, drops, key gating, recovery and optional rewards | `GreatPalace.html`, `images/GreatPalaceMap.png`, `images/GreatPalaceMapPath1.png` through `GreatPalaceMapPath15.png` |
| Changes to assumptions about progression, enemies and item placement | `SecondQuest.html`, `Rando.html`; `Dragmire.html` for the additional region |

Other regional chapters: `RutoVillage.html`, `MidoroPalace.html`, `IslandPalace.html`, `NorthernIslands.html`, `MazeIsland.html`, `OceanPalace.html`, `KasutoRegion.html`, `EyeRockPalace.html`.

The guide explicitly compacts dungeon maps and uses markers for some displaced connections. Screenshot placement, route numbers and cave letters are **guide annotations**, not GameMaker coordinates, scene IDs or Tiled filenames. Read the relevant walkthrough section and transition markers together. The small in-game map screenshots also omit some within-room obstructions.

Some full maps are very large panoramas: `ParapaPalaceMap.png` is 21706 × 2881 pixels. Inspect relevant regions at readable zoom rather than trusting a downscaled overview. Such images exceed the atlas annotator's 20-megapixel input limit; use a screenshot of the relevant region for a [reference brief](visual-workflow.md).

## Design observations to discuss, not universal rules

- **Show something worth returning for.** North Palace's early EXP ledge and Parapa's visible roof heart piece give context to later abilities or a longer route. Ask what the player notices before they can reach a reward.
- **Let upgrades change how familiar places are used.** The Candle changes dark-room exploration; the Hammer and Flying Boots open revisits and routes. Ask what a new ability changes beyond its pickup room.
- **Consider the cost of a failed attempt or detour.** Parapa's roof route can drop the player into an earlier room. The guide also discusses recovery pickups, enemy respawn differences, village travel and palace shortcuts. Evaluate the whole return trip, not only the individual jump or fight.
- **Place encounters in a spatial context.** The Death Mountain route descriptions distinguish slopes, pits, bridges and platforming by their enemies and hazards. Consider how terrain and enemy behavior interact, and which abilities the player is expected to have.
- **Distinguish route progress from optional payoff.** The walkthrough separates key/tool/boss routes from container pieces, EXP bags, Gold Slimes and broader treasure hunts. State whether a proposed reward or challenge is required, optional now, or intended for a later return.
- **Name the quest and settings.** Second Quest and randomization alter available abilities, hazards and routes. A sensible First Quest assumption may be wrong elsewhere.

These are interpretations of the sampled player experience, not claims about HoverBat's stated intentions or requirements for every future addition. The user's specific design goals take precedence.

## Connect a reference to an implementation

For example, `ParapaPalace.html` describes the entrance roof heart piece, torch-lit rooms and Horsehead. [rm_data_init_Palc_A.gml](../../scripts/rm_data_init_Palc_A.gml) names Parapa, registers a heart piece in scene `00`, registers `TorchA` in dark scenes, and puts `Horsehead01` in logical scene `0D` using tile file `PalcA_012`. This confirms useful points of correspondence, not complete walkthrough/build parity. [maps.md](maps.md) explains the separate scene IDs, JSON and cached metadata that must be checked.

For a future content request:

1. Read the relevant guide chapter and view the local map/detail images; record the page/image and described location.
2. State the intended player experience, required abilities, optional rewards, return route and quest/settings.
3. Resolve the actual scene/tile/spawn data in the repository; verify connections instead of translating screenshot positions directly into coordinates.
4. Follow the nearest working content implementation and its cookbook. Report guide/source disagreements and validate the changed runtime behavior.

Initial review sampled the introduction, North Palace, Parapa, Death Mountain, Treasure Hunt, Great Palace routing, Second Quest and Rando text; visually inspected the Death Mountain cave diagram, small Parapa map and pillar screenshot. This was not an exhaustive review of all chapters/images or a gameplay test.
