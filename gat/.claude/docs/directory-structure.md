# Directory Structure

## Project Layout

```text
design/
  gdd/
    game.md               ← game overview (designer)
    systems-index.md      ← system map (designer)
    {system}.md           ← per-system GDD (designer)
  art/
    art-direction.md      ← global art bible (artist)
    {system}-art.md       ← per-system art doc (artist)

production/
  milestone.md            ← milestone roadmap (planner)
  milestone-01-name/
    tasks.md              ← implementation task list (planner)
    tech.md               ← milestone architecture (programmer)
    art-prompts.md        ← text prompt pack (artist)

src/                      ← game code (programmer)
tests/                    ← tests (programmer)
assets/                   ← checked-in assets
```

## `.claude` Layout

```text
.claude/
  settings.json
  agents/
    designer.md
    planner.md
    programmer.md
    artist.md
  skills/
    workflow-start/SKILL.md
    design/SKILL.md
    milestone/SKILL.md
    plan/SKILL.md
    implement/SKILL.md
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
      plan/
        milestone.md
        tech.md
        tasks.md
        art-prompts.md
```

## Mental Model

1. `design/` defines the game.
2. `production/` breaks it into milestone execution packets.
3. `src/` and `tests/` realize one task at a time.
4. `.claude/` defines how the agent team produces all of the above.
