"""Check boss-test resource/data integration; this is NOT a GML/runtime test.

Reads the checked-in SceneData01 cache, as the game normally does. The small
decoder below supports only the flat DS-map types observed in that cache and
fails on unknown types/versions instead of guessing. No save files are read.
"""
from __future__ import annotations

import json
import re
import struct
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def flat_map(encoded: str) -> dict:
    data = bytes.fromhex(encoded)
    version, count = struct.unpack_from("<II", data)
    assert version == 402, f"Unsupported DS-map version {version}"
    pos = 8

    def value():
        nonlocal pos
        kind = struct.unpack_from("<I", data, pos)[0]
        pos += 4
        if kind in (0, 10):
            result = struct.unpack_from("<d" if kind == 0 else "<q", data, pos)[0]
            pos += 8
            return result
        if kind == 1:
            size = struct.unpack_from("<I", data, pos)[0]
            pos += 4
            result = data[pos:pos + size].decode("utf-8")
            pos += size
            return result
        raise AssertionError(f"Unsupported DS value type {kind} at {pos - 4}")

    result = {}
    for _ in range(count):
        key = value()
        assert key not in result, f"Duplicate cache key {key}"
        result[key] = value()
    assert pos == len(data), "Unconsumed DS-map bytes"
    return result


def source(name: str) -> str:
    return (ROOT / "scripts" / f"{name}.gml").read_text(encoding="utf-8-sig")


def main() -> None:
    project = ET.parse(ROOT / "ZALiA.project.gmx").getroot()
    script_paths = [node.text.replace("\\", "/") for node in project.iter("script")]
    new_scripts = list((ROOT / "scripts").glob("dev_boss_test_*.gml"))
    new_scripts += list((ROOT / "scripts").glob("OptionsMenu_*BossTest*.gml"))
    new_scripts += list((ROOT / "scripts").glob("OptionsMenu_*BossHero*.gml"))
    for path in new_scripts:
        assert script_paths.count(path.relative_to(ROOT).as_posix()) == 1, path.name
        assert not re.search(r"\b(function|constructor)\b", re.sub(r"//[^\n]*", "", path.read_text(encoding="utf-8-sig"))), path.name
    for path in script_paths:
        assert (ROOT / path).is_file(), f"Missing registered script: {path}"

    # Find actual registered Boss descendants, not only names on a copied list.
    parents = {}
    for path in (ROOT / "objects").glob("*.object.gmx"):
        parents[path.name.removesuffix(".object.gmx")] = ET.parse(path).getroot().findtext("parentName")

    def boss(name):
        seen = set()
        while name in parents and name not in seen:
            if name == "Boss":
                return True
            seen.add(name)
            name = parents[name]
        return False

    cache = json.loads((ROOT / "datafiles/rm_tile_data/SceneData01.txt").read_text(encoding="utf-8-sig"))
    spawns = flat_map(cache["spawn_data"])
    scenes = flat_map(cache["scene_data"])
    dimensions = flat_map(cache["_Tile_File_Dimensions"])
    tile_files = {}
    for path in (ROOT / "datafiles/rm_tile_data").rglob("*.json"):
        tile_files.setdefault(path.stem, []).append(path)
    catalog = source("dev_boss_test_catalog")
    # Discovery uses data_go_prop1's index registry, not names mentioned in
    # selector code (which are only phase, entrance, or label exceptions).
    property_types = set(re.findall(r"data_go_prop1\(\s*(\w+)\s*,", source("GameObjectData_Create")))
    assert "ds_map_find_first(g.dm_go_prop)" in catalog
    assert "is_ancestor(_registered,Boss)" in catalog
    assert "_registered!=Rebonack01B" in catalog
    assert "dk_FullName" in catalog
    registered = []
    for name in sorted(parents):
        count = int(spawns.get(name + "_Count", 0))
        if not boss(name) or not count or name == "Rebonack01B":
            continue
        assert name in property_types, f"Spawned boss lacks data_go_prop1 registration: {name}"
        for index in range(1, count + 1):
            key = spawns[f"{name}{index:02X}_Spawn_Datakey"]
            # Phase02 is the Ganon3 transit scene, not another boss fight.
            data = [spawns.get(f"{key}_Data{i:02X}") for i in range(1, 16)]
            if name == "Ganon3" and any(isinstance(v, str) and v.startswith("_Phase") and v != "_Phase00" for v in data):
                continue
            registered.append((name, key))

    counts = []
    for quest in (1, 2):
        entries = []
        for name, key in registered:
            if quest == 1 and name in ("Ganon1", "Ganon2", "Ganon3"):
                continue
            if f"{quest:02X}" not in spawns.get(key + "_Qualified_Quest_Nums", "0102"):
                continue
            scene = spawns[key + "_Rm_Name"]
            entrance = scenes.get(scene + "_Exit01_Name")
            assert isinstance(entrance, str), f"No entrance: {scene}"
            if name == "Ganon1":
                exits = [scenes[f"{scene}_Exit{i:02X}_Name"]
                         for i in range(1, int(scenes[scene + "_Exit_Count"]) + 1)]
                left = [e for e in exits if int(scenes[e + "_Num"]) & 0x20]
                assert len(left) == 1, f"Ganon P1 needs one normal left entrance: {left}"
                assert entrance != left[0], "Review Ganon P1 first-exit workaround: cache changed"
                assert "g.EXIT_DIR_LEFT" in catalog
            filename = scenes.get(f"{scene}_FileName_Quest{quest:02X}")
            # g_Room_Start chooses Q1 tiles where no Q2 override exists.
            if filename is None:
                filename = scenes.get(f"{scene}_FileName_Quest01")
            assert filename in tile_files, f"Missing Q{quest} tile file for {scene}: {filename}"
            assert len(tile_files[filename]) == 1, f"Ambiguous tile file: {filename}"
            assert dimensions.get(filename + "_Width", 0) > 0, filename
            assert dimensions.get(filename + "_Height", 0) > 0, filename
            entries.append((name, key, int(spawns[key + "_Version"])))
        counts.append(len(entries))
        print(f"Quest {quest}: {len(entries)} encounters")
        for name, key, version in entries:
            print(f"  {name:15} v{version}  {key}")
        assert any(n == "Carock01" and v == 2 and k.startswith("_EastA_51") for n, k, v in entries), "Pendant Carock missing"
        assert any(n == "Rebonack01A" and v == 2 for n, k, v in entries), "Dark Knight missing"
    # New registered encounters may increase these totals without checker edits.
    assert all(counts), "No eligible boss encounters discovered"

    # Launch runs on OptionsMenu. rmA_ACTION is a g-owned alias, not an asset.
    launch = re.sub(r"//[^\n]*", "", source("dev_boss_test_start"))
    assert not re.search(r"(?<![\w.])rmA_ACTION\b", launch), "Unqualified action-room alias in OptionsMenu context"
    assert "g.rmA_ACTION" in launch, "Use g's configured action room for tests"

    # Guard placement matters: no disk write or normal completion first.
    for name in ("file_save", "save_game_pref", "set_saved_value"):
        text = source(name)
        assert text.index("if (dev_boss_test_active()) exit;") < text.index("file_text_open_write"), name
    for name, marker in (("Ganon1_update_battle", "var _DATAKEY = get_defeated_dk()+dk_spawn;"),
                         ("Ganon2_update_battle", "f.dm_quests[?Defeated_DATAKEY] =")):
        text = source(name)
        assert text.index("dev_boss_test_defeated(id)") < text.index(marker), name
    assert "_boss.object_index==Rebonack01A) return false" in source("dev_boss_test_defeated")
    assert "_OBJECT!=Rebonack01B" in source("GameObject_create")
    assert "Cutscene_ShadowBoss_1" in source("GameObject_create")
    # Hero preferences remain distinct from gameplay state, and must survive
    # restoration of the encoded-save cache captured before opening Options.
    hero_load = source("OptionsMenu_BossHero_load")
    hero_save = source("OptionsMenu_BossHero_save")
    assert 'BossHero_dg[#2,12]=1;' in hero_load
    assert 'BossHero_dg[#2,13]=1;' in hero_load
    assert 'val(_dm[?BossHero_dg[#0,_i]],_max)' in hero_load
    assert 'set_saved_value(f.file_num,"_DevBossTest_HeroStats_v1"' in hero_save
    assert 'file_save(' not in hero_save
    assert hero_save.index('if (dev_boss_test_active()') < hero_save.index('set_saved_value(')
    assert hero_save.index('set_saved_value(') < hero_save.index('ds_map_write(global.dm_save_file_data)')
    assert 'if (menu_state==menu_state_BOSS_HERO) OptionsMenu_BossHero_save();' in source("update_OptionsMenu")
    assert source("dev_boss_test_start").index('OptionsMenu_BossHero_load();') < source("dev_boss_test_start").index('global.DevBossTest_stage=1;')
    assert 'dev_boss_test_hero_apply();' in source("dev_boss_test_room_start")
    assert not re.search(r'\blives\s*=', source("dev_boss_test_hero_apply")), "Tests must leave spare lives unchanged"
    # Every editable collectible must resolve through the same item registry
    # used by the randomizer (no accidental zero-bit toggles).
    keys = re.search(r'ds_list_add\(_keys,(.*?)\);', hero_load, re.S).group(1)
    item_types = [key.strip() for key in keys.split(',')][:11]
    item_registry = source("g_Create")
    for item_type in item_types:
        assert re.search(re.escape(item_type) + r'\+STR_Bit\]\s*=\s*_bit;', item_registry), item_type
    print(f"PASS: {len(new_scripts)} scripts registered; cache roster and source guards checked.")
    print("GML compilation and gameplay/state restoration remain separate runtime checks.")


if __name__ == "__main__":
    main()
