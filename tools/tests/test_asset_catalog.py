"""Fixture checks for resource discovery, missing data, and offline output."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from urllib.parse import unquote

SPEC = importlib.util.spec_from_file_location("catalog", Path(__file__).parents[1] / "generate_asset_catalog.py")
catalog = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(catalog)


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.output = self.root / "dev/generated/catalog"
        for name in ("sprites/images", "background/images", "objects", "scripts", "docs/codex"):
            (self.root / name).mkdir(parents=True)
        (self.root / "ZALiA.project.gmx").write_text(
            '<assets><sprites name="Sprites"><sprites name="Enemies">'
            '<sprite>sprites\\spr_Test</sprite></sprites></sprites>'
            '<backgrounds name="Tiles"><background>background\\ts_Test</background></backgrounds></assets>')
        (self.root / "sprites/spr_Test.sprite.gmx").write_text(
            '<sprite><width>16</width><height>32</height><xorig>8</xorig><yorigin>16</yorigin>'
            '<bbox_right>15</bbox_right><bbox_bottom>31</bbox_bottom><frames>'
            '<frame index="0">images\\frame space.png</frame>'
            '<frame index="1">images\\missing.png</frame></frames></sprite>')
        (self.root / "sprites/images/frame space.png").write_bytes(b"fixture")
        (self.root / "background/ts_Test.background.gmx").write_text(
            '<background><width>128</width><height>128</height><istileset>-1</istileset>'
            '<tilewidth>8</tilewidth><tileheight>8</tileheight><data>images\\tiles.png</data></background>')
        (self.root / "background/images/tiles.png").write_bytes(b"fixture")
        (self.root / "objects/Test.object.gmx").write_text('<object><spriteName>spr_Test</spriteName></object>')
        (self.root / "scripts/Test.gml").write_text('GO_set_sprite(id,spr_Test);\n// spr_Test\nspr_TestExtra;')

    def test_manifest_metadata_and_exact_mentions(self):
        result = catalog.build_catalog(self.root, self.output)
        sprite = next(a for a in result["assets"] if a["name"] == "spr_Test")
        self.assertEqual(sprite["group"], "Sprites / Enemies")
        self.assertEqual(sprite["origin"], [8, 16])
        self.assertEqual(sprite["bbox"], [0, 0, 15, 31])
        self.assertTrue(sprite["registered"])
        self.assertEqual(sprite["mentions"][0]["lines"], [1, 2])
        self.assertEqual(sprite["objects"][0]["field"], "spriteName")
        self.assertTrue(sprite["frames"][0]["exists"])
        self.assertFalse(sprite["frames"][1]["exists"])
        self.assertIn("%20", sprite["frames"][0]["url"])
        self.assertEqual((self.output / unquote(sprite["frames"][0]["url"])).resolve(),
                         self.root / "sprites/images/frame space.png")
        self.assertEqual(len(result["warnings"]), 1)

    def test_unregistered_and_malformed_resources_are_visible(self):
        (self.root / "sprites/extra.sprite.gmx").write_text('<sprite><frames/></sprite>')
        (self.root / "sprites/broken.sprite.gmx").write_text('<sprite>')
        result = catalog.build_catalog(self.root, self.output)
        extra = next(a for a in result["assets"] if a["name"] == "extra")
        self.assertFalse(extra["registered"])
        self.assertTrue(any("broken.sprite.gmx" in w for w in result["warnings"]))
        self.assertTrue(any("no image frames" in w for w in result["warnings"]))

    def test_reference_outside_checkout_is_not_exported(self):
        (self.root / "sprites/unsafe.sprite.gmx").write_text(
            '<sprite><frames><frame index="0">../../outside.png</frame></frames></sprite>')
        result = catalog.build_catalog(self.root, self.output)
        self.assertFalse(any(a["name"] == "unsafe" for a in result["assets"]))
        self.assertTrue(any("reference leaves repository" in w for w in result["warnings"]))

    def test_output_is_deterministic_and_does_not_touch_source(self):
        before = (self.root / "sprites/spr_Test.sprite.gmx").read_bytes()
        catalog.generate(self.root, self.output)
        first = (self.output / "data.js").read_bytes()
        catalog.generate(self.root, self.output)
        self.assertEqual(first, (self.output / "data.js").read_bytes())
        self.assertEqual(before, (self.root / "sprites/spr_Test.sprite.gmx").read_bytes())
        payload = json.loads(first.decode().removeprefix("window.CATALOG = ").strip().removesuffix(";"))
        self.assertEqual(len(payload["assets"]), 2)
        self.assertTrue((self.output / "annotate.js").is_file())

    def test_palette_bgr_aliases_defaults_and_comment_exclusion(self):
        (self.root / "scripts/p_init.gml").write_text('''
C_WHT0=$FFFFFF;
C_RED0=$0000FF;
C_BLU0=$FF0000;
C_GRN0=$00FF00;
C_YLW0=$00FFFF;
C_MGN0=$FF00FF;
C_BLK0=$000000;
C_CYN0=$FFFF00;
C_TEST=$123456;
C_ALIAS=C_TEST;
// PAL_FAKE = build_pal(C_TEST);
/* PAL_FAKE2 = build_pal(C_TEST); */
PAL_TEST = build_pal(C_TEST,C_RED0,C_BLU0,C_GRN0,-2,-2,-2,-2);
PAL_DEFAULT = build_pal(-1,C_ALIAS);
PAL_COPY = PAL_TEST;
PAL_EDIT = strReplaceAt(PAL_COPY, get_pal_col_pos(0,"B"), global.PAL_CHAR_PER_COLOR, color_str(C_TEST));
PAL_EDIT = strReplaceAt(PAL_EDIT, get_pal_col_pos(0,"K"), global.PAL_CHAR_PER_COLOR, color_str(get_pal_color(PAL_EDIT,0,"B")));
PAL_UNRESOLVED = build_pal(dynamic_value);
''')
        result = catalog.build_catalog(self.root, self.output)["palettes"]
        presets = {p["name"]: p for p in result["presets"]}
        self.assertEqual(set(presets), {"PAL_TEST", "PAL_DEFAULT", "PAL_COPY", "PAL_EDIT"})
        self.assertEqual(presets["PAL_TEST"]["colors"][0], [0x56, 0x34, 0x12, 255])
        self.assertEqual(presets["PAL_TEST"]["colors"][4:], presets["PAL_TEST"]["colors"][:4])
        self.assertEqual(presets["PAL_DEFAULT"]["colors"][0], [255,255,255,255])
        self.assertEqual(presets["PAL_DEFAULT"]["colors"][2], [0,0,255,255])
        self.assertEqual(presets["PAL_EDIT"]["colors"][6], [0x56, 0x34, 0x12, 255])
        self.assertEqual(presets["PAL_COPY"]["colors"][6], [0,0,255,255])
        self.assertEqual(result["unresolved"], ["PAL_UNRESOLVED"])

    def test_versions_follow_registration_callbacks_and_item_sprite_assignments(self):
        for name in ("EnemyTest", "ItemTest"):
            (self.root / "objects" / (name + ".object.gmx")).write_text('<object/>')
        (self.root / "scripts/GameObjectData_Create.gml").write_text('''
PIa = global.PI_MOB_RED;
o_name = object_get_name(EnemyTest);
data_go_scr(o_name, Test);
data_go_prop2(o_name+"01", PIa, 0);
// data_go_prop2(o_name+"99", PIa, 0);
o_name = computed_name;
data_go_prop2(o_name+"03", PIa, 0);
o_name = object_get_name(object);
data_go_scr(o_name, Test);
data_go_prop2(o_name+"04", PIa, 0);
o_name = object_get_name(ItemTest);
_PI1=PIa;
data_go_prop2(o_name+"02", _PI1, 0);
''')
        (self.root / "scripts/g_Create.gml").write_text(
            '_obj=ItemTest; _name=object_get_name(_obj); _bit=0; _spr=ts_Test;')
        result = catalog.build_catalog(self.root, self.output)
        sprite = next(a for a in result["assets"] if a["name"] == "spr_Test")
        tile = next(a for a in result["assets"] if a["name"] == "ts_Test")
        self.assertEqual([(v["key"],v["slot"]) for v in sprite["variants"]], [("EnemyTest01","PI_MOB_RED")])
        self.assertEqual([(v["key"],v["slot"]) for v in tile["variants"]], [("ItemTest02","PI_MOB_RED")])
        self.assertTrue(sprite["frames"][0]["previewUrl"].startswith("data:image/png;base64,"))


if __name__ == "__main__":
    unittest.main()
