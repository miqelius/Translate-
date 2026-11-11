import pytest
from pydantic import ValidationError

from engine.result import TranslationResult


def test_result_accepts_valid_payload():
    result = TranslationResult(
        final_translation="გამარჯობა",
        confidence_score=90,
        issues_fixed=["ტერმინი გასწორდა"],
        summary="შემოწმდა",
    )
    assert result.confidence_score == 90

def test_result_rejects_confidence_outside_range():
    with pytest.raises(ValidationError):
        TranslationResult(
            final_translation="x", confidence_score=101, summary="invalid"
        )
