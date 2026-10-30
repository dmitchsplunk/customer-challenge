# <Customer> agent skeleton (LangGraph)

A small agent in the shape of the customer's. Four steps: intake,
route, resolve (articles or one tool call), write. Three tools. Mock data. No
UI. **No observability code.** That part is yours.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# .env was created in step 4 of the main README. Do not copy .env.example over it.
python app.py "How do I change my direct deposit?"
python run_batch.py 10   # traffic
FAILURE_MODE=<failure> python run_batch.py 5   # this scenario's planted failure
```

## The planted failure

This scenario's planted failure is `<failure>`. It is off by default, so plain
runs are clean traffic. Turn it on with `FAILURE_MODE=<failure>` for one run or
in `.env`. The modes are in `failure.py`. It exists so your evaluators and
controls have something to catch. Synthetic data only.

## Layout

| File | What |
|---|---|
| `app.py` | CLI chat. Builds the graph, calls it. |
| `run_batch.py` | Replays `questions.txt`, rotating through the users in `data.py` so per-user views have something to group. |
| `agent/graph.py` | The four-step graph. |
| `agent/nodes.py` | The steps, marked `# STEP:`. |
| `agent/tools.py` | The tools, marked `# TOOL:`. |
| `data.py` | Mock articles, records, screens. |
| `failure.py` | Planted failure switch. |

## What you still have to do

The skeleton does none of this; it is yours to do. These are steps 5 to 8 of the main README.

- Get traces into your project: instrument the graph with the splunk-ao SDK.
- Tag every trace with the metadata the customer asked to filter by.
- Turn on the evaluators your design worksheet says, and no more.
- Stretch: write one custom judge in the customer's own definition of a bad answer.
- Make something act on the failure: one runtime control on the right step,
   or one alert that reaches someone outside the console. One is enough; both
   is better.
- Run the batch, flip the failure on, and make sure the above catches it.
- Show the console views from your worksheet.

Docs: https://agent-observability-docs.splunk.com (SDK: `pip install splunk-ao`)
