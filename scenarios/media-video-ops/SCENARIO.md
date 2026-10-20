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
things they want to see.

## The agent
An incident triage bot for the team that runs video infrastructure. It sits in
the on-call channel and does the first pass on every alert so an engineer
doesn't have to.

A typical run: monitoring raises "encoder ENC-204 dropped output on channel
17." The bot classifies the alert and sets a severity (triage), then
either finds the matching runbook (knowledge) or calls tools: look up the
device's status, open or update the ticket, post to the on-call channel
(action). A writer
produces the summary the on-call engineer reads. It handles 10 to 15 incidents
a day.

The customer's list below also mentions a customer-facing agent. For the
challenge, the triage bot is the one you build.

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
| Bot developer, owns the code | A change they can ship in one pull request; every tool call visible; the proxy |
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
obeys an "ignore your instructions" line in the input.

## What changes what you show
- Outbound traffic from the bot's host is blocked until a domain is whitelisted.
  "How did you get traffic out?" will be asked at the show-and-tell; have the answer.
- A change is a PR, a review, and a restart. Your instrumentation has to be
  inert until an environment variable is set; show the diff.
- 10 to 15 incidents a day is too thin; replay closed incidents into a separate
  agent stream and show that stream.
- The developer holds no cloud credentials; judge evaluators need an
  integration the platform team sets up.

## Your deliverable
Two things.

1. A short show and tell for your coach and team, two to three minutes, console
   open. Show the console views that show what you solved for the customer,
   each tied to one of the quotes in "What they said they want". Say what you
   built and what you configured.
2. Your success criteria: three to five lines, in the customer's words.

This is not a certification demo. After the bootcamp you record a full
customer-facing demo of your agent for L2. The session explains how.

## Next
Finished reading? Go to the README at the repo root, step 2: the design
worksheet. It lists every step from here to the show-and-tell.
