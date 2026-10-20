#!/usr/bin/env python3
"""Compliance check for a generated agent skeleton.

The build skills must hand the team an agent with NO observability wiring in it.
The team adds that themselves. This script fails if the skeleton breaks that rule,
exceeds the complexity caps, or was not customized for the customer in brief.yaml
(HR template text left behind, tools not renamed, write tool not set, too few
questions). Run it from the skeleton directory or pass a path.

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


# ---- fit check: was the template actually customized for this customer? ----
HR_TEMPLATE_TEXT = ["employee self-service", "human in HR", "Jordan Lee", "KB-001", "open_screen",
                    "start_workflow", "lookup_my_record", "Direct Deposit", "next pay date"]
MIN_QUESTIONS = 30

def _read_brief(root: pathlib.Path) -> dict:
    b = root / "brief.yaml"
    if not b.exists():
        return {}
    try:
        import yaml  # type: ignore
        return yaml.safe_load(b.read_text()) or {}
    except Exception:
        out: dict = {}
        for line in b.read_text().splitlines():
            if line.startswith("slug:"): out["slug"] = line.split(":", 1)[1].strip().strip('"')
            if line.startswith("customer:"): out["customer"] = line.split(":", 1)[1].strip().strip('"')
            if "tools_and_data:" in line:
                out.setdefault("agent", {})["tools_and_data"] = [x.strip().strip('"') for x in line.split("[", 1)[1].rstrip("]").split(",")]
        return out

def fit_check(root: pathlib.Path) -> list[str]:
    probs: list[str] = []
    brief = _read_brief(root)
    slug = str(brief.get("slug") or "")
    customer = str(brief.get("customer") or "")
    code = {p: p.read_text(errors="ignore") for p in root.rglob("*.py") if ".venv" not in p.parts and p.name != "run_batch.py"}
    tools_files = [p for p in code if p.name == "tools.py"]
    # 1. HR template text left behind (any scenario but HR)
    if slug and slug != "hr-payroll":
        for p, text in code.items():
            for needle in HR_TEMPLATE_TEXT:
                if needle in text:
                    probs.append(f"{p.relative_to(root)}: HR template text left in place ('{needle}'). Customize it for {customer or 'the customer'}.")
                    break
    # 2. the write tool is set and exists
    for p in tools_files:
        text = code[p]
        m = re.search(r'^WRITE_TOOL\s*=\s*"([A-Za-z_][A-Za-z0-9_]*)"', text, re.M)
        if not m:
            probs.append(f"{p.relative_to(root)}: WRITE_TOOL is not set. Name the one tool that changes something.")
        elif not re.search(rf"^def {re.escape(m.group(1))}\(", text, re.M):
            probs.append(f"{p.relative_to(root)}: WRITE_TOOL is '{m.group(1)}' but no tool with that name is defined.")
    # 3. tool names should come from the brief
    want = [str(t) for t in (brief.get("agent") or {}).get("tools_and_data", [])]
    if want and tools_files and slug != "hr-payroll":
        text = " ".join(code[p].lower() for p in tools_files)
        hits = sum(1 for t in want if any(w for w in re.findall(r"[a-z]{4,}", t.lower()) if w in text))
        if hits < max(1, len(want) // 2):
            probs.append(f"tools.py: only {hits} of {len(want)} tools from brief.yaml are recognizable. Rename the tools for {customer or 'the customer'}.")
    # 4. questions: enough of them, and no template header
    q = root / "questions.txt"
    if q.exists():
        lines = q.read_text().splitlines()
        if any(l.startswith("# CUSTOMIZE") for l in lines):
            probs.append("questions.txt: the template's '# CUSTOMIZE' header is still there. Remove it.")
        n = len([l for l in lines if l.strip() and not l.startswith("#")])
        if n < MIN_QUESTIONS:
            probs.append(f"questions.txt has {n} inputs; the skill asks for {MIN_QUESTIONS}.")
    # 4b. a scenario with a second source must fill SOURCE_RECORDS, including a record for the fake article
    if (brief.get("agent") or {}).get("second_source"):
        dp = root / "data.py"
        if dp.exists():
            try:
                import runpy
                ns = runpy.run_path(str(dp))
                recs, fake = ns.get("SOURCE_RECORDS") or {}, ns.get("FAKE_ARTICLE") or {}
                if not recs:
                    probs.append("data.py: SOURCE_RECORDS is empty. This scenario has a second source (" + str(brief["agent"]["second_source"]) + "); fill it so the writer sees both.")
                elif fake.get("id") not in recs:
                    probs.append("data.py: SOURCE_RECORDS has no record for the fake article (" + str(fake.get("id")) + "). Add one that does not list what the fake article claims.")
            except Exception as exc:  # a broken data.py is reported by the smoke test; do not fail the check twice
                probs.append(f"data.py: could not be read ({type(exc).__name__}).")
    # 5. README names the customer
    readme = root / "README.md"
    if readme.exists() and customer:
        title = readme.read_text(errors="ignore").splitlines()[0].lower() if readme.read_text(errors="ignore").strip() else ""
        words = [w for w in re.findall(r"[a-z]{3,}", customer.lower()) if w not in ("and", "the", "team", "company")]
        if "<customer>" in title or not any(w in title for w in words):
            probs.append(f"README.md: the title does not name the customer ({customer}).")
    # 6. env files: placeholders that break the model client
    for name in (".env.example", ".env"):
        f = root / name
        if f.exists():
            text = f.read_text(errors="ignore")
            if "provided_by_facilitator" in text:
                probs.append(f"{name}: 'provided_by_facilitator' placeholder still present. Fill it in or delete the line.")
            if name == ".env" and re.search(r"^OPENAI_BASE_URL=\s*$", text, re.M):
                probs.append(".env: OPENAI_BASE_URL is empty. Delete the line if you have no gateway; an empty value points the client at nothing.")
    return probs

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
    # .env files are allowed to carry SPLUNK_AO_* placeholders (the host template does); code must not read them.
    for p in py_files:
        text = p.read_text(errors="ignore")
        for prefix in FORBIDDEN_ENV:
            if prefix in text:
                problems.append(f"{p.relative_to(root)}: reads {prefix}* variables. Leave observability config to the team.")
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
    problems += fit_check(root)
    if problems:
        print("SKELETON CHECK: FAIL")
        for x in problems: print("  -", x)
        return 1
    print(f"SKELETON CHECK: OK  ({len(py_files)} py files, {steps} steps, {tools} tools)")
    return 0

if __name__ == "__main__":
    sys.exit(main(pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()))
