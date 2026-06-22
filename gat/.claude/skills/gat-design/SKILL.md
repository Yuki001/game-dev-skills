---
name: gat-design
description: "Continue the design pipeline after brainstorm, or add one missing system GDD with art."
argument-hint: "[<system-name>]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion
---

# Design

This skill writes all design and art documents. For the initial concept interview,
it delegates to `/gat-brainstorm`.

## Phase 1: Resolve Mode

Check existing files:

- If `design/gdd/game.md` missing → hand off: tell the user to run `/gat-brainstorm [hint]` first. Stop.
- If argument matches a system name in `systems-index.md` → Mode: `system`

With `game.md` present, assess completeness:

- `systems-index.md` missing → Mode: `continue`
- `design/art/art-direction.md` missing → Mode: `continue`
- Any system in `systems-index.md` lacks a GDD → Mode: `continue`
- Any system in `systems-index.md` lacks an art doc → Mode: `continue`
- All of the above are present → report design is complete, stop

## Phase 2: Execute

Read templates:

- `.claude/docs/templates/design/system-gdd.md`
- `.claude/docs/templates/design/global-art.md`
- `.claude/docs/templates/design/system-art.md`
- `.claude/docs/templates/design/content-data.md`

### Continue mode

**Step 1** — If `design/art/art-direction.md` is missing, spawn `gat-artist` to write it:

- Pass `game.md`, global-art template

Skip this step if `art-direction.md` already exists.

**Ask after Step 1 complete** — Let user confirm changes:

Use `AskUserQuestion`:

- "Do you want to change the design docs? Or continue to next step?"
- Options: `Yes, continue to next step` / `Let me adjust something`

**Step 2** — For each system in `systems-index.md` lacking a GDD, in order:

Spawn `gat-designer` → `design/gdd/<system>.md`:
- Pass `game.md`, `systems-index.md`, system-gdd template
- Pass existing system GDD if present

**Step 3 — Content Fill** (for systems with high content volume)

For each system whose system GDD is complete AND which requires substantial content data, spawn `gat-designer` to write `design/content/<system>-data.md`:

- Pass the system GDD, `game.md`, `systems-index.md`, content-data template
- Pass existing content doc if present
- The content doc fills specific instances, parameters, sequences, and groups — the **data** that instantiates the **rules** defined in the system GDD

A system needs a content-data doc when its GDD defines data structures that need many concrete instances (e.g. an `enemy` GDD defines enemy attributes → content doc fills 25+ specific enemies; a `stage` GDD defines wave scheduling → content doc fills wave-by-wave scripts for all 5 stages).

Systems that are purely mechanical (e.g. `input`, `tbs-scoring`) typically do NOT need content-data docs — their parameters fit within the GDD itself.

**Step 4** — For each system in `systems-index.md` lacking an art doc, in order:

Spawn `gat-artist` → `design/art/<system>-art.md`:
- Pass `game.md`, `art-direction.md`, the system GDD, the content-data doc (if it exists), system-art template
- Pass existing system art doc if present
- The artist now has both the GDD (rules/schema) and the content-data doc (specific instances) to design complete visuals

### System mode

Require `design/gdd/game.md` and `design/gdd/systems-index.md`.

**Step 1** — Spawn `gat-designer` → `design/gdd/<system>.md`

**Step 2** — If the system needs content data, spawn `gat-designer` → `design/content/<system>-data.md`

**Step 3** — Spawn `gat-artist` → `design/art/<system>-art.md`:
- Pass `game.md`, `art-direction.md`, the system GDD, the content-data doc (if it exists), system-art template
- Pass existing system art doc if present

## Phase 3: Review

Summarize what was created or updated.

Use `AskUserQuestion`:

- `Plan milestones (Recommended)` → Run `/gat-milestone`
- `Add another system` → Run `/gat-design <name>`
- `Stop here`
