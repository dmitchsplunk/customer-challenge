# <Customer> agent skeleton (pure Python)

No framework. Three agents and a writer as plain functions, a hand-written
tool-calling loop against the model's API, three tools, mock data. **No observability code.** That part is yours,
and on this path you build every span by hand.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env     # model name only; OPENAI_API_KEY and OPENAI_BASE_URL are already set
python app.py "When is my next pay date?"
python run_batch.py 10
FAILURE_MODE=<failure> python run_batch.py 5   # this scenario's planted failure
```

## The planted failure

This scenario's planted failure is `<failure>`. It is off by default, so plain
runs are clean traffic. Turn it on with `FAILURE_MODE=<failure>` for one run or
in `.env`. Modes are listed in `failure.py`. Synthetic data only.

## Layout

| File | What |
|---|---|
| `app.py` | CLI chat. Calls `handle()`. |
| `run_batch.py` | Replays `questions.txt`, rotating through the users in `data.py` so per-user views have something to group. |
| `agents.py` | `triage_agent`, `knowledge_agent`, `action_agent` (the tool loop), `writer`, and `handle()`. Marked `# STEP:`. |
| `tools.py` | Tool functions and their JSON schemas. Marked `# TOOL:`. |
| `data.py` | Mock articles, records, screens. |
| `failure.py` | Planted failure switch. |

## Where the seams are

- `handle()` is one run of the agent. That is your trace.
- Each `*_agent` function is one agent. That is an agent span.
- `chat()` and the loop in `action_agent` are the model calls. Those are LLM spans; the response object carries token counts.
- `run_tool()` is every tool call. Those are tool spans.

## What you still have to do

These are steps 5 to 8 of the main README.

- Get traces into your project with the splunk-ao SDK: one trace per `handle()`, spans for agents, model calls, and tools.
- Tag every trace with the metadata the customer asked to filter by.
- Turn on the evaluators your design worksheet says, and no more.
- Stretch: write one custom judge in the customer's own definition of a bad answer.
- Make something act on the failure: one runtime control on the right step,
   or one alert that reaches someone outside the console. One is enough; both
   is better.
- Run the batch, flip the failure on, and make sure the above catches it.
- Show the console views from your worksheet.

Docs: https://agent-observability-docs.splunk.com (SDK: `pip install splunk-ao`)
