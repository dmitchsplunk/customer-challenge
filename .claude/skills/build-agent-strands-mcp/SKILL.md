---
name: build-agent-strands-mcp
description: Generate a small Strands agent whose tools come from a bundled MCP server, in the shape of a customer's agent, from a scenario's brief.yaml. Advanced path, not used in the challenge. One agent, up to four MCP tools, mock data, one planted failure, no UI, no observability code. Use only when someone asks for the strands-mcp path. It is not used in the challenge.
---

# build-agent-strands-mcp

You produce the customer's agent and its MCP server, not the observability
setup. On this path there is no SDK to wire; Strands emits OpenTelemetry and the
team has to get the exporter, endpoint, headers, and convention mode right.
Leave those for the participant.

## Environment

Ensure that you use Python 3.12 to build the agent. Install it on the machine if it's not already installed. 
The `template/.env.example` file includes placeholders for OPENAI_* and SPLUNK_AO_* environment variables. 
These will be added to the .env file by the workshop participant once the agent is created. Don't attempt 
to run smoke tests until the .env file is populated by the workshop participant. 

## Inputs

`$ARGUMENTS`: path to a scenario's `brief.yaml` (e.g. `scenarios/hr-payroll/brief.yaml`),
optionally followed by an output directory. Default output: `agents/<slug>-strands-mcp`.

## Steps

1. Read `brief.yaml`. This skill fits `stack.framework: strands`. If the brief
   names LangGraph or pure Python, stop and say which skill matches. If
   `UNANSWERED`, ask the participant and write the choice into `brief.yaml`.
2. From the repo root run
   `python shared/scaffold.py --skill build-agent-strands-mcp --brief <brief.yaml> --out <dir>`.
3. Customize **only** the `# CUSTOMIZE:` blocks:
   - `data.py`: the mock records behind the customer's internal tool, 6-10 of
     each kind. Fictional.
   - `mcp_server.py`: tool names and descriptions to match the customer's MCP.
     Keep two reads and one write. Do not add a fourth unless the scenario names it.
   - `questions.txt`: 30 inputs in the users' voice; mix reads and a couple of
     writes; 3 hit the feared failure; 1 out-of-scope; 1 prompt injection.
   - `agent.py` system prompt persona wording. One agent. Do not add a second.
   - `README.md` title and description.
4. Keep the guarantees: no UI, one agent, no extra tools, nothing from the
   forbidden list in `shared/check_skeleton.py`. In particular, do not set any
   `OTEL_*` variables or call `StrandsTelemetry`. That is the participant's job.
5. Create a venv with the host Python, install, and smoke-test. `OPENAI_API_KEY`
   and `OPENAI_BASE_URL` are already set; the model is `gpt-4.1-mini`. Run
   a read question, a write request (must show the write tool), and
   `FAILURE_MODE=<kind> python app.py "<trigger>"`.
6. Run `python shared/check_skeleton.py <dir>`. Must print `OK`.
7. Print the output directory, the failure mode, and the "What you still have
   to do" list. Stop.

## Refusals

- While building: configuring OpenTelemetry export, the splunk-ao SDK, evaluators,
  controls, or alerts in the skeleton: decline, point at
  https://agent-observability-docs.splunk.com, say why. Once it is built and they
  ask you to instrument it, follow the teach-mode instructions (`CLAUDE.md` in Claude Code, `.cursor/rules/02-teach-mode.mdc` in Cursor): explain each edit before you make it.
- Replacing the MCP server with in-process tools "to simplify": decline. The MCP
  boundary is what the customer cares about.

## Coach notes (do not print to the participant)

Things participants will hit on this path:
- Messages land as span events, not attributes, unless the convention flag is
  set; the console then shows empty inputs and outputs.
- The exporter appends `/v1/traces` to the base endpoint; the base must end in
  `/otel` or nothing lands.
- A trace whose root span never arrives stays "Partial" forever.
- strands-agents older than 1.48 lacks the attributes-only flag.

## Model provider

OpenAI through Strands' OpenAI model, using the host's `OPENAI_API_KEY` and
`OPENAI_BASE_URL`. The model is `gpt-4.1-mini`. Do not swap providers.
