# Feedback guide

There are no scores. Each team presents its approach and demo as the customer
meeting, and the coaches give feedback on the spot. Use these four questions,
in this order, and say what you saw rather than grading it.

## 1. Does every screen trace back to the customer?
For each screen: which quote from the scenario does it answer? A screen with no
quote behind it is a platform tour. Say which one and why it didn't land.

## 2. Are the evaluators and the control the right ones for this customer, and can the team say why?
Not "did you turn on PII" but "why PII and not instruction adherence for
the systems engineer?" Luna versus LLM-judge should be a deliberate choice. If the planted
failure wasn't caught, ask what would have caught it.

## 3. Would the customer agree with the success criteria?
Three to five, in the customer's words, each with how it's proven, plus the
objection this customer will raise and the answer. Point at any criterion the
customer never asked for.

## 4. Can the team explain every setting and every line they wrote?
Pick two settings and one line of instrumentation at random. If they can't
explain it, say so plainly; that's the thing to fix before a real customer.

## Things to call out when you see them
- More than two minutes of the readout spent on the agent itself.
- A skeleton that grew past four steps or four tools.
- Claiming the product does something the scenario's traps say it doesn't.
- Attacking the incumbent instead of answering the objection.

End each team's feedback with one sentence: the single thing to do differently
on their next real customer.
