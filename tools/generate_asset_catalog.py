"""Generate an offline, read-only visual catalog from GMS 1.4 GMX resources.

Python 3 standard library only. Run from any directory; no game files are edited.
Source links target the repository; preview PNGs are embedded in generated data.
"""

import argparse
import base64
from functools import lru_cache
from collections import defaultdict
import json
import os
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET
from urllib.parse import quote


TEMPLATE_DIR = Path(__file__).resolve().parent / "asset_catalog"


def active_gml(text):
    """Remove comments, preserving strings and line numbers; never execute GML."""
    pattern = r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|/\*[\s\S]*?\*/|//[^\n]*'
    return re.sub(pattern, lambda m: re.sub(r"[^\n]", " ", m[0])
                  if m[0].startswith(("//", "/*")) else m[0], text)


def palette_data(root, output, assets):
    """Extract a bounded subset of literal palette definitions and registration links.

    This is source inspection, not a GML interpreter or a scene palette resolver.
    Unsupported named palette expressions are reported instead of approximated.
    """
    @lru_cache(maxsize=None)
    def read(name):
        path = root / "scripts" / (name + ".gml")
        return active_gml(path.read_text(encoding="utf-8-sig")) if path.exists() else ""

    source = "scripts/p_init.gml"
    text = read("p_init")
    original_path = root / source
    original_lines = original_path.read_text(encoding="utf-8-sig").splitlines() if original_path.exists() else []
    constants, palettes, unresolved = {}, {}, set()
    order = ["WHT", "RED", "BLU", "GRN", "YLW", "MGN", "BLK", "CYN"]
    # GML packed colors are BGR integers, unlike CSS hex RGB.
    def rgb(value):
        return [value & 255, (value >> 8) & 255, (value >> 16) & 255, 255]

    for line_no, line in enumerate(text.splitlines(), 1):
        match = re.fullmatch(r"\s*(C_\w+)\s*=\s*(\$[0-9A-Fa-f]+|C_\w+)\s*;\s*", line)
        if match:
            key, value = match.groups()
            if value.startswith("$"):
                constants[key] = int(value[1:], 16)
            elif value in constants:
                constants[key] = constants[value]
        match = re.fullmatch(r"\s*(PAL_\w+)\s*=\s*(.*?)\s*;\s*", line)
        if not match or "_SET" in match[1] or match[1].startswith("PAL_POS_") or match[1] == "PAL_PER_SCENE":
            continue
        key, expression = match.groups()
        colors = None
        build = re.fullmatch(r"build_pal\(([^()]*)\)", expression)
        if build and all("C_" + c + "0" in constants for c in order):
            base = [constants["C_" + c + "0"] for c in order]
            args = [arg.strip() for arg in build[1].split(",")]
            values = []
            for arg in args:
                values.append(constants.get(arg) if arg not in ("-1", "-2") else int(arg))
            if len(values) <= 8 and None not in values:
                values += [-1] * (8 - len(values))
                values = [base[i] if v == -1 else v for i, v in enumerate(values)]
                # -2 aliases W/R/B/G for the second quartet; first quartet keeps base.
                colors = [((base[i] if i < 4 else values[i - 4]) if v == -2 else v)
                          for i, v in enumerate(values)]
                colors = [rgb(v) for v in colors]
        elif expression in palettes:
            colors = [c[:] for c in palettes[expression]["colors"]]
        else:
            replace = re.fullmatch(r'strReplaceAt\((PAL_\w+),\s*get_pal_col_pos\(0,"([WRBGYMKC])"\),\s*global.PAL_CHAR_PER_COLOR,\s*color_str\((.*)\)\)', expression)
            if replace and replace[1] in palettes:
                value = constants.get(replace[3])
                lookup = re.fullmatch(r'get_pal_color\((PAL_\w+),0,"([WRBGYMKC])"\)', replace[3])
                color = rgb(value) if value is not None else None
                if lookup and lookup[1] in palettes:
                    color = palettes[lookup[1]]["colors"]["WRBGYMKC".index(lookup[2])][:]
                if color:
                    colors = [c[:] for c in palettes[replace[1]]["colors"]]
                    colors["WRBGYMKC".index(replace[2])] = color
        if colors:
            palettes[key] = {"name": key, "colors": colors, "path": source,
                             "url": url_for(root / source, output), "line": line_no,
                             "description": original_lines[line_no-1].partition("//")[2].strip()}
            unresolved.discard(key)
        else:
            palettes.pop(key, None)
            unresolved.add(key)

    by_name = {a["name"]: a for a in assets}
    registrations = read("GameObjectData_Create")
    aliases = dict(re.findall(r"\b(PI\w+)\s*=\s*global\.(PI_\w+)\s*;", registrations))
    # Blocks bounded by literal object_get_name assignments. Do not guess computed keys.
    starts = list(re.finditer(r"\bo_name\s*=\s*([^;]+);", registrations))
    items = read("g_Create")
    item_sprites = defaultdict(set)
    for m in re.finditer(r"_obj\s*=\s*(\w+);\s*_name=object_get_name\(_obj\);\s*_bit=[^;]+;\s*_spr=(\w+);", items):
        item_sprites[m[1]].add(m[2])
    for index, start in enumerate(starts):
        object_expression = re.fullmatch(r"object_get_name\((\w+)\)\s*", start[1])
        if not object_expression:
            continue
        obj = object_expression[1]
        # `object_get_name(object)` uses a variable, not a literal resource key.
        if not (root / "objects" / (obj + ".object.gmx")).is_file():
            continue
        block = registrations[start.end():starts[index+1].start() if index+1 < len(starts) else len(registrations)]
        related = set(item_sprites[obj])
        prop = re.search(r"data_go_prop1\([^;]+\);", block)
        if prop:
            related.update(set(re.findall(r"\b\w+\b", prop[0])) & by_name.keys())
        callback = re.search(r"data_go_scr\(([^;]+)\);", block)
        if callback:
            for name in re.findall(r"\b\w+\b", callback[1]):
                related.update(set(re.findall(r"\b\w+\b", read(name))) & by_name.keys())
        for m in re.finditer(r'data_go_prop2\(\s*o_name\s*\+\s*"([0-9A-Fa-f]+)"\s*,\s*([^,\)]+)', block):
            token = m[2].strip()
            # Resolve a simple local slot alias only within this registration block.
            local = re.findall(r"\b" + re.escape(token) + r"\s*=\s*(PI\w+)\s*;", block[:m.start()])
            if local:
                token = local[-1]
            slot = aliases.get(token, token.removeprefix("global."))
            line = registrations[:start.end()+m.start()].count("\n") + 1
            variant = {"key": obj + m[1], "slot": slot, "line": line,
                       "path": "scripts/GameObjectData_Create.gml",
                       "url": url_for(root / "scripts/GameObjectData_Create.gml", output)}
            for name in related & by_name.keys():
                by_name[name].setdefault("variants", []).append(variant)
    return {"presets": list(palettes.values()), "unresolved": sorted(unresolved),
            "base": [rgb(constants.get("C_" + c + "0", v)) for c, v in zip(order,
                      [0xffffff, 0xff, 0xff0000, 0xff00, 0xffff, 0xff00ff, 0, 0xffff00])]}


def repo_path(root, value, base=None):
    """Accept GMX Windows separators, but never link outside the checkout."""
    candidate = ((base or root) / value.replace("\\", "/")).resolve()
    if not candidate.is_relative_to(root):
        raise ValueError("reference leaves repository: " + value)
    return candidate


def url_for(path, output):
    return quote(os.path.relpath(path, output).replace("\\", "/"), safe="/")


def number(node, name, default=0):
    return int(node.findtext(name, str(default)))


def manifest_groups(root):
    tree = ET.parse(root / "ZALiA.project.gmx")
    groups = {}
    # Group nodes are plural; resource leaves use singular tags.
    def visit(node, trail):
        if node.tag in ("sprites", "backgrounds"):
            trail = trail + [node.get("name", node.tag)]
        if node.tag in ("sprite", "background") and node.text:
            suffix = ".sprite.gmx" if node.tag == "sprite" else ".background.gmx"
            path = repo_path(root, node.text.strip() + suffix)
            groups[path] = " / ".join(trail)
        for child in node:
            visit(child, trail)
    visit(tree.getroot(), [])
    return groups


def build_catalog(root, output):
    root, output = root.resolve(), output.resolve()
    groups = manifest_groups(root)
    assets, warnings = [], []
    for folder, kind, suffix in (("sprites", "sprite", ".sprite.gmx"),
                                 ("background", "background", ".background.gmx")):
        paths = set((root / folder).glob("*" + suffix))
        paths.update(path for path in groups if path.name.endswith(suffix))
        for path in sorted(paths, key=lambda p: p.name.casefold()):
            try:
                node = ET.parse(path).getroot()
                name = path.name.removesuffix(suffix)
                asset = {
                    "name": name, "kind": kind, "group": groups.get(path, "Unregistered"),
                    "registered": path in groups,
                    "path": path.relative_to(root).as_posix(), "sourceUrl": url_for(path, output),
                    "width": number(node, "width"), "height": number(node, "height"),
                    "frames": [], "mentions": [], "objects": [],
                }
                if kind == "sprite":
                    asset["origin"] = [number(node, "xorig"), number(node, "yorigin")]
                    asset["bbox"] = [number(node, "bbox_left"), number(node, "bbox_top"),
                                     number(node, "bbox_right"), number(node, "bbox_bottom")]
                    asset["bboxMode"] = number(node, "bboxmode")
                    frames = [(frame.get("index", "?"), frame.text or "")
                              for frame in node.findall("./frames/frame")]
                else:
                    asset["tile"] = {key: number(node, key) for key in
                                     ("istileset", "tilewidth", "tileheight", "tilexoff",
                                      "tileyoff", "tilehsep", "tilevsep")}
                    frames = [("0", node.findtext("data", ""))]
                for index, value in frames:
                    image_path = repo_path(root, value, path.parent)
                    exists = bool(value) and image_path.is_file()
                    asset["frames"].append({"index": index, "url": url_for(image_path, output),
                                            "path": image_path.relative_to(root).as_posix(),
                                            "exists": exists})
                    if exists:
                        # Embedded PNGs keep canvas pixel reads origin-clean on file://.
                        asset["frames"][-1]["previewUrl"] = "data:image/png;base64," + base64.b64encode(image_path.read_bytes()).decode("ascii")
                    if not exists:
                        warnings.append(f"{name}: missing image {value!r}")
                if not frames:
                    warnings.append(f"{name}: no image frames")
                assets.append(asset)
            except (ET.ParseError, OSError, ValueError) as error:
                warnings.append(f"{path.relative_to(root)}: {error}")

    by_name = {asset["name"]: asset for asset in assets}
    # Exact identifier occurrences, explicitly not a behavior/animation inference.
    # Include comments in these source mentions and label that limitation in the UI.
    for path in sorted((root / "scripts").rglob("*.gml")):
        content = path.read_text(encoding="utf-8-sig", errors="replace")
        hits = defaultdict(list)
        for line_no, line in enumerate(content.splitlines(), 1):
            for name in set(re.findall(r"[A-Za-z_][A-Za-z_0-9]*", line)) & by_name.keys():
                hits[name].append(line_no)
        for name, lines in hits.items():
            by_name[name]["mentions"].append({"path": path.relative_to(root).as_posix(),
                                              "url": url_for(path, output), "lines": lines})
    for path in sorted((root / "objects").glob("*.object.gmx")):
        try:
            node = ET.parse(path).getroot()
            for field in ("spriteName", "maskName"):
                name = node.findtext(field)
                if name in by_name:
                    by_name[name]["objects"].append({"path": path.relative_to(root).as_posix(),
                                                   "url": url_for(path, output), "field": field})
        except (ET.ParseError, OSError) as error:
            warnings.append(f"{path.relative_to(root)}: {error}")
    palettes = palette_data(root, output, assets)
    return {"assets": assets, "warnings": warnings, "palettes": palettes, "version": 2}


def generate(root, output):
    catalog = build_catalog(root, output)
    output.mkdir(parents=True, exist_ok=True)
    for filename in ("index.html", "catalog.css", "catalog.js", "annotate.js", "palettes.js"):
        shutil.copyfile(TEMPLATE_DIR / filename, output / filename)
    index = output / "index.html"
    index.write_text(index.read_text(encoding="utf-8").replace(
        "../../../docs/codex/visual-workflow.md", url_for(root / "docs/codex/visual-workflow.md", output)),
        encoding="utf-8")
    # Separate classic JS works from file:// without fetch or an HTTP server.
    payload = json.dumps(catalog, ensure_ascii=True, separators=(",", ":"))
    (output / "data.js").write_text("window.CATALOG = " + payload + ";\n", encoding="utf-8")
    (output / "diagnostics.json").write_text(json.dumps(catalog["warnings"], indent=2) + "\n",
                                            encoding="utf-8")
    return catalog


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=TEMPLATE_DIR.parent.parent)
    parser.add_argument("--output", type=Path, help="default: ROOT/dev/generated/asset-catalog")
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output.resolve() if args.output else root / "dev/generated/asset-catalog"
    try:
        catalog = generate(root, output)
    except (OSError, ET.ParseError, ValueError) as error:
        parser.exit(1, f"Cannot generate catalog: {error}\n")
    registered = sum(asset["registered"] for asset in catalog["assets"])
    print(f"Catalog: {output / 'index.html'}")
    print(f"{len(catalog['assets'])} assets; {registered} registered; "
          f"{len(catalog['warnings'])} warnings (see diagnostics.json)")


if __name__ == "__main__":
    main()
