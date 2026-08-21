# Balance Calculation Recipes

Read only the recipes needed for the current task. Each recipe must produce
inspectable inputs, formulas, results, and checks. Use a spreadsheet for
editable design tables and a script for large enumeration, simulation, or
repeated analysis.

Implement selected recipes in a temporary verification script or a persistent
simulation/tuning tool according to `simulation-and-tooling.md`. Temporary
scripts prove the current calculation; persistent tools retain parameter
input, scenarios, seeds, sweeps, target checks, and result files for repeated
use.

## Recipe index

- First-pass values: [progression curves](#recipe-select-and-validate-a-progression-curve)
  and [cost curves](#recipe-build-supporting-math-and-a-cost-curve)
- Player-facing outcomes: [combat and TTK](#recipe-combat-output-and-ttk),
  [progression timing](#recipe-progression-and-time-to-milestone), and
  [economy stock](#recipe-economy-stock-and-affordability)
- Option and reward value: [situational comparison](#recipe-compare-options-and-situational-value),
  [probability building blocks](#recipe-probability-building-blocks-and-common-distributions),
  and [weighted rewards](#recipe-weighted-rewards-and-streaks)
- Stateful models: [iterative simulation](#recipe-iterative-or-monte-carlo-simulation)
  and [Markov analysis](#recipe-state-transition-and-markov-analysis)
- Competitive systems: [power trajectory](#recipe-pvp-power-and-feedback-trajectory),
  [matchup matrix](#recipe-pvp-matchup-matrix),
  [initial-condition advantage](#recipe-initial-condition-and-side-advantage),
  and [rating calibration](#recipe-rating-prediction-and-calibration)
- Observed evidence: [descriptive statistics](#recipe-descriptive-statistics-and-uncertainty)
  and [before/after telemetry](#recipe-beforeafter-telemetry-comparison)

## Shared model rules

- Put constants and assumptions in named inputs rather than repeated formulas.
- Record units and rule/config version.
- Separate input, calculation, output, and validation areas.
- Keep per-step and cumulative values distinct.
- Validate one representative result by hand.
- Calculate low, expected, high/optimized, and boundary cases as relevant.
- Preserve source data and seeds for reproducible stochastic results.
- Validate every probability is in `[0, 1]`, every required denominator is
  non-zero, and all logarithm, root, and inverse inputs are in their domains.
- State whether time and counts are continuous or discrete; use the game's
  actual rounding and event order for discrete outcomes.

## Recipe: Select and validate a progression curve

### Inputs

Progression index, target per-step and cumulative outcomes, starting and ending
values, milestone durations, earning or opposing-power curve, perceptible
increment, and legitimate minimum/maximum range.

### Candidate shapes

```text
identity:                y = x
linear point value:      y = a + b*x
arithmetic step:         step_i = a + (i - 1)*d
arithmetic cumulative:   cumulative_n = n*(2*a + (n - 1)*d)/2
exponential point value: y = a*r^x
geometric step:          step_i = a*r^(i - 1)
geometric cumulative:    cumulative_n = a*(r^n - 1)/(r - 1), r != 1
logarithmic:             y = a + b*log_base(x)
triangular from 1..n:    cumulative_n = k*n*(n + 1)/2
piecewise:               use documented rules across milestone ranges
```

Define the starting index. `n*(n+1)/2` sums `1..n`; `x*(x-1)/2` sums
`0..x-1`. Do not exchange them without shifting the index.

When fitting a curve through endpoints:

```text
linear_b = (y_end - y_start) / (x_end - x_start)
linear_a = y_start - linear_b*x_start
exponential_r = (y_end / y_start)^(1 / (x_end - x_start))
exponential_a = y_start / exponential_r^x_start
```

The exponential fit requires positive endpoint values. For logarithms require
`x > 0`, `base > 0`, and `base != 1`. When `r = 1`, geometric cumulative is
`n*a`.

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

## Recipe: Build supporting math and a cost curve

### Inputs

Anchor unit, resource price or progression position, every benefit and
drawback, attribute quantities and unit values, slots, availability,
reliability, setup, interactions, target curve, and accepted anchor objects.

### Compute

```text
total_benefit = sum(attribute_quantity_j * attribute_unit_value_j)
                + interaction_terms
total_cost = resource_cost + modeled_drawbacks + opportunity_costs
balance_delta = total_benefit - target_benefit_at_cost
identity_curve_delta = total_benefit - total_cost - target_offset
```

Use `target_offset = 0` when balanced objects should net to zero. Keep
interaction terms explicit: a combined effect may be stronger or weaker than
the sum of its parts. Derive probabilistic or situational attributes through
the relevant recipes below rather than assigning unsupported point values.

### Check and output

- Reproduce the accepted anchors before pricing new objects.
- Test discrete thresholds, slots, reliability, and combinations that break a
  smooth or additive curve.
- Output each cost/benefit contribution, interaction term, target value,
  balance delta, above/below-curve status, and sensitivity to uncertain values.

## Recipe: Combat output and TTK

### Inputs

Damage components, action timing, hit probability, critical rule, resource
cost, reload/cooldown/recovery, target health, mitigation, healing, and relevant
combat windows.

### Compute

```text
expected_damage_per_action = sum(outcome_probability * outcome_damage)
cycle_time = next_action_ready_time - current_action_start_time
sustained_output = expected_damage_per_action / cycle_time
```

Calculate `next_action_ready_time` from the real timing rules. When cooldown
starts at action start and reload does not overlap it, a common special case is:

```text
cycle_time = max(action_time + recovery_time, cooldown_from_action_start)
             + amortized_reload_time
```

Use the game's real mitigation rule. For a simple constant damage reduction
`0 <= r < 1`:

```text
effective_health = health / (1 - r)
hits_to_defeat = ceil(health / damage_after_mitigation_per_hit)
TTK = first_hit_time + (hits_to_defeat - 1)*cycle_time
```

The hit and TTK formulas are deterministic baselines. Do not take the ceiling
of an expected damage value and call it expected TTK. When the only randomness
is an independent hit probability `p` per attack and damage and cycle time are
constant per attack, use the negative-binomial closed form from the
[probability building-blocks recipe](#recipe-probability-building-blocks-and-common-distributions)
instead of a simulation:

```text
expected_attacks_to_defeat = hits_to_defeat / p
expected_TTK = first_attack_time + (expected_attacks_to_defeat - 1)*cycle_time
```

`first_attack_time` is the time of the first attack attempt, hit or miss. Use
exact enumeration or a short turn/time simulation when random damage, healing,
phases, control, priorities, or resource state makes a closed formula
misleading.

### Check and output

- Compare burst and sustained output.
- Include miss, downtime, overkill, wasted area/healing, and resource limits.
- Require `cycle_time > 0`, exhaustive outcome probabilities summing to 1,
  and positive post-mitigation damage for a reachable defeat.
- Output option, expected action value, cycle time, sustained value, actions to
  defeat, TTK, resource efficiency, and scenario.

## Recipe: Progression and time to milestone

### Inputs

Per-level or milestone requirements, earning rates by activity, expected
activity mix, success rate, session length, player/challenge power, reward
timestamps or intervals, and unlocks. Use normalized challenge and skill
components only when a perceived-challenge score is required.

### Compute

```text
cumulative_requirement_n = sum(step_requirement_1 through step_requirement_n)
continuous_time_to_step = step_requirement / effective_earning_rate
discrete_steps_to_step = ceil(step_requirement / net_earning_per_step)
cumulative_continuous_time_n = sum(continuous_time_to_step_1
                                   through continuous_time_to_step_n)
cumulative_discrete_steps_n = sum(discrete_steps_to_step_1
                                  through discrete_steps_to_step_n)
power_ratio = player_power / challenge_power
progression_velocity_t = (progress_t - progress_(t-1)) / delta_time
progression_acceleration_t = (velocity_t - velocity_(t-1)) / delta_time
mean_reward_interval = sum(reward_intervals) / count(reward_intervals)
reward_density = reward_count / time_or_content_span
maximum_reward_drought = max(reward_intervals)
```

When all components share a documented normalized scale, an optional
perception diagnostic is:

```text
perceived_challenge = virtual_challenge + skill_challenge
                       - virtual_player_power - actual_player_skill
```

Use separate paths for ordinary, underpowered legitimate, optimized, and catch-
up players. If earning rate changes with power, calculate it at every milestone
instead of holding it constant.

### Check and output

- Flag abrupt changes in time, power ratio, or unlocked decisions.
- Require positive earning rate, net earning per step, challenge power, and
  time span for the corresponding divisions. Calculate interval metrics only
  when at least one valid reward interval exists.
- Show per-step and cumulative values, reward clusters, and reward droughts.
- Output milestone, requirement, earning rate, time, cumulative time, player
  power, challenge power, ratio, unlock, and status.

## Recipe: Economy stock and affordability

### Inputs

Starting stock, source and sink rates, conversions, transfers, cap/decay/reset,
prices or representative price-index basket, per-player stock distribution,
active player counts, activity rate, and segment horizon.

### Compute

```text
stock_next = opening_stock + sources - sinks + incoming - outgoing
net_flow = sources - sinks + incoming - outgoing
continuous_time_to_afford = max(0, price - current_stock)
                            / positive_net_earning_rate
discrete_steps_to_afford = ceil(max(0, price - current_stock)
                                / net_earning_per_step)
conversion_output = conversion_input * conversion_rate * (1 - fee_rate)
conversion_cycle_multiplier = product(conversion_rate_i * (1 - fee_rate_i))
payback_time = upgrade_cost / incremental_net_income_rate
inflation_rate = price_index_t / price_index_(t-1) - 1
top_share = sum(largest share_count stocks) / total_stock
gini = (2*sum(i * stock_i_ascending)) / (player_count * total_stock)
       - (player_count + 1)/player_count
aggregate_net_creation = aggregate_created - aggregate_destroyed
per_capita_net_creation = aggregate_net_creation / active_players
```

`gini` requires every included stock to be non-negative and sorted ascending,
with `i` from 1 to `player_count`. If debt is legitimate, report debt
separately or use a documented debt-compatible inequality measure.
`aggregate_created` and `aggregate_destroyed` are population totals in the
target resource. Count conversions that create or destroy that resource, and
exclude internal transfers that cancel across the population.

Apply caps, floors, resets, and conditional purchases in the order used by the
game. If net earning is zero or negative, report the purchase as unreachable
under the modeled path instead of dividing by zero. Simulate by
session/day/turn when actions change future rates. Replace the proportional
fee formula with the game's actual flat, tiered, minimum, or ordered fee rules.

Treat a repeatable conversion cycle with `conversion_cycle_multiplier > 1` as
an arbitrage or duplication defect unless an omitted time, capacity, risk, or
other cost removes the gain. Use `payback_time` only when incremental income
is positive and stable; otherwise simulate the changing income path. For an
open market, find candidate equilibrium prices where
`supply_quantity(price) = demand_quantity(price)` rather than inventing a
universal price equation.

For open or long-lived economies, monitor distribution health as well as
totals: report top share and Gini per segment and horizon, and compare
per-capita net currency creation with the price index over the same window.
Treat a persistent gap between money growth and price/sink adjustment as an
inflation warning to investigate, not proof of a defect; treat rising
concentration alongside stagnant new-player stock as a guardrail failure only
when it violates a documented concentration or new-player-access target.

### Check and output

- Find first surplus, deficit, cap, blocked purchase, and runaway loop.
- Reject invalid divisions, negative post-fee conversion rates, price-index
  comparisons with a non-positive baseline, and concentration metrics with a
  negative included stock or non-positive total stock. Report population size
  and the top-share definition when comparing concentration across populations.
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
normalized_weight_i = scenario_weight_i / sum(scenario_weights)
weighted_value = sum(normalized_weight_i * value_in_scenario_i)
net_modeled_value = weighted_value - modeled_costs
```

When the player can keep and switch among options, calculate the new option's
marginal value against the existing loadout instead of its standalone value:

```text
marginal_loadout_value = sum(normalized_weight_i
    * (best_value_with_new_option_i - best_existing_value_i))
switch_adjusted_value = marginal_loadout_value - setup_and_switch_costs
```

Keep non-convertible costs visible instead of assigning unsupported weights.
Identify strict dominance only after all legitimate scenarios and costs are
included. Include future opportunity, setup, and switching costs; do not
subtract an already-irrecoverable sunk cost from a forward-looking choice.

### Check and output

- Recompute with low/high scenario weights to show sensitivity.
- Identify breakpoints where the preferred option changes.
- Require non-negative scenario weights with a positive total and compare the
  freely-switchable, costly-switching, and locked-in cases when relevant.
- Output option, scenario values, weighted value, explicit costs, omitted
  factors, strong/weak situation, and dominance/viability result.

## Recipe: Probability building blocks and common distributions

### Inputs

Events and outcomes, possibility-space size, conditional order, independence,
replacement rule, trial count, success probability, and whether order matters.

### Compute

```text
P(not A) = 1 - P(A)
P(A and B) = P(A) * P(B given A)
P(A and B, independent) = P(A) * P(B)
P(A or B) = P(A) + P(B) - P(A and B)
P(A given B) = P(B given A) * P(A) / P(B)
C(n,k) = n! / (k!*(n-k)!)
Perm(n,k) = n! / (n-k)!
P(binomial X=k) = C(n,k)*p^k*(1-p)^(n-k)
E(binomial X) = n*p
Var(binomial X) = n*p*(1-p)
P(geometric T=t) = (1-p)^(t-1)*p
E(geometric T) = 1/p
Var(geometric T) = (1-p)/p^2
P(negative_binomial T=t for the k-th success) = C(t-1, k-1)*p^k*(1-p)^(t-k)
E(negative_binomial T) = k/p
Var(negative_binomial T) = k*(1-p)/p^2
P(final outcome) = sum_over_paths(product(conditional_probability_on_path))
```

Use combinations when order does not matter and permutations when it does.
The binomial, geometric, and negative-binomial formulas require independent
trials with constant `p`; use a state model when pity, depletion, memory, or
player actions change the probability. The negative binomial gives a closed
form for expected attempts to reach `k` successes, such as landing
`hits_to_defeat` hits under a constant miss chance, before reaching for
simulation.

### Check and output

- Require integer `n >= 0`, valid `k`, `0 <= p <= 1`, and a non-zero Bayes
  denominator. Require `p > 0` for geometric mean/variance, and `p > 0` with
  integer `k >= 1` for the negative binomial. Define `0! = 1`.
- Confirm mutually exclusive outcomes sum to 1 and independently enumerate a
  small equivalent case.
- Output event tree or paths, formula assumptions, exact probability, and the
  enumeration or simulation cross-check.

## Recipe: Weighted rewards and streaks

### Inputs

Weights/probabilities, reward values, roll frequency, selection stages,
replacement rule, pity/guarantee state, duplicate protection, and horizon.

### Compute

```text
probability_i = weight_i / sum(weights)
expected_value = sum(probability_i * value_i)
expected_utility = sum(probability_i * utility(outcome_i, player_state))
variance = sum(probability_i * (value_i - expected_value)^2)
P(at_least_one_success_in_n_independent_trials) = 1 - (1 - p)^n
P(no_success_in_n_independent_trials) = (1 - p)^n
```

For `K` desired cards in a deck of `N`, drawing `n` without replacement:

```text
P(at_least_one) = 1 - C(N-K, n) / C(N, n)
P(exactly_k_desired) = C(K, k)*C(N-K, n-k) / C(N, n)
E(desired_count) = n*K / N
```

For a uniform collection of `N` distinct rewards drawn with replacement:

```text
H_N = sum(1/i for i = 1..N)
expected_draws_to_complete = N*H_N
Var(draws_to_complete) = N^2*sum(1/i^2 for i = 1..N) - N*H_N
```

The coupon-collector formulas require equal draw probability for each
remaining reward and independence between draws; simulate when weights are
unequal, pity applies, or the pool is stateful.

Define `C(n,k) = 0` for an impossible numerator combination inside an otherwise
valid experiment. Reject invalid deck or draw inputs such as `n > N` instead
of dividing by zero. Model pity and stateful rules as state transitions or
simulation; do not reuse the initial probability for every trial.

### Check and output

- Verify probabilities at every stage sum to 1.
- Require non-negative weights with a positive total. Keep nominal value and
  state-dependent player utility separate.
- Report expected value, expected utility, variance, median/percentiles,
  no-success probability, attempts to first success, high tail, and maximum
  guaranteed attempts.
- Cross-check nested tables using effective final-item probability.

## Recipe: Iterative or Monte Carlo simulation

### Inputs

Initial state, action policy, transition order, random distributions, terminal
condition, maximum steps, trial count, seeds, and recorded outputs.

### Compute

```text
state_next = transition(state_current, action, environment, random_input)
Monte_Carlo_standard_error_of_mean = sample_standard_deviation
                                     / sqrt(independent_trial_count)
```

Use exact enumeration when all outcomes are tractable. Otherwise run seeded
trials, record distributions rather than only means, and repeat with independent
seeds or batches.

### Check and output

- Stop non-terminating trials and report their rate.
- Verify an exact or hand-calculated subcase.
- Require more than one independent trial before estimating standard error
  from a sample standard deviation.
- Report trial count, seeds, runtime, mean, median, percentiles, tails, and
  uncertainty appropriate to the decision.
- Do not report an unobserved rare event as probability zero.

## Recipe: State-transition and Markov analysis

### Inputs

Finite states, initial state-probability vector, transition order and matrix,
absorbing states, time step, rewards by state or transition, and horizon.
Choose and document a row- or column-stochastic convention; the formulas below
use columns as source states.

### Compute

```text
state_probability_(t+1) = transition_matrix * state_probability_t
state_probability_t = transition_matrix^t * initial_probability
finish_cdf_t = sum(probability_in_absorbing_states_at_t)
finish_pmf_t = finish_cdf_t - finish_cdf_(t-1)
expected_finish_time = sum(t * finish_pmf_t)
steady_state = transition_matrix * steady_state
```

For an absorbing chain split into transient block `Q` and transient-to-
absorbing block `R` under the same column convention:

```text
fundamental_matrix = inverse(I - Q)
expected_steps_from_start = ones^T * fundamental_matrix * transient_start
absorption_probabilities = R * fundamental_matrix * transient_start
```

Use a linear solve rather than explicitly forming an inverse in production
code. Fall back to seeded simulation when the state space is too large or the
player policy cannot be fixed credibly.

### Check and output

- Require non-negative entries, each source column summing to 1, and the state
  vector summing to 1 after representative transitions.
- Verify one small chain by hand and flag unreachable states, non-terminating
  classes, and singular `I - Q`.
- If absorbing probability does not approach 1, report the non-termination
  probability and do not present a truncated finite mean as unconditional.
- Do not claim a unique limiting steady state without checking recurrence,
  irreducibility, and periodicity as relevant.
- Output state definitions, matrix convention, transient distributions,
  absorption/steady-state results, expected duration, and truncation error.

## Recipe: PvP power and feedback trajectory

### Inputs

One consistently scaled power measure per player/team and time step, match
phase, leader identity, win-likelihood estimate, finish time, and threshold for
a strategically decided result.

### Compute

```text
total_power_t = sum(player_power_i_t)
net_power_change_t = total_power_t - total_power_(t-1)
leader_advantage_t = leader_power_t - strongest_other_power_t
advantage_velocity_t = (leader_advantage_t - leader_advantage_(t-1))
                       / delta_time
strategically_decided_time = first sustained threshold crossing
cleanup_time = actual_finish_time - strategically_decided_time
```

Use total-power change to classify positive-, zero-, or negative-sum phases.
Use the direction and persistence of leader-advantage change to diagnose
snowball or catch-up feedback; do not infer feedback from a single match.
Define a near-zero tolerance for sum classification. Define a sustained
crossing with a documented win-likelihood threshold and hold window.

### Check and output

- Verify the power scale predicts meaningful outcomes and does not conceal
  territory, information, economy, or action-economy reversals.
- Segment by side, map, skill, matchup, and version; report distributions of
  decided time and cleanup time rather than one trajectory.
- Output phase, each side's power, total power, leader advantage, recovery
  probability/path, meaningful decisions remaining, and guardrail status.

## Recipe: PvP matchup matrix

### Inputs

Choices or strategies, consistent payoff definition, matches or modeled
outcomes, sample counts, skill/map/side segments, and availability/cost.

### Compute

Build one row per choice and one column per opponent choice. Record win rate,
score differential, or another consistent payoff. Calculate weighted overall
results only after displaying within-matchup cells.

For a simultaneous two-player zero-sum game with row-player payoff matrix `A`,
solve mixed strategies by linear programming when an equilibrium is useful:

```text
row player: maximize v subject to A^T*x >= v*1, sum(x) = 1, x >= 0
column player: minimize v subject to A*y <= v*1, sum(y) = 1, y >= 0
```

The solution gives equilibrium strategy probabilities and game value `v`.
Do not use a matrix-inverse shortcut unless the matrix is square, non-singular,
and a full-support solution is known to exist.

### Check and output

- Identify dominated rows/columns, counter cycles, sparse cells, and segment
  reversals.
- Do not force a unique mixed-strategy solution for noisy, multiplayer,
  sequential, general-sum, or multiple-equilibrium cases.
- Output payoff and sample/assumption matrices together, plus equilibrium
  probabilities and exploitability only when the assumptions fit.

## Recipe: Initial-condition and side advantage

### Inputs

Initial conditions to compare (first move, side, spawn, map, or starting
stock), equivalent matched samples or swap experiments per condition,
compensation candidates and their cost unit, target win rate, and other
systems the compensation touches.

### Compute

For a two-condition symmetric game from equivalent samples:

```text
advantage = win_rate_condition_A - win_rate_condition_B
```

Prefer swap evidence: the same players, builds, or matchup with the initial
condition exchanged, so skill and matchup confounds cancel. Estimate a
compensation value (komi, bonus stock, or tempo credit) by measuring win rate
at two or more compensation levels and interpolating to the target:

```text
slope = (win_rate_at_c1 - win_rate_at_c0) / (c1 - c0)
compensation_estimate = c0 + (target_win_rate - win_rate_at_c0) / slope
```

Verify the estimate at the proposed value instead of trusting the
interpolation; win-rate response to compensation is often nonlinear or
stepped. For more than two conditions, compare every pair rather than only
each condition against the average.

### Check and output

- Require equivalent segments, versions, and exposure definitions with adequate
  sample sizes. Report per-condition counts and uncertainty; for swap or
  matched designs require complete pairs. Do not pool conditions with
  different matchup exposure.
- Do not compensate past the target: check that the disadvantaged condition
  does not become advantaged and that the compensation does not distort
  economy, tempo, or decision value elsewhere.
- When no observations exist, estimate with a simulator or a designed
  experiment and label the result as modeled rather than measured.
- Output condition pair, win rates, advantage, sample counts, compensation
  candidates with measured or modeled response, the selected value, and the
  target.

## Recipe: Rating prediction and calibration

### Inputs

Rating purpose, prior ratings, opponents, outcomes, uncertainty or update
factor, rating scale, match format, team aggregation, prediction window, and
held-out match results.

### Compute

For a two-player Elo-style baseline:

```text
expected_score_A = 1 / (1 + 10^((rating_B - rating_A)/scale))
new_rating_A = old_rating_A + K*(actual_score_A - expected_score_A)
calibration_error_bin = observed_score_rate_bin - mean_predicted_score_bin
Brier_score = mean((predicted_win_probability - binary_result)^2)
```

Use `actual_score` of 1 for a win, 0 for a loss, and only use 0.5 for a draw
when half a win matches the game. Use a multiclass calibration metric rather
than binary Brier score when draws or placements are separate outcomes.

### Check and output

- Confirm paired two-player expected scores sum to 1 and that rating updates
  conserve or intentionally create/remove rating according to policy. Require
  a positive rating scale and non-negative update factor.
- Evaluate out-of-sample calibration, predictive error, convergence speed,
  volatility, segment bias, and extreme mismatches against a simple baseline.
- Do not copy Elo, Glicko, TrueSkill, or team aggregation into a game whose
  luck, placements, teams, opponent selection, or uncertainty violate its
  assumptions. Output the exact variant and parameters used.

## Recipe: Descriptive statistics and uncertainty

### Inputs

Observed values, whether they are a full population or sample, observation
unit, pairing/repeated-player structure, missing values, segments, and the
minimum practically meaningful effect.

### Compute

```text
mean = sum(x_i) / n
population_variance = sum((x_i - mean)^2) / n
sample_variance = sum((x_i - mean)^2) / (n - 1)
standard_deviation = sqrt(selected_variance)
standard_error_of_mean = sample_standard_deviation / sqrt(n)
difference_in_means = proposed_mean - current_mean
difference_in_rates = proposed_rate - current_rate
Pearson_r = sum((x_i - mean_x)*(y_i - mean_y))
            / sqrt(sum((x_i - mean_x)^2)*sum((y_i - mean_y)^2))
```

Use population variance only for the complete population being described;
use sample variance for a sample used to infer beyond itself. Report median and
decision-relevant quantiles even though they do not need a closed formula.

### Check and output

- Require `n > 0`, `n > 1` for sample variance, and non-zero variance in both
  variables for correlation.
- Do not interpret a p-value as the probability that a hypothesis is true.
  Choose confidence intervals and statistical tests only after the guardrails
  in `evidence-and-validation.md`; account for pairing, repeated players,
  multiple comparisons, peeking, and non-normal data.
- Output counts, missingness, mean, median, standard deviation, quantiles,
  practical effect, uncertainty, segments, raw-data visualization, and limits.

## Recipe: Before/after telemetry comparison

### Inputs

Decision, current/proposed version, numerator and denominator, population,
segments, observation window, exclusions, and target effect.

### Compute

```text
rate = numerator / denominator
absolute_change = proposed_rate - current_rate
relative_change = absolute_change / current_rate
selection_rate = option_selections / eligible_selection_opportunities
win_rate = wins / eligible_matches
retention_rate = returning_cohort_members / eligible_cohort_members
churn_rate = 1 - retention_rate
conversion_rate = paying_users / eligible_users
ARPU = revenue / all_eligible_users
ARPPU = revenue / paying_users
```

When the current rate is zero, omit relative change and report the absolute
change with counts. Calculate only metrics relevant to the design decision;
monetization metrics do not substitute for player welfare or balance outcomes.
Use the descriptive-statistics recipe above and choose any inferential method
only through `evidence-and-validation.md`.

### Check and output

- Compare equivalent segments and exposure.
- Require positive denominators and define eligibility, cohort date, exposure,
  and repeat observations before calculating rates. Omit `ARPPU` when there
  are no paying users.
- Separate practical effect size from statistical significance.
- Output current, proposed, absolute and relative change, target, sample count,
  segment, and evidence limitation.
