"""Parse downloaded source files and store results in PostgreSQL."""

import argparse
import asyncio
import hashlib
import json
from pathlib import Path

from hardenhelp.config import get_settings
from hardenhelp.db.session import make_engine, make_sessionmaker
from hardenhelp.ingest.parse import ParseError, parse_file
from hardenhelp.ingest.store import (
    document_id,
    parsed_ids,
    save_document,
    save_failure,
)


def load_manifest(path: Path) -> list[dict]:
    """Load downloaded records from the JSONL manifest."""
    if not path.is_file():
        raise FileNotFoundError(f"Manifest not found: {path}")

    records = []

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue

        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on manifest line {line_number}: {exc}") from exc

        if not isinstance(record, dict):
            raise ValueError(f"Manifest line {line_number} must contain an object")

        if record.get("status") == "downloaded":
            records.append(record)

    return records


def add_file_hash(record: dict, path: Path) -> dict:
    """Add the SHA-256 hash expected by the database store."""
    updated_record = record.copy()
    updated_record["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return updated_record


async def process_record(session_factory, record: dict) -> str:
    """Parse one downloaded file and save its result or failure."""
    path = Path(record["path"])

    try:
        if not path.is_file():
            raise ParseError("missing_file", f"File not found: {path}")

        record = add_file_hash(record, path)
        parsed = parse_file(path)

        async with session_factory() as session:
            await save_document(session, record, parsed)

        print(f"PARSED: {path.name}")
        return "parsed"

    except ParseError as exc:
        error = exc

    except Exception as exc:
        error = ParseError("crash", f"{type(exc).__name__}: {exc}")

    if path.is_file() and "sha256" not in record:
        record = add_file_hash(record, path)

    async with session_factory() as session:
        await save_failure(session, record, error)

    print(f"FAILED: {path.name} - {error.reason}: {error.detail}")
    return "failed"


async def main() -> None:
    argument_parser = argparse.ArgumentParser(
        description="Parse downloaded HardenHelp source files."
    )
    argument_parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("data/raw/manifest.jsonl"),
        help="Path to the download manifest.",
    )
    argument_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of downloaded files to parse.",
    )

    args = argument_parser.parse_args()

    if args.limit is not None and args.limit < 1:
        argument_parser.error("--limit must be greater than 0")

    records = load_manifest(args.manifest)

    if args.limit is not None:
        records = records[: args.limit]

    print(f"Loaded {len(records)} downloaded record(s).")

    if not records:
        print("No downloaded records to parse.")
        return

    settings = get_settings()
    engine = make_engine(settings)
    session_factory = make_sessionmaker(engine)

    parsed_count = 0
    failed_count = 0
    skipped_count = 0

    try:
        async with session_factory() as session:
            existing_ids = await parsed_ids(session)

        for record in records:
            if not record.get("path"):
                print("FAILED: Manifest record has no file path.")
                failed_count += 1
                continue

            path = Path(record["path"])

            if not path.is_file():
                print(f"FAILED: File not found: {path}")
                failed_count += 1
                continue

            sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
            external_id = document_id(sha256)

            if external_id in existing_ids:
                print(f"SKIPPED: {path.name} (already stored)")
                skipped_count += 1
                continue

            record["sha256"] = sha256
            result = await process_record(session_factory, record)

            if result == "parsed":
                parsed_count += 1
                existing_ids.add(external_id)
            else:
                failed_count += 1

    finally:
        await engine.dispose()

    print("\nParsing summary:")
    print(f"Parsed: {parsed_count}")
    print(f"Skipped: {skipped_count}")
    print(f"Failed: {failed_count}")
    print(f"Total: {len(records)}")


if __name__ == "__main__":
    asyncio.run(main())
