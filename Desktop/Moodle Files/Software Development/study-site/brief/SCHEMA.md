# Content schema (one JSON file per module: `content/<id>.json`)

Write each module with a **Python script** (keep it at `study-site/content/src/<id>.py`) that builds a dict and writes it with
`json.dump(module, f, ensure_ascii=False, indent=1)`. Never hand-type the JSON. Then run the validator:

```
cd "/Users/russell/Desktop/Moodle Files/Software Development/study-site"
uv run python tools/validate.py content/<id>.json
```
It must print `RESULT: PASS` (warnings are allowed only when you can justify each one).

## Markdown conventions
- Every field ending in `_md`, and every string in `key_points` and `traps`, is Markdown (CommonMark + tables).
- Code, tool output, terminal sessions and diffs go in fenced blocks with a language tag:
  `python`, `toml`, `bash` (commands only), `console` (a terminal transcript with `$ ` prompts and output), `text` (plain tool output: mypy, ruff, pytest, uv errors), `diff`, `yaml`.
- Inline code with backticks for every identifier, command, file name and flag: `uv sync`, `pyproject.toml`, `--strict`.
- No HTML, no images, no emoji, no math. Tables are fine.

## Top-level object
```jsonc
{
  "id": "testing-tdd",                 // given in your task; also the file name
  "order": 8,                          // given
  "module": "M2",                      // "M1" | "M2" | "M3" | "X" (cross-cutting: history, sample paper)
  "title": "Testing and TDD",          // short, specific
  "sessions": [8],                     // session numbers covered
  "predicted": false,                  // true only for session 10 material written before its slides exist
  "sources": ["slides-session-8", "labs/08-tdd.md", "expense-tracker v0.3..v0.4"],
  "summary_md": "3–5 sentences: what this module teaches, in the course's own words, and why it matters.",
  "exam_focus_md": "How the teacher can examine this: the artefacts he will show and the judgements he will ask for. 4–8 bullet points.",
  "sections": [ /* Section */ ],
  "terms":     [ /* Term */ ],
  "traps":     [ "Markdown: a common wrong belief + the correction, one or two sentences" ],
  "flashcards":[ /* Flashcard */ ],
  "questions": [ /* Question: mcq | open | sort */ ]
}
```

### Section (5–10 per module; the lesson, in order)
```jsonc
{
  "id": "testing-tdd-s3",              // <module id>-s<n>
  "heading": "Fixtures and parametrize",
  "body_md": "Teach from zero, in the order the slides teach it. 150–450 words. Use the course's own example (expense-tracker, Expense, total_by_category, remove_duplicates...) and show the real code/output in fenced blocks.",
  "key_points": ["2–5 memorable one-liners"],
  "exam_note_md": "Optional. One or two sentences: how this tends to be examined or the judgement it tests.",
  "source_ref": "S8 slides 9–10",     // where it comes from: 'S8 slide 9', 'labs/08-tdd.md', 'expense-tracker 1e421bc'
  "check": ["testing-tdd-q04", "testing-tdd-q05"]   // 1–3 question ids (mcq or sort) shown inline after the section as a quick check
}
```

### Term (glossary; 8–25 per module)
```jsonc
{ "term": "Fixture", "definition_md": "A function pytest calls for you to build shared test data; a test asks for it by naming it as a parameter.", "section_ref": "testing-tdd-s3" }
```

### Flashcard (16–30 per module)
```jsonc
{ "id": "testing-tdd-f01", "front_md": "Why compare floats with `pytest.approx`?", "back_md": "`0.1 + 0.2 == 0.3` is `False`; money in floats needs a tolerance.", "kind": "concept", "section_ref": "testing-tdd-s2" }
```
`kind`: `concept` (why/what), `distinction` (X vs Y), `reading` (what does this output/code mean), `recall` (a fact that must be known: a time-box, an artifact's commitment, 755 = rwxr-xr-x). Recall cards must be facts the slides present as content, not flag trivia.

### Question: common fields
```jsonc
{
  "id": "testing-tdd-q07",             // <module id>-q<nn>, two digits
  "type": "mcq",                       // "mcq" | "open" | "sort"
  "level": "exam",                     // "core" | "exam" | "hard" | "beyond"  (see EXAM.md)
  "skills": ["read-tool-output"],      // 1–3 of: concept, read-code, read-tool-output, read-diff, compare, judgement, predict-output
  "stem_md": "Scenario + artefact + the question.",
  "explanation_md": "The full reasoning, 40–180 words: why the answer is right, in the course's terms.",
  "section_ref": "testing-tdd-s2",     // the lesson section that teaches it (link target for 'revise this')
  "source_ref": "S8 slide 8; lab 08 troubleshooting",
  "origin": "slides",                  // "teacher-sample" | "teacher-variant" | "slides" | "lab" | "history" | "predicted"
  "verified_by": "run"                 // "run" (you executed the code/tool and the shown output is real) | "source" (the fact is stated in the slides/labs) | "reasoning"
}
```
A question that shows any tool or program output must have `"verified_by": "run"`.

### mcq
```jsonc
{
  ...common,
  "type": "mcq",
  "options": [                          // exactly 4, in a–d order; exactly one has "correct": true
    { "text_md": "Open `pyproject.toml` at line 7 and look for the syntax mistake", "correct": true,
      "why_md": "Why it is right: the error names the file, the line and the column. Read the message, fix the cause." },
    { "text_md": "Delete `.venv` and run `uv sync` again", "correct": false,
      "why_md": "The misconception it represents and why it fails: the virtual environment is not the problem; uv never got as far as touching it, because it could not read the project file." },
    ...
  ]
}
```
Rules: options are parallel in form and similar in length (the right one must not be the longest by habit); no "all/none of the above", no "both a and b", no option that refers to another by letter; vary the position of the correct option across the module (each of a–d is correct roughly a quarter of the time). Every `why_md` is specific (it names the misconception), 1–3 sentences.

### open
```jsonc
{
  ...common,
  "type": "open",
  "stem_md": "The shared scenario and artefact (code / diff / output).",
  "parts": [
    {
      "label": "1",
      "prompt_md": "In one sentence, what does this function do?",
      "marks": 1,                       // 1–3
      "model_answer_md": "What a full-marks student writes, in 1–3 lines of plain prose (no code).",
      "rubric": ["Each point a marker looks for, one per item; the student scores 1 per point made, capped at marks"],
      "weak_answers_md": "The typical incomplete or confused answers and exactly what they miss (in-depth, this is shown when the student self-marks low)."
    }
  ],
  "lines": "5–8"                        // expected handwritten length of the whole answer
}
```
Rules: 2–4 parts; total marks 3–8; model answers are prose, never code (a single identifier or a command name in backticks is fine); rubric points are concrete and checkable ("names that `print` inside the function prevents asserting on the result", not "mentions testability").

### sort (classification; the card-sort idea, also sample Q9 part 1)
```jsonc
{
  ...common,
  "type": "sort",
  "stem_md": "Put each mypy error into the kind of problem it reports.",
  "categories": [ {"id": "missing", "label": "Missing annotation"}, {"id": "disagree", "label": "Types disagree"}, {"id": "none", "label": "None not handled"} ],
  "items": [ { "text_md": "`Function is missing a type annotation  [no-untyped-def]`", "category": "missing", "why_md": "mypy cannot see inside a function without a signature." } ]
}
```
Rules: 2–5 categories, 4–10 items, every category used at least once, each item's `why_md` 1–2 sentences.

## Module-specific extras
- `pipes-bash` adds `"sample_files": {"expenses.csv": "<file content>"}` and `"pipelines": [ { "id": "...", "title": "...", "goal_md": "...", "stages": [ {"cmd": "grep dining expenses.csv", "output": "<exact GNU output>", "explain_md": "..."} , {"cmd": "| cut -d, -f4", ...} ], "takeaway_md": "..." } ]` (6–12 pipelines; the stage outputs are real runs on the sample file).
- `history` adds `"commits": [ { "hash": "3e0834f", "tag": null, "message": "...", "kind": "feature|refactor|test|build|docs|fix|ci", "summary_md": "what changed and why, 2–5 sentences", "concepts_md": "which session idea it illustrates", "message_md": "is this a good commit message, and why (short)", "section_ref": "<id of a history section>" } ]` for **all 20 commits** in order (oldest first). Diffs are extracted from git at build time; do not paste them into the JSON.
- `sample-paper` has questions with `origin: "teacher-sample"` (the nine originals, same numbering in `id`: `sample-paper-q01`…`q09`) and `origin: "teacher-variant"` (2–3 variants per original, `variant_of: "sample-paper-q03"`), plus per-original `dissection_md` field on the original question: what it really tests, the trap, what a full-marks answer contains, and how it could be made harder within the teacher's limits.

## IDs and references
- Ids are unique across the whole site. `section_ref` always points to a section in the same module. (The `history` module's sections follow the tags: v0.0 the script, v0.1 packaged, v0.2 clean code, v0.3 core/shell + strict, v0.4 tested, plus one on reading diffs and writing commit messages. The `sample-paper` module's sections teach exam technique: how the paper works, answering multiple choice with no penalty, writing a 5–8 line open answer, reading tool output under time pressure, and one section per open-question shape.)
- `check` lists only questions of type mcq or sort from the same module.
