# SWDev 6-Hour Cram

A quick page for the Software Development for Business mid-term (Thu 22 Oct 2026, 14:00, 1 hour, pen and
paper, sessions 1 to 10). It is built around the teacher's nine sample questions and his official answers:
what each question asks, what type of question it is, and the level of answer that earns full marks. The
route is 5 h 55 in all. It reads the verified content of the main study site and never changes it.

`CRAM6_SPEC.md` is the design. This file says how to build, check and publish the page.

## What is in this folder

| Path | What it is |
|---|---|
| `types/S1.json` ... `S9.json`, `P1.json` ... `P4.json` | The thirteen stops (written by `types/src/<tid>.py`). S1 to S9 each start from one sample question; P1 to P4 are the same shapes on other topics. |
| `types/_example6.json`, `_example6_open.json` | Two small complete fixtures (S3 with a multiple-choice sample, S7 with an open sample and `short_answers`) for `--example` builds and the tests. They show the shape of a type file. |
| `route.json` | The route: 18 stops (`kind`, `ref`, `title`, `minutes`, `note`), 355 minutes. |
| `exam_intro.json` | "How he marks": the facts, his marking guide (checked word for word against his file), the answer formula, the multiple-choice strategy, the 60-minute plan and the nine sample shapes. |
| `official.py` | Reads his two Markdown files (`study-site/sources/moodle/midterm-sample-questions.md` and `midterm-sample-answers.md`). The validator and the build both use it, so his words are never retyped. |
| `validate_types.py` | Validates the type files against the spec. |
| `build_cram.py` | Builds the page. |
| `app/` | `cram.css`, `shell.html` and `js/` (listed in `js/ORDER`). No bundler, no framework. |
| `tests/` | `node --test` tests of the pure logic, and of the build. |
| `SWDev 6-Hour Cram (offline).html` | The built page as a full document. Open it in any browser. |
| `dist/artifact.html` | The built page in publish shape (see Publish). |

Every command below needs the study-site Python environment. Quote the paths: they contain spaces.

```bash
SITE="/Users/russell/Desktop/Moodle Files/Software Development/study-site"
cd "/Users/russell/Desktop/Moodle Files/Software Development/SWDev 6-Hour Cram"
```

## Validate the type files

```bash
uv run --project "$SITE" python validate_types.py                 # every S*.json and P*.json
uv run --project "$SITE" python validate_types.py types/S3.json   # one file
```

It checks:

- **Fields and counts.** 1 to 2 basics blocks (P stops up to 3) of 80 to 200 words, 0 to 3 quick checks,
  3 to 5 method steps, 0 to 1 worked example, 3 to 5 twists, 3 to 4 traps, 3 to 5 bullets in `spot_md`,
  `minutes` as in the spec (15, 25 or 20), and a `name` that is the stop's name.
- **`sample` (S1 to S9; P stops must not have one).** `qnum` is `Q<n>`, `kind` is `mcq` for S1 to S6 and
  `open` for S7 to S9, four options and an answer index, or three prompts, `his_answer_md` and 3 to 6 bullets
  in `decoded_md`. The question's code blocks and lines, the options, the answer letter, the prompts and his
  words must match `official.py`'s reading of his files. A changed word is an error.
- **Practice.** 4 to 8 ids for S1 to S6 and P1 to P4 (mostly multiple choice); 2 to 3 open and about 2
  multiple-choice ids for S7 to S9. Each id exists in the bank at level core or exam, is not one of the nine
  sample-paper originals, is used by one stop only (the other type files are read too; example files are
  only compared with each other) and does not file `Returning Any` under "types disagree" (his answer is
  "Any leaks in").
- **`short_answers`.** One entry for every part label of every open practice id, no extras, each 4 to 90
  words (a warning above 45): a full-marks answer at his length.
- **The main site's Markdown rules.** Fences tagged and balanced, banned phrases, British spelling, no
  emoji, no raw HTML.

It prints `RESULT: PASS` or `RESULT: FAIL` and exits 1 on a failure. A warning does not fail it.

## Build

```bash
uv run --project "$SITE" python build_cram.py             # needs S1..S9 and P1..P4
uv run --project "$SITE" python build_cram.py --example   # the types/_example*.json fixtures only
uv run --project "$SITE" python build_cram.py --partial   # the S*/P* files that exist
uv run --project "$SITE" python build_cram.py --out DIR   # write under DIR instead of here
uv run --project "$SITE" python build_cram.py --types DIR # read the type files from DIR
```

The build validates every type file, `route.json` and `exam_intro.json`, loads the bank questions the stops
practise (full objects from `study-site/content`, provenance included), his nine sample questions with his
official answers (from his own file, put on the sample paper's originals), Papers A and B from
`papers.json` (Papers C and D are left out), renders every `*_md` field to HTML with Pygments highlighting
(the main site's renderer), embeds one JSON data block and writes both pages. It stops with every problem
listed, and writes nothing, on a missing id, a validation error, a route stop that points nowhere, a route
over 360 minutes, a type missing from the route in a full build, a marking guide that is not his, or a
missing type file in a full build.

An `--example` or `--partial` build says so on the route page and in the footer, so it cannot be mistaken
for the real one. A warning is printed when a type file's `minutes` differs from `route.json`
(`route.json` wins).

## Test

```bash
node --test tests/
```

| File | Covers |
|---|---|
| `clock.test.mjs` | the route clock: schedule, progress, pace, next stop, projections; the real route is 355 minutes |
| `scoring.test.mjs` | multiple choice, rubric self-marking, sorting, the pytest-style summary |
| `mistakes.test.mjs` | attempt records, the mistakes queue, practice sessions |
| `paper.test.mjs` | a sitting: clock, warnings, marking, hand-in, recording a mark |
| `state.test.mjs` | repairing and merging saved state (sample blocks included), the store with storage blocked |
| `route.test.mjs` | hash routes use only `[A-Za-z0-9._~-]`, every stop has a link |
| `tutor.test.mjs` | the prompt for "Ask Claude about this" |
| `util.test.mjs` | clocks, labels, the seeded shuffle |
| `build.test.mjs` | the build and its failures (needs `uv`), the publish shape, the data block, his answers on the sample paper, `validate_types.py` rules, `route.json`, and a full build once all thirteen type files exist |

Lint the Python files with the study-site tools:

```bash
uv run --project "$SITE" ruff check build_cram.py validate_types.py official.py
uv run --project "$SITE" mypy build_cram.py validate_types.py official.py   # strict, see mypy.ini
```

## Publish

Publish `dist/artifact.html` as a claude.ai Artifact. It starts with `<title>SWDev 6-Hour Cram</title>`
then `<style>`, with no doctype, `html`, `head` or `body`. The only external files are the Google Fonts.

Declare the tutor when publishing: `capabilities: {sample: {}}`. The "Ask Claude about this" button
appears after a practice question is answered, only when `window.claude.use("sample")` resolves; it is
never asked for on load and nothing is sent before the click. Opened as the offline file, or without the
capability, the button is simply absent.

Progress lives in the browser under the localStorage key `swdev-cram6-v1` (every access is guarded;
with storage blocked the page works and the footer says progress is not being saved). It is per
browser: the artifact and the offline file do not share it.

## How the page works

- **Route** (`#home`): "How he marks", then the 18 stops as a timeline from the start time you set
  (default: when you first open it). Each stop has its minutes, a planned clock time, a done tick and a
  status. The pace line compares minutes of work done with minutes elapsed. The header counts down to the
  exam.
- **How he marks** (`#start`): the format, his limits, his marking guide word for word, the answer
  formula (idea, because, point at the code or output), the multiple-choice strategy, a 60-minute plan
  and his nine questions with the stop for each.
- **A stop** (`#type.S3`): S1 to S9 open with **his question**: "Try it first" (pick a to d, or write each
  part in a lined box), then "Show his answer", which reveals his official answer word for word and then
  what he is looking for. What you tried and whether his answer is shown are kept per stop. Then the one
  idea, how it appears, spot it, the basics with quick checks, the method, a worked example when there
  is one, twists, traps, what to write and the practice. P1 to P4 open with how to spot the shapes.
- **Practice** (`#type.S3.practice`): one question at a time, every option's reason after answering. Open
  questions have lined answer boxes. After "Show the full-marks answer" the page shows **Full marks at his
  length** (the stop's `short_answers`), the bank's longer model answer folded under **More detail**, the
  rubric to tick, and **His marking guide** beside your mark. Sort questions by tapping. A summary offers
  "redo the ones you missed".
- **Papers** (`#paper`, `#paper.paper-a`, `#sit.<id>`, `#review.paper-a`): the teacher's sample (30 min)
  and Papers A and B (60 min). All questions on one page, nothing marked until hand-in, a clock that keeps
  running if you leave the page, an automatic hand-in at 0:00 (also if the page was closed). Then the
  score, where marks were lost by stop, and a full review in which open answers are marked against the
  rubric. On the sample paper the review shows his official answers first.
- **Mistakes** (`#mistakes`): every question whose latest attempt was wrong, from practice and papers; a
  right answer takes it off. Redo all of them or one stop at a time.
- **The answer formula** (`#final`, the last stop): the formula, his marking guide, the strategy and the
  phrases to write, stop by stop.
- **Keyboard**: `a` to `d` or `1` to `4` choose (in his question, a quick check, practice and a paper),
  `Enter` checks then goes on, `1` to `5` place a sort item, `?` lists them.

Hash routes use only `[A-Za-z0-9._~-]` (the Artifact viewer passes nothing else). Light and dark follow
the system and can be switched in the footer. The layout was checked at 360 px with no sideways scroll.

## Changing a type

Edit `types/src/<tid>.py`, run it (`uv run --project "$SITE" python types/src/S5.py`), validate, build.
Take practice ids from the bank at core or exam level, copy tool output from the bank or the sources, never
invent it, and copy his question and his answer from `official.py`'s two source files (the validator
rejects any change to his words).
