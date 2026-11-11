import pytest


@pytest.fixture(autouse=True)
def _clean_state(monkeypatch):
    """No real credentials or cached clients may leak between tests."""
    from agents import clients
    from apps.telegram import handlers

    for name in ("BOT_TOKEN", "DEEPSEEK_API_KEY", "GEMINI_API_KEY", "ALLOWED_USER_IDS",
                 "MAX_CONCURRENT_JOBS", "REQUEST_TIMEOUT_SECONDS", "LOG_LEVEL"):
        monkeypatch.delenv(name, raising=False)
    clients.get_deepseek_client.cache_clear()
    clients.get_gemini_client.cache_clear()
    handlers.active_users.clear()
    yield
