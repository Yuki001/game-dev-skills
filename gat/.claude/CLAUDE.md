# Simplified Game Agents

This repository defines a minimal Claude Code workflow for game development.

## Team

- `designer` owns `gat/overview/game.md`, `gat/overview/systems-index.md`, and per-milestone system GDD + content-data docs under `gat/milestone/m{N}-<name>/<system>/`
- `writer` owns `gat/narrative/*` story, world, character, quest, and dialogue documents (global, not split per milestone)
- `planner` owns `gat/milestone/milestone.md` and the `m{N}-brief.md` skeletons under each milestone directory
- `artist` owns `gat/overview/art-direction.md` and per-milestone system art docs under `gat/milestone/m{N}-<name>/<system>/`

## Main Flow

`/gat-brainstorm [hint] -> /gat-story -> /gat-milestone -> /gat-design {milestone} {system} -> downstream engineering workflow`

Milestone planning runs BEFORE per-system design. `/gat-milestone` needs only `gat/overview/` (and reads `gat/narrative/`); it does not require any system GDDs to exist.

`/gat-story` is optional for abstract or non-narrative games, but use it before milestone planning when story, world, characters, quests, dialogue, or authored narrative content matter.

The flow has two loops:

- **Loop A — refine globals (`/gat-brainstorm` ↔ `/gat-story`):** iterate on the SAME global files (`gat/overview/*` and `gat/narrative/*`), refining them over multiple passes. May re-enter later when engineering or later-milestone feedback surfaces a change to the overview or narrative.
- **Loop B — iterate milestones (`/gat-design {M}` → engineering):** each iteration delivers ONE new milestone — design its systems, hand the milestone directory to engineering, then loop back for the next milestone. Each milestone brief includes detailed internal iterations for the downstream engineering workflow to handle. Multiple milestones may be in progress at different stages at the same time.

`/gat-milestone` sits between the two loops: it consumes the globals from Loop A and produces the milestone plan that Loop B iterates over.

## Working Rules

- Keep documents concise and implementation-facing
- Prefer updating existing files over creating parallel variants
- Keep the global overview (`gat/overview/`) separate from per-milestone system documents
- Keep narrative docs separate from gameplay system GDDs; narrative is global and coherent, not split per milestone
- Use `.claude/docs/templates/design/*` and `.claude/docs/templates/plan/*` as the canonical scaffolds
- System GDDs define rules and data structures; `<system>-data-m{N}.md` fills specific instances for that milestone
- Narrative docs define premise, world, cast, quests, and dialogue delivery; gameplay mechanics still belong in GDDs
- Preserve template metadata and source-reference sections unless a section is truly not applicable
- Track the global system list in `gat/overview/systems-index.md`; track per-milestone progress in each `m{N}-brief.md`
- `/gat-design` requires a mandatory `{milestone}` argument — if omitted, it stops and asks for one. No inference, default, or fallback
- A later milestone may redefine a system differently from an earlier one (additions, modifications, even conflicts). This is expected iteration, not an error
- `gat/milestone/milestone.md` is an ordered set of milestone handoff slices with status (`planned -> designing -> designed`), not a task plan
- Different milestones may be in progress at the same time at different stages. A milestone may enter the engineering workflow as soon as its design docs are complete — later milestones need not be designed first
- Engineering feedback may flow back to update `gat/overview/`, `gat/narrative/`, or the remaining milestone plan. Detecting docs made stale by such edits is the user's responsibility, not automated
- Technical design, implementation task breakdown, verification plans, and code changes happen outside GAT
- Art outputs are text only in this repo
- If the design or narrative docs are ambiguous, clarify them before milestone planning or downstream handoff
- GAT skills read and write only `gat/` paths. Legacy `design/` and `production/` paths are not read or written

## References

@.claude/docs/directory-structure.md
@.claude/docs/workflow-catalog.yaml

Start with `/gat-workflow-start` if you want the repo to tell you the next step.
