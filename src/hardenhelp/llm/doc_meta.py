"""Metadata contract for HardenHelp documents."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

Short = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=120),
]

Values = Annotated[
    list[Short],
    Field(default_factory=list, max_length=8),
]

Kind = Literal[
    "guideline",
    "rule",
    "notice",
    "list",
    "report",
    "faq",
    "form",
    "tutorial",
    "reference",
    "other",
]


class DocMeta(BaseModel):
    """Validated metadata extracted from a security document."""

    model_config = ConfigDict(extra="forbid")

    doc_kind: Kind
    year: int | None = Field(default=None, ge=1950, le=2027)
    language: Literal["en", "ta", "hi", "other"]
    summary: str = Field(min_length=20, max_length=300)
    topics: Annotated[list[Short], Field(min_length=1, max_length=6)]

    stig_id: Values
    rule_id: Values
    cci: Values
    ssg_rule: Values
    severity: Values
    os: Values

    @field_validator("topics")
    @classmethod
    def tidy_topics(cls, value: list[str]) -> list[str]:
        """Lowercase topics and remove duplicates."""
        return list(dict.fromkeys(topic.lower() for topic in value))

    @field_validator("stig_id", "rule_id", "cci", "ssg_rule", "severity", "os")
    @classmethod
    def remove_duplicates(cls, value: list[str]) -> list[str]:
        """Remove duplicate metadata values while preserving order."""
        return list(dict.fromkeys(value))
