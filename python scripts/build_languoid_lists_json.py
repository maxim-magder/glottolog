from collections import OrderedDict
import json
import re
from pathlib import Path

ROOT = Path(".")
LANGUOIDS = ROOT / "languoids"

CATEGORIES = {
    "dialects": "dialects_*.md",
    "languages": "languages_*.md",
    "families": "families_*.md",
}


def parse_label(label: str):
    codes = []
    remaining = label
    while True:
        match = re.match(r"^(.*)\s*\[([^\]]+)\]\s*$", remaining)
        if not match:
            break
        remaining = match.group(1)
        codes.insert(0, match.group(2))
    return remaining.strip(), codes


def parse_line(line: str):
    line = line.strip()
    if not line.startswith("- [") or "](" not in line or not line.endswith(")"):
        return None

    split_index = line.rfind("](")
    label = line[line.find("[") + 1 : split_index]
    target = line[split_index + 2 : -1]
    if target.endswith("/md.ini"):
        target = target[: -len("md.ini")] + "md.json"
    elif target.endswith(".md"):
        target = target[:-3] + ".json"

    if not label or not target:
        return None

    name, codes = parse_label(label)
    if not name:
        return None

    entry = OrderedDict()
    entry["name"] = name
    if codes:
        entry["glottocode"] = codes[0]
    if len(codes) > 1:
        entry["iso639_3"] = codes[1]
    if len(codes) > 2:
        entry["extra_codes"] = codes[2:]
    entry["path"] = target
    return entry


def parse_file(path: Path):
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        entry = parse_line(line)
        if entry:
            entries.append(entry)
    return entries


def write_json(path: Path, payload: OrderedDict) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"Wrote {path}")


def main() -> None:
    for category, pattern in CATEGORIES.items():
        files = sorted(LANGUOIDS.glob(pattern))
        if not files:
            continue

        master_entries = []
        source_files = []
        for md_path in files:
            entries = parse_file(md_path)
            source_file = str(md_path.with_suffix(".json").relative_to(ROOT))
            source_files.append(source_file)

            payload = OrderedDict()
            payload["source_file"] = source_file
            payload["count"] = len(entries)
            payload["entries"] = entries
            write_json(md_path.with_suffix(".json"), payload)

            for entry in entries:
                master_entry = OrderedDict(entry)
                master_entry["source_file"] = source_file
                master_entries.append(master_entry)

        master_payload = OrderedDict()
        master_payload["source_files"] = source_files
        master_payload["count"] = len(master_entries)
        master_payload["entries"] = master_entries
        write_json(LANGUOIDS / f"{category}.json", master_payload)


if __name__ == "__main__":
    main()
