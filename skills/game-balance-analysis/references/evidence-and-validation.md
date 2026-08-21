# Evidence and Validation

Read this reference when a balance decision uses playtests, telemetry,
match/economy logs, surveys, experiments, or other observed player data. It
turns a model prediction into an evidence-backed decision.

## Required inputs

- decision and predicted effect;
- metric definitions with numerator, denominator, unit, and event trigger;
- player, session, match, content, and version identifiers;
- population, segments, time range, and exposure rules;
- missing, duplicate, retry, disconnect, bot, and exclusion handling;
- target band, minimum meaningful change, and action for each result.

## Required analysis tool

Create a reproducible analysis script when raw or tabular evidence is supplied.
Use a temporary script for a one-off judgment and delete it after preserving
the metric tables, conclusion, and cleanup status. Retain it as a persistent
analysis tool only for recurring reports or repeated balance decisions. It
should load the original data without modifying it, apply versioned filters and
segment definitions, validate counts and missing values, and export the metric
tables and charts used by the conclusion. Parameterize time range, version,
population, segment, exclusions, and target thresholds instead of hardcoding
one query.

When comparing a model with observed play, have the analysis tool join or align
the same scenarios and metrics so model-runtime gaps are explicit. Save both
the machine-readable result and the command/config that produced it.

When comparing versions, cohorts, or experiment arms, build equivalent
rate-and-delta tables through the
[before/after telemetry recipe](calculation-recipes.md#recipe-beforeafter-telemetry-comparison)
before applying inferential methods.

## Validate the evidence first

1. Reproduce a small number of known sessions from raw events or direct
   observation.
2. Confirm rules/config and telemetry come from the same version.
3. Reconcile totals and missing values before calculating rates.
4. Verify that each observation belongs to the intended population and has a
   valid opportunity to produce the outcome.
5. Record exclusions and show whether they can change the conclusion.

Do not tune from an unverified dashboard total.

## Segment and summarize

Segment only where the design predicts a meaningful difference, commonly by
skill/rating, progression, build, role, map, side, mode, party, platform,
version, or activity level.

For every reported result include:

- observation count and missing count;
- numerator and denominator for rates;
- mean, median, spread, and uncertainty through the
  [descriptive-statistics recipe](calculation-recipes.md#recipe-descriptive-statistics-and-uncertainty)
  when the distribution can be skewed;
- relevant percentiles or tails;
- time range, version, filters, and segment;
- practical effect size and uncertainty.

Show both weighted population results and important within-segment results. Do
not remove outliers until they are classified as error, exploit, rare valid
behavior, or a relevant extreme.

## Match evidence to the claim

Use precise language:

- `descriptive`: the observed data show a pattern;
- `associational`: two variables move together after stated segmentation;
- `predictive`: a model forecasts held-out outcomes with measured accuracy;
- `causal`: a controlled intervention supports that the change produced the
  effect under the experiment's assumptions.

For observational data, consider reverse direction, confounding, selection,
survivorship, matchmaking/exposure, and instrumentation error. Do not write a
causal conclusion from correlation alone.

## Use playtests to explain mechanisms

Use observed playtests when the question is why players choose, fail,
misunderstand, or exploit:

1. give testers the intended build, content, or starting state;
2. observe decisions and information without teaching the desired solution;
3. record failure point, recovery, time, and explanation from the player;
4. include an optimizing or adversarial pass;
5. compare the behavior with the model prediction;
6. change one responsible factor and rerun the decisive case.

Early prototypes need direct observation more than large samples. Later beta
or post-launch decisions can use telemetry to locate population patterns, then
targeted playtests to determine their mechanism.

## Statistical guardrails

Before inference, check independence, repeated players/teams, sample and
expected counts, distribution/variance assumptions, multiple comparisons,
repeated peeking, attrition, and exposure bias. Report practical effect size,
not only a p-value.

If assumptions fail, use an appropriate resampling, hierarchical, paired, or
other specialist method, or remain descriptive. High-impact experiments,
rating inference, monetization, privacy, and complex causal questions require
current specialist sources.

## Decision and rollout

Define before validation:

| Result | Decision |
| --- | --- |
| Target met and guardrails healthy | Accept or continue rollout |
| Target met but one guardrail fails | Revise or limit rollout |
| Change smaller than meaningful threshold | Do not claim improvement |
| Target moves in the wrong direction | Reject or roll back |
| Sample/data quality insufficient | Continue measurement without verdict |

State monitoring duration, stop threshold, rollback value, and affected
segments. Preserve the previous version and baseline calculation.

## Deliverable

Return:

1. evidence scope and quality checks;
2. metrics and segment table;
3. model prediction versus observed result;
4. descriptive, associational, predictive, or causal claim level;
5. effect size, uncertainty, and alternative explanations;
6. accept, revise, reject, roll back, or continue-measuring decision;
7. next targeted playtest or measurement.
