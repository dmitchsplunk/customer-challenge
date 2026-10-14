# Start here

## What this is

Over two days your team acts as the solutions engineers for one customer,
written up as a scenario. Four scenarios are offered; 
the facilitator assigns one per group. You work out what that customer asked for, set up
Splunk Agent Observability for an agent shaped like theirs, and at the end
present the result to that customer, played by your coaches, who ask the
questions quoted in the scenario.

The agent is given to you and kept small. What you set up in the product, and
how well it answers what the customer said, is the whole exercise.

Naming: the product is Splunk Agent Observability (SAO). The Python SDK is
`splunk-ao` and the docs are at https://agent-observability-docs.splunk.com.
What the SDK calls an agent stream is the bucket of traces inside a project;
some console screens still say log stream. Same thing.

## Rules of the road

- Spend your time on the product and the customer, not on the agent. The agent
  is capped at four steps and four tools; `shared/check_skeleton.py` counts them.
- You may use Claude Code or Cursor to help write the instrumentation. You
  must be able to explain every line at the readout.
- If the scenario says the customer didn't ask for it, it isn't in your demo.
- Between the two blocks, coaches answer in the workshop channel the facilitator
  names, within 30 minutes. In the room, just ask. They won't write your code.
- The `demo-builder` skill in this repo is for after the challenge. Using it
  during the challenge defeats the exercise, and the coaches will notice.

## Before day one

Ensure that Cursor or Claude is installed on your machine. 

## Day one: Discover, Design, Build (about two hours)

**Step 1. Read the scenario.** `scenarios/<your scenario>/SCENARIO.md`. Read it
twice. Mark the three to five sentences the customer said that you think the
demo must answer. If the customer didn't say something, you don't know it;
don't invent it for the demo.
Done when: your team agrees on which quotes the demo must answer.

**Step 2. Fill the design worksheet.** `worksheets/design-worksheet.md`, or the
Word version `design-worksheet.docx` next to it if you'd rather fill it by hand. Three
to five rows. Each row starts with a quote, then what you'll show, which
product feature does it, and how you'll set it up. Below the table: the three
screens you'll show, the metadata you'll tag on every trace, and the build
path (the scenario's framework tells you which build skill).
Save your copy as `agents/<your folder>/readout/worksheet.md` (or `.docx`) once the agent
folder exists (until then, anywhere your team can see it).
Done when: a coach has crossed out anything the customer didn't ask for and put
their name on the sign-off line.

**Step 3. Prepare the environment.**

Access the Splunk Show event by clicking the link provided by your workshop instructor. You’ll need to sign in using your Cisco.com account.

We’ve prepared an Ubuntu Linux instance in AWS/EC2 for each attendee. To get the details of your EC2 instance from the Splunk Show event:

* Click **Enroll event** on the top-right corner
* Then look near the bottom of the page for your EC2 instance details

Using a terminal window, use the SSH Command and SSH Password to connect 
to your environment. 

The workshop requires Python 3.12+, so run the following command using the terminal 
to install Python 3.12 on the ec2 instance: 

```bash
sudo apt-get update && sudo apt-get install -y python3.12 python3.12-venv
```

Navigate to the home directory, then clone the GitHub repository where the Customer Challenge 
materials are stored: 

```bash
cd ~
git clone https://github.com/dmitchsplunk/customer-challenge.git
cd customer-challenge
```

Then, use Cursor or Claude to ssh to the ec2 instance using the information from Splunk Show. 

## Cursor: Connect to EC2 Instance

With Cursor, this is done using the `Remote-SSH` extension. Once connected, open the 
`/home/splunk/customer-challenge` folder using Cursor. 

## Claude: Connect to EC2 Instance

* Open Claude Desktop
* Click on the `Code` tab
* Click on the `Local` button
* Choose `SSH` -> `Add SSH connection...`

![Claude Config](./images/claude-config.png)

* Add the SSH connection details using the information from Splunk Show

![Claude SSH Connection](./images/claude-ssh-connection.png)

* Click on `Select Folder` and open the `/home/splunk/customer-challenge` folder
* Click `Trust Workspace` when prompted

Now, any commands you enter into Claude will be executed on the EC2 instance. 

**Step 4. Generate the agent.** 

In this step, we'll use AI to build an agent using the provided skills. 

Using Claude Code, this can be achieved via the following prompt: 

````
/build-agent-<path> scenarios/<your scenario>/brief.yaml
````
> Fill in the appropriate path and scenario name before running the commmand. For example: `/build-agent-langgraph scenarios/auto-retail/brief.yaml`

In Cursor, use the following prompt instead: 

````
build the agent for scenarios/<your scenario>/brief.yaml on the <path> path
````

> For example:  `Please build the agent for scenarios/auto-retail/brief.yaml on the langgraph path`.

A few minutes later you have a folder under `agents/` with a working agent, mock
data, 30 realistic inputs, and one planted failure taken from the scenario. The
skill creates the virtual environment (venv), installs, and runs one question; its README shows how to
do that yourself if anything failed. The failure is off by default. It has no
observability code in it.

Once the agent is built, open the `agents/<scenario name>/.env` file for editing, 
and add the following environment variables, using the values provided by your
facilitator: 

````
OPENAI_API_KEY=provided_by_facilitator 
OPENAI_BASE_URL=provided_by_facilitator
SPLUNK_AO_CONSOLE_URL=https://console.multitenant.sao.splunkcloud.com 
SPLUNK_AO_API_URL=https://api.multitenant.sao.splunkcloud.com
SPLUNK_AO_API_KEY=provided_by_facilitator 
SPLUNK_AO_PROJECT=provided_by_facilitator
SPLUNK_AO_AGENT_STREAM=${INSTANCE}
````

Done when: `python app.py "<a question>"` answers, and
`FAILURE_MODE=<the scenario's failure> python app.py "<a question>"` shows the failure.

**Step 5. Instrument it and get the first trace in.** This is yours to do, from
the docs. Pointers, not answers:
- `pip install "splunk-ao[langchain]"` in the agent's venv (plain `splunk-ao` on the Python path).
- The SDK reads `SPLUNK_AO_CONSOLE_URL`, `SPLUNK_AO_API_URL`, `SPLUNK_AO_API_KEY`,
  and `SPLUNK_AO_PROJECT` from the environment. Use that project. The agent
  stream name is `INSTANCE`. The SDK does not read it, so pass
  `agent_stream=os.environ["INSTANCE"]` when you create the logger. Do not
  create a project, and do not put the console login (`SPLUNK_AO_USER`,
  `SPLUNK_AO_PASSWORD`, `SPLUNK_AO_USER_ID`) in the agent.
- The agent calls `gpt-4.1-mini` through `OPENAI_API_KEY` and `OPENAI_BASE_URL`.
  Those are already set. Do not clear them in `.env`.
- LangGraph path: the LangChain callback, https://agent-observability-docs.splunk.com/sdk-api/third-party-integrations/langchain
  (one object attached to the graph call).
- Python path: the logger, https://agent-observability-docs.splunk.com/sdk-api/logging/splunk-ao-logger
  (start a trace, add agent, LLM and tool spans, conclude, flush) around the
  seams the README names. Overview of both: https://agent-observability-docs.splunk.com/sdk-api/logging/logging-basics
- Metadata: whatever your worksheet says the customer wants to filter by, on
  every trace. `run_batch.py` already rotates through several users.

Run one question, find the trace in the console. Then turn on the evaluators
your worksheet names, and no more: agent stream, Configure Evaluators.
Luna evaluators run on Splunk-hosted small models with no setup. LLM-judge
evaluators need a model integration on the org; the facilitator set one up. If
an evaluator shows an error about a model integration, that is the org, not you:
tell the facilitator.
Done when: a trace with the full tree is in your project, with your metadata
on it, and the evaluators are scoring.

**Checkpoint.** At the end of day one, one line per team: what's wired, what's left.
Optional homework, under an hour: run the batch with the planted failure on, and
bind one control.

## Day two: Validate, Position, Solve (about two hours)

**Step 6. Validate.** Prove the failure gets caught and stopped.
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
   docs first; `coaching/` has a worked example of each if you get stuck.
5. Run the coach: `/coach agents/<your folder>` (Cursor: "coach agents/<your
   folder>"). It reads your work and asks the questions the customer will ask.
Done when: the planted failure is caught and acted on, and clean traffic is
left alone.

**Step 7. Write the success criteria.** Use `worksheets/success-criteria.md`,
or the Word version `success-criteria.docx` next to it. Three to five lines, not
a plan. Each one in the customer's words with how your demo proves it, taken
from your worksheet rows. Then one line for the objection this customer will
raise and your answer, and one line for what you'd hand off because it isn't
this product's job.
Save it as `agents/<your folder>/readout/success-criteria.md` (or `.docx`).
Done when: the customer would agree those are the criteria.

**Step 8. Present.** Ten minutes as the customer meeting. Coaches play the roles
from the scenario and ask the quoted questions. Three screens, each tied to a
quote, then the success criteria. Then five minutes of feedback on four things: does every
screen trace back to the customer, are the evaluators and control the right
ones and why, would the customer agree with the success criteria, can you explain
every setting and line you wrote.

## Where things are

| | |
|---|---|
| Your customer | `scenarios/<your scenario>/SCENARIO.md` and `brief.yaml` |
| The worksheet | `worksheets/design-worksheet.md`, or `.docx` to fill in Word |
| Success criteria sheet | `worksheets/success-criteria.md`, or `.docx` |
| What coaches look for | `worksheets/feedback-guide.md` |
| Control and alert examples | `coaching/` |
| Commands in detail | `README.md` |
| Your agent | `agents/<your folder>/` after step 3 |
| Product docs and SDK | https://agent-observability-docs.splunk.com |
