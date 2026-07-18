# Milestone Brief: M{N} - [Milestone Name]

> **Status**: Planned | Designing | Designed
> **Last Updated**: [Date]
> **Owner**: planner (scope + iteration plan), designer (per-system progress rows)
> **Source Roadmap**: gat/milestone/milestone.md
> **Source Overview**: gat/overview/game.md, gat/overview/systems-index.md, gat/overview/art-direction.md

> **Status lifecycle**: `planned -> designing -> designed`.
> The planner sets `planned` and advances to `designing`/`designed` from observed
> design documents. Engineering execution is handled downstream; GAT does not
> track engineering or internal iteration execution status.

## 1. Milestone Overview

- Handoff goal:
- Why this milestone exists:
- Player-visible or validation outcome:
- Systems in scope:
- Systems intentionally out of scope:

## 2. Progress Tracker

> One row per system in this milestone. The designer updates a row after writing
> that system's docs. `Design Status` values: Pending | Designing | Designed.
> A system may be introduced across more than one iteration.

| System | Iteration(s) | GDD | Art | Data | Design Status |
|--------|--------------|-----|-----|------|---------------|
| [system] | I1 | [path or —] | [path or —] | [path or —] | Pending |

## 3. Iteration Plan

> An iteration is the smallest coherent vertical slice of this milestone that can
> be started through the project's real runtime entry, exercised end to end, and
> left in a runnable state. Every iteration must preserve the launch path and
> produce a new observable result, even when the feature is incomplete or uses
> placeholder art.
>
> Do not split by a fixed number of systems: split by player flow, integration risk,
> or feedback value. As a sizing heuristic, ordinary milestones should usually have
> 3-6 iterations; a very small milestone may have 1-2, while a plan needing more than
> 6 should be reconsidered as multiple milestones. Never add empty iterations just to
> meet a number.
>
> Repeat the following subsection for every iteration. Keep the description long
> enough for an engineer to understand what must be runnable and what feedback the
> iteration is meant to produce.

> For the first milestone only, name I1 `Bootstrap Runtime Shell` and use it to
> establish the project's global startup and runtime shell. For later milestones,
> do not rebuild the bootstrap shell: name I1 after the first new vertical slice
> and reuse the established startup path. Only change the shared shell when that
> change is an explicit part of the milestone scope.

### Iteration I1 — [First Vertical Slice Name]

- **Goal**: [For the first milestone: establish the global skeleton and prove the first playable or visual flow. For later milestones: deliver the first new vertical slice while reusing the established runtime shell.]
- **Why this is first**: [dependency, integration risk, or feedback reason]
- **Systems introduced or changed**: [systems]
- **Minimum runtime slice**: [the established runtime shell plus this iteration's player-facing or validation-facing flow]
- **Shortest player/test flow**: [steps from starting the project to the first result]
- **Observable result**: [what a player or tester can see or otherwise verify]
- **Integration verification**: [real runtime check and expected result]
- **Completion evidence**: [screenshot, recording, runtime observation, or other evidence]

### Iteration I2 — [Vertical Slice Name]

- **Goal**: [one coherent player-facing or validation-facing increment]
- **Why this slice belongs here**: [dependency, risk, or feedback reason]
- **Systems introduced or changed**: [systems]
- **Minimum runtime slice**: [what remains runnable from the established start flow]
- **Shortest player/test flow**: [steps]
- **Observable result**: [what must be visible or otherwise verifiable]
- **Integration verification**: [real runtime check and expected result]
- **Completion evidence**: [evidence]

> Add or remove iteration subsections according to scope. The planner should
> normally produce 3-6 meaningful iterations for an ordinary milestone, but may
> choose fewer for a small milestone. If more than 6 are needed, reconsider the
> milestone boundary instead of making each iteration too small to validate.

## 4. File Reference

> Relative paths from this milestone directory. Use this as the index for the
> downstream engineering workflow.

| File | Path |
|------|------|
| [system] GDD | [system]/[system]-gdd-m{N}.md |
| [system] data | [system]/[system]-data-m{N}.md |
| [system] art | [system]/[system]-art-m{N}.md |

## 5. Context To Read

- Overview docs: gat/overview/game.md, gat/overview/systems-index.md, gat/overview/art-direction.md
- Narrative docs (scoped range for this milestone): [list relevant gat/narrative/*.md and the sections/quests/beats this milestone covers]
- Content data needed:

## 6. Dependencies From Earlier Milestones

| Earlier Milestone | System | What Is Reused | Notes |
|-------------------|--------|----------------|-------|
| [M{K}] | [system] | | |

## 7. Handoff And Feedback

- Acceptance boundary for the whole milestone:
- Handoff boundary for each iteration:
- Decisions the downstream workflow may make:
- Decisions that must come back to design:
- Handoff to next milestone:
- Feedback destination when runtime or integration checks fail:

## 8. Risks And Unknowns

| Risk / Unknown | Impact | Mitigation |
|----------------|--------|------------|
| | | |

## 9. Notes

- [Additional context, including whether earlier-milestone docs for a reused system have been superseded by this milestone's redefinition]
