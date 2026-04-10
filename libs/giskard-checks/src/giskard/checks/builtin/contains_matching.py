"""Contains-any / contains-all check implementation.

This module provides two checks that validate whether a set of keywords
appears within a text string. It supports Unicode normalization, case
sensitivity control, and flexible text extraction from traces.
"""

from __future__ import annotations

from typing import override

from giskard.core import provide_not_none
from pydantic import Field

from ..core.check import Check
from ..core.extraction import NoMatch, provided_or_resolve
from ..core.result import CheckResult
from ..core import Trace
from ..utils.normalization import NormalizationForm, normalize_string


@Check.register("contains_any")
class ContainsAny[InputType, OutputType, TraceType: Trace](  # pyright: ignore[reportMissingTypeArgument]
    Check[InputType, OutputType, TraceType]
):
    """Check that passes if the text contains AT LEAST ONE value from the list.

    Examples
    --------
    Direct text and values::

        check = ContainsAny(
            text="Machine learning is a subset of AI.",
            values=["machine learning", "ML", "artificial intelligence"],
            case_sensitive=False,
        )

    Extract text from trace::

        check = ContainsAny(
            text_key="trace.last.outputs.response",
            values=["consult a doctor", "medical advice"],
        )
    """

    text: str | None = Field(
        default=None,
        description="The text string to search within. If None, extracted from trace using text_key.",
    )
    text_key: str = Field(
        default="trace.last.outputs",
        description="JSONPath expression to extract the text from the trace.",
    )
    values: list[str] = Field(
        description="List of strings to check against. Passes if at least one is found.",
    )
    normalization_form: NormalizationForm | None = Field(
        default="NFKC",
        description="Unicode normalization form to apply (NFC, NFD, NFKC, NFKD). Defaults to NFKC.",
    )
    case_sensitive: bool = Field(
        default=False,
        description="If True, matching is case-sensitive. Defaults to False.",
    )

    def _format_str(self, value: str) -> str:
        """Format a string for matching by applying normalization and case handling."""
        value = normalize_string(value, self.normalization_form)
        if not self.case_sensitive:
            value = value.lower()
        return value

    @override
    async def run(self, trace: TraceType) -> CheckResult:
        """Execute the contains-any check."""
        text = provided_or_resolve(
            trace, key=self.text_key, value=provide_not_none(self.text)
        )

        details = {"text": text, "values": self.values}

        if isinstance(text, NoMatch):
            return CheckResult.failure(
                message=f"No value found for text key '{self.text_key}'.",
                details=details,
            )

        if not isinstance(text, str):
            return CheckResult.failure(
                message=f"Value for text key '{self.text_key}' is not a string, got {type(text)}.",
                details=details,
            )

        formatted_text = self._format_str(text)

        for value in self.values:
            if self._format_str(value) in formatted_text:
                return CheckResult.success(
                    message=f"The text contains '{value}'.",
                    details={**details, "matched": value},
                )

        return CheckResult.failure(
            message=f"The text does not contain any of: {self.values}.",
            details=details,
        )


@Check.register("contains_all")
class ContainsAll[InputType, OutputType, TraceType: Trace](  # pyright: ignore[reportMissingTypeArgument]
    Check[InputType, OutputType, TraceType]
):
    """Check that passes if the text contains EVERY value from the list.

    Examples
    --------
    Direct text and values::

        check = ContainsAll(
            text="The dosage is 200mg. Consult a doctor before use.",
            values=["dosage", "mg", "consult"],
            case_sensitive=False,
        )

    Extract text from trace::

        check = ContainsAll(
            text_key="trace.last.outputs.response",
            values=["definition", "example"],
        )
    """

    text: str | None = Field(
        default=None,
        description="The text string to search within. If None, extracted from trace using text_key.",
    )
    text_key: str = Field(
        default="trace.last.outputs",
        description="JSONPath expression to extract the text from the trace.",
    )
    values: list[str] = Field(
        description="List of strings to check against. Passes only if every item is found.",
    )
    normalization_form: NormalizationForm | None = Field(
        default="NFKC",
        description="Unicode normalization form to apply (NFC, NFD, NFKC, NFKD). Defaults to NFKC.",
    )
    case_sensitive: bool = Field(
        default=False,
        description="If True, matching is case-sensitive. Defaults to False.",
    )

    def _format_str(self, value: str) -> str:
        """Format a string for matching by applying normalization and case handling."""
        value = normalize_string(value, self.normalization_form)
        if not self.case_sensitive:
            value = value.lower()
        return value

    @override
    async def run(self, trace: TraceType) -> CheckResult:
        """Execute the contains-all check."""
        text = provided_or_resolve(
            trace, key=self.text_key, value=provide_not_none(self.text)
        )

        details = {"text": text, "values": self.values}

        if isinstance(text, NoMatch):
            return CheckResult.failure(
                message=f"No value found for text key '{self.text_key}'.",
                details=details,
            )

        if not isinstance(text, str):
            return CheckResult.failure(
                message=f"Value for text key '{self.text_key}' is not a string, got {type(text)}.",
                details=details,
            )

        formatted_text = self._format_str(text)

        missing = [v for v in self.values if self._format_str(v) not in formatted_text]

        if missing:
            return CheckResult.failure(
                message=f"The text is missing: {missing}.",
                details={**details, "missing": missing},
            )

        return CheckResult.success(
            message=f"The text contains all of: {self.values}.",
            details=details,
        )
