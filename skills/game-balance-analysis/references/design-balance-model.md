# Design a Balance Model

Use this playbook to create first-pass numbers for a new or incompletely tuned
system. Produce an editable model and concrete values; do not stop at design
principles.

## Required inputs

Collect or infer:

- balance target: mathematical relationship, difficulty, progression, initial
  conditions, strategy viability, object value, fairness, or a stated mix;
- target player experience and audience;
- player actions and meaningful choices;
- resources, costs, rewards, and state changes;
- session, encounter, progression, or season horizon;
- content counts and important milestones;
- technical or production constraints;
- existing fixed values that must be preserved.

If inputs are incomplete, state a small set of assumptions and continue with
adjustable ranges. Ask only when different answers would require fundamentally
different models.

## Procedure

1. **Choose player-facing targets.** Express the desired result as measurable
   ranges: encounter duration, actions to defeat, time to unlock, purchases per
   session, failure band, option value, or another observable outcome.
2. **Classify the relationships.** Mark compared options as transitive,
   intransitive, situational, or mixed so the model uses the right comparison.
3. **Map the system.** List resources and actions with their units. Record
   sources, sinks, conversions, caps, cooldowns, probabilities, and feedback
   loops that affect the target.
4. **Choose an anchor.** Select one ordinary outcome or reference object and
   give it a baseline value. Scale related values from that anchor instead of
   inventing every parameter independently.
5. **Write the equations.** Define how inputs produce player-facing outcomes.
   Keep constants and tuning knobs explicit.
6. **Implement the model.** For a numerical system intended for continued
   tuning, build and retain the domain simulator described in
   `simulation-and-tooling.md`. Use temporary scripts for isolated formula or
   known-case checks. Confirm one
   known or hand-calculated case before using the persistent tool for design.
7. **Validate model fidelity.** Compare intermediate and final results with
   confirmed rules and known cases. If the model or simulator is wrong, update
   both, add the failed case as a regression, and rerun validation before
   designing parameters.
8. **Generate first-pass values.** Fill the full required range, including
   content tiers or progression milestones. Prefer simple relationships until
   the design requires a breakpoint or hand-authored exception.
9. **Run scenarios.** Calculate at least low, expected, high-skill or optimized,
   and edge cases relevant to the game.
10. **Sweep and adjust.** Use sensitivity or bounded parameter sweeps to find
   candidates that meet the target without violating guardrails. Rerun the
   selected values and identify adjacent systems that also moved.
11. **Define validation.** State what a playtest or data sample must show before
   the first pass is accepted.

## Required artifacts

### Target table

| Outcome | Target range | Audience/segment | Horizon | Rationale |
| --- | --- | --- | --- | --- |

### Parameter table

| Parameter | Unit | Initial value/range | Formula or source | Tuning role |
| --- | --- | --- | --- | --- |

### Scenario table

| Scenario | Inputs/build | Calculated outcome | Target | Status |
| --- | --- | --- | --- | --- |

Use `within`, `below`, or `above` for status and explain material misses.

## Decision checks

- Every number has a unit and affects a named player-facing outcome.
- The anchor produces the intended ordinary case.
- Early, middle, late, and extreme values have been calculated.
- No legitimate option strictly dominates another unless dominance is
  intentional and priced accordingly.
- Resource stocks remain bounded over the intended horizon.
- A random reward is described by its distribution, not only its average.
- Rounding, caps, and breakpoints are explicit.
- The model exposes a small set of predictable tuning knobs.
- The retained simulator passes a known case, invariants, target checks, and
  the required scenario set; model defects have regression cases.

## Deliverable

Return:

1. assumptions and fixed constraints;
2. target, parameter, and scenario tables;
3. equations and verification evidence from any temporary scripts used;
4. persistent simulator, parameter/config files, reproduction command, and
   result files;
5. recommended first-pass values, not merely example values;
6. sensitivity/sweep summary and rejected candidates;
7. known omissions and a concrete validation plan.

## Stop conditions

Do not present values as ready for production when the player-facing target is
unresolved, a required cross-system rule is unknown, or the model cannot be
checked against any representative scenario. Deliver a labeled provisional
model and list the smallest missing decisions instead.
