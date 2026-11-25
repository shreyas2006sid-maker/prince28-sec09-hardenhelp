"""Compare the HardenHelp parser with PyYAML across downloaded files."""

import json
from pathlib import Path

import yaml

from hardenhelp.ingest.parse import ParseError, parse_text

MANIFEST = Path("data/raw/manifest.jsonl")


def load_manifest() -> list[dict]:
    """Load successfully downloaded files."""
    records = []

    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if line.strip():
            record = json.loads(line)

            if record.get("status") == "downloaded":
                records.append(record)

    return records


def compare_hardenhelp(path: Path) -> str:
    """Run the existing HardenHelp parser."""
    try:
        parsed = parse_text(path)
        pages = len(parsed.pages)
        characters = sum(len(page.text) for page in parsed.pages)

        return f"SUCCESS: {pages} pages, {characters:,} chars"

    except ParseError as exc:
        return f"FAILED: {exc.reason}"


def compare_pyyaml(path: Path) -> str:
    """Run PyYAML's safe loader."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        result = yaml.safe_load(content)
        result_type = type(result).__name__

        return f"SUCCESS: {result_type}"

    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)

        if mark is not None:
            return f"FAILED: line {mark.line + 1}"

        return f"FAILED: {type(exc).__name__}"

    except OSError as exc:
        return f"FAILED: {type(exc).__name__}"


def main() -> None:
    records = load_manifest()

    print(f"Files selected for comparison: {len(records)}")
    print()
    print("| File | HardenHelp parser | PyYAML |")
    print("|---|---|---|")

    hardenhelp_success = 0
    yaml_success = 0

    for record in records:
        path = Path(record["path"])

        hardenhelp_result = compare_hardenhelp(path)
        yaml_result = compare_pyyaml(path)

        if hardenhelp_result.startswith("SUCCESS"):
            hardenhelp_success += 1

        if yaml_result.startswith("SUCCESS"):
            yaml_success += 1

        print(f"| {path.name} | {hardenhelp_result} | {yaml_result} |")

    print()
    print("--- SUMMARY ---")
    print(f"Total files: {len(records)}")
    print(f"HardenHelp parser: {hardenhelp_success}/{len(records)} successful")
    print(f"PyYAML: {yaml_success}/{len(records)} successful")


if __name__ == "__main__":
    main()
