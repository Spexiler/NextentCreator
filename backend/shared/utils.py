import re


def count_words(text: str) -> int:
    if not text:
        return 0
    cleaned = re.sub(r"\s+", "", text)
    return len(cleaned)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    if not text or len(text) <= max_length:
        return text or ""
    return text[:max_length].rstrip() + suffix


def format_agent_time(seconds: float) -> str:
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    return f"{seconds:.1f}s"