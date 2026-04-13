"""Sentiment analysis check implementation."""

from __future__ import annotations

from textblob import TextBlob
from typing import override

from giskard.core import provide_not_none
from pydantic import Field

from ..core import Trace
from ..core.check import Check
from ..core.extraction import NoMatch, provided_or_resolve
from ..core.result import CheckResult


@Check.register("sentiment")
class Sentiment[InputType, OutputType, TraceType: Trace](
    Check[InputType, OutputType, TraceType]
):
    """Check that validates the sentiment polarity of text output."""

    text: str | None = Field(default=None, description="The text string to analyze. If None, it will be extracted from the trace using text_key.")
    text_key: str = Field(default="trace.last.outputs", description="JSONPath expression to extract text from the trace.")
    min_polarity: float | None = Field(default=None, description="The minimum acceptable polarity score, from -1.0 to 1.0.")
    max_polarity: float | None = Field(default=None, description="The maximum acceptable polarity score, from -1.0 to 1.0.")

    @override
    async def run(self, trace: TraceType) -> CheckResult:
        text = provided_or_resolve(
            trace, key=self.text_key, value=provide_not_none(self.text)
        )
        details = {"text": text}

        # handle NoMatch
        if isinstance(text, NoMatch):
            return CheckResult.failure(message=f"No text found at key {self.text_key}", details=details)

        # handle wrong type
        if not isinstance(text, str):
            return CheckResult.failure(message=f"Value for text key '{self.text_key}' is not a string, got {type(text).__name__}.", details=details)

        # compute polarity
        polarity = TextBlob(text).sentiment.polarity
        details["polarity"] = polarity

        # check bounds
        if self.min_polarity is not None and polarity < self.min_polarity:
            return CheckResult.failure(
                message=f"Sentiment polarity {polarity:.2f} is below the required minimum of {self.min_polarity:.2f}.",  # hint: show actual vs required
                details=details,
            )

        if self.max_polarity is not None and polarity > self.max_polarity:
            return CheckResult.failure(
                message=f"Sentiment polarity {polarity:.2f} is above the required maximum of {self.max_polarity:.2f}.",
                details=details,
            )

        return CheckResult.success(
            message=f"Sentiment polarity {polarity:.2f} is within acceptable bounds.",
            details=details,
        )
