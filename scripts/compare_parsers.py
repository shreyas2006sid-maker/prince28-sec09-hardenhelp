"""Compare available parsing approaches across the downloaded corpus."""

import json
from pathlib import Path

from hardenhelp.ingest.parse import ParseError, parse_file, parse_text

MANIFEST = Path("data/raw/manifest.jsonl")


def load_manifest() -> list[dict]:
    """Load downloaded files from the manifest."""
    records = []

    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if line.strip():
            record = json.loads(line)

            if record.get("status") == "downloaded":
                records.append(record)

    return records


def main() -> None:
    records = load_manifest()

    print(f"Files selected for comparison: {len(records)}")
    print("=" * 70)

    pdf_count = 0

    for record in records:
        path = Path(record["path"])

        if path.suffix.lower() == ".pdf":
            pdf_count += 1

        print(f"\nFILE: {path.name}")
        print(f"TYPE: {path.suffix.lower()}")

        try:
            parsed = parse_text(path) if path.suffix.lower() == ".var" else parse_file(path)

            total_chars = sum(len(page.text) for page in parsed.pages)
            heading_count = sum(len(page.headings) for page in parsed.pages)
            table_count = sum(page.tables for page in parsed.pages)

            print(f"PARSER: {parsed.parser}")
            print(f"KIND: {parsed.kind}")
            print(f"PAGES: {len(parsed.pages)}")
            print(f"HEADINGS: {heading_count}")
            print(f"TABLES: {table_count}")
            print(f"EXTRACTED CHARACTERS: {total_chars}")
            print(f"TITLE: {parsed.title}")

        except ParseError as exc:
            print(f"FAILED: {exc.reason} - {exc.detail}")

    print("\n" + "=" * 70)
    print("COMPARISON SUMMARY")
    print(f"Total downloaded files: {len(records)}")
    print(f"PDF files available: {pdf_count}")

    if pdf_count == 0:
        print("PDF parser comparison skipped: the corpus contains no PDF files.")

    print(
        "YAML and VAR files use the plain parser. "
        "Their extracted structure should be checked manually."
    )


if __name__ == "__main__":
    main()
