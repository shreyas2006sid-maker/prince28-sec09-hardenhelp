"""Command-line interface for the HardenHelp downloader."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def add_download_arguments(parser: argparse.ArgumentParser) -> None:
    """Add common downloader options."""

    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Minimum delay between requests to the same host.",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        choices=range(1, 5),
        default=4,
        help="Maximum concurrent downloads (1-4).",
    )
    parser.add_argument(
        "--attempts",
        type=int,
        default=4,
        help="Maximum download attempts per source.",
    )


def add_urls_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments for downloading approved URLs from a CSV inventory."""

    parser.add_argument(
        "--csv",
        type=Path,
        default=ROOT / "data" / "sources.csv",
        help="Path to the source inventory CSV.",
    )
    add_download_arguments(parser)
    parser.add_argument(
        "--source",
        type=str,
        help="Download only records matching this source name.",
    )


def add_repo_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments for collecting files from ComplianceAsCode."""

    parser.add_argument(
        "--ref",
        default="main",
        help="Git branch, tag, or commit to collect from (default: main).",
    )
    parser.add_argument(
        "--path",
        action="append",
        required=True,
        help="Repository path prefix to collect. Repeat to add more paths.",
    )
    parser.add_argument(
        "--ext",
        action="append",
        help=(
            "File extension to collect, such as .yml. "
            "Repeat to add more extensions. Defaults to the supported set."
        ),
    )
    add_download_arguments(parser)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments and preserve the legacy command syntax."""

    arguments = list(sys.argv[1:] if argv is None else argv)

    commands = {"urls", "repo", "sitemap", "manual"}

    if not arguments or (arguments[0] not in commands and arguments[0] not in {"-h", "--help"}):
        arguments.insert(0, "urls")

    parser = argparse.ArgumentParser(description="HardenHelp compliant security-source ingestion.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    urls_parser = subparsers.add_parser(
        "urls",
        help="Download approved URLs listed in a CSV inventory.",
        description="Download approved URLs from data/sources.csv.",
    )
    add_urls_arguments(urls_parser)

    repo_parser = subparsers.add_parser(
        "repo",
        help="Collect approved files from ComplianceAsCode/content.",
        description=(
            "Discover commit-pinned files from the approved "
            "ComplianceAsCode repository and download them."
        ),
    )
    add_repo_arguments(repo_parser)

    subparsers.add_parser(
        "sitemap",
        help="Discover URLs from a sitemap (not implemented yet).",
    )
    subparsers.add_parser(
        "manual",
        help="Register manually downloaded files (not implemented yet).",
    )

    args = parser.parse_args(arguments)

    if args.command in {"sitemap", "manual"}:
        parser.error(f"The '{args.command}' command is not implemented yet. Use 'urls' or 'repo'.")

    if args.delay < 0:
        parser.error("--delay cannot be negative.")

    if args.attempts < 1:
        parser.error("--attempts must be at least 1.")

    if (
        args.command == "repo"
        and args.ext
        and any(
            not extension.startswith(".") or extension != extension.casefold()
            for extension in args.ext
        )
    ):
        parser.error("Each --ext value must start with a dot and be lowercase.")

    return args


def report_result(result: dict) -> None:
    """Print the result of one download."""

    print(f"{result['status'].upper()}: {result['url']}")

    if result.get("error"):
        print(f"  Reason: {result['error']}")


def print_summary(summary: dict[str, int]) -> None:
    """Print download summary counts."""

    print("\nDownload summary:")

    for status, count in summary.items():
        print(f"{status.capitalize()}: {count}")


def run_urls(args: argparse.Namespace) -> None:
    """Download approved CSV sources and print a summary."""

    from hardenhelp.ingest.fetch import fetch_all, read_sources

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

    try:
        summary = asyncio.run(
            fetch_all(
                sources=sources,
                root=ROOT,
                max_concurrency=args.concurrency,
                per_host_delay=args.delay,
                max_attempts=args.attempts,
                on_result=report_result,
            )
        )
    except (ValueError, OSError) as error:
        raise SystemExit(str(error)) from error

    print_summary(summary)


def run_repo(args: argparse.Namespace) -> None:
    """Discover and download approved ComplianceAsCode repository files."""

    from hardenhelp.ingest.fetch import fetch_all
    from hardenhelp.ingest.repo import discover_repository_sources

    try:
        commit_sha, sources = discover_repository_sources(
            ref=args.ref,
            path_prefixes=args.path,
            extensions=set(args.ext) if args.ext else None,
        )
    except (ValueError, OSError, httpx.HTTPError) as error:
        raise SystemExit(f"Repository discovery failed: {error}") from error

    print("Repository: ComplianceAsCode/content")
    print(f"Resolved commit: {commit_sha}")
    print(f"Discovered files: {len(sources)}")

    if not sources:
        print("No matching files found. Nothing to download.")
        return

    print("Starting downloads...")

    try:
        summary = asyncio.run(
            fetch_all(
                sources=sources,
                root=ROOT,
                max_concurrency=args.concurrency,
                per_host_delay=args.delay,
                max_attempts=args.attempts,
                on_result=report_result,
            )
        )
    except (ValueError, OSError) as error:
        raise SystemExit(f"Repository download failed: {error}") from error

    print_summary(summary)


def main() -> None:
    """Run the selected ingestion command."""

    args = parse_args()

    if args.command == "urls":
        run_urls(args)
    elif args.command == "repo":
        run_repo(args)


if __name__ == "__main__":
    main()
