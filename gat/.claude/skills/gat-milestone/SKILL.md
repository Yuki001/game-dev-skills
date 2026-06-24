---
name: gat-milestone
description: "Break the design into milestone handoff slices and create production/milestone.md. Stops before technical design, task breakdown, or implementation."
argument-hint: "[optional planning focus]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion
---

# Milestone

This skill writes:

- `production/milestone.md`

It does not create milestone directories, task lists, technical designs, prompt
packs, or implementation files. Those belong to the downstream engineering
workflow.

## Phase 1: Validate Inputs

Fail if any of these are missing:

- `design/gdd/game.md`
- `design/gdd/systems-index.md`
- `design/art/art-direction.md`

Also stop if no system GDDs exist in `design/gdd/` besides `game.md` and `systems-index.md`.

Read:

- `design/gdd/game.md`
- `design/gdd/systems-index.md`
- all existing `design/gdd/*.md` except `game.md` and `systems-index.md`
- all existing `design/content/*-data.md`
- all existing `design/narrative/*.md`
- `design/art/art-direction.md`
- all existing `design/art/*-art.md`
- `.claude/docs/templates/plan/milestone.md`
- `production/milestone.md` if exists

## Phase 2: Hand Off To The Planner

Spawn `gat-planner` agent with all read content plus:

- instruction to write or update `production/milestone.md`
- instruction to split the project into ordered milestone handoff slices (`M01`, `M02`, ...)
- instruction not to create milestone directories, task lists, technical designs, prompt packs, or code
- planning focus from argument if provided

The planner should:

- choose a small set of meaningful milestones that can be handed off one stage at a time
- give each milestone a clear goal, player-facing outcome, and named system set
- define what is in scope and explicitly out of scope for each milestone
- include design, art, narrative, content, and risk context needed by a downstream engineering workflow
- avoid technical architecture, file plans, coding tasks, and implementation sequencing

## Phase 3: Review

Summarize how many milestones were planned and which comes first.

Use `AskUserQuestion`:

- `Start downstream engineering flow` → Tell the user to hand the chosen milestone to their preferred engineering workflow
- `Stop here`
