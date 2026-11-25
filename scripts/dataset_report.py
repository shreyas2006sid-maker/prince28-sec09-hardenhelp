"""Generate DATASET.md and docs/CAPACITY.md from the current corpus."""

import argparse
import csv
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from hardenhelp.ingest.parse import ParseError, parse_file

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "data" / "raw" / "manifest.jsonl"
SOURCES_FILE = ROOT / "data" / "sources.csv"


def load_manifest(path: Path) -> list[dict]:
    """Load all manifest records."""
    if not path.is_file():
        raise FileNotFoundError(f"Manifest not found: {path}")

    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def load_sources() -> list[dict]:
    """Load the source inventory."""
    if not SOURCES_FILE.is_file():
        raise FileNotFoundError(f"Source inventory not found: {SOURCES_FILE}")

    lines = SOURCES_FILE.read_text(encoding="utf-8-sig").splitlines()
    csv_lines = [line for line in lines if line.strip() and not line.lstrip().startswith("#")]
    return list(csv.DictReader(csv_lines))


def resolve_file(record: dict, manifest: Path) -> Path:
    """Resolve a manifest path, with a fallback to the raw folder."""
    recorded = record.get("path")
    if recorded:
        path = Path(recorded)
        if path.is_file():
            return path

        fallback = manifest.parent / path.name
        if fallback.is_file():
            return fallback

    raise FileNotFoundError(f"Downloaded file not found: {record.get('path', '(no path)')}")


def measure_corpus(records: list[dict], manifest: Path) -> dict:
    """Measure downloaded files and parse them using HardenHelp."""
    downloaded = [record for record in records if record.get("status") == "downloaded"]

    result = {
        "downloaded": len(downloaded),
        "parsed": 0,
        "failed": 0,
        "missing": 0,
        "pages": 0,
        "heading_entries": 0,
        "tables": 0,
        "characters": 0,
        "text_bytes": 0,
        "raw_bytes": 0,
        "files": [],
        "errors": [],
    }

    for record in downloaded:
        try:
            path = resolve_file(record, manifest)
            result["raw_bytes"] += path.stat().st_size
            parsed = parse_file(path)

            page_count = len(parsed.pages)
            heading_entries = sum(len(page.headings) for page in parsed.pages)
            table_count = sum(page.tables for page in parsed.pages)
            characters = sum(len(page.text) for page in parsed.pages)
            text_bytes = sum(len(page.text.encode("utf-8")) for page in parsed.pages)

            result["parsed"] += 1
            result["pages"] += page_count
            result["heading_entries"] += heading_entries
            result["tables"] += table_count
            result["characters"] += characters
            result["text_bytes"] += text_bytes
            result["files"].append(
                {
                    "title": record.get("title") or path.name,
                    "name": path.name,
                    "source": record.get("source") or "Unknown",
                    "pages": page_count,
                    "characters": characters,
                    "bytes": path.stat().st_size,
                    "parser": parsed.parser,
                    "kind": parsed.kind,
                }
            )

        except FileNotFoundError as exc:
            result["missing"] += 1
            result["errors"].append(str(exc))
        except (ParseError, OSError) as exc:
            result["failed"] += 1
            result["errors"].append(f"{record.get('title', 'Unknown')}: {exc}")

    return result


def format_bytes(value: int) -> str:
    return f"{value / (1024 * 1024):.4f} MiB"


def percentage(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "N/A"
    return f"{numerator / denominator * 100:.2f}%"


def build_dataset_report(
    sources: list[dict], records: list[dict], metrics: dict, generated: str
) -> str:
    source_counts = Counter(row.get("source") or "Unknown" for row in sources)
    status_counts = Counter(record.get("status", "unknown") for record in records)

    lines = [
        "# HardenHelp Dataset Documentation",
        "",
        "## 1. Dataset Overview",
        "",
        "HardenHelp uses security configuration information related to Ubuntu 22.04 LTS "
        "and its security hardening requirements.",
        "",
        "The target is Ubuntu 22.04 LTS STIG requirements and matching ComplianceAsCode rules.",
        "",
        "## 2. Source Inventory",
        "",
        f"The source inventory contains **{len(sources)} records** in `data/sources.csv`.",
        "",
        "| Source | Inventory records |",
        "|---|---:|",
    ]

    for source, count in sorted(source_counts.items()):
        lines.append(f"| {source} | {count} |")

    lines.extend(
        [
            f"| **Total** | **{len(sources)}** |",
            "",
            "The inventory lists candidate resources. It does not mean every resource "
            "has been downloaded or approved for redistribution.",
            "",
            "## 3. Actual Collection Status",
            "",
            f"Report generated: {generated}",
            "",
            f"- Manifest records: {len(records)}",
            f"- Successfully downloaded files: {metrics['downloaded']}",
            f"- Files parsed successfully by the local parser: {metrics['parsed']}",
            f"- Local parsing failures: {metrics['failed']}",
            f"- Missing downloaded files: {metrics['missing']}",
            "",
            "Manifest status counts:",
            "",
            "| Status | Records |",
            "|---|---:|",
        ]
    )

    for status, count in sorted(status_counts.items()):
        lines.append(f"| {status} | {count} |")

    lines.extend(
        [
            "",
            "## 4. Local Parser Measurements",
            "",
            "| Metric | Measured value |",
            "|---|---:|",
            f"| Downloaded source files | {metrics['downloaded']} |",
            f"| Successfully parsed files | {metrics['parsed']} |",
            f"| Local parsing failures | {metrics['failed']} |",
            f"| Parser-generated pages | {metrics['pages']} |",
            f"| Heading path entries across pages | {metrics['heading_entries']} |",
            f"| Extracted Markdown tables | {metrics['tables']} |",
            f"| Extracted characters | {metrics['characters']:,} |",
            f"| Raw source size | {metrics['raw_bytes']:,} bytes |",
            f"| Raw source size | {format_bytes(metrics['raw_bytes'])} |",
            f"| Extracted UTF-8 text size | {metrics['text_bytes']:,} bytes |",
            f"| Estimated tokens (characters / 4) | {metrics['characters'] // 4:,} |",
            "",
            "These are local parser measurements. They do not prove that pages are stored "
            "in PostgreSQL. Use `scripts/parsing_coverage.py` for database storage coverage.",
            "",
            "The token count is a rough estimate, not a model tokenizer measurement. "
            "Heading path entries count the heading paths attached to pages, so the same "
            "heading can be counted on multiple pages.",
            "",
            "## 5. Downloaded File Details",
            "",
            "| File | Source | Parser | Pages | Characters | Raw bytes |",
            "|---|---|---|---:|---:|---:|",
        ]
    )

    for item in metrics["files"]:
        lines.append(
            f"| {item['name']} | {item['source']} | {item['parser']} | "
            f"{item['pages']} | {item['characters']:,} | {item['bytes']:,} |"
        )

    lines.extend(
        [
            "",
            "## 6. Licensing and Usage Restrictions",
            "",
            "- ComplianceAsCode entries are labelled BSD-3-Clause in the inventory. "
            "Retain applicable notices and check the repository licence.",
            "- DISA and NIST entries require checking the applicable source and document notices.",
            "- Ubuntu and OpenSCAP reference entries remain reference-only until their "
            "specific redistribution permissions are confirmed.",
            "- Public accessibility does not automatically grant permission "
            "to redistribute content.",
            "- The inventory licence field is recorded metadata, not a legal determination.",
            "",
            "## 7. Data Collection Safeguards",
            "",
            "The downloader is designed to use source approval checks, robots.txt checks, "
            "a descriptive User-Agent, request delays, limited concurrency, retries, "
            "resumable downloads, response validation and a download manifest.",
            "",
            "## 8. Known Gaps",
            "",
            "- The source inventory is larger than the currently downloaded corpus.",
            "- Not every source has verified redistribution permission.",
            "- The local parser measurements do not establish PostgreSQL storage coverage.",
            "- Token counts are estimates and should be replaced with tokenizer measurements "
            "when an embedding model is selected.",
            "- The full target corpus has not yet been collected.",
            "- OCR and scanned-document coverage require separate verification.",
            "",
            "## 9. References",
            "",
            "- DISA STIG: https://www.stigviewer.com/",
            "- NIST NCP: https://ncp.nist.gov/",
            "- ComplianceAsCode: https://github.com/ComplianceAsCode/content",
            "- Ubuntu: https://ubuntu.com/",
            "- OpenSCAP: https://www.open-scap.org/",
            "",
            "---",
            "",
            "**Project:** HardenHelp",
            "",
            "**Target platform:** Ubuntu 22.04 LTS",
            "",
            "**Inventory:** `data/sources.csv`",
            "",
        ]
    )

    return "\n".join(lines)


def build_capacity_report(metrics: dict, full_files: int, generated: str) -> str:
    downloaded = metrics["downloaded"]
    estimated_tokens = metrics["characters"] // 4
    average_tokens = estimated_tokens / downloaded if downloaded else 0
    projected_tokens = round(average_tokens * full_files)
    chunks_at_500 = (projected_tokens + 499) // 500 if projected_tokens else 0
    ten_x_tokens = estimated_tokens * 10
    ten_x_chunks = (ten_x_tokens + 499) // 500 if ten_x_tokens else 0

    return "\n".join(
        [
            "# Capacity and Scalability",
            "",
            "## 1. Purpose",
            "",
            "This report estimates corpus capacity using the current downloaded files. "
            "It distinguishes measured local data from projections.",
            "",
            f"Report generated: {generated}",
            "",
            "## 2. Measured Current Corpus",
            "",
            "| Metric | Measured value |",
            "|---|---:|",
            f"| Downloaded source files | {downloaded} |",
            f"| Successfully parsed files | {metrics['parsed']} |",
            f"| Parser-generated pages | {metrics['pages']} |",
            f"| Heading path entries | {metrics['heading_entries']} |",
            f"| Extracted tables | {metrics['tables']} |",
            f"| Extracted characters | {metrics['characters']:,} |",
            f"| Raw source size | {metrics['raw_bytes']:,} bytes |",
            f"| Extracted UTF-8 text size | {metrics['text_bytes']:,} bytes |",
            f"| Estimated tokens | {estimated_tokens:,} |",
            "",
            "Token estimate = extracted characters / 4. This is a planning estimate, "
            "not an exact tokenizer result.",
            "",
            "## 3. Full Target Projection",
            "",
            f"The requested planning target is **{full_files:,} files/rules**. "
            "This is a projection, not a claim that the target has been collected.",
            "",
            f"- Average estimated tokens per downloaded file: {average_tokens:,.1f}",
            f"- Projected tokens at the full target: {projected_tokens:,}",
            f"- Approximate 500-token chunks at the full target: {chunks_at_500:,}",
            "",
            "The projection assumes the average size of the current corpus remains "
            "representative. The actual full corpus may be substantially different.",
            "",
            "## 4. Embedding Cost",
            "",
            "No embedding provider or model is configured, so an actual embedding cost "
            "cannot currently be calculated.",
            "",
            f"- Current estimated input: {estimated_tokens:,} tokens.",
            f"- Full-target estimated input: {projected_tokens:,} tokens.",
            "- Cost formula: (input tokens / 1,000,000) × provider price per million tokens.",
            "- Convert the provider's price to INR using the applicable exchange rate "
            "when estimating rupee cost.",
            "",
            "**Question: Is embedding cost a problem?** It cannot be determined until "
            "a provider and model price are selected. The full-target token estimate "
            "above is the input needed for that calculation.",
            "",
            "## 5. PostgreSQL Storage",
            "",
            f"The extracted text alone occupies {metrics['text_bytes']:,} UTF-8 bytes "
            "locally. This is not a measurement of PostgreSQL storage.",
            "",
            "Database storage also includes row, index, JSONB, and database overhead. "
            "Vector storage cannot be estimated reliably until the embedding dimensions "
            "and storage format are selected.",
            "",
            "**Question: Do vectors and text fit in free PostgreSQL?** Check the actual "
            "database provider dashboard for its current storage limit and current usage. "
            "Compare those values with a database-side measurement after loading the "
            "full corpus. Do not treat local text bytes as total database size.",
            "",
            "## 6. Least Certain Estimate",
            "",
            "The least certain number is the full-target token projection because it "
            "assumes the current files represent all future rules and documents.",
            "",
            "A better measurement is to collect a representative sample across all "
            "target operating systems and file types, count tokens using the selected "
            "embedding model's tokenizer, and then project by source category.",
            "",
            "## 7. What Changes at 10x Corpus Size?",
            "",
            f"- At 10x the current corpus, the rough estimate is {ten_x_tokens:,} tokens "
            f"and {ten_x_chunks:,} chunks of 500 tokens each.",
            "- Re-measure database storage, indexing, ingestion time, query latency, "
            "and embedding cost; do not assume they scale linearly.",
            "",
            "## 8. Current Limitations",
            "",
            "- No embedding provider or model is configured.",
            "- Token count is estimated rather than measured with a model tokenizer.",
            "- PostgreSQL storage usage and provider quota have not been measured here.",
            "- Vector dimensions and vector storage overhead are not yet known.",
            "- The full target corpus has not been collected.",
            "- Production load and query performance have not been benchmarked.",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate DATASET.md and docs/CAPACITY.md from the corpus."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Path to the JSONL download manifest.",
    )
    parser.add_argument(
        "--full-files",
        type=int,
        default=4000,
        help="Full target corpus size used for capacity projections.",
    )
    args = parser.parse_args()

    if args.full_files < 1:
        parser.error("--full-files must be at least 1")

    manifest = args.manifest
    if not manifest.is_absolute():
        manifest = ROOT / manifest

    records = load_manifest(manifest)
    sources = load_sources()
    metrics = measure_corpus(records, manifest)
    generated = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")

    (ROOT / "DATASET.md").write_text(
        build_dataset_report(sources, records, metrics, generated),
        encoding="utf-8",
    )

    capacity_path = ROOT / "docs" / "CAPACITY.md"
    capacity_path.parent.mkdir(parents=True, exist_ok=True)
    capacity_path.write_text(
        build_capacity_report(metrics, args.full_files, generated),
        encoding="utf-8",
    )

    print("Dataset reports generated.")
    print(f"Manifest: {manifest}")
    print(f"Inventory records: {len(sources)}")
    print(f"Downloaded files: {metrics['downloaded']}")
    print(f"Locally parsed files: {metrics['parsed']}")
    print(f"Local parsing failures: {metrics['failed']}")
    print(f"Missing files: {metrics['missing']}")
    print(f"Parser-generated pages: {metrics['pages']}")
    print(f"Estimated tokens: {metrics['characters'] // 4:,}")
    print("Updated: DATASET.md")
    print("Updated: docs/CAPACITY.md")

    if metrics["errors"]:
        print("\nFiles needing attention:")
        for error in metrics["errors"]:
            print(f"- {error}")


if __name__ == "__main__":
    main()
