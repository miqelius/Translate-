import pytest

from core.config import get_settings

BASE = {"BOT_TOKEN": "t", "DEEPSEEK_API_KEY": "d", "GEMINI_API_KEY": "g"}


def test_missing_variables_are_listed():
    with pytest.raises(ValueError, match="BOT_TOKEN, GEMINI_API_KEY"):
        get_settings({"DEEPSEEK_API_KEY": "d"})


def test_whitespace_only_value_counts_as_missing():
    with pytest.raises(ValueError, match="DEEPSEEK_API_KEY"):
        get_settings({**BASE, "DEEPSEEK_API_KEY": "   "})


def test_defaults():
    s = get_settings(BASE)
    assert s.allowed_user_ids == frozenset()
    assert s.max_concurrent_jobs == 5
    assert s.request_timeout_seconds == 90.0
    assert s.log_level == "INFO"


def test_optional_values_parsed():
    s = get_settings({**BASE, "ALLOWED_USER_IDS": "1, 2;3,", "MAX_CONCURRENT_JOBS": "2",
                      "REQUEST_TIMEOUT_SECONDS": "30.5", "LOG_LEVEL": "debug"})
    assert s.allowed_user_ids == frozenset({1, 2, 3})
    assert s.max_concurrent_jobs == 2
    assert s.request_timeout_seconds == 30.5
    assert s.log_level == "DEBUG"


@pytest.mark.parametrize("extra", [
    {"ALLOWED_USER_IDS": "abc"},
    {"MAX_CONCURRENT_JOBS": "0"},
    {"MAX_CONCURRENT_JOBS": "x"},
    {"REQUEST_TIMEOUT_SECONDS": "-1"},
])
def test_invalid_optional_values_rejected(extra):
    with pytest.raises(ValueError):
        get_settings({**BASE, **extra})
