# Economy Playbook

Read this reference for currencies, inventory resources, production,
consumption, prices, trading, gifting, auctions, inflation, resets, and
long-lived progression economies. Pair it with one task playbook and the
relevant [calculation recipes](calculation-recipes.md).

## Required inputs

- every resource and its unit;
- sources, sinks, conversions, transfers, caps, decay, and resets;
- acquisition and spending rules with rates and prerequisites;
- starting stock and intended daily/session/season horizon;
- price table and goods or power purchased;
- ordinary, new, highly active, optimizing, and paying segments when relevant;
- trade, gifting, market, or multi-account rules.

## Persistent simulation tool

When the economy will receive continued content or tuning, create and retain an
economy simulator that advances the system by the meaningful time step: action,
match, session, day, or season. For a one-off rate, affordability, or proposal
check, use a temporary script instead. The
persistent simulator should:

- load sources, sinks, conversions, prices, caps, resets, and segment behavior
  from editable input data;
- simulate new, ordinary, highly active, optimizing, and paying paths when
  relevant;
- track stock, net flow, affordability, blocked actions, production capacity,
  and transfers at each step;
- detect negative stock, cap pressure, unreachable purchases, runaway
  compounding, circular conversions, and conservation violations;
- sweep rates, prices, caps, sink strength, and reset cadence;
- export time-series and per-segment target/guardrail results.

For open economies, represent external supply/demand or player transactions as
explicit policies or observed inputs rather than an unexplained adjustment.
Verify a short forecast by hand before running the full horizon.

## Procedure

1. Build a source/sink table and a stock forecast for each important segment
   using the
   [economy stock and affordability recipe](calculation-recipes.md#recipe-economy-stock-and-affordability).
   Use the same horizon for income and spending.
2. Calculate affordability in time, attempts, or opportunity cost, not only
   nominal currency price.
3. Mark every loop in which owning a resource or upgrade increases future
   income. Project compounding loops separately from flat flows.
4. Find the earliest surplus, poverty, cap, or progression gate. Trace whether
   it comes from a source, sink, price, content schedule, or cross-resource
   conversion.
5. For open economies, add transfers and market behavior. Test thin and liquid
   markets, rich-to-new-player transfers, speculation, collusion, duplication,
   and multi-account loops.
6. Compare fixes by changing the smallest responsible rate, price, cap, sink,
   supply, or reset rule. Sweep credible ranges and forecast each candidate
   across the full horizon.
7. Identify who gains and loses from the change; averages are insufficient when
   segments have materially different flows. For open or long-lived economies,
   track top-share and Gini concentration from the
   [economy stock and affordability recipe](calculation-recipes.md#recipe-economy-stock-and-affordability)
   next to the segment flows.
8. For a deployed change, compare equivalent versions, segments, and exposure
   using the
   [before/after telemetry recipe](calculation-recipes.md#recipe-beforeafter-telemetry-comparison).

## Working tables

### Flow table

| Resource | Source/rate | Sink/rate | Conversion/transfer | Cap/reset | Owner |
| --- | --- | --- | --- | --- | --- |

### Forecast

| Segment/time | Opening stock | Sources | Sinks | Transfers | Closing stock | Blocked purchase |
| --- | --- | --- | --- | --- | --- | --- |

### Tuning proposal

| Parameter | Current | Proposed | Stock/affordability effect | Affected segment | Risk |
| --- | --- | --- | --- | --- | --- |

## Acceptance checks

- Every permanent source has a relevant sink or intentional accumulation goal.
- Ordinary players can reach required purchases within the target cadence.
- Optimizing players cannot create an unintended self-sustaining surplus or
  conversion loop.
- New or unlucky players cannot enter an unrecoverable poverty state.
- Wealth concentration stays within intent across the horizon; rising top
  share or Gini alongside stagnant new-player stock is flagged even when
  segment averages pass.
- Prices remain meaningful relative to income, substitutes, slots, risk, and
  future value.
- Trading and gifting are modeled as transfers or new sources correctly.
- A reset clearly defines what is lost, retained, and accelerated afterward.
- Monetization-linked changes state their effects on time, skill, luck,
  competitive power, and player welfare; current legal questions are escalated.
- Any retained simulator passes invariants and target checks for every required
  segment and preserves the exact accepted parameter set.
