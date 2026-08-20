# Combat and Progression Playbook

Read this reference for attacks, abilities, enemies, encounters, character
power, XP, levels, rewards, difficulty, and PvE progression. Pair it with one
task playbook and the relevant calculation recipes.

## Required inputs

- actor health, mitigation, damage, timing, accuracy, resources, and recovery;
- ability cycle, cooldown, range, area, control, setup, and failure behavior;
- encounter composition, duration target, retry cost, and progression point;
- expected novice, ordinary, practiced, and optimized builds where relevant;
- XP/reward requirements, earning rates, content counts, and milestones.

Use ranges when timing or execution varies. Keep theoretical maximum separate
from practical expected performance.

## Persistent simulation tools

When combat or progression will be tuned repeatedly, create and retain one or
both tools. For a one-off formula or proposal check, use a temporary script
with the same model rules and delete it after preserving the evidence.

- **Combat simulator:** execute turns, ticks, or discrete events with the real
  update order, action policies/rotations, cooldowns, resources, mitigation,
  healing, control, phases, targeting, and random outcomes. Report burst,
  sustained output, actions/turns to defeat, TTK distribution, survival,
  resource use, idle time, and failed guardrails by scenario.
- **Growth simulator:** step through levels or milestones using XP/reward
  requirements, earning policies, player/challenge curves, unlocks, caps,
  catch-up, and resets. Report per-step and cumulative time, power ratio,
  affordability, and progression breakpoints for each player path.

Expose actor, ability, enemy, curve, and scenario parameters outside the source
code. Support ordinary, novice/underpowered, optimized, and boundary scenarios,
plus sweeps for the parameters being tuned. Verify at least one combat or
milestone result by hand before trusting the tool.

## Combat procedure

1. Build one row per actor, weapon, or ability with raw parameters and derived
   burst, sustained output, effective health, resource efficiency, and cycle
   time.
2. Calculate discrete hits/actions and time to defeat for representative
   targets. Include reload, cooldown, downtime, miss rate, mitigation, healing,
   control, and invulnerable windows that occur in the real encounter.
3. Run at least ordinary and optimized rotations. Add novice or failure cases
   when the audience or difficulty target depends on them.
4. Compare the number of meaningful decision cycles, allowed mistakes, danger
   windows, recovery opportunities, and time spent after the outcome is already
   decided.
5. Price non-damage value explicitly: mobility, range, control, information,
   safety, area coverage, reliability, and setup cost.
6. Propose exact values that move the calculated outcome into its target band.
   Use the simulator to sweep the tuning range and recalculate neighboring
   options and enemies affected by the change.

## Progression procedure

1. Select milestone rows from start through endgame rather than inspecting
   every level first.
2. Calculate player power, enemy/challenge power, XP or reward requirement,
   earning rate, time/attempts to milestone, and unlocked decisions at each row.
3. Compare per-step and cumulative values. Detect sudden changes caused by
   curve mismatch, reward gaps, enemy scaling, or a newly multiplicative stat.
4. Run ordinary, underpowered legitimate, and optimized paths.
5. Check whether numeric growth changes player capability or is cancelled by
   automatic scaling. Preserve meaningful new actions, mastery, or content
   access in the progression plan.
6. Set caps, catch-up, resets, or piecewise segments only where the main curve
   cannot serve a legitimate range. Rerun the full growth simulator after each
   structural curve change.

## Deliverable tables

### Combat

| Option/actor | Burst | Sustained output | Effective health | TTK | Resource cost | Strong/weak situation |
| --- | --- | --- | --- | --- | --- | --- |

### Progression

| Milestone | Player power | Challenge power | Ratio | Time/attempts | New decision | Status |
| --- | --- | --- | --- | --- | --- | --- |

For tuning work, add current, target, and proposed values to the relevant
table.

## Acceptance checks

- TTK and difficulty are evaluated as discrete gameplay outcomes, not only
  continuous DPS ratios.
- An HP increase does not merely lengthen a solved encounter.
- Different options produce different useful decisions rather than cosmetic
  numeric variation.
- Failure is attributable to visible, learnable, or preparable causes at the
  intended difficulty.
- Reward timing fits the intended session and content cadence.
- Progression does not require repeated content after its decisions and
  learning have been exhausted unless that repetition is intentional.
- Optimized growth does not make later content or earlier mechanics irrelevant
  without an explicit goal.
- Any retained combat/growth tool passes known cases, records seeds when
  random, and shows that proposed values meet targets across required
  scenarios; temporary checks are deleted after judgment.
