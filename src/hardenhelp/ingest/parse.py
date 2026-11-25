"""Turn one raw file into clean pages.

No database here: a file goes in, and either a ParsedDoc comes out or a ParseError
with a reason. Every page keeps its page number and the section path it starts in,
because answers will cite "document, page, section".
"""

import re
import unicodedata
from collections import Counter
from contextlib import suppress
from dataclasses import dataclass, field
from pathlib import Path

import pymupdf
import trafilatura
import yaml
from pypdf import PdfReader
from yaml.nodes import MappingNode, ScalarNode, SequenceNode

TEXT_TYPES = {".md", ".mdx", ".markdown", ".txt", ".rst", ".adoc", ".sgml", ".py", ".var"}
DATA_TYPES = {".json", ".yaml", ".yml", ".csv", ".xml"}
PAGE_CHARS = 3000
MIN_CHARS_PER_PAGE = 50


@dataclass
class ParsedPage:
    page_no: int
    text: str
    headings: list[str] = field(default_factory=list)
    tables: int = 0


@dataclass
class ParsedDoc:
    parser: str
    kind: str
    title: str
    pages: list[ParsedPage]
    scanned_pages: list[int] = field(default_factory=list)


class ParseError(Exception):
    """A file we could not parse, with a short machine-readable reason."""

    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(f"{reason}: {detail}" if detail else reason)
        self.reason = reason
        self.detail = detail[:500]


# ---------- cleaning ----------
def clean_text(text: str) -> str:
    """The same small repairs for every parser."""

    # Repair common UTF-8 text incorrectly decoded as Latin-1.
    if "ï¼" in text or "Ã" in text:
        with suppress(UnicodeEncodeError, UnicodeDecodeError):
            text = text.encode("latin-1").decode("utf-8")

    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\x00", "").replace("Ã‚", "")
    text = re.sub(r"(?<=[a-z])-\n(?=[a-z])", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" ?\n ?", "\n", text)

    return re.sub(r"\n{3,}", "\n\n", text).strip()


def drop_repeated_lines(pages: list[str]) -> list[str]:
    """Remove headers and footers: lines that open or close most pages."""
    if len(pages) < 4:
        return pages

    def key(line: str) -> str:
        return re.sub(r"\d+", "#", line.strip().lower())

    seen: Counter[str] = Counter()

    for page in pages:
        lines = [ln for ln in page.splitlines() if ln.strip()]
        seen.update({key(ln) for ln in lines[:2] + lines[-2:] if not ln.startswith("#")})

    repeated = {k for k, count in seen.items() if count >= 0.6 * len(pages)}
    cleaned = []

    for page in pages:
        lines = page.splitlines()
        edge = {i for i, ln in enumerate(lines) if ln.strip()}
        edge = set(sorted(edge)[:2] + sorted(edge)[-2:])
        cleaned.append(
            "\n".join(ln for i, ln in enumerate(lines) if not (i in edge and key(ln) in repeated))
        )

    return cleaned


HEADING = re.compile(r"^(#{1,6}) +(.+?)\s*$")


def heading_title(raw: str) -> str:
    """Remove heading anchors."""
    return re.sub(r"\s*\{\s*[#.][^}]*\}\s*$", "", raw).strip()


FENCE = re.compile(r"^\s*(```|~~~)")


def headings_in(text: str, in_code: bool = False) -> tuple[list[tuple[int, str]], bool]:
    """Find headings, ignoring headings inside code blocks."""
    found = []

    for line in text.splitlines():
        if FENCE.match(line):
            in_code = not in_code
        elif not in_code and (match := HEADING.match(line)):
            found.append((len(match.group(1)), heading_title(match.group(2))))

    return found, in_code


def with_heading_paths(texts: list[str]) -> list[ParsedPage]:
    """Number pages and remember the section each page starts in."""
    pages, path, in_code = [], [], False

    for number, text in enumerate(texts, start=1):
        pages.append(
            ParsedPage(
                number,
                text,
                headings=list(path),
                tables=text.count("\n|---"),
            )
        )

        found, in_code = headings_in(text, in_code)

        for level, title in found:
            path = path[: level - 1] + [title]

    return pages


# ---------- YAML control headings ----------
def yaml_control_pages(text: str) -> tuple[str, list[ParsedPage]] | None:
    """Split STIG YAML controls into pages with their control titles."""
    try:
        root = yaml.compose(text)
    except yaml.YAMLError:
        return None

    if not isinstance(root, MappingNode):
        return None

    values = {key.value: value for key, value in root.value if isinstance(key, ScalarNode)}

    title_node = values.get("title")
    controls_node = values.get("controls")

    if not isinstance(controls_node, SequenceNode):
        return None

    document_title = title_node.value if isinstance(title_node, ScalarNode) else ""

    sections = []

    for control in controls_node.value:
        if not isinstance(control, MappingNode):
            continue

        control_values = {
            key.value: value for key, value in control.value if isinstance(key, ScalarNode)
        }

        control_title = control_values.get("title")

        if isinstance(control_title, ScalarNode):
            sections.append(
                (
                    control.start_mark.index,
                    control.end_mark.index,
                    control_title.value,
                )
            )

    if not sections:
        return None

    pages = []
    page_no = 1

    def add_pages(section_text: str, heading: str | None) -> None:
        nonlocal page_no

        for page_text in split_pages(section_text):
            cleaned = clean_text(page_text)

            if cleaned:
                pages.append(
                    ParsedPage(
                        page_no=page_no,
                        text=cleaned,
                        headings=[heading] if heading else [],
                        tables=0,
                    )
                )
                page_no += 1

    # Preserve the document metadata before the first control.
    add_pages(text[: sections[0][0]], None)

    # Give every control page its corresponding control title.
    for start, end, heading in sections:
        add_pages(text[start:end], heading)

    if not pages:
        return None

    return document_title, pages


def finish(
    parser: str,
    kind: str,
    title: str,
    texts: list[str],
    scanned_pages: list[int] | None = None,
) -> ParsedDoc:
    texts = drop_repeated_lines([clean_text(t) for t in texts])
    texts = [clean_text(t) for t in texts]

    if not any(texts):
        raise ParseError("empty", "no text after cleaning")

    found, _ = headings_in("\n".join(texts))

    final_title = title or (found[0][1] if found else "")

    return ParsedDoc(
        parser=parser,
        kind=kind,
        title=final_title,
        pages=with_heading_paths(texts),
        scanned_pages=scanned_pages or [],
    )


# ---------- PDF, parser 1: PyMuPDF ----------
def _body_size(doc: pymupdf.Document) -> float:
    """Find the most common font size, counted by characters."""
    sizes: Counter[float] = Counter()

    for page in list(doc)[:30]:
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    sizes[round(span["size"], 1)] += len(span["text"])

    return sizes.most_common(1)[0][0] if sizes else 10.0


def _heading_level(text: str, size: float, bold: bool, body: float) -> int:
    if not 2 < len(text) <= 120 or not any(ch.isalpha() for ch in text):
        return 0

    if size >= body * 1.6:
        return 1
    if size >= body * 1.3:
        return 2
    if size >= body * 1.12 or (bold and len(text) <= 80 and not text.endswith((".", ",", ";"))):
        return 3

    return 0


def _open_pdf(path: Path) -> pymupdf.Document:
    try:
        doc = pymupdf.open(path)
    except Exception as exc:
        raise ParseError("corrupt", str(exc)) from exc

    if doc.needs_pass:
        raise ParseError("encrypted", "the PDF needs a password")

    if doc.page_count == 0:
        raise ParseError("empty", "the PDF has no pages")

    return doc


def parse_pdf_pymupdf(path: Path) -> ParsedDoc:
    """Extract PDF text and identify image-based scanned pages."""
    doc = _open_pdf(path)
    body = _body_size(doc)

    texts = []
    scanned_pages = []
    page_numbers_with_text = []

    for page_no, page in enumerate(doc, start=1):
        tables = list(page.find_tables().tables) if len(page.get_cdrawings()) >= 4 else []

        used: set[int] = set()
        out: list[str] = []

        for block in page.get_text("dict")["blocks"]:
            if block["type"] != 0:
                continue

            rect = pymupdf.Rect(block["bbox"])
            inside = next(
                (i for i, table in enumerate(tables) if rect.intersects(table.bbox)),
                None,
            )

            if inside is not None:
                if inside not in used:
                    used.add(inside)
                    out.append("\n" + tables[inside].to_markdown().strip() + "\n")
                continue

            for line in block["lines"]:
                text = "".join(span["text"] for span in line["spans"]).strip()

                if not text:
                    continue

                size = max(span["size"] for span in line["spans"])
                bold = all(span["flags"] & 16 for span in line["spans"])
                level = _heading_level(text, size, bold, body)

                out.append(f"{'#' * level} {text}" if level else text)

        page_text = "\n".join(out)
        page_chars = len(clean_text(page_text))

        texts.append(page_text)

        if page_chars >= MIN_CHARS_PER_PAGE:
            page_numbers_with_text.append(page_no)
        elif page.get_images(full=True):
            scanned_pages.append(page_no)

    # Fully image-based PDFs still need OCR.
    if not page_numbers_with_text and scanned_pages:
        raise ParseError(
            "no_text_layer",
            f"No usable text layer found; scanned pages: {scanned_pages}",
        )

    return finish(
        "pymupdf",
        "pdf",
        (doc.metadata or {}).get("title") or "",
        texts,
        scanned_pages=scanned_pages,
    )


def parse_pdf_ocr(path: Path, language: str = "eng") -> ParsedDoc:
    """For scans: read pixels with Tesseract, which must be installed."""
    doc = _open_pdf(path)

    try:
        texts = [
            page.get_text(
                textpage=page.get_textpage_ocr(
                    language=language,
                    dpi=200,
                    full=True,
                )
            )
            for page in doc
        ]
    except Exception as exc:
        raise ParseError("ocr_unavailable", str(exc)) from exc

    return finish(f"ocr-{language}", "pdf", "", texts)


# ---------- PDF, parser 2: pypdf ----------
def parse_pdf_pypdf(path: Path) -> ParsedDoc:
    try:
        reader = PdfReader(path)

        if reader.is_encrypted and not reader.decrypt(""):
            raise ParseError("encrypted", "the PDF needs a password")

        texts = [page.extract_text() or "" for page in reader.pages]

    except ParseError:
        raise
    except Exception as exc:
        raise ParseError("corrupt", str(exc)) from exc

    if not texts:
        raise ParseError("empty", "the PDF has no pages")

    if sum(len(t) for t in texts) < MIN_CHARS_PER_PAGE * len(texts):
        raise ParseError(
            "no_text_layer",
            f"almost no text on {len(texts)} pages: needs OCR",
        )

    return finish("pypdf", "pdf", "", texts)


# ---------- HTML ----------
def parse_html(path: Path) -> ParsedDoc:
    html = path.read_text(encoding="utf-8", errors="replace")

    markdown = trafilatura.extract(
        html,
        output_format="markdown",
        include_tables=True,
    )

    if not markdown or len(markdown) < 40:
        raise ParseError(
            "empty",
            "no main content found (a page built by JavaScript?)",
        )

    meta = trafilatura.extract_metadata(html)

    return finish(
        "trafilatura",
        "html",
        (meta.title if meta else "") or "",
        split_pages(markdown),
    )


# ---------- text files ----------
RST_MARKS = {"=": 1, "-": 2, "~": 3, "^": 3, '"': 3}


def markup_to_markdown(text: str, suffix: str) -> str:
    """Rewrite reStructuredText and AsciiDoc headings as Markdown headings."""
    lines = text.splitlines()

    if suffix == ".adoc":
        return "\n".join(
            re.sub(
                r"^(=+) ",
                lambda match: "#" * len(match.group(1)) + " ",
                line,
            )
            for line in lines
        )

    if suffix not in {".rst", ".txt"}:
        return text

    out: list[str] = []

    for i, line in enumerate(lines):
        under = lines[i + 1] if i + 1 < len(lines) else ""
        is_rule = len(under) >= 3 and len(set(under)) == 1 and under[0] in RST_MARKS

        if line.strip() and is_rule and len(under) >= len(line.rstrip()):
            out.append("#" * RST_MARKS[under[0]] + " " + line.strip())
        elif not (out and len(line) >= 3 and len(set(line)) == 1 and line[0] in RST_MARKS):
            out.append(line)

    return "\n".join(out)


def split_pages(text: str, size: int = PAGE_CHARS) -> list[str]:
    """Cut on blank lines into pieces of about size characters."""
    pages, current, length = [], [], 0

    for para in re.split(r"\n\s*\n", text):
        if current and length + len(para) > size:
            pages.append("\n\n".join(current))
            current, length = [], 0

        current.append(para)
        length += len(para)

    if current:
        pages.append("\n\n".join(current))

    return pages


def parse_text(path: Path) -> ParsedDoc:
    suffix = path.suffix.lower()
    text = path.read_text(encoding="utf-8", errors="replace")

    if suffix in {".yaml", ".yml"}:
        result = yaml_control_pages(text)

        if result is not None:
            title, pages = result
            return ParsedDoc(
                "plain",
                "data",
                title or path.stem,
                pages,
            )

        # Extract the top-level title without parsing Jinja templates.
        match = re.search(
            r"(?m)^title:\s*['\"]?(.+?)['\"]?\s*$",
            text,
        )
        yaml_title = match.group(1).strip() if match else path.stem

        return finish(
            "plain",
            "data",
            yaml_title,
            split_pages(text),
        )

    if suffix in DATA_TYPES:
        return finish(
            "plain",
            "data",
            path.stem,
            split_pages(text),
        )

    return finish(
        "plain",
        "text",
        "",
        split_pages(markup_to_markdown(text, suffix)),
    )


# ---------- parser registry ----------
PDF_PARSERS = {
    "pymupdf": parse_pdf_pymupdf,
    "pypdf": parse_pdf_pypdf,
}


def parse_file(path: Path, pdf_parser: str = "pymupdf") -> ParsedDoc:
    """Pick parser by file type. Raises ParseError, never anything else."""
    suffix = path.suffix.lower()

    try:
        if suffix == ".pdf":
            return PDF_PARSERS[pdf_parser](path)

        if suffix in {".html", ".htm"}:
            return parse_html(path)

        if suffix in TEXT_TYPES | DATA_TYPES:
            return parse_text(path)

    except ParseError:
        raise
    except Exception as exc:
        raise ParseError(
            "crash",
            f"{type(exc).__name__}: {exc}",
        ) from exc

    raise ParseError("unsupported_type", suffix or "no file extension")
