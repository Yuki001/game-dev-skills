# PvP and Metagame Playbook

Read this reference for competitive options, characters, factions, sides,
matchups, snowballing, comeback systems, match length, ratings, rankings, and
metagame changes. Pair it with one task playbook and the relevant
[calculation recipes](calculation-recipes.md).

## Required inputs

- win condition, match format, player count, sides, roles, and turn/order rules;
- option or strategy definitions and legal combinations;
- payoff, matchup, selection, ban, and win data with sample counts when
  available;
- skill/rating bands, maps, sides, modes, party composition, and patch version;
- economy, territory, information, and power state over match time;
- target for fairness, diversity, prediction, match length, or spectator value.

## Persistent simulation tools

For repeated competitive tuning, create and retain a matchup analyzer that
accepts option, side, map, skill, and version segments and produces both
payoff/win matrices and sample/assumption matrices. When game rules are
available, add a seeded match or encounter simulator for candidate changes;
when only telemetry is available, keep modeled and observed results separate.
Use and delete a temporary script for a one-off matrix or patch judgment.

For snowball and comeback questions, create a trajectory simulator or analyzer
that records power, economy, territory, information, win likelihood, recovery
paths, and meaningful decisions over match time. Support parameter sweeps for
cost, power, timing, comeback strength, and matchup modifiers.

The tool must flag sparse cells, dominated options, segment reversals,
pre-match-determined outcomes, and guardrail failures rather than hiding them
inside an overall average.

## Procedure

1. Define the competitive target. Do not substitute equal overall win rate for
   balanced matchups, meaningful roles, or equal opportunity under similar
   skill.
2. Build a matchup matrix using one consistent outcome and include sample count
   or confidence limitation for each cell, following the
   [PvP matchup-matrix recipe](calculation-recipes.md#recipe-pvp-matchup-matrix).
3. Segment by skill, map, side, build, and version until known asymmetries are
   visible. Compare both weighted population results and within-segment results.
4. Remove strictly dominated choices from the assumed strategic set only after
   real cost, availability, execution, and situational value are included using
   the
   [option-comparison recipe](calculation-recipes.md#recipe-compare-options-and-situational-value).
5. Plot or tabulate lead state over time: power, income, territory, information,
   recovery probability, and meaningful decisions remaining for the trailing
   side.
6. Check turtling, stalling, sandbagging, leader targeting, kingmaking,
   elimination downtime, counter-picking, and pre-match outcome determination.
7. Distinguish an underlying rule/object problem from a metagame response. Do
   not add a narrow counter to conceal an unacceptable base relationship.
8. Propose exact power, cost, availability, matchup, comeback, or timing changes
   and use the tool to sweep and recalculate the affected matrix or lead
   trajectory.
9. For a deployed patch, compare equivalent versions, segments, and exposure
   using the
   [before/after telemetry recipe](calculation-recipes.md#recipe-beforeafter-telemetry-comparison).

## Working tables

### Matchup matrix

| Option | Opponent A | Opponent B | Opponent C | Overall | Sample/assumption |
| --- | --- | --- | --- | --- | --- |

### Match trajectory

| Time/phase | Leader advantage | Recovery chance/path | Trailing decisions | End-state risk |
| --- | --- | --- | --- | --- |

## Rating and ranking tasks

When the task concerns ratings, define whether the value is for prediction,
matchmaking, visible progression, or rewards. Evaluate out-of-sample outcome
prediction and calibration. Do not prescribe Elo, Glicko, or a matrix solution
without verifying that team, placement, asymmetry, opponent selection, and
uncertainty assumptions fit the game.

## Acceptance checks

- Important matchup cells and skill bands are acceptable even when the overall
  average looks healthy.
- The leading side benefits from success without ending meaningful opposition
  too early.
- Comeback rules do not make avoiding the lead optimal.
- Counters remain usable often enough to justify their cost and slot.
- Match duration includes cleanup time after the strategic result is clear.
- A proposed patch does not merely rotate one dominant strategy into another.
- Any retained analyzer preserves segment/sample context and the simulator's
  candidate values pass matchup, lead, and match-length guardrails; temporary
  checks are deleted after judgment.
