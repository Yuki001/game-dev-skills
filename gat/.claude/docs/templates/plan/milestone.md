# Milestone Plan

> **Status**: Draft | In Review | Approved
> **Last Updated**: [Date]
> **Path**: gat/milestone/milestone.md

> **Status lifecycle** (per milestone): `planned -> designing -> designed -> building -> built`.
> The planner sets `planned` and advances to `designing`/`designed` from observed
> design documents. `building` and `built` are advanced by the user (GAT cannot
> observe engineering progress). Each milestone's detailed status and progress
> tracker live in its `m{N}-brief.md`.

## Project Summary

- Game:
- Planning basis:
- Total milestones:
- Current planning assumption:

## Milestone Order

| Milestone ID | Name | Handoff Goal | Player / Validation Outcome | Systems | Status |
|--------------|------|--------------|-----------------------------|---------|--------|
| M01 | Example | Establish playable core loop | Player can complete one satisfying loop | movement, combat, hud | planned |

## Milestone Details

### M01 - Example

- Handoff goal:
- Why this milestone exists:
- Player-visible or validation outcome:
- Systems in scope:
- Systems intentionally out of scope:
- Overview docs to read: gat/overview/game.md, gat/overview/systems-index.md, gat/overview/art-direction.md
- Milestone brief: gat/milestone/m1-<name>/m1-brief.md
- Per-system design docs: gat/milestone/m1-<name>/<system>/<system>-{gdd,data,art}-m1.md
- Narrative docs to read (scoped range): [relevant gat/narrative/*.md and the sections/quests/beats this milestone covers]
- Content data needed:
- Dependencies from earlier milestones:
- Handoff to next milestone:
- Acceptance boundary for downstream workflow:
- Decisions downstream workflow may make:
- Decisions that must come back to design:
- Risks and unknowns:
- Notes:

### M02 - [Milestone Name]

- Handoff goal:
- Why this milestone exists:
- Player-visible or validation outcome:
- Systems in scope:
- Systems intentionally out of scope:
- Overview docs to read: gat/overview/game.md, gat/overview/systems-index.md, gat/overview/art-direction.md
- Milestone brief: gat/milestone/m2-<name>/m2-brief.md
- Per-system design docs: gat/milestone/m2-<name>/<system>/<system>-{gdd,data,art}-m2.md
- Narrative docs to read (scoped range): [relevant gat/narrative/*.md and the sections/quests/beats this milestone covers]
- Content data needed:
- Dependencies from earlier milestones:
- Handoff to next milestone:
- Acceptance boundary for downstream workflow:
- Decisions downstream workflow may make:
- Decisions that must come back to design:
- Risks and unknowns:
- Notes:

## Sequencing Notes

- Why this order:
- Cross-milestone dependencies:
- First validation milestone:
- Recommended first downstream engineering handoff:

## Milestone Risk Register

| Milestone | Main Risk | Impact | Mitigation |
|-----------|-----------|--------|------------|
| M01 | [Risk] | | |

## Downstream Engineering Handoff

- Preferred handoff unit: one milestone at a time
- Technical design owner: downstream engineering workflow
- Task breakdown owner: downstream engineering workflow
- Implementation owner: downstream engineering workflow
- Verification owner: downstream engineering workflow

## Working Rules

- `gat/milestone/milestone.md` is the global milestone roadmap; each `m{N}-brief.md` is the expanded, self-contained handoff packet for one milestone.
- Planning runs BEFORE per-system design; do not require system GDDs to exist.
- Create a directory `gat/milestone/m{N}-<name>/` and an `m{N}-brief.md` skeleton for each planned milestone.
- Do not include technical architecture, file plans, implementation tasks, or test plans here.
- Each milestone should name the systems and docs it draws from.
- Global design lives in `gat/overview/` and `gat/narrative/`; implementation planning happens downstream.
- A later milestone may redefine a system differently from an earlier one — note such reuse, do not treat it as a conflict.
