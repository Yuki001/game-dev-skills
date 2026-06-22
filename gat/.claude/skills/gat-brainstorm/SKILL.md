---
name: gat-brainstorm
description: "Brainstorm a game idea through one-question-at-a-time designer interviews. Produces game.md and systems-index.md, or runs as discussion-only."
argument-hint: "[<hint> | discuss]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion
---

# Brainstorm

This skill explores a game concept through open-ended designer interview.
Spawn `gat-designer` for design reasoning. Pick questions from the angle table
below — follow the conversation, not a script.

## Phase 1: Resolve Mode

- If argument is `discuss` → Mode: `discuss` (no files written, exploration only)
- If argument is a hint or empty → Mode: `design` (produces design docs)

Check whether `design/gdd/game.md` already exists. If so, note it — the
interview may refine or replace existing decisions.

## Phase 2: The Interview

### Core Rules

- **One question at a time.** Never batch. Wait for the answer before the next question.
- **Provide a recommended answer** with each question. Explain the design reasoning.
- **Prefer open-ended questions.** Let the user type free-form responses. Reserve
  `AskUserQuestion` (multiple-choice) for when you are presenting concrete solution
  options and need the user to pick one. Most of the interview should be dialogue,
  not forms.
- **Pick angles, don't follow steps.** Use the angle table as a menu. Jump to
  whatever dimension is most useful next — chase what's interesting or ambiguous.
- **If a question can be answered by reading existing design files, read them
  instead of asking.**
- **Spawn `gat-designer`** when you need a design reasoning pass: drafting a core
  loop, proposing systems, evaluating a trade-off, or checking consistency.

### Drilling into Vague Ideas

When the user has a fuzzy idea — about the whole game or a single system — your
job is to make it concrete through relentless, curious questioning. This is the
core of the interview.

**How to drill:**

- When the user says something vague ("combat should feel impactful"), ask what
  specifically makes it impactful — is it animation, sound, damage numbers,
  controller rumble, enemy reaction, time-to-kill? Keep asking until the
  abstraction bottoms out in concrete mechanics.
- When the user proposes a system, ask about its boundaries. What does it NOT
  do? What system owns the adjacent responsibility? A system without edges is
  still fuzzy.
- When the user describes a player experience ("I want the player to feel
  lost"), ask what the game does to create that feeling. What does the player
  see, hear, and do? What information is withheld? What mechanics produce the
  emotion?
- When the user references another game ("like Dark Souls but..."), isolate what
  exactly they want to keep and what they want to change. The reference is a
  shortcut — unpack it.
- Ask about edge cases and failure states. What happens when the player ignores
  the system? What happens when they optimize it to the extreme? The answers
  reveal whether the system is understood or still hazy.
- Ask about the player's moment-to-moment decisions. If the user can't describe
  what choices the player makes inside the system, the system isn't clear yet.
- If an answer opens three new questions, pick the most foundational one first.
  Resolve dependencies before details.

**Signals that something is still vague and needs more drilling:**

- The user uses abstract adjectives without mechanics behind them ("fun",
  "smooth", "deep", "cool")
- A system is named but its inputs, outputs, and rules are undefined
- Two systems have overlapping or unclear boundaries
- The user can describe what the system IS but not what the player DOES in it
- Numbers are absent where they matter (how many? how long? how much?)

### Seed Extraction

If a concept hint was provided, first spawn `gat-designer` to extract what the
hint already answers. Briefly summarize what's established so the user can
confirm or correct before diving in. Skip if no hint.

### Interview Angles

Pick questions from any angle below. There is no fixed order — follow the
thread that matters most at each moment. The table is a palette, not a checklist.

| # | Angle | Purpose | Example prompts |
|---|-------|---------|-----------------|
| 1 | **Genre & Style** | Establish the game's identity and reference points | What genre(s) does this live in? What games should it feel like? Real-time or turn-based? 2D or 3D? Single-player, co-op, or competitive? |
| 2 | **Core Player Verb** | Pin down the primary action the player repeats | What does the player actually DO moment-to-moment — shoot, build, explore, talk, craft, steer, command? What makes that action satisfying? |
| 3 | **Target Feeling** | Define the emotional experience | What should the player feel during play — tension, mastery, wonder, power, relaxation, social connection, fear, curiosity? When do they feel it most? |
| 4 | **Fantasy & Role** | Clarify who the player is in the world | What fantasy does the game fulfill? Who is the player — hero, commander, survivor, creator, investigator, merchant? |
| 5 | **Scope & Constraints** | Set boundaries early | Rough scope (jam, indie, commercial)? Platform? Timeline? Team size? Content rating? Hard constraints? |
| 6 | **Core Loop** | Map the repeatable cycle that drives engagement | What's the 30-second loop? The 5-minute loop? The session loop? What pulls the player back in? |
| 7 | **Systems & Mechanics** | Explore what systems the game needs | What systems does the core loop imply? Which are essential vs. nice-to-have? What does each system depend on? |
| 8 | **Progression & Goals** | Define how the player grows and what they strive for | Short-term goals? Long-term goals? Skill tree or gear-based? Linear or branching? How does difficulty ramp? |
| 9 | **Economy & Resources** | Map currencies, sinks, and sources | What resources does the player manage? How are they earned and spent? Is there inflation risk? |
| 10 | **Risk & Reward** | Balance tension against payoff | What does the player risk losing? What do they gain for taking risks? Is failure interesting or just punishing? |
| 11 | **Player Agency** | How much control and choice the player has | Where do players make meaningful choices? Are choices tactical (moment-to-moment) or strategic (long-term)? Emergent or scripted? |
| 12 | **Feedback & Juice** | How the game communicates back to the player | How does the player know they did something right? What visual/audio hooks sell the actions? Screen shake, particles, sound? |
| 13 | **Onboarding & Clarity** | How the player learns the game | Tutorial or discovery? How do you teach without lecturing? What's the first thing a new player does? |
| 14 | **Narrative & World** | Story, setting, and tone | Is there a story? Player-driven or authored? What's the tone? How does the world reinforce the mechanics? |
| 15 | **Multiplayer & Social** | Other humans in the experience | Cooperative, competitive, or solo with social features? Synchronous or asynchronous? How do players interact? |
| 16 | **Replayability & Depth** | What keeps players coming back | Procedural generation, build variety, difficulty modes, secrets? What's different on run #2 vs. run #50? |
| 17 | **Accessibility** | Who can play and how | Difficulty options? Color independence? Remappable controls? Reaction-time accommodations? |
| 18 | **Monetization** | Business model (if applicable) | Premium, F2P, subscription? If F2P, what's sold and does it affect gameplay? Any dark patterns to avoid? |
| 19 | **Platform & Controls** | Input method and platform constraints | Mouse/keyboard, controller, touch? How many buttons does the design assume? Platform-specific constraints? |
| 20 | **Content Volume** | How much stuff the game needs | How many levels, enemies, items, abilities? Is content hand-crafted, procedural, or both? What's the MVP slice? |

### Navigating the Interview

- **Start where the energy is.** If the user leads with a mechanic, start at
  Systems. If they describe a feeling, start at Target Feeling. If they mention
  a reference game, start at Genre & Style.
- **Drill, don't move on.** When the user gives a vague or high-level answer,
  stay on that thread. Ask the follow-up that forces them to be specific. See
  "Drilling into Vague Ideas" above — this is where most of the value comes from.
- **Dive when something is interesting.** A throwaway answer about "the world is
  post-apocalyptic" might open a rich thread about Narrative & World, Economy
  (scarcity), or Fantasy & Role. Follow it.
- **Ask open-ended, resolve with options.** Most questions should be free-form
  dialogue — the user types their thoughts. Use `AskUserQuestion` only when you
  have 2-3 concrete design proposals and need the user to choose among them (e.g.
  picking a core loop direction, choosing between two system architectures).
- **Spawn `gat-designer` mid-interview** when you need to synthesize answers
  into a concrete proposal (core loop draft, system list, trade-off analysis).
  Present what the agent returns, then ask about it.
- **Loop back naturally.** If a later answer contradicts an earlier assumption,
  point it out and resolve the tension. Don't pretend consistency exists when it
  doesn't.
- **Know when to stop.** The interview has covered enough when:
  - The core loop is clear and the user can describe it in their own words
  - The system list is named with rough dependencies
  - Scope boundaries are set
  - The user starts repeating themselves rather than adding new information

## Phase 3: Write or Summarize

### If Mode is `design`

Before writing, summarize what's been decided. Ask:

> "Ready to write the design docs?"
> Options: `Yes, write them` / `Let me keep discussing`

If yes, read templates:
- `.claude/docs/templates/design/game-overview.md`
- `.claude/docs/templates/design/systems-index.md`

Spawn `gat-designer` to write both files in one pass:
- `design/gdd/game.md`
- `design/gdd/systems-index.md`

Pass all interview answers, the confirmed system list with dependencies, and
both templates.

### If Mode is `discuss`

Summarize what was decided and what remains open. No files written.

Suggest:
- `/gat-brainstorm` (without `discuss`) to turn this discussion into design docs
- `/gat-design` to continue the pipeline (only after design docs exist)

## Phase 4: Hand Off

Summarize what was created or discussed.

If design docs were written, suggest next steps:
- `/gat-design` to continue the pipeline (art-direction, system GDDs, art docs)
- `/gat-milestone` to break the game into milestones (only after all design docs are complete)
