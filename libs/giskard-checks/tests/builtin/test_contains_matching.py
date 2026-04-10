from giskard.checks import CheckStatus, ContainsAny, ContainsAll, Trace


async def test_contains_any_passes_when_one_matches() -> None:
    check = ContainsAny(text="Machine learning is amazing", values=["ML", "machine learning", "AI"])
    result = await check.run(Trace())
    assert result.status == CheckStatus.PASS

async def test_contains_any_fails_when_nothing_matches() -> None:
    check = ContainsAny(text="Hello world", values=["Python", "Java", "Rust"])
    result = await check.run(Trace())
    assert result.status == CheckStatus.FAIL


async def test_contains_any_case_insensitive() -> None:
    # "MACHINE LEARNING" in text, "machine learning" in values — different case, should still match
    check = ContainsAny(text="MACHINE LEARNING is powerful", values=["machine learning"], case_sensitive=False)
    result = await check.run(Trace())
    assert result.status == CheckStatus.PASS  # ✅ Now this makes sense

async def test_contains_all_passes_when_all_match() -> None:
    check = ContainsAll(text="Machine learning is amazing", values=["Machine learning", "amazing"])
    result = await check.run(Trace())
    assert result.status == CheckStatus.PASS

async def test_contains_all_fails_when_one_is_missing() -> None:
    check = ContainsAll(text="Machine learning is amazing", values=["Machine learning", "AI"])
    result = await check.run(Trace())
    assert result.status == CheckStatus.FAIL

async def test_contains_all_missing_reported_in_details() -> None:
    check = ContainsAll(text="Machine learning is amazing", values=["Machine learning", "AI"])
    result = await check.run(Trace())
    assert result.status == CheckStatus.FAIL
    assert "AI" in result.details["missing"]  # ← new line, verify details

async def test_contains_any_empty_values_fails() -> None:
    check = ContainsAny(text="Hello world", values=[])
    result = await check.run(Trace())
    assert result.status == CheckStatus.FAIL

async def test_contains_all_empty_values_passes() -> None:
    check = ContainsAll(text="Hello world", values=[])
    result = await check.run(Trace())
    assert result.status == CheckStatus.PASS

async def test_contains_any_extracts_text_from_trace() -> None:
    from giskard.checks import Interaction
    check = ContainsAny(
        text_key="trace.last.outputs.response",
        values=["Paris"]
    )
    interaction = Interaction(
        inputs={"query": "Capital of France?"},
        outputs={"response": "The capital of France is Paris."},
    )
    result = await check.run(Trace(interactions=[interaction]))
    assert result.status == CheckStatus.PASS

async def test_contains_any_missing_text_in_trace() -> None:
    check = ContainsAny(text_key="trace.last.outputs.nonexistent", values=["Paris"])
    result = await check.run(Trace())
    assert result.status == CheckStatus.FAIL
    assert "nonexistent" in result.message  # key name appears in error
