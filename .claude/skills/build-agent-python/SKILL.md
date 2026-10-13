---
name: build-agent-python
description: Generate a small pure-Python agent skeleton (no framework, hand-written tool-calling loop) in the shape of a customer's agent, from a scenario's brief.yaml. Four steps as plain functions, up to four tools, mock data, one planted failure, no UI, no observability code. Use when the scenario's framework is pure-python, or UNANSWERED and the team chooses this path. The team instruments it by hand afterwards.
---

# build-agent-python

You produce the customer's agent, not the observability setup. On this path the
team builds every span by hand with the SDK logger, so the skeleton must leave
clean seams and nothing more.

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
   - `questions.txt`: 30 inputs in the users' voice; 3 hit the feared failure,
     2 are out of scope, 1 is a prompt injection.
   - Prompts in `agents.py`: category list and persona wording. Do not add
     agents. Tool names and schema descriptions in `tools.py` if the customer's
     tools have obvious names. Do not add a fourth tool unless the scenario names one.
   - `README.md` title and description.
4. Keep the seams. `handle()` is one run, each `*_agent` is one agent, `chat()`
   and the loop in `action_agent` are the model calls, `run_tool()` is every
   tool call. The team will wrap exactly those. Do not restructure them.
5. Keep the guarantees: no UI, no extra agents or tools, no memory, retries,
   streaming, or anything on the forbidden list in `shared/check_skeleton.py`.
6. Create a venv with the host Python, install, and smoke-test. `OPENAI_API_KEY`
   and `OPENAI_BASE_URL` are already set; the model is `gpt-4.1-mini`. Run
   `python app.py "<a knowledge question>"`, `python app.py "<an action request>"`
   (must show a tool call), and `FAILURE_MODE=<kind> python app.py "<trigger>"`.
7. Run `python shared/check_skeleton.py <dir>`. Must print `OK`.
8. Print the output directory, the failure mode, and the "What you still have
   to do" list. Stop.

## Refusals

- Adding the splunk-ao SDK, OpenTelemetry, evaluators, controls, or alerts to
  the skeleton: decline, point at https://agent-observability-docs.splunk.com, explain that the team must
  set that up to learn it.
- Swapping in a framework "to make it easier": decline. This path exists to
  practice instrumenting an agent that has no framework.

## Model provider

OpenAI chat completions against the host endpoint (`OPENAI_API_KEY`,
`OPENAI_BASE_URL`, model `gpt-4.1-mini`). Do not swap providers.
