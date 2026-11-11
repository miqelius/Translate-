# MIQELIUS Historical Translation Bot

Telegram long-polling worker that translates text into a historical-diplomatic Georgian style through a multi-agent pipeline.

## Configuration

Set these environment variables in your host dashboard (never commit real secrets):
- `BOT_TOKEN` (required): token from BotFather
- `DEEPSEEK_API_KEY` (required)
- `GEMINI_API_KEY` (required)
- `ALLOWED_USER_IDS` (strongly recommended): your numeric Telegram user ID; comma-separated IDs if needed. Empty means anyone can use the bot and consume your API credits.
- `MAX_CONCURRENT_JOBS` (default `1` in the Render Blueprint)
- `REQUEST_TIMEOUT_SECONDS` (default `90`)
- `LOG_LEVEL` (default `INFO`)

## Deploy

This is a background worker, not a web service. Run exactly one instance per Telegram bot token. The included Render Blueprint uses a paid Starter worker; Render's free web-service tier is not suitable for an always-on polling worker.

## Local run

`pip install -r requirements-dev.txt && cp .env.example .env && python bot.py`

Never commit `.env`. If a Telegram token was ever exposed in Git history, revoke it in BotFather and create a replacement.

## Verification status

The supplied Phase 1A package reports 48 tests passing and 88% coverage. Python byte-compilation was checked during repository preparation. Real Telegram/provider API calls and a live hosted deployment have not yet been verified.
