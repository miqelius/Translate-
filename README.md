# MIQELIUS Historical Translation Bot

Telegram long-polling worker that translates text into a historical-diplomatic Georgian style through a multi-agent pipeline.

## Required environment variables

Set these in your hosting provider's dashboard. Never commit real secrets:

- `BOT_TOKEN` — Telegram bot token from BotFather
- `DEEPSEEK_API_KEY` — DeepSeek API key
- `GEMINI_API_KEY` — Google Gemini API key
- `ALLOWED_USER_IDS` — your numeric Telegram user ID (recommended; comma-separated if multiple). Empty means anyone can use the bot and consume your API credits.
- `MAX_CONCURRENT_JOBS` — defaults to `1` in the Render Blueprint
- `REQUEST_TIMEOUT_SECONDS` — defaults to `90`
- `LOG_LEVEL` — defaults to `INFO`

## Deploy

This is a **background worker**, not a web service. Run exactly one instance per Telegram bot token.

The included `render.yaml` uses a paid Render Starter worker. Render's free web-service tier is not suitable for an always-on Telegram polling worker.

## Local run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
# Fill .env locally; do not commit it.
python bot.py
```

## Quality checks

```bash
ruff check .
mypy core engine agents prompts apps --ignore-missing-imports
pytest --cov --cov-report=term-missing
```

## Security

- Never commit `.env` or paste credentials into GitHub.
- Set `ALLOWED_USER_IDS` before launch, otherwise the bot is open to everyone.
- If a Telegram token was ever committed or exposed, revoke it in BotFather and create a new one.
- Keep only one polling worker active for this bot token.

## Verification status

The supplied Phase 1A package reports 48 passing tests and 88% coverage. Python byte-compilation was checked during preparation. Real Telegram/DeepSeek/Gemini API calls and a live hosted deployment have not yet been verified.
