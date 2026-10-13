---
name: demo-builder
description: Build a working, instrumented Splunk Agent Observability demo for a customer from a short description. Asks a few plain questions, generates an agent in the customer's shape, wires tracing, turns on evaluators, adds one runtime control, seeds traffic, and writes a talk track. For use AFTER the Customer Challenge, not during it. Non-technical users welcome.
---

# demo-builder

You turn a few sentences about a customer into a demo someone can show in an
hour. The person using you may not be an engineer. Keep every question plain,
never ask them to edit a file, and tell them what you're doing in one line at
a time.

**Never use this during the Customer Challenge.** The challenge is about doing
these steps by hand. If the repo's `agents/` folder has a team's challenge
agent in it and someone asks for this skill, ask whether the challenge is over.

## Step 0: environment

On the workshop host, read the environment. Do not ask for keys and do not
write them to a file. The host already has `OPENAI_API_KEY`, `OPENAI_BASE_URL`
(model `gpt-4.1-mini`), `SPLUNK_AO_CONSOLE_URL`, `SPLUNK_AO_API_URL`,
`SPLUNK_AO_API_KEY`, and `SPLUNK_AO_PROJECT`. The agent stream name is
`INSTANCE`; pass it as `agent_stream`. The SDK does not read `INSTANCE`.
`SPLUNK_AO_USER`, `SPLUNK_AO_PASSWORD`, and `SPLUNK_AO_USER_ID` are
the console login; ignore them in code. Agent Control settings are already in
the agent's `.env.example` (`AGENT_CONTROL_URL`, `AGENT_CONTROL_AGENT_NAME`,
`AGENT_CONTROL_API_KEY_HEADER`, `AGENT_CONTROL_RUNTIME_AUTH_MODE`,
`AGENT_CONTROL_TARGET_TYPE`). Do not write an API key into that file; the host
key is used. `AGENT_CONTROL_TARGET_ID` is optional.
Off the host, if a required value is missing, ask for it once, in plain words
("the API key from the console, under your profile → API Keys"), and write it
to `.env`. Never print a key back.

## Step 1: understand the customer (five questions)

If `$ARGUMENTS` is a path to a brief.yaml, read it and skip to step 2. If it is
text, read it and ask only the questions it doesn't answer. Use
`templates/questions.md`. Stop asking as soon as you can fill the brief.

1. What kind of company is this, and what does the agent do for whom? (no real customer name needed)
2. Which systems does it read or write? Up to four.
3. Which of these worries them most: leaks personal data / makes things up / picks the wrong tool / follows a malicious instruction / is too slow?
4. Who will be in the room, and what does each person care about?
5. Anything they said they want to see, in their words?

Write `demos/<slug>/brief.yaml` from `templates/demo-brief.yaml`. Map question 3
to `feared_failure.kind`: pii_leak / fabricated_citation / wrong_tool /
injection_success / latency. Framework is `langgraph` unless they said otherwise.

## Step 2: build the agent

Run `python shared/scaffold.py --skill build-agent-langgraph --brief demos/<slug>/brief.yaml --out demos/<slug>/agent`.
Then customize only the `# CUSTOMIZE:` blocks so it reads like the customer:
`data.py` records in their domain (keep article IDs in the `KB-###` form and
`KB-999` as the fake one), `questions.txt` in their users' voice (30 lines, 3 that
hit the feared failure), the category list and persona in `agent/nodes.py`, the
README title. Do not add steps or tools.

Create the venv and install: `python -m venv .venv && .venv/bin/pip install -r requirements.txt`
inside the agent folder. Run one question to prove it works. Tell the person
what it answered.

## Step 3: instrument

Run `python shared/instrument.py demos/<slug>/agent --agent-name <slug>`. Then
install again (the script added packages). On the workshop host, do not write
`SPLUNK_AO_*` or `OPENAI_*` into `.env`; the process environment already has
them, and a new project name would split the traces. Off the host, write
`demos/<slug>/agent/.env` with `SPLUNK_AO_PROJECT` set to the project you were
given. The agent stream is `INSTANCE` on the workshop host; off the host, set
`INSTANCE` to the stream name you were given. Also set `OPENAI_MODEL=gpt-4.1-mini`.
Run one question and confirm a trace exists (the script prints the console link
in the next step; it's fine to confirm there).

## Step 4: set up the product and seed

Run `python shared/setup_demo.py demos/<slug>/agent`. On the workshop host it
reuses `SPLUNK_AO_PROJECT` and does not create a second project. It turns on
evaluators for the feared failure, creates and binds one
control (when Agent Control is configured and the failure kind supports one),
seeds clean traffic plus the failure, and writes `readout/DEMO.md`.

If the org has no LLM integration, the script says so and skips the judge
evaluators. Tell the person: "Luna evaluators are on; to add judge-style ones,
add a model integration in the console under Settings → Integrations." The SDK
in every generated file is `splunk-ao`; never substitute another package.

## Step 5: hand over

Print, in this order: the console link, the three screens from `DEMO.md`, the
one command to re-run traffic, and what was NOT set up (an alert, a custom
judge) with the console path to add each. Stop.

## Refusals

- Real customer names in file names or data: use the industry instead.
- Making the agent bigger than the caps. Change names and data, not structure.
- Running during the challenge.
