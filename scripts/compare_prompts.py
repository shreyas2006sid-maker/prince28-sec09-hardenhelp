"""Evaluate HardenHelp classification prompts with persistent response caching.

Run:
    uv run python scripts/compare_prompts.py
"""

import argparse
import asyncio
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

from hardenhelp.config import get_settings
from hardenhelp.llm.gateway import build_gateway

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TESTSET = ROOT / "eval" / "prompt_testset.jsonl"
DEFAULT_PROMPTS = ROOT / "prompts"
DEFAULT_OUTPUT = ROOT / "eval" / "results"
DEFAULT_CACHE = ROOT / "eval" / "cache" / "classifier_cache.jsonl"

VALID_LABELS = {"docs", "personal", "off_topic"}
INJECTION_QUESTION_INDEX = 19


def sha256(value: str) -> str:
    """Return the SHA-256 hash of a string."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_testset(path: Path) -> list[dict]:
    """Load and validate the JSONL test set."""
    questions = []

    with path.open("r", encoding="utf-8-sig") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number}: {exc}") from exc

            if not isinstance(item, dict):
                raise ValueError(f"Line {line_number} must contain a JSON object.")

            question = item.get("question")
            label = item.get("label")

            if not isinstance(question, str) or not question.strip():
                raise ValueError(f"Line {line_number} has a missing or empty question.")

            if label not in VALID_LABELS:
                raise ValueError(f"Line {line_number} has an invalid label: {label!r}")

            questions.append(
                {
                    "question": question.strip(),
                    "label": label,
                }
            )

    if not questions:
        raise ValueError("The test set contains no questions.")

    return questions


def load_cache(path: Path) -> dict:
    """Load previously successful model responses."""
    cache = {}

    if not path.exists():
        return cache

    with path.open("r", encoding="utf-8-sig") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid cache JSON on line {line_number}: {exc}") from exc

            if record.get("cache_key") and record.get("status") == "ok":
                cache[record["cache_key"]] = record

    return cache


def make_cache_key(prompt_text: str, question: str) -> str:
    """Create a cache key from the prompt and question."""
    return sha256(sha256(prompt_text) + ":" + sha256(question))


def validate_prediction(raw_answer: str) -> str | None:
    """Accept only an exact, lowercase classification label."""
    prediction = raw_answer.strip()

    if prediction in VALID_LABELS:
        return prediction

    return None


async def run_evaluation(
    questions: list[dict],
    prompt_files: list[Path],
    output_file: Path,
    cache_file: Path,
) -> list[dict]:
    """Evaluate prompts, using cached answers whenever possible."""
    settings = get_settings()
    gemini_only_settings = settings.model_copy(update={"groq_api_key": ""})
    gateway = build_gateway(gemini_only_settings)

    cache = load_cache(cache_file)
    results = []
    model_calls = 0

    cache_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        with (
            output_file.open("w", encoding="utf-8") as output,
            cache_file.open("a", encoding="utf-8") as cache_output,
        ):
            for prompt_file in prompt_files:
                prompt_version = prompt_file.stem
                prompt_text = prompt_file.read_text(encoding="utf-8-sig").strip()

                if not prompt_text:
                    raise ValueError(f"Prompt file is empty: {prompt_file}")

                print(f"\nTesting prompt: {prompt_version}")

                for index, item in enumerate(questions, start=1):
                    question = item["question"]
                    expected = item["label"]
                    cache_key = make_cache_key(prompt_text, question)

                    print(
                        f"  Question {index}/{len(questions)} [{expected}]...",
                        end=" ",
                        flush=True,
                    )

                    if cache_key in cache:
                        record = dict(cache[cache_key])
                        record["prompt_version"] = prompt_version
                        record["question_index"] = index
                        record["label"] = expected
                        record["question"] = question
                        record["cache_hit"] = True
                        print("CACHED")

                    else:
                        model_calls += 1

                        try:
                            response = await gateway.generate(
                                [
                                    {
                                        "role": "system",
                                        "content": prompt_text,
                                    },
                                    {
                                        "role": "user",
                                        "content": question,
                                    },
                                ],
                                purpose="classifier_eval",
                                prompt_version=prompt_version,
                            )

                            raw_answer = response.text
                            prediction = validate_prediction(raw_answer)

                            record = {
                                "cache_key": cache_key,
                                "prompt_version": prompt_version,
                                "question_index": index,
                                "label": expected,
                                "question": question,
                                "status": "ok",
                                "answer": raw_answer,
                                "prediction": prediction,
                                "correct": prediction == expected,
                                "provider": response.provider,
                                "model": response.model,
                                "tokens_in": response.tokens_in,
                                "tokens_out": response.tokens_out,
                                "latency_ms": response.latency_ms,
                                "cost_inr": response.cost_inr,
                                "attempts": response.attempts,
                                "fallback_used": response.fallback_used,
                                "cache_hit": False,
                            }

                            cache[cache_key] = record

                            cache_output.write(json.dumps(record, ensure_ascii=False) + "\n")
                            cache_output.flush()

                            print(f"{prediction or 'INVALID'} ({response.latency_ms} ms)")

                        except Exception as exc:
                            record = {
                                "prompt_version": prompt_version,
                                "question_index": index,
                                "label": expected,
                                "question": question,
                                "status": "error",
                                "prediction": None,
                                "correct": False,
                                "error": (f"{type(exc).__name__}: {exc}"),
                                "cache_hit": False,
                            }

                            print(f"FAILED ({type(exc).__name__})")

                    results.append(record)

                    evaluation_record = {
                        key: value for key, value in record.items() if key != "cache_key"
                    }
                    output.write(json.dumps(evaluation_record, ensure_ascii=False) + "\n")
                    output.flush()

    finally:
        for provider in gateway.providers:
            client = getattr(provider, "_client", None)
            if client is not None:
                await client.aclose()

    print(f"\nModel calls made now: {model_calls}")
    return results


def write_report(
    path: Path,
    results: list[dict],
    prompt_names: list[str],
    question_count: int,
) -> None:
    """Write classification accuracy and comparison results."""
    lines = [
        "# HardenHelp Classification Prompt Comparison",
        "",
        f"Generated: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        "",
        f"Questions per prompt: {question_count}",
        "",
        "| Prompt | Correct | Missed | Invalid | Accuracy |",
        "|---|---:|---:|---:|---:|",
    ]

    for name in prompt_names:
        items = [item for item in results if item["prompt_version"] == name]

        correct = sum(item.get("correct", False) for item in items)
        invalid = sum(
            item.get("status") == "ok" and item.get("prediction") is None for item in items
        )
        missed = len(items) - correct
        accuracy = correct / len(items) * 100 if items else 0

        lines.append(f"| {name} | {correct} | {missed} | {invalid} | {accuracy:.1f}% |")

    lines.extend(
        [
            "",
            "## Missed questions",
            "",
        ]
    )

    for name in prompt_names:
        items = [
            item
            for item in results
            if item["prompt_version"] == name and not item.get("correct", False)
        ]

        lines.append(f"### {name}")
        lines.append("")

        if not items:
            lines.append("No missed questions.")
        else:
            for item in items:
                got = item.get("prediction")
                if item.get("status") == "error":
                    got = "ERROR"
                elif got is None:
                    got = "INVALID"

                lines.append(
                    f"- Q{item['question_index']}: "
                    f"expected `{item['label']}`, got `{got}`. "
                    f"{item['question']}"
                )

        lines.append("")

    lines.extend(
        [
            "## Evaluation notes",
            "",
            "- Only exact lowercase labels are accepted.",
            "- Invalid responses count as incorrect.",
            "- Cached responses do not make new model calls.",
            "- The injection test is question 19 and must be `off_topic`.",
            "",
        ]
    )

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare HardenHelp classification prompts.")
    parser.add_argument(
        "--testset",
        type=Path,
        default=DEFAULT_TESTSET,
    )
    parser.add_argument(
        "--prompts-dir",
        type=Path,
        default=DEFAULT_PROMPTS,
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT,
    )
    parser.add_argument(
        "--cache",
        type=Path,
        default=DEFAULT_CACHE,
    )
    args = parser.parse_args()

    try:
        questions = load_testset(args.testset)
        prompt_files = sorted(args.prompts_dir.glob("classify_*.md"))

        if not prompt_files:
            raise ValueError(f"No classify_*.md files found in {args.prompts_dir}")

        args.output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = args.output_dir / (f"classification_{timestamp}.jsonl")
        report_file = args.output_dir / (f"classification_report_{timestamp}.md")

        print(f"Questions loaded: {len(questions)}")
        print(f"Classifier prompts found: {len(prompt_files)}")

        results = asyncio.run(
            run_evaluation(
                questions,
                prompt_files,
                output_file,
                args.cache,
            )
        )

        prompt_names = [path.stem for path in prompt_files]

        write_report(
            report_file,
            results,
            prompt_names,
            len(questions),
        )

        successful = sum(item.get("status") == "ok" for item in results)
        correct = sum(item.get("correct", False) for item in results)

        injection_results = [
            item for item in results if item.get("question_index") == INJECTION_QUESTION_INDEX
        ]

        print("\n--- Classification summary ---")
        print(f"Total evaluations: {len(results)}")
        print(f"Successful responses: {successful}")
        print(f"Correct classifications: {correct}")

        print("\n--- Missed questions ---")
        for item in results:
            if item.get("correct", False):
                continue

            got = item.get("prediction")
            if item.get("status") == "error":
                got = "ERROR"
            elif got is None:
                got = "INVALID"

            print(
                f"missed | {item['prompt_version']} | "
                f"Q{item['question_index']} | "
                f"expected={item['label']} | got={got}"
            )

        for item in injection_results:
            if item.get("prediction") != "off_topic":
                print(
                    f"LEAK | {item['prompt_version']} | "
                    f"Q{INJECTION_QUESTION_INDEX} | "
                    f"got={item.get('prediction') or 'INVALID'}"
                )

        print(f"\nResults: {output_file}")
        print(f"Report: {report_file}")
        print(f"Cache: {args.cache}")

        return 1 if successful != len(results) else 0

    except Exception as exc:
        print(
            f"Error: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
