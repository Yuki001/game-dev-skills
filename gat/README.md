# Simplified Game Agents

A minimal Claude Code workflow for game development, simplified from [Claude-Code-Game-Studios](https://github.com/Donchitos/Claude-Code-Game-Studios).

## Background

Claude-Code-Game-Studios is a full game studio architecture with 48 agents, 68 skills, 12 hooks, and a three-tier director hierarchy. This project strips that down to the essential pre-production document pipeline: three roles, four skills, and a linear flow from concept to milestone handoff.

What was removed: director tier, phase gates, ADR system, engine-specific agents, hook automation, and team orchestration skills.

What was kept: the document-driven handoff chain that keeps downstream engineering grounded in the same game overview, system docs, art direction, and milestone plan.

## Roles

- `gat-designer` — game overview, systems index, system GDDs, content data
- `gat-planner` — ordered milestone handoff roadmap
- `gat-artist` — global art direction and system art docs

## Skills

| Skill | What it produces |
|---|---|
| `/gat-workflow-start` | inspects repo state, recommends next step |
| `/gat-brainstorm [hint \| discuss]` | one-question-at-a-time designer interview → `game.md` + `systems-index.md` + `art-direction.md`; or discussion-only |
| `/gat-design [<system-name>]` | continues the design pipeline: all system GDDs + content data + system art docs; or add one system |
| `/gat-milestone` | ordered milestone handoff roadmap in `production/milestone.md` |

## Workflow

```
/gat-brainstorm [hint]  ← interview → game.md + systems-index.md + art-direction.md
/gat-design             ← system GDDs + content data + system art docs
/gat-milestone          ← ordered milestone handoff roadmap
# hand one milestone at a time to your downstream engineering workflow
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
# Technical design, task breakdown, implementation, and verification happen in a downstream engineering workflow.
```

## What This Repo Does Not Do

- No automatic asset generation
- No binary art pipeline
- No phase gates or director approval
- No engine-specific tooling
- No technical design, task breakdown, implementation, or verification workflow
