"""Command-line interface for the HardenHelp downloader."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Download approved HardenHelp source files.")
    parser.add_argument(
        "--csv",
        type=Path,
        default=ROOT / "data" / "sources.csv",
        help="Path to the source inventory CSV.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Minimum delay between requests to the same host.",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=4,
        help="Maximum number of concurrent downloads (1-4).",
    )
    parser.add_argument(
        "--attempts",
        type=int,
        default=4,
        help="Maximum download attempts per source.",
    )
    parser.add_argument(
        "--source",
        type=str,
        help="Download only records matching this source name.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the downloader and print a summary."""
    from hardenhelp.ingest.fetch import fetch_all, read_sources

    args = parse_args()

    if not args.csv.is_file():
        raise SystemExit(f"Source CSV not found: {args.csv}")

    try:
        sources = read_sources(args.csv)
    except (OSError, ValueError) as error:
        raise SystemExit(f"Could not read source CSV: {error}") from error

    if args.source:
        sources = [
            source for source in sources if source.source.casefold() == args.source.casefold()
        ]

    print(f"Loaded {len(sources)} source record(s).")

    def report(result: dict) -> None:
        """Print the result of one source."""
        print(f"{result['status'].upper()}: {result['url']}")
        if result.get("error"):
            print(f"  Reason: {result['error']}")

    try:
        summary = asyncio.run(
            fetch_all(
                sources=sources,
                root=ROOT,
                max_concurrency=args.concurrency,
                per_host_delay=args.delay,
                max_attempts=args.attempts,
                on_result=report,
            )
        )
    except ValueError as error:
        raise SystemExit(str(error)) from error

    print("\nDownload summary:")
    for status, count in summary.items():
        print(f"{status.capitalize()}: {count}")


if __name__ == "__main__":
    main()
