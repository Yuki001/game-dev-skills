# Verification Scripts and Simulation Tools

Use executable artifacts for every non-trivial numeric model. Choose the
artifact lifecycle before writing code: temporary verification scripts prove a
specific calculation or judgment, while persistent tools support repeated
model validation, simulation, exploration, parameter tuning, and regression
checking.

## Choose the lifecycle

| Artifact | Use when | Location | End state |
| --- | --- | --- | --- |
| Temporary verification script | One-off formula check, invariant test, boundary calculation, independent proposal verification, or small parameter comparison | A dedicated task temp directory | Capture the required evidence, then delete the script and scratch outputs |
| Persistent simulation/tuning tool | Designing a full numerical system, repeated parameter changes, many scenarios, ongoing content production, or designer-operated tuning | User-selected location or a project path such as `tools/balance/<system>/` | Retain source, configs, scenarios, checks, and accepted results |

Do not place either artifact inside an installed skill. Do not delete user-
authored files or shared project tools during temporary cleanup; remove only
the exact scratch directory or files created for the current task after their
resolved paths have been verified.

## Temporary verification scripts

Keep a temporary script as small as the decision allows. It should:

- reproduce the exact formula, update order, or rule being checked;
- load or embed only the parameters needed for this judgment;
- check units, probability totals, bounds, invariants, rounding, and a known
  hand-calculated or runtime case;
- run current and proposed values under equivalent scenarios;
- use recorded seeds and enough trials when randomness is material;
- print or write concise results that can be included in the final judgment;
- fail clearly when an assumption, invariant, or target is violated.

Use a temp script instead of building a permanent framework when the code will
not be reused after the current conclusion. Before deletion, preserve in the
analysis or requested deliverable:

- formula/model checked;
- inputs, scenarios, seeds, and trial count;
- current and candidate results;
- pass/fail findings and limitations.

Then delete the temporary script and scratch outputs and state that cleanup was
completed.

## Persistent simulation/tuning tools

Persistent tools should make repeated design work faster and safer. Choose:

- a script or CLI for reproducible batch simulation, enumeration, sweeps, and
  automatic target checks;
- a spreadsheet for direct table editing when formulas remain inspectable;
- a lightweight local web UI for repeated interactive tuning, backed by the
  same model used by the CLI or batch runner.

Prefer the project's language when the tool imports real configuration or
shares formulas with runtime code. Otherwise, prefer a portable Python model.

### Tool contract

A retained tool should provide, as relevant:

- editable parameter input through JSON, CSV, YAML, spreadsheet cells, or clear
  CLI arguments rather than hidden constants;
- model and game/config versions;
- named scenarios with audience, build, content, and horizon assumptions;
- deterministic seeds and repeatable batch execution;
- human-readable summary plus machine-readable CSV or JSON results;
- target ranges and automatic `pass`, `fail`, or `warning` checks;
- invariant checks such as probability totals, non-negative stock, caps,
  conservation, valid transitions, and termination;
- model-fidelity cases that compare tool output with confirmed rules, hand
  calculations, runtime examples, or observed results;
- a regression suite containing every previously corrected model defect;
- parameter overrides, sensitivity, and sweep support without source edits;
- enough logging to locate a failed formula, scenario, or constraint.

Keep the model separate from presentation and file loading so the core logic
can be checked independently.

## Build and verify a persistent tool

1. **Write the model contract.** List inputs, units, formulas, update order,
   target metrics, constraints, scenarios, and intentional omissions.
2. **Implement the smallest useful simulator.** Reproduce authoritative game
   rules; label every approximation.
3. **Add known-case and invariant checks.** Compare at least one result with a
   hand calculation or confirmed runtime example.
4. **Run the current or baseline parameters.** Preserve the baseline output.
5. **Run ordinary and boundary scenarios.** Include optimized or adversarial
   policies when they can change the preferred values.
6. **Run sensitivity and parameter sweeps.** Identify thresholds and influential
   parameters.
7. **Select candidate parameters.** Reject candidates that meet the primary
   target by violating a guardrail or adjacent-system constraint.
8. **Rerun accepted candidates.** Save the exact inputs and before/after output.
9. **Compare with play or telemetry.** Treat a persistent model-runtime gap as
   a model defect or missing behavior, not a reason to tune to the faulty model.

## Model and parameter correction loop

When a result does not meet expectations, classify the failure before changing
values:

| Failure | Required action |
| --- | --- |
| Tool implementation disagrees with the written model | Fix the tool, add the case as a regression, and rerun all model checks |
| Model omits or misrepresents a confirmed game rule or interaction | Revise the model contract and tool together, version the change, and recalibrate before tuning |
| Tool/model matches confirmed behavior but target metrics fail | Keep the model and tune the relevant parameters |
| Runtime/config differs from the intended authoritative values | Resolve the source-of-truth mismatch before model or parameter tuning |
| Observed data are noisy or not comparable to the scenario | Improve the evidence or scenario alignment before deciding what to change |

Use this order:

1. reproduce the mismatch with a minimal scenario;
2. compare each intermediate state or calculation with the authoritative rule;
3. correct the tool or model if fidelity fails;
4. add the mismatch as a permanent regression case;
5. rerun known cases, invariants, ordinary scenarios, and boundary scenarios;
6. tune parameters only after model validation passes;
7. rerun the accepted parameters and compare with play or telemetry again.

Keep model changes separate from parameter changes in version history and
result summaries so a numerical improvement cannot hide a fidelity regression.

## Parameter adjustment

Expose a small set of meaningful tuning knobs. Use one-at-a-time sensitivity
to understand direction, then grid, random, bounded search, or another
appropriate method. Do not start with a black-box optimizer before the model
passes known cases and invariants.

Define targets and guardrails instead of optimizing one unconstrained score.
Return several candidates when they produce meaningfully different valid
experiences. Record parameter ranges, scenario weights, objectives, rejected
candidates, failed guardrails, and selected tradeoffs.

## Persistent result schema

Use this logical shape even when the output format differs:

```text
model_version
game_or_config_version
model_validation_cases
model_changes
parameters
scenarios
seed_and_trial_count
metrics_by_scenario
targets_and_guardrails
pass_fail_warning_results
sensitivity_or_sweep_summary
assumptions_and_omissions
```

## Delivery

For a temporary script, return the verification evidence and cleanup status,
not a stale scratch-file path.

For a persistent tool, return:

- source and parameter/config files;
- exact reproduction command or interaction;
- baseline and accepted result files;
- model-fidelity and regression results, including any model/tool revisions;
- target/guardrail and sweep summary;
- selected parameters, rejected alternatives, and known model-runtime gaps.
