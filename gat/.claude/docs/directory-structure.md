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
    designer.md
    planner.md
    artist.md
  skills/
    gat-workflow-start/SKILL.md
    gat-brainstorm/SKILL.md
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
        global-art.md
        system-art.md
        content-data.md
      plan/
        milestone.md
```

## Mental Model

1. `design/` defines the game.
2. `production/milestone.md` breaks it into ordered handoff stages.
3. Downstream engineering workflows handle technical design, task breakdown, implementation, and verification.
4. `.claude/` defines how the GAT agent team produces the pre-production docs.
