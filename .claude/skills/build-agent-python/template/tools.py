"""Tools as plain functions, plus the JSON schemas the model sees. Max 4. Each marked '# TOOL:'."""
import json, time
import data
from failure import active


# TOOL: open a screen
def open_screen(screen: str) -> dict:
    ok = screen in data.SCREENS
    return {"opened": screen if ok else None, "known_screens": data.SCREENS, "ok": ok}


# TOOL: start a workflow
def start_workflow(workflow: str, details: str = "") -> dict:
    ok = workflow in data.WORKFLOWS
    return {"started": workflow if ok else None, "details": details, "reference": "WF-48213" if ok else None, "ok": ok}


# TOOL: look up the user's own record
def lookup_my_record(user_id: str) -> dict:
    if active("latency"):
        time.sleep(6)
    return data.RECORDS.get(user_id) or {"error": f"no record for {user_id}"}


FUNCTIONS = {"open_screen": open_screen, "start_workflow": start_workflow, "lookup_my_record": lookup_my_record}
# CUSTOMIZE: the one tool that changes something. The planted wrong_tool failure forces it on requests that only asked a question.
WRITE_TOOL = "start_workflow"

# What the model sees. CUSTOMIZE descriptions if the customer's tools have obvious names.
SCHEMAS = [
    {"type": "function", "function": {"name": "open_screen", "description": "Open a named screen in the self-service app.",
        "parameters": {"type": "object", "properties": {"screen": {"type": "string", "enum": data.SCREENS}}, "required": ["screen"]}}},
    {"type": "function", "function": {"name": "start_workflow", "description": "Start a workflow with free-text details.",
        "parameters": {"type": "object", "properties": {"workflow": {"type": "string", "enum": data.WORKFLOWS}, "details": {"type": "string"}}, "required": ["workflow"]}}},
    {"type": "function", "function": {"name": "lookup_my_record", "description": "Return the requesting user's own record: next pay date, PTO balance, direct deposit status.",
        "parameters": {"type": "object", "properties": {"user_id": {"type": "string"}}, "required": ["user_id"]}}},
]


def run_tool(name: str, args: dict) -> str:
    fn = FUNCTIONS.get(name)
    return json.dumps(fn(**args) if fn else {"error": f"unknown tool {name}"})
