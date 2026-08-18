# Interface, Feedback, and Accessibility Review

Use this reference for controls, HUD, menus, information timing, feedback, error recovery, remapping, readability, sensory alternatives, and difficulty accommodations.

## Evidence to collect

- Input maps, interaction flows, HUD states, notification priorities, tutorials, error messages, and accessibility settings;
- recordings of input, game response, animation, sound, network acknowledgement, and visible state change;
- misinputs, repeated inputs, missed signals, menu abandonment, remapping needs, and device-specific failures;
- target display sizes, viewing distances, color and contrast constraints, text density, subtitle needs, and motion effects.

## Review prompts

### Intention-to-action loop

- Can the player discover an available action when it becomes relevant?
- Does the mapping remain predictable across modes and contexts?
- Can the player cancel, correct, or safely retry an accidental action?

### Information timing

- What must the player know before choosing, while acting, and after resolution?
- Is critical information available in the player's likely focus area and for long enough to be understood?
- Which signals compete for the same visual, audio, or haptic channel?

### Feedback causality

- Which response confirms input acceptance, state change, success, failure, and magnitude?
- Can players distinguish a rule restriction from input loss, latency, cooldown, or animation lock?
- Are strong effects reserved for meaningful events so that emphasis remains legible?

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
- HUD density grows while decision-relevant information remains hard to find;
- a color-only, sound-only, or short-duration signal carries critical meaning;
- remapping produces conflicts or leaves required actions unavailable;
- interface modes reuse controls without clear transition feedback;
- accessibility settings exist individually but combine into an unusable state.

## Small experiments

- Measure the delay from input to each feedback channel for one core action.
- Test a critical encounter with one presentation channel removed and identify lost information.
- Ask players to complete one flow using a different input device or remapped layout without coaching.
- Compare comprehension using a simplified HUD against the current HUD at the intended viewing distance.

