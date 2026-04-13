import pytest
from giskard.checks import Sentiment, CheckStatus, Trace, Interaction
from giskard.checks.core.extraction import NoMatch


async def test_min_polarity_passes() -> None:
    """Test that check passes when Sentiment has minimum polarity as 0.0"""
    check = Sentiment(text="I love this product, it is absolutely amazing!", min_polarity=0.0)
    result = await check.run(Trace())
    assert result.status == CheckStatus.PASS
    

async def test_min_polarity_fails() -> None:
    """Test that check fails when Sentiment has minimum polarity as 0.0"""
    check = Sentiment(text="I hate this product, it is absolutely terrible!", min_polarity=0.0)
    result = await check.run(Trace())
    assert result.status == CheckStatus.FAIL

async def test_max_polarity_fails() -> None:
    """Test that check fails when Sentiment has maximum polarity as 0.0"""
    check = Sentiment(text="I love this product, it is absolutely amazing!", max_polarity=0.0)
    result = await check.run(Trace())
    assert result.status == CheckStatus.FAIL

async def test_no_bounds_passes() -> None:
    """Test that check passes when Sentiment has no bounds"""
    check = Sentiment(text="I love this product, it is absolutely amazing!")
    result = await check.run(Trace())
    assert result.status == CheckStatus.PASS

async def test_text_from_trace() -> None:
    """Test extracting text from trace"""
    check = Sentiment(text_key="trace.last.outputs.response")
    interaction = Interaction(
        inputs={"query": "What is the sentiment of this text?"},
        outputs={"response": "I love this product, it is absolutely amazing!"},
    )
    result = await check.run(Trace(interactions=[interaction]))
    assert result.status == CheckStatus.PASS
    assert result.details["text"] == "I love this product, it is absolutely amazing!"

async def test_text_not_found_in_trace() -> None:
    """Test that check fails when text is not found in trace"""
    check = Sentiment(text_key="trace.last.outputs.nonexistent")
    interaction = Interaction(
        inputs={"query": "What is the sentiment of this text?"},
        outputs={"response": "I love this product, it is absolutely amazing!"},
    )
    result = await check.run(Trace(interactions=[interaction]))
    assert result.status == CheckStatus.FAIL
    assert isinstance(result.details["text"], NoMatch)
