"""Worked example for coaches: one runtime control on the agent's reply step.

Regex for a US SSN in the reply, post stage, action = steer with a safe
message. Attached to a policy, policy bound to the agent by name. Needs
AGENT_CONTROL_URL and AGENT_CONTROL_API_KEY (or SPLUNK_AO_API_KEY) in .env.
Run once from the agent folder:
    python ../../coaching/control-example.py
Then wrap the reply step with `@control(step_name="write")` from `agent_control`
and catch `ControlSteerError` / `ControlViolationError` around the graph call.
Show this to a team only after they have tried; it is a reference, not a shortcut.
"""
import asyncio, os, sys
from dotenv import load_dotenv
load_dotenv()
import agent_control
from agent_control.client import AgentControlClient
from agent_control import policies as ac_policies

AGENT_NAME = os.environ.get("AGENT_CONTROL_AGENT_NAME", "my-team-agent")
POLICY_NAME = os.environ.get("AGENT_CONTROL_POLICY_NAME", f"{AGENT_NAME}-guardrails-v1")
CONTROL_NAME = os.environ.get("AGENT_CONTROL_CONTROL_NAME", f"{AGENT_NAME}_no_ssn_in_reply")
CONTROL = {
    "execution": "sdk", "enabled": True, "tags": ["workshop", "pii"],
    "description": "Regex on the write step output: any SSN pattern in a reply is rewritten before the employee sees it.",
    "scope": {"step_types": ["llm"], "step_names": ["write"], "stages": ["post"]},
    "condition": {"selector": {"path": "output"}, "evaluator": {"name": "regex", "config": {"pattern": r"\b\d{3}-\d{2}-\d{4}\b"}}},
    "action": {"decision": "steer", "steering_context": {"message": (
        "I've answered your question, but I can't include identifying details in this reply. "
        "If you need to confirm what's on file, open Profile > Personal Info in self-service.")}},
}

async def main():
    url = os.environ["AGENT_CONTROL_URL"]
    os.environ["AGENT_CONTROL_URL"] = url
    key = os.environ.get("AGENT_CONTROL_API_KEY") or os.environ["SPLUNK_AO_API_KEY"]; hdr = os.environ.get("AGENT_CONTROL_API_KEY_HEADER", "Galileo-API-Key")
    os.environ.setdefault("AGENT_CONTROL_API_KEY", key); os.environ.setdefault("AGENT_CONTROL_API_KEY_HEADER", hdr)
    print("server:", url)
    agent_control.init(agent_name=AGENT_NAME, agent_description="Employee self-service assistant (workshop)", agent_version="1.0.0")
    res = await agent_control.list_controls(name=CONTROL_NAME, limit=5)
    items = res.get("items") or res.get("controls") or []
    cid = next((c.get("id") or c.get("control_id") for c in items if c.get("name") == CONTROL_NAME), None)
    if cid is None:
        r = await agent_control.create_control(name=CONTROL_NAME, data=CONTROL); cid = r.get("control_id") or r.get("id"); print("created control", cid)
    else:
        print("reused control", cid)
    async with AgentControlClient(base_url=url, api_key=key, api_key_header=hdr) as client:
        try:
            r = await ac_policies.create_policy(client, POLICY_NAME); pid = r.get("policy_id") or r.get("id"); print("created policy", pid)
        except Exception as exc:
            print("policy create failed:", str(exc)[:120]); return 1
        await ac_policies.add_control_to_policy(client, pid, cid); print("attached control", cid, "to policy", pid)
        await ac_policies.assign_policy_to_agent(client, AGENT_NAME, pid); print("bound policy", pid, "to agent", AGENT_NAME)
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
