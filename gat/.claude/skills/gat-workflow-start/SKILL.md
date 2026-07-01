---
name: gat-workflow-start
description: "Inspect the repo state and show a status panel across all milestones, recommending the earliest actionable next step in the workflow."
argument-hint: "[no arguments]"
user-invocable: true
allowed-tools: Read, Glob, Grep, AskUserQuestion
---

# Workflow Start

This skill is the workflow router for the simplified project. Because
milestones can be in progress at different stages at the same time, it outputs a
status panel (not a single command) and recommends the earliest actionable step.

Read only `gat/` paths. Do not read or consider legacy `design/` or `production/`
paths.

## Phase 1: Inspect State

Check for these files (all under `gat/`):

- `gat/overview/game.md`
- `gat/overview/systems-index.md`
- `gat/overview/art-direction.md`
- `gat/narrative/*.md`
- `gat/milestone/milestone.md`
- each `gat/milestone/m{N}-<name>/m{N}-brief.md`
- each system's docs under `gat/milestone/m{N}-<name>/<system>/`

## Phase 2: Derive Per-Milestone Stage

For each milestone that has an `m{N}-brief.md`, derive its stage from filesystem
state:

- `planned` — brief exists, all systems Pending (no GDDs on disk)
- `designing` — at least one system designed but not all
- `designed` — every in-scope system's GDD (and art/data where required) is on disk
- `building` / `built` — user-set only; GAT cannot observe engineering. Read the
  status field from `m{N}-brief.md` if the user has advanced it past `designed`.

If the brief's status field disagrees with filesystem state, trust the brief's
status only when it is `building` or `built` (engineering stages GAT can't
derive); otherwise derive from files.

## Phase 3: Status Panel

Report a short factual summary:

```
GAT Status:

Overview:
  gat/overview/game.md          [present | missing]
  gat/overview/systems-index.md [present | missing]
  gat/overview/art-direction.md [present | missing]

Narrative:
  gat/narrative/*.md            [N docs | missing]

Milestones (from gat/milestone/milestone.md):
  M1 <name>   [planned | designing | designed | building | built]  (K/N systems designed)
  M2 <name>   [planned | designing | designed | building | built]  (K/N systems designed)
  ...
```

## Phase 4: Route

Use earliest-first priority to pick the primary recommendation, and list other
valid actions:

1. If `gat/overview/game.md`, `gat/overview/systems-index.md`, or `gat/overview/art-direction.md` is missing:
   recommend `/gat-brainstorm` (with optional hint). This is the earliest step.
2. Else if the game needs narrative (per overview/user goal) and `gat/narrative/story.md` does not exist:
   recommend `/gat-story`.
3. Else if `gat/milestone/milestone.md` is missing:
   recommend `/gat-milestone`.
4. Else if the earliest milestone with unwritten systems exists:
   recommend `/gat-design <that milestone>` (continue) or `/gat-design <that milestone> <system>`.
5. Else if the earliest milestone is fully `designed` but no later milestone needs design:
   state that the milestone is ready for engineering handoff (the user runs their downstream engineering workflow on that milestone directory).
6. Otherwise:
   state that GAT pre-production is complete for all planned milestones and tell the user to hand milestones one at a time to their downstream engineering workflow.

Always also list other valid actions (e.g., "M1 ready for engineering; M2
designing — run `/gat-design m2-<name>` to continue M2").

## Phase 5: Hand Off

End with one short line telling the user which command to run next (the primary
recommendation), plus any alternative actions.
