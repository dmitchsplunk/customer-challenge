# Coach checklist

## Traces
- [ ] One trace per customer interaction, not per model call.
- [ ] Agent, LLM, and tool spans nested the way the agent actually runs.
- [ ] LLM spans carry model name and token counts.
- [ ] Tool spans carry inputs, outputs, and status; failures show as errors.
- [ ] Trace and spans have inputs and outputs the customer could read.
- [ ] Metadata on every trace matches the filters the customer asked for.
- [ ] Traces are complete, none stuck as "partial".

## Evaluators
- [ ] Each enabled evaluator maps to a quote in the scenario.
- [ ] Luna vs LLM-judge choice is deliberate and the team can say why.
- [ ] LLM-judge evaluators have a model integration and actually score.
- [ ] (stretch) One custom judge written in the customer's definition of a bad answer.
- [ ] The planted failure is caught by at least one evaluator, with a rationale.

## Something acts on the failure (a control, an alert, or both)
- [ ] Control: bound to the right step (pre or post) with a real action; fires
      on the planted failure, quiet on clean traffic; the team can show what
      the end user sees when it fires.
- [ ] Alert: reaches a channel outside the console when the evaluator flags
      the failure.
- [ ] At least one of the two is present and demonstrated.

## Demo
- [ ] Every console view ties to a quote, and the person stayed within the time.
- [ ] Under two minutes on the agent itself.
- [ ] Out-of-scope asks from the scenario are handed off, not claimed.
- [ ] The team can explain every line of instrumentation.
