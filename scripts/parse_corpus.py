"""Parse downloaded source files and store results in PostgreSQL."""

import argparse
import asyncio
import json
from pathlib import Path

from hardenhelp.config import get_settings
from hardenhelp.db.session import make_engine, make_sessionmaker
from hardenhelp.ingest.parse import ParseError, parse_file, parse_text
from hardenhelp.ingest.store import save_failure, save_parsed


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


async def process_record(session_factory, record: dict) -> str:
    """Parse one downloaded file and save its result or failure."""
    path = Path(record["path"])

    try:
        parsed = parse_text(path) if path.suffix.lower() == ".var" else parse_file(path)
    except ParseError as exc:
        reason = exc.reason
        detail = exc.detail
    except Exception as exc:
        reason = "crash"
        detail = f"{type(exc).__name__}: {exc}"
    else:
        async with session_factory() as session, session.begin():
            document = await save_parsed(
                session,
                path=path,
                record=record,
                parsed=parsed,
            )

        print(
            f"PARSED: {path.name} "
            f"(document_id={document.id}, pages={len(parsed.pages)}, "
            f"parser={parsed.parser})"
        )
        return "parsed"

    async with session_factory() as session, session.begin():
        await save_failure(
            session,
            path=path,
            record=record,
            reason=reason,
            detail=detail,
        )

    print(f"FAILED: {path.name} - {reason}: {detail}")
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
    args = argument_parser.parse_args()

    records = load_manifest(args.manifest)
    print(f"Loaded {len(records)} downloaded record(s).")

    if not records:
        print("No downloaded records to parse.")
        return

    settings = get_settings()
    engine = make_engine(settings)
    session_factory = make_sessionmaker(engine)

    parsed_count = 0
    failed_count = 0

    try:
        for record in records:
            if not record.get("path"):
                print("FAILED: Manifest record has no file path.")
                failed_count += 1
                continue

            result = await process_record(session_factory, record)

            if result == "parsed":
                parsed_count += 1
            else:
                failed_count += 1
    finally:
        await engine.dispose()

    print("\nParsing summary:")
    print(f"Parsed: {parsed_count}")
    print(f"Failed: {failed_count}")
    print(f"Total: {len(records)}")


if __name__ == "__main__":
    asyncio.run(main())
