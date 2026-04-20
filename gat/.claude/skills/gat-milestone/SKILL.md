---
name: gat-milestone
description: "Break the project into milestones and create production/milestone.md plus milestone directories."
argument-hint: "[optional planning focus]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion
---

# Milestone

This skill writes:

- `production/milestone.md`
- `production/milestone-xx-name/`

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
- `design/art/art-direction.md`
- all existing `design/art/*-art.md`
- `.claude/docs/templates/plan/milestone.md`
- `production/milestone.md` if exists

## Phase 2: Hand Off To The Planner

Spawn `gat-planner` agent with all read content plus:

- instruction to write or update `production/milestone.md`
- instruction to define milestone directories using pattern `production/milestone-01-name/`
- planning focus from argument if provided

The planner should:

- choose a small set of meaningful milestones
- give each a clear goal and named system set
- define code focus and art focus per milestone
- include sequencing notes and milestone-level risks
- keep milestone names short and path-safe

## Phase 3: Review

Summarize how many milestones were planned and which comes first.

Use `AskUserQuestion`:

- `Plan first milestone (Recommended)` → Run `/gat-plan`
- `Stop here`
