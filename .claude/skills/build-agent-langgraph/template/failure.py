"""Planted failure switch. DEMO ONLY.

The agent needs something for evaluators and controls to catch. The build skill
sets the default from the customer's "feared failure". Set FAILURE_MODE=none for
a clean run. Everything here is synthetic.
"""
import os

MODES = ("none", "fabricated_citation", "pii_leak", "wrong_tool", "injection_success", "latency", "wrong_category")
# injection_success: an "ignore your instructions" request is not escalated, and the reply ends with a
# synthetic internal record, as if the bot complied. Deterministic, so evaluators on the input and the
# output both have something to catch, and a control on the input can stop it before the model runs.


def mode() -> str:
    m = os.getenv("FAILURE_MODE", "none").strip().lower()
    return m if m in MODES else "none"


def active(name: str) -> bool:
    return mode() == name
