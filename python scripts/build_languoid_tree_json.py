from collections import OrderedDict
import configparser
from pathlib import Path
import json

TREE_ROOT = Path("languoids/tree")
OUTPUT = Path("languoids/tree.json")

LIST_KEYS = {"countries", "macroareas"}


def normalize_value(key: str, value: str):
    if value is None:
        return value
    if key.lower() in LIST_KEYS:
        items = [line.strip() for line in value.splitlines() if line.strip()]
        return items
    return value


def load_ini_file(path: Path) -> OrderedDict:
    config = configparser.ConfigParser(
        dict_type=OrderedDict,
        interpolation=None,
    )
    config.optionxform = str
    config.read(path, encoding="utf-8")

    data = OrderedDict()
    if config.defaults():
        data["DEFAULT"] = OrderedDict(
            (key, normalize_value(key, value))
            for key, value in config.defaults().items()
        )
    for section in config.sections():
        section_items = OrderedDict()
        for key, value in config._sections[section].items():
            if key == "__name__":
                continue
            section_items[key] = normalize_value(key, value)
        data[section] = section_items
    return data


def build_node(dir_path: Path) -> OrderedDict:
    is_root = dir_path == TREE_ROOT
    rel_path = "" if is_root else str(dir_path.relative_to(TREE_ROOT))
    parent_path = None if is_root else str(dir_path.parent.relative_to(TREE_ROOT))

    node = OrderedDict()
    node["path"] = rel_path
    node["glottocode"] = None if is_root else dir_path.name
    node["name"] = None
    node["parent"] = parent_path
    node["ini_files"] = OrderedDict()

    for ini_file in sorted(dir_path.glob("*.ini")):
        node["ini_files"][ini_file.name] = load_ini_file(ini_file)

    md_core = node["ini_files"].get("md.ini", {}).get("core", {})
    if "name" in md_core:
        node["name"] = md_core["name"]

    children = []
    for child in sorted(p for p in dir_path.iterdir() if p.is_dir()):
        children.append(build_node(child))
    node["children"] = children
    return node


def main() -> None:
    tree = build_node(TREE_ROOT)
    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(tree, f, ensure_ascii=False, indent=2)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()