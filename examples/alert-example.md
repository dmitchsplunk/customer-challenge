# Worked example: an alert on an evaluator

Alerts are configured on the agent stream in the console, not in code.

1. Open the project, then the agent stream, then the Alerts tab.
2. New alert. Condition: an evaluator value, for example output PII is not
   empty, or trace latency above a threshold in milliseconds.
3. Destination: a webhook. Slack and ServiceNow both accept incoming webhooks;
   the facilitator has a test Slack channel with a webhook URL.
4. Save, then trigger it: run the batch with the planted failure on for the PII
   case, or `FAILURE_MODE=latency` for the latency case.

What "done" looks like: a message arrives in the channel naming the trace,
without anyone watching the console. That is the systems engineer's question in
the HR scenario answered.
