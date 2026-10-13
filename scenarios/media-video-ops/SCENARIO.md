# Scenario: Pay-TV operator, engineering security team

## Who they are
A large pay-TV and streaming operator. Their AI work started with one
incident triage bot for video infrastructure, built by one developer. That bot
got the engineering security team's attention, and the question is now bigger
than one bot: how does the company detect and respond to risk from agents, the
way its SOC does for everything else? They run Splunk, with an OpenTelemetry
stack on AWS and Kubernetes.

**Why they need agent observability.** Security has no visibility into what
agents do: whether an alert's text can hijack the bot, whether a tool call can
pull subscriber data, whether a customer-facing agent is making things up, and
what any of it costs. Nothing today catches those in real time or routes them
to an analyst.

**Where they're heading.** Agent-level detection and response that plugs into
their existing security workflow and observability stack: injections blocked
live, data exfiltration stopped at the tool call, grounding scored, spend
governed, flagged sessions reviewed by a person. They sent a list of eight
things they want to see; the challenge is to deliver the five that are ours and
be honest about the other three.

## The agent
An incident triage bot for the team that runs video infrastructure. It sits in
the on-call channel and does the first pass on every alert so an engineer
doesn't have to.

A typical run: monitoring raises "encoder ENC-204 dropped output on channel
17." The bot classifies the alert and sets a severity (triage), finds the
matching runbook (knowledge), then calls tools: look up the device's status,
open or update the ticket, post to the on-call channel (action). A writer
produces the summary the on-call engineer reads. It handles 10 to 15 incidents
a day.

The customer's list below also mentions a customer-facing agent. For the
challenge, the triage bot is the one you build, and the grounding score is
shown on its replies.

Your starter agent is the same four steps and three tools, over synthetic
runbooks, devices, tickets, and subscriber records.

| | |
|---|---|
| Language and framework | Python; no framework. A hand-written loop against the model's API. |
| Model | A hosted model reached through an API key the platform team issued |
| Hosting | On-prem, behind a corporate proxy that blocks outbound traffic by default; AWS and Kubernetes elsewhere in the stack |
| Steps | Triage (classify, set severity), knowledge (find the runbook), action (one tool call), write the summary |
| Tools | Look up a device's status, open or update a ticket, post to the on-call channel |
| Data | Runbooks, device inventory, open tickets, and, reachable by the tools, subscriber records the bot should never surface |
| Traffic | 10 to 15 incidents a day |
| Modality | Text only today |
| Change process | Feature branch, pull request, peer review, merge, production deploy. A deploy restarts the bot. |

## Who you will present to
| Role | Cares about |
|---|---|
| Director of software engineering, engineering security | SOC-level visibility into agentic AI risk; how it plugs into detection and response |
| Bot developer, owns the code | A change she can ship in one pull request; every tool call visible; the proxy |
| Splunk admin lead | Whether this lands in the Splunk they already run; who gets alerted and how |

## What they said they want
From the director's email asking for the session, lightly cleaned up. They
asked for it "live if possible," focused on two things: integration effort with
their existing AWS, Kubernetes, and OpenTelemetry stack, and SOC-level
visibility into agentic AI risk.

1. "Agent hijacking detection: a prompt-injection attack caught and blocked in real time."
2. "Data exfiltration guardrails: blocking a tool-call attempt to leak subscriber PII."
3. "Hallucination and factual grounding scoring for a customer-facing GenAI agent."
4. "Full agent-to-infra correlation: trace a single agent action from prompt through tool call through AWS and Kubernetes, in one view."
5. "Cost and usage governance: token cost and latency per agent, with runaway-spend alerting."
6. "SOC analyst workflow with the AI assistant: ask why an agent took an action and get a cited trace answer."
7. "Human-in-the-loop review queues for flagged agent sessions."
8. "Multimodal evaluation: video or audio metadata, or a closed-captioning agent use case."

And from the bot developer:
- "I added the tracers to the bot code, but the internal proxy does indeed block outbound traffic. I put in a request to whitelist the domain."
- "Deploying the bot means restarting it."

## The failure they fear most
Items 1 and 2 together: an alert's text carries an injected instruction, the
bot follows it, and a tool call goes after subscriber data. This is the planted
failure in your starter agent (`injection_success`): with it on, the writer
obeys an "ignore your instructions" line in the input. The prompt-injection
evaluator should flag it; a control on the input, before the model runs, should
stop it.

## What is, and isn't, this product's job
Five of the eight are this product, and that's your demo: 1, 2, 3, 5, 7. Say
so plainly, and say the rest plainly too:
- Item 4, prompt-to-infrastructure correlation in one view, is Splunk
  Observability Cloud and the platform, with agent traces alongside the
  infrastructure traces. Show where the agent trace ends; don't claim the rest.
- Item 6, the assistant, exists but runs on an external model. For a security
  audience that's a question, not a feature. Mention it, don't lean on it.
- Item 8, multimodal, is not in scope. Their own bot is text only today.

## What changes what you show
- Outbound traffic from the bot's host is blocked until a domain is whitelisted.
  "How did you get traffic out?" is a readout question; have the answer.
- A change is a PR, a review, and a restart. Your instrumentation has to be
  inert until an environment variable is set; show the diff.
- 10 to 15 incidents a day is too thin; replay closed incidents into a separate
  agent stream and show that stream.
- The developer holds no cloud credentials; judge evaluators need an
  integration the platform team sets up. Lead with Luna evaluators.

## Traps
- Trying to show all eight. Five are yours; three are hand-offs.
- Showing the injection caught after the fact. They asked for "caught and
  blocked in real time." That's a control on the input, not an evaluator on the
  output.
- Making the agent bigger. One bot, one developer, four steps.

## Your deliverable
A 10-minute customer meeting. Coaches play the roles in "Who you will present
to" and ask the questions in "What they said they want". Then 5 minutes of
feedback. Three screens, each tied to a numbered item: the injected alert
blocked before the model runs, with the evaluator flag on the record (1 and 2);
a grounding score with its rationale on a reply (3); token cost and latency per
agent with an alert on a spend threshold (5). Then your three to five success
criteria, and the honest sentence about items 4, 6, and 8.

## Next
Finished reading? Go to `scenarios/START-HERE.md`, step 2: the design worksheet.
It lists every step from here to the readout.
