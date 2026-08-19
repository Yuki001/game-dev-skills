# Interface, Feedback, and Accessibility Review

Use this reference for controls, physical interaction context, HUD, menus, information timing, feedback, error recovery, remapping, readability, sensory alternatives, and difficulty accommodations.

## Evidence to collect

- Venue, posture, viewing distance, input hardware, input maps, interaction flows, HUD states, notification priorities, tutorials, error messages, and accessibility settings;
- recordings of input, game response, animation, sound, network acknowledgement, and visible state change;
- misinputs, repeated inputs, missed signals, menu abandonment, remapping needs, and device-specific failures;
- target display sizes, viewing distances, color and contrast constraints, text density, subtitle needs, and motion effects.

## Review prompts

### Intention-to-action loop

- Can the player discover an available action when it becomes relevant?
- Does the mapping remain predictable across modes and contexts?
- Can the player cancel, correct, or safely retry an accidental action?

### Physical context and mapping

- How do venue, posture, reach, viewing distance, ambient noise, interruption, and session length affect interaction?
- Does the physical action map naturally to the in-game action, especially for touch, motion, VR, arcade, or custom hardware?
- Can repeated actions be performed comfortably and reliably across the intended session?

### Interface model

- What does the interface invite players to believe they are manipulating: an object, space, character, instrument, document, or command system?
- Does that model predict how unfamiliar controls and states behave?
- Where does the interface break its own model for convenience, and is the exception communicated before it causes an error?

### Information timing

- What must the player know before choosing, while acting, and after resolution?
- Is critical information available in the player's likely focus area and for long enough to be understood?
- Which signals compete for the same visual, audio, or haptic channel?

### Feedback causality

- Which response confirms input acceptance, state change, success, failure, and magnitude?
- Can players distinguish a rule restriction from input loss, latency, cooldown, or animation lock?
- Are strong effects reserved for meaningful events so that emphasis remains legible?

### Feedback richness

- Does the core interaction produce continuous feedback during the action, not only at its resolution?
- Does one player action create visible second-order effects, such as chain reactions or cascading motion, that amplify its felt impact?
- Is the most repeated action satisfying to perform even when its outcome is routine?
- Can players understand the core interaction from physical intuition before learning any symbols or rules?

### Mode and context

- How does the player recognize a control or UI mode change before acting under the wrong assumption?
- Do keyboard, controller, touch, and assistive-input flows preserve the same capability even when layouts differ?
- Does stress or speed make a normally clear interface unreliable?

### Practical accessibility

- Is important meaning duplicated across color, shape, position, text, sound, or haptics where necessary?
- Can text, subtitles, timing windows, hold/toggle behavior, camera motion, and control bindings adapt without breaking rules?
- Do difficulty options describe what they change instead of attaching judgment to the player?

## Failure signals

- players repeat an input because acknowledgement is late or ambiguous;
- the most frequent action feels inert until its result appears, so repetition becomes tiring;
- HUD density grows while decision-relevant information remains hard to find;
- a color-only, sound-only, or short-duration signal carries critical meaning;
- remapping produces conflicts or leaves required actions unavailable;
- interface modes reuse controls without clear transition feedback;
- the physical setup makes a frequent action tiring, imprecise, inaccessible, or socially awkward;
- interface symbols suggest one model while behavior follows another;
- accessibility settings exist individually but combine into an unusable state.

## Small experiments

- Measure the delay from input to each feedback channel for one core action.
- Test a critical encounter with one presentation channel removed and identify lost information.
- Ask players to complete one flow using a different input device or remapped layout without coaching.
- Compare comprehension using a simplified HUD against the current HUD at the intended viewing distance.
- Test the same core interaction in its actual venue and posture rather than only at a development desk.
- Introduce one unfamiliar action and ask players to predict its result from the existing interface model before trying it.
- Remove one feedback layer, such as particles, animation, or sound, from a core action and measure how much slower players learn it or how much sooner they tire of it.
