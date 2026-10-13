# Design worksheet

Team: ______________   Scenario: ______________   Coach sign-off (name): ______  Date: ______

Prefer to fill it in Word? `design-worksheet.docx` next to this file is the same sheet.
Save your filled copy as `agents/<your folder>/readout/worksheet.md` (or `.docx`).

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

Rules of thumb the coach will check:
- Three to five rows. More than five means you're doing a platform tour.
- At least one row is an evaluator, and at least one row is something that acts
  on the failure: a runtime control, or an alert that answers "how would I know
  without watching the UI". One of the two is enough.
- The feared failure from the scenario appears in at least one row, and you can
  say which evaluator catches it and which control stops it.
- Anything the scenario's traps say is not this product's job is NOT on this
  sheet. Write one sentence below on who you'd hand it to instead.

Out of scope hand-off: ______________________________________________

## The three screens
What the customer sees, in order. One line each.
1. 
2. 
3. 

## Metadata we'll tag on every trace
(so the filters the customer asked for actually work)
- 

## Build path
Framework from the scenario: ____________  →  skill: `build-agent-__________`
If the customer didn't say, write what you'd ask them and what you're assuming meanwhile.
