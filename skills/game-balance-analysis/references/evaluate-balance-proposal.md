# Evaluate a Balance Proposal

Use this playbook to judge a proposed parameter set, patch, character, item,
economy rule, progression curve, reward table, or comparison between options.
End with an explicit verdict supported by calculations and design constraints.

## Required inputs

Identify:

- the proposal and its stated goal;
- current and proposed values;
- target audience, mode, content, and time horizon;
- baseline or alternatives being compared;
- expected player behavior and success signal;
- evidence or model used by the proposer.

When there is no explicit baseline, reconstruct the current state or choose a
clearly labeled reference case.

## Procedure

1. **Restate the claim.** Convert the proposal into a falsifiable statement,
   such as "reduces optimized TTK without changing ordinary TTK by more than
   5%."
2. **Classify the relationship.** Determine whether compared options are
   transitive, intransitive, situational, or mixed. Do not evaluate every set
   against one absolute power curve.
3. **Build an independent verifier.** By default, implement the relevant
   formulas and scenarios as a temporary verification script through
   `simulation-and-tooling.md`; run it and delete it after the verdict and
   evidence are captured. Use or create a persistent tool only when ongoing
   evaluation is part of the request. Do not accept supplied spreadsheet
   totals, simulator output, or percentages without checking formulas, units,
   ranges, rounding, and one known case.
4. **Validate the model.** When a persistent simulator is used, compare it with
   confirmed rules, intermediate states, and regression cases. Fix and version
   the model/tool before judging proposed parameters if fidelity fails.
5. **Compare equivalent scenarios.** Hold content, skill, build, map, opponent,
   and horizon constant unless the proposal intentionally changes them.
6. **Check real costs and benefits.** Include action time, slots, risk,
   availability, setup, reliability, information, and situational frequency.
7. **Stress and sweep the proposal.** Test ordinary, optimized, weak, strong,
   and boundary cases, then sweep the parameters that can reverse the verdict.
8. **Check whether the difference is harmful.** Preserve intentional
   asymmetry, identity, discovery, or accessibility when the choice space and
   fairness remain healthy. Do not recommend equality solely because values
   differ.
9. **Trace side effects.** Identify thresholds, curves, economies, rewards,
   counters, and adjacent options changed by the proposal.
10. **Judge evidence.** Separate calculated prediction from playtest or telemetry
   confirmation.
11. **Issue a verdict.** Use one of the defined verdicts and state the minimum
   correction or validation required.

## Verdicts

- `accept`: the proposal meets the target across relevant cases and has no
  material unaddressed risk;
- `accept with conditions`: acceptable if named monitoring, content, or rollout
  conditions are met;
- `revise`: direction is sound, but specific parameters or omissions must be
  corrected;
- `reject`: the proposal contradicts the target, creates a more serious issue,
  or is based on an invalid model;
- `insufficient evidence`: required rules, data, or comparison cases are
  missing and plausible answers change the verdict.

## Required artifacts

### Proposal comparison

| Metric/scenario | Current | Proposed | Target | Delta | Result |
| --- | --- | --- | --- | --- | --- |

### Risk table

| Risk | Trigger | Impacted players/content | Mitigation or test |
| --- | --- | --- | --- |

## Decision checks

- The proposal improves the stated target rather than a convenient proxy.
- Percentage changes are translated into player-facing outcomes.
- Averages do not hide critical matchups, tiers, or skill bands.
- No compared option is evaluated under a more favorable scenario.
- The change is large enough to matter but not larger than required.
- New breakpoints, loops, exploits, or dominant combinations are addressed.
- A difference is changed because it harms choice, fairness, or the intended
  experience, not merely because it is numerically unequal.
- Confidence matches the strength of the evidence.

## Deliverable

Return the verdict first, followed by the independent verification evidence,
temporary-script cleanup status or retained-tool path, verified calculations,
sweep results, failed or passed checks, tradeoffs, exact required revisions,
and the smallest validation needed to finalize the decision.
