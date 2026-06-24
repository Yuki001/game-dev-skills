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
- `design/narrative/*.md`
- `design/art/art-direction.md`
- `design/art/*-art.md`
- `production/milestone.md`

## Phase 2: Summarize State

Report a short factual summary:

- Game overview present or missing
- Systems index present or missing
- Number of system GDDs
- Number of narrative docs
- Art direction present or missing
- Number of system art docs
- Milestone handoff roadmap present or missing

## Phase 3: Route

Use this logic:

1. If `design/gdd/game.md`, `design/gdd/systems-index.md`, or `design/art/art-direction.md` is missing:
   recommend `/gat-brainstorm` (with optional hint)
2. If the game overview or user goal indicates story, plot, lore, worldbuilding, characters, quests, dialogue, or authored narrative content matters, and no `design/narrative/story.md` exists:
   recommend `/gat-story`
3. If any system in `systems-index.md` lacks a GDD or art doc:
   recommend `/gat-design` to continue the pipeline
4. If `production/milestone.md` is missing:
   recommend `/gat-milestone`
5. Otherwise:
   state that GAT pre-production is complete and tell the user to hand one milestone at a time to their downstream engineering workflow

## Phase 4: Hand Off

End with one short line telling the user which command to run next.
