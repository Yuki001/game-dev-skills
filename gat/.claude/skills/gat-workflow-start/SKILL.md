---
name: gat-workflow-start
description: "Inspect the repo state and recommend the next step in the simplified workflow."
argument-hint: "[no arguments]"
user-invocable: true
allowed-tools: Read, Glob, Grep, AskUserQuestion
---

# Workflow Start

This skill is the workflow router for the simplified project.

## Phase 1: Inspect State

Check for these files:

- `design/gdd/game.md`
- `design/gdd/systems-index.md`
- `design/gdd/*.md` except `game.md` and `systems-index.md`
- `design/art/art-direction.md`
- `design/art/*-art.md`
- `production/milestone.md`
- `production/milestone-*/tasks.md`
- `production/milestone-*/tech.md`
- `production/milestone-*/art-prompts.md`

Also inspect whether any milestone `tasks.md` contains `Status: Ready`.

## Phase 2: Summarize State

Report a short factual summary:

- Game overview present or missing
- Systems index present or missing
- Number of system GDDs
- Art direction present or missing
- Number of system art docs
- Milestone plan present or missing
- Number of milestone directories
- Whether a milestone `tasks.md` exists
- Whether a milestone `tech.md` exists
- Whether a ready task exists
- Whether any milestone art prompt pack exists

## Phase 3: Route

Use this logic:

1. If `design/gdd/game.md` is missing:
   recommend `/gat-design` (with optional hint)
2. If any system in `systems-index.md` lacks a GDD or art doc:
   recommend `/gat-design` to continue the pipeline
3. If `production/milestone.md` is missing:
   recommend `/gat-milestone`
4. If milestone directories exist but at least one lacks `tasks.md` or `tech.md`:
   recommend `/gat-plan`
5. If a ready task exists:
   recommend `/gat-implement`
6. Otherwise:
   state that the workflow is set up and point to the next milestone artifact that is still missing

## Phase 4: Hand Off

End with one short line telling the user which command to run next.
