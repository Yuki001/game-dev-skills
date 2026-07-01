---
name: gat-design
description: "Design one system within a specific milestone's scope: write the milestone-scoped system GDD, content data, and system art doc, and update the milestone brief's progress. Requires a mandatory milestone argument."
argument-hint: "{milestone} {system | hint}"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion
---

# Design

This skill designs a single system within a specific milestone, after
`/gat-brainstorm` (overview) and `/gat-milestone` (milestone plan) are done.
For story, worldbuilding, characters, quests, dialogue, or authored narrative
content, delegate to `/gat-story`. For the initial concept interview, delegate
to `/gat-brainstorm`.

The `milestone` argument is **mandatory**. If it is omitted, the skill stops and
asks the user to specify a milestone — no inference, default, or fallback.

## Phase 1: Resolve Mode

Check existing files:

- If `gat/overview/game.md` or `gat/overview/systems-index.md` missing → hand off: tell the user to run `/gat-brainstorm [hint]` first. Stop.
- If `gat/overview/art-direction.md` missing → hand off: tell the user to run `/gat-brainstorm [hint]` to establish global art direction. Stop.
- If `gat/milestone/milestone.md` missing → hand off: tell the user to run `/gat-milestone` first. Stop.
- If no `milestone` argument provided → STOP. Tell the user a milestone is required and show the milestones listed in `gat/milestone/milestone.md`. Do NOT infer or default one. Do NOT write any files.
- If the `milestone` argument does not match any milestone directory under `gat/milestone/` (i.e., no `m{N}-<name>/m{N}-brief.md` exists) → STOP. Tell the user the milestone was not found and list the valid milestones.

Then resolve sub-mode:

- If a `system` (or hint) argument is also provided → Mode: `system` (design that one system in the milestone)
- If only a `milestone` argument is provided → Mode: `continue` (auto-fill all systems in that milestone's brief that are not yet designed). Continue is scoped to that milestone only — it does NOT cross into other milestones.

## Phase 2: Execute

Read templates:

- `.claude/docs/templates/design/system-gdd.md`
- `.claude/docs/templates/design/system-art.md`
- `.claude/docs/templates/design/content-data.md`

Read context:

- `gat/overview/game.md`, `gat/overview/systems-index.md`, `gat/overview/art-direction.md`
- the target milestone's `m{N}-brief.md` (for scope, in-scope systems, and the progress tracker)
- relevant `gat/narrative/*.md` when narrative context affects the system
- existing system docs under `gat/milestone/m{N}-<name>/<system>/` if present

Also read existing `gat/narrative/*.md` when present and pass relevant narrative
context to spawned agents. Do not create or rewrite narrative docs here; use
`/gat-story` for that.

### Continue mode (`/gat-design {milestone}`)

For each system listed in the milestone's `m{N}-brief.md` that is not yet
designed (progress row Pending), in the brief's order:

1. Spawn `gat-designer` → `gat/milestone/m{N}-<name>/<system>/<system>-gdd-m{N}.md`
2. If the system needs content data, spawn `gat-designer` → `gat/milestone/m{N}-<name>/<system>/<system>-data-m{N}.md`
3. Spawn `gat-artist` → `gat/milestone/m{N}-<name>/<system>/<system>-art-m{N}.md`
4. Update that system's progress row in `m{N}-brief.md` to Designed.

Do NOT design systems belonging to other milestones.

### System mode (`/gat-design {milestone} {system | hint}`)

**Step 1** — Spawn `gat-designer` → `gat/milestone/m{N}-<name>/<system>/<system>-gdd-m{N}.md`
- Pass `gat/overview/game.md`, `gat/overview/systems-index.md`, the milestone's `m{N}-brief.md`, system-gdd template
- Pass existing system GDD if present (e.g., an earlier milestone's version of the same system, for reference — a later milestone may redefine it differently)

**Step 2 — Content Fill** (for systems with high content volume, within this milestone's scope)

If the system requires substantial content data, spawn `gat-designer` to write
`gat/milestone/m{N}-<name>/<system>/<system>-data-m{N}.md`:

- Pass the system GDD, `gat/overview/game.md`, `gat/overview/systems-index.md`, the milestone brief, content-data template
- Pass existing content doc if present
- The content doc fills specific instances, parameters, sequences, and groups for THIS milestone — the data that instantiates the rules defined in the milestone's system GDD

A system needs a content-data doc when its GDD defines data structures that need
many concrete instances (e.g. an `enemy` GDD defines enemy attributes → content
doc fills the specific enemies in scope for this milestone).

Systems that are purely mechanical (e.g. `input`, `tbs-scoring`) typically do
NOT need content-data docs — their parameters fit within the GDD itself.

**Step 3** — Spawn `gat-artist` → `gat/milestone/m{N}-<name>/<system>/<system>-art-m{N}.md`:
- Pass `gat/overview/game.md`, `gat/overview/art-direction.md`, the milestone's system GDD, the content-data doc (if it exists), the milestone brief, system-art template
- Pass existing system art doc if present

**Step 4 — Update Progress**

After writing a system's docs, update that system's row in the milestone's
`m{N}-brief.md` progress tracker (System | GDD | Art | Data | Status) to mark
GDD/Art/Data paths filled and Status Designed. If this was the first system
designed in the milestone, also set the milestone status from `planned` to
`designing` (in both the brief and `gat/milestone/milestone.md`).

## Phase 3: Review

Summarize what was created or updated for the system(s) in the milestone.

Use `AskUserQuestion`:

- `Design another system in this milestone` → Run `/gat-design <milestone> <system>`
- `Continue remaining systems in this milestone` → Run `/gat-design <milestone>`
- `Stop here` (hand the milestone to engineering when all its systems are Designed)
