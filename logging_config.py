"""Central logging configuration."""
import logging


def configure_logging(level: str = "INFO") -> None:
    resolved = logging.getLevelName(level.upper())
    logging.basicConfig(
        level=resolved if isinstance(resolved, int) else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    # Keep third-party HTTP chatter out of production logs.
    for noisy in ("httpx", "httpcore", "openai", "google_genai"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
