# Simplified Game Agents

This repository defines a minimal Claude Code workflow for game development.

## Team

- `designer` owns `design/gdd/game.md`, `design/gdd/systems-index.md`, system GDD files, and `design/content/*-data.md` content documents
- `writer` owns `design/narrative/*` story, world, character, quest, and dialogue documents
- `planner` owns `production/milestone.md`
- `artist` owns `design/art/art-direction.md` and system art docs

## Main Flow

`/gat-brainstorm [hint] -> /gat-story -> /gat-design -> /gat-milestone -> downstream engineering workflow`

`/gat-story` is optional for abstract or non-narrative games, but use it before milestone planning when story, world, characters, quests, dialogue, or authored narrative content matter.

## Working Rules

- Keep documents concise and implementation-facing
- Prefer updating existing files over creating parallel variants
- Keep the game overview separate from the per-system documents
- Keep narrative docs separate from gameplay system GDDs
- Use `.claude/docs/templates/design/*` and `.claude/docs/templates/plan/*` as the canonical scaffolds
- System GDDs define rules and data structures; `design/content/<system>-data.md` fills specific instances
- Narrative docs define premise, world, cast, quests, and dialogue delivery; gameplay mechanics still belong in GDDs
- Preserve template metadata and source-reference sections unless a section is truly not applicable
- Track system order in `design/gdd/systems-index.md`
- Plan milestones before handing work to downstream engineering
- `production/milestone.md` is an ordered set of milestone handoff slices, not a task plan
- Technical design, implementation task breakdown, verification plans, and code changes happen outside GAT
- Art outputs are text only in this repo
- If the design or narrative docs are ambiguous, clarify them before milestone planning or downstream handoff

## References

@.claude/docs/directory-structure.md
@.claude/docs/workflow-catalog.yaml

Start with `/gat-workflow-start` if you want the repo to tell you the next step.
