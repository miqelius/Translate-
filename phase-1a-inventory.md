# Phase 1A inventory — source: original `bot.py`

## Functions and classes

| Original unit | Decision | Destination | Notes |
|---|---|---|---|
| `TranslationResult` | MOVE | `engine/result.py` | Pydantic fields and constraints retained |
| `call_translator` | MOVE | `agents/translator.py` | DeepSeek model and prompt retained |
| `call_accuracy_reviewer` | MOVE | `agents/accuracy.py` | Reviewer prompt retained |
| `call_guard` | MOVE | `agents/historical_guard.py` | Guard prompt retained |
| `call_critic` | MOVE | `agents/style.py` | Critic prompt retained |
| `call_synthesizer` | MOVE | `agents/synthesizer.py` | Gemini model, JSON validation and fallback retained |
| `cmd_start` | MOVE | `apps/telegram/handlers.py` | Start response retained |
| `send_result` | MOVE | `apps/telegram/formatters.py` | HTML escaping, message length and TXT fallback retained |
| `process_translation_request` | MOVE | `apps/telegram/handlers.py` | 500-word check and in-memory active-user guard retained |
| `main` | MOVE | `apps/telegram/__main__.py` | Polling startup retained |
| module-level clients | MOVE | `agents/clients.py` | Lazy construction; credentials are not read during test imports |

## Globals and state

| Name | Decision | Destination / reason |
|---|---|---|
| `active_users` | DEFER | Remains process-local in handlers until database/job phases |
| `TELEGRAM_MSG_LIMIT` | MOVE | `apps/telegram/formatters.py` |
| `bot`, `dp` | MOVE | Runtime objects are created in `apps/telegram/__main__.py` |
| Provider clients | MOVE | Lazy factories in `agents/clients.py` |

## Environment variables

| Variable | Required | Destination |
|---|---:|---|
| `BOT_TOKEN` | yes | `core/config.py` |
| `DEEPSEEK_API_KEY` | yes | `core/config.py` |
| `GEMINI_API_KEY` | yes | `core/config.py` |

## Dependencies

`aiogram`, `openai`, `google-genai`, `python-dotenv`, and `pydantic` remain. Version constraints are retained from the original requirements file. Test/lint tools are listed in `requirements-dev.txt`.

## Intentionally deferred

Mode registry, language selection, translation memory, glossary, durable jobs, worker, rate limits, retry/fallback policy, website, PDF/DOCX parsing and chunking are not Phase 1A work.

## Verification caveat

The prompt strings are copied from the original source. The automated prompt tests protect the extracted values. The model response is nondeterministic, so a live API output is not expected to be byte-identical. Manual Telegram verification with valid credentials is still required.
