from pathlib import Path
import re

ROOT = Path(".")
LANGUOIDS = ROOT / "languoids"

INDEX_FILES = ["languages.md", "families.md", "dialects.md"]
LIST_PATTERNS = ["languages_*.md", "families_*.md", "dialects_*.md"]

INDEX_LINK_RE = re.compile(r"\((languages|families|dialects)_[a-z0-9]+\.md\)")
TREE_MD_INI_RE = re.compile(r"\(tree/[^)]+/md\.ini\)")


def update_index_files() -> None:
    for name in INDEX_FILES:
        path = LANGUOIDS / name
        text = path.read_text(encoding="utf-8")
        text = INDEX_LINK_RE.sub(r"(\1.json)", text)
        path.write_text(text, encoding="utf-8")

    readme = LANGUOIDS / "README.md"
    text = readme.read_text(encoding="utf-8")
    text = text.replace("(languages.md)", "(languages.json)")
    text = text.replace("(families.md)", "(families.json)")
    text = text.replace("(dialects.md)", "(dialects.json)")
    readme.write_text(text, encoding="utf-8")


def update_list_files() -> None:
    for pattern in LIST_PATTERNS:
        for path in sorted(LANGUOIDS.glob(pattern)):
            text = path.read_text(encoding="utf-8")
            text = TREE_MD_INI_RE.sub(lambda m: m.group(0).replace("md.ini", "md.json"), text)
            path.write_text(text, encoding="utf-8")


def main() -> None:
    update_index_files()
    update_list_files()


if __name__ == "__main__":
    main()
