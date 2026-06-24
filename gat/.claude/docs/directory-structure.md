# Directory Structure

## Project Layout

```text
design/
  gdd/
    game.md               ← game overview (designer)
    systems-index.md      ← system map (designer)
    {system}.md           ← per-system GDD (designer)
  content/
    {system}-data.md      ← concrete data instances (designer)
  narrative/
    story.md              ← premise, themes, structure, delivery (writer)
    world.md              ← setting, factions, locations, world rules (writer)
    characters.md         ← cast, arcs, relationships, voices (writer)
    quests.md             ← authored quest beats and consequences (writer)
    dialogue.md           ← dialogue strategy, barks, samples, UI text (writer)
  art/
    art-direction.md      ← global art bible (artist)
    {system}-art.md       ← per-system art doc (artist)

production/
  milestone.md            ← ordered milestone handoff roadmap (planner)

# Source code, tests, technical designs, task lists, and implementation artifacts
# are owned by the downstream engineering workflow, not GAT.
assets/                   ← checked-in assets
```

## `.claude` Layout

```text
.claude/
  settings.json
  agents/
    gat-designer.md
    gat-writer.md
    gat-planner.md
    gat-artist.md
  skills/
    gat-workflow-start/SKILL.md
    gat-brainstorm/SKILL.md
    gat-story/SKILL.md
    gat-design/SKILL.md
    gat-milestone/SKILL.md
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
```

## Mental Model

1. `design/` defines the game, including systems, content, narrative, and art direction.
2. `production/milestone.md` breaks it into ordered handoff stages.
3. Downstream engineering workflows handle technical design, task breakdown, implementation, and verification.
4. `.claude/` defines how the GAT agent team produces the pre-production docs.
