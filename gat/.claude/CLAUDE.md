# Simplified Game Agents

This repository defines a minimal Claude Code workflow for game development.

## Team

- `designer` owns `design/gdd/game.md`, `design/gdd/systems-index.md`, system GDD files, and `design/content/*-data.md` content documents
- `planner` owns `production/milestone.md` and milestone production folders
- `programmer` owns milestone `tech.md` files plus `src/` and `tests/`
- `artist` owns `design/art/art-direction.md`, system art docs, and milestone `art-prompts.md` files

## Main Flow

`/gat-design [hint] -> /gat-milestone -> /gat-plan -> /gat-implement`

## Working Rules

- Keep documents concise and implementation-facing
- Prefer updating existing files over creating parallel variants
- Keep the game overview separate from the per-system documents
- Use `.claude/docs/templates/design/*` and `.claude/docs/templates/plan/*` as the canonical scaffolds
- System GDDs define rules and data structures; `design/content/<system>-data.md` fills specific instances
- Preserve template metadata and source-reference sections unless a section is truly not applicable
- Track system order in `design/gdd/systems-index.md`
- Plan milestones before creating milestone-level documents
- Break each milestone into small tasks before writing code
- Implement one task at a time
- Art outputs are text only in this repo
- If the design docs are ambiguous, clarify them before planning or coding

## References

@.claude/docs/directory-structure.md
@.claude/docs/workflow-catalog.yaml

Start with `/workflow-start` if you want the repo to tell you the next step.
