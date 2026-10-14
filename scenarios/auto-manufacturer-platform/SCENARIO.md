# Scenario: Automotive manufacturer, internal platform team

## Who they are
The internal platform team at a large automotive manufacturer. Everything
runs on-prem, including Splunk. Engineers across the company are building
agents fast, and most of them are MCP servers over internal tools, used from
whatever coding assistant each engineer prefers.

**Why they need agent observability.** They have no way to tell whether an MCP
is any good, whether it is being used the way its author intended, or what it
costs per consumer. Today they have homegrown pieces, some token tracking and
some monitoring, built by different people, and nothing that evaluates agent
behavior.

**Where they're heading.** A purpose-built platform, on their own Kubernetes,
that evaluates tool use across the harnesses people actually use, shows cost per
consumer, takes the thumbs-up and thumbs-down feedback they already collect as
an input to evaluation, and lets many agent owners see only their own data.

## The agent
An internal assistant for the platform team's own engineers. Instead of
writing searches and editing alerts in their on-prem Splunk by hand, an
engineer asks in plain language and the agent does it through the platform
team's tools.

A typical run: an engineer asks "Which hosts on the paint line were degraded
in the last hour? Raise the disk alert threshold to 90 percent." The agent
works out what is being asked (triage), finds the relevant internal doc
(knowledge), then calls the tools: search events, check host status, update an
alert (action). A writer turns the results into a short answer.

In production those tools sit behind MCP servers the team built, and engineers
reach them from several different harnesses that behave differently against
the same server. Your starter agent skips all of that: the tools are plain
Python functions with the same names and shapes, so you build no MCP plumbing.

| | |
|---|---|
| Language and framework | Python; no framework. A hand-written tool-calling loop. |
| Model | On Bedrock, behind their own gateway |
| Hosting | On-prem |
| Shape | A triage step, a knowledge step over internal docs, an action step that calls the tools, and a writer. Two read tools, one write tool. |
| Tools | Search events, host status, update an alert |
| Data | Log events, host health, alert definitions |

## Who you will present to
| Role | Cares about |
|---|---|
| Platform lead, owns the Splunk MCP | MCP quality across harnesses, token cost per consumer, feeding existing user feedback into evaluation, per-owner data segregation |
| Platform engineer | Specifics of the use case for the demo |
| Platform engineer | Which product does what, and why there are two |

## What they said they want
In their words, lightly cleaned up.

- Platform lead: "One of the things I really care about, especially for MCPs, is how different harnesses interact with the same MCP. They have different truncation limits for reading tool descriptions. They make different choices about which tools to call when given the same prompt."
- Platform lead: "Everybody needs some framework and some help to say, I just wrote this thing, is it any good? Is it being used the way I think it is?"
- Platform lead: "Keeping an eye on token cost and who's consuming the most tokens is relevant too."
- Platform lead: "If we have an agent with an existing feedback mechanism, thumbs up, thumbs down, comments, can we hook into that as another data source for the evaluator?"
- Platform lead: "How do we let owners of many agents view their own data and segregate it so they're not touching other stuff?"
- Platform lead: "We open an MCP to our own application and we're seeing our traffic patterns change. Some of our interest is monitoring the load on our own thing."

## The failure they fear most
A tool that is "not used the way I think it is": the agent picks the wrong
tool, or no tool, for a request that clearly needs one. This is the planted
failure in your starter agent (`wrong_tool`).

## What changes what you show
- Many agent owners, each of whom must see only their own data. One project per
  owner is a screen, not a footnote.

## Traps
- Monitoring the load on their MCP server. That is APM and the Splunk platform, not this product. A team that builds load dashboards missed the lead's actual ask.
- Building a pretty agent. He said "lots of MCPs," not "a chat UI."
- Claiming to see agents nobody instrumented.

## Your deliverable
Two parts. In the session, a short show-and-tell to your group, two to three
minutes, console open: what you built, which evaluators and control you set
up and why, and what you hit. Coaches give feedback. After the bootcamp, a
recorded demo run as the customer meeting with the people in "Who you will
present to", answering the questions in "What they said they want". The
facilitator gives the window and where to submit it. Three screens, each tied to one of the quotes, then your three
to five success criteria. The thing they actually asked for is proof that you
can tell, per tool, whether it was the right call and whether it worked: tool
selection quality and tool error rate, per tool, on the trace.

## Next
Finished reading? Go to the README at the repo root, step 2: the design
worksheet. It lists every step from here to the show-and-tell.
