from giskard.checks import CheckStatus, JsonValid, Trace


async def test_json_valid_passes_for_valid_json() -> None:
    check = JsonValid(text='{"name": "Alice", "age": 30}')
    result = await check.run(Trace())
    assert result.status == CheckStatus.PASS
    
async def test_json_valid_fails_for_invalid_json() -> None:
    check = JsonValid(text='{name: Alice}')
    result = await check.run(Trace())
    assert result.status == CheckStatus.FAIL

async def test_json_valid_passes_for_matching_schema()-> None:
    check = JsonValid(text='{"name": "Alice", "age": 30}', json_schema={
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required": ["name", "age"]
    })
    result = await check.run(Trace())
    assert result.status == CheckStatus.PASS

async def test_json_valid_fails_for_non_matching_schema()-> None:
    check = JsonValid(text='{"name": "Alice", "age": "30"}', json_schema={
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required": ["name", "age"]
    })
    result = await check.run(Trace())
    assert result.status == CheckStatus.FAIL

async def test_json_valid_extracts_text_from_trace() -> None:
    from giskard.checks import Interaction
    interaction = Interaction(
        inputs={"query": "Return JSON"},
        outputs='{"name": "Alice", "age": 30}',   # ← valid JSON as output
    )
    check = JsonValid(text_key="trace.last.outputs")
    result = await check.run(Trace(interactions=[interaction]))
    assert result.status == CheckStatus.PASS

async def test_json_valid_fails_when_key_not_in_trace() -> None:
    check = JsonValid(text_key="trace.last.outputs.nonexistent")
    result = await check.run(Trace())
    assert result.status == CheckStatus.FAIL
