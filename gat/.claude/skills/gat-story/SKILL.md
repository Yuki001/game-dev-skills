---
name: gat-story
description: "Develop game story and narrative through one-question-at-a-time writer interviews. Produces narrative docs under gat/narrative/ or runs as discussion-only. Use when the user wants story, plot, lore, worldbuilding, characters, quests, dialogue, narrative tone, or authored story content for a GAT game."
argument-hint: "[<hint> | discuss]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion
---

# Story

This skill explores and documents a game's narrative through open-ended writer
interview. Spawn `gat-writer` for narrative reasoning. Spawn `gat-designer` or
`gat-artist` only when story choices need design-system or visual-direction checks.
Pick questions from the angle table below — follow the conversation, not a script.

## Phase 1: Resolve Mode

- If argument is `discuss` → Mode: `discuss` (no files written, exploration only)
- If argument is a hint or empty → Mode: `story` (produces narrative docs under `gat/narrative/`)

Check whether these files exist:

- `gat/overview/game.md`
- `gat/overview/systems-index.md`
- `gat/overview/art-direction.md`
- `gat/narrative/story.md`
- `gat/narrative/world.md`
- `gat/narrative/characters.md`
- `gat/narrative/quests.md`
- `gat/narrative/dialogue.md`

If foundational overview docs exist, read them before asking questions that they
already answer. If they are missing, proceed only with high-level narrative
brainstorming and note that final narrative docs may need revision after
`/gat-brainstorm` establishes the game overview and systems.

## Phase 2: The Interview

### Core Rules

- **One question at a time.** Never batch. Wait for the answer before the next question.
- **Provide a recommended answer** with each question. Explain the narrative reasoning.
- **Prefer open-ended questions.** Let the user type free-form responses. Reserve
  `AskUserQuestion` for concrete options where the user needs to choose.
- **Pick angles, don't follow steps.** Use the angle table as a menu. Jump to
  whatever dimension is most useful next.
- **If a question can be answered by reading existing files, read them instead of asking.**
- **Spawn `gat-writer`** when you need narrative synthesis: premise, tone,
  character arcs, world logic, quest structure, dialogue voice, or consistency checks.
- **Spawn `gat-designer`** when narrative choices affect mechanics, system
  ownership, progression, player agency, or content volume.
- **Spawn `gat-artist`** when narrative choices affect visual identity,
  character/world art hooks, readability, motifs, or asset groups.

### Drilling into Vague Narrative Ideas

When the user has a fuzzy story idea, make it playable and specific through
curious questioning.

**How to drill:**

- When the user says the story should feel a certain way, ask what event,
  character choice, or player action creates that feeling.
- When the user mentions lore, ask how the player encounters it: dialogue,
  quest, item text, environment, UI, systemic event, or cutscene.
- When a character is named, ask what they want, what blocks them, how they
  pressure the player, and whether they change.
- When the user references another work, isolate what to borrow: structure,
  tone, world texture, relationship dynamic, mystery shape, or dialogue style.
- When a branching idea appears, ask how many branches must be produced and
  whether consequences are cosmetic, systemic, or story-changing.
- When a world fact appears, ask what it causes in daily life, factions,
  resources, locations, or mechanics.
- If an answer opens three new questions, resolve the one that most affects
  player role, stakes, or content scope first.

**Signals that something is still vague and needs more drilling:**

- The user uses abstract story adjectives without concrete beats behind them
  ("dark", "emotional", "epic", "mysterious", "cozy")
- The protagonist, antagonist, or player role lacks motivation
- The world has lore but no player-facing delivery method
- The story can be summarized but not played
- Branching is proposed without content-budget boundaries
- Tone conflicts with gameplay, art direction, or target audience

### Seed Extraction

If a concept hint was provided, first spawn `gat-writer` to extract what the hint
already answers. Briefly summarize what's established so the user can confirm or
correct before diving in. Skip if no hint.

### Interview Angles

Pick questions from any angle below. There is no fixed order — follow the thread
that matters most at each moment. The table is a palette, not a checklist.

| # | Angle | Purpose | Example prompts |
|---|-------|---------|-----------------|
| 1 | **Narrative Need** | Decide whether the game needs light flavor, authored story, or deep narrative systems | How much story does this game need to work? Could it be mostly atmospheric, or does it need plot progression? |
| 2 | **Player Role** | Anchor story to the player's fantasy and verbs | Who is the player in the world? What do they do that matters narratively? |
| 3 | **Premise & Conflict** | Define the situation and pressure | What is wrong with the world when play begins? Who or what opposes the player? |
| 4 | **Stakes** | Make outcomes meaningful | What happens if the player fails? Are the stakes personal, communal, cosmic, comedic, or material? |
| 5 | **Theme** | Clarify what the story is about beneath plot | What question does the story keep asking? What value is being tested? |
| 6 | **Tone** | Set the audience contract | Should this feel sincere, tragic, funny, eerie, heroic, cozy, satirical, or something else? |
| 7 | **Structure** | Shape story progression | Is the story linear, episodic, hub-based, branching, cyclical, or emergent? |
| 8 | **World Rules** | Build coherent setting constraints | What facts about the world must always be true? What can never happen here? |
| 9 | **Factions & Power** | Create social pressure and conflict | Who holds power? Who wants change? What resources are scarce? |
| 10 | **Locations** | Turn setting into playable places | Which places must the player visit, revisit, or transform? What does each location do for the story? |
| 11 | **Characters** | Define cast function and arcs | Who matters to the player? What does each major character want, and how do they change? |
| 12 | **Antagonism** | Clarify opposition | Is the antagonist a person, system, environment, mystery, inner flaw, or rival goal? |
| 13 | **Relationships** | Create emotional stakes | Which relationships carry the story? Ally, rival, mentor, dependent, enemy, community? |
| 14 | **Quests & Beats** | Map narrative into player action | What are the key story beats, and what does the player do during each one? |
| 15 | **Choice & Consequence** | Bound interactivity | Which choices matter? Are consequences immediate, delayed, cosmetic, mechanical, or ending-related? |
| 16 | **Dialogue & Voice** | Define how characters sound | How talkative is the game? Do characters speak in full conversations, short barks, UI text, or silent implication? |
| 17 | **Environmental Storytelling** | Express story without exposition | What should the player infer from spaces, props, signs, ruins, UI, enemies, or routines? |
| 18 | **Lore Budget** | Prevent scope creep | How many factions, named NPCs, locations, lore entries, quests, and endings are reasonable for MVP? |
| 19 | **Art Hooks** | Connect narrative to visuals | What motifs, silhouettes, symbols, color meanings, or materials should art direction carry? |
| 20 | **Sensitivity & Rating** | Avoid harmful or mismatched content | Are there themes that need content warnings, cultural review, age-rating limits, or softer handling? |
| 21 | **Localization & Readability** | Keep text producible and readable | How text-heavy can the game be? Does dialogue need to be easy to localize, skip, replay, or summarize? |

### Navigating the Interview

- **Start where the energy is.** If the user leads with a character, start there.
  If they lead with setting, start with world rules. If they lead with mechanics,
  start with player role and story delivery.
- **Drill, don't move on.** When the answer is abstract, ask the follow-up that
  turns it into a beat, role, rule, or delivery method.
- **Ask open-ended, resolve with options.** Most questions should be dialogue.
  Use `AskUserQuestion` only when choosing among concrete narrative proposals.
- **Spawn `gat-writer` mid-interview** when you need a concise story proposal,
  character arc set, quest structure, or consistency pass. Present the result,
  then ask what to keep or change.
- **Loop back naturally.** If a later answer contradicts an earlier canon point,
  point it out and resolve the tension.
- **Know when to stop.** The interview has covered enough when:
  - The player role, premise, conflict, stakes, tone, and theme are clear
  - The story delivery method is known
  - The world has enough rules and locations for the game's scope
  - Major characters or factions have motivations and functions
  - Narrative content volume is bounded
  - The user starts repeating themselves rather than adding new information

## Phase 3: Write or Summarize

### If Mode is `story`

Before writing, summarize what's been decided across premise, world, characters,
structure, delivery, scope, and open questions. Ask:

> "Ready to write the narrative docs?"
> Options: `Yes, write them` / `Let me keep discussing`

If yes, read the relevant templates:

- `.claude/docs/templates/design/narrative-story.md`
- `.claude/docs/templates/design/narrative-world.md`
- `.claude/docs/templates/design/narrative-characters.md`
- `.claude/docs/templates/design/narrative-quests.md`
- `.claude/docs/templates/design/narrative-dialogue.md`

Spawn `gat-writer` to write the narrative docs under `gat/narrative/`.

Always write or update:

- `gat/narrative/story.md`

Write or update these only when the game needs them:

- `gat/narrative/world.md` for setting rules, factions, locations, culture, or environmental storytelling
- `gat/narrative/characters.md` for named cast, factions-as-characters, voice, arcs, or relationships
- `gat/narrative/quests.md` for authored missions, story objectives, progression beats, or branching consequences
- `gat/narrative/dialogue.md` for conversations, barks, VO, UI narrative text, or reusable voice rules

Pass all interview answers, existing overview/narrative files, and the selected
templates. Instruct the writer to preserve template metadata and source-reference
sections, mark uncertain material as open questions, and keep outputs concise.

### If Mode is `discuss`

Summarize what was decided and what remains open. No files written.

Suggest:

- `/gat-story` (without `discuss`) to turn this discussion into narrative docs
- `/gat-milestone` to plan milestone slices after overview (and narrative, if needed) are ready

## Phase 4: Hand Off

Summarize what was created or discussed.

If narrative docs were written, suggest next steps:

- `/gat-milestone` to plan milestone slices (milestone planning runs BEFORE per-system design; do NOT run `/gat-design` directly from here)
- If story revealed or changed systems, update `gat/overview/systems-index.md` (via `/gat-brainstorm` or directly) before planning milestones
