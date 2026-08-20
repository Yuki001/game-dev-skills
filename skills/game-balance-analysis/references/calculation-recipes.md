# Balance Calculation Recipes

Read only the recipes needed for the current task. Each recipe must produce
inspectable inputs, formulas, results, and checks. Use a spreadsheet for
editable design tables and a script for large enumeration, simulation, or
repeated analysis.

Implement selected recipes in a temporary verification script or a persistent
simulation/tuning tool according to `simulation-and-tooling.md`. Temporary
scripts prove the current calculation and are deleted after judgment;
persistent tools retain parameter input, scenarios, seeds, sweeps, target
checks, and result files for repeated use.

## Shared model rules

- Put constants and assumptions in named inputs rather than repeated formulas.
- Record units and rule/config version.
- Separate input, calculation, output, and validation areas.
- Keep per-step and cumulative values distinct.
- Validate one representative result by hand.
- Calculate low, expected, high/optimized, and boundary cases as relevant.
- Preserve source data and seeds for reproducible stochastic results.

## Recipe: Select and validate a progression curve

### Inputs

Progression index, target per-step and cumulative outcomes, starting and ending
values, milestone durations, earning or opposing-power curve, perceptible
increment, and legitimate minimum/maximum range.

### Candidate shapes

```text
identity:       y = x
linear:         y = a + b*x
exponential:    y = a*r^x
logarithmic:    y = a + b*log(x)
triangular:     cumulative_y_n = k*n*(n+1)/2
piecewise:      use different documented rules across milestone ranges
```

Choose by intended outcome:

- identity for direct exchange or one-to-one scaling;
- linear for a constant increment;
- exponential for compounding or constant multiplicative growth;
- logarithmic for strong early gains followed by diminishing returns;
- triangular for cumulative cost whose per-step increase is linear;
- piecewise for onboarding, content tiers, caps, or deliberate local peaks.

### Check and output

- Calculate per-step and cumulative values at start, early, middle, late, end,
  and one point beyond the intended range.
- Compare the curve with earning rate, challenge power, and player-facing time;
  a smooth parameter curve can still produce erratic experience.
- Flag zero/negative-domain errors, overflow, imperceptible increments, sharp
  breakpoints, and caps reached during ordinary play.
- Output candidate formula, parameters, milestone table, player-facing outcome,
  rejected alternatives, and reason for the selected curve.

## Recipe: Combat output and TTK

### Inputs

Damage components, action timing, hit probability, critical rule, resource
cost, reload/cooldown/recovery, target health, mitigation, healing, and relevant
combat windows.

### Compute

```text
expected_damage_per_action = sum(outcome_probability * outcome_damage)
cycle_time = action_time + required_recovery + amortized_reload_or_cooldown
sustained_output = expected_damage_per_action / cycle_time
```

Use the game's real mitigation rule. For a simple constant damage reduction
`r` below 1:

```text
effective_health = health / (1 - r)
```

Calculate discrete actions to defeat with the actual rounding and first-action
timing. Use a short turn/time simulation when healing, phases, control,
cooldowns, priorities, or random effects make a closed formula misleading.

### Check and output

- Compare burst and sustained output.
- Include miss, downtime, overkill, wasted area/healing, and resource limits.
- Output option, expected action value, cycle time, sustained value, actions to
  defeat, TTK, resource efficiency, and scenario.

## Recipe: Progression and time to milestone

### Inputs

Per-level or milestone requirements, earning rates by activity, expected
activity mix, success rate, session length, player/challenge power, and unlocks.

### Compute

```text
cumulative_requirement_n = sum(step_requirement_1 through step_requirement_n)
time_to_step = step_requirement / effective_earning_rate
cumulative_time_n = sum(time_to_step_1 through time_to_step_n)
power_ratio = player_power / challenge_power
```

Use separate paths for ordinary, underpowered legitimate, optimized, and catch-
up players. If earning rate changes with power, calculate it at every milestone
instead of holding it constant.

### Check and output

- Flag abrupt changes in time, power ratio, or unlocked decisions.
- Show per-step and cumulative values.
- Output milestone, requirement, earning rate, time, cumulative time, player
  power, challenge power, ratio, unlock, and status.

## Recipe: Economy stock and affordability

### Inputs

Starting stock, source and sink rates, conversions, transfers, cap/decay/reset,
prices, activity rate, and segment horizon.

### Compute

```text
stock_next = opening_stock + sources - sinks + incoming - outgoing
net_flow = sources - sinks + incoming - outgoing
time_to_afford = max(0, price - current_stock) / positive_net_earning_rate
```

Apply caps, floors, resets, and conditional purchases in the order used by the
game. If net earning is zero or negative, report the purchase as unreachable
under the modeled path instead of dividing by zero. Simulate by
session/day/turn when actions change future rates.

### Check and output

- Find first surplus, deficit, cap, blocked purchase, and runaway loop.
- Run multiple player segments and the full economy horizon.
- Output time row, opening stock, each source/sink, transfers, purchases,
  closing stock, and blocked/available decisions.

## Recipe: Compare options and situational value

### Inputs

Every relevant benefit and cost, units, content or matchup scenarios, scenario
frequency/weight, availability, setup, reliability, slots, and execution band.

Classify the set before calculating:

- `transitive`: compare benefit against cost or disadvantage;
- `intransitive`: use matchup/payoff relations and counter cycles;
- `situational`: weight value by the situations that actually occur;
- `mixed`: report separate models rather than one false total.

### Compute

For comparable scenario values:

```text
weighted_value = sum(scenario_weight * value_in_scenario)
net_modeled_value = weighted_value - modeled_costs
```

Keep non-convertible costs visible instead of assigning unsupported weights.
Identify strict dominance only after all legitimate scenarios and costs are
included.

### Check and output

- Recompute with low/high scenario weights to show sensitivity.
- Identify breakpoints where the preferred option changes.
- Output option, scenario values, weighted value, explicit costs, omitted
  factors, strong/weak situation, and dominance/viability result.

## Recipe: Weighted rewards and streaks

### Inputs

Weights/probabilities, reward values, roll frequency, selection stages,
replacement rule, pity/guarantee state, duplicate protection, and horizon.

### Compute

```text
probability_i = weight_i / sum(weights)
expected_value = sum(probability_i * value_i)
P(at_least_one_success_in_n_independent_trials) = 1 - (1 - p)^n
P(no_success_in_n_independent_trials) = (1 - p)^n
```

For `K` desired cards in a deck of `N`, drawing `n` without replacement:

```text
P(at_least_one) = 1 - C(N-K, n) / C(N, n)
```

Use zero for impossible combinations. Model pity and stateful rules as state
transitions or simulation; do not reuse the initial probability for every
trial.

### Check and output

- Verify probabilities at every stage sum to 1.
- Report expected value, median/percentiles, no-success probability, attempts
  to first success, high tail, and maximum guaranteed attempts.
- Cross-check nested tables using effective final-item probability.

## Recipe: Iterative or Monte Carlo simulation

### Inputs

Initial state, action policy, transition order, random distributions, terminal
condition, maximum steps, trial count, seeds, and recorded outputs.

### Compute

```text
state_next = transition(state_current, action, environment, random_input)
```

Use exact enumeration when all outcomes are tractable. Otherwise run seeded
trials, record distributions rather than only means, and repeat with independent
seeds or batches.

### Check and output

- Stop non-terminating trials and report their rate.
- Verify an exact or hand-calculated subcase.
- Report trial count, seeds, runtime, mean, median, percentiles, tails, and
  uncertainty appropriate to the decision.
- Do not report an unobserved rare event as probability zero.

## Recipe: PvP matchup matrix

### Inputs

Choices or strategies, consistent payoff definition, matches or modeled
outcomes, sample counts, skill/map/side segments, and availability/cost.

### Compute

Build one row per choice and one column per opponent choice. Record win rate,
score differential, or another consistent payoff. Calculate weighted overall
results only after displaying within-matchup cells.

### Check and output

- Identify dominated rows/columns, counter cycles, sparse cells, and segment
  reversals.
- Do not force a unique mixed-strategy solution for singular, noisy,
  multiplayer, sequential, or non-zero-sum cases.
- Output matrix value and sample/assumption matrix together.

## Recipe: Before/after telemetry comparison

### Inputs

Decision, current/proposed version, numerator and denominator, population,
segments, observation window, exclusions, and target effect.

### Compute

```text
rate = numerator / denominator
absolute_change = proposed_rate - current_rate
relative_change = absolute_change / current_rate
```

When the current rate is zero, omit relative change and report the absolute
change with counts. Also report distribution summaries and uncertainty. Use a
statistical test only after checking its assumptions through
`evidence-and-validation.md`.

### Check and output

- Compare equivalent segments and exposure.
- Separate practical effect size from statistical significance.
- Output current, proposed, absolute and relative change, target, sample count,
  segment, and evidence limitation.
