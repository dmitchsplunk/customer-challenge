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

**Where they're heading.** They keep LangFuse for developer tracing. They want a
loop that improves without a human in it every time, governance across all
projects, and token spend they can see per request and per business unit, in
terms that hold up with their buyer.

## The agent
A car-shopping assistant embedded in dealer websites. A shopper chats with it
instead of browsing inventory pages.

A typical run: a shopper says "I want a hybrid SUV under 40k with hands-free
driving, and I have a 2019 sedan to trade in." The agent works out what is
being asked (router), searches dealer inventory, pulls feature descriptions
for the matching models from the marketing brochures, compares the candidates,
estimates the trade-in and a monthly payment, and offers a test-drive slot. A
writer turns all of that into the reply.

Your starter agent is smaller than the real one: intake, route, look up (a
brochure and the dealer's inventory record for the vehicle), write. Keep it small.

| | |
|---|---|
| Language and framework | Python, LangGraph |
| Model | Bedrock |
| Hosting | AWS |
| Steps | Intake, route, look up (brochures and inventory records), write the reply |
| Tools | Inventory lookup, trade-in estimate, test-drive booking |
| Data | Brochures, inventory records, vehicle names |

## Who you will present to
| Role | Cares about |
|---|---|
| Buyer, second in command, owns their highest-priority triage agent | Cost and token spend, one governance view across business units |
| Head of ML | "Is this calibrated?" about any evaluator you show |
| Technical evaluation owner | Runs a human-calibrated LLM-as-judge in production today and wants the loop automated; has seen the tour |
| New stakeholder, role unknown | Governance, probably |

## What they said they want
From meeting notes, so the wording is close rather than exact.

- Technical evaluation owner: "We've seen these functionalities with other products."
- Head of ML: "Is this calibrated?"
- Buyer: wants to see where the token spend goes, per request and per business unit, and one governance view across the business units.
- The team: "We're not replacing LangFuse."

## The failure they fear most
The assistant tells a shopper that a vehicle has a feature, such as a
hands-free driving package, that the dealer's records do not show for that
vehicle, and cites a brochure for it. Nobody finds out until a shopper arrives
asking for it. This is the planted failure in your starter agent
(`fabricated_citation`).

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
