---
name: build-agent-python
description: Generate a small pure-Python agent skeleton (no framework, hand-written tool-calling loop) in the shape of a customer's agent, from a scenario's brief.yaml. Four steps as plain functions, up to four tools, mock data, one planted failure, no UI, no observability code. Use when the scenario's framework is pure-python, or UNANSWERED and the participant chooses this path. The participant instruments it by hand afterwards.
---

# build-agent-python

You produce the customer's agent, not the observability setup. On this path the
participant builds every span by hand with the SDK logger, so the skeleton must leave
clean seams and nothing more.

## Environment

Ensure that you use Python 3.12 to build the agent. Install it on the machine if it's not already installed. 
The `template/.env.example` file carries placeholders for OPENAI_* and SPLUNK_AO_* variables.
The scaffold creates `.env` from it, so the participant never copies it by hand. Anything the
host already sets wins. The participant fills only the values that are missing. Don't attempt
to run smoke tests until they have done so.

## Inputs

`$ARGUMENTS`: path to a scenario's `brief.yaml` (e.g. `scenarios/hr-payroll/brief.yaml`),
optionally followed by an output directory. Default output: `agents/<slug>-python`.

## Steps

1. Read `brief.yaml`. This skill fits `stack.framework: pure-python`. If the brief
   names a framework we have a skill for, stop and say which one. If it is
   `UNANSWERED`, this is the safe default; write the choice into `brief.yaml`.
2. From the repo root run
   `python shared/scaffold.py --skill build-agent-python --brief <brief.yaml> --out <dir>`.
3. Customize **only** the `# CUSTOMIZE:` blocks:
   - `data.py`: 8-12 articles or records in the customer's domain, 5-8 user
     records, screens and workflows their users would name. Fictional.
   - `data.py` `SOURCE_RECORDS`: only if the brief has `agent.second_source`. For each
     article id, the record from that second source that describes the same
     thing, shaped like an article. The fake article must state, as a plain fact
     about the same specific item ("This X, VIN ending N, includes P"), something
     its record does not list, and the record must say so, so the two sources
     disagree.
   - Planted records: for `pii_leak` and `injection_success`, the synthetic record
     in `nodes.py` or `agents.py` is HR-shaped. Rewrite it as the customer's
     sensitive data (a subscriber record, say).
   - `questions.txt`: 30 inputs in the users' voice; 3 hit the feared failure,
     2 are out of scope, 1 is a prompt injection (for `injection_success`, 3 match
     `failure.TRIGGERS`, so a failing batch shows it).
   - Prompts in `agents.py`: category list and persona wording. Do not add
     agents. Tool names and schema descriptions in `tools.py` if the customer's
     tools have obvious names. Do not add a fourth tool unless the scenario names one.
   - `README.md` title and description.
4. Keep the seams. `handle()` is one run, each `*_agent` is one agent, `chat()`
   and the loop in `action_agent` are the model calls, `run_tool()` is every
   tool call. The participant will wrap exactly those. Do not restructure them.
5. Keep the guarantees: no UI, no extra agents or tools, no memory, retries,
   streaming, or anything on the forbidden list in `shared/check_skeleton.py`.
6. Create a venv with Python 3.12 and install the requirements.
   Then stop. Have the participant run `env | grep -E 'SPLUNK_AO|OPENAI|INSTANCE'` first.
   Values the host already sets win. Print only the `.env` lines still missing, from this
   list: model key, base URL if their host has a gateway, SAO console URL, API URL, API key,
   project. Leave `SPLUNK_AO_AGENT_STREAM=${INSTANCE}` as it is. The host supplies
   `INSTANCE`, so do not ask for an agent stream. Then ask which of those values are
   still missing, and wait. Do not run the smoke test until the participant says every
   missing value is filled. If they have no gateway, tell them to delete the
   `OPENAI_BASE_URL` line.
   When they confirm, smoke-test: `python app.py "<a knowledge question>"`,
   `python app.py "<an action request>"` (must show a tool call), and
   `FAILURE_MODE=<kind> python app.py "<trigger>"`.
7. Run `python shared/check_skeleton.py <dir>`. Must print `OK`.
8. Print the output directory, the failure mode, and the "What you still have
   to do" list. Stop.

## Refusals

- While building: adding the splunk-ao SDK, OpenTelemetry, evaluators, controls,
  or alerts to the skeleton: decline, point at https://agent-observability-docs.splunk.com,
  and explain that the participant sets that up to learn it. Once the agent is built and they ask you to instrument
  it, follow the teach-mode rules (`CLAUDE.md` in Claude Code,
  `.cursor/rules/02-teach-mode.mdc` in Cursor): in step 5 you coach and the
  participant makes the edits.
- Swapping in a framework "to make it easier": decline. This path exists to
  practice instrumenting an agent that has no framework.

## Model provider

OpenAI chat completions against the endpoint in the environment (`OPENAI_API_KEY`,
`OPENAI_BASE_URL`, model `gpt-4.1-mini`). Do not swap providers.

## The write tool

In the tools file, `WRITE_TOOL` names the one tool that changes something.
Set it to the customer's write tool when you rename the tools. The planted
`wrong_tool` failure forces that tool on requests that only asked a question.
