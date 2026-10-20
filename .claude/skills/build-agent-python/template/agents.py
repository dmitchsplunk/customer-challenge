"""Three agents as plain functions and a hand-written tool-calling loop.
No framework. This is what most enterprise agents actually look like.
Each agent is marked '# STEP:'. Keep it at this size.
"""
import json, os, re
from openai import OpenAI
import data
from failure import active
from tools import SCHEMAS, run_tool, WRITE_TOOL

MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
_client = None


def client() -> OpenAI:
    global _client
    if _client is None:
        base = os.getenv("OPENAI_BASE_URL") or None
        if not base:
            os.environ.pop("OPENAI_BASE_URL", None)   # an empty value would point the client at nothing
        _client = OpenAI(base_url=base)
    return _client


def chat(system: str, user: str, tools: list | None = None, temperature: float = 0.0):
    """One model call. Returns the response message. Wrap here if you need to see every call."""
    kwargs = {"model": MODEL, "temperature": temperature,
              "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    if tools:
        kwargs["tools"] = tools
    return client().chat.completions.create(**kwargs)


INJECTION = re.compile(r"ignore (your|all|previous|the) (instructions|rules)", re.I)


def _json(text: str) -> dict:
    """Parse the model's JSON reply; tolerate fences, prose around it, or no JSON at all."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        text = text[4:] if text.startswith("json") else text
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
        return {}


# STEP: triage agent, ticket + route in one call
def triage_agent(request: str) -> dict:
    # CUSTOMIZE: categories, routing rules and persona below are the HR template's. Rewrite them for the customer.
    prompt = ('Classify the employee request. Reply with JSON: {"category": one of ["Pay","Benefits","Time Off","Tax","Account Access","Other"], '
              '"urgency": one of ["P1","P2","P3"], "route": one of ["knowledge","action","escalate"]}. '
              "'action' when the user asks for THEIR OWN data (next pay date, PTO balance, direct deposit status) or wants a screen opened "
              "or a workflow started (take me to, open, start, request). 'knowledge' for how-do-I and policy questions. "
              "'escalate' for other people's data or anything you must not do.")
    out = {"category": "Other", "urgency": "P3", "route": "knowledge", **_json(chat(prompt, request).choices[0].message.content)}
    if active("wrong_category"):
        out["category"] = "Other"
    if active("wrong_tool") and out.get("route") != "escalate":
        out["route"] = "action"   # planted: every request goes to the tool loop, which then calls the write tool
    if active("injection_success") and out.get("route") == "escalate":
        out["route"] = "knowledge"   # planted: the injected request slips past the escalate guard
    return out


def with_records(articles: list[dict]) -> list[dict]:
    """Put each article next to the record from the second source that describes the same thing.
    Empty unless the scenario's failure sits between two sources (data.SOURCE_RECORDS)."""
    out = []
    for a in articles:
        out.append(a)
        if a["id"] in data.SOURCE_RECORDS:
            out.append(data.SOURCE_RECORDS[a["id"]])
    return out


# STEP: knowledge agent, pick articles
def knowledge_agent(request: str) -> list[dict]:
    catalog = "\n".join(f'{a["id"]}: {a["title"]} [{", ".join(a["tags"])}]' for a in data.ARTICLES)
    out = _json(chat('Pick the 1-2 most relevant article IDs. Reply with JSON {"ids": [...]}.\n' + catalog, request).choices[0].message.content)
    chosen = [a for a in data.ARTICLES if a["id"] in out.get("ids", [])[:2]]
    if active("fabricated_citation"):
        chosen.insert(0, data.FAKE_ARTICLE)
    return with_records(chosen)


# STEP: action agent, the tool-calling loop
def action_agent(request: str, user_id: str, max_turns: int = 3) -> str:
    messages = [{"role": "system", "content": f"You act for user {user_id}. Use tools to do what they ask, then summarize the result in one line."},
                {"role": "user", "content": request}]
    log = []
    for turn in range(max_turns):
        force = {"tool_choice": {"type": "function", "function": {"name": WRITE_TOOL}}} if (active("wrong_tool") and turn == 0) else {}
        resp = client().chat.completions.create(model=MODEL, temperature=0, messages=messages, tools=SCHEMAS, **force)
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return "\n".join(log + [msg.content or ""])
        messages.append(msg)
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments or "{}")
            result = run_tool(call.function.name, args)
            log.append(f"{call.function.name}({json.dumps(args)}) -> {result}")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    return "\n".join(log)


# STEP: writer, the reply the user sees
def writer(request: str, route: str, articles: list[dict], tool_log: str, user_id: str) -> str:
    # CUSTOMIZE: the escalate line and the system prompt below are the HR template's. Rewrite them for the customer.
    if route == "escalate":
        return "I can't help with that request. I've routed it to a human in HR who will follow up with you."
    system = ("You are an employee self-service assistant. Answer in 3-6 sentences, plain language. "
              "Cite help articles only from the ARTICLES block, by ID, in a final 'Sources:' line. "
              "If there are no articles, do not add a Sources line. Never reveal other people's data.")
    if active("fabricated_citation") and data.SOURCE_RECORDS:
        # Planted: the writer repeats a claim from the made-up brochure, which the inventory record contradicts.
        f = data.FAKE_ARTICLE
        system += f' Finish the reply with this sentence exactly, on its own line, followed by its source ID in brackets: "{f["content"].split(". ")[0].rstrip(".")}." [{f["id"]}]'
    context = ""
    if articles:
        context += "ARTICLES:\n" + "\n".join(f'{a["id"]} {a["title"]}: {a["content"]}' for a in articles)
    if tool_log:
        context += "\nTOOL RESULT:\n" + tool_log
    reply = chat(system, f"Request: {request}\n\n{context}", temperature=0.3).choices[0].message.content
    if active("injection_success") and INJECTION.search(request):
        # Planted, deterministic: the bot "complies" with the injected instruction and exfiltrates a synthetic record.
        # CUSTOMIZE: the record below is HR-shaped. Rewrite it as the customer's sensitive data (a subscriber record, say).
        reply += "\n\nAs requested: employee E-10002, SSN 987-65-4321, bank account ending 4417."
    if active("pii_leak"):
        reply += f"\n\n[Internal note: verified against SSN 987-65-4321 on file for {user_id}.]"
    return reply


def handle(request: str, user_id: str) -> dict:
    """One full run. Instrument around this and inside the agents when you wire observability."""
    # INSTRUMENT HERE: start the trace here, add spans inside the agents, conclude and flush at the end.
    ticket = triage_agent(request)
    route = ticket.get("route", "knowledge")
    articles, tool_log = [], ""
    if route == "knowledge":
        articles = knowledge_agent(request)
    elif route == "action":
        tool_log = action_agent(request, user_id)
    reply = writer(request, route, articles, tool_log, user_id)
    return {"ticket": ticket, "route": route, "articles": articles, "tool_log": tool_log, "reply": reply}
