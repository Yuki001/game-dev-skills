---
name: game-design-review
description: Review, critique, compare, improve, or stress-test an existing game concept, GDD, mechanic, puzzle, economy, level, theme, emotional arc, interface, narrative, social feature, prototype, pitch, or playtest result. Use when the user asks what is weak, risky, unclear, unbalanced, contradictory, insufficiently engaging, or worth validating next in a game design. Produce evidence-based findings, explicit tradeoffs, and the smallest useful prototype or playtest experiment.
---

# Game Design Review

Review a design by tracing how rules and presentation are likely to shape player decisions and experience. Treat the review as a decision aid, not a universal checklist or a substitute for playtesting.

## Responsibility boundary

- Use this skill when a design object or decision already exists and needs examination.
- This skill is self-contained. Do not assume any other skill, workflow, repository layout, document set, or game engine exists.
- When the user needs a new formal design document rather than a review, return the clarified direction, constraints, open questions, and validation criteria needed to author it.
- Do not convert a design recommendation directly into code structure, engine APIs, or implementation tasks.

## Workflow

1. **Name the review object.** Identify whether the review concerns the whole game, one loop, one mechanic, a content set, a level, an interface flow, a narrative beat, a social feature, or a production choice.
2. **State the decision at stake.** Express the uncertainty as a choice or testable question. If no decision exists, identify the most consequential unresolved assumption.
3. **Build an evidence baseline.** Gather the intended audience and experience, current rules, constraints, prototype behavior, telemetry, and playtest observations. Mark every material statement as `confirmed`, `assumed`, or `unknown`.
4. **Route selectively.** Read two or three relevant references from the table below. Add another only when the first pass exposes a dependency that materially changes the decision.
5. **Trace effects.** Connect each design choice to expected player information, decision, action, feedback, and longer-term consequence. Distinguish a visible symptom from its likely cause.
6. **Prioritize findings.** Rank issues by player impact, likelihood, reversibility, and cost of learning. Do not give every observation equal weight.
7. **Recommend the smallest intervention.** Prefer a reversible rule, content, pacing, information, or presentation change that directly addresses the cause.
8. **Define validation.** End with the smallest prototype, simulation, or playtest that can distinguish the current design from the proposed alternative.

For a whole-game audit, review one domain at a time, summarize its decisions, and then run a short cross-domain contradiction pass. Do not produce one giant undifferentiated checklist.

## Reference routing

| Review concern | Read | Focus |
| --- | --- | --- |
| Audience, intended experience, motivation, comprehension | `references/experience-and-audience.md` | Player promise, motivation chain, learning assumptions, experience gaps |
| Core concept, theme, emotion, aesthetic identity, curiosity and novelty | `references/concept-theme-and-emotion.md` | Concept clarity, thematic coherence, emotional causes, expressive unity, memorable identity |
| Actions, rules, information, agency, risk and strategy | `references/actions-rules-and-agency.md` | Decision quality, rule legibility, dominant behavior, uncertainty |
| Challenge, rewards, progression, economy and replay depth | `references/challenge-progression-and-economy.md` | Difficulty shape, reward meaning, sources/sinks, viable paths |
| Puzzles, deductions, hints, bottlenecks and visible progress | `references/puzzles-and-problem-solving.md` | Problem representation, reasoning chain, solution structure, recovery and hint escalation |
| Level space, encounters, navigation and pacing | `references/space-level-and-pacing.md` | Route choice, readability, rhythm, recovery, spatial pressure |
| Attention curve, memorable moments, indirect guidance and presence | `references/attention-guidance-and-presence.md` | Interest over time, voluntary guidance, freedom, interruption, projection and retelling |
| Controls, UI, feedback and practical accessibility | `references/interface-feedback-and-accessibility.md` | Intention-to-action loop, information timing, error recovery, input and perception barriers |
| Narrative, world, characters and player-authored stories | `references/narrative-world-and-characters.md` | Playable story delivery, world causality, role, agency and character function |
| Competition, cooperation, community and harmful behavior | `references/social-community-and-safety.md` | Incentives between players, trust, expression, moderation and spectator clarity |
| Scope, prototypes, playtests, technology, business and responsibility | `references/production-validation-and-responsibility.md` | Production fit, evidence quality, risk retirement, sustainability and player welfare |

## Review modes

- **Focused review:** inspect one decision with two or three references and return only the findings that could change it.
- **Exploratory review:** when the design object is still immature, identify the player promise and central uncertainty, outline two or three coherent directions, and define a small test that can distinguish them. Stop before expanding into a full design document.
- **Comparative review:** apply the same evidence and criteria to every option; do not let one option receive a stricter review.
- **Post-playtest review:** begin with observed behavior, separate repeated patterns from anecdotes, and propose the next discriminating test.
- **Whole-game audit:** stage the review across domains, then reconcile contradictions involving audience, theme, emotion, mechanics, progression, attention, interface, narrative, scope, and production.

## Finding quality

A useful finding contains:

- **Observation:** what the current design or evidence shows;
- **Mechanism:** how it may alter player understanding, choice, behavior, or feeling;
- **Evidence status:** confirmed fact, supported inference, assumption, or unknown;
- **Impact:** what fails if the issue is real;
- **Recommendation:** the smallest change worth trying;
- **Validation:** what result would support or reject the recommendation.

Avoid findings based only on personal taste. When evidence is missing, write a hypothesis and a test rather than presenting a prediction as fact.

## Report structure

Use the shortest report that resolves the request. For a formal review, use:

```markdown
# Design Review: [object]

## Decision at stake
[The choice or uncertainty this review should resolve.]

## Evidence baseline
- Confirmed: ...
- Assumed: ...
- Unknown: ...

## Priority findings
### [Severity] [Finding]
- Observation:
- Mechanism:
- Evidence status:
- Recommendation:
- Validation:

## Tradeoffs
[What improves, what may get worse, and who is affected.]

## Next experiment
[Smallest build, simulation, or playtest; participants; observable signals; decision rule.]
```

Use `critical`, `major`, or `minor` only when severity helps prioritization:

- `critical`: undermines the core promise or prevents meaningful validation;
- `major`: materially harms a common player path or creates expensive downstream rework;
- `minor`: local friction or polish issue that does not invalidate the current direction.

## Guardrails

- Do not fabricate player reactions, telemetry, market facts, or playtest evidence.
- Do not hide conflicting goals. State the tradeoff and identify who makes the final decision.
- Do not expand the feature set merely to answer a design weakness; removal, clarification, or a smaller rule change may be better.
- Do not prescribe technical architecture. Express confirmed design constraints and validation criteria so a later technical process can consume them without requiring a particular tool or workflow.
