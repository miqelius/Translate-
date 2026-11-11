"""Compatibility entry point: existing Procfile can keep using python bot.py."""
import asyncio

from apps.telegram.__main__ import main

if __name__ == "__main__":
    asyncio.run(main())
