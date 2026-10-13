#!/usr/bin/env python3
"""Compliance check for a generated agent skeleton.

The build skills must hand the team an agent with NO observability wiring in it.
The team adds that themselves. This script fails if the skeleton breaks that rule
or exceeds the complexity caps. Run it from the skeleton directory or pass a path.

Exit code 0 = compliant, 1 = violations found.
"""
from __future__ import annotations
import re, sys, pathlib

FORBIDDEN_IMPORTS = [
    "splunk_ao", "galileo", "opentelemetry", "langsmith", "langfuse",
    "arize", "phoenix", "agent_control", "traceloop", "openinference",
]
FORBIDDEN_ENV = ["GALILEO_", "SPLUNK_AO_", "OTEL_", "LANGCHAIN_TRACING", "LANGSMITH_"]
MAX_PY_FILES = 12
MAX_TOOLS = 4
MAX_STEPS = 4
REQUIRED = ["README.md", "questions.txt", "run_batch.py", ".env.example", "requirements.txt"]

def main(root: pathlib.Path) -> int:
    problems: list[str] = []
    py_files = [p for p in root.rglob("*.py") if ".venv" not in p.parts and "venv" not in p.parts]
    if len(py_files) > MAX_PY_FILES:
        problems.append(f"{len(py_files)} Python files; cap is {MAX_PY_FILES}. The agent is too big.")
    tools = steps = 0
    for p in py_files:
        text = p.read_text(errors="ignore")
        for mod in FORBIDDEN_IMPORTS:
            if re.search(rf"^\s*(import|from)\s+{re.escape(mod)}\b", text, re.M):
                problems.append(f"{p.relative_to(root)}: imports '{mod}'. The skeleton must contain no observability code.")
        tools += len(re.findall(r"^\s*#\s*TOOL:", text, re.M))
        steps += len(re.findall(r"^\s*#\s*STEP:", text, re.M))
    for p in list(root.glob(".env*")) + list(root.glob("*.md")):
        text = p.read_text(errors="ignore")
        for prefix in FORBIDDEN_ENV:
            if prefix in text and p.name != "README.md":
                problems.append(f"{p.name}: mentions {prefix}* variables. Leave observability config to the team.")
    if tools > MAX_TOOLS:
        problems.append(f"{tools} tools marked '# TOOL:'; cap is {MAX_TOOLS}.")
    if steps > MAX_STEPS:
        problems.append(f"{steps} steps marked '# STEP:'; cap is {MAX_STEPS}.")
    for name in REQUIRED:
        if not (root / name).exists():
            problems.append(f"missing {name}")
    readme = (root / "README.md")
    if readme.exists() and "What you still have to do" not in readme.read_text(errors="ignore"):
        problems.append("README.md lacks the 'What you still have to do' section.")
    q = root / "questions.txt"
    if q.exists():
        n = len([l for l in q.read_text().splitlines() if l.strip() and not l.startswith("#")])
        if n < 20:
            problems.append(f"questions.txt has {n} inputs; need at least 20 so the team has traffic to evaluate.")
    if problems:
        print("SKELETON CHECK: FAIL")
        for x in problems: print("  -", x)
        return 1
    print(f"SKELETON CHECK: OK  ({len(py_files)} py files, {steps} steps, {tools} tools)")
    return 0

if __name__ == "__main__":
    sys.exit(main(pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()))
