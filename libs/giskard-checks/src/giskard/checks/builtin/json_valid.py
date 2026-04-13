"""JSON validation check implementation."""

from __future__ import annotations

import json
import jsonschema
from typing import override


from giskard.core import provide_not_none
from pydantic import Field

from ..core import Trace
from ..core.check import Check
from ..core.extraction import NoMatch, provided_or_resolve
from ..core.result import CheckResult


@Check.register("json_valid")
class JsonValid[InputType, OutputType, TraceType: Trace](  # pyright: ignore[reportMissingTypeArgument]
    Check[InputType, OutputType, TraceType]
):
    """Check that passes if the output is valid JSON, with optional schema validation."""

    text: str | None = Field(
        default=None,
        description="The text string to check. If None, extracted from trace using text_key."
    )
    text_key: str = Field(
        default="trace.last.outputs",
        description="JSONPath expression to extract text from the trace."
    )
    json_schema: dict | None = Field(
        default=None,
        description="Optional JSON schema to validate the parsed JSON against."
    )

    @override
    async def run(self, trace: TraceType) -> CheckResult:
        text = provided_or_resolve(
            trace, key=self.text_key, value=provide_not_none(self.text)
        )

        details = {"text": text}

        # handle NoMatch — same as ContainsAny
        if isinstance(text, NoMatch):
            return CheckResult.failure(message=f"No text found at key {self.text_key}",  details=details)

        # handle wrong type
        if not isinstance(text, str):
            return CheckResult.failure(message=f"Value for text key '{self.text_key}' is not a string, got {type(text)}.",  details=details)

        # try to parse JSON
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as e:
            return CheckResult.failure(
                message= f"Output is not valid JSON: {e}",   # hint: show the parse error e
                details={**details, "error": str(e)},
            )

        if self.json_schema is not None:
            try:
                jsonschema.validate(instance=parsed, schema=self.json_schema)
            except jsonschema.exceptions.ValidationError as e:
                return CheckResult.failure(
                    message=f"JSON does not match schema: {e.message}",
                    details={**details, "error": e.message, "parsed": parsed},
                )
        
        return CheckResult.success(
            message="Output is valid JSON",
            details={**details, "parsed": parsed},
        )
