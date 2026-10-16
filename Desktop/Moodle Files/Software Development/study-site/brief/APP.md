# App architecture and features

## Repository layout (study-site/)
```
brief/            the briefs (read-only for builders)
content/          <module>.json written by content authors; papers.json (mock papers); _fixture.json (builder test data)
content/src/      the Python scripts that generate each module JSON
sources/          slide text, labs, Moodle pages, history patch (read-only)
app/
  shell.html      the page body markup (no <html>/<head>/<body>)
  styles.css      design tokens + all styles
  js/             plain browser JS, no framework, no bundler; files are concatenated in the order of app/js/ORDER
tools/
  validate.py     content validator (exists; do not weaken it)
  build.py        content → data → single-file pages in dist/
tests/            node --test unit tests for pure JS logic (*.test.mjs) and build tests
dist/
  index.html      standalone page (full <!doctype html> document) — opens from Finder with a double-click
  artifact.html   the same page in the Artifact publish shape: starts with <title> then <style>, no doctype/html/head/body tags
README.md         how to build, validate, test, and update after session 10
```

## Build (tools/build.py, run with `uv run python tools/build.py`)
1. Load every `content/*.json` not starting with `_` (or only `_fixture.json` with `--fixture`), plus `content/papers.json` if present. Run the validator's `validate_module` on each module and refuse to build on errors.
2. Convert Markdown → HTML with markdown-it-py (CommonMark + tables), with fenced code highlighted by Pygments at build
   time (class-based spans, short class names; map `console` → a console/bash lexer that dims the `$ ` prompt, `text` → no
   highlighting, `diff` → diff lexer). Every key ending in `_md` becomes the same key ending in `_html`; `key_points` and
   `traps` become lists of HTML strings. Escape correctly; never trust raw HTML from content (markdown-it `html: false`).
3. For the `history` module, attach for each commit: date, author-free message body, `--stat` summary and the diff (excluding
   `uv.lock` and `expenses.csv`, and collapsing any file diff over ~150 lines with a note), rendered as highlighted HTML.
   Source: `git -C ../_repos/expense-tracker show <hash>`. The page never needs git at runtime.
4. Emit one JSON blob `{meta, modules, papers, plan, glossary}` into `<script type="application/json" id="study-data">`.
   `meta.exam = {"date": "2026-10-22T14:00:00+02:00", "minutes": 60, "room": "108", "weight": "30%", "sessions": "1–10"}`.
5. Concatenate `app/styles.css`, `app/shell.html` and `app/js/*` (ORDER file) into `dist/artifact.html` and wrap a copy as
   `dist/index.html`. Inline everything except the Google Fonts `<link>`. No external scripts. Report sizes.
6. Fail loudly (non-zero exit, clear message) on any problem. Ruff-clean and `mypy --strict`-clean Python.

## Runtime (vanilla JS, one global namespace `SD`)
- Router: hash-based, tokens separated by `.` only (the Artifact viewer only passes `#[A-Za-z0-9._~-]+`), e.g.
  `#home`, `#learn.testing-tdd`, `#learn.testing-tdd.s3`, `#practice`, `#q.testing-tdd-q07`, `#exam`, `#exam.paper-b`,
  `#history.04d699f`, `#labs.pipes`, `#cards`, `#glossary`, `#plan`. Back/forward work. Wrap `location.hash` writes in try/catch
  and keep the route in memory too.
- Store: one state object `{v:1, q:{[id]:{a:attempts,c:correct,last:ts,ok:bool,conf:'sure'|'unsure'|'guess'|null}},
  fc:{[id]:{box:1..5,due:ts}}, sec:{[id]:ts}, exams:[...], drafts:{...}, plan:{[day]:[done ids]}, prefs:{theme,timerHidden}}`.
  Persist to localStorage (key `swdev-midterm-v1`, every access in try/catch; the page works with storage blocked).
  Optional cloud sync when running as a claude.ai Artifact: `const db = await window.claude?.use?.("db")` and
  `const user = await window.claude?.use?.("user")` — both may be `null` or never resolve; never block first paint;
  use `db.collection("data/users/" + await user.id()).doc("progress")`, merge by per-item `last` timestamp, debounce writes
  (≥ 4 s, only on change). Read `/private/tmp/claude-501/bundled-skills/2.1.295/cf5eaae0465fdcbaeb152b77c5940dfa/artifact-capabilities/0.2.78/{claude,db,user}.d.ts`
  for the exact API before writing this. If anything fails, stay on localStorage silently (one small "Progress saved on
  this device" / "Progress synced" status in the footer).
- Section status (CI-check metaphor): ✓ passing when the last attempts on its questions are ≥ 80% correct and ≥ 3 answered;
  ✗ failing when < 60% with ≥ 2 answered; ○ otherwise. Module status aggregates its sections.

## Views
1. **Home** (`#home`): countdown to Thu 22 Oct 14:00 in mono (`7 d 18 h`), the exam in one line (1 h · pen and paper ·
   multiple choice with no penalty + 5–8 line answers · sessions 1–10 · no code writing), "Continue" (last place), the
   module check list (M1/M2/M3 + history + sample paper) with status, "Weak spots" count (questions answered wrong or
   guessed, due for review), last exam result in pytest-summary form, and today's block from the study plan.
2. **Plan** (`#plan`): the eight-day plan (Wed 14 → Thu 22 Oct morning) with checkable items linking to modules, papers and
   drills. Session 10 is Fri 16 Oct: the plan says to re-check the predicted module after class. Sunday 18 is the project's
   partial-submission deadline, so that day is light.
3. **Learn** (`#learn.<module>[.sN]`): module page = summary, "how it is examined" box, section list with status. Section
   page = body, key points, exam note in the margin (inline under the text below 1200px), then the section's quick-check
   questions inline, then prev/next section. Module end: traps list, glossary terms, "Practise this module".
   Predicted modules carry a visible `predicted` chip and a one-line note: written before the session-10 slides.
4. **Practice** (`#practice`): pick scope (all / module / section), type (mcq / open / sort), level (core → beyond), and a
   mode: "Next 10", "Weak spots" (wrong, or right but guessed, oldest first), "Not tried yet", "Teacher's sample + variants".
   One question at a time; progress bar like `7/10`; after each: full feedback; "Revise: <section heading>" link.
   Optional confidence buttons before checking an MCQ (Sure / Unsure / Guess): a correct guess still counts as a weak spot.
5. **Question components** (shared by Learn, Practice, Exam review):
   - mcq: as DESIGN.md. Options are shuffled in Practice (stable per attempt) but never in Exam papers. After checking:
     verdict line, every option's why, the explanation, "Revise" link.
   - open: stem + parts with lined textareas (drafts autosaved), "Show model answer" → per part: model answer, rubric
     checklist the student ticks (score = min(marks, ticked)), and `weak_answers` shown when they score below full marks.
     "Mark my answer with Claude" button only when `await window.claude?.use?.("sample")` resolves non-null: sends the
     question, parts, model answers, rubric and the student's text; asks for strict JSON
     `{parts:[{label, met:[rubric indexes], marks, feedback}], summary}` via `sample.json(...)`; shows it next to the self-mark;
     handles `not_granted` (hide), `rate_limited` (say so), other errors (one line). Read `sample.d.ts` first. Never call on load.
   - sort: items listed; each item has category buttons (tap to assign; keyboard 1–5); "Check" marks each item and shows its why.
6. **Exam** (`#exam`): choose a paper: the mock papers from `papers.json` (each shows its kind: realistic / worst case /
   beyond, number of questions, 60 min), the teacher's sample paper (9 questions, 30 min suggested), and "Build a paper from
   the bank" (stratified across modules: 12 mcq + 3 open, prefer not-yet-seen and weak questions). Rules screen mirroring the
   real paper. During the paper: sticky bar with time left (count-down, can be hidden; warnings at 10 and 5 min, shown inline
   in the bar, not modal), question navigator (answered / flagged / blank), flag for review, all answers autosaved so a reload
   resumes. No feedback until submission. At 0:00 the paper is submitted automatically (record if time ran out).
   Results: pytest-style summary line, mcq auto-marked, open questions marked by the student against the rubric (and
   optionally Claude), score as marks and %, per-module breakdown table, time used; review list of every question with the
   student's answer, the correct answer, all whys and the explanation, plus "Revise" links; wrong ones also become weak spots.
   Exam attempts are kept (history list with date, paper, score).
7. **Flashcards** (`#cards`): Leitner boxes 1–5 (the flashcard-trainer idea from the project menu): due cards first, flip,
   "Again" (box 1) / "Good" (+1) / "Easy" (+2); filter by module; keyboard F / 1 / 2 / 3.
8. **History** (`#history[.<hash>]`): the expense-tracker's 20 commits as a vertical timeline grouped by tag (v0.0 → v0.4),
   each with kind chip (feature / refactor / test / build / docs / fix / ci), message, summary. Commit page: message, why it
   matters, which session idea, message review, `--stat`, the diff (collapsible files). "Guess the message" mode: diff shown,
   message hidden; the student writes or picks a message, then sees the real one and the review.
9. **Terminal lab** (`#labs[.pipes|.perms|.paths|.chains]`):
   - Pipeline stepper (data from the `pipes-bash` module's `pipelines` and `sample_files`): run a pipeline stage by stage,
     showing each intermediate output; "predict the next output" before revealing.
   - Permissions: toggle r/w/x for owner/group/others ↔ octal ↔ `ls -l` string (`-rwxr-xr-x`); drill mode with random
     targets; explains 644/755/600/777 as the slides do.
   - Paths: a fixed tree (the expense-tracker under `/home/alice/code`), a current directory, a `cd` command (relative,
     absolute, `..`, `~`, `-`, no argument); student predicts `pwd`; drill mode. Exact POSIX semantics for the cases used.
   - Exit codes and `&&` / `||` / `;`: a chain like `uv run ruff check . && uv run mypy src tests && uv run pytest` with given
     per-command exit statuses; student predicts which commands run and the final `$?`; plus the `set -e` variant. Exact bash
     semantics for these operators (left-associative, equal precedence for && and ||).
10. **Glossary** (`#glossary`): all terms A–Z with module and link; filter box.
11. **Search**: a small search box in the header (titles, terms, question stems) — optional if time allows.

## Quality bar
- `node --test tests/` passes: unit tests for every pure function (scoring, section status, Leitner scheduling,
  paper building, shuffling stability, path resolution, permission conversion, chain evaluation, line estimate).
- No console errors. Works in current Chrome and Safari. Works with localStorage blocked and with `window.claude` absent.
- Checked with real screenshots at 1280×800 and 390×844, light and dark (headless Chrome:
  `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --screenshot=... --window-size=...`, and for
  scripted flows puppeteer-core installed in `$SCRATCH/e2e` driving that same Chrome). Look at every screenshot you take.
- Accessible: semantic landmarks, headings in order, labels on every control, focus visible, live region for timer warnings
  and answer verdicts, colour never the only signal (✓/✗ text too).
