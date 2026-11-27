"""Question classification for the HardenHelp chat router."""

CLASSIFIER_PROMPT_VERSION = "classify_v4"
ALLOWED_CATEGORIES = {"docs", "personal", "off_topic"}


async def classify_question(gateway, system_prompt: str, question: str):
    """Classify a question and return its category and recorded LLM result."""
    result = await gateway.generate(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        purpose="classification",
        prompt_version=CLASSIFIER_PROMPT_VERSION,
        temperature=0.0,
    )

    category = result.text.strip()

    if category not in ALLOWED_CATEGORIES:
        raise ValueError(f"Classifier returned an invalid category: {category!r}")

    return category, result
