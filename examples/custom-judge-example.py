"""Worked example: a custom LLM judge for a failure that sits between two sources.

Use it only after you have tried yourself. The retail scenario's failure cannot be caught by a
preset, because the preset only asks whether the reply matches the sources it was given, and the
made-up brochure is one of them. This judge compares the reply with the second source, the
inventory record, which is the source of truth for the specific car.

The id prefixes in the prompt (BRO-, INV-) match the retail data; change them to match yours.

Run once from your agent's folder, with its .env loaded:
    python ../../examples/custom-judge-example.py
Then open Configure Evaluators on your agent stream and check that the judge is on, send the
failing batch, and read the rationale on a flagged reply. Tune the prompt if it misses; a first
version of any judge misses some.
"""
import os
from dotenv import load_dotenv
load_dotenv()
from splunk_ao.evaluators import create_custom_llm_evaluator
from splunk_ao.agent_streams import enable_evaluators

NAME = "unsupported_feature_claim"
PROMPT = (
    "You are auditing a car dealer assistant's reply for a shopper. The input contains two kinds of sources: brochures "
    "(ids start BRO-), which describe a model in general and can list options a specific car does not have, and inventory "
    "records (ids start INV-), which describe the actual car and are the source of truth for what it has. "
    "Look at every vehicle feature, package or option the reply says the car has or offers. For each one, check the inventory "
    "record. If the reply says or implies the car has or offers a feature that the inventory record does not list, or lists as "
    "not installed, even if a brochure says so, the answer is true. If every feature the reply claims is in the inventory "
    "record, the answer is false.\n\nInput: {input}\n\nReply: {output}"
)

stream = os.getenv("SPLUNK_AO_AGENT_STREAM") or os.environ["INSTANCE"]
try:
    create_custom_llm_evaluator(name=NAME, user_prompt=PROMPT, description="Reply claims a feature the inventory record does not list")
    print("created judge", NAME)
except Exception as exc:  # already exists, or the org has no model integration
    print("create judge:", str(exc)[:200])
enable_evaluators(agent_stream_name=stream, project_name=os.environ["SPLUNK_AO_PROJECT"], metrics=[NAME])
print("enabled on stream", stream)
