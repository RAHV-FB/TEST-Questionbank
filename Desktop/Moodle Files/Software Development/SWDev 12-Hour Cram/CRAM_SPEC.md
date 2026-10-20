# SWDev 12-Hour Cram — spec

The student has about 12 hours before the Software Development for Business mid-term (Thu 22 Oct 2026, 14:00,
1 hour, pen and paper, multiple choice with no penalty + short open answers of 5–8 lines, no code writing,
"judgement, not memorised flags", sessions 1–10). They want something **quick, exercise-led**: teach the basics
from zero, then practise with real exam-style questions so they know what they are up against.

This cram is a separate page. It does not change the main study site; it reads its verified content.

## Paths (quote them; they contain spaces)
- CRAM = `/Users/russell/Desktop/Moodle Files/Software Development/SWDev 12-Hour Cram`
- SITE = `/Users/russell/Desktop/Moodle Files/Software Development/study-site` (read-only for cram agents)
- Bank: `SITE/content/<module>.json` (12 modules, 609 verified questions; schema in `SITE/brief/SCHEMA.md`), mock papers `SITE/content/papers.json`.
- Exam facts and the teacher's limits: `SITE/brief/EXAM.md`. Writing style: `SITE/brief/STYLE.md` (British spelling, short direct sentences, no AI-isms, no em-dash asides, no emoji).
- Teacher's sample questions verbatim: `SITE/sources/moodle/midterm-sample-questions.md`. Slides text: `SITE/sources/slides/`. Labs: `SITE/sources/labs/`.
- Disjoint question pools per type: `CRAM/pools.json` (`pools[tid]` lists the candidate question ids with type, level, skills and a stem preview).

## The 12 exercise types
| tid | name | teacher's shape it mirrors | bank modules |
|---|---|---|---|
| T01 | Tool errors and project setup | sample Q1 (uv error → what next) | project-anatomy, sample Q1 + variants |
| T02 | Programs and the command line | typer argument/option, exit codes, entry points | cli-program |
| T03 | Clean-code problems | sample Q5 (name the problem), Q7 | clean-code, sample Q5 + variants |
| T04 | Refactoring or not | sample Q2 | refactor-types (refactoring part), sample Q2 + variants |
| T05 | mypy errors and the right fix | sample Q3, Q9 | refactor-types (typing part), sample Q3 + variants |
| T06 | Core, shell and failing well | Q7 open (what is wrong), structure | core-shell-failing |
| T07 | Failing tests, pytest and TDD | sample Q4 | testing-tdd, sample Q4 + variants |
| T08 | Paths, files and permissions | terminal transcripts | terminal-files |
| T09 | Pipes, text wrangling and bash scripts | sample Q6 | pipes-bash (incl. Lab 10), sample Q6 + variants |
| T10 | Process: lifecycle, Agile and Scrum | scenario judgement | sdlc-agile, scrum |
| T11 | Diffs and commit messages | sample Q8 | history |
| T12 | Writing the open answers | sample Q7, Q8, Q9 | sample-paper opens and exam-technique items |

## Type file: `CRAM/types/<tid>.json` (write it with a Python script `CRAM/types/src/<tid>.py`, json.dump ensure_ascii=False, indent=1)
```jsonc
{
  "tid": "T05",
  "name": "mypy errors and the right fix",
  "shape_md": "Which sample questions this mirrors and how it appears on the paper (1–2 sentences).",
  "minutes": 40,                         // suggested time for the whole block
  "one_md": "One sentence: the single idea this type tests.",
  "spot_md": "How to recognise it on the paper: 3–5 bullets (what the artefact looks like, the question wording).",
  "basics": [                            // 2–4 blocks: teach from ZERO, fast. Tables welcome.
    { "id": "T05-b1", "heading": "What mypy is and how to read one error", "body_md": "120–320 words, the course's own examples (expense-tracker, Expense, total_by_category...). Real tool output in fenced blocks copied from the bank or sources, never invented." }
  ],
  "checks": [                            // 3–5 quick 'check yourself' items placed after the basics; NEW but simple and certain
    { "id": "T05-c1", "q_md": "…", "options": ["…", "…", "…"], "answer": 1, "why_md": "one or two sentences" }
  ],
  "method": ["3–6 numbered steps: how to answer this type on the paper, in order (markdown)"],
  "worked": [                            // 1–2 worked examples, preferably the teacher's sample question for this shape
    { "title": "Sample Q3", "question_md": "verbatim stem + options/artefact", "steps_md": ["step by step reasoning"], "answer_md": "the answer and why" }
  ],
  "twists": [ { "twist_md": "a variation the teacher could set", "how_md": "how to handle it" } ],   // 4–8
  "traps": ["the mistake + the correction, 1–2 sentences"],                                        // 4–8
  "say_md": "Bullets: the exact phrases/vocabulary to write on the paper for this type (course terms).",
  "practice": ["bank question ids from pools[tid] ONLY, 10–14, ordered from core to hard; for open-heavy types include 2–4 open; T12 is mostly open"]
}
```
Rules for authors:
- Only ids from `pools[tid]`. Prefer `exam` and `hard` levels (≈20% core, 50% exam, 30% hard/beyond); skip near-duplicates; cover every sub-topic of the type. Read each chosen question in full from the bank first.
- Facts must match the slides/labs and the bank. Never invent tool output; copy real output from bank questions or sources.
- "Basics" is a fast, from-zero lesson for someone who half-followed the sessions: concrete, short paragraphs, tables, one idea at a time.
- Markdown conventions as in SITE/brief/SCHEMA.md (fenced blocks with a language tag: python, toml, bash, console, text, diff; backticks for code).
- Validate with `uv run --project "SITE" python "CRAM/validate_types.py" CRAM/types/<tid>.json` once that script exists (the builder writes it); otherwise check ids against pools.json yourself.

## The 12-hour route (`CRAM/route.json`, written by the builder)
Start: "The exam in 2 minutes" (5) → Baseline: the teacher's sample paper, 9 questions (30) → T10 (40) → T01 (40) → T02 (35) → break (10) → T03 (40) → T04 (35) → T05 (40) → T06 (35) → break (10) → T07 (45) → T11 (35) → T12 (40) → T08 (30) → T09 (45) → break (10) → Paper A, realistic (60) → review Paper A (20) → redo mistakes (15) → Paper C, worst case (60) → review Paper C (20) → final: the "say it on the paper" list (10). Total ≈ 12 h.

## The page (built by the builder)
Single self-contained HTML, two outputs: `CRAM/SWDev 12-Hour Cram (offline).html` (full document) and `CRAM/dist/artifact.html` (publish shape: starts with `<title>SWDev 12-Hour Cram</title>` then `<style>`, no doctype/html/head/body). Same design language as the main site (copy its tokens and component look from `SITE/app/styles.css`: IBM Plex, steel neutrals, git-orange accent, light + dark, no gradients/emoji/AI clichés). Views:
1. **Route (home):** "The exam in 2 minutes" box (format, scope, limits, the 9 sample shapes), then the route as a timeline: each stop with minutes, a running clock (start time you set, default now), done checkboxes, progress; "Continue" button.
2. **Type page:** one-liner → Spot it → Basics (blocks, each followed by its quick checks inline) → Method → Worked example(s) → Twists → Traps → "Write this on the paper" → **Practice** (one question at a time; mcq with a)–d) options; after answering show every option's why + the explanation; open questions: lined textareas, model answer + rubric self-mark + weak answers; sort questions: tap-to-assign) → summary with "redo wrong ones".
3. **Papers:** the teacher's sample paper (9 originals from the sample-paper module) and Papers A–D from papers.json: 60-min timer (30 for the sample), all questions on one page, no feedback until hand in, auto-marked mcq, rubric self-marking for open, full review with explanations.
4. **Mistakes:** every question answered wrong, to redo.
5. **Tutor (online only):** an "Ask Claude about this" button after a question is answered, via the Artifact `sample` capability (`await window.claude?.use?.("sample")`; hide when null; never on load). See `/private/tmp/claude-501/bundled-skills/2.1.295/cf5eaae0465fdcbaeb152b77c5940dfa/artifact-capabilities/0.2.78/sample.d.ts`.
Progress in localStorage (key `swdev-cram-v1`, every access in try/catch; works with storage blocked). Keyboard: a–d / 1–4 pick, Enter checks/next. Works at 360 px wide without horizontal scroll. No console errors. No external scripts; only Google Fonts.
