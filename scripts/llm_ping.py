"""Test Gemini and Groq LLM API connectivity."""

import sys
import time

import httpx
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    gemini_api_key: str = ""
    groq_api_key: str = ""

    llm_primary_model: str = "gemini-3.5-flash"
    llm_fallback_model: str = "openai/gpt-oss-20b"


PROMPT = "Reply with exactly: HardenHelp LLM connection successful."

MAX_ATTEMPTS = 3
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def error_message(response: httpx.Response) -> str:
    try:
        data = response.json()
        return data.get("error", {}).get("message", response.text[:500])
    except ValueError:
        return response.text[:500]


def post_with_retries(
    client: httpx.Client,
    url: str,
    **kwargs,
) -> httpx.Response | None:
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = client.post(url, **kwargs)

            if response.status_code not in RETRYABLE_STATUS_CODES:
                return response

            if attempt == MAX_ATTEMPTS:
                return response

            print(
                f"Temporary HTTP {response.status_code}. Retrying ({attempt}/{MAX_ATTEMPTS - 1})..."
            )

        except (httpx.TimeoutException, httpx.TransportError) as exc:
            if attempt == MAX_ATTEMPTS:
                print(f"FAILED: {type(exc).__name__}: {exc}")
                return None

            print(f"{type(exc).__name__}. Retrying ({attempt}/{MAX_ATTEMPTS - 1})...")

        time.sleep(2**attempt)

    return None


def test_gemini(
    client: httpx.Client,
    api_key: str,
    model: str,
) -> bool:
    print(f"\n--- GEMINI TEST ({model}) ---")

    if not api_key:
        print("FAILED: GEMINI_API_KEY is missing.")
        return False

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    headers = {"x-goog-api-key": api_key}

    payload = {
        "contents": [{"parts": [{"text": PROMPT}]}],
        "generationConfig": {
            "maxOutputTokens": 100,
            "temperature": 0,
        },
    }

    response = post_with_retries(
        client,
        url,
        headers=headers,
        json=payload,
    )

    if response is None:
        return False

    if response.is_error:
        print(f"FAILED: HTTP {response.status_code}")
        print(error_message(response))
        return False

    try:
        data = response.json()
        answer = data["candidates"][0]["content"]["parts"][0]["text"]

        print("SUCCESS: Gemini responded.")
        print(f"Response: {answer.strip()}")
        return True

    except (KeyError, IndexError, ValueError) as exc:
        print(f"FAILED: {type(exc).__name__}: {exc}")
        return False


def test_groq(
    client: httpx.Client,
    api_key: str,
    model: str,
) -> bool:
    print(f"\n--- GROQ TEST ({model}) ---")

    if not api_key:
        print("FAILED: GROQ_API_KEY is missing.")
        return False

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": PROMPT,
            }
        ],
        "max_tokens": 100,
        "temperature": 0,
    }

    try:
        response = client.post(
            url,
            headers=headers,
            json=payload,
        )

        if response.is_error:
            print(f"FAILED: HTTP {response.status_code}")
            print(error_message(response))
            return False

        data = response.json()
        answer = data["choices"][0]["message"]["content"]

        print("SUCCESS: Groq responded.")
        print(f"Response: {answer.strip()}")
        return True

    except (httpx.RequestError, KeyError, IndexError, ValueError) as exc:
        print(f"FAILED: {type(exc).__name__}: {exc}")
        return False


def main() -> int:
    settings = LLMSettings()

    print("=" * 55)
    print("HARDENHELP - LLM CONNECTIVITY TEST")
    print("=" * 55)

    timeout = httpx.Timeout(
        connect=10.0,
        read=90.0,
        write=30.0,
        pool=10.0,
    )

    with httpx.Client(timeout=timeout) as client:
        gemini_ok = test_gemini(
            client,
            settings.gemini_api_key,
            settings.llm_primary_model,
        )

        groq_ok = test_groq(
            client,
            settings.groq_api_key,
            settings.llm_fallback_model,
        )

    print("\n" + "=" * 55)
    print("FINAL RESULTS")
    print("=" * 55)

    print(f"Gemini: {'PASS' if gemini_ok else 'FAIL'}")
    print(f"Groq:   {'PASS' if groq_ok else 'FAIL'}")

    if gemini_ok and groq_ok:
        print("\nBoth LLM providers are working!")
        return 0

    if gemini_ok or groq_ok:
        print("\nOne provider is working. Check the failed provider.")
        return 1

    print("\nBoth providers failed. Check configuration and errors.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
