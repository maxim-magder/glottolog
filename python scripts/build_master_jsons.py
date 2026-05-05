from collections import OrderedDict
import configparser
from pathlib import Path
import json

ROOT = Path(".")
TREE_JSON = ROOT / "languoids/tree.json"

LIST_KEYS = {"countries", "macroareas"}


def normalize_value(key: str, value: str):
    if value is None:
        return value
    if key.lower() in LIST_KEYS:
        items = [line.strip() for line in value.splitlines() if line.strip()]
        return items
    return value


def ini_to_ordered_dict(ini_path: Path) -> OrderedDict:
    config = configparser.ConfigParser(
        dict_type=OrderedDict,
        interpolation=None,
    )
    config.optionxform = str
    config.read(ini_path, encoding="utf-8")

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


def load_tree_json() -> OrderedDict:
    with TREE_JSON.open("r", encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=OrderedDict)


def build_master(tree: OrderedDict, config_files, output_path: Path) -> None:
    master = OrderedDict()
    master["config"] = OrderedDict()
    for cfg in config_files:
        master["config"][cfg.name] = ini_to_ordered_dict(cfg)
    master["languoid_tree"] = tree

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(master, f, ensure_ascii=False, indent=2)
    print(f"Wrote {output_path}")


def main() -> None:
    tree = load_tree_json()

    macroareas = ROOT / "config/macroareas.ini"
    aes_status = ROOT / "config/aes_status.ini"
    aes_sources = ROOT / "config/aes_sources.ini"

    build_master(
        tree,
        [macroareas],
        ROOT / "master_macroareas_tree.json",
    )

    build_master(
        tree,
        [aes_status, macroareas],
        ROOT / "master_aes_status_macroareas_tree.json",
    )

    build_master(
        tree,
        [aes_sources, aes_status, macroareas],
        ROOT / "master_aes_sources_aes_status_macroareas_tree.json",
    )


if __name__ == "__main__":
    main()