#!/usr/bin/env python3
"""Copy a build skill's template into a new directory and seed it with the brief.

    python shared/scaffold.py --skill build-agent-langgraph --brief scenarios/hr-payroll/brief.yaml --out agents/hr-payroll-langgraph

Shared by all build skills so they can't drift. After this, the skill customizes
the '# CUSTOMIZE:' blocks and nothing else.
"""
import argparse, pathlib, re, shutil, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS = ROOT / ".claude" / "skills"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill", required=True, choices=[p.name for p in SKILLS.iterdir() if (p / "template").is_dir()])
    ap.add_argument("--brief", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--failure", default=None, help="override feared_failure.kind")
    a = ap.parse_args()
    template = SKILLS / a.skill / "template"
    out = pathlib.Path(a.out).resolve()
    if out.exists() and any(out.iterdir()):
        print(f"refusing to overwrite non-empty {out}"); return 1
    shutil.copytree(template, out, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", ".venv", "*.pyc"))
    brief = pathlib.Path(a.brief).read_text()
    (out / "brief.yaml").write_text(brief)
    m = re.search(r'^customer:\s*"?([^"\n]*)"?', brief, re.M)
    name = m.group(1).strip() if m and m.group(1).strip() else "Customer"
    km = re.search(r'^\s*kind:\s*(\S+)', brief, re.M)
    kind = a.failure or (km.group(1) if km else "none")
    if kind in ("UNANSWERED", "", None): kind = "none"
    readme = out / "README.md"; readme.write_text(readme.read_text().replace("<Customer>", name).replace("<failure>", kind))
    # The failure is OFF by default so plain runs are clean traffic; the kind is recorded for the team.
    env = out / ".env.example"
    env.write_text(re.sub(r"^FAILURE_MODE=.*$", f"FAILURE_MODE=none\n# This scenario's planted failure is: {kind}. Turn it on with FAILURE_MODE={kind}", env.read_text(), flags=re.M))
    print(f"scaffolded {out}\n  skill={a.skill} customer={name} planted_failure={kind} (off by default)\n  next: customize '# CUSTOMIZE:' blocks, then: python shared/check_skeleton.py {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
