"""Report parsing coverage for the current downloaded manifest."""

import asyncio
import json
from pathlib import Path

from sqlalchemy import text

from hardenhelp.config import get_settings
from hardenhelp.db.session import make_engine

MANIFEST = Path("data/raw/manifest.jsonl")


def normalise(path: str) -> str:
    return str(Path(path).resolve()).casefold()


def percentage(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "N/A (no records)"
    return f"{numerator / denominator * 100:.2f}%"


def load_manifest() -> list[dict]:
    if not MANIFEST.is_file():
        raise FileNotFoundError(f"Manifest not found: {MANIFEST}")

    return [
        json.loads(line)
        for line in MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.strip() and json.loads(line).get("status") == "downloaded"
    ]


async def main() -> None:
    records = load_manifest()

    manifest_paths = {normalise(record["path"]) for record in records if record.get("path")}

    engine = make_engine(get_settings())

    try:
        async with engine.connect() as connection:
            documents = (
                (
                    await connection.execute(
                        text("""
                        SELECT
                            metadata->>'path' AS path,
                            (metadata->>'pages')::integer AS expected_pages,
                            COUNT(p.id) AS stored_pages
                        FROM documents d
                        LEFT JOIN pages p ON p.document_id = d.id
                        WHERE metadata ? 'path'
                        GROUP BY d.id
                    """)
                    )
                )
                .mappings()
                .all()
            )

            failures = (
                (await connection.execute(text("SELECT path FROM parse_failures"))).mappings().all()
            )

        parsed_by_path = {normalise(row["path"]): row for row in documents if row["path"]}

        failed_paths = {normalise(row["path"]) for row in failures}

        parsed_paths = manifest_paths & parsed_by_path.keys()
        failed_current = manifest_paths & failed_paths

        unmatched_paths = manifest_paths - parsed_by_path.keys() - failed_paths

        expected_pages = sum(parsed_by_path[path]["expected_pages"] or 0 for path in parsed_paths)

        stored_pages = sum(parsed_by_path[path]["stored_pages"] for path in parsed_paths)

        total_files = len(manifest_paths)
        parsed_count = len(parsed_paths)
        failed_count = len(failed_current)
        unmatched_count = len(unmatched_paths)

        print("\nHardenHelp Parsing Coverage")
        print("=" * 45)

        print("\nCurrent Manifest")
        print(f"Downloaded files : {total_files}")
        print(f"Parsed files     : {parsed_count}")
        print(f"Failed files     : {failed_count}")
        print(f"Unmatched files  : {unmatched_count}")
        print(f"Document coverage: {percentage(parsed_count, total_files)}")

        print("\nPage Storage")
        print(f"Expected pages   : {expected_pages}")
        print(f"Stored pages     : {stored_pages}")
        print(f"Page storage coverage: {percentage(stored_pages, expected_pages)}")

        if unmatched_paths:
            print("\nFiles not yet processed:")
            for path in sorted(unmatched_paths):
                print(path)

        if failed_current:
            print("\nFiles with recorded parse failures:")
            for path in sorted(failed_current):
                print(path)

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
