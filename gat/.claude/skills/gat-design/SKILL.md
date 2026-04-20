---
name: gat-design
description: "Run the full design pipeline with brainstorm wizard, or add one missing system."
argument-hint: "[<hint> | <system-name>]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion
---

# Design

This skill writes all design and art documents.

## Phase 1: Resolve Mode

Check existing files:

- If `design/gdd/game.md` missing → Mode: `wizard`
- If argument matches a system name in `systems-index.md` → Mode: `system`
- If `game.md` exists and at least one system in `systems-index.md` lacks a GDD → Mode: `continue`
- If `game.md` exists and all systems have GDDs → report design is complete, stop

Treat any non-system-name argument as a concept hint passed into the wizard.

## Phase 2: Wizard

Skip this phase if Mode is `continue` or `system`.

### Step 1 — Core Concept

If a concept hint was provided, first spawn `gat-designer` to extract what is already answered from the hint:

- genre / style
- core player verb
- target feeling
- rough scope

Then use `AskUserQuestion` to ask only the questions the hint did not answer. If the hint answered all four, skip Step 1 entirely and proceed to Step 2.

### Step 2 — Concept Direction

Spawn `gat-designer` to generate 2-3 short concept directions (3-5 sentences each) based on Step 1 answers.

Use `AskUserQuestion`:

- "Which direction resonates most, or describe your own?"
- Options: present the 2-3 directions as options plus "Describe my own"

### Step 3 — System Scope

Spawn `gat-designer` to propose a system list with brief rationale for each, based on the chosen direction.

Use `AskUserQuestion` (multiSelect):

- "Which systems should be in scope?"
- List the proposed systems as options

Then use a second `AskUserQuestion`:

- "Any systems to add that are missing? (leave blank to continue)"

### Step 4 — Confirm Before Writing

Show a one-paragraph summary: chosen direction + confirmed system list.

Use `AskUserQuestion`:

- "Ready to write the design docs?" 
- Options: `Yes, write them (Recommended)` / `Let me adjust something`

If user wants to adjust, loop back to the relevant step.

## Phase 3: Execute

Read templates:

- `.claude/docs/templates/design/game-overview.md`
- `.claude/docs/templates/design/systems-index.md`
- `.claude/docs/templates/design/system-gdd.md`
- `.claude/docs/templates/design/global-art.md`
- `.claude/docs/templates/design/system-art.md`

### Wizard or Continue mode

**If Mode is `wizard`:** execute Steps 1-3 below in order.
**If Mode is `continue`:** skip Steps 1-2, go directly to Step 3.

**Step 1** — Spawn `gat-designer` to write `design/gdd/game.md` and `design/gdd/systems-index.md`:

- Pass wizard answers (direction, confirmed system list)
- Pass templates
- Instruction: write both files in one pass

**Step 2** — Spawn `gat-artist` to write `design/art/art-direction.md`:

- Pass `game.md`, global-art template
- Pass existing `art-direction.md` if present

**Step 3** — For each system in `systems-index.md` lacking a GDD, in order:

Spawn `gat-designer` → `design/gdd/<system>.md`:
- Pass `game.md`, `systems-index.md`, system-gdd template
- Pass existing system GDD if present

Then spawn `gat-artist` → `design/art/<system>-art.md`:
- Pass `game.md`, `art-direction.md`, the newly written system GDD, system-art template
- Pass existing system art doc if present

### System mode

Require `design/gdd/game.md` and `design/gdd/systems-index.md`.

Spawn `gat-designer` → `design/gdd/<system>.md`

Then spawn `gat-artist` → `design/art/<system>-art.md`

## Phase 4: Review

Summarize what was created or updated.

Use `AskUserQuestion`:

- `Plan milestones (Recommended)` → Run `/gat-milestone`
- `Add another system` → Run `/gat-design <name>`
- `Stop here`
