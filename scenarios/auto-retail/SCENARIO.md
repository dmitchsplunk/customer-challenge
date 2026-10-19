# Scenario: Automotive retail marketplace

## Who they are
A large automotive retail marketplace and a mature AI shop: more than 17
agents in production across 20 business units, dozens of ML engineers, and an
internal fine-tuned model. Developers trace agents with LangFuse and CloudWatch
and are not giving that up.

**Why they need agent observability.** Their evaluation today is a
human-calibrated LLM-as-judge that one person maintains by hand. It doesn't
scale across 20 business units, it doesn't close the loop automatically, and
nobody has one governance view or a clear picture of token spend. They have
already seen a tour of our product and said they'd seen it all elsewhere.

**Where they're heading.** Keep LangFuse for developer tracing and add an
enterprise layer on top: calibrated evaluators that catch grounding failures
between their own systems, a loop that improves without a human in it every
time, governance across all projects, and cost visibility that holds up with
their buyer.

## The agent
A car-shopping assistant embedded in dealer websites. A shopper chats with it
instead of browsing inventory pages.

A typical run: a shopper says "I want a hybrid SUV under 40k with hands-free
driving, and I have a 2019 sedan to trade in." The agent works out what is
being asked (router), searches dealer inventory, pulls feature descriptions
for the matching models from the marketing brochures, compares the candidates,
estimates the trade-in and a monthly payment, and offers a test-drive slot. A
writer turns all of that into the reply.

Your starter agent is smaller than the real one: route, look up inventory and
the brochure, compare, write. That is enough, because the failure below lives
between the brochure lookup and the writer. Keep it small.

| | |
|---|---|
| Language and framework | Python, LangGraph |
| Model | Bedrock |
| Hosting | AWS |
| Steps | Router, inventory search, marketing lookup, compare, trade-in estimate, financing, scheduler, writer |
| Tools | Inventory (dealer management system), brochure CMS, trade-in valuation, financing calculator, scheduler |

## The failure they have actually seen
The brochure for a model says it has a hands-free driving package. The
inventory record for the specific vehicle does not. The compare step leads
with the first brochure bullet, so the shopper is told the car has a feature
it doesn't. No prompt injection. A grounding failure between two of their own
systems, reproducible every time. This is the planted failure in your starter
agent (`fabricated_citation`).

## Who you will present to
| Role | Cares about |
|---|---|
| Buyer, second in command, owns their highest-priority triage agent | Cost and token spend, one governance view across business units |
| Head of ML | "Is this calibrated?" about any evaluator you show |
| Technical evaluation owner | He runs a human-calibrated LLM-as-judge in production today and wants the loop automated; he has seen the tour |
| New stakeholder, role unknown | Governance, probably |

## What they said they want
From meeting notes, so the wording is close rather than exact.

- Technical evaluation owner: "We've seen these functionalities with other products."
- Head of ML: "Is this calibrated?"
- Buyer: tokenomics is what caught his attention; the triage agent is his top priority; he wants one governance view across the business units.
- The team: "We're not replacing LangFuse."

## What changes what you show
- They keep LangFuse. The objection is "we have this already"; the answer is
  what sits next to it, never what replaces it.
- The tokenomics module groups by provider, model, and user from a directory
  import. It does not attribute cost per agent or per trace; the agent-stream
  metrics view does that. Show the right screen for the claim.

## Out of scope
- The platform tour. If your demo opens with the agent graph, you've lost the evaluation owner.
- Attacking LangFuse.
- Inventing a customer-facing access path for tokenomics that doesn't exist.

## Your deliverable
Two parts. In the session, a short show-and-tell to your group, two to three
minutes, console open: what you built, which evaluators and control you set
up and why, and what you hit. Coaches give feedback. After the bootcamp, a
recorded demo run as the customer meeting with the people in "Who you will
present to", answering the questions in "What they said they want". The
facilitator gives the window and where to submit it. The head of ML will ask "is this calibrated?"; the evaluation
owner will say they've seen it. Three screens, each tied to one of the quotes,
then your three to five success criteria. The win is a custom judge grounded
against inventory, with a rationale the head of ML would accept, and honesty
about what tokenomics does and doesn't attribute.

## Next
Finished reading? Go to the README at the repo root, step 2: the design
worksheet. It lists every step from here to the show-and-tell.
