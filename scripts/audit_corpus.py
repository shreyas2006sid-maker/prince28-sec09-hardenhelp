"""Compare the current download manifest with PostgreSQL records."""

import asyncio
import json
from pathlib import Path

from sqlalchemy import text

from hardenhelp.config import get_settings
from hardenhelp.db.session import make_engine


def normalise(path: str) -> str:
    return str(Path(path).resolve()).casefold()


async def main() -> None:
    manifest_path = Path("data/raw/manifest.jsonl")

    records = [
        json.loads(line)
        for line in manifest_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    downloaded = [
        record for record in records if record.get("status") == "downloaded" and record.get("path")
    ]

    manifest_paths = {normalise(record["path"]) for record in downloaded}

    engine = make_engine(get_settings())

    try:
        async with engine.connect() as connection:
            documents = (
                (
                    await connection.execute(
                        text("""
                        SELECT
                            d.id,
                            d.title,
                            d.metadata->>'path' AS path,
                            d.metadata->>'parser' AS parser,
                            d.metadata->>'pages' AS expected_pages,
                            COUNT(p.id) AS stored_pages
                        FROM documents d
                        LEFT JOIN pages p ON p.document_id = d.id
                        GROUP BY d.id
                        ORDER BY d.id
                    """)
                    )
                )
                .mappings()
                .all()
            )

            failures = (
                (
                    await connection.execute(
                        text("""
                        SELECT path, reason
                        FROM parse_failures
                        ORDER BY path
                    """)
                    )
                )
                .mappings()
                .all()
            )

        database_paths = {normalise(row["path"]) for row in documents if row["path"]}

        print("\nCURRENT MANIFEST")
        print("=" * 65)
        print(f"Downloaded records: {len(downloaded)}")

        print("\nPOSTGRESQL DOCUMENTS")
        print("=" * 65)
        print(f"Parsed documents: {len(documents)}")
        print(f"Parse failures: {len(failures)}")

        print("\nDOCUMENT DETAILS")
        print("-" * 65)

        for row in documents:
            print(
                f"ID={row['id']} | "
                f"Title={row['title']} | "
                f"Parser={row['parser']} | "
                f"Pages={row['stored_pages']}/{row['expected_pages']} | "
                f"Path={row['path']}"
            )

        print("\nMANIFEST FILES NOT MATCHED IN DATABASE")
        print("-" * 65)

        missing = manifest_paths - database_paths
        if missing:
            for path in sorted(missing):
                print(path)
        else:
            print("None")

        print("\nDATABASE FILES NOT IN CURRENT MANIFEST")
        print("-" * 65)

        extra = database_paths - manifest_paths
        if extra:
            for path in sorted(extra):
                print(path)
        else:
            print("None")

        print("\nRECORDED PARSE FAILURES")
        print("-" * 65)

        if failures:
            for failure in failures:
                print(f"{failure['reason']} | {failure['path']}")
        else:
            print("None")

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
