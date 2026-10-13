"""Tools the action step can call. Max 4. Each is marked '# TOOL:' for the skeleton check."""
import json, time
from langchain_core.tools import tool
import data
from failure import active


# TOOL: open a screen in the self-service app
@tool
def open_screen(screen: str) -> str:
    """Open a named screen in the employee self-service app for the user."""
    ok = screen in data.SCREENS
    return json.dumps({"opened": screen if ok else None, "known_screens": data.SCREENS, "ok": ok})


# TOOL: start a workflow
@tool
def start_workflow(workflow: str, details: str = "") -> str:
    """Start a workflow (time_off_request, address_change, timecard_correction, beneficiary_change) with free-text details."""
    ok = workflow in data.WORKFLOWS
    return json.dumps({"started": workflow if ok else None, "details": details, "reference": "WF-48213" if ok else None, "ok": ok})


# TOOL: look up the requesting user's own record
@tool
def lookup_my_record(user_id: str) -> str:
    """Return the requesting user's own record: next pay date, PTO balance, direct deposit status."""
    if active("latency"):
        time.sleep(6)
    rec = data.RECORDS.get(user_id)
    return json.dumps(rec or {"error": f"no record for {user_id}"})


TOOLS = [open_screen, start_workflow, lookup_my_record]
TOOLS_BY_NAME = {t.name: t for t in TOOLS}
