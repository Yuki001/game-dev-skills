# Simplified Game Agents

A minimal Claude Code workflow for game development, simplified from [Claude-Code-Game-Studios](https://github.com/Donchitos/Claude-Code-Game-Studios).

## Background

Claude-Code-Game-Studios is a full game studio architecture with 48 agents, 68 skills, 12 hooks, and a three-tier director hierarchy. This project strips that down to the essential document pipeline: four roles, six skills, and a linear flow from concept to code.

What was removed: director tier, phase gates, ADR system, engine-specific agents, hook automation, and team orchestration skills.

What was kept: the document-driven handoff chain that keeps code and art grounded in the same game overview, system docs, and milestone plan.

## Roles

- `gat-designer` — game overview, systems index, system GDDs, content data
- `gat-planner` — milestone roadmap and task lists
- `gat-programmer` — milestone tech architecture and code implementation
- `gat-artist` — global art direction, system art docs, milestone prompt packs

## Skills

| Skill | What it produces |
|---|---|
| `/gat-workflow-start` | inspects repo state, recommends next step |
| `/gat-brainstorm [hint \| discuss]` | one-question-at-a-time designer interview → `game.md` + `systems-index.md` + `art-direction.md`; or discussion-only |
| `/gat-design [<system-name>]` | continues the design pipeline: all system GDDs + content data + system art docs; or add one system |
| `/gat-milestone` | `production/milestone.md` + milestone directories |
| `/gat-plan [milestone]` | `tasks.md` + `tech.md` + `art-prompts.md` for one milestone |
| `/gat-implement [milestone \| TASK-xxx]` | implements one ready task from `tasks.md` |

## Workflow

```
/gat-brainstorm [hint]  ← interview → game.md + systems-index.md + art-direction.md
/gat-design             ← system GDDs + content data + system art docs
/gat-milestone
/gat-plan               ← repeat for each milestone
/gat-implement          ← repeat until milestone is done
```

Run `/gat-workflow-start` at any point to get the recommended next step.

## Output Structure

```
design/
  gdd/game.md
  gdd/systems-index.md
  gdd/{system}.md
  content/{system}-data.md
  art/art-direction.md
  art/{system}-art.md
production/
  milestone.md
  milestone-01-name/
    tasks.md
    tech.md
    art-prompts.md
src/
tests/
```

## What This Repo Does Not Do

- No automatic asset generation
- No binary art pipeline
- No phase gates or director approval
- No engine-specific tooling
