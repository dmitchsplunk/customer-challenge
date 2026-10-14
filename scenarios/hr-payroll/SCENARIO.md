# Scenario: HR and payroll software company

## Who they are
A large HR and payroll software company. They are putting an AI assistant
inside their product so employees can ask payroll and benefits questions and
get things done without a ticket. Their rule is that none of their data leaves
their own data centers, so everything AI runs on their own hardware.

**Why they need agent observability.** They can trace the assistant today with
a self-hosted open-source tool, but tracing is all it does. It doesn't tell them
when the assistant puts someone's bank account number in a reply, doesn't stop
it, and doesn't tell anyone it happened.

**Where they're heading.** One platform their infrastructure team can run and
their security team can trust: evaluation and guardrails on top of tracing,
alerts that reach people, and one view across data centers.

## The agent
An employee self-service assistant inside their HR and payroll product.
Employees of their customers use it instead of calling their HR team.

A typical run: an employee types "I want to change my direct deposit." The
agent turns that into a ticket (intake), decides whether it is a question or
an action (route), then either answers from the help articles or makes one
tool call: open the direct-deposit screen, start a workflow, or look up the
employee's own record for things like the next pay date or PTO balance
(resolve). A last step writes the reply the employee sees (write).

Your starter agent is the same four steps and three tools, over 20 synthetic
help articles and a handful of synthetic employee records.

| | |
|---|---|
| Language and framework | Python, LangGraph |
| Model | Their own, self-hosted, behind an internal gateway |
| Hosting | On-prem |
| Steps | Intake (turn the request into a ticket), route, resolve (articles or one tool call), write the reply |
| Tools | Open a screen, start a workflow, look up the requesting employee's own record |
| Data | 20 help articles, employee records, screen and workflow names |

## Who you will present to
| Role | Cares about |
|---|---|
| Systems engineer, would administer the platform | Admin overhead on his team, one consolidated view across data centers, latency alerting, no external models touching their data |
| Monitoring and guardrails lead | Fidelity of the traces, fidelity of the guardrails, anomaly alerting |
| Data science lead | How agent-to-agent orchestration is traced, using their own models for evaluation, role-based access for agents |
| Security lead | Guardrails |
| Program coordinator | Simple latency and token reporting |

## What they said they want
In their words, lightly cleaned up.

- Systems engineer: "Say the PII evaluator goes off and notices the agent just provided someone's bank account information. Is that alerted? How would somebody know that happened, unless they were looking at the UI?"
- Monitoring lead: "My team is interested in the guardrails piece, and the fidelity of what we can get out of that. From a monitoring standpoint we want the fidelity of the traces, and what we can use for anomaly alerting, for weird things occurring."
- Program coordinator: "Just some simple reporting on latency for these models and token usage, per client or employee. Simple things we could get right off the bat."
- Someone on their side: "What's the difference between evaluators and controls? How do they link together?"
- Data science lead: "Can we have access to these guardrail models and use our own data to train them? We'll be identifying the false positives and annotating that data."
- Data science lead: "Role-based access for the agents. An agent not having access to another agent. Identity and access management for the agent."
- Systems engineer: "Base expectation is latency monitoring and alerting. Three to seven seconds is normal. Alert at sixty seconds plus, or on timeouts."

## The failure they fear most
The assistant puts personal data, a bank account number or an SSN, into a
reply, and nobody finds out until someone happens to look. This is the planted
failure in your starter agent (`pii_leak`).

## Traps
- Doing too much. The PII question is the whole demo: evaluator, alert, control, in that order.
- Comparing against the tracing tool they already run. They described its gaps; they didn't ask for a bake-off.
- Leaning on any feature that calls an external model.

## Your deliverable
Two parts. In the session, a short show-and-tell to your group, two to three
minutes, console open: what you built, which evaluators and control you set
up and why, and what you hit. Coaches give feedback. After the bootcamp, a
recorded demo run as the customer meeting with the people in "Who you will
present to", answering the questions in "What they said they want". The
facilitator gives the window and where to submit it. Three screens, each tied to one of those quotes, then your
three to five success criteria.

## Next
Finished reading? Go to the README at the repo root, step 2: the design
worksheet. It lists every step from here to the show-and-tell.
