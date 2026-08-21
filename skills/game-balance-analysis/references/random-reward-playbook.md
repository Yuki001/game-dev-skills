# Random Reward Playbook

Read this reference for loot, card draws, dice, critical hits, procedural
outcomes, weighted tables, streaks, pity systems, duplicate protection, and
luck-versus-skill decisions. Pair it with one task playbook and the relevant
[calculation recipes](calculation-recipes.md).

## Required inputs

- all outcomes, weights/probabilities, quantities, and player value;
- roll frequency and relevant session or progression horizon;
- independent, without-replacement, conditional, or stateful selection rules;
- multi-stage tables, guarantees, pity, duplicate protection, and reset rules;
- player choices that change exposure, probability, or consequences;
- displayed odds and intended emotional result;
- economy or competitive systems receiving the rewards.

## Persistent simulation tool

For a random-reward system that will receive continued content or tuning,
create and retain an exact enumerator for tractable finite outcomes and a
seeded simulator for large, nested, repeated, or stateful systems. For a
one-off probability or proposal check, use a temporary script and delete it
after preserving the evidence. A retained tool should:

- load weights, reward values, pool state, pity, guarantees, duplicate
  protection, replacement, and horizon from editable parameters;
- reproduce the exact multi-stage selection order;
- report effective probabilities, EV, median/percentiles, time/attempts to
  success, drought/streak probabilities, high tail, and guarantee limits;
- preserve player state when utility changes through ownership, thresholds, or
  duplication;
- sweep weights, pity thresholds, guarantee timing, and protection rules;
- verify probability totals and compare one analytic case with simulation.

Use multiple recorded seeds or independent batches for simulation. Save the
accepted reward parameters and the distribution results used to justify them.

## Procedure

1. Reconstruct the exact selection algorithm. Expand nested rarity, item,
   quantity, replacement, and guarantee stages instead of analyzing only the
   top-level percentage.
2. Use the
   [weighted rewards and streaks recipe](calculation-recipes.md#recipe-weighted-rewards-and-streaks)
   to calculate expected value, variance or spread, important percentiles,
   probability of no success, attempts/time to first success, and relevant
   streak lengths.
3. Use combinatorics for manageable finite pools, state transitions for pity or
   repeated effects, and the
   [iterative or Monte Carlo simulation recipe](calculation-recipes.md#recipe-iterative-or-monte-carlo-simulation)
   when exact enumeration is impractical. Cross-check at least one analytic or
   hand-calculated case.
4. Convert reward outcomes into economy, combat, collection, or progression
   value. Equal rarity does not imply equal player value.
5. Evaluate ordinary-session outcomes rather than relying on the long-run
   average. Include low-tail and high-tail player experiences.
6. Check player agency: information, risk selection, mitigation, adaptation,
   recovery, and whether skill can affect consequences.
7. Propose exact weights, thresholds, guarantees, or protection rules and
   sweep credible ranges, then recalculate the full distribution and downstream
   resource flow for accepted candidates using the
   [economy stock and affordability recipe](calculation-recipes.md#recipe-economy-stock-and-affordability)
   when rewards enter an economy.
8. Verify that displayed odds describe the effective conditional event players
   believe they are choosing.

## Three-layer judgment

Evaluate every important random outcome at three levels:

| Layer | Required question | Typical evidence |
| --- | --- | --- |
| Mathematical probability | What is the actual distribution over the player's horizon? | Exact calculation, enumeration, or simulation |
| Player utility | What is each outcome worth in the player's current state? | Thresholds, duplication, loss, scarcity, and diminishing value |
| Perceived probability | What process and odds does the player believe they face? | Disclosure, feedback, sequence visibility, playtest explanation, and trust |

Do not infer acceptable utility from positive expected value. A duplicate,
missed threshold, irreversible loss, or long drought can carry more weight than
its nominal numeric value. Do not dismiss perceived unfairness when the game
hides conditional odds, multi-stage rolls, pity state, or the cause of a streak.

When perception differs from the implemented distribution, test changes to
disclosure, feedback, guarantees, risk choice, or agency as well as changing
the probabilities themselves.

## Working table

| Outcome/tier | Effective probability | Value | EV contribution | Time/attempts | Protection rule |
| --- | --- | --- | --- | --- | --- |

Also report:

| Measure | Current | Proposed | Target/intent |
| --- | --- | --- | --- |
| Expected value | | | |
| Median or typical outcome | | | |
| No-success probability at horizon | | | |
| High-tail outcome | | | |
| Guaranteed maximum attempts | | | |

Add player utility and perceived-probability findings for each material reward
or failure state.

## Acceptance checks

- Effective probabilities sum to 1 at every selection stage.
- Independent and dependent events are not mixed incorrectly.
- The expected value is supported by an acceptable outcome distribution.
- The worst legitimate streak fits the promised experience or is bounded.
- Pity and duplicate protection do not create an unintended optimal exploit or
  economy spike.
- Randomness creates adaptation, anticipation, or variety rather than deciding
  the outcome without useful response.
- Competitive or monetized randomness receives current engineering, security,
  disclosure, and legal review when required.
- Any retained enumerator/simulator passes analytic known cases, probability
  invariants, target distribution checks, and the complete stateful horizon;
  temporary checks are deleted after judgment.
