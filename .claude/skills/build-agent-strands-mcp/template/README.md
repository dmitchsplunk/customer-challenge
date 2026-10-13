# <Customer> agent skeleton (Strands + MCP)

A Strands agent whose tools all come from a small MCP server the skeleton also
provides. One agent, three MCP tools (two reads, one write), mock data, no UI.
**No observability code.** On this path Strands emits OpenTelemetry natively;
the team configures where it goes and in what shape. That is the lesson, and it
has sharp edges on purpose.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env     # model name only; OPENAI_API_KEY and OPENAI_BASE_URL are already set
python app.py "Which hosts are degraded right now?"
python run_batch.py 10
FAILURE_MODE=<failure> python run_batch.py 5   # this scenario's planted failure
```

The MCP server starts as a subprocess over stdio each run. To poke it directly:
`python mcp_server.py` and speak MCP, or point any MCP-capable harness at it.

## The planted failure

This scenario's planted failure is `<failure>`, off by default; turn it on with
`FAILURE_MODE=<failure>`. Modes: `wrong_tool` (the right tool is
missing from the list), `ambiguous_tools` (two read tools describe themselves
identically, so harnesses pick differently), `stale_result` (search returns
yesterday's data), `pii_leak`, `latency`, `injection_success`. Synthetic only.

## Layout

| File | What |
|---|---|
| `app.py` | CLI chat. |
| `run_batch.py` | Replays `questions.txt`, rotating through the users in `data.py` so per-user views have something to group. |
| `agent.py` | The Strands agent, connected to the MCP server. Marked `# STEP:`. |
| `mcp_server.py` | The MCP server, three tools marked `# TOOL:`. |
| `data.py` | Mock events, alerts, hosts. |
| `failure.py` | Planted failure switch. |

## What you still have to do

1. Get traces into your project. Strands speaks OpenTelemetry; you set the
   exporter, the endpoint, the headers, and the semantic-convention mode. Read
   the docs carefully: where messages land (attributes vs events) and what the
   endpoint path is both matter.
2. Make sure every MCP call shows as a tool span with its arguments and result.
3. Tag every trace with the metadata the customer asked to filter by (user, team, harness).
4. Turn on the evaluators your design worksheet says, tool-focused ones first.
5. Run the same questions through a second harness against this same MCP server
   and compare tool choices in an experiment. That is what the customer asked for.
6. Make something act on the failure: one runtime control on the write tool,
   or one alert that reaches someone outside the console.
7. Run the batch, flip the failure on, make sure the above catches it.
8. Build the three-screen demo from the worksheet.

Docs: https://agent-observability-docs.splunk.com (SDK: `pip install splunk-ao`)
