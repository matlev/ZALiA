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


if __name__ == "__main__":
    unittest.main()
