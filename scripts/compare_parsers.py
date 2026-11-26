"""Compare document parsers across downloaded files."""

import argparse
import json
import re
from pathlib import Path

import pymupdf
import trafilatura
from pypdf import PdfReader

from hardenhelp.ingest.parse import ParseError, parse_file

MANIFEST = Path("data/raw/manifest.jsonl")
NOTES = Path("NOTES.md")

OTHER_EXTENSIONS = {".md", ".markdown", ".rst", ".yaml", ".yml", ".txt", ".var"}


def load_manifest() -> list[dict]:
    """Load successfully downloaded files."""
    if not MANIFEST.exists():
        return []

    records = []

    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if line.strip():
            record = json.loads(line)

            if record.get("status") == "downloaded":
                path = Path(record["path"])
                if path.is_file():
                    records.append(record)

    return records


def compare_hardenhelp(path: Path) -> str:
    """Run the existing HardenHelp parser."""
    try:
        parsed = parse_file(path)
        pages = len(parsed.pages)
        characters = sum(len(page.text) for page in parsed.pages)
        preview = " ".join(page.text.strip() for page in parsed.pages)[:150]

        return f"SUCCESS: {pages} pages, {characters:,} chars; preview: {preview!r}"
    except ParseError as exc:
        return f"FAILED: {exc.reason}"
    except Exception as exc:
        return f"FAILED: {type(exc).__name__}"


def compare_pdf(path: Path) -> tuple[str, str]:
    """Compare PyMuPDF and pypdf on a PDF."""
    try:
        with pymupdf.open(path) as document:
            page_count = len(document)
            characters = sum(len(page.get_text()) for page in document)

        pymupdf_result = f"SUCCESS: {page_count} pages, {characters:,} chars"
    except Exception as exc:
        pymupdf_result = f"FAILED: {type(exc).__name__}"

    try:
        reader = PdfReader(str(path))
        page_count = len(reader.pages)
        characters = sum(len(page.extract_text() or "") for page in reader.pages)
        pypdf_result = f"SUCCESS: {page_count} pages, {characters:,} chars"
    except Exception as exc:
        pypdf_result = f"FAILED: {type(exc).__name__}"

    return pymupdf_result, pypdf_result


def compare_html(path: Path) -> tuple[str, str]:
    """Compare Trafilatura with basic HTML tag stripping."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        extracted = trafilatura.extract(content) or ""
        trafilatura_result = f"SUCCESS: {len(extracted):,} chars"
    except Exception as exc:
        trafilatura_result = f"FAILED: {type(exc).__name__}"

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        stripped = re.sub(r"<[^>]+>", " ", content)
        stripped = re.sub(r"\s+", " ", stripped).strip()
        plain_result = f"SUCCESS: {len(stripped):,} chars"
    except Exception as exc:
        plain_result = f"FAILED: {type(exc).__name__}"

    return trafilatura_result, plain_result


def select_files(records: list[dict], explicit: list[str]) -> list[Path]:
    """Select explicit paths or the largest relevant downloaded files."""
    if explicit:
        return [Path(item) for item in explicit]

    candidates = [
        Path(record["path"])
        for record in records
        if Path(record["path"]).suffix.lower() in {".pdf", ".html", ".htm"}
    ]

    if not candidates:
        candidates = [
            Path(record["path"])
            for record in records
            if Path(record["path"]).suffix.lower() in OTHER_EXTENSIONS
        ]

    return sorted(
        candidates,
        key=lambda path: path.stat().st_size,
        reverse=True,
    )[:10]


def append_notes(lines: list[str]) -> None:
    """Append comparison results without replacing existing notes."""
    if not lines:
        print("No comparison results to append to NOTES.md.")
        return

    with NOTES.open("a", encoding="utf-8") as file:
        file.write("\n\n## Day 7 Parser Comparison\n\n")
        file.write("\n".join(lines))
        file.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare HardenHelp document parsers.")
    parser.add_argument("paths", nargs="*", help="Optional file paths.")
    args = parser.parse_args()

    records = load_manifest()
    paths = select_files(records, args.paths)

    print(f"Files selected for comparison: {len(paths)}")
    print()

    table = [
        "| File | HardenHelp parser | Comparison parser |",
        "|---|---|---|",
    ]

    compared = 0

    for path in paths:
        if not path.is_file():
            print(f"SKIPPED: {path} (file not found)")
            continue

        suffix = path.suffix.lower()
        hardenhelp_result = compare_hardenhelp(path)

        if suffix == ".pdf":
            first, second = compare_pdf(path)
            comparison = f"PyMuPDF: {first}; pypdf: {second}"

        elif suffix in {".html", ".htm"}:
            first, second = compare_html(path)
            comparison = f"Trafilatura: {first}; tag stripping: {second}"

        else:
            comparison = "Single parser; manual output inspection"

        table.append(f"| {path.name} | {hardenhelp_result} | {comparison} |")
        compared += 1

    if compared:
        print("\n".join(table))
        append_notes(table)
    else:
        print("No supported files were available for comparison.")

    print()
    print(f"compared {compared} files -> table written to NOTES.md")


if __name__ == "__main__":
    main()
