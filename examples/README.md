# Worked examples for step 6

Use these only after you have tried it from the docs.

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
  bootcamp tenant are in your agent's `.env.example`; if the key is empty, ask
  your facilitator for it. Then wrap your reply step with
  `@control(step_name="write")` as the docs show.
- `alert-example.md`: an alert on the agent stream that posts to a channel when an
  evaluator flags a trace.
- `custom-judge-example.py`: a custom LLM judge that compares a reply with a second source. For
  failures that no preset evaluator can see, because the preset only checks a reply against
  the sources it was given.
