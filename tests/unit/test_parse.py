from pathlib import Path

import pymupdf
import pytest

from hardenhelp.ingest.parse import (
    ParseError,
    clean_text,
    drop_repeated_lines,
    headings_in,
    markup_to_markdown,
    parse_file,
    parse_text,
    split_pages,
    with_heading_paths,
)


def test_clean_text_removes_null_bytes():
    assert clean_text("Hello\x00World") == "HelloWorld"


def test_clean_text_normalizes_unicode():
    assert clean_text("ＡＢＣ") == "ABC"


def test_clean_text_joins_hyphenated_words():
    assert clean_text("cyber-\nsecurity") == "cybersecurity"


def test_drop_repeated_lines_keeps_short_documents():
    pages = ["Page one", "Page two"]
    assert drop_repeated_lines(pages) == pages


def test_drop_repeated_lines_removes_repeated_headers():
    pages = [
        "Report 2024\nFirst page content",
        "Report 2025\nSecond page content",
        "Report 2026\nThird page content",
        "Report 2027\nFourth page content",
    ]

    result = drop_repeated_lines(pages)

    assert all("Report" not in page for page in result)


def test_headings_in_finds_markdown_headings():
    found, _ = headings_in("# Introduction\n## Security")

    assert found == [(1, "Introduction"), (2, "Security")]


def test_parse_yaml_extracts_control_titles_as_headings(tmp_path: Path):
    path = tmp_path / "stig.yml"
    path.write_text(
        "title: Ubuntu STIG\n"
        "controls:\n"
        "  - id: UBTU-22-211000\n"
        "    title: Ubuntu must be vendor-supported.\n"
        "    levels:\n"
        "      - high\n"
        "  - id: UBTU-22-211015\n"
        "    title: Ubuntu must disable Ctrl-Alt-Delete.\n",
        encoding="utf-8",
    )

    result = parse_text(path)

    assert result.kind == "data"
    assert result.title == "Ubuntu STIG"

    control_headings = [page.headings[0] for page in result.pages if page.headings]

    assert control_headings == [
        "Ubuntu must be vendor-supported.",
        "Ubuntu must disable Ctrl-Alt-Delete.",
    ]


def test_headings_in_ignores_code_blocks():
    found, _ = headings_in("# Real heading\n```python\n# Not a heading\n```\n## Another heading")

    assert found == [(1, "Real heading"), (2, "Another heading")]


def test_with_heading_paths_tracks_sections():
    pages = with_heading_paths(
        [
            "# Main\nIntroduction",
            "More introduction",
            "## Details\nMore details",
        ]
    )

    assert pages[0].headings == []
    assert pages[1].headings == ["Main"]
    assert pages[2].headings == ["Main"]


def test_split_pages_splits_paragraphs():
    result = split_pages("First paragraph\n\nSecond paragraph")

    assert len(result) == 1
    assert "First paragraph" in result[0]
    assert "Second paragraph" in result[0]


def test_markup_to_markdown_converts_adoc_headings():
    result = markup_to_markdown("== Introduction", ".adoc")

    assert result == "## Introduction"


def test_markup_to_markdown_converts_rst_headings():
    result = markup_to_markdown("Introduction\n============", ".rst")

    assert result == "# Introduction"


def test_parse_text_reads_markdown(tmp_path: Path):
    path = tmp_path / "guide.md"
    path.write_text(
        "# Introduction\n\nSecurity documentation",
        encoding="utf-8",
    )

    result = parse_text(path)

    assert result.kind == "text"
    assert result.title == "Introduction"
    assert len(result.pages) == 1


def test_parse_text_reads_json(tmp_path: Path):
    path = tmp_path / "records.json"
    path.write_text('{"name": "Security"}', encoding="utf-8")

    result = parse_text(path)

    assert result.kind == "data"
    assert result.title == "records"


def test_parse_file_rejects_unsupported_types(tmp_path: Path):
    path = tmp_path / "archive.zip"
    path.write_bytes(b"sample")

    with pytest.raises(ParseError) as error:
        parse_file(path)

    assert error.value.reason == "unsupported_type"


def test_parse_file_rejects_empty_text(tmp_path: Path):
    path = tmp_path / "empty.txt"
    path.write_text("", encoding="utf-8")

    with pytest.raises(ParseError) as error:
        parse_file(path)

    assert error.value.reason == "empty"


@pytest.mark.parametrize("parser", ["pymupdf", "pypdf"])
def test_parse_file_reads_pdf(tmp_path: Path, parser: str):
    path = tmp_path / "guide.pdf"

    document = pymupdf.open()
    page = document.new_page()
    page.insert_text(
        (72, 72),
        "Security Guide\n"
        "This document contains enough text for the PDF parser "
        "to recognize a valid text layer and extract its content.",
    )
    document.save(path)
    document.close()

    result = parse_file(path, pdf_parser=parser)

    assert result.kind == "pdf"
    assert len(result.pages) == 1
    assert "Security Guide" in result.pages[0].text
