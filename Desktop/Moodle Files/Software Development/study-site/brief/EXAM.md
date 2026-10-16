# The mid-term: facts, limits and how we calibrate

Course: Software Development for Business (ESADE, BBA + BAIB, Autumn 2026). Lecturer: Alberto Cámara.
Student: one BAIB student preparing alone. Today is Wed 14 Oct 2026.

## Facts (from the teacher, verbatim where quoted)
- **Thursday 22 October 2026, 14:00, room 108, 1 hour, 30% of the course mark.** It "removes nothing from the final".
- Covers **sessions 1–10**: "starting a project, clean code and tests, the terminal".
- Pen and paper. Closed book, no devices.
- "Mixture of multiple-choice questions (no penalty for wrong) and open questions with short answers". The sample document adds: open questions are "answered in 5–8 lines".
- "You will be expected to explain, compare, or read a piece of code or tool output and say what it does or what is wrong. **You will not write code. Judgement, not memorised flags.**"
- "Prepare with the session slides and the **expense-tracker history on GitHub**."
- "You read code, tool output or a diff, and say what it does or what is wrong." "Judge your reasons, not the letter."
- The sample questions "show the kind of question, not the exam, and the exam does not reuse them. The topics are not a full list of what is covered."
- The syllabus (older text) says exams are "multiple-choice, code-reading, and short on-paper coding and refactoring tasks"; the newer mid-term statements override it: no code writing. Refactoring is asked as "describe in words how you would change it" (sample Q7.3).

## Scope map (session → content)
| Session | Date | Content | Sources |
|---|---|---|---|
| 1 | 8 Sep | What SE is; six ways working code fails; methodology/tool per problem; SDLC seven phases; bugs/features/refactor/tech debt; modules ↔ phases; card sort | slides-session-1 |
| 2 | 15 Sep | Waterfall (5 phases, outputs, document gates, where it works, why it fails for software); Agile (2001, iterative, manifesto 4 values, 12 principles in 4 groups); Scrum/Kanban/XP/Lean; what the course uses; plan/re-plan workshop | slides-session-2, moodle/project-pages.md |
| 3 | 18 Sep | Setup lab: why standardise ("works on my machine"), the CI referee (ruff + mypy + pytest), six tools (WSL2, VS Code, uv, git, GitHub, Docker), what a virtual environment is, terminal + git survival kits, push → Actions | slides-session-3, labs/00-setup.md |
| 4 | 22 Sep | Scrum: roles, self-managing, artifacts + commitments, backlog, Definition of Done, ceremonies + time-boxes, what they are not, pillars/values, what Scrum does not give; course mapping. Anatomy: script vs project, pyproject.toml line by line, src/ layout, uv run, uv.lock / `uv sync --locked`, commit a953d05; backlog brief | slides-session-4, moodle/project-pages.md |
| 5 | 25 Sep | Practice 1: program vs script, `[project.scripts]` resolution, `__main__.py`, typer (type hints are the spec), argument vs option, exit codes, argparse, the three that bite, CP1 | slides-session-5, labs/01-scaffold.md |
| 6 | 29 Sep | Clean code: economics, comments are for why, naming table, magic numbers, one function one job (SRP), guard clauses, computation is not output, tuple → `@dataclass(frozen=True)`, type hints as contracts, ruff check/format, refactor exercise; the five commits to v0.2 | slides-session-6, history |
| 7 | 6 Oct | Refactoring moves; decompose conditional; mypy vs linter; reading an error; `--strict` and the three kinds of error; strict in pyproject; functional core / imperative shell; failing well (raise vs return None, bare except, fail loudly at the boundary, stderr + exit code); logging vs print; lab 07 (invoice refactor + mypy troubleshooting table) | slides-session-7, labs/07-refactor.md |
| 8 | 9 Oct | Practice 2: red/green/refactor, Arrange-Act-Assert, reading pytest output, `pytest.approx`, fixtures, parametrize, edge cases on purpose, live TDD of remove_duplicates, `dict.fromkeys` + frozen ⇒ hashable, the parts that touch the world (2x2 diagram), tmp_path, CliRunner, monkeypatch, which tool for CP2, coverage is a map, hypothesis pointer, three that bite, CP2 | slides-session-8, labs/08-tdd.md, slides/image-only-slides.md |
| 9 | 13 Oct | Terminal vs shell vs OS; why the terminal survived; one tree under /; pwd/ls/-a/-l; . and ..; absolute vs relative; reading a path in an error; Tab/↑/Ctrl-R/Ctrl-C/cd -/cd; mkdir/touch/cp/cp -r/mv/rm; rm danger; permissions rwx; "permission denied" and chmod +x; WSL /mnt/c; 644/755/600/777; man etc. ("not examined as recall") | slides-session-9, labs/09-terminal.md |
| 10 | 16 Oct (Fri, taught; slides-session-10.txt and labs 10-wrangling.md, 10-bash.md, 10-kpi-analyzer.md, 10-check.sh in sources/) | Originally announced as: "pipes, text wrangling and bash scripts. Same terminal, same project." Labs `10-wrangling.md` (in class) and `10-bash.md`. "We write v0.5's scripts/check.sh together on Friday." Sample Q6 already uses `grep "food" expenses.csv \| wc -l`. **Predicted content**: stdin/stdout/stderr, pipes, redirection (`>`, `>>`, `2>`, `<`), grep/wc/sort/uniq/cut/head/tail/find, exit codes and `$?`, `&&` / `\|\|`, a bash script with a shebang, variables and quoting, `set -e` (-u, pipefail), and scripts/check.sh chaining ruff + mypy + pytest | slides-session-9 take-aways, labs/README.md, moodle/session6-midterm-slide.md |

The group project pages (brief, backlog brief, partial rubric) are course context; the exam can lean on them (Definition of Done, "the referee, not the judge", public repo / no secrets, CI green at the tag).

Out of scope for the mid-term: M4 Git in depth (branching, merging, conflicts, PRs, review — sessions 11–14) and M5 Docker (sessions 15–18). The git *survival kit* (clone, switch -c, status, add, commit, push, tag) and reading commits/diffs/commit messages ARE in scope because sessions 3–8 used them and the teacher says to study the expense-tracker history.

## What a question looks like (teacher style)
Multiple choice (4 options a–d, one correct, no penalty):
- A realistic scenario + an artefact (terminal transcript, tool output, code, diff, failing test line) + a judgement question: "What should you do next?", "What can you conclude?", "Which fix is most appropriate?", "Which of these is a refactoring?", "Which clean-code problem does this describe best?", "What does this command print?".
- Distractors are the moves a real but careless student would make: delete .venv, reinstall the tool, `# type: ignore`, change the type to Any, rerun a failing test until it passes, trust whichever changed last.
Open (5–8 lines in total, usually 2–4 numbered parts):
- "Read code and say what is wrong" (what it does in one sentence → two problems a teammate would face → describe in words how you would change it and which problem each change solves).
- "Compare" (a diff + two commit messages → what does the change do → which message is better for someone reading history six months later → one test you would add, in words).
- "Read tool output" (sort errors into the kinds from session 7 → which one is a real crash for a user and why → do you accept `# type: ignore` to get CI green?).

## Calibration: "assume the worst, within his limits, then a small step beyond"
His limits (never break these):
- No question asks the student to write code. Open answers are prose. ("Describe in words".)
- No flag trivia ("Judgement, not memorised flags"; session 9 says man/whoami/df/top/nano are "not examined as recall"). A flag may appear inside an artefact; the question is about meaning or judgement, never "what does -x stand for".
- No syntax-trick questions (missing colon, typo hunting). The bug is always about the course's ideas.
- Everything must be answerable from sessions 1–10 material plus reasoning.

Levels (field `level`):
- `core` — the idea itself, stated plainly (20–30% of a module).
- `exam` — sample-paper difficulty and shape (35–45%).
- `hard` — worst case within limits: longer or noisier artefacts (several errors, a realistic pytest failure block, a 15-line function with three problems), two plausible options where only careful reading separates them, combining two sessions (e.g. exit codes + CI; dataclass frozen + dict.fromkeys) (20–30%).
- `beyond` — a small step past the slides, still in the course's spirit: the obvious next consequence of an idea taught (e.g. `set -e` in check.sh, why `uv sync --locked` fails after editing pyproject without `uv lock`, what a passing test with no assert proves, what happens to coverage when tests have weak asserts), or the next consequence of session 10's pipes and scripts (5–15%).

## Verification standard ("no mistakes")
- Every tool output shown to the student (mypy, ruff, pytest, uv, python, shell) is produced by **actually running the tool** in the sandbox (see VERIFY.md), then trimmed. Never invent an error message format.
- Every claim in an explanation is backed by the slides/labs/history or by a run. If the course's slides simplify something, follow the slides and do not contradict them; if a slide is technically imprecise, keep the slide's framing in the answer and add a one-line precise note only when it matters.
- Every MCQ has exactly one defensible answer. If a careful expert could argue for a second option, rewrite it.
- Shell outputs are shown as they would appear on the course's Linux/WSL Ubuntu (GNU) machines. You run them on macOS (BSD tools) — see VERIFY.md for the known differences.
