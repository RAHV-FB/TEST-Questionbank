# SWDev 12-Hour Cram

A quick, exercise-led page for the Software Development for Business mid-term (Thu 22 Oct 2026, 14:00,
1 hour, sessions 1 to 10). It teaches each kind of question from zero, then practises it on real
exam-style questions, so the student knows what they are up against. It reads the verified content of
the main study site and never changes it.

`CRAM_SPEC.md` is the design. This file says how to build, check and publish the page.

## What is in this folder

| Path | What it is |
|---|---|
| `types/T01.json` ... `T12.json` | The twelve exercise types (written by `types/src/<tid>.py`). `_example.json` is one complete fake type for `--example` builds. |
| `pools.json`, `make_pools.py` | The disjoint question pool for each type, split from the study-site bank. |
| `route.json` | The 12-hour route: 23 stops (`kind`, `ref`, `title`, `minutes`, `note`), 710 minutes. |
| `exam_intro.json` | The text of "The exam in 2 minutes": facts, limits, technique and the nine sample shapes. |
| `validate_types.py` | Validates the type files against the spec. |
| `build_cram.py` | Builds the page. |
| `app/` | `cram.css`, `shell.html` and `js/` (listed in `js/ORDER`). No bundler, no framework. |
| `tests/` | `node --test` tests of the pure logic, and of the build. |
| `SWDev 12-Hour Cram (offline).html` | The built page as a full document. Open it in any browser. |
| `dist/artifact.html` | The built page in publish shape (see Publish). |

Every command below needs the study-site Python environment. Quote the paths: they contain spaces.

```bash
SITE="/Users/russell/Desktop/Moodle Files/Software Development/study-site"
cd "/Users/russell/Desktop/Moodle Files/Software Development/SWDev 12-Hour Cram"
```

## Validate the type files

```bash
uv run --project "$SITE" python validate_types.py                  # every types/T*.json
uv run --project "$SITE" python validate_types.py types/T05.json   # one file
```

It checks fields and counts (2 to 4 basics, 3 to 5 checks, 3 to 6 method steps, 1 to 2 worked examples,
4 to 8 twists and traps, 10 to 14 practice ids), that every check has a valid answer index, that every
practice id is in `pools.json` for that type, that no id is used by two types (the other type files
are read too), and the main site's Markdown rules: fences tagged and balanced, banned phrases, British
spelling, no emoji, no raw HTML. It prints `RESULT: PASS` or `RESULT: FAIL` and exits 1 on a failure.
A warning (for example a basics block outside 120 to 320 words, or a practice list that is mostly
core) does not fail it.

## Build

```bash
uv run --project "$SITE" python build_cram.py             # needs all of T01 ... T12
uv run --project "$SITE" python build_cram.py --example   # types/_example.json only (T07)
uv run --project "$SITE" python build_cram.py --partial   # the T*.json files that exist
uv run --project "$SITE" python build_cram.py --out DIR   # write under DIR instead of here
uv run --project "$SITE" python build_cram.py --types DIR # read the type files from DIR
```

The build validates every type file, `route.json` and `exam_intro.json`, loads the bank questions the
types practise (full objects from `study-site/content`, provenance included), the nine
`teacher-sample` questions of the sample-paper module and the four mock papers in `papers.json`, renders
every `*_md` field to HTML with Pygments highlighting (the main site's renderer), embeds one JSON data
block and writes both pages. It stops with every problem listed, and writes nothing, on a missing id,
a validation error, a route stop that points nowhere, or a missing type file in a full build.

An `--example` or `--partial` build says so on the route page and in the footer, so it cannot be mistaken
for the real one. A warning is printed when a type file's `minutes` differs from `route.json`
(`route.json` wins).

## Test

```bash
node --test tests/
```

| File | Covers |
|---|---|
| `clock.test.mjs` | the route clock: schedule, progress, pace, next stop, projections |
| `scoring.test.mjs` | multiple choice, rubric self-marking, sorting, the pytest-style summary |
| `mistakes.test.mjs` | attempt records, the mistakes queue, practice sessions |
| `paper.test.mjs` | a sitting: clock, warnings, marking, hand-in, recording a mark |
| `state.test.mjs` | repairing and merging saved state, the store with storage blocked |
| `route.test.mjs` | hash routes use only `[A-Za-z0-9._~-]`, every stop has a link |
| `tutor.test.mjs` | the prompt for "Ask Claude about this" |
| `util.test.mjs` | clocks, labels, the seeded shuffle |
| `build.test.mjs` | the build and its failures (needs `uv`), a full build of the twelve types, the publish shape, `validate_types.py` |

Lint the two Python files with the study-site tools:

```bash
uv run --project "$SITE" ruff check build_cram.py validate_types.py
uv run --project "$SITE" mypy build_cram.py validate_types.py      # strict, see mypy.ini
```

## Publish

Publish `dist/artifact.html` as a claude.ai Artifact. It starts with `<title>SWDev 12-Hour Cram</title>`
then `<style>`, with no doctype, `html`, `head` or `body`. The only external files are the Google Fonts.

Declare the tutor when publishing: `capabilities: {sample: {}}`. The "Ask Claude about this" button
appears after a question is answered, only when `window.claude.use("sample")` resolves; it is never
asked for on load and nothing is sent before the click. Opened as the offline file, or without the
capability, the button is simply absent.

Progress lives in the browser under the localStorage key `swdev-cram-v1` (every access is guarded;
with storage blocked the page works and the footer says progress is not being saved). It is per
browser: the artifact and the offline file do not share it.

## How the page works

- **Route** (`#home`): the exam in 2 minutes, then the 23 stops as a timeline from the start time you set
  (default: when you first open it). Each stop has its minutes, a planned clock time, a done tick and a
  status. The pace line compares minutes of work done with minutes elapsed.
- **Type page** (`#type.T07`): the one idea, how it appears, spot it, basics each followed by its quick
  checks, method, worked examples, twists, traps, what to write, then the practice
  (`#type.T07.practice`): one question at a time, every option's reason after answering, open questions
  with lined answer boxes, a model answer and rubric self-marking, sort questions by tapping, and a
  summary with "redo the ones you missed". Checks are spread over the basics blocks in order.
- **Papers** (`#paper`, `#paper.paper-a`, `#sit.<id>`, `#review.paper-a`): the teacher's sample (30 min)
  and Papers A to D (60 min). All questions on one page, nothing marked until hand-in, a clock that
  keeps running if you leave the page, an automatic hand-in at 0:00 (also if the page was closed). Then
  the score, where marks were lost by type, and a full review in which open answers are marked against
  the rubric.
- **Mistakes** (`#mistakes`): every question whose latest attempt was wrong, from practice and papers;
  a right answer takes it off. Redo all of them or one type at a time.
- **Keyboard**: `a` to `d` or `1` to `4` choose, `Enter` checks then goes on, `1` to `5` place a sort
  item, `?` lists them.

Hash routes use only `[A-Za-z0-9._~-]` (the Artifact viewer passes nothing else). Light and dark follow
the system and can be switched in the footer. The layout was checked at 360 px with no sideways scroll.

## Changing a type

Edit `types/src/<tid>.py`, run it (`uv run --project "$SITE" python types/src/T05.py`), validate, build.
Use only ids from `pools[tid]` in `pools.json`; copy tool output from the bank or the sources, never
invent it.
