"""Planted failure switch. DEMO ONLY. Set FAILURE_MODE=none for a clean run."""
import os

MODES = ("none", "wrong_tool", "ambiguous_tools", "stale_result", "pii_leak", "latency", "injection_success")


def mode() -> str:
    m = os.getenv("FAILURE_MODE", "none").strip().lower()
    return m if m in MODES else "none"


def active(name: str) -> bool:
    return mode() == name
