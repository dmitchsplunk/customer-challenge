#!/usr/bin/env python3
"""Set up the product side of a customer demo for an instrumented agent.

    python shared/setup_demo.py <agent dir> [--clean 12] [--failure 4] [--no-control] [--no-seed]

Reads the process environment (and <agent dir>/.env for anything not already
set) for SPLUNK_AO_* / AGENT_CONTROL_* / OPENAI_* and <agent dir>/brief.yaml
for the customer and the feared failure. Then:
  1. uses the existing SPLUNK_AO_PROJECT and the agent stream named by INSTANCE
  2. turns on evaluators matched to the feared failure
  3. creates one Agent Control control for that failure, a policy, binds it to the agent
  4. seeds traffic: clean runs plus runs with the planted failure
  5. writes <agent dir>/readout/DEMO.md with console links and a talk track

AFTER THE CHALLENGE ONLY.
"""
import argparse, asyncio, json, os, pathlib, random, re, subprocess, sys, time

BASE_EVALS = ["context_adherence_luna", "completeness_luna", "action_advancement_luna",
              "tool_selection_quality_luna", "prompt_injection_luna", "input_pii", "output_pii"]
BY_FAILURE = {
    "pii_leak": {"evals": [], "control": ("no_pii_in_reply", r"\b\d{3}-\d{2}-\d{4}\b|[\w.+-]+@[\w-]+\.[\w.]+",
                 "I've answered your question, but I can't include identifying details in this reply. If you need to confirm what's on file, use the Personal Info screen.")},
    "fabricated_citation": {"evals": [], "control": ("no_fabricated_article", None,
                 "I couldn't find a verified help article for that request. Rather than guess, please contact the support desk, or check the help center for the official steps.")},
    "injection_success": {"evals": [], "control": ("block_prompt_injection", r"(?i)ignore (your|all|previous|the) (instructions|rules)", None)},
    "wrong_tool": {"evals": [], "control": None},
    "wrong_category": {"evals": [], "control": None},
    "latency": {"evals": [], "control": None},
}


def load_env(d: pathlib.Path):
    env = {}
    for p in (d / ".env",):
        if p.exists():
            for line in p.read_text().splitlines():
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.split("=", 1); env[k.strip()] = v.strip()
    for k, v in env.items():
        os.environ.setdefault(k, v)
    return env


def yaml_get(text, key):
    m = re.search(rf'^\s*{key}:\s*"?([^"\n]*)"?\s*$', text, re.M); return m.group(1).strip() if m else ""


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("agent_dir"); ap.add_argument("--clean", type=int, default=12)
    ap.add_argument("--failure", type=int, default=4); ap.add_argument("--no-control", action="store_true"); ap.add_argument("--no-seed", action="store_true")
    a = ap.parse_args(); d = pathlib.Path(a.agent_dir).resolve(); load_env(d)
    if not os.environ.get("SPLUNK_AO_PROJECT"):
        print("missing SPLUNK_AO_PROJECT (the workshop host already exports it; do not create a project)"); return 1
    if not os.environ.get("INSTANCE"):
        print("missing INSTANCE. That variable is the agent stream name on this host. The SDK does not read it; pass it as agent_stream."); return 1
    hosted = bool(os.environ.get("SPLUNK_AO_CONSOLE_URL") and os.environ.get("SPLUNK_AO_API_KEY"))
    saas = bool(os.environ.get("SPLUNK_AO_REALM") and os.environ.get("SPLUNK_AO_O11Y_TOKEN"))
    if not (hosted or saas): print("set SPLUNK_AO_CONSOLE_URL + SPLUNK_AO_API_KEY (hosted) or SPLUNK_AO_REALM + SPLUNK_AO_O11Y_TOKEN (Observability Cloud)"); return 1
    if not (os.environ.get("OPENAI_API_KEY") and os.environ.get("OPENAI_BASE_URL")): print("OPENAI_API_KEY and OPENAI_BASE_URL must both be set (they are preset on the workshop host)"); return 1
    brief = (d / "brief.yaml").read_text() if (d / "brief.yaml").exists() else ""
    customer = yaml_get(brief, "customer") or d.name; kind = yaml_get(brief, "kind") or "none"
    slug = yaml_get(brief, "slug") or os.environ.get("AGENT_CONTROL_AGENT_NAME") or d.parent.name
    import httpx
    from splunk_ao.projects import get_project
    from splunk_ao.agent_streams import get_agent_stream, create_agent_stream, enable_evaluators

    # 1. project from the host, agent stream from INSTANCE. Do not create a second project.
    pname, sname = os.environ["SPLUNK_AO_PROJECT"], os.environ["INSTANCE"]
    proj = get_project(name=pname)
    if proj is None:
        print(f"project {pname!r} does not exist. Use the SPLUNK_AO_PROJECT already set on this host."); return 1
    stream = get_agent_stream(name=sname, project_id=str(proj.id)) or create_agent_stream(name=sname, project_id=str(proj.id))
    pid, sid = str(proj.id), str(stream.id); print(f"[1/5] project {pname} ({pid}) agent stream {sname} ({sid})")

    # 2. evaluators (Luna set always; the judge-style one only when the org has a model integration)
    want = list(BASE_EVALS) + BY_FAILURE.get(kind, {}).get("evals", [])
    has_integration = True
    if hosted:
        base = (os.environ.get("SPLUNK_AO_API_URL") or os.environ["SPLUNK_AO_CONSOLE_URL"].replace("console.", "api.")).rstrip("/")
        h = {os.environ.get("AGENT_CONTROL_API_KEY_HEADER", "Splunk-AO-API-Key"): os.environ["SPLUNK_AO_API_KEY"]}
        try: has_integration = bool(httpx.get(f"{base}/integrations", headers=h, timeout=30).json())
        except Exception: has_integration = True
    if has_integration: want.append("instruction_adherence")
    else: print("      no LLM integration on this org: skipping LLM-judge evaluators (Luna ones still run)")
    try:
        enabled = enable_evaluators(agent_stream_name=sname, project_name=pname, metrics=want)
        items = [{"name": n} for n in want]
        print(f"[2/5] evaluators: {want}")
    except Exception as exc:
        items = []; print(f"[2/5] evaluators: FAILED ({type(exc).__name__}: {str(exc)[:120]}). Turn them on in the console: agent stream -> Configure Evaluators.")

    # 3. control
    control_info = None
    spec = BY_FAILURE.get(kind, {}).get("control")
    ac_url = os.environ.get("AGENT_CONTROL_URL")
    if a.no_control or not spec or not ac_url:
        print(f"[3/5] control: skipped ({'no control for this failure kind' if not spec else 'Agent Control not configured'})")
    else:
        name, pattern, steer = spec
        if kind == "fabricated_citation":
            ids = sorted(set(re.findall(r'"id":\s*"([A-Z]+-\d{3})"', (d / "data.py").read_text())))
            real = [i for i in ids if not i.endswith("999")]; prefix = real[0].split("-")[0] if real else "KB"
            nums = "|".join(i.split("-")[1] for i in real); pattern = rf"\b{prefix}-(?!(?:{nums})\b)\d{{3}}\b"
        os.environ["AGENT_CONTROL_URL"] = ac_url
        key = os.environ.get("AGENT_CONTROL_API_KEY") or os.environ.get("SPLUNK_AO_API_KEY", ""); hdr = os.environ.get("AGENT_CONTROL_API_KEY_HEADER", "Splunk-AO-API-Key")
        agent_name = os.environ.get("AGENT_CONTROL_AGENT_NAME", slug); target = os.environ.get("AGENT_CONTROL_TARGET_ID")
        target_type = os.environ.get("AGENT_CONTROL_TARGET_TYPE", "log_stream")
        os.environ.setdefault("AGENT_CONTROL_RUNTIME_AUTH_MODE", "jwt")
        cname = f"{slug}_{name}"; polname = f"{slug}-guardrails-{int(time.time())%100000}"
        stage = "pre" if kind == "injection_success" else "post"; path = "input" if stage == "pre" else "output"
        action = {"decision": "steer", "steering_context": {"message": steer}} if steer else {"decision": "deny"}
        data = {"execution": "sdk", "enabled": True, "tags": ["demo", kind],
                "description": f"Demo control for {customer}: {kind}.",
                "scope": {"step_types": ["llm"], "step_names": ["write"], "stages": [stage]},
                "condition": {"selector": {"path": path}, "evaluator": {"name": "regex", "config": {"pattern": pattern}}}, "action": action}
        import agent_control
        from agent_control.client import AgentControlClient
        from agent_control import policies as pol, controls as ctl

        async def go():
            kw = {"target_type": target_type, "target_id": target} if target else {}
            agent_control.init(agent_name=agent_name, agent_description=f"{customer} demo agent", agent_version="1.0.0", **kw)
            res = await agent_control.list_controls(name=cname, limit=5); items_ = res.get("items") or res.get("controls") or []
            cid = next((c.get("id") or c.get("control_id") for c in items_ if c.get("name") == cname), None)
            if cid is None:
                cid = (await agent_control.create_control(name=cname, data=data)); cid = cid.get("control_id") or cid.get("id")
            async with AgentControlClient(base_url=ac_url, api_key=key, api_key_header=hdr) as client:
                p = await pol.create_policy(client, polname); polid = p.get("policy_id") or p.get("id")
                await pol.add_control_to_policy(client, polid, cid)
                await pol.assign_policy_to_agent(client, agent_name, polid)
                if target:
                    await ctl.clone_and_bind_control(client, cid, target_type="log_stream", target_id=target)
            return cid, polid
        cid, polid = asyncio.run(go()); control_info = (cname, cid, polid, action["decision"])
        print(f"[3/5] control {cname} (id {cid}) -> policy {polid} -> agent {agent_name}, action={action['decision']}")

    # 4. seed
    py = d / ".venv" / "bin" / "python"; py = str(py) if py.exists() else sys.executable
    if a.no_seed:
        print("[4/5] seed: skipped")
    else:
        users = ["E-10001", "E-10002", "E-10003"]; dcs = ["dc-east-1", "dc-west-1"]
        def run(n, failure, control_on=True):
            env = dict(os.environ, DEMO_USER_ID=random.choice(users), DEMO_DATA_CENTER=random.choice(dcs), FAILURE_MODE=failure)
            if not control_on: env["AGENT_CONTROL_DISABLED"] = "true"
            out = subprocess.run([py, "run_batch.py", str(n)], cwd=d, env=env, capture_output=True, text=True, timeout=1800)
            return [l for l in out.stdout.splitlines() if l.startswith("[")]
        clean = run(a.clean, "none")
        # the failure twice: with the control OFF so the evaluator catches it on the record,
        # and with the control ON so the audience sees it stopped at runtime.
        caught = run(a.failure, kind, control_on=False) if kind != "none" else []
        stopped = run(a.failure, kind, control_on=True) if (kind != "none" and control_info) else []
        print(f"[4/5] seeded {len(clean)} clean + {len(caught)} with {kind} (control off, evaluator catches) + {len(stopped)} with {kind} (control on, stopped)")

    # 5. readout
    console = (os.environ.get("SPLUNK_AO_CONSOLE_URL") or f"https://app.{os.environ.get('SPLUNK_AO_REALM','us1')}.signalfx.com").rstrip("/")
    rd = d / "readout"; rd.mkdir(exist_ok=True)
    lines = [f"# Demo talk track: {customer}", "", f"Project `{pname}`, agent stream `{sname}`.", f"Console: {console}  (project {pid}, agent stream {sid})", "",
             "## What is set up", f"- Traces from every run, tagged with user_id, data_center, channel, failure_mode.", f"- Evaluators: " + (", ".join(i['name'] for i in items) if items else "turn on in the console") + "."]
    if control_info: lines.append(f"- Agent Control: `{control_info[0]}` on the write step, action {control_info[3]}, bound through policy {control_info[2]}.")
    lines += ["", "## Three screens", "1. Trace list filtered to `failure_mode = " + kind + "`: the evaluator column shows the catch on the runs made with the control off.",
              "2. One trace opened: the full tree, the tool call, the reply, the evaluator rationale.",
              ("3. The same request with the control on: the reply rewritten or blocked, with the audit line." if control_info else "3. Metrics grouped by user_id and data_center: latency and tokens with no custom work."),
              "", "## Re-run", f"`cd {d}` then `python run_batch.py 10` for clean traffic, `FAILURE_MODE={kind} python run_batch.py 4` for the failure, `python app.py \"<question>\"` for one request live."]
    (rd / "DEMO.md").write_text("\n".join(lines) + "\n"); print(f"[5/5] readout: {rd/'DEMO.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
