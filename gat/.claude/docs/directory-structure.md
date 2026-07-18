# Directory Structure

## Project Layout

```text
gat/                          ← all GAT-produced documents live here
  overview/
    game.md                   ← game overview (designer)
    systems-index.md          ← system map: names, deps, priorities, status (designer)
    art-direction.md          ← global art bible (artist)
  narrative/                  ← global narrative, kept coherent as a whole (writer)
    story.md                  ← premise, themes, structure, delivery
    world.md                  ← setting, factions, locations, world rules
    characters.md             ← cast, arcs, relationships, voices
    quests.md                 ← authored quest beats and consequences
    dialogue.md               ← dialogue strategy, barks, samples, UI text
  milestone/
    milestone.md              ← ordered milestone roadmap with status (planner)
    m1-<name>/                ← per-milestone handoff unit
      m1-brief.md             ← milestone brief: goal, scope, progress tracker, file refs, internal iterations (planner skeleton; designer updates progress)
      <system>/
        <system>-gdd-m1.md    ← per-system GDD scoped to this milestone (designer)
        <system>-data-m1.md   ← concrete data instances for this milestone (designer)
        <system>-art-m1.md    ← per-system art doc for this milestone (artist)
    m2-<name>/
      m2-brief.md
      <system>/
        <system>-gdd-m2.md    ← may redefine the system vs m1 (iteration is allowed)
        <system>-data-m2.md
        <system>-art-m2.md
    ...

# Source code, tests, technical designs, task lists, and implementation artifacts
# are owned by the downstream engineering workflow, not GAT.
assets/                       ← checked-in assets
```

## `.claude` Layout

```text
.claude/
  settings.json
  CLAUDE.md
  agents/
    gat-designer.md
    gat-writer.md
    gat-planner.md
    gat-artist.md
  skills/
    gat-workflow-start/SKILL.md
    gat-brainstorm/SKILL.md
    gat-story/SKILL.md
    gat-milestone/SKILL.md
    gat-design/SKILL.md
  docs/
    directory-structure.md
    workflow-catalog.yaml
    templates/
      design/
        game-overview.md
        systems-index.md
        system-gdd.md
        content-data.md
        narrative-story.md
        narrative-world.md
        narrative-characters.md
        narrative-quests.md
        narrative-dialogue.md
        global-art.md
        system-art.md
      plan/
        milestone.md
        m-brief.md
```

## Mental Model

1. `gat/overview/` defines the global game vision: pillars, core loop, system index, and shared art direction. It is the only design input `/gat-milestone` needs.
2. `gat/narrative/` defines story, world, characters, quests, and dialogue as one coherent package. It is global, not split per milestone.
3. `gat/milestone/milestone.md` breaks the game into ordered milestone slices. Planning runs BEFORE per-system design — milestone is a scope-control tool, not an archive step.
4. Each `gat/milestone/m{N}-<name>/` directory is a self-contained handoff packet: the brief (goal, scope, progress, file references) plus every system's GDD, data, and art doc for that milestone. A later milestone may redefine a system differently from an earlier one.
5. Downstream engineering workflows handle technical design, task breakdown, implementation, and verification — one milestone directory at a time.
6. `.claude/` defines how the GAT agent team produces the pre-production docs.

## Workflow Order

```text
   ┌────────────────  Loop A (refine globals) ────────────────┐
   ▼                                                          │
/gat-brainstorm  →  /gat-story         (overview + narrative)
                          │
                          ▼
                     /gat-milestone           (plan all milestone slices)
                          │
   ┌────────────────  Loop B (per milestone) ──────────────┐ │
   ▼                                                      │ │
/gat-design {M} {system}  →  engineering workflow   (one milestone per iteration)
   │                                                      │ │
   └──────── engineering feedback may flow back ──────────┘ │
                              │                             │
                              └─────────────────────────────┘
```

The flow is not a single pipeline — it has two loops:

**Loop A — refine globals (`/gat-brainstorm` ↔ `/gat-story`).** These two
iterate on the SAME global files (`gat/overview/*` and `gat/narrative/*`),
refining them over multiple passes rather than producing new files each time.
The interview can loop back and forth until overview and narrative are coherent.
Loop A can also re-enter later: engineering feedback or a later milestone's
design may surface a change to the overview or narrative, and these skills
refine the same files again.

**Loop B — iterate milestones (`/gat-design {M}` → engineering).** Each
iteration of this loop delivers ONE new milestone: design that milestone's
systems, hand the milestone directory to the downstream engineering workflow,
then loop back to design the next milestone. Different milestones can be in
progress at different stages at the same time. Engineering feedback from one
milestone may flow back into the next milestone's design (and, via Loop A, into
the globals).

`/gat-milestone` sits between the two loops: it consumes the globals from Loop A
and produces the milestone plan that Loop B iterates over.

- `/gat-brainstorm` and `/gat-story` refine the same overview/narrative files (Loop A).
- After `/gat-milestone` plans the slices, Loop B begins: `/gat-design {milestone} {system}` designs one system within one milestone, then engineering implements it.
- A milestone may enter the downstream engineering workflow as soon as its design docs are complete — later milestones do not have to be designed first.
