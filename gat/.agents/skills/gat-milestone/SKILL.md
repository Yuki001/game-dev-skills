---
name: gat-milestone
description: Plan ordered GAT milestone handoff slices from overview and narrative documents, create the milestone roadmap and per-milestone brief skeletons, and stop before technical design or implementation. Use after foundational GAT documents are ready and before per-system design.
---

# Milestone

## Codex Runtime

This skill is fully contained in the installed `.agents` directory. Resolve all linked resources relative to this `SKILL.md`; do not read workflow resources outside this packaged directory.

Before acting, read [GAT Workflow](../../references/gat-workflow.md). Read [Directory Structure](../../references/directory-structure.md) or [Workflow Catalog](../../references/workflow-catalog.yaml) only when their structure or ownership details are needed.

Use these packaged role profiles for every role-specific pass:

- [gat-planner](../../references/roles/gat-planner.md)

When the workflow says to spawn one of these roles, create a Codex subagent with that exact task name when collaboration is available. Give it the complete role profile, relevant source documents, confirmed decisions, template, and exact target paths; wait for it and review its result before continuing. This skill explicitly authorizes those named workflow subagents. If subagents are unavailable, perform the same pass yourself using the packaged role profile.

Treat the directory containing `.agents` as the repository root. All GAT project documents live under that root's `gat/` directory. Use Codex filesystem tools and the environment's supported patch editor while preserving unrelated user changes.

Interpret `AskUserQuestion` in the procedure as a single concise user question. Use a structured choice UI only for a genuine 2-3 option decision; otherwise ask in ordinary dialogue and wait. Command examples use Codex skill syntax (`$gat-*`).


This skill plans milestone slices BEFORE per-system design and creates:

- `gat/milestone/milestone.md` — the ordered milestone roadmap with status
- `gat/milestone/m{N}-<name>/` — per-milestone directory skeletons
- `gat/milestone/m{N}-<name>/m{N}-brief.md` — milestone brief skeletons (all systems Pending, status `planned`)

It does NOT require any system GDD to exist. It does not create task lists,
technical designs, prompt packs, or implementation files. Those belong to the
downstream engineering workflow.

## Phase 1: Validate Inputs

Fail if any of these are missing:

- `gat/overview/game.md`
- `gat/overview/systems-index.md`
- `gat/overview/art-direction.md`

Do NOT fail when no system GDDs exist. Planning runs before design; the systems
index's priorities and dependencies are sufficient input for slicing.

Read:

- `gat/overview/game.md`
- `gat/overview/systems-index.md`
- `gat/overview/art-direction.md`
- all existing `gat/narrative/*.md` (used to inform milestone boundaries)
- `../../assets/templates/plan/milestone.md`
- `../../assets/templates/plan/m-brief.md`
- `gat/milestone/milestone.md` if it already exists
- existing `gat/milestone/m{N}-<name>/m{N}-brief.md` files if any milestones are already planned

## Phase 2: Hand Off To The Planner

Spawn `gat-planner` agent with all read content plus:

- instruction to write or update `gat/milestone/milestone.md` as an ordered set of milestone slices (`M01`, `M02`, ...) with a status column (`planned -> designing -> designed`)
- instruction to create a directory `gat/milestone/m{N}-<name>/` for each planned milestone
- instruction to author an `m{N}-brief.md` skeleton (template: `../../assets/templates/plan/m-brief.md`) for each milestone, listing every in-scope system with status Pending and the milestone status `planned`
- instruction to add an internal iteration plan to each brief using the template's repeated subsections;
- instruction NOT to write system GDDs, content-data docs, art docs, task lists, technical designs, prompt packs, or code
- planning focus from argument if provided

The planner should:

- choose a small set of meaningful milestones that can be handed off one stage at a time
- give each milestone a clear goal, player-facing outcome, and named system set
- define what is in scope and explicitly out of scope for each milestone
- use the systems index priorities + dependencies + narrative structure to slice; it does not need per-system rule detail
- include overview, narrative (scoped range), and content context needed by a downstream engineering workflow
- avoid technical architecture, file plans, coding tasks, and implementation sequencing
- set each new milestone's status to `planned`

## Phase 3: Review

Summarize how many milestones were planned, which comes first, and which directories/briefs were created.

Use `AskUserQuestion`:

- `Start designing the first milestone (Recommended)` → Tell the user to run `$gat-design <first-milestone> <system>` or `$gat-design <first-milestone>` (continue)
- `Stop here`
