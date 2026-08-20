# Diagnose and Tune an Existing System

Use this playbook when an existing game, configuration, prototype, or dataset
shows a suspected imbalance. Reconstruct what the system currently does,
identify the root cause, and calculate one or more concrete fixes.

## Required inputs

Collect as available:

- rules, formulas, configuration tables, and relevant code behavior;
- reported symptom and who experiences it;
- intended outcome or acceptable range;
- content, map, build, opponent, and progression context;
- playtest notes or telemetry with version and sample scope;
- previous changes that may have shifted the system.

Do not treat player wording such as "overpowered" or "too slow" as the root
cause. Convert it into observable behavior and outcomes.

## Procedure

1. **Reproduce the current model.** Run and update an existing persistent
   simulator when available. Otherwise, build a temporary checker from
   `simulation-and-tooling.md` using authoritative rates, costs, probabilities,
   curves, or matchups. Create a new persistent tool only when repeated tuning
   or future content work justifies it. Resolve discrepancies between
   documentation, tool output, and runtime data before tuning.
2. **Validate the model.** If the simulator disagrees with confirmed rules,
   intermediate states, known cases, or comparable runtime behavior, update the
   model contract and tool, add the mismatch as a regression, and rerun model
   checks before diagnosing parameters.
3. **Locate the failure.** Identify the first stage where a result leaves its
   target: acquisition, conversion, combat resolution, content exposure,
   progression, matchmaking, feedback, or player understanding.
4. **Separate scope.** Check whether the issue affects all players and content
   or only particular segments, builds, maps, tiers, opponents, or time bands.
5. **Test alternative causes.** Examine omitted costs, situational frequency,
   execution burden, visibility, feedback loops, and upstream resource access.
6. **Change the smallest responsible parameter set.** Prefer a change whose
   downstream effect is predictable. Avoid simultaneous unrelated adjustments.
7. **Sweep and recalculate.** Run sensitivity or bounded parameter sweeps, then
   execute the same scenarios for current and candidate values. Include new
   breakpoints or optimal strategies.
8. **Compare options.** When more than one fix is credible, show the tradeoff
   between changing power, cost, availability, frequency, counterplay, or
   communication.
9. **Define verification and rollback.** State test population, observation,
   acceptable band, failure signal, and what value should be restored.

## Required artifacts

### Diagnosis table

| Symptom | Confirmed behavior | Root cause/hypothesis | Evidence | Confidence |
| --- | --- | --- | --- | --- |

### Before/after table

| Metric or scenario | Current | Target | Proposal A | Proposal B | Side effect |
| --- | --- | --- | --- | --- | --- |

Use actual calculated values. If a value cannot be calculated, mark the
assumption or required measurement in the cell.

## Decision checks

- The current result is reproducible from authoritative values.
- The proposed change affects the stated root cause.
- Ordinary and optimized scenarios are both covered.
- The proposal does not create a new dominant strategy, dead option, infinite
  loop, economy deficit, or late-game spike.
- Segment averages do not hide a reversal for important groups.
- Player-facing feedback is considered when perception differs from the rule.
- The expected effect is large enough to be perceptible and worth the change.

## Deliverable

Return:

1. reconstructed current model;
2. prioritized diagnosis with evidence status;
3. exact proposed parameter changes and percentage/absolute deltas;
4. temporary-script verification evidence and cleanup status, or the updated
   persistent tool, parameters, reproduction command, and outputs;
5. before/after scenario and sweep results;
6. affected neighboring systems and content;
7. recommended option with reason;
8. verification, stop, and rollback criteria.

## Stop conditions

Use `insufficient evidence` instead of a confident diagnosis when the current
rule cannot be reconstructed, the symptom is not reproducible, or plausible
causes imply opposite changes. State the next measurement or controlled test
that would distinguish them.
