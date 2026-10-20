# Scenario: Automotive manufacturer, internal platform team

## Who they are
The internal platform team at a large automotive manufacturer. Everything
runs on-prem, including Splunk. Engineers across the company are building
agents fast, most of them small tools over internal systems, used from
whatever coding assistant each engineer prefers.

**Why they need agent observability.** They have no way to tell whether a
tool is any good, whether it is being used the way its author intended, or
what it costs per consumer. Today they have homegrown pieces, some token
tracking and some monitoring, built by different people, and nothing that
evaluates agent behavior.

**Where they're heading.** A purpose-built platform, on their own
Kubernetes, that evaluates how agents use tools, shows cost per consumer, and
lets many agent owners see only their own data.

## The agent
An internal assistant for the platform team's own engineers. Instead of
writing searches and editing alerts in their on-prem Splunk by hand, an
engineer asks in plain language and the agent does it through the platform
team's tools.

A typical run: an engineer asks "Which hosts on the paint line were degraded
in the last hour? Raise the disk alert threshold to 90 percent." The agent
works out what is being asked (triage), then either answers from the
internal docs (knowledge) or calls the tools: search events, check host status,
update an alert (action). A writer turns the result into a short answer.

In production those tools sit behind MCP servers the team built, and engineers
reach them from several different coding assistants, which don't always pick
the same tool for the same request. Your starter agent skips all of that: the tools are plain
Python functions with the same names and shapes, so you build no MCP plumbing.

| | |
|---|---|
| Language and framework | Python; no framework. A hand-written tool-calling loop. |
| Model | On Bedrock, behind their own gateway |
| Hosting | On-prem |
| Shape | A triage step, then either a knowledge step over internal docs or an action step that calls the tools, and a writer. Two read tools, one write tool. |
| Tools | Search events, host status, update an alert |
| Data | Log events, host health, alert definitions |

## Who you will present to
| Role | Cares about |
|---|---|
| Platform lead, owns the internal tools | Tool quality, token cost per consumer, per-owner data segregation |
| Platform engineer | Specifics of the use case for the demo |

## What they said they want
In their words, lightly cleaned up.

- Platform lead: "Everybody needs some framework and some help to say, I just wrote this thing, is it any good? Is it being used the way I think it is?"
- Platform lead: "They make different choices about which tools to call when given the same prompt."
- Platform lead: "Keeping an eye on token cost and who's consuming the most tokens is relevant too."
- Platform lead: "How do we let owners of many agents view their own data and segregate it so they're not touching other stuff?"
- Platform lead: "We open an MCP to our own application and we're seeing our traffic patterns change. Some of our interest is monitoring the load on our own thing."

## The failure they fear most
A tool "not used the way I think it is": the agent calls the write tool,
update an alert, on a request that only asked a question. Nobody asked for a
change and something changed. This is the planted failure in your starter
agent (`wrong_tool`).

## What changes what you show
- Many agent owners, each of whom must see only their own data. In the lab you
  have one project and your own agent stream, so your stream stands in for an
  owner's project: say "one project per owner" over the project list.

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
