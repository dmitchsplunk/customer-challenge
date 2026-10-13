#!/usr/bin/env python3
"""Add Splunk Agent Observability wiring (the splunk-ao SDK) to a scaffolded LangGraph agent.

    python shared/instrument.py <agent dir> [--agent-name NAME]

Deterministic, idempotent. Patches app.py (SDK callback + metadata + steer/deny
handling), agent/graph.py (Agent Control on the write step), adds
agent/control_setup.py, and appends the needed packages to requirements.txt.

AFTER THE CHALLENGE ONLY. During the challenge the team does this by hand.
"""
import argparse, pathlib, re, sys

MARK = "# --- SAO instrumentation (added by shared/instrument.py) ---"

APP_ASK = '''
%s
from splunk_ao import SplunkAOLogger  # noqa: E402
from splunk_ao.handlers.langchain import SplunkAOCallback  # noqa: E402

USER_ID = os.getenv("DEMO_USER_ID", "E-10001")
DATA_CENTER = os.getenv("DEMO_DATA_CENTER", "dc-east-1")
CHANNEL = os.getenv("DEMO_CHANNEL", "web")


def ask(graph, request: str, user_id: str = USER_ID) -> dict:
    logger = SplunkAOLogger(project=os.environ["SPLUNK_AO_PROJECT"], agent_stream=os.environ["INSTANCE"])
    cb = SplunkAOCallback(splunk_ao_logger=logger, start_new_trace=True, flush_on_chain_end=True)
    cfg = {"callbacks": [cb], "metadata": {"user_id": user_id, "data_center": DATA_CENTER,
                                           "channel": CHANNEL, "failure_mode": mode()}}
    try:
        return graph.invoke({"request": request, "user_id": user_id}, config=cfg)
    except Exception as exc:
        try:
            from agent_control import ControlSteerError, ControlViolationError
        except ImportError:
            raise
        if isinstance(exc, ControlSteerError):
            name = getattr(exc, "control_name", "control")
            steering = getattr(exc, "steering_context", None)
            steering = steering if isinstance(steering, str) else str(steering or "")
            return {"ticket": {"category": "n/a"}, "route": "steered",
                    "reply": f"{steering}\\n\\n[Agent Control {name} rewrote this reply before it reached you.]"}
        if isinstance(exc, ControlViolationError):
            name = getattr(exc, "control_name", "control")
            return {"ticket": {"category": "n/a"}, "route": "blocked",
                    "reply": f"I can't share that reply. A person will follow up.\\n\\n[Agent Control {name} blocked this reply.]"}
        raise
''' % MARK

GRAPH_PATCH = '''
%s
import os as _os
if _os.getenv("AGENT_CONTROL_DISABLED", "").lower() not in ("1", "true", "yes"):
    from . import control_setup  # noqa: F401
    from agent_control import control, ControlSteerError, ControlViolationError

    _controlled_write = control(step_name="write")(write)

    def write(state):  # noqa: F811  (wraps the template's write step)
        """Run the write step under Agent Control. A steer or deny becomes the
        step's output, so the trace completes and shows what the user saw."""
        try:
            return _controlled_write(state)
        except ControlSteerError as exc:
            steering = getattr(exc, "steering_context", None)
            steering = steering if isinstance(steering, str) else str(steering or "")
            return {"reply": f"{steering}\\n\\n[Agent Control {getattr(exc, 'control_name', 'control')} rewrote this reply before it reached you.]"}
        except ControlViolationError as exc:
            return {"reply": f"I can't share that reply. A person will follow up.\\n\\n[Agent Control {getattr(exc, 'control_name', 'control')} blocked this reply.]"}
''' % MARK

CONTROL_SETUP = '''"""Register this agent with Agent Control on import. Added by shared/instrument.py."""
import logging, os
import agent_control

AGENT_NAME = os.environ.get("AGENT_CONTROL_AGENT_NAME", "%s")
_url = os.environ.get("AGENT_CONTROL_URL")
if _url:
    os.environ["AGENT_CONTROL_URL"] = _url
os.environ.setdefault("AGENT_CONTROL_API_KEY_HEADER", "Splunk-AO-API-Key")
os.environ.setdefault("AGENT_CONTROL_RUNTIME_AUTH_MODE", "jwt")
os.environ.setdefault("AGENT_CONTROL_TARGET_TYPE", "log_stream")
_target = os.environ.get("AGENT_CONTROL_TARGET_ID")
_target_type = os.environ.get("AGENT_CONTROL_TARGET_TYPE", "log_stream")

AGENT = None
if os.getenv("AGENT_CONTROL_DISABLED", "").lower() not in ("1", "true", "yes"):
    try:
        kw = {"target_type": _target_type, "target_id": _target} if _target else {}
        AGENT = agent_control.init(agent_name=AGENT_NAME, agent_description="Customer demo agent", agent_version="1.0.0", **kw)
    except Exception as exc:
        logging.getLogger(__name__).warning("Agent Control init failed (%%s); controls will no-op", exc)
'''


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("agent_dir"); ap.add_argument("--agent-name", default=None)
    a = ap.parse_args(); d = pathlib.Path(a.agent_dir).resolve()
    app = d / "app.py"; graph = d / "agent" / "graph.py"; req = d / "requirements.txt"
    if not (app.exists() and graph.exists()):
        print("not a LangGraph skeleton (need app.py and agent/graph.py)"); return 1
    name = a.agent_name or d.name
    s = app.read_text()
    if MARK in s:
        print("app.py already instrumented")
    else:
        m = re.search(r'\nUSER_ID = os\.getenv\("DEMO_USER_ID", "E-10001"\)\n\n\ndef ask\(graph, request: str, user_id: str = USER_ID\) -> dict:\n    return graph\.invoke\(\{"request": request, "user_id": user_id\}\)\n', s)
        if not m:
            print("app.py does not match the template; refusing to guess"); return 1
        s = s[:m.start()] + APP_ASK + s[m.end():]
        app.write_text(s); print("app.py: callback, metadata, steer/deny handling")
    g = graph.read_text()
    if MARK in g:
        start = g.index("\n" + MARK); end = g.index("\n\n\ndef build_graph", start)
        g = g[:start] + GRAPH_PATCH.rstrip("\n") + g[end:]
        graph.write_text(g); print("agent/graph.py: Agent Control block refreshed")
    else:
        g = g.replace("from .state import State\n", "from .state import State\n" + GRAPH_PATCH, 1)
        graph.write_text(g); print("agent/graph.py: Agent Control on the write step")
    cs = d / "agent" / "control_setup.py"
    if not cs.exists():
        cs.write_text(CONTROL_SETUP % name); print("agent/control_setup.py: added")
    r = req.read_text() if req.exists() else ""
    add = [p for p in ("splunk-ao[langchain]>=0.5", "agent-control-sdk>=8.4", "httpx>=0.27") if p.split(">=")[0].split("[")[0] not in r]
    if add:
        req.write_text(r.rstrip("\n") + "\n" + "\n".join(add) + "\n"); print("requirements.txt:", ", ".join(add))
    env = d / ".env.example"; e = env.read_text() if env.exists() else ""
    if "SPLUNK_AO_PROJECT" not in e:
        e += ("\n# --- Splunk Agent Observability (splunk-ao SDK) ---\n"
              "# On the workshop host these are already exported. Do not assign them\n"
              "# here: an empty value or a new project name sends traces to the wrong place.\n"
              "# SDK: SPLUNK_AO_CONSOLE_URL, SPLUNK_AO_API_URL, SPLUNK_AO_API_KEY, SPLUNK_AO_PROJECT\n"
              "# Agent stream name: INSTANCE (pass it to the logger; the SDK does not read it)\n"
              "# Console login only; the SDK does not read these: SPLUNK_AO_USER, SPLUNK_AO_PASSWORD, SPLUNK_AO_USER_ID\n"
              "# Agent Control values live in this file already. Do not add an API key.\n")
        env.write_text(e); print(".env.example: observability variables")
    print(f"done: {d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
