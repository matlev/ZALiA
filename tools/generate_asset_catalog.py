"""Generate an offline, read-only visual catalog from GMS 1.4 GMX resources.

Python 3 standard library only. Run from any directory; no game files are edited.
Images remain in the repository; keep the generated folder in the same checkout.
"""

import argparse
from collections import defaultdict
import json
import os
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET
from urllib.parse import quote


TEMPLATE_DIR = Path(__file__).resolve().parent / "asset_catalog"


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
    return {"assets": assets, "warnings": warnings, "version": 1}


def generate(root, output):
    catalog = build_catalog(root, output)
    output.mkdir(parents=True, exist_ok=True)
    for filename in ("index.html", "catalog.css", "catalog.js", "annotate.js"):
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
