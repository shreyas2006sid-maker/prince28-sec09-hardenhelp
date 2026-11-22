"""Week 1 self-check for HardenHelp.

Checks project files, Git state, tests, CI/CD and live health.
Standard library only. This script does not modify the project.
"""

import json
import re
import subprocess
import sys
import tomllib
import urllib.request
from pathlib import Path

ROOT = Path.cwd()

OK = "  ok "
BAD = "  ✗  "
WARN = "  !  "

results: list[tuple[str, bool]] = []


def check(
    day: str,
    label: str,
    passed: bool,
    hint: str = "",
    warn_only: bool = False,
) -> None:
    mark = OK if passed else (WARN if warn_only else BAD)
    print(f"{mark}{label}" + ("" if passed or not hint else f"\n       → {hint}"))

    if not warn_only:
        results.append((day, passed))


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )


def exists(path: str) -> bool:
    return (ROOT / path).exists()


def main() -> int:
    live = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else None

    if not exists("pyproject.toml"):
        print("Run this from your project folder (where pyproject.toml is).")
        return 2

    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    pkg = pyproject["project"]["name"].replace("-", "_")

    readme = (ROOT / "README.md").read_text(encoding="utf-8") if exists("README.md") else ""

    notes = (ROOT / "NOTES.md").read_text(encoding="utf-8") if exists("NOTES.md") else ""

    tracked = run(["git", "ls-files"]).stdout.split()

    # D01
    print("\nD01 · Repo, card and quality gates")

    for f in [
        "README.md",
        "docs/QUESTIONS.md",
        "docs/REQUIREMENTS.md",
        ".pre-commit-config.yaml",
        ".env.example",
        "uv.lock",
    ]:
        check("D01", f, exists(f), f"Missing: {f}")

    q = (
        (ROOT / "docs/QUESTIONS.md").read_text(encoding="utf-8")
        if exists("docs/QUESTIONS.md")
        else ""
    )

    # Count numbered Markdown questions such as "1. Question?"
    rows = len(re.findall(r"^\s*\d+\.\s+", q, flags=re.M))

    check(
        "D01",
        f"docs/QUESTIONS.md has 10 questions ({rows} found)",
        rows >= 10,
        "Add real questions until there are 10.",
    )

    todo = q.count("TODO")

    check(
        "D01",
        "No TODO left in docs/QUESTIONS.md",
        todo == 0,
        f"{todo} TODOs remain.",
        warn_only=True,
    )

    check(
        "D01",
        ".env is NOT committed",
        ".env" not in tracked,
        "Remove .env from Git and rotate exposed passwords.",
    )

    check(
        "D01",
        "Pre-commit hooks installed",
        exists(".git/hooks/pre-commit"),
        "Run: uv run pre-commit install",
    )

    # D02
    print("\nD02 · FastAPI service")

    for f in [
        f"src/{pkg}/api/main.py",
        f"src/{pkg}/config.py",
        "data/sample_records.json",
    ]:
        check("D02", f, exists(f), "Missing required file.")

    try:
        n = len(json.loads((ROOT / "data/sample_records.json").read_text(encoding="utf-8")))
    except (OSError, ValueError):
        n = 0

    check(
        "D02",
        f"Sample records: {n} found (20 expected)",
        n >= 20,
        "Check data/sample_records.json.",
    )

    # D03
    print("\nD03 · PostgreSQL")

    versions = (
        list((ROOT / "migrations/versions").glob("*.py")) if exists("migrations/versions") else []
    )

    check(
        "D03",
        f"2+ migrations ({len(versions)} found)",
        len(versions) >= 2,
        "Check migrations/versions.",
    )

    for f in [
        f"src/{pkg}/db/models.py",
        "scripts/load_db.py",
    ]:
        check("D03", f, exists(f), "Missing required file.")

    check(
        "D03",
        "NOTES.md has D03 section",
        "## D03" in notes,
        "Add the D03 migration and loader notes.",
    )

    # D04
    print("\nD04 · Docker, Compose and tests")

    for f in [
        "Dockerfile",
        ".dockerignore",
        "docker-compose.yml",
        "Makefile",
        "tests/unit",
        "tests/integration",
    ]:
        check("D04", f, exists(f), "Missing required file or folder.")

    check(
        "D04",
        "README has local run instructions",
        "Run locally in one command" in readme,
        "Add the D04 README section.",
    )

    tests = run(["uv", "run", "pytest", "tests/unit"])

    summary = re.search(
        r"\d+ (?:passed|failed|error)[^\n]*",
        tests.stdout,
    )

    last = summary.group(0) if summary else "no test summary"

    check(
        "D04",
        f"Unit tests pass ({last})",
        tests.returncode == 0,
        "Run uv run poe test and inspect the first failure.",
    )

    # D05
    print("\nD05 · CI/CD and going live")

    for f in [
        ".github/workflows/ci.yml",
        ".github/workflows/cd.yml",
        "scripts/smoke.py",
    ]:
        check("D05", f, exists(f), "Missing required file.")

    check(
        "D05",
        "README has CI badge",
        "actions/workflows/ci.yml/badge.svg" in readme,
        "Add the CI badge.",
    )

    url_match = re.search(
        r"https://[\w.-]+\.onrender\.com",
        readme,
    )

    check(
        "D05",
        "README has live URL",
        bool(url_match),
        "Add your live Render URL.",
    )

    tag = run(["git", "tag", "--list", "week-1"]).stdout.strip()

    check(
        "D05",
        "Git tag week-1 exists",
        tag == "week-1",
        "Create and push the week-1 tag.",
    )

    check(
        "D05",
        "NOTES.md has D05 section",
        "## D05" in notes,
        "Add rollback and deployment notes.",
    )

    # LIVE
    if live or url_match:
        base = live or url_match.group(0)

        print(f"\nLIVE · {base}")

        try:
            with urllib.request.urlopen(
                f"{base}/health",
                timeout=90,
            ) as response:
                body = json.loads(response.read())

            check(
                "LIVE",
                f"/health returned 200, version {body.get('version')}",
                True,
            )

            head = run(
                [
                    "git",
                    "rev-parse",
                    "--verify",
                    "--quiet",
                    "origin/main",
                ]
            )

            if head.returncode == 0:
                sha = head.stdout.strip()

                check(
                    "LIVE",
                    "Live version matches origin/main",
                    body.get("version") == sha,
                    f"origin/main is {sha[:7]}; check the latest deployment.",
                    warn_only=True,
                )

        except Exception as error:
            check(
                "LIVE",
                "/health returned 200",
                False,
                str(error),
            )

    # SUMMARY
    total = len(results)
    passed = sum(ok for _, ok in results)

    print(f"\n{passed} of {total} checks passed.")

    for day in ["D01", "D02", "D03", "D04", "D05", "LIVE"]:
        missing = [ok for d, ok in results if d == day and not ok]

        if missing:
            print(f"Start with {day}: {len(missing)} open item(s).")
            break
    else:
        print("Week 1 is complete!")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
