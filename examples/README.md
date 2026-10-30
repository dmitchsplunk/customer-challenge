# Worked examples for steps 5 and 6

Use these only after you have tried it from the docs.

- `metadata-fields-example.py`: the SDK packs all your metadata into one JSON
  attribute, so `user_id` and similar keys can't be filtered or grouped on cleanly.
  This wraps one SDK function so each key becomes its own field. It works for any
  scenario and any metadata keys. Run it from your agent's folder to see the
  before and after, with no credentials:

  ```bash
  python ../../examples/metadata-fields-example.py
  ```

  Then copy the function into your `app.py` and call it once at startup, before
  the first trace.

- `control-example.py`: creates a regex control that steers any reply containing an
  SSN, puts it in a policy, and binds the policy to your agent. Run it once from your
  agent's venv with the agent's `.env` loaded:

  ```bash
  pip install "agent-control-sdk==8.4.0" httpx
  python ../../examples/control-example.py
  ```

  It reads `AGENT_CONTROL_URL`, `AGENT_CONTROL_API_KEY`,
  `AGENT_CONTROL_API_KEY_HEADER`, and `AGENT_CONTROL_AGENT_NAME` from the environment.
  Without the header variable the control plane returns 401. The values for the
  bootcamp tenant are in your agent's `.env.example`. The key is filled from
  `SPLUNK_AO_API_KEY`, so you do not need to ask for it. Then wrap your reply step with
  `@control(step_name="write")` as the docs show.
- `alert-example.md`: an alert on the agent stream that posts to a channel when an
  evaluator flags a trace.
- `custom-judge-example.py`: a custom LLM judge that compares a reply with a second source. For
  failures that no preset evaluator can see, because the preset only checks a reply against
  the sources it was given.
