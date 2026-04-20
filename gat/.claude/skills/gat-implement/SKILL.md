---
name: gat-implement
description: "Implement one ready task from a milestone tasks.md."
argument-hint: "[milestone-id | milestone-directory | TASK-xxx]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent, AskUserQuestion
---

# Implement

This skill implements one task at a time from `tasks.md`.

## Phase 1: Find The Task

If argument is a milestone directory or id:
- read that milestone's `tasks.md`
- choose first task with `Status: Ready`

If argument is a task id like `TASK-001`:
- search `production/milestone-*/tasks.md`
- locate the matching task

If no argument:
- glob `production/milestone-*/tasks.md`
- choose first task with `Status: Ready`
- if none exist, stop and say there is no ready task

## Phase 2: Load Context

Read:

- the milestone `tasks.md`
- `design/gdd/game.md`
- `design/gdd/systems-index.md` if exists
- system GDDs listed in the selected task
- the matching milestone `tech.md`

If task is missing acceptance criteria or files to touch, stop and say to refine with `/gat-plan`.
If milestone is missing `tech.md`, stop and say to run `/gat-plan` first.

## Phase 3: Hand Off To The Programmer

Spawn `gat-programmer` agent with:

- the selected task section
- the full milestone `tasks.md`
- game overview, systems index, relevant system GDDs
- the milestone `tech.md`
- instruction to implement only this task
- instruction to update task status when finished or blocked

The programmer should edit the smallest useful set of files in `src/` and `tests/`.

## Phase 4: Report

Summarize files changed, tests added, final task status.

Use `AskUserQuestion`:

- `Implement next ready task (Recommended)` → Run `/gat-implement`
- `Stop here`
