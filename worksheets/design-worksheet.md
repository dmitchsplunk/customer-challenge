# Design worksheet

Name: ______________   Scenario: ______________   Date: ______

Save your filled copy as `agents/<your folder>/readout/worksheet.md`.

Fill this from the scenario before you build anything. Every row must
start with something the customer actually said. If you can't point to a quote,
the row doesn't belong here.

| # | Customer said (quote + who) | What we'll show them | SAO feature that does it | How we set it up (your words) |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

Rules of thumb to check with your team:
- Three to five rows. More than five means you're doing a platform tour.
- At least one row is an evaluator, and at least one row is something that acts
  on the failure: a runtime control, or an alert that answers "how would I know
  without watching the UI". One of the two is enough.
- The feared failure from the scenario appears in at least one row, and you can
  say which evaluator catches it and which control stops it.
- Anything the customer asked for that is not this product's job is NOT on
  this sheet. Write one sentence below on who you'd hand it to instead.

Out of scope hand-off: ______________________________________________

## The console views you'll show
Pages in the Splunk Agent Observability console that show what you solved for the
customer, in order. One line each. You have two to three minutes.
1. 
2. 
3. 

## Metadata we'll tag on every trace
(so the filters the customer asked for actually work)
Look in what the customer said for "per ___" or "only their own ___". Each one is
something you will want to filter or group by in the console, so each needs a label
on every trace. For example, "per branch" means a `branch` label.
Skip anything the console already separates for you: the agent stream, the project, the
model.
If the customer didn't say, use `user_id` and write that down. Use one to three short
keys with plain names.
- 

## Build path
Framework from the scenario: ____________  →  skill: `build-agent-__________`
If the customer didn't say, write what you'd ask them and what you're assuming meanwhile.
