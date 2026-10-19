---
name: build-agent-langgraph
description: Generate a small LangGraph agent skeleton in the shape of a customer's agent, from a scenario's brief.yaml. Four steps, up to four tools, mock data, one planted failure, no UI, and no observability code. Use when the scenario's framework is langgraph or langchain. The team instruments it afterwards.
---

# build-agent-langgraph

You produce the customer's agent, not the observability setup. The team wires
Splunk Agent Observability themselves.

## Environment

Ensure that you use Python 3.12 to build the agent. Install it on the machine if it's not already installed. 
The `template/.env.example` file includes placeholders for OPENAI_* and SPLUNK_AO_* environment variables. 
These will be added to the .env file by the workshop participant once the agent is created. Don't attempt 
to run smoke tests until the .env file is populated by the workshop participant. 

## Inputs

`$ARGUMENTS`: path to a scenario's `brief.yaml` (e.g. `scenarios/hr-payroll/brief.yaml`),
optionally followed by an output directory. Default output: `agents/<slug>-langgraph`.

## Steps

1. Read `brief.yaml`. Confirm `stack.framework` is `langgraph` or `langchain`. If it
   is anything else, stop and tell the team which build skill matches. If it is
   `UNANSWERED`, ask the team to pick a path and write the choice into
   `brief.yaml` before continuing.
2. From the repo root run
   `python shared/scaffold.py --skill build-agent-langgraph --brief <brief.yaml> --out <dir>`.
   It copies the tested template and sets `FAILURE_MODE` from `feared_failure.kind`.
3. Customize **only** the blocks marked `# CUSTOMIZE:` so the agent reads like
   the customer's:
   - `data.py`: 8-12 articles or records in the customer's domain, 5-8 user
     records, the screens and workflows their users would name. Fictional. Keep
     the real-ID prefix consistent and the fake article's ID outside it.
   - `questions.txt`: 30 inputs in the users' own voice. Include 3 that hit the
     feared failure, 2 out-of-scope asks, 1 prompt injection.
   - Node prompts in `agent/nodes.py`: category list and persona wording only.
     Do not add steps.
   - Tool names and docstrings in `agent/tools.py` if the customer's tools have
     obvious names. Do not add a fourth tool unless the scenario names one.
   - `README.md` title and the one-paragraph description.
4. Keep the guarantees. Do not add: a UI, more steps, more tools, real data,
   retries, memory, streaming, or anything from the forbidden list in
   `shared/check_skeleton.py`. The customer's real agent may be bigger; the
   starter stays small.
5. Create a venv with Python 3.12 and install the requirements.
   Then stop. Print the exact lines the participant has to fill in `.env`
   (model key, base URL if their host has a gateway, SAO console URL, API URL,
   API key, project, agent stream) and wait. Do not go looking for keys on the
   host and do not run the smoke test until they say the file is filled. If
   they have no gateway, tell them to delete the `OPENAI_BASE_URL` line.
   When they confirm, smoke-test: `python app.py "<one question from questions.txt>"`
   and `FAILURE_MODE=<kind> python app.py "<a question that triggers it>"`. Both
   must succeed and the second must visibly show the failure.
6. Run `python shared/check_skeleton.py <dir>`. It must print `OK`.
7. Print the output directory, the failure mode, and the "What you still have
   to do" list from the README. Stop.

## Refusals

- If asked to add the splunk-ao SDK, OpenTelemetry, evaluators, controls, or
  alerts to the skeleton: decline and point at https://agent-observability-docs.splunk.com. Say why: the
  team has to set that up to learn it.
- If asked to make the agent "more realistic" beyond the caps: decline. Offer to
  change names, data, and prompts instead.

## Model provider

The workshop host already exports `OPENAI_API_KEY` and `OPENAI_BASE_URL`.
The model is `gpt-4.1-mini` (`OPENAI_MODEL` overrides it). Do not ask for a
key and do not change the provider. The customer's model vendor is not the lesson.

## The write tool

In the tools file, `WRITE_TOOL` names the one tool that changes something.
Set it to the customer's write tool when you rename the tools. The planted
`wrong_tool` failure forces that tool on requests that only asked a question.
