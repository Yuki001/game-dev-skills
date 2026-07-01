# GAT — Game Agents Toolkit

A minimal Claude Code workflow for game pre-production. Four roles, five skills,
and a milestone-driven document pipeline that hands off to a downstream
engineering workflow one milestone at a time.

## Why

Most game-design workflows force a waterfall: design the whole game up front,
then plan milestones, then build. GAT inverts that. Milestone planning runs
BEFORE per-system design, so you only design the systems needed for the current
slice, and engineering feedback from one milestone can reshape the next.

## Roles

- `gat-designer` — game overview, systems index, and per-milestone system GDDs + content data
- `gat-writer` — story, worldbuilding, characters, quests, dialogue (global, coherent as a whole)
- `gat-planner` — milestone roadmap and per-milestone brief skeletons
- `gat-artist` — global art direction and per-milestone system art docs

## Skills

| Skill | What it produces |
|---|---|
| `/gat-workflow-start` | status panel across all milestones + recommended next step |
| `/gat-brainstorm [hint \| discuss]` | one-question-at-a-time designer interview → `gat/overview/` (game.md + systems-index.md + art-direction.md); or discussion-only |
| `/gat-story [hint \| discuss]` | one-question-at-a-time writer interview → narrative docs under `gat/narrative/`; or discussion-only |
| `/gat-milestone [focus]` | milestone roadmap + per-milestone directory skeletons + `m{N}-brief.md` skeletons. Needs only overview + narrative; no system GDDs required |
| `/gat-design {milestone} {system \| hint}` | designs one system within a milestone → that milestone's GDD + content data + art doc, and updates the brief's progress. `{milestone}` is mandatory |

## Workflow

The flow is not a single pipeline — it has two loops:

```
   ┌────────────  Loop A: refine globals  ────────────┐
   ▼                                                 │
/gat-brainstorm  →  /gat-story      (overview + narrative, same files refined)
                        │
                        ▼
                   /gat-milestone        (plan all milestone slices)
                        │
   ┌────────────  Loop B: per milestone  ───────────┐│
   ▼                                                ││
/gat-design {M} {system}  →  engineering workflow   (one milestone per iteration)
   │                                                ││
   └──── engineering feedback flows back ───────────┘│
                            │                         │
                            └─────────────────────────┘
```

- **Loop A — refine globals** (`/gat-brainstorm` ↔ `/gat-story`): iterate on the
  SAME global files (`gat/overview/*`, `gat/narrative/*`), refining them over
  multiple passes. Can re-enter later when feedback surfaces a change.
- **Loop B — iterate milestones** (`/gat-design {M}` → engineering): each
  iteration delivers ONE new milestone — design it, hand it to engineering, loop
  back for the next. Multiple milestones can be in progress at different stages.

`/gat-milestone` sits between the two loops: it consumes the globals from Loop A
and produces the milestone plan that Loop B iterates over.

Run `/gat-workflow-start` at any point to see the status panel and the recommended next step.

## Output Structure

```
gat/
  overview/
    game.md                    ← global game vision (designer)
    systems-index.md           ← global system registry: names, deps, priorities (designer)
    art-direction.md           ← global art bible (artist)
  narrative/                   ← global narrative, kept coherent as a whole (writer)
    story.md / world.md / characters.md / quests.md / dialogue.md
  milestone/
    milestone.md               ← ordered milestone roadmap with status (planner)
    m1-<name>/                 ← self-contained handoff packet for one milestone
      m1-brief.md              ← goal, scope, progress tracker, file refs (planner skeleton; designer updates progress)
      <system>/
        <system>-gdd-m1.md     ← per-system GDD scoped to this milestone (designer)
        <system>-data-m1.md    ← concrete data instances for this milestone (designer)
        <system>-art-m1.md     ← per-system art doc for this milestone (artist)
    m2-<name>/                 ← a later milestone may redefine a system differently from m1
      ...
# Technical design, task breakdown, implementation, and verification happen in a
# downstream engineering workflow, one milestone directory at a time.
```

## What This Repo Does Not Do

- No automatic asset generation
- No binary art pipeline (art outputs are text only)
- No technical design, task breakdown, implementation, or verification workflow — those belong downstream
- No auto-migration of legacy `design/` or `production/` files — GAT skills read and write only `gat/` paths
