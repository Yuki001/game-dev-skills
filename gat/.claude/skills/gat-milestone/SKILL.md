---
name: gat-milestone
description: "Plan milestone slices from overview + narrative alone (no system GDDs required), create per-milestone directory skeletons and briefs, and write gat/milestone/milestone.md. Runs before per-system design. Stops before technical design, task breakdown, or implementation."
argument-hint: "[optional planning focus]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion
---

# Milestone

This skill plans milestone slices BEFORE per-system design and creates:

- `gat/milestone/milestone.md` — the ordered milestone roadmap with status
- `gat/milestone/m{N}-<name>/` — per-milestone directory skeletons
- `gat/milestone/m{N}-<name>/m{N}-brief.md` — milestone brief skeletons (all systems Pending, status `planned`)

It does NOT require any system GDD to exist. It does not create task lists,
technical designs, prompt packs, or implementation files. Those belong to the
downstream engineering workflow.

## Phase 1: Validate Inputs

Fail if any of these are missing:

- `gat/overview/game.md`
- `gat/overview/systems-index.md`
- `gat/overview/art-direction.md`

Do NOT fail when no system GDDs exist. Planning runs before design; the systems
index's priorities and dependencies are sufficient input for slicing.

Read:

- `gat/overview/game.md`
- `gat/overview/systems-index.md`
- `gat/overview/art-direction.md`
- all existing `gat/narrative/*.md` (used to inform milestone boundaries)
- `.claude/docs/templates/plan/milestone.md`
- `.claude/docs/templates/plan/m-brief.md`
- `gat/milestone/milestone.md` if it already exists
- existing `gat/milestone/m{N}-<name>/m{N}-brief.md` files if any milestones are already planned

## Phase 2: Hand Off To The Planner

Spawn `gat-planner` agent with all read content plus:

- instruction to write or update `gat/milestone/milestone.md` as an ordered set of milestone slices (`M01`, `M02`, ...) with a status column (`planned -> designing -> designed -> building -> built`)
- instruction to create a directory `gat/milestone/m{N}-<name>/` for each planned milestone
- instruction to author an `m{N}-brief.md` skeleton (template: `.claude/docs/templates/plan/m-brief.md`) for each milestone, listing every in-scope system with status Pending and the milestone status `planned`
- instruction NOT to write system GDDs, content-data docs, art docs, task lists, technical designs, prompt packs, or code
- planning focus from argument if provided

The planner should:

- choose a small set of meaningful milestones that can be handed off one stage at a time
- give each milestone a clear goal, player-facing outcome, and named system set
- define what is in scope and explicitly out of scope for each milestone
- use the systems index priorities + dependencies + narrative structure to slice; it does not need per-system rule detail
- include overview, narrative (scoped range), and content context needed by a downstream engineering workflow
- avoid technical architecture, file plans, coding tasks, and implementation sequencing
- set each new milestone's status to `planned`

## Phase 3: Review

Summarize how many milestones were planned, which comes first, and which directories/briefs were created.

Use `AskUserQuestion`:

- `Start designing the first milestone (Recommended)` → Tell the user to run `/gat-design <first-milestone> <system>` or `/gat-design <first-milestone>` (continue)
- `Stop here`
