---
name: gat-plan
description: "Create tasks.md, tech.md, and art-prompts.md for one milestone."
argument-hint: "[milestone-id | milestone-directory]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion
---

# Plan

This skill writes for one milestone:

- `production/milestone-xx-name/tasks.md`
- `production/milestone-xx-name/tech.md`
- `production/milestone-xx-name/art-prompts.md`

## Phase 1: Validate Inputs

Fail if any of these are missing:

- `design/gdd/game.md`
- `design/gdd/systems-index.md`
- `production/milestone.md`

Read:

- `design/gdd/game.md`
- `design/gdd/systems-index.md`
- all existing `design/gdd/*.md` except `game.md` and `systems-index.md`
- `design/art/art-direction.md` if exists
- all existing `design/art/*-art.md`
- `production/milestone.md`
- `.claude/docs/templates/plan/tasks.md`
- `.claude/docs/templates/plan/tech.md`
- `.claude/docs/templates/plan/art-prompts.md`

Resolve the target milestone:

- If argument identifies a milestone, use it
- Otherwise choose the first milestone directory that lacks `tasks.md`
- If all have `tasks.md`, choose the first lacking `tech.md`

Stop if no milestone can be resolved.

Read existing milestone files if present:

- `production/milestone-xx-name/tasks.md`
- `production/milestone-xx-name/tech.md`
- `production/milestone-xx-name/art-prompts.md`

## Phase 2: Spawn Planner

Spawn `gat-planner` agent to write `tasks.md`:

- Pass game overview, systems index, system GDDs, milestone roadmap
- Pass selected milestone identity and directory
- Pass tasks template and existing tasks.md if any
- Instruction: define build order, create small programmer-owned tasks, make dependencies explicit, include verification notes per task

## Phase 3: Spawn Programmer and Artist in Parallel

After planner finishes, spawn both:

**`gat-programmer` agent** → write `tech.md`:
- Pass game overview, systems index, system GDDs, milestone roadmap
- Pass the newly written tasks.md
- Pass tech template and existing tech.md if any
- Instruction: describe milestone-level architecture, per-system technical breakdowns, testing focus, known limitations

**`gat-artist` agent** → write `art-prompts.md`:
- Pass game overview, systems index, system GDDs
- Pass art-direction.md and system art docs
- Pass milestone roadmap and selected milestone
- Pass art-prompts template and existing art-prompts.md if any
- Instruction: produce named prompt entries with style anchors, main prompt, negative prompt where useful

## Phase 4: Review

Summarize: milestone planned, task count, tech systems covered, prompt entries added.

Use `AskUserQuestion`:

- `Implement first task (Recommended)` → Run `/gat-implement`
- `Stop here`
