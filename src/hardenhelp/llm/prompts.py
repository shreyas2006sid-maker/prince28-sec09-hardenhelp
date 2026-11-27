"""Load versioned prompts from the project's prompts directory."""

from pathlib import Path


def load_prompt(directory: Path, name: str) -> str:
    """Load a prompt file and fail clearly if it is missing or empty."""
    path = directory / f"{name}.md"
    prompt = path.read_text(encoding="utf-8").strip()

    if not prompt:
        raise ValueError(f"Prompt file is empty: {path}")

    return prompt
