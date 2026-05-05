from collections import OrderedDict
import configparser
from pathlib import Path
import json

ROOT = Path(".")  # run from repo root

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


def main() -> None:
    for ini_file in sorted(ROOT.rglob("*.ini")):
        json_path = ini_file.with_suffix(".json")
        data = ini_to_ordered_dict(ini_file)
        with json_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Wrote {json_path}")


if __name__ == "__main__":
    main()