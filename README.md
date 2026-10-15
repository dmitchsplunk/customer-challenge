# Start here

## What this is

Over two days you act as the solutions engineer for one customer, written up as
a scenario. Four scenarios are offered, and the facilitator assigns one to each
person. Your team works on the same scenario. Each of you builds in your own
environment and produces your own deliverable.

This is an individual exercise in a group setting. Your team is there to
discuss ideas with you, not to do the work for you. Your coach guides you and
does not do the work for you.

Your goal is to finish with two things. The first is an agent that shows the
customer's use case. The second is a Splunk Agent Observability configuration
that meets the customer's requirements.

At the end you show what you set up, in the agent and in Splunk Agent
Observability, to your coach and team. This is a team-only show and tell. It is
not an L2 certification demo. After the bootcamp you record a full
customer-facing demo of your agent and configuration to complete L2. The
session gives more detail.

The agent is given to you and kept small. What you set up in the product, and
how well it answers what the customer said, is the whole exercise.

Naming: the product is Splunk Agent Observability (SAO). The Python SDK is
`splunk-ao` and the docs are at <https://agent-observability-docs.splunk.com>.
What the SDK calls an agent stream is the bucket of traces inside a project;
some console screens still say log stream. Same thing.

## Rules of the road

- Spend your time on the product and the customer, not on the agent. The agent
  is capped at four steps and four tools; `shared/check_skeleton.py` counts them.
- You may use Claude Code or Cursor to help write the instrumentation. You
  must be able to explain every line at the show-and-tell.
- If the scenario says the customer didn't ask for it, it isn't in your demo.
- Between the two blocks, coaches answer in the workshop channel the facilitator
  names, within 30 minutes. In the room, just ask. They won't write your code.
- The `demo-builder` skill in this repo is for after the challenge. Using it
  during the challenge defeats the exercise, and the coaches will notice.

## Before day one

Ensure that Cursor or Claude is installed on your machine.

## Day one: Discover, Design, Build (about two hours)

### Step 1. Read the scenario (10 minutes)

Read `scenarios/<your scenario>/SCENARIO.md` twice. Mark the three to five
sentences the customer said that you think the demo must answer. If the
customer didn't say something, you don't know it; don't invent it for the demo.

**Done when:** you have marked the quotes your demo must answer, and your group agrees they are the right ones.

### Step 2. Fill the design worksheet (30 minutes)

Fill in `worksheets/design-worksheet.md`. Three to five rows. Each row starts
with a quote, then what you'll show, which product feature does it, and how
you'll set it up. Below the table: the three screens you'll show, the metadata
you'll tag on every trace, and the build path (the scenario's framework tells
you which build skill).

Keep it next to this README for now, as `worksheets/my-worksheet.md`. Once the
agent folder exists in step 4, move it to `agents/<your folder>/readout/worksheet.md`.

**Done when:** you have reviewed the worksheet with your team and removed
anything the customer didn't ask for.

### Step 3. Prepare the environment (20 minutes)

Access the Splunk Show event by clicking the link provided by your workshop
instructor. You'll need to sign in using your Cisco.com account.

We've prepared an Ubuntu Linux instance in AWS/EC2 for each attendee. To get
the details of your EC2 instance from the Splunk Show event:

- Click **Enroll event** on the top-right corner.
- Then look near the bottom of the page for your EC2 instance details.

Using a terminal window, run the SSH command from Splunk Show, for example
`ssh -p 2222 splunk@<ip address>`. When it asks for a password, use the
**second** SSH password listed for your instance.

The workshop requires Python 3.12+, so run the following command using the
terminal to install Python 3.12 on the EC2 instance:

```bash
sudo apt-get update && sudo apt-get install -y python3.12 python3.12-venv
```

Navigate to the home directory, then clone the GitHub repository where the
Customer Challenge materials are stored:

```bash
cd ~
git clone https://github.com/dmitchsplunk/customer-challenge.git
cd customer-challenge
```

Then, use Claude or Cursor to SSH to the EC2 instance using the information
from Splunk Show.

Refer to [CLAUDE-SETUP.md](environment/CLAUDE-SETUP.md) or
[CURSOR-SETUP.md](environment/CURSOR-SETUP.md) for detailed instructions.

### Step 4. Generate the agent (30 minutes)

In this step, we'll use AI to build an agent using the provided skills.

Using Claude Code, this can be achieved via the following prompt:

```text
/build-agent-<path> scenarios/<your scenario>/brief.yaml
```

Fill in the appropriate path and scenario name before running the command. For
example:

```text
/build-agent-langgraph scenarios/auto-retail/brief.yaml
```

In Cursor, use the following prompt instead:

```text
build the agent for scenarios/<your scenario>/brief.yaml on the <path> path
```

For example:

```text
Please build the agent for scenarios/auto-retail/brief.yaml on the langgraph path
```

A few minutes later you have a folder under `agents/` with a working agent,
mock data, 30 realistic inputs, and one planted failure taken from the
scenario. The skill creates the virtual environment (venv), installs, and runs
one question; its README shows how to do that yourself if anything failed. The
failure is off by default. It has no observability code in it.

Once the agent is built, open the `agents/<scenario name>/.env` file for
editing, and add the following environment variables, using the values provided
by your facilitator:

```text
OPENAI_API_KEY=provided_by_facilitator
OPENAI_BASE_URL=provided_by_facilitator
SPLUNK_AO_CONSOLE_URL=https://console.multitenant.sao.splunkcloud.com
SPLUNK_AO_API_URL=https://api.multitenant.sao.splunkcloud.com
SPLUNK_AO_API_KEY=provided_by_facilitator
SPLUNK_AO_PROJECT=provided_by_facilitator
SPLUNK_AO_AGENT_STREAM=${INSTANCE}
```

**Done when:** `python app.py "<a question>"` answers, and
`FAILURE_MODE=<the scenario's failure> python app.py "<a question>"` shows the
failure.

### Step 5. Instrument it and get the first trace in (30 minutes)

This is yours to do, from the docs. Pointers, not answers:

- `pip install "splunk-ao[langchain]"` in the agent's venv (plain `splunk-ao`
  on the Python path).
- The SDK reads `SPLUNK_AO_CONSOLE_URL`, `SPLUNK_AO_API_URL`,
  `SPLUNK_AO_API_KEY`, and `SPLUNK_AO_PROJECT` from the environment. Use that
  project. The agent stream name is `INSTANCE`. The SDK does not read it, so
  pass `agent_stream=os.environ["INSTANCE"]` when you create the logger. Do not
  create a project, and do not put the console login (`SPLUNK_AO_USER`,
  `SPLUNK_AO_PASSWORD`, `SPLUNK_AO_USER_ID`) in the agent.
- The agent calls `gpt-4.1-mini` through `OPENAI_API_KEY` and
  `OPENAI_BASE_URL`. Those are already set. Do not clear them in `.env`.
- LangGraph path: the LangChain callback,
  <https://agent-observability-docs.splunk.com/sdk-api/third-party-integrations/langchain>.
  Attach it on the graph call, `graph.invoke(..., config={"callbacks": [cb], ...})`,
  not on the `ChatOpenAI` object. On the LLM you only get model spans; on the
  invoke you get the whole tree, one trace per request, and a place to put
  your metadata.
- Python path: the logger,
  <https://agent-observability-docs.splunk.com/sdk-api/logging/splunk-ao-logger>
  (start a trace, add agent, LLM and tool spans, conclude, flush) around the
  seams the README names. Overview of both:
  <https://agent-observability-docs.splunk.com/sdk-api/logging/logging-basics>
- Metadata: whatever your worksheet says the customer wants to filter by, on
  every trace. `run_batch.py` already rotates through several users.

Run one question, find the trace in the console. Then turn on the evaluators
your worksheet names, and no more: agent stream, Configure Evaluators. Luna
evaluators run on Splunk-hosted small models with no setup. LLM-judge
evaluators need a model integration on the org; the facilitator set one up. If
an evaluator shows an error about a model integration, that is the org, not
you: tell the facilitator.

**Done when:** a trace with the full tree is in your project, with your
metadata on it, and the evaluators are scoring.

### End of day one

Where you should be when the block ends:

- Design worksheet filled and signed off by a coach.
- Agent generated and answering.
- Instrumented: a trace with the full tree in your project, with your metadata.
- Traffic: `python run_batch.py 10` has run at least once.
- At least one evaluator from your worksheet turned on and scoring.

One line per person at the checkpoint: what's wired, what's left. If you are
behind, say so; the coaches use the gap between blocks to catch people up.
Optional homework, under an hour: run the batch with the planted failure on,
and bind one control.

## Day two: Validate, Position, Solve (about three and a half hours)

### Step 6. Validate (120 minutes)

Prove the failure gets caught and stopped.

1. Send clean traffic: `python run_batch.py 10`. Nothing should flag.
2. Send the failure: `FAILURE_MODE=<the scenario's failure> python run_batch.py 5`.
   This replays five questions with the planted failure switched on, so the
   agent misbehaves the way the customer fears. For HR that is
   `FAILURE_MODE=pii_leak python run_batch.py 5`, and some replies will leak
   another employee's data. The agent's README names the mode for your
   scenario.
3. In the console, confirm an evaluator flags those traces and its rationale
   says why.
4. Make something act on it. Either a runtime control that steers or blocks
   the reply (set up in the Agent Control console or with the SDK), or an alert
   on the agent stream that posts to a channel. One is enough. Work from the
   docs first; `examples/` has a worked example of each if you get stuck.
5. Run the coach: `/coach agents/<your folder>` (Cursor: "coach agents/<your
   folder>"). It reads your work and asks the questions the customer will ask.

**Done when:** the planted failure is caught and acted on, and clean traffic is
left alone.

### Step 7. Write the success criteria (30 minutes)

Use `worksheets/success-criteria.md`. Three to five lines, not a plan. Each one
in the customer's words with how your demo proves it, taken from your worksheet
rows. Then one line for the objection this customer will raise and your answer,
and one line for what you'd hand off because it isn't this product's job.

Save it as `agents/<your folder>/readout/success-criteria.md`.

**Done when:** the customer would agree those are the criteria.

### Step 8. Show and tell (60 minutes in all, 2 to 3 minutes each)

Each person shows their work to their coach and team. Keep it to two or three
minutes per person. This is informal. It is not a certification demo.

A short turn in front of your group, console open: what you built, which
evaluators and control you set up and why, what you hit along the way, and
which quote each screen answers. This is not a customer presentation; it is
how the group learns from each other and how the coaches see where everyone
is. Coaches give feedback on the spot on four
things: does every screen trace back to the customer, are the evaluators and
control the right ones and why, would the customer agree with the success
criteria, can you explain every setting and line you wrote.

The facilitator may pick a few people to show their work to the whole room on
the last day. Same format, a little longer.

### Step 9. Back up your agent (5 minutes)

Your EC2 instance is deleted the day after the bootcamp. Before you leave,
copy your agent folder and worksheets to your laptop so you can record your
demo from them:

```bash
rsync -av -e "ssh -p 2222" --exclude .venv splunk@<your instance>:~/customer-challenge/agents/<your folder>/ ~/customer-challenge-agent/
```

Recreate the venv on your laptop with Python 3.12 and `requirements.txt` plus
`splunk-ao`. Your `.env` holds the keys the facilitator gave you; keep it off
shared drives.

## After the bootcamp: record your demo

Record the demo as the customer meeting: the people in the scenario's "Who you
will present to", the questions in "What they said they want", three screens
each tied to a quote, then your success criteria as the POC you propose. The
facilitator gives the window and where to submit it. Use the feedback from the
show-and-tell before you record.

## Where things are

| What | Where |
| --- | --- |
| Your customer | `scenarios/<your scenario>/SCENARIO.md` and `brief.yaml` |
| The worksheet | `worksheets/design-worksheet.md` |
| Success criteria sheet | `worksheets/success-criteria.md` |
| Commands in detail | `README.md` |
| Your agent | `agents/<your folder>/` after step 4 |
| Product docs and SDK | <https://agent-observability-docs.splunk.com> |
