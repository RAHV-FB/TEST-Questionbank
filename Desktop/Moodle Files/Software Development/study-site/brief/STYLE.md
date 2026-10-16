# Writing style

The reader is a smart second/third-year business + AI student who has done one Python course, has attended the
sessions with varying attention, and has eight days. They want to understand, not to be entertained.

## Voice
- British spelling, matching the teacher: behaviour, organise, licence (noun), colour, artefact, favourite, recognise.
  (Code keeps its own spelling: `color` stays `color` inside code.)
- Use the course's own vocabulary and examples: "the referee, not the judge", functional core / imperative shell,
  Definition of Done, guard clauses, "a tuple is a missing type", "computation is not output", "fail loudly at the boundary",
  "works on my machine", Bar Ramon / Zara / Cabify expenses, `total_by_category`, `remove_duplicates`, `largest_expense`.
- Short, direct sentences. Active voice. Second person ("you") for instructions and explanations.
- Concrete over abstract: show the line of code, the output, the number.
- Explanations reason like a good teacher marking a script: name the misconception, then the idea that fixes it.

## Never
- Emoji, exclamation marks, rhetorical questions as headings, "Let's", "In summary", "In conclusion".
- Filler and AI-isms: delve, crucial, vital, leverage, robust, seamless, seamlessly, journey, unlock, empower, game-changer,
  "dive into", "deep dive" (except quoting the slide), "it's worth noting", "it is important to note", "worth mentioning",
  "in today's", "plays a key role", "a testament to", "not only ... but also", "honest caveat", "the magic of".
- Em-dash asides in prose. Use a full stop or a comma. (En dashes in ranges like 5–8 are fine.)
- Scare quotes around invented labels; "not X, but Y" framing as a reflex.
- Inventing facts about the course (dates, rules, numbers) that are not in the sources.
- Contradicting the slides. If the slide simplifies, teach the slide's version.

## Lengths
- Section `body_md`: 150–450 words. Lead with the idea, then the course's example, then the consequence.
- `explanation_md`: 40–180 words. `why_md` per option: 1–3 sentences. `weak_answers_md`: 30–120 words.
- Model open answers: what a strong student writes by hand in the time available. Total of all parts 5–8 handwritten lines
  (about 60–120 words). Not an essay.

## Formatting
- One idea per paragraph. Bullets for lists of parallel items only. Tables when comparing (Waterfall vs Agile, argument vs option).
- Every command, file, flag, identifier in backticks.
- Fenced blocks for any code/output with the right language tag (see SCHEMA.md).
