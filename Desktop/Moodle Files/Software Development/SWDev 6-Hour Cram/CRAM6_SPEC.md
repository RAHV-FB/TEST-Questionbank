# SWDev 6-Hour Cram — spec

The mid-term is **Thu 22 Oct 2026, 14:00**: 1 hour, pen and paper, multiple choice (no penalty) + short open
answers of 5–8 lines, no code writing, sessions 1–10. The teacher has now published **official answers** to his
nine sample questions. The student wants a **6-hour maximum** cram built around those samples: what each question
asks, what type of question it is, and what level of answer earns full marks. Not worst-case depth: there is no
time for it and no use for it. The samples will not be on the paper and their topics are not the only ones, but they
show the question types and the expected level.

## Sources (quote paths; they contain spaces)
- THE KEY SOURCE: `/Users/russell/Desktop/Moodle Files/Software Development/study-site/sources/moodle/midterm-sample-answers.md` (his official answers + marking guide, verbatim) and `.../sources/moodle/midterm-sample-questions.md` (the nine questions).
- Bank of verified questions: `/Users/russell/Desktop/Moodle Files/Software Development/study-site/content/<module>.json` (schema: `study-site/brief/SCHEMA.md`). Papers: `study-site/content/papers.json`.
- Slides: `study-site/sources/slides/`; labs: `study-site/sources/labs/`. Style: `study-site/brief/STYLE.md` (British spelling, short plain sentences, no AI-isms, no em-dash asides).
- The engine (copied from the 12-Hour Cram): `/Users/russell/Desktop/Moodle Files/Software Development/SWDev 6-Hour Cram/` (`build_cram.py`, `validate_types.py`, `app/`, `route.json`, `exam_intro.json`, `tests/`, `README.md`). The 12-hour cram's spec, for the engine's existing type fields: `.../SWDev 12-Hour Cram/CRAM_SPEC.md`.

## What his answers tell us (apply everywhere)
- **Marking:** full marks = the right idea **with a reason (the "because")**; partial = idea without reason or half-right reason; zero = terms listed without connecting them to the code or output.
- **Length:** one or two sentences per part. Always tied to the artefact shown (name the line, the column, the error).
- **MCQ:** the wrong options are careless moves (delete `.venv`, reinstall, `--upgrade`, `# type: ignore`, `Any`, rerun a flaky test, trust whichever changed last). His "why" is two or three sentences.
- **Q9 kinds:** missing annotation ("what type is this?"), None not handled ("this can be missing"), **Any leaks in ("I gave up on this value")** for `Returning Any … [no-any-return]`, plus "types disagree" from slide 10. Never file `Returning Any` under "types disagree".

## Stops (type files `types/<tid>.json`, each written by a generator `types/src/<tid>.py`)
| tid | stop | minutes |
|---|---|---|
| S1 | Q1 Tool error: what do you do next? | 15 |
| S2 | Q2 Is it a refactoring? | 15 |
| S3 | Q3 A mypy error: which fix? | 15 |
| S4 | Q4 A test fails: what can you conclude? | 15 |
| S5 | Q5 Name the clean-code problem | 15 |
| S6 | Q6 What does this command print? | 15 |
| S7 | Q7 Read code and say what is wrong (open) | 25 |
| S8 | Q8 Compare a diff and two commit messages (open) | 25 |
| S9 | Q9 Read tool output (open, harder) | 25 |
| P1 | Same shapes, other topics: lifecycle, Agile, Scrum, backlog, Definition of Done | 20 |
| P2 | Same shapes, other topics: the terminal, paths, permissions, pipes, scripts, exit codes | 20 |
| P3 | Same shapes, other topics: the CLI (typer arguments/options, exit codes), functional core / imperative shell, failing well | 20 |
| P4 | Same shapes, other topics: tests (TDD, fixtures, parametrize, approx, tmp_path / CliRunner / monkeypatch, edge cases) and project setup (uv, uv.lock, src layout, CI as referee) | 20 |

Route (`route.json`, ≤ 6 h): How he marks (10) → S1–S6 (15 each) → S7–S9 (25 each) → break (10) → P1–P4 (20 each) → Paper A (60) → mark and review Paper A with his marking guide (25) → the answer formula, final check (5). Total ≈ 5 h 55.

### Type file shape (engine fields kept, two new ones, everything shorter than the 12-hour cram)
```jsonc
{
  "tid": "S3", "name": "A mypy error: which fix?", "minutes": 15,
  "shape_md": "Which sample question this is and how the shape appears on the paper (1–2 sentences).",
  "one_md": "The one idea he tests, in one sentence.",
  "sample": {                                  // NEW, S1–S9 only; rendered FIRST on the page
    "qnum": "Q3", "kind": "mcq",               // "mcq" | "open"
    "question_md": "the question exactly as in midterm-sample-questions.md (code/output in fenced blocks)",
    "options": ["Add `# type: ignore` to the line", "..."],   // mcq only, a)–d) order
    "answer": 1,                               // mcq only: index of his answer
    "parts": ["In one sentence, what does this function do?", "..."],   // open only
    "his_answer_md": "his official answer, VERBATIM from midterm-sample-answers.md",
    "decoded_md": "What he is looking for: 3–6 bullets. The pattern, the level, why each wrong option is tempting, what earns the because."
  },
  "spot_md": "How to recognise this shape on the real paper, with other topics: 3–5 bullets.",
  "basics": [ { "id": "S3-b1", "heading": "...", "body_md": "ONLY the knowledge needed at his level, 80–200 words. 1–2 blocks max." } ],
  "checks": [],                                // optional, 0–3 quick checks (engine format)
  "method": ["3–5 steps: how to answer this shape like his official answer"],
  "worked": [],                                // optional 0–1: one SAME-SHAPE example on a different topic, answered at his length
  "twists": [ { "twist_md": "the same shape on another session's topic", "how_md": "how to answer, one or two sentences" } ],   // 3–5
  "traps": ["the tempting wrong move + the correction"],     // 3–4
  "say_md": "The answer formula and key phrases for this shape (bullets).",
  "practice": ["bank question ids, exam or core level only (no hard/beyond), 4–8 for S1–S6 and P1–P4 (mostly mcq), 2–3 open + 2 mcq for S7–S9; never an id used by another stop; never the sample-paper originals q01–q09 (they are the sample block)"],
  "short_answers": { "<open practice qid>": { "1": "a full-marks answer at HIS length: the idea + because, 1–2 sentences", "2": "..." } }   // NEW: required for every open practice id, one entry per part label
}
```
P1–P4 have no `sample`; they open with `spot_md` and teach only what his level needs.

## The page (engine changes)
- Title "SWDev 6-Hour Cram"; localStorage key `swdev-cram6-v1`; header countdown to Thu 22 Oct 14:00.
- **Home / How he marks** (exam_intro.json): the format; his marking guide verbatim; the answer formula ("idea + because + point at the code/output"); MCQ strategy (no penalty → answer all; eliminate the careless moves); a 60-minute time plan; then the route timeline.
- **Sample block** at the top of S1–S9: his question → "Try it first" (mcq: pick a)–d); open: a lined textarea per part) → "Show his answer" reveals `his_answer_md` (labelled "Teacher's official answer") → then `decoded_md`. Remember state per stop.
- **Practice feedback for open questions:** show `short_answers` first as "Full marks at his length", then the bank's longer model answer collapsed under "More detail", then the rubric self-mark. Also show his marking guide beside the self-mark.
- **Papers:** only the teacher's sample paper (with his official answers in the review) and Papers A and B from papers.json (realistic). Drop C and D.
- Everything else as the 12-hour cram engine already does (practice runner, mistakes, tutor via `sample` capability, keyboard, 360 px, light/dark, no console errors). `validate_types.py`: drop the pools.json rule; instead check that every practice id exists in the bank, is level core or exam, is not a sample-paper original, and is used by one stop only; check `sample` (S1–S9) and `short_answers` (every open practice id × every part label).
