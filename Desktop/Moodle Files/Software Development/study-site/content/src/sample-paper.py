"""Generate content/sample-paper.json: the teacher's sample paper, solved and extended.

Every tool output shown below was produced by a real run (uv 0.12, mypy 2.4.0, ruff 0.16.9,
pytest 9.1.1, Python 3.13) in the work folders scratchpad/work/sample-paper/ and
scratchpad/work/sample-paper-fix/ (review fixes); shell outputs are
shown in GNU format as on the course's Linux machines.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MID = "sample-paper"
OUT = Path(__file__).resolve().parent.parent / f"{MID}.json"


def qid(n: int) -> str:
    return f"{MID}-q{n:02d}"


def sid(n: int) -> str:
    return f"{MID}-s{n}"


def md(text: str) -> str:
    return text.strip("\n")


def opt(text: str, why: str, correct: bool = False) -> dict[str, Any]:
    return {"text_md": md(text), "correct": correct, "why_md": md(why)}


def mcq(
    n: int,
    level: str,
    skills: list[str],
    stem: str,
    options: list[dict[str, Any]],
    explanation: str,
    section: int,
    source: str,
    origin: str,
    verified: str,
    variant_of: int | None = None,
    dissection: str | None = None,
) -> dict[str, Any]:
    q: dict[str, Any] = {
        "id": qid(n),
        "type": "mcq",
        "level": level,
        "skills": skills,
        "stem_md": md(stem),
        "options": options,
        "explanation_md": md(explanation),
        "section_ref": sid(section),
        "source_ref": source,
        "origin": origin,
        "verified_by": verified,
    }
    if variant_of is not None:
        q["variant_of"] = qid(variant_of)
    if dissection is not None:
        q["dissection_md"] = md(dissection)
    return q


def part(
    label: str, prompt: str, marks: int, model: str, rubric: list[str], weak: str
) -> dict[str, Any]:
    return {
        "label": label,
        "prompt_md": md(prompt),
        "marks": marks,
        "model_answer_md": md(model),
        "rubric": [md(r) for r in rubric],
        "weak_answers_md": md(weak),
    }


def open_q(
    n: int,
    level: str,
    skills: list[str],
    stem: str,
    parts: list[dict[str, Any]],
    explanation: str,
    section: int,
    source: str,
    origin: str,
    verified: str,
    lines: str = "5–8",
    variant_of: int | None = None,
    dissection: str | None = None,
) -> dict[str, Any]:
    q: dict[str, Any] = {
        "id": qid(n),
        "type": "open",
        "level": level,
        "skills": skills,
        "stem_md": md(stem),
        "parts": parts,
        "lines": lines,
        "explanation_md": md(explanation),
        "section_ref": sid(section),
        "source_ref": source,
        "origin": origin,
        "verified_by": verified,
    }
    if variant_of is not None:
        q["variant_of"] = qid(variant_of)
    if dissection is not None:
        q["dissection_md"] = md(dissection)
    return q


def sort_q(
    n: int,
    level: str,
    skills: list[str],
    stem: str,
    categories: list[tuple[str, str]],
    items: list[tuple[str, str, str]],
    explanation: str,
    section: int,
    source: str,
    origin: str,
    verified: str,
    variant_of: int | None = None,
) -> dict[str, Any]:
    q: dict[str, Any] = {
        "id": qid(n),
        "type": "sort",
        "level": level,
        "skills": skills,
        "stem_md": md(stem),
        "categories": [{"id": c, "label": label} for c, label in categories],
        "items": [{"text_md": md(t), "category": c, "why_md": md(w)} for t, c, w in items],
        "explanation_md": md(explanation),
        "section_ref": sid(section),
        "source_ref": source,
        "origin": origin,
        "verified_by": verified,
    }
    if variant_of is not None:
        q["variant_of"] = qid(variant_of)
    return q


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------

sections: list[dict[str, Any]] = [
    {
        "id": sid(1),
        "heading": "How the paper works",
        "body_md": md("""
The mid-term is on **Thursday 22 October 2026 at 14:00 in room 108**. It lasts one hour, it is worth 30% of your course mark and it removes nothing from the final. It covers sessions 1–10: starting a project, clean code and tests, and the terminal. Pen and paper, closed book, no devices.

It has two kinds of question. **Multiple choice** has four options and no penalty for a wrong answer. **Open questions** are answered in 5–8 lines; in the sample, each is split into three numbered parts. You will not write code. The teacher's own description is the best summary: you explain, compare, or read a piece of code or tool output and say what it does or what is wrong. "Judgement, not memorised flags."

Every sample question follows the same pattern: a realistic scenario, an artefact, and a judgement.

| Q | Artefact | The judgement |
|---|---|---|
| 1 | a `uv sync` error | what to do next |
| 2 | four described changes | which one is a refactoring |
| 3 | code and a mypy error | which fix is right |
| 4 | a `FAILED` pytest line | what you can conclude |
| 5 | a described function | which clean-code problem |
| 6 | a shell pipeline | what it prints |
| 7 | a seven-line function | what it does, what is wrong, how to change it |
| 8 | a diff and two commit messages | what changed, which message, which test |
| 9 | a mypy log | sort the errors, find the crash, judge `# type: ignore` |

Two limits come from his statements, and the sample shows a third. No question asks you to write code: refactoring is asked as "Describe (in words, do not write code) how you would change it". No question asks what a flag stands for; a flag can appear inside an artefact, and the question is about what the command means. And the sample has no syntax tricks: every bug is one of the course's ideas.

The exam does not reuse these nine questions, and their topics are not a full list. What comes back is the **shape**: an artefact you have met in class (the expense-tracker, its history, the tools' output) and a decision a teammate would have to make. The slides and the expense-tracker history are what the teacher tells you to prepare with.
"""),
        "key_points": [
            "One hour, sessions 1–10, pen and paper, 30%: multiple choice with no penalty plus open answers of 5–8 lines.",
            "You never write code. You read code, tool output or a diff and judge it.",
            "Flags can appear in an artefact; the question is always about meaning.",
            "The questions change; the shape (scenario, artefact, judgement) does not.",
        ],
        "exam_note_md": "Session 8's last slide says how to use the sample: answer on paper first, then open the answers, and judge your reasons, not the letter.",
        "source_ref": "S6 slide 4; S8 slide 31; moodle/midterm-sample-questions.md",
        "check": [qid(36)],
    },
    {
        "id": sid(2),
        "heading": "Multiple choice with no penalty",
        "body_md": md("""
With no penalty, a blank and a wrong answer both score zero, and a guess sometimes scores. **Never leave a multiple-choice question blank.** If time runs out, put a letter on every remaining one.

Answer in this order:

1. **Read the artefact before the options.** Decide what it says: which tool, which file and line, what the message means, which value came out. Only then read a–d, looking for the option that acts on what you found.
2. **Eliminate the careless moves.** The teacher builds the distractors from moves a real but rushed student makes. Most of them change something the artefact never mentions.
3. **Choose between the two that remain** by asking which one fixes the cause rather than the symptom.

| Careless move | Why it fails |
|---|---|
| Delete `.venv`, reinstall uv, `--upgrade` | the error named a file and a line; the environment was never the problem |
| `# type: ignore`, change the type to `Any`, delete the hints | silences the referee; the bug is still there |
| Rerun a failing test until it passes | a test on a pure function gives the same answer every time |
| Trust whichever changed last, or was written first | age does not decide who is right; the specification does |
| Change the CI step until it is green | moves the referee instead of fixing the code |

Some questions test a concept rather than an artefact (sample Q2 and Q5). Use the course's own test as the tie-breaker. A refactoring changes the structure and keeps the behaviour: "if the output changes, it was not a refactoring". One function has one job: "can I describe it without the word *and*?" The option that passes the course's test is the answer, even when another option sounds more technical.

Two more habits. First, check the reason as well as the action: many options carry one ("because the test was written first"), and a sensible action with a wrong reason is still a wrong option. Second, decide from the artefact, not from length. In the sample the right option is the longest in five of the six multiple-choice questions (clearly so in Q1, Q2, Q4 and Q5), because it carries the precise condition ("with every test still passing unchanged"). That is a pattern in one sample, not a rule, and an examiner can reverse it: use it only as a last resort, after elimination, when you must guess.
"""),
        "key_points": [
            "No penalty: a blank is the only guaranteed zero. Answer every one.",
            "Artefact first, options second.",
            "Cross out the options that act on something the artefact never mentions.",
            "For concept questions, apply the course's definition as the test.",
        ],
        "exam_note_md": "Sample Q1, Q3 and Q4 each have three options from the careless-move family; the right one acts on what the output says.",
        "source_ref": "moodle/midterm-sample-questions.md; S7 slides 5, 9; S6 slide 18",
        "check": [qid(50), qid(1)],
    },
    {
        "id": sid(3),
        "heading": "Reading uv, ruff and mypy output fast",
        "body_md": md("""
Every tool in the course reports the same three things in its own layout: **where** (file, line, sometimes column), **what** (a message in plain words) and **a name** to search for. Session 7 taught it on mypy:

```text
src/report.py:15: error: Item "None" of "Expense | None" has no attribute "category"  [union-attr]
```

`src/report.py:15` is the file and line. The message says the value can be `None` and the code asks it for `.category`. `[union-attr]` is the error code, the thing you would search for. When there are many errors, **read the first one, fix it, run again**: later errors are often the same one repeating. mypy ends with a count (`Found 3 errors in 1 file`) or with `Success: no issues found`.

ruff puts the rule code first and the place on the next line:

```text
F401 [*] `os` imported but unused
 --> lint_me.py:1:8
```

uv writes `error:` and explains underneath. This is the real uv 0.12 output for a file broken the way sample Q1 describes, trimmed: uv first prints the same message as a `warning:` while it reads its settings, then the `error:` block that stops it. The error adds the offending line and a caret under the column:

```text
error: Failed to parse: `pyproject.toml`
  cause: TOML parse error at line 7, column 12
           |
         7 |     { name "Alberto Camara", email = "camara@protonmail.com" }
           |            ^
         missing assignment between key-value pairs, expected `=`
```

Three uv errors cover most of what you will meet:

| uv says | It means |
|---|---|
| `TOML parse error at line 7, column 12` | a typing mistake in `pyproject.toml`, at that place |
| ``The lockfile at `uv.lock` needs to be updated, but `--locked` was provided.`` | `pyproject.toml` changed and nobody ran `uv lock` and committed `uv.lock` |
| `` error: Failed to spawn: `expense` `` | no installed command has that name; compare with `[project.scripts]` |

Under time pressure, skip the noise (`Using CPython ...`, `Resolved 20 packages ...`, a `warning:` that repeats the error) and go straight to the line that starts with `error:`. Then ask two questions: which file does it name, and what does it say is wrong there? The right answer to a "what next" question acts on that file.
"""),
        "key_points": [
            "Where, what, and a name to search: `file:line`, message, `[code]`.",
            "Read the first error, fix it, run again.",
            "uv: find the line starting with `error:`, then read the lines under it.",
            "A lockfile error means: run `uv lock` and commit `uv.lock`.",
        ],
        "exam_note_md": "Expect real output with noise around it. The marks go to the student who finds the one line that matters.",
        "source_ref": "S7 slide 9; S6 slide 27; S4 slide 24; labs/01-scaffold.md troubleshooting",
        "check": [qid(38), qid(45)],
    },
    {
        "id": sid(4),
        "heading": "Reading pytest and shell output",
        "body_md": md("""
pytest prints a dot for each passing test and an `F` for each failure, then one block per failure and a summary. Under pressure, read three things.

**The `FAILED` line** names the file, the test and, for a parametrised test, the case in square brackets:

```text
FAILED tests/test_report.py::test_minimum_keeps_amounts_equal_to_it[10.0-expected2]
2 failed, 22 passed in 0.07s
```

`[10.0-expected2]` is the case with `minimum` 10.0, and 22 other tests passed.

**The `E` lines** show both sides of the `assert` in the order the test wrote them. The course writes the result first and the expected value second, and pytest often adds a `where` line saying which value came from the function:

```text
E       assert 90.0 == 95.0
E        +  where 90.0 = apply_discount(100.0)
```

**What it proves.** A failure proves that the code and the test disagree. It does not say which one is right; that is what sample Q4 tests. The specification decides: the backlog item, the Product Owner, the commit that changed the rule. And a line such as `assert 30.299999999999997 == 30.3` is not a bug in the arithmetic: money in floats needs `pytest.approx`.

Shell output is read the same way: what does each stage print, and what does the next stage do with it?

```bash
grep "food" expenses.csv | wc -l
```

`grep` prints every **line** that contains the text `food` anywhere: in the category, inside a merchant name such as `Seafood Shack`, or in the header if it matched. The pipe `|` sends those lines to `wc -l`, which counts them and prints one number. On a file with four food expenses and one dining expense at Seafood Shack, the course's Linux machines print:

```console
$ grep "food" expenses.csv | wc -l
5
```

Two more facts help. `wc -l expenses.csv` counts the header too: the demo file prints `421 expenses.csv` for 420 expenses. And `uniq -c` only merges identical lines that sit next to each other, which is why the idiom is `sort | uniq -c`.
"""),
        "key_points": [
            "`FAILED` line: which test and which case. `E` lines: both sides, result first in the course's tests.",
            "A failing test says the code and the test disagree, not which is right.",
            "`grep` prints matching lines; `wc -l` counts them. Matching is by text, anywhere in the line.",
            "The header is a line too.",
        ],
        "exam_note_md": "Sample Q4 and Q6 are both reading questions: one line of pytest, one pipeline. The harder versions add noise or a file where the obvious count is wrong.",
        "source_ref": "S8 slides 7–8, 10, 16; labs/08-tdd.md troubleshooting; S9 take-aways; sample Q4, Q6",
        "check": [qid(39), qid(40), qid(6)],
    },
    {
        "id": sid(5),
        "heading": "Writing a 5–8 line open answer",
        "body_md": md("""
Five to eight handwritten lines is about 60–120 words for the whole question, not per part. The marks sit in the numbered parts, so the structure of your answer should copy the structure of the question.

**Answer each part separately, with its number.** Write "1.", "2.", "3." in the margin. A marker looks for each part's points in that part's lines, and a good point written under the wrong number is easy to miss.

**Do exactly what the part asks.** "In one sentence" means one sentence. "Name two problems" means two, clearly separated. "Describe in words" means no code: you may name an identifier (`total_by_category`, `Expense`) but never write a block of code.

**For every problem, give three things:**

1. the problem, pointing at the code ("`r[1]` and `r[2]`", "the `print` on line 6");
2. its consequence for a teammate who reads, tests or changes it ("every call prints, so the total cannot be reused without that output");
3. the change, in words ("return the total and let the CLI print it").

Compare two answers to sample Q7, part 2:

| Weak | Strong |
|---|---|
| The names are bad and the code is not clean. | `r[1]` and `r[2]` do not say which is the amount, so a teammate must guess. |
| It could be more efficient. | It prints inside the calculation, so every caller gets output it did not ask for. |

The weak column states opinions. The strong column names the line and the consequence, which is what a rubric checks.

**Judgement questions** ("Do you accept?", "Which message is better?") get a verdict first, then the reason, then what you would do instead: "No. `# type: ignore` hides the crash on line 15; handle the `None` instead."

Use the course's vocabulary. "Computation is not output", "a tuple is a missing type", "one function, one job", "fail loudly at the boundary" and "the referee, not the judge" each pack a whole idea into a phrase the marker recognises. Finally, leave no part blank: one concrete line on a part earns more than a perfect paragraph on another.
"""),
        "key_points": [
            "60–120 words for the whole question; number every part.",
            "Problem, consequence for a teammate, change in words.",
            "Judgement parts: verdict first, then the reason, then the real fix.",
            "Name identifiers if you like; never write code.",
        ],
        "exam_note_md": "Each open part is marked on its own, so a short concrete line on every part beats a long answer to one.",
        "source_ref": "sample Q7–Q9 wording; S8 slide 31; S6 slides 13–24",
        "check": [qid(41), qid(48)],
    },
    {
        "id": sid(6),
        "heading": "Shape 1: read code and say what is wrong",
        "body_md": md("""
The first open shape gives you a short function and three tasks: say what it does, name the problems, describe the change. The problems always come from sessions 6 and 7, so check the code against this list.

| Look for | The course's words | Consequence for a teammate |
|---|---|---|
| `d`, `t`, `x`, `process`, `calc` | a name that needs a comment is not finished | they must trace the code to know what it holds or returns |
| `r[1]`, `e[3]`, a tuple of mixed things | a tuple is a missing type | nobody can tell what position 3 is; use `@dataclass(frozen=True)` |
| `print` next to a calculation | computation is not output | every call prints; if it prints instead of returning, a test cannot assert on it |
| several verbs in one description | one function, one job | to test one job you must run them all |
| `5`, `40`, `"food"` in the middle of code | magic numbers | a rule change means hunting through the code |
| no hints | type hints are contracts | mypy and the editor cannot help |
| bare `except:`, `return -1` | failing well | bugs become a silent wrong answer |

Sample Q7 is the model:

```python
def process(rows):
    total = 0
    for r in rows:
        if r[2] == "food":
            total += float(r[1])
    print("Food total:", total)
    return total
```

Part 1 wants one sentence: it adds up the amounts of the rows whose third field is `"food"`, prints that total and returns it. Part 2 wants two problems with consequences: the positions `r[1]` and `r[2]` and the name `process` hide what the data is; the `print` mixes computation with output, so every call writes to the screen and the total cannot be reused quietly. The function also returns the total, so "a test cannot check it" would be the wrong reason. Part 3 wants a change per problem: an `Expense` with named fields and a name that says what it returns, then a function that only returns while the CLI prints.

Running it shows two quieter problems. With no food rows it returns `0`, an `int`, and `mypy --strict` reports `Incompatible types in assignment (expression has type "float", variable has type "int")`, session 7's "int here, float there". And `ruff check` prints `All checks passed!`: a linter checks style and simple mistakes, not design. Two problems named precisely beat seven named vaguely.
"""),
        "key_points": [
            "Check names, tuples, `print`, jobs, magic numbers, hints and failure handling.",
            "Pair every problem with its consequence for a teammate.",
            "Pair every change with the problem it solves.",
            "A clean ruff run says nothing about design.",
        ],
        "exam_note_md": "The harder version is longer (three problems, one of which only shows when the code runs) or adds session 7's failing well: a bare `except` that returns `-1`.",
        "source_ref": "S6 slides 13–26; S7 slides 5, 17–19; sample Q7",
        "check": [qid(5), qid(23), qid(46)],
    },
    {
        "id": sid(7),
        "heading": "Shape 2: compare a diff and two commit messages",
        "body_md": md("""
The second open shape shows a diff and asks what changed, which commit message is better, and which test you would add.

**Reading a diff.** Lines starting with `-` were removed, lines with `+` were added, lines starting with a space are unchanged context. `@@ -22,7 +27,16 @@` says where the hunk sits. Read the removed and added lines as a pair: what did the code do before, and what does it do now?

**Part 1: what the change does.** Answer in behaviour, for a concrete input: "a file with a negative amount now raises `ValueError`; files without one load as before". Then decide whether behaviour changed. Session 7's rule: change the structure, keep the behaviour, and "if the output changes, it was not a refactoring". Session 6 checked it with `diff before.txt after.txt`: nothing printed means you are safe. One identical report is not proof, though. In the demo history, extracting `largest_expense` (commit `9d6c607`) gives the same report on `expenses.csv` and a different one on a file that contains only refunds. The slides still list this extraction as a refactoring move; the lesson is that one run is evidence, not proof.

**Part 2: which message is better.** Take the point of view of the reader six months later, scrolling `git log --oneline`. They see one line per commit. A good message says what the change does, in words they would search for. The demo history is full of good models:

```text
5e9466d Replace magic numbers with named constants
f3bb801 Rename calculate_totals to total_by_category
15836e1 Move printing and exiting out of the report module
d3df52b Use dict.fromkeys to drop duplicates in order
```

`Fix stuff in loader`, `Refactor`, `WIP` or `Update report.py` tell that reader nothing they could not get by opening the diff. A good message is also honest: if the change alters behaviour, the message says so.

**Part 3: the test you would add.** In words, give the input, the action and the expected result: "a CSV with one negative amount, written in `tmp_path`; `load_expenses` raises `ValueError`". Pick the edge the change created: empty, zero, negative, duplicate, missing. "Test that the function works" names no input and no result, so it earns nothing.
"""),
        "key_points": [
            "Read `-` and `+` as a before-and-after pair; answer in behaviour.",
            "If the output changes, it was not a refactoring; one identical run is not proof.",
            "A message is for the reader of `git log` in six months: what changed, in searchable words.",
            "A test in words: input, action, expected result.",
        ],
        "exam_note_md": "Expect a real diff from the expense-tracker history: the teacher told you to prepare with it.",
        "source_ref": "S7 slide 5; S6 slides 30–31; S4 slide 25; S8 slide 11; expense-tracker 9d6c607, 15836e1, d3df52b",
        "check": [qid(42), qid(31), qid(15)],
    },
    {
        "id": sid(8),
        "heading": "Shape 3: read tool output and judge it",
        "body_md": md("""
The third shape gives you a log and asks for three judgements: sort the errors, find the real danger, and decide whether a shortcut is acceptable.

**Sort by kind.** Session 7 grouped mypy's errors into three kinds:

| Kind | mypy is asking | Typical codes | Fix |
|---|---|---|---|
| Missing annotation | "what type is this?" | `[no-untyped-def]`, `[var-annotated]`, `[type-arg]`, `[no-untyped-call]` | write the hint |
| Types disagree | "int here, float there" | `[assignment]`, `[arg-type]`, `[return-value]`, `[no-any-return]` | make them agree (`0.0`, `float(...)`) |
| None not handled | "this can be missing" | `[union-attr]`, `[operator]` with `None` | check it, or change the type |

Codes help, but read the message: anything that names `None` is the third kind, and "missing a type annotation" is the first. `Returning Any from function declared to return "float"` sits with types disagree: the function promises a `float` and mypy sees `Any`, usually a value from `json` or `csv`. Sample Q9 confirms it by design: three errors, three kinds, and lines 8 and 15 are clearly the other two. Lab 07 also offers annotating the variable as a fix, so the model answer here also accepts "missing annotation" when you explain where the `Any` comes from; only converting with `float(...)` turns a `"900"` into `900.0`.

**Find the crash.** None not handled is the kind that crashes for a real user: "Empty list → None → crash at 2 a.m." Running the code behind sample Q9 with an empty list ends in `AttributeError: 'NoneType' object has no attribute 'category'`. A types-disagree error can crash too when the wrong thing is passed, for example a path where a list was expected. A missing annotation crashes nothing by itself; it means mypy cannot check what goes into or out of that function.

**Judge the shortcut.** The proposals vary (`# type: ignore`, change the type to `Any`, `strict = false`, run `mypy src` instead of `mypy src tests`) and the answer has the same shape each time: they make the referee quiet, not the code correct. With three `# type: ignore` comments the sample Q9 code passes:

```text
Success: no issues found in 2 source files
```

and still crashes on an empty list. CI is the referee every group shares, and a green check is in every Definition of Done; forcing it green ships the bug with a tick. Say no, then name the real fix for each line.
"""),
        "key_points": [
            "Three kinds: missing annotation, types disagree, None not handled.",
            "None not handled is the kind that crashes for a user.",
            "`# type: ignore`, `Any`, `strict = false`: a quiet referee, the same bug.",
            "Answer judgement parts with a verdict, a reason and the real fix.",
        ],
        "exam_note_md": "The teacher calls Q9 the harder question. The worst case is a real log of seven errors across `src` and `tests`; sort by the message, not by how frightening it looks.",
        "source_ref": "S7 slides 8–11; labs/07-refactor.md troubleshooting; S3 slide 3; moodle/project-pages.md",
        "check": [qid(34), qid(3), qid(47)],
    },
    {
        "id": sid(9),
        "heading": "A 60-minute plan, and the night before",
        "body_md": md("""
The paper's exact mix is not published, so plan by proportion and adjust when you see it.

| Minutes | What |
|---|---|
| 0–2 | Skim every page. Count the multiple-choice and open questions, note any marks. |
| 2–25 | Multiple choice, first pass. Artefact first, eliminate, answer. Put a dot next to any you are unsure of and move on. |
| 25–52 | Open questions. Divide the time by their number (about 8–9 minutes each for three). Answer every numbered part. |
| 52–58 | Back to the dotted multiple choice. Re-read the artefact, not your first answer. |
| 58–60 | Every multiple-choice question has a letter; every open part has at least one line. |

Two rules protect your marks. **Never let one question eat another's time**: if an open part is stuck, write the one concrete line you have and move on. **Spread before you polish**: two lines on each of three parts score more than eight lines on one. If the open questions carry more marks than the multiple choice, shift time towards them.

**The night before.** The teacher's advice is the session slides, the expense-tracker history, and the sample answered on paper first. A good evening:

1. Redo the nine sample questions on paper, timed, without notes. Then compare with the model answers and mark your reasons, not your letters.
2. Walk the expense-tracker history from `3e0834f` to `v0.4`: for each commit, say what changed and which session's idea it shows.
3. Revise the tables you must apply without thinking: the three kinds of mypy error, the refactoring moves, the edge-case questions (empty, zero, negative, duplicate, missing), argument versus option, exit codes and the pipe idioms from session 10.
4. Revise what the sample never asks about. Its nine questions draw almost entirely on sessions 3–10, and "the topics are not a full list". Still in scope: the seven lifecycle phases and bugs, features, refactor and tech debt (session 1); Waterfall against Agile and the manifesto's four values (session 2); Scrum's roles, artifacts and their commitments, events and time-boxes, and the Definition of Done (session 4); paths, "permission denied" and `644` against `755` (session 9).
5. Sleep. A tired reader skips the one line in the output that matters.

What not to do: memorise flags ("judgement, not memorised flags"), learn git branching or Docker (sessions 11 onwards), or practise writing code from memory. None of it is on this paper.
"""),
        "key_points": [
            "Skim, multiple choice, open questions, back to the dotted ones, then check for blanks.",
            "Spread before you polish; never let one question eat another's time.",
            "Night before: the sample on paper, the history, the tables. No flags.",
            "The sample never asks about the lifecycle, Agile, Scrum, or paths and permissions; they are still examined.",
        ],
        "exam_note_md": "Session 10 (Friday 16 October) is the last session in scope: pipes, text wrangling and bash scripts, all in the pipes and bash module.",
        "source_ref": "S6 slide 4; S8 slide 31; S9 slides 2, 24; labs/README.md",
        "check": [qid(43), qid(44), qid(49)],
    },
]

# ---------------------------------------------------------------------------
# Terms
# ---------------------------------------------------------------------------

terms = [
    ("Artefact", "The thing a question shows you: a terminal transcript, tool output, code, a diff or a failing test line. Read it before the options.", 1),
    ("No penalty", "A wrong multiple-choice answer scores the same as a blank: zero. So a guess can only help, and no question should be left blank.", 2),
    ("Distractor", "A wrong option built from a real but careless move: delete `.venv`, `# type: ignore`, rerun until green, trust whichever changed last.", 2),
    ("Error code", "The name in square brackets at the end of a mypy line, such as `[union-attr]`, or at the start of a ruff line, such as `F401`: what you search for.", 3),
    ("`uv.lock`", "The lockfile: the exact version of every dependency, committed. CI runs `uv sync --locked`, which refuses to install when it disagrees with `pyproject.toml`.", 3),
    ("`FAILED` line", "pytest's summary line for a failing test: file, test name, the `parametrize` case in square brackets, and the `assert` that failed.", 4),
    ("`pytest.approx`", "Compares floats with a tolerance. Money in floats needs it, because `0.1 + 0.2 == 0.3` is `False`.", 4),
    ("Pipe (`|`)", "Sends what one command prints to the next command as its input: `grep \"food\" expenses.csv | wc -l` counts the matching lines.", 4),
    ("Rubric point", "One concrete thing a marker looks for in a part, such as naming the `print` and saying every call writes to the screen. Each point scores, up to the part's marks.", 5),
    ("Computation is not output", "A function that returns can be tested, reused and read on its own; a function that prints can only be looked at. Print in the shell.", 6),
    ("A tuple is a missing type", "`r[2]` or `e[3]` says nothing about what it holds. A `@dataclass(frozen=True)` with named fields turns `e[3]` into `expense.amount`.", 6),
    ("One function, one job", "The Single Responsibility Principle. Test: can you describe the function without the word \"and\"?", 6),
    ("Magic number", "A constant in the code with no name, such as `40` or a pass mark of `5`. Name it once (`RULE_WIDTH`) and change it in one place.", 6),
    ("Demo tags and your tags", "The expense-tracker's tags `v0.0` to `v0.4` are the demo's. The tags in your own repository (`v0.1` for Checkpoint 1, `v0.2` for Checkpoint 2, `v0.5` for the partial submission) share some of the names but mark your group's work, not the demo.", 9),
    ("Refactoring", "Change the structure, keep the behaviour. \"If the output changes, it was not a refactoring.\"", 7),
    ("Commit message", "The line a reader sees in `git log --oneline`. A good one says what the change does, in words someone would search for six months later.", 7),
    ("Missing annotation", "Session 7's first kind of mypy error: \"what type is this?\". Fix: write the hint, including `-> None` on tests.", 8),
    ("Types disagree", "Session 7's second kind: \"int here, float there\", or a promised `float` that returns `Any`. Fix: make them agree.", 8),
    ("None not handled", "Session 7's third kind: \"this can be missing\". The one that crashes for a user. Fix: check it, or change the type.", 8),
    ("`# type: ignore`", "A comment that tells mypy to stop reporting a line. It hides the error; it never fixes the code.", 8),
    ("The referee, not the judge", "How the course describes CI: it does not mark you, but a red check means the work is not valid. Bending the referee to go green defeats it.", 8),
]

# ---------------------------------------------------------------------------
# Traps
# ---------------------------------------------------------------------------

traps = [
    "\"Leaving a multiple-choice question blank is safer.\" There is no penalty for a wrong answer, so a blank is the only guaranteed zero.",
    "\"An error from uv means the environment is broken.\" Read the `error:` line: a TOML parse error names a file, a line and a column. Deleting `.venv` or reinstalling uv changes nothing there.",
    "\"Every rename is a refactoring.\" Renaming a command, an option or a printed label changes what users type or read. Only renames inside the code keep the behaviour.",
    "\"The newer one wins\" (or \"the older one wins\"). When a test fails, neither age nor authorship decides who is right; the specification does.",
    "\"`# type: ignore` or `Any` fixes a mypy error.\" They switch the check off; the crash on an empty list is still there, now with a green tick.",
    "\"`grep \"food\" expenses.csv | wc -l` counts food expenses.\" It counts lines containing the text `food` anywhere, including a merchant called `Seafood Shack`; `wc -l` on a file also counts the header.",
    "\"The same report on `expenses.csv` proves a refactoring.\" One input is not proof: commit `9d6c607` gives the same report on the sample file and a different one on a file of refunds. The slides still list this extraction as a refactoring move; the lesson is that one run is evidence, not proof.",
    "\"A passing test proves the code is right.\" A test with no `assert` passes even against a function that returns `[]`; it only proves the call did not raise.",
    "\"An open answer is stronger with code.\" You will not write code. Describe the change in words and name the problem it solves.",
    "\"Swapping a component (CSV for JSON) is a refactoring, as in session 1.\" Session 1 used the word loosely; the exam applies session 7's definition: if what the program reads, writes or prints changes, it was not a refactoring.",
    "\"A function with a `print` in it cannot be tested.\" Only if it prints instead of returning. Sample Q7 prints and returns, so a test can assert on the total; the cost there is output on every call.",
    "\"The sample paper is the syllabus.\" Its topics are not a full list: the lifecycle, Agile, Scrum, and paths and permissions are still examined.",
]

# ---------------------------------------------------------------------------
# Flashcards
# ---------------------------------------------------------------------------

cards = [
    ("When, where, how long, and how much is the mid-term worth?", "Thursday 22 October 2026, 14:00, room 108, one hour, 30% of the course mark. It removes nothing from the final.", "recall", 1),
    ("Which sessions does the mid-term cover, and what are you never asked to do?", "Sessions 1–10: starting a project, clean code and tests, the terminal. You never write code: \"Judgement, not memorised flags.\"", "recall", 1),
    ("What three parts does every sample question have?", "A realistic scenario, an artefact (output, code, diff, test line) and a judgement: what to do, what is wrong, what it prints.", "concept", 1),
    ("Why answer every multiple-choice question?", "No penalty: a wrong answer scores the same as a blank, so a guess can only gain.", "concept", 2),
    ("What do \"delete `.venv`\", \"reinstall uv\" and \"`uv sync --upgrade`\" have in common in sample Q1?", "They act on something the error never mentioned. The error names `pyproject.toml`, line 7, column 12.", "concept", 2),
    ("Concept questions: the course's test for a refactoring, and for one job?", "Refactoring: the structure changes and the behaviour stays. One job: you can describe it without \"and\".", "distinction", 2),
    ("Read `src/report.py:15: error: ... [union-attr]` in three parts.", "Where: `src/report.py`, line 15. What: the message in plain words. `[union-attr]`: the code to search for.", "reading", 3),
    ("uv: \"The lockfile at `uv.lock` needs to be updated, but `--locked` was provided.\" What happened, and the fix?", "`pyproject.toml` changed but the updated `uv.lock` was never committed. Run `uv lock`, commit `uv.lock`, push.", "reading", 3),
    ("`uv run expense report` gives \"Failed to spawn: `expense`\". Why?", "No installed command has that name. `[project.scripts]` installs `expenses`; compare the two letter by letter.", "reading", 3),
    ("Twelve mypy errors on screen. Where do you start?", "With the first one. Fix it and run again: later errors are often the same one repeating.", "concept", 3),
    ("`E assert 90.0 == 95.0` followed by `where 90.0 = apply_discount(100.0)`. Which value did the code produce?", "90.0: the `where` line says it came from `apply_discount(100.0)`. The test expected 95.0.", "reading", 4),
    ("A test fails after a teammate's change. Who is right?", "The failure cannot tell you. Check which matches what the rule is supposed to be: the backlog item, the Product Owner, the commit that changed the rule.", "concept", 4),
    ("What does `grep \"food\" expenses.csv | wc -l` print?", "One number: how many lines contain the text `food` anywhere (category, merchant name, header).", "reading", 4),
    ("`wc -l expenses.csv` prints `421 expenses.csv`, but `read_expenses` returns 420 expenses. Why?", "The header line is a line too; `read_expenses` skips it.", "distinction", 4),
    ("Why does `uniq -c` need `sort` first?", "`uniq` only merges identical lines that sit next to each other.", "concept", 4),
    ("How long is a 5–8 line answer?", "About 60–120 words for the whole question, split across its numbered parts.", "recall", 5),
    ("The three things to write for each problem in an open answer?", "The problem (pointing at the code), its consequence for a teammate, and the change in words.", "concept", 5),
    ("In sample Q7, what do `r[1]` and `r[2]` hold, and why is that a problem?", "The amount and the category. A position says nothing: a tuple is a missing type. Use an `Expense` dataclass with named fields.", "reading", 6),
    ("Why is a `print` inside a calculation a problem?", "Computation is not output: every call writes to the screen, so the result cannot be reused quietly. If the function prints instead of returning, a test cannot assert on it either; sample Q7 prints and returns, so there the cost is the output, not the test.", "concept", 6),
    ("ruff prints `All checks passed!`. Is the code clean?", "Not necessarily: ruff checks style and simple mistakes, not names, jobs or design. Sample Q7 passes ruff.", "distinction", 6),
    ("When is a change not a refactoring?", "When behaviour changes: the output, the exit code, the command-line interface. \"If the output changes, it was not a refactoring.\"", "concept", 7),
    ("What makes a commit message good for a reader six months later?", "The log line alone says what changed, in words they would search for: `Reject negative amounts when loading expenses`, not `Fix stuff in loader`.", "concept", 7),
    ("How do you describe a test in words?", "Input, action, expected result: \"a CSV with one negative amount; `load_expenses` raises `ValueError`\".", "concept", 7),
    ("Session 7's three kinds of mypy error, and their fixes?", "Missing annotation: write the hint. Types disagree: make them agree. None not handled: check it, or change the type.", "recall", 8),
    ("Which kind is `Returning Any from function declared to return \"float\"`, and the fix?", "Types disagree (sample Q9 has one error per kind): promised `float`, got `Any` (from `json` or `csv`). Convert it with `float(...)`; lab 07 also allows annotating the variable, but only the conversion turns a `\"900\"` into `900.0`.", "reading", 8),
    ("Why refuse `# type: ignore` \"to get CI green\"?", "It silences the referee; the `None` crash still ships. Fix the causes instead.", "concept", 8),
    ("Eight minutes left: an untouched open question and two dotted multiple-choice answers. Order?", "One or two concrete lines on each open part first, then a final look at the dotted ones.", "concept", 9),
    ("What did the teacher say to prepare with?", "The session slides and the expense-tracker history on GitHub; answer the sample on paper first, then check your reasons.", "recall", 9),
]

# ---------------------------------------------------------------------------
# Questions: the nine originals
# ---------------------------------------------------------------------------

questions: list[dict[str, Any]] = []

questions.append(mcq(
    1, "exam", ["read-tool-output", "judgement"],
    """
You run `uv sync` in a fresh clone of your group's repo and see:

```console
$ uv sync
Using CPython 3.13.1
error: Failed to parse `pyproject.toml`
  TOML parse error at line 7, column 12
```

What should you do next?
""",
    [
        opt("Delete `.venv` and run `uv sync` again",
            "The misconception is \"something is wrong with the environment\". uv failed while reading `pyproject.toml`, before it touched any environment, and a fresh clone has no `.venv` anyway (it is in `.gitignore`)."),
        opt("Open `pyproject.toml` at line 7 and look for the syntax mistake",
            "The error names the file, the line and the column. A TOML parse error is a typing mistake in that file: fix it there and run `uv sync` again.", True),
        opt("Run `uv sync --upgrade` to refresh the packages",
            "Upgrading changes which versions get locked; it cannot help when uv cannot read the project file at all. It stops on the same line."),
        opt("Reinstall uv",
            "uv works: it read the file and told you where the problem is. Reinstalling the tool that gave you the right answer only costs time."),
    ],
    """
Read the error before acting. uv stopped while parsing `pyproject.toml`, the project's single source of truth, and it says where: line 7, column 12. That is a typing mistake (a missing `=`, quote or bracket), so the next step is to open the file at that line. The three distractors are the "turn it off and on again" family: they all act on something the message never mentions. The real uv output is even more helpful than the trimmed version on the paper: it prints the offending line, a caret under column 12 and what it expected (`missing assignment between key-value pairs, expected =`).
""",
    3, "sample Q1; S4 slides 21, 24; S7 slide 9", "teacher-sample", "run",
    dissection="""
**What it really tests.** Whether you read an error before you act. uv stopped while parsing `pyproject.toml`, the project's single source of truth, and told you where: line 7, column 12. Session 7's three-step reading (where, what, what to search for) works on every tool, not only mypy.

**The trap.** Three options are the "turn it off and on again" family: delete `.venv`, upgrade, reinstall. They feel like action, and they all act on something the message never mentions. Option a is doubly wrong: a fresh clone has no `.venv` yet, because `.gitignore` keeps it out of the repository.

**Full marks.** Option b. The real uv 0.12 output is even more explicit than the trimmed one in the question. With a missing `=` on line 7 it prints (after a `warning:` block that repeats the same message):

```text
error: Failed to parse: `pyproject.toml`
  cause: TOML parse error at line 7, column 12
           |
         7 |     { name "Alberto Camara", email = "camara@protonmail.com" }
           |            ^
         missing assignment between key-value pairs, expected `=`
```

Fix the line, run `uv sync` again and commit the fix: if the broken file reached the repository, CI's `uv sync --locked` is failing on the same line for everyone.

**How he could make it harder.** Keep the shape and change the error: a lockfile that disagrees with `pyproject.toml` in CI, a `.python-version` that breaks `requires-python`, or `Failed to spawn` after a typo in the command name. Or bury the `error:` line under lines of normal output. The variants below do all of these.
""",
))

questions.append(mcq(
    2, "exam", ["concept", "judgement"],
    "Which of these changes is a refactoring?",
    [
        opt("Adding a `--month` option to the `report` command",
            "A new option is new behaviour for the user: a feature. The command line is part of what the program does."),
        opt("Fixing a bug where the last expense in the file was skipped",
            "A bug fix changes the output, because the last expense is now counted. Useful work, but \"if the output changes, it was not a refactoring\"."),
        opt("Renaming variables and splitting one long function into two, with every test still passing unchanged",
            "Renaming and extracting a function are session 7's refactoring moves, and tests that pass without being edited are the evidence that behaviour stayed the same.", True),
        opt("Replacing the CSV file with a JSON file",
            "Changing the storage format changes what the program reads and writes: every existing CSV file stops working. Session 1 used \"refactor\" for swapping components, but session 7's definition decides here: the behaviour changed."),
    ],
    """
Session 7 defines it: refactoring changes the structure and keeps the behaviour, and "if the output changes, it was not a refactoring". Session 1 already separated bugs (unintended behaviours) from features (new behaviour); a refactoring is neither. Only option c changes structure alone, and it brings its own proof: the tests, which pin the behaviour, pass without being edited. The others are a feature (a), a bug fix (b) and a change of storage format that every existing data file would notice (d).
""",
    7, "sample Q2; S7 slide 5; S1 slide 19", "teacher-sample", "source",
    dissection="""
**What it really tests.** The definition, applied: refactoring changes the structure and keeps the behaviour. Session 7: "If the output changes, it was not a refactoring." Session 1 already named the other kinds of work: bugs (unintended behaviours) and features (new behaviour).

**The trap.** Every option is something a good developer might do, and three of them "improve the code". The bug fix (b) is the most tempting: it feels like cleaning up, but the report now includes an expense it used to skip. Option d hides a second trap. Session 1's lifecycle slide used "refactor" loosely, for software that must "connect to new components that replace old components", which sounds like swapping CSV for JSON. The exam's test is session 7's: same behaviour. Every existing CSV file stops working, so d is a behaviour change.

**Full marks.** Option c, and the phrase that proves it: "with every test still passing unchanged". Tests pin behaviour; if they pass without being edited, the behaviour they check did not change. Renaming and extracting a function are two of the six moves on the session 7 slide.

**How he could make it harder.** Make every option a rename, so the word stops being a clue and only one rename is invisible to users. Show a real commit that extracts a function and quietly changes a rare behaviour, such as `9d6c607` in the demo history. Or ask you to sort the history's commit messages into refactorings and features.
""",
))

questions.append(mcq(
    3, "exam", ["read-code", "read-tool-output", "judgement"],
    """
`mypy --strict` reports this error on the code below:

```python
def find_expense(expenses: list[Expense], expense_id: int) -> Expense | None: ...

expense = find_expense(expenses, 3)
total += expense.amount
```

```text
error: Item "None" of "Expense | None" has no attribute "amount"  [union-attr]
```

Which fix is most appropriate?
""",
    [
        opt("Add `# type: ignore` to the line",
            "It silences the line, not the problem: when `find_expense` returns `None`, `expense.amount` still crashes with `AttributeError`. The checker found a real bug and you would be hiding it."),
        opt("Handle the `None` case before using `expense.amount`",
            "mypy says the value can be missing. Deciding what happens when expense 3 does not exist (skip it, or report it and stop) is the fix session 7 gives: check it, or change the type.", True),
        opt("Change the return type of `find_expense` to `Any`",
            "`Any` switches off checking for every caller, so this error disappears, but `None` still comes back at run time and the crash is unchanged."),
        opt("Delete the type annotations from the function",
            "Without annotations mypy no longer knows that the function can return `None`, so this warning disappears and `--strict` complains about the missing annotations instead. The crash remains; you have only blinded the tool."),
    ],
    """
This is the "None not handled" kind from session 7, the one that crashes for a real user: an id that does not exist gives `None`, and `None.amount` raises `AttributeError`. Running the snippet confirms it ends in `AttributeError: 'NoneType' object has no attribute 'amount'`. The fix is to handle the `None` before using the value: a guard clause that skips or reports the missing expense, or a change to `find_expense` so it cannot return `None`. Options a, c and d all make mypy quiet without making the program correct.
""",
    8, "sample Q3; S7 slides 8, 10; labs/07-refactor.md troubleshooting", "teacher-sample", "run",
    dissection="""
**What it really tests.** Session 7's third kind of error, None not handled, and the judgement that goes with it: the type checker found a real bug, so fix the program, not the checker. The slide's own example has the same shape: `largest_expense` returns `Expense | None`, and "Empty list → None → crash at 2 a.m."

**The trap.** Options a, c and d all make the red text disappear. That is what a student under pressure wants, and none of them changes what happens when expense 3 does not exist. Running the snippet shows the program the checker was worried about:

```text
AttributeError: 'NoneType' object has no attribute 'amount'
```

**Full marks.** Option b. In words: before adding `expense.amount`, check whether `find_expense` returned `None`, and decide what a missing expense means (skip it, or report "no expense with id 3" and exit non-zero in the shell). The other route in lab 07's troubleshooting table is to change the function so it cannot return `None`; that is not offered here.

**How he could make it harder.** Use the other kinds: `Returning Any from function declared to return "float"` with a value from `json`, or `Missing type arguments for generic type "dict"`. Add a respectable-looking wrong option such as `# type: ignore[no-any-return]`. Or ask where the `None` should be handled: in the core, or at the boundary with an exit code.
""",
))

questions.append(mcq(
    4, "exam", ["read-tool-output", "judgement"],
    """
A test fails after a teammate changed `apply_discount`:

```text
FAILED tests/test_totals.py::test_total_with_discount - assert 90.0 == 95.0
```

The test expects 95.0. The function now returns 90.0. What can you conclude?
""",
    [
        opt("The function is wrong, because the test was written first",
            "Being written first does not make a test right: the rule may have changed since. Age is not evidence."),
        opt("The test is wrong, because the function was changed more recently",
            "This is \"trust whichever changed last\". A recent change is the likeliest thing to have broken the rule."),
        opt("The test is flaky and should be rerun until it passes",
            "`apply_discount` is a pure calculation: same input, same output. Rerunning gives 90.0 again; nothing about it is random."),
        opt("You can't tell yet: check which of the two matches what the discount is supposed to be",
            "The failure proves only that the code and the test disagree. Which one is right depends on the specification: is the discount 5% or 10%?", True),
    ],
    """
A failing test is information, not a verdict. `assert 90.0 == 95.0` says the function returned 90.0 and the test expected 95.0; it cannot say which of the two describes the business rule. So look outside the code: the backlog item, the Product Owner, the commit message of the teammate's change. If the discount is now 10%, the test is out of date and is updated in the same change; if it is still 5%, the function has a bug and the test just caught it. Options a and b pick a winner by timing, and c treats a deterministic failure as luck.
""",
    4, "sample Q4; S8 slides 5, 7", "teacher-sample", "run",
    dissection="""
**What it really tests.** What a failing test proves: that the code and the test disagree. It does not prove which one is wrong. Session 8: "The test forces you to say what done means", and what done means lives in the specification, not in whichever file is newer.

**The trap.** Options a and b sound like reasoning because they give a reason, but the reason is age: "written first", "changed more recently". Option c treats a deterministic calculation as luck. Our run of the same situation shows that pytest gives you more than the summary line:

```text
E       assert 90.0 == 95.0
E        +  where 90.0 = apply_discount(100.0)
```

The `where` line confirms the 90.0 came from the function.

**Full marks.** Option d, plus what to do next: check the rule (backlog item, Product Owner, the teammate's commit message). If the discount is now 10%, the test is stale and is updated in the same change; if it is still 5%, the function has a bug.

**How he could make it harder.** Put the evidence in the stem (a commit that says the rule changed), so that this time you can tell. Give real program output with no test at all and a user's complaint. Or show a test that passes but checks nothing.
""",
))

questions.append(mcq(
    5, "exam", ["concept", "read-code"],
    "A function called `process(rows)` reads a file, validates each row, calculates totals and prints a report. Which clean-code problem does this describe best?",
    [
        opt("The function name is too long",
            "`process` is short, not long; its problem is that it is vague. Naming matters, but it is not what this description shows best."),
        opt("The function does several jobs at once, so it is hard to test and to change",
            "Reads, validates, calculates and prints: four jobs. To test the totals you need a real file and a way to capture the printed report, and changing the layout means touching the calculation.", True),
        opt("The function repeats the same code in several places",
            "Nothing in the description shows duplication: each step happens once. A real clean-code problem, but not this one."),
        opt("The function uses too many type hints",
            "Type hints are contracts that mypy and teammates read; there is no such thing as too many. The description says nothing about hints."),
    ],
    """
Session 6's test: can you describe the function without the word "and"? This one reads a file and validates each row and calculates totals and prints a report: the Single Responsibility Principle broken four times. The consequences are what a teammate feels: you cannot test the calculation without a file on disk and captured output, and any change to one job risks the others. The course's fix is the demo's own path: commit `9d6c607` took the reading and the formatting out of `run()` (`read_expenses`, `format_report`, next to the existing `total_by_category`) on the way to v0.2, and `15836e1` moved the remaining printing into the CLI for v0.3.
""",
    6, "sample Q5; S6 slides 18, 20", "teacher-sample", "source",
    dissection="""
**What it really tests.** One function, one job (the Single Responsibility Principle), with session 6's test: can you describe it without the word "and"? The description has four verbs: reads, validates, calculates, prints.

**The trap.** Option a is half right: `process` is a poor name, which is why it tempts. But it is vague, not long, and the question asks which problem the description shows *best*. Options c and d name real clean-code ideas (duplication, type hints) that the description gives no evidence for.

**Full marks.** Option b, with the consequence: to test the totals you need a file on disk and a way to capture the printed report; to change the report's layout you edit the function that does the arithmetic. The course's own fix is the demo's path: `9d6c607` separated reading (`read_expenses`) and formatting (`format_report`) from the calculation (`total_by_category`) before v0.2, and `15836e1` left the printing to the CLI for v0.3.

**How he could make it harder.** Remove the easy answer: show a function that does exactly one job but is badly named, so "several jobs" becomes the distractor. Show the consequence in tool output: a test that gets `None` because the function prints. Or hide the second job, such as a file write inside a function that looks pure.
""",
))

questions.append(mcq(
    6, "exam", ["predict-output", "read-tool-output"],
    """
`expenses.csv` has one expense per line, and each line includes its category. What does this command print?

```bash
grep "food" expenses.csv | wc -l
```
""",
    [
        opt("The number of lines that contain the word food",
            "`grep` prints each line that contains `food`; the pipe hands those lines to `wc -l`, which counts lines and prints one number.", True),
        opt("The number of times food appears in the whole file",
            "`wc -l` counts lines, not matches: a line that contains `food` twice still counts once."),
        opt("Every line that contains food",
            "That is what `grep \"food\" expenses.csv` prints on its own. The pipe sends those lines to `wc -l`, so you only see the count."),
        opt("The number of words in the file",
            "That would be counting words in the whole file. Here `wc` only sees the lines `grep` let through, and `-l` counts lines."),
    ],
    """
Read a pipeline stage by stage. `grep "food" expenses.csv` prints the lines that contain the text `food`. The `|` sends that output to the next command instead of the screen. `wc -l` counts the lines it receives and prints the number; on the course's Linux machines that is just a number, such as `5`. One precision for later questions: `grep` matches the letters anywhere in the line, so a merchant such as `Seafood Shack` would be counted too, and so would the header if it contained the text. "Lines that contain the word food" is still the best of the four descriptions.
""",
    4, "sample Q6; S9 slide 6 and take-aways", "teacher-sample", "run",
    dissection="""
**What it really tests.** Reading a pipeline stage by stage: `grep` prints the matching lines, `|` sends them on, `wc -l` counts lines. Pipes are session 10's topic; the sample already uses them, so expect at least one.

**The trap.** Each wrong option is one stage misread. Option c forgets the pipe and describes `grep` alone. Option b confuses lines with matches (a line with `food` twice counts once). Option d describes counting words in the whole file.

**Full marks.** Option a. On the course's Linux machines the output is just a number. We ran it on a small file with four food expenses and a dining expense at `Seafood Shack`:

```console
$ grep "food" expenses.csv | wc -l
5
```

Five, not four: `grep` matches the letters `food` anywhere in the line. Option a is still the best of the four descriptions, but the precise version is "lines that contain the text food".

**How he could make it harder.** Show the file and ask for the number, so that the `Seafood Shack` line decides it. Ask why `wc -l expenses.csv` prints 421 when there are 420 expenses (the header). Or step into session 10 with `cut -d, -f3 expenses.csv | uniq -c`, where forgetting `sort` splits the counts.
""",
))

questions.append(open_q(
    7, "exam", ["read-code", "judgement"],
    """
**Read code and say what is wrong.**

```python
def process(rows):
    total = 0
    for r in rows:
        if r[2] == "food":
            total += float(r[1])
    print("Food total:", total)
    return total
```
""",
    [
        part("1", "In one sentence, what does this function do?", 1,
             "It adds up the amounts (second field) of the rows whose third field is \"food\", prints that food total and returns it.",
             ["Says it totals the amounts of only the rows whose category (`r[2]`) is \"food\", and that it both prints and returns the total"],
             "\"It processes the rows\" repeats the name and says nothing. \"It calculates the total\" misses that only food rows count. \"It prints the food total\" misses that it also returns it, which matters for part 2. One sentence, three facts: which rows, what it adds up, what it does with the result."),
        part("2", "Name two problems a teammate would face when reading, testing or changing it.", 2,
             "Reading: `r[1]` and `r[2]` (and the name `process`) say nothing, so a teammate must guess which is the amount. Changing: the `print` runs on every call, so the total cannot be reused quietly, and changing the wording means editing the arithmetic.",
             [
                 "Names the vague name or the positions (`process`, `r[1]`, `r[2]`) and says a reader must guess what they hold (a tuple is a missing type)",
                 "Names the `print` inside the calculation and says every call produces output, so the total cannot be reused quietly and the wording is tied to the arithmetic (computation is not output). Not \"a test cannot check the total\": the function returns it",
                 "Names the hard-coded `\"food\"`: another category needs a copy of the function",
                 "Names the missing type hints: `mypy --strict` rejects it, and `total = 0` starts as an `int`",
             ],
             "\"The names are bad\" or \"it is not clean code\" are verdicts without evidence: which names, and what can a teammate not do because of them? \"There are no comments\" contradicts the course: a comment that explains what code does is a failure of naming. Two problems in one breath may score, but each needs its consequence: guessing the columns, or output on every call that nobody can switch off. Careful: \"a test cannot check the total\" is wrong here, because the function returns it."),
        part("3", "Describe (in words, do not write code) how you would change it, and which of the two problems each change solves.", 2,
             "Use an `Expense` dataclass so `r[1]` becomes `expense.amount`, and a name that says what it returns, such as `food_total`: that solves the reading problem. Remove the `print` and let the CLI print the result: that solves the output problem, because the CLI decides the wording and the function can be reused or tested without printing.",
             [
                 "A change for the names: a name that says what it returns and named fields (a dataclass) instead of positions, explicitly linked to the reading problem",
                 "A change for the output: return only and print in the caller (the shell), explicitly linked to the output problem from part 2",
             ],
             "Writing the new function in code ignores the instruction and costs time. \"Make it cleaner\" or \"use better names\" without naming the change (a dataclass with named fields, return instead of print) scores nothing. The most common miss is the second half of the question: say which problem each change solves."),
    ],
    """
The function's job is easy to state, which is the point: part 1 checks that you read it correctly, including that it both prints and returns. Parts 2 and 3 test session 6's vocabulary used as consequences. `r[1]` and `r[2]` are a tuple used where a type belongs, so a teammate must guess which field is which; the `print` mixes computation with output, so every call prints and the report wording is welded to the arithmetic (a test can still assert on the returned total). The changes mirror the demo's path to v0.3: an `Expense` dataclass with named fields, a name that says what it returns, a function that only returns, and printing in the CLI. Linking each change to its problem is half of part 3.
""",
    6, "sample Q7; S6 slides 13–24; S7 slides 5, 10", "teacher-sample", "run",
    dissection="""
**What it really tests.** Reading code against sessions 6 and 7: names that say what they hold, a tuple is a missing type, computation is not output, one function one job, hints as contracts. Part 3 tests whether you can turn a diagnosis into a plan, in words, with each change linked to a problem.

**The trap.** Writing code in part 3 (the question forbids it), or listing style complaints without consequences ("names are bad"). The other trap is quantity: seven vague problems score less than two precise ones. And resist the reflex "a test cannot check the total": the function returns the total, so a test can (we ran `assert process(rows) == 12.5`: `1 passed`). The cost of the `print` is output on every call.

**What a run adds.** `ruff check` prints `All checks passed!` on this function, which shows a linter is not a design review. `mypy --strict` finds two errors:

```text
src/report.py:1: error: Function is missing a type annotation  [no-untyped-def]
src/report.py:5: error: Incompatible types in assignment (expression has type "float", variable has type "int")  [assignment]
```

The second is session 7's "int here, float there": `total = 0` makes the function return the `int` `0` when there are no food rows. (A precise note: strict mode still reads the body of an unannotated function, which is how it spots this; what it cannot check is anything that comes from `rows`.)

**Full marks.** One sentence for part 1; two problems with consequences for part 2 (positions and names; the `print` inside the calculation); two changes, each tied to its problem, for part 3. See the model answers.

**How he could make it harder.** A longer function with three problems, one of which only shows when you run it (a division by zero on an empty list). Or failure handling: a bare `except` that returns `-1`, so a wrong number flows silently into a total.
""",
))

questions.append(open_q(
    8, "exam", ["read-diff", "compare", "judgement"],
    """
**Compare.** A teammate shows you this diff from the expense-tracker history:

```diff
 def load_expenses(path):
     with open(path) as file:
         rows = list(csv.reader(file))
-    return [Expense(row[0], float(row[1])) for row in rows]
+    expenses = [Expense(row[0], float(row[1])) for row in rows]
+    if any(expense.amount < 0 for expense in expenses):
+        raise ValueError("Negative amount in " + path)
+    return expenses
```

Two candidate commit messages:

- A: `Fix stuff in loader`
- B: `Reject negative amounts when loading expenses`
""",
    [
        part("1", "What does this change do?", 2,
             "After building the list, `load_expenses` now checks the amounts: if any expense is negative it raises a `ValueError` naming the file, so the whole file is rejected. Files with no negative amounts load as before, and zero is still accepted.",
             [
                 "Says it now raises `ValueError` (with the path in the message) when any amount is negative",
                 "Says the whole load fails (nothing is returned), while files without negative amounts behave as before",
             ],
             "\"It adds error handling\" or \"it validates the data\" does not say what happens. The marker wants the behaviour: a negative amount makes the whole load fail with `ValueError`, and files without one load as before. \"It removes negative expenses\" misreads the diff: nothing is filtered out, the whole file is refused."),
        part("2", "Which message is better, and why? Answer from the point of view of someone reading the history six months later.", 2,
             "B. In `git log` it tells that reader what behaviour changed (negative amounts are now rejected at load time), so someone wondering why a file with a refund suddenly fails can find this commit from the one line. A says neither what was fixed nor that behaviour changed; the reader has to open the diff.",
             [
                 "Chooses B and says it states what the change does (rejects negative amounts when loading)",
                 "Explains the future reader's benefit: they can find or understand the change from the log line without opening the diff, while A says nothing about what or why",
             ],
             "\"B, because it is more detailed\" is true but answers a different question. The question names the reader: someone six months later, scanning one line per commit. Say what B allows them to do (find when negative amounts started being rejected, without opening the diff) and what A fails to say (what was fixed, and that behaviour changed)."),
        part("3", "Name one test you would add for this change, in words.", 1,
             "Write a small CSV with one negative amount in `tmp_path`, call `load_expenses` on it and check that it raises `ValueError`.",
             ["Describes an input with a negative amount and the expected result, `load_expenses` raises `ValueError` (also accepted: a file of positive amounts still loads; an amount of exactly 0 is accepted)"],
             "\"Test that the function works\" or \"test negative numbers\" names no input and no expected result. A test in words has three parts: the input (a CSV with one negative amount), the action (call `load_expenses`), and the expected result (it raises `ValueError`). Writing the test in code is not asked for and costs time."),
    ],
    """
The diff adds a check after the list is built: any negative amount makes `load_expenses` raise `ValueError` with the path in the message, so the whole file is refused. Our run of both versions confirms it: positive files load as before, a file with `Zara,-15.00` raises `ValueError: Negative amount in refund.csv`, and `0.00` passes. Message B wins because the reader six months later scans one line per commit in `git log --oneline` and needs to know what behaviour changed; A only says something was fixed somewhere. The test follows from the change: a small CSV with a negative amount, and the expectation that loading raises `ValueError`.
""",
    7, "sample Q8; S4 slide 25; S8 slides 11, 20", "teacher-sample", "run",
    dissection="""
**What it really tests.** Three skills on one artefact: reading a diff as a before and an after, judging a commit message from a future reader's position, and describing a test in words with an input and an expected result.

**The trap.** In part 1, "it adds validation" is too vague: say what happens (a `ValueError` naming the file, the whole load fails) and what does not change (files without negative amounts load as before). In part 2, "B is longer" or "B is more professional" misses the reader the question names. In part 3, "test that it works" has no input and no result.

**What a run adds.** We ran the before and after versions. A file of positive amounts loads identically; a file with `Zara,-15.00` raises `ValueError: Negative amount in refund.csv`; an amount of exactly `0.00` still loads, because the check is `< 0`. That boundary makes a good second test. One note: the demo's real reader is called `read_expenses`; `load_expenses` here is the teacher's illustration in the same style.

**Full marks.** See the model answers: behaviour before and after; B, because the log line alone says what changed; a test with a negative amount expecting `ValueError`.

**How he could make it harder.** Use a real diff from the history whose behaviour change is subtle, such as `15836e1`, where the error message moves from stdout to stderr. Or make the change itself questionable: the demo's tests already treat a negative amount as a refund.
""",
))

questions.append(open_q(
    9, "exam", ["read-tool-output", "judgement"],
    """
**Read tool output (harder).** You run `uv run mypy --strict src` on a teammate's branch:

```text
src/report.py:8: error: Function is missing a type annotation  [no-untyped-def]
src/report.py:15: error: Item "None" of "Expense | None" has no attribute "category"  [union-attr]
src/report.py:22: error: Returning Any from function declared to return "float"  [no-any-return]
```
""",
    [
        part("1", "Sort the three errors into the kinds we discussed in session 7.", 3,
             "Line 8: missing annotation. Line 15: None not handled. Line 22: types disagree, because the function promises a `float` but returns `Any` from something untyped.",
             [
                 "Line 8 (`no-untyped-def`): missing annotation",
                 "Line 15 (`union-attr`): None not handled",
                 "Line 22 (`no-any-return`): types disagree, declared `float` but returns `Any` (accept \"missing annotation\" only if the student explains the `Any` comes from an untyped source such as `json`)",
             ],
             "Copying the codes (`no-untyped-def`, `union-attr`) without naming the kinds misses the question: it asks for session 7's categories. Another weak pattern puts all three under \"types are wrong\". Line 22 is where students hesitate: the promise says `float`, mypy sees `Any`, so the two sides disagree."),
        part("2", "Which one points to a bug that could crash the program for a real user, and why?", 2,
             "Line 15. The value can be `None` (for example when the list of expenses is empty), and asking `None` for `.category` raises `AttributeError`, which stops the program. The other two mean mypy cannot check something; they do not crash anything by themselves.",
             [
                 "Picks line 15 (`union-attr`)",
                 "Explains the mechanism: a missing value (`None`, for example an empty list) is asked for `.category`, raising `AttributeError`, and the program crashes",
             ],
             "Choosing line 8 because a missing annotation sounds serious, or line 22 because `Any` sounds dangerous: neither crashes by itself. Naming line 15 without the mechanism earns half: say when the value is `None` (an empty list, nothing found) and what happens next (`AttributeError`, the program stops)."),
        part("3", "Your teammate proposes silencing all three with `# type: ignore` \"to get CI green\". Do you accept? Give your reasoning.", 2,
             "No. `# type: ignore` silences mypy but does not change the program: line 15 still crashes on an empty list, now behind a green tick from the team's referee. Fix the causes instead: hints on line 8, a `None` check before line 15, `float(...)` on line 22.",
             [
                 "Says no, because the ignore hides the problem without fixing it (line 15 still crashes)",
                 "Says what to do instead (fix each cause: add the hints, handle the `None`, convert the `Any`), or explains that CI is the shared referee or Definition of Done that a forced green defeats",
             ],
             "\"Yes, temporarily, to meet the deadline\" accepts a green tick on code that still crashes. \"No, because ignores are bad practice\" gives a verdict without the reason. The reason the marker wants: `# type: ignore` hides the crash on line 15 without fixing it, and CI is the shared referee. Better still, name the real fix for each line."),
    ],
    """
Session 7 named three kinds: missing annotation (line 8: no hints, so mypy cannot check what goes in or comes out), types disagree (line 22: the function promises a `float` and returns `Any` from something untyped, such as `json`), and None not handled (line 15). Only the third crashes by itself: when the list is empty the value is `None`, and `.category` raises `AttributeError`. We reproduced all three lines with `uv run mypy --strict src` and confirmed the crash. Silencing them with `# type: ignore` gives `Success` and keeps the crash. CI is the referee every group relies on and a green check is in every Definition of Done, so you refuse and fix the three causes, each a line or two.
""",
    8, "sample Q9; S7 slides 8–11; labs/07-refactor.md troubleshooting; moodle/project-pages.md", "teacher-sample", "run",
    dissection="""
**What it really tests.** Session 7's three kinds of mypy error, the one kind that crashes for a user, and a judgement about the CI referee. It is the paper's "harder" question because it combines reading output with a decision.

**The code behind it.** This file (imports and a constant omitted) produces the three lines in the question under `mypy --strict`:

```python
def format_line(name, amount):
    return name.ljust(NAME_WIDTH) + f"{amount:.2f}".rjust(10)


def category_of_largest(expenses: list[Expense]) -> str:
    by_amount = sorted(expenses, key=lambda expense: expense.amount)
    largest = by_amount[-1] if by_amount else None
    return largest.category


def monthly_budget(path: str) -> float:
    with open(path) as handle:
        settings = json.load(handle)
    budget = settings["monthly_budget"]
    return budget
```

With an empty list, `category_of_largest` ends in `AttributeError: 'NoneType' object has no attribute 'category'`. With `# type: ignore` on all three lines, mypy prints `Success: no issues found in 2 source files` and the crash is unchanged.

**The trap.** In part 2, choosing line 8 because "missing" sounds serious; a missing annotation only means mypy cannot check how the function is used. In part 3, "yes, just for now": a green tick on a crashing program is the referee misleading the whole group.

**Full marks.** See the model answers. For line 22, "types disagree" is the intended kind (declared `float`, got `Any`); naming the untyped source (`json`) shows you understand why.

**How he could make it harder.** A real log of seven errors across `src` and `tests`, with two crashes of different likelihood and a test missing `-> None`. Or a different shortcut: changing the CI step to `mypy src`, so the tests are no longer checked.
""",
))

# ---------------------------------------------------------------------------
# Variants of Q1 (uv errors)
# ---------------------------------------------------------------------------

questions.append(mcq(
    10, "hard", ["read-tool-output", "judgement"],
    """
A teammate added a dependency to `pyproject.toml`, ran `uv sync` on their laptop (everything worked) and pushed. The CI step *Install dependencies from the lockfile* is now red:

```console
$ uv sync --locked
Using CPython 3.13.15
Creating virtual environment at: .venv
Resolved 20 packages in 5ms
error: The lockfile at `uv.lock` needs to be updated, but `--locked` was provided.

hint: To update the lockfile, run `uv lock`.
```

What should happen next?
""",
    [
        opt("Run `uv lock` locally, commit the updated `uv.lock` and push it",
            "On the teammate's laptop `uv sync` quietly rewrote `uv.lock`; the new lockfile simply never reached GitHub. Committing it makes the two files agree again, which is what `--locked` checks.", True),
        opt("Change the CI step to plain `uv sync` so it can update the lockfile itself",
            "That moves the referee. CI would install whatever it resolves that day, and the point of the lockfile (the same versions for every teammate and for CI) is lost."),
        opt("Delete `uv.lock` from the repository so there is nothing to disagree with",
            "With no lockfile, `uv sync --locked` fails with `Unable to find lockfile`, and every machine would resolve its own versions: \"works on my machine\" again."),
        opt("Re-run the CI job, since the lockfile check sometimes fails on a cold cache",
            "The check compares two committed files; nothing about it is random. A re-run reads the same files and fails the same way."),
    ],
    """
`--locked` means: install exactly what `uv.lock` says, and refuse if `uv.lock` no longer matches `pyproject.toml`. The teammate's `uv sync` updated the lockfile on their laptop (we reproduced it: `git status --short` then lists `uv.lock` as modified), so locally everything worked, but only `pyproject.toml` was pushed. This is session 4's point: "works on my machine" can usually be pinpointed to a lockfile that was never committed. The hint line even says what to run. Lab 01's troubleshooting table gives the same fix: run `uv lock`, commit `uv.lock`, push.
""",
    3, "S4 slide 24; S5 slide 13; labs/01-scaffold.md §4 and troubleshooting", "teacher-variant", "run", variant_of=1,
))

questions.append(mcq(
    11, "exam", ["read-tool-output", "concept"],
    """
You clone the demo project, run `uv sync`, and then try to run the report:

```console
$ uv run expense report
error: Failed to spawn: `expense`
  cause: No such file or directory (os error 2)
```

The project's `pyproject.toml` contains:

```toml
[project.scripts]
expenses = "expense_tracker.cli:app"
```

What is the problem?
""",
    [
        opt("The virtual environment is damaged; delete `.venv` and sync again",
            "uv ran fine and looked for a command called `expense`. A new `.venv` would install the same `expenses` command, and `expense` would still not exist."),
        opt("typer is missing, so it has to be added to the dependencies",
            "typer is already a dependency, and a missing library gives an import error from Python, not \"Failed to spawn\" from uv."),
        opt("No command is called `expense`: the project installs `expenses`",
            "`[project.scripts]` decides the command's name: `expenses` points to module `expense_tracker.cli`, object `app`. Type `uv run expenses report`.", True),
        opt("The data file `expenses.csv` is missing from the folder",
            "A missing data file is reported by the program itself (`could not read ...`). Here the program never started: uv could not find a command with that name."),
    ],
    """
"Failed to spawn" means uv could not start the program you named. The command names a project installs are the left-hand sides of `[project.scripts]`, here `expenses`. Session 5 put it this way: `expenses` resolves to module `expense_tracker.cli` and object `app`, and "rename either side and the command disappears". Lab 01's troubleshooting table adds a second cause: `uv sync` has not been run since `[project.scripts]` changed. With `uv run` that rarely bites, because `uv run` re-syncs the project before it runs (we renamed the command and `uv run expense-tracker report` worked at once); the old name is what fails. Read the backticked name in the error and compare it, letter by letter, with the table.
""",
    3, "S5 slide 5; labs/01-scaffold.md troubleshooting", "teacher-variant", "run", variant_of=1,
))

questions.append(mcq(
    12, "beyond", ["read-tool-output", "judgement"],
    """
A teammate pinned the project to the Python on their laptop and pushed. You pull and run `uv sync`:

```console
$ uv sync
Using CPython 3.12.14
error: The Python request from `.python-version` resolved to Python 3.12.14, which is incompatible with the project's Python requirement: `>=3.13` (from `project.requires-python`)
Use `uv python pin` to update the `.python-version` file to a compatible version
```

CI installs Python 3.13. What is the right fix?
""",
    [
        opt("Lower `requires-python` to `>=3.12` so the project accepts their laptop",
            "That bends the project's promise to one machine. CI and the other teammates use 3.13, and code that relies on 3.13 would now be allowed to run where it may break."),
        opt("Delete `.venv` and run `uv sync` again",
            "The error is about two settings that disagree, not about the environment. A new `.venv` would be built from the same `.python-version` and fail the same way."),
        opt("Install Python 3.13 with the operating system's installer, then sync",
            "uv uses the interpreter that `.python-version` asks for; while it says 3.12, uv keeps choosing 3.12. And uv can install 3.13 by itself."),
        opt("Set `.python-version` back to `3.13`; uv installs that Python itself",
            "`requires-python` and CI both say 3.13, so the pin is the odd one out. uv installs and uses Python 3.13 for everyone: the same versions on every machine.", True),
    ],
    """
Two files talk about Python. `requires-python` in `pyproject.toml` is the project's promise (`>=3.13`); `.python-version` names the interpreter uv should use. The teammate's pin says 3.12, which breaks the promise, so uv refuses. Session 3's point is that uv installs Python itself, so nobody needs to adapt the project to the Python they happen to have. Restoring the pin to 3.13 makes your machine, theirs and CI agree. Reading the error is enough: it names both files and points to `uv python pin` as the tool for updating the pin.
""",
    3, "S3 slides 3, 5; S4 slides 21, 23; labs/00-setup.md uv steps", "teacher-variant", "run", variant_of=1,
))

# ---------------------------------------------------------------------------
# Variants of Q2 (refactoring)
# ---------------------------------------------------------------------------

questions.append(mcq(
    13, "hard", ["concept", "judgement"],
    "Four teammates each made one rename in the expense-tracker. Which change is a refactoring?",
    [
        opt("Renaming the `--min` option of `report` to `--minimum-amount`, and updating the tests",
            "The option is part of the command-line interface: `expenses report --min 20` now fails. That the tests had to change is the giveaway that behaviour changed."),
        opt("Renaming the command in `[project.scripts]` from `expenses` to `expense-tracker`",
            "The command users type disappears: `uv run expenses report` now fails with \"Failed to spawn\". An interface change, not a refactoring."),
        opt("Renaming the report's `TOTAL` label to `Grand total`",
            "The printed report changes, so `diff before.txt after.txt` would show a difference. \"If the output changes, it was not a refactoring.\""),
        opt("Renaming `calculate_totals` to `total_by_category` and updating its caller",
            "The function is internal: its caller changes in the same commit and nothing a user types or reads changes. It is commit `f3bb801` in the demo history.", True),
    ],
    """
All four are renames, and that is the trap: "rename" sounds like a refactoring move, so a careless reader picks any of them. The test is behaviour as a user meets it: what they type, what they read, what exit code they get. A rename inside the code (d) keeps all three. Renaming an option (a), the installed command (b) or a printed label (c) changes the interface or the output. Session 6's exercise made it checkable: run the report before and after, `diff` the two files, and nothing printed means you are safe.
""",
    7, "S7 slide 5; S6 slides 30–31; S5 slide 5; expense-tracker f3bb801", "teacher-variant", "source", variant_of=2,
))

questions.append(mcq(
    14, "hard", ["read-code", "compare", "judgement"],
    """
Commit `9d6c607` (*Separate reading and printing from the calculation*) extracted `largest_expense` out of `run()`. Before, inside `run()`:

```python
largest_amount = 0.0
largest = None
for expense in expenses:
    if expense[AMOUNT] > largest_amount:
        largest_amount = expense[AMOUNT]
        largest = expense
```

After:

```python
def largest_expense(expenses):
    largest = None
    for expense in expenses:
        if largest is None or expense[AMOUNT] > largest[AMOUNT]:
            largest = expense
    return largest
```

On the demo's `expenses.csv` the report is identical before and after. Which statement is most accurate?
""",
    [
        opt("It is a pure refactoring, because the report on `expenses.csv` is identical",
            "One input proves little. The sample file has only positive amounts, which is where the two versions agree."),
        opt("It changes behaviour when no amount is above zero, such as a file of refunds",
            "The old loop starts at `0.0`, so a negative amount never beats it and nothing is printed as the largest. The new function starts from the first expense. On a file of two refunds only the new version prints `Zara (clothing) on 2025-07-09 for -15.00` as the largest.", True),
        opt("It changes behaviour for an empty list: the new function crashes",
            "Both versions give `None` for an empty list: the loop never runs and `largest` stays `None`."),
        opt("It changes behaviour for ties: the new version keeps the last equal amount",
            "Both versions compare with a strict `>`, so a later equal amount never replaces the first. Ties go to the first in both."),
    ],
    """
A refactoring keeps the behaviour for every input, not only for the file you tried. Session 6's `diff before.txt after.txt` is good evidence, but it only covers the input you ran. Here the old code had a hidden rule (an expense must beat `0.0` to count) that the extraction dropped. Running the demo at `f3bb801` and at `9d6c607` confirms it: identical reports on `expenses.csv`, different reports on a file containing only refunds. The new behaviour is arguably better, but it is a behaviour change, and a commit that restructures and changes behaviour at once is harder to review. The honest version is two commits, or a message that says both. The slides list this extraction as a refactoring move (S7 slide 5), and on the course's data it behaves as one: if the exam asks whether it is a refactoring, the slides' answer is yes, citing the identical report. This question is the step beyond: one identical run is evidence, not proof.
""",
    7, "S7 slide 5; S6 slide 30; expense-tracker f3bb801..9d6c607", "teacher-variant", "run", variant_of=2,
))

questions.append(sort_q(
    15, "exam", ["concept", "read-diff"],
    "These commit messages come from the expense-tracker history. Put each commit in the kind of work it is.",
    [
        ("refactor", "Refactoring: same behaviour, better structure"),
        ("feature", "Feature: new behaviour for the user"),
        ("safety", "Safety net: tests or checks, program unchanged"),
    ],
    [
        ("`6efdf9d Filter by category and ignore small amounts`", "feature",
         "New ways to use the report: it can now be filtered by category and minimum."),
        ("`c746d38 Print the largest expense`", "feature",
         "The report prints a line it did not print before."),
        ("`bc9ef3d Add an add command that writes to data/`", "feature",
         "A whole new command for the user."),
        ("`5e9466d Replace magic numbers with named constants`", "refactor",
         "`40` becomes `RULE_WIDTH` and so on; the report is the same, character for character."),
        ("`f3bb801 Rename calculate_totals to total_by_category`", "refactor",
         "An internal rename with its caller updated; users see nothing."),
        ("`d3df52b Use dict.fromkeys to drop duplicates in order`", "refactor",
         "Same results, shorter code; the five duplicate tests stay green, which is the proof."),
        ("`d38d9e6 Test the pure core`", "safety",
         "Adds `tests/test_report.py` only; the program does what it did before."),
        ("`0e05065 Run ruff, mypy and pytest on every push`", "safety",
         "Adds the CI workflow, the referee; no line of the program changes."),
    ],
    """
Session 1 named features (new behaviour); session 7 defined refactoring (new structure, same behaviour). The history also has commits that change neither: tests and CI make the program safer to change without changing it. Use the message and what you know of the diff: a new option, line or command is a feature; a rename, a constant or a shorter implementation with the same results is a refactoring; a commit that only adds tests or a workflow is a safety net.
""",
    7, "S1 slide 19; S7 slide 5; S6 slide 31; expense-tracker history", "teacher-variant", "source", variant_of=2,
))

# ---------------------------------------------------------------------------
# Variants of Q3 (mypy fixes)
# ---------------------------------------------------------------------------

questions.append(mcq(
    16, "hard", ["read-tool-output", "judgement"],
    """
`mypy --strict` reports one error on this function:

```python
import json


def monthly_budget(path: str) -> float:
    with open(path) as handle:
        settings = json.load(handle)
    return settings["monthly_budget"]
```

```text
budget.py:7: error: Returning Any from function declared to return "float"  [no-any-return]
```

Which fix is most appropriate?
""",
    [
        opt("Convert the value with `float(...)` before returning it",
            "The value comes from `json`, which mypy cannot see into. Converting makes the promise true (a `\"900\"` in the file becomes `900.0`) and fails right there if the value is not a number. mypy then reports `Success`.", True),
        opt("Change the return type to `Any`, since that is what `json` gives back",
            "The error moves instead of going away: a caller that returns `monthly_budget(path) - spent` from a function declared `-> float` now gets `Returning Any from function declared to return \"float\"`, and every other caller silently loses its checking."),
        opt("Add `# type: ignore[no-any-return]`, naming the exact error code",
            "Naming the code looks careful, but it still only silences mypy. If the file says `\"900\"`, the function returns the string `'900'` while promising a float."),
        opt("Delete `-> float` so that mypy stops comparing the two",
            "Under `--strict` a missing return type is its own error (`Function is missing a return type annotation`), and the contract that told callers what they get is gone."),
    ],
    """
This is the types-disagree kind with a twist: the function promises a `float`, but the value comes from `json.load`, which returns `Any`, so mypy cannot check it. Lab 07's troubleshooting table gives the fix: the value came from something untyped, so convert it or annotate it. Running it shows why this matters: with `{"monthly_budget": "900"}` in the file, the original returns the string `'900'` from a function that says `float`, and a later subtraction would crash far from the cause. Options b, c and d move, hide or replace the error without making the value a float. Option c is the worst-case distractor because naming the code looks professional.
""",
    8, "labs/07-refactor.md troubleshooting; S7 slide 10", "teacher-variant", "run", variant_of=3,
))

questions.append(mcq(
    17, "exam", ["read-tool-output", "concept"],
    """
In `totals.py` (the `Expense` dataclass is defined above this function), `mypy --strict` reports one error:

```python
def total_by_category(expenses: list[Expense]) -> dict:
    totals: dict[str, float] = {}
    for expense in expenses:
        totals[expense.category] = totals.get(expense.category, 0.0) + expense.amount
    return totals
```

```text
totals.py:12: error: Missing type arguments for generic type "dict"  [type-arg]
```

Which kind of error is it, and what does it ask you to do?
""",
    [
        opt("Types disagree: the function builds one thing and promises another",
            "It promises a `dict` and returns a `dict`; nothing disagrees. The complaint is that the promise is incomplete."),
        opt("None not handled: `totals.get` can return `None`",
            "With a default (`0.0`), `get` never returns `None` here, and mypy names `None` explicitly when that is the problem."),
        opt("Missing annotation: say what the dict holds, `dict[str, float]`",
            "A bare `dict` tells mypy and the reader nothing about keys and values. Lab 07: write `dict[str, float]`, not `dict`.", True),
        opt("A ruff style warning that is safe to ignore",
            "It is mypy (the `file:line: error:` layout and the `[type-arg]` code), and under `--strict` it turns CI red."),
    ],
    """
Read the message literally: "missing type arguments" means the hint exists but is incomplete. A `dict` of what to what? That is session 7's first kind, missing annotation, whose question is "what type is this?" and whose fix is to write the hint: `-> dict[str, float]`. The body already knows the answer (`totals: dict[str, float]`), so the fix is one line. Lab 07's troubleshooting table lists the same message with the same fix, and says the same goes for `list` and `tuple`.
""",
    8, "S7 slide 10; labs/07-refactor.md troubleshooting", "teacher-variant", "run", variant_of=3,
))

questions.append(mcq(
    18, "beyond", ["read-code", "judgement"],
    """
The expense-tracker gains a `show` command: `uv run expenses show 3` prints expense number 3. Its core function is:

```python
def find_expense(expenses: list[Expense], expense_id: int) -> Expense | None:
    if 0 <= expense_id < len(expenses):
        return expenses[expense_id]
    return None
```

A user types an id that does not exist. Which design follows the course's rules for failing well?
""",
    [
        opt("`show` checks for `None`, writes `no expense with id 3` to stderr and exits with code 1",
            "A missing id is a normal \"no result\" for the core, so it returns `None`; the shell, where the program meets the user, reports it on stderr and exits non-zero. That is \"fail loudly, at the boundary\".", True),
        opt("`find_expense` returns `-1` for a missing id, and `show` prints whatever it gets",
            "\"Do not return -1 and hope somebody checks.\" `show` would print `-1` and exit 0: a program that lies about failing."),
        opt("`find_expense` returns an empty `Expense(\"\", \"\", \"\", 0.0)`, so nobody sees `None`",
            "mypy is happy and nothing crashes, but the user sees a blank expense of 0.00 as if it existed: a silent wrong answer, the worst way to fail."),
        opt("`show` wraps everything in a bare `except:` and prints `something went wrong`",
            "A bare `except` hides every bug (a typo, a missing import, Ctrl-C) behind the same vague message. Catch only what you can handle."),
    ],
    """
Session 7's table: a normal "no result" is `return None`, a caller that cannot carry on gets an exception, and crossing to the shell means translating into an exit code. A missing id is a normal "no result" for `find_expense`, so `Expense | None` is an honest type; mypy then forces every caller to handle the `None`, which is sample Q3's lesson. The place to handle it here is the shell: a message with `err=True` and `raise typer.Exit(code=1)`, as the demo's `report` command does for a missing file. Options b and c hide the failure, and d hides every other failure too.
""",
    8, "S7 slides 17–19; S5 slide 9; expense-tracker 15836e1", "teacher-variant", "source", variant_of=3,
))

# ---------------------------------------------------------------------------
# Variants of Q4 (who is right when a test fails)
# ---------------------------------------------------------------------------

questions.append(mcq(
    19, "hard", ["read-tool-output", "judgement"],
    """
CI is red after a teammate's push.

```console
$ git log --oneline
810913d Raise the member discount to 10% (backlog item 7, agreed in Sprint Planning)
8f2e122 Give members a discount on every price
```

```text
>       assert member_price(100.0) == pytest.approx(95.0)
E       assert 90.0 == 95.0 ± 9.5e-05
E
E         comparison failed
E         Obtained: 90.0
E         Expected: 95.0 ± 9.5e-05

tests/test_pricing.py:7: AssertionError
=========================== short test summary info ============================
FAILED tests/test_pricing.py::test_members_pay_less - assert 90.0 == 95.0 ± 9...
1 failed in 0.01s
```

What should you do?
""",
    [
        opt("Revert the discount to 5%, because the test defined the rule first",
            "The rule changed on purpose: the commit cites a backlog item agreed in Sprint Planning. Reverting would undo the Product Owner's decision."),
        opt("Widen the `pytest.approx` tolerance until 90.0 is accepted",
            "`approx` absorbs rounding noise such as `0.30000000000000004`, not a 5-euro difference. A tolerance that wide would accept almost any price."),
        opt("Delete the test, since the discount rule keeps changing",
            "A rule that changes is when you want a test pinning the current value. Without it, the next accidental change goes unnoticed."),
        opt("Update the test to expect 90.0, because the rule itself changed",
            "This time the evidence exists: the commit names backlog item 7. The test describes the old rule, so it is the one out of date. Ideally it changes in the same commit as the rule, so CI never goes red.", True),
    ],
    """
Sample Q4's lesson is that a failure alone cannot tell you who is right; you check the specification. Here the specification is in front of you: the latest commit raises the discount to 10% for backlog item 7, agreed in Sprint Planning. So the function matches the rule and the test is stale. The output is noisier than in Q4 because of `pytest.approx`, but it says the same thing: obtained 90.0, expected 95.0. The professional habit is that a rule change and its test change travel in one commit, so CI never goes red and the test always describes the current rule.
""",
    4, "S8 slides 5, 7–8; S4 slides 9–10; moodle/project-pages.md", "teacher-variant", "run", variant_of=4,
))

questions.append(mcq(
    20, "hard", ["read-tool-output", "judgement"],
    """
A user runs the demo at `v0.4`:

```console
$ uv run expenses report --category dining --min 20
Expense report for expenses.csv
category: dining
only amounts of 20.00 or more
----------------------------------------
dining                 3157.92
----------------------------------------
TOTAL                  3157.92

Largest single expense:
Ferreteria Mas (home) on 2025-11-17 for 296.49
```

They report: "I asked for dining and got a home expense." In `cli.py`, `largest_expense(expenses)` is called with every expense, not the filtered ones, and no test covers this. What is the right first step?
""",
    [
        opt("Change `largest_expense` to apply the filters too, since the header says dining",
            "That may be the right outcome, but it settles the rule on one user's word. Nobody has said what this line is meant to show, and the change could break what the Product Owner wanted."),
        opt("Close the report: the code does what it was written to do",
            "Code doing what it was written to do is no evidence that it was written right. This is sample Q4 again, with the winner picked by whoever wrote it."),
        opt("Find out what the line should show (backlog, Product Owner), then pin it with a test",
            "The code and the user's expectation disagree, and nothing written down decides between them. Check the specification first; whichever way it goes, a test then makes the rule explicit.", True),
        opt("Delete the `Largest single expense` line, since it causes confusion",
            "Removing a feature to avoid a question changes behaviour without asking anyone. What the product does is the Product Owner's decision."),
    ],
    """
This is sample Q4 without the test: two descriptions of the behaviour disagree, the code's and the user's, and the code cannot tell you which is right. The history shows the largest line was added in `c746d38` by looping over every row, after the filters already existed, and nothing records whether that was intended. In Scrum terms, what the product should do is the Product Owner's call; in testing terms, an unpinned rule is where a test belongs. So the first step is to find out the rule, and the second is a test that pins it (red first, if the code must change). Options a, b and d each decide the rule alone.
""",
    4, "S8 slide 5; S4 slides 6–7, 9; expense-tracker c746d38, v0.4", "teacher-variant", "run", variant_of=4,
))

questions.append(mcq(
    21, "beyond", ["read-code", "read-tool-output", "judgement"],
    """
A teammate adds this test, and pytest is happy:

```python
from expense_tracker.report import Expense, total_by_category


def test_total_by_category() -> None:
    expenses = [
        Expense("2025-07-01", "Bar Ramon", "dining", 10.0),
        Expense("2025-07-02", "Zara", "clothing", 40.0),
    ]
    total_by_category(expenses, category="", minimum=0.0)
```

```text
.                                                                        [100%]
1 passed in 0.01s
```

What does this passing test prove?
""",
    [
        opt("Only that the call does not raise an exception",
            "Without an `assert`, a test passes whenever the code runs to the end. A `total_by_category` that returned `[]` passes it too: we ran that stub.", True),
        opt("That `total_by_category` groups the totals correctly",
            "Nothing compares the result with anything. The result is computed and thrown away."),
        opt("That `total_by_category` is a pure function",
            "Calling a function says nothing about whether it prints or reads files, and this test does not check anything at all."),
        opt("Nothing yet, because pytest skips tests that contain no `assert`",
            "pytest ran it and counted it: `1 passed`. That is the danger: it looks like a real test in the summary."),
    ],
    """
A test is Arrange, Act, Assert, and this one stops after Act. pytest marks a test as passed when it runs to the end without an exception, so this test passes for the right function and for a broken one: we replaced `total_by_category` with a stub returning `[]` and it still said `1 passed`. It does add coverage, which is why session 8 calls coverage a map, not a score: "100% coverage with weak assertions proves nothing". The partial-submission rubric scores "tests that pass without checking anything" at 1. The fix is one line: assert the expected list, `[("clothing", 40.0), ("dining", 10.0)]`.
""",
    4, "S8 slides 6, 24; slides/partial-rubric.txt criterion 4", "teacher-variant", "run", variant_of=4,
))

# ---------------------------------------------------------------------------
# Variants of Q5 (clean-code problem)
# ---------------------------------------------------------------------------

questions.append(mcq(
    22, "hard", ["read-code", "concept"],
    """
Read this function from a teammate's branch. `mypy --strict` and `ruff check` both pass on it.

```python
def check(expenses: list[Expense]) -> list[Expense]:
    return [expense for expense in expenses if expense.amount < 0]
```

Which clean-code problem does it have?
""",
    [
        opt("It does two jobs: it filters, and it builds a new list",
            "Building the result is how it filters. You can describe it without \"and\": it returns the refunds. One job."),
        opt("It should print the refunds instead of returning them",
            "That is the opposite of the course's rule: a function that returns can be tested and reused; one that prints can only be looked at."),
        opt("Its name does not say what it returns: the refunds",
            "`check` sounds like a yes/no question or a validation that raises. It actually returns the negative expenses, so `refunds` would say what it returns, as session 6's naming table asks.", True),
        opt("It should raise `ValueError` when no expense is negative",
            "No refunds is a normal \"no result\": session 7's table says return an empty list, and raise only when the caller cannot carry on."),
    ],
    """
Sample Q5 described a function with too many jobs. This one has exactly one job, which removes the usual answer, and the tools are green, which removes the lazy answers. What is left is session 6's naming table: a function name says what it returns (`calculate_totals` became `total_by_category`), and a boolean reads as a yes/no question (`is_duplicate`). `check` breaks the first rule and borrows the look of the second: a teammate reading `if check(expenses):` expects a yes or a no and gets a list. Renamed `refunds` (or `negative_expenses`), it needs no comment. Option d mistakes a normal empty result for a failure.
""",
    6, "S6 slides 13, 15, 18", "teacher-variant", "run", variant_of=5,
))

questions.append(mcq(
    23, "exam", ["read-tool-output", "read-code", "judgement"],
    """
A teammate tries to test this function:

```python
def largest_expense(expenses: list[Expense]) -> None:
    largest = max(expenses, key=lambda expense: expense.amount)
    print(f"Largest: {largest.merchant} ({largest.category}) {largest.amount:.2f}")
```

```text
>       assert largest_expense(EXPENSES) == "Zara"
E       AssertionError: assert None == 'Zara'

tests/test_report.py:10: AssertionError
----------------------------- Captured stdout call -----------------------------
Largest: Zara (clothing) 40.00
=========================== short test summary info ============================
FAILED tests/test_report.py::test_largest_is_zara - AssertionError: assert No...
```

Which change fixes the cause?
""",
    [
        opt("Change the test to expect `None`, since that is what the function returns",
            "The test would pass and check nothing useful: every function that only prints returns `None`."),
        opt("Make the function return the largest expense, and print it in the CLI",
            "Computation is not output. Once it returns an `Expense`, the test can compare the result with Zara's expense, and the shell does the printing.", True),
        opt("Keep the body and change the signature to `-> Expense`",
            "The body still returns nothing: mypy then reports `Missing return statement`, and the test still gets `None`."),
        opt("Use `tmp_path`, so that the test can read what was printed",
            "`tmp_path` gives a test an empty folder for files; it has nothing to do with printed output. The problem is in the function, not in the test."),
    ],
    """
The output says it twice: the function returned `None` (the `assert None == 'Zara'` line), and the answer only went to the screen (the *Captured stdout* section shows `Largest: Zara (clothing) 40.00`). Session 6: "A function that returns can be tested, reused and read on its own. A function that prints can only be looked at." Session 8 lists it among the three that bite: "You cannot assert on a print. Make it return, and print in the shell." After the change, the CLI prints the line with `typer.echo`, as the demo's `cli.py` does from `v0.3` on.
""",
    6, "S6 slide 20; S8 slide 28; expense-tracker 15836e1", "teacher-variant", "run", variant_of=5,
))

questions.append(mcq(
    24, "beyond", ["read-code", "read-tool-output", "judgement"],
    r"""
A teammate wanted a record of the last report, so they added three lines at the end of `total_by_category`:

```python
    ordered = sorted(totals.items(), key=lambda pair: -pair[1])
    with open("data/last_totals.csv", "w") as handle:
        for name, amount in ordered:
            handle.write(f"{name},{amount:.2f}\n")
    return ordered
```

On their laptop `pytest` says `2 passed`. In CI the same two tests fail:

```text
E       FileNotFoundError: [Errno 2] No such file or directory: 'data/last_totals.csv'
FAILED tests/test_report.py::test_no_expenses_means_no_totals - FileNotFoundE...
FAILED tests/test_report.py::test_totals_are_grouped_by_category - FileNotFou...
2 failed in 0.02s
```

What is the real problem, and the fix?
""",
    [
        opt("CI is flaky: re-run the job until it is green",
            "The failure is deterministic: `data/` does not exist in a fresh clone, every single time."),
        opt("CI lacks the folder: commit `data/` so every clone has it",
            "`data/` is in `.gitignore` on purpose: it holds a user's own expenses, and the repository is public. A pure function would also still be writing into the project."),
        opt("The name is wrong: rename it `write_totals_by_category`",
            "An honest name would describe the mess, not fix it: the tests would still need the folder."),
        opt("The core writes a file: move the write into `cli.py`",
            "Computing totals and saving them are two jobs, and the saving touches the world. With the write in `cli.py`, the tests pass a list and get a list, on any machine.", True),
    ],
    """
This is sample Q5's "several jobs" in its most expensive form: one of the jobs is I/O hidden inside the functional core. Session 7: the core takes values and returns values, with no `open`, `print` or `sys.exit`; the shell is the only place that touches the world. Session 8's three that bite include tests that need your laptop: these pass where `data/` happens to exist (`2 passed`, as we reproduced) and fail on CI's fresh clone, because `data/` is in the demo's `.gitignore`. Moving the write to the CLI makes `total_by_category` pure again, and its tests need nothing but a list.
""",
    6, "S7 slides 13–15; S8 slides 19, 28; expense-tracker bc9ef3d (.gitignore data/)", "teacher-variant", "run", variant_of=5,
))

# ---------------------------------------------------------------------------
# Variants of Q6 (shell output)
# ---------------------------------------------------------------------------

SMALL_CSV = """date,merchant,category,amount
2025-07-01,Mercadona,food,23.40
2025-07-01,Cabify,transport,12.50
2025-07-02,Bar Ramon,food,10.00
2025-07-03,Zara,clothing,40.00
2025-07-04,Seafood Shack,dining,38.00
2025-07-05,Bonpreu,food,15.20
2025-07-06,Bar Ramon,food,10.00
2025-07-07,Cabify,transport,9.80"""

questions.append(mcq(
    25, "hard", ["predict-output", "read-tool-output"],
    f"""
`expenses.csv` contains:

```text
{SMALL_CSV}
```

What does this command print?

```bash
grep "food" expenses.csv | wc -l
```
""",
    [
        opt("`4`: the number of expenses in the food category",
            "That is what you wanted to count, not what `grep` matches. `grep` knows nothing about columns."),
        opt("The four food lines, one per line",
            "That is `grep` on its own. The pipe sends its lines to `wc -l`, which prints only a count."),
        opt("`9`, because `wc -l` counts every line of the file",
            "`wc -l` only sees the lines `grep` passed on; the file's nine lines (header included) never reach it."),
        opt("`5`, because the line for `Seafood Shack` also contains food",
            "`grep` matches the letters `food` anywhere in a line, so the dining expense at Seafood Shack is counted with the four food expenses.", True),
    ],
    """
`grep "food"` keeps every line in which the text `food` appears, wherever it appears: four lines have it as the category, and one has it inside the merchant name `Seafood Shack`. `wc -l` counts those five lines, and on Linux prints `5`. This is the worst case of sample Q6: the command does what it says, which is not what the person typing it meant. Counting a column needs a pattern that pins the column, such as `",food,"`, which prints `4` on this file. The judgement being tested is reading what a command matches, not what you hoped it matches.
""",
    4, "sample Q6; S9 take-aways", "teacher-variant", "run", variant_of=6,
))

questions.append(mcq(
    26, "exam", ["read-tool-output", "concept"],
    """
In the demo repository:

```console
$ wc -l expenses.csv
421 expenses.csv
$ head -3 expenses.csv
date,merchant,category,amount
2025-07-01,Cabify,transport,36.25
2025-07-01,Ferreteria Mas,home,29.49
```

Yet `len(read_expenses("expenses.csv"))` is 420. Why the difference?
""",
    [
        opt("`wc -l` counts the six duplicate rows twice",
            "`wc -l` counts each line once, duplicates included, and so does `read_expenses`. The six duplicates explain 420 against 414, a different question."),
        opt("The header line is a line too, and `read_expenses` skips it",
            "`date,merchant,category,amount` is line 1 of the file, and `read_expenses` skips it with `next(reader)`. 421 lines, 420 expenses.", True),
        opt("`wc -l` adds one extra line for the end of the file",
            "`wc -l` counts newline characters; there is no extra line for the end of the file."),
        opt("`read_expenses` drops one row whose amount is not a number",
            "It only skips rows that do not have four fields, and the sample file has none. The difference is the header."),
    ],
    """
`wc -l` counts lines, and the first line of a CSV is its header. The demo's `read_expenses` skips it with `next(reader)` before reading rows, so 421 lines give 420 expenses. Session 8 used these numbers: `len(read_expenses("expenses.csv"))` is 420 and, after `remove_duplicates`, 414. When a count from the shell and a count from the program differ by one, check the header first.
""",
    4, "S8 slide 16; S9 slide 9; expense-tracker 9d6c607 (read_expenses)", "teacher-variant", "run", variant_of=6,
))

questions.append(mcq(
    27, "hard", ["read-tool-output", "predict-output"],
    """
A teammate wants a count per category from a small `expenses.csv` (a header plus eight expenses) and runs:

```console
$ cut -d, -f3 expenses.csv | uniq -c
      1 category
      1 food
      1 transport
      1 food
      1 clothing
      1 dining
      2 food
      1 transport
```

Why does `food` appear three times?
""",
    [
        opt("`cut` printed the category column three times over",
            "`cut -d, -f3` prints the third field of each line once, in file order: one output line per line of the file."),
        opt("The file uses three different spellings of food",
            "All three are the same word; the output repeats `food` because of where the lines sit, not how they are spelled."),
        opt("`uniq` only merges equal lines that sit next to each other",
            "In file order the food lines are not all adjacent, so `uniq` counts each run separately. With `sort` before `uniq -c`, the output has one line, `4 food`.", True),
        opt("`uniq -c` counts characters in each line, not lines",
            "It counts how many times a line repeats in a row: the `2 food` line is two adjacent food lines."),
    ],
    """
`uniq` compares each line with the one just before it. The categories arrive in file order (food, transport, food, clothing, dining, food, food, transport), so `food` appears in three separate runs and is counted three times. Sorting first groups equal lines, which is why the idiom is `sort | uniq -c`; on this file it prints `1 category`, `1 clothing`, `1 dining`, `4 food` and `2 transport`. Notice the `1 category` line too: the header is a line, so it is counted unless you skip it. Pipes are session 10 material, prepared before its slides were published; the skill is the one sample Q6 already uses, reading each stage's output.
""",
    4, "S10 slides 4 and 6–7; S9 take-aways; labs/10-wrangling.md", "teacher-variant", "run", variant_of=6,
))

# ---------------------------------------------------------------------------
# Variants of Q7 (read code)
# ---------------------------------------------------------------------------

questions.append(open_q(
    28, "hard", ["read-code", "judgement"],
    """
A teammate in the Gradebook group wrote:

```python
def calc(s):
    t = 0
    w = 0
    for x in s:
        if x[2] > 0:
            t += x[1] * x[2]
            w += x[2]
    avg = t / w
    if avg >= 5:
        print("PASS", round(avg, 2))
    else:
        print("FAIL", round(avg, 2))
    return avg
```

Called as `calc([("midterm", 6.0, 0.3), ("project", 8.0, 0.3), ("final", 3.5, 0.4)])`, it prints `PASS 5.6` and returns `5.6`.
""",
    [
        part("1", "In one sentence, what does this function do?", 1,
             "It computes the weighted average of the marks (skipping zero weights), prints PASS or FAIL against 5 with that average, and returns it.",
             ["Says it computes a weighted average of marks and prints PASS or FAIL against 5, returning the average"],
             "\"It calculates the grade\" or \"it calculates the average\" misses the weights and the pass or fail decision. \"It prints PASS or FAIL\" misses that the number is computed and returned. One sentence must cover what goes in, what is computed and what comes out."),
        part("2", "Name three problems a teammate would face when reading, testing or changing it.", 3,
             "`calc`, `t`, `w`, `x[1]` and `x[2]` say nothing, so you must guess which position is the mark. The pass or fail decision is only printed, so a test cannot check it. The pass mark `5` is a magic number, and an empty list crashes with `ZeroDivisionError`.",
             [
                 "Names and positions (`calc`, `t`, `w`, `x[1]`, `x[2]`) hide what they hold: a tuple is a missing type",
                 "The pass or fail decision is printed, not returned (computation mixed with output), so it cannot be asserted",
                 "The pass mark `5` is a magic number: changing it means hunting through the code",
                 "An empty list or all weights zero divides by zero (`ZeroDivisionError`)",
                 "No type hints: `mypy --strict` rejects it",
             ],
             "Three style complaints (\"short names, no comments, too long\") without saying what a teammate cannot do earn little. \"Add comments\" is the opposite of the course's rule: rename instead. \"It could crash\" without the input that crashes it (an empty list, or every weight zero) is too vague to score."),
        part("3", "Describe in words (no code) how you would change it, and which problem each change solves.", 3,
             "A `Mark` dataclass and the name `weighted_average` fix the reading problem. Returning the average, with a separate pass check, and printing PASS or FAIL only in the CLI fixes the testing problem. A named `PASS_MARK` and a decision for an empty gradebook (raise, reported by the shell) fix the last two.",
             [
                 "A dataclass with named fields and names that say what they hold or return, linked to the reading problem",
                 "Return values (the average, and a pass or fail result) and print only in the CLI, linked to the testing problem",
                 "A named constant for the pass mark, or a decision for the empty case reported at the boundary, linked to the magic number or the crash",
             ],
             "Rewriting the function in code ignores the instruction and loses time. \"Make it cleaner\" or \"split it into functions\" without saying which functions and why scores nothing. The most common miss is not linking each change to a problem from part 2, which the question explicitly asks for."),
    ],
    """
This is sample Q7 made longer and denser: three problems instead of two, and one of them only shows when you run it. Running it confirms part 1 (`PASS 5.6`, returns `5.6`) and the crash: both `calc([])` and a list whose weights are all zero raise `ZeroDivisionError: division by zero`. `ruff check` passes, and `mypy --strict` reports only `Function is missing a type annotation`: with no hint on `s`, everything read from it is unknown to mypy, so it has nothing to compare. The marks go to concrete problems with their consequences, and to changes linked to those problems.
""",
    6, "S6 slides 15–24; S7 slides 5, 17; S8 slide 11", "teacher-variant", "run", lines="6–8", variant_of=7,
))

questions.append(open_q(
    29, "beyond", ["read-code", "judgement"],
    """
The Parking lot group's fee function:

```python
def fee(ticket):
    try:
        minutes = ticket["exit"] - ticket["entry"]
        if minutes <= 60:
            return 2.50
        return 2.50 + (minutes - 60) / 60 * 1.80
    except:
        return -1
```

A ticket is a dict such as `{"entry": 600, "exit": 780}` (minutes since midnight); for that ticket it returns `6.1`. A car that is still parked has `"exit": None`.
""",
    [
        part("1", "What does `fee` return for a car that is still parked, and what goes wrong when a teammate adds up the day's takings with it?", 2,
             "It returns `-1`: subtracting from `None` raises a `TypeError` that the bare `except` swallows. In the takings each parked car silently counts as minus one euro: 2.50 and 6.10 plus a parked car total 7.60, not 8.60, with no error.",
             [
                 "Says it returns `-1` because the `TypeError` on `None` is caught by the bare `except`",
                 "Says the `-1` is added like a fee, so the takings are silently wrong (no error, no exit code)",
             ],
             "\"It returns an error\" is wrong: nothing reports an error, which is the problem. \"It crashes\" is also wrong: the bare `except` catches the `TypeError`. The marks are for `-1`, and for what `-1` does downstream: it is added to the takings like a fee, making the day's total one euro short per parked car."),
        part("2", "Name two other problems a teammate would face.", 2,
             "The bare `except` hides every bug: a misspelt key such as `\"exti\"` also gives `-1` instead of failing. And `2.50`, `1.80` and `60` are magic numbers, in a ticket that is a dict of strings mypy cannot check.",
             [
                 "The bare `except` hides every bug (a typo in a key, a wrong type) behind the same `-1`",
                 "Magic numbers `2.50`, `1.80` and `60` (prices and the first hour) have no names",
                 "The ticket is a dict with string keys, a missing type, and there are no hints, so `mypy --strict` cannot check it",
             ],
             "Repeating part 1 (the `-1`) does not count as another problem. \"Bad names\" is weak here: `fee` and `minutes` are fine. Strong answers name the bare `except` hiding unrelated bugs, the magic prices, or the dict with string keys that mypy cannot check."),
        part("3", "Describe in words how you would change the failure handling. Do not write code.", 2,
             "Remove the bare `except` and the `-1`. A parked car is a normal \"no fee yet\" (skip it, or return `None` with an honest type). A malformed ticket raises `ValueError`, which the CLI reports on stderr with exit code 1.",
             [
                 "Removes the bare `except` and the `-1` sentinel (\"do not return -1 and hope somebody checks\")",
                 "Separates the normal missing exit (`None` or skip, with an honest type) from a real error (raise), reported at the boundary on stderr with a non-zero exit code",
             ],
             "\"Add better error handling\" says nothing. \"Catch `TypeError` instead\" narrows the `except` but still returns `-1`. The course's rules give the answer: no sentinel values, a missing exit is a normal \"no result\", a malformed ticket raises, and the shell prints to stderr and exits non-zero."),
    ],
    """
Sample Q7 asked about names and output; this one adds session 7's failing well. Running it confirms each claim: a parked car returns `-1`; a misspelt key returns `-1`; the takings for two paid tickets (2.50 and 6.10) plus one parked car come out as `7.6`, one euro short, with no error. ruff with the course's rule set flags the `except:` line as `E722`. The course's rules are short: catch only what you can handle, do not return `-1` and hope somebody checks, raise in the core, and translate to stderr and an exit code in the shell.
""",
    6, "S7 slides 17–19; S6 slides 16, 22–24; S5 slide 9", "teacher-variant", "run", variant_of=7,
))

# ---------------------------------------------------------------------------
# Variants of Q8 (compare a diff)
# ---------------------------------------------------------------------------

questions.append(open_q(
    30, "hard", ["read-diff", "compare", "judgement"],
    """
From the demo history, trimmed. In `src/expense_tracker/cli.py`:

```diff
@@ -22,7 +27,16 @@ def report(
     category: str = typer.Option("", help="Only this category."),
     minimum: float = typer.Option(0.0, "--minimum", "--min", help="Ignore amounts below this."),
 ) -> None:
-    run(path, category, minimum)
+    try:
+        expenses = read_expenses(path)
+    except (OSError, ValueError):
+        typer.echo(f"could not read {path}", err=True)
+        raise typer.Exit(1) from None
+
+    totals = total_by_category(expenses, category, minimum)
+    largest = largest_expense(expenses)
+    for line in format_report(path, category, minimum, totals, largest):
+        typer.echo(line)
```

In `src/expense_tracker/report.py`:

```diff
-def run(path: str, category: str, minimum: float) -> None:
-    try:
-        expenses = read_expenses(path)
-    except (OSError, ValueError):
-        print(f"could not read {path}")
-        sys.exit(1)
-
-    totals = total_by_category(expenses, category, minimum)
-    largest = largest_expense(expenses)
-    for line in format_report(path, category, minimum, totals, largest):
-        print(line)
```

Two candidate messages. A: `Refactor`. B: `Move printing and exiting out of the report module`.
""",
    [
        part("1", "What does this change do?", 2,
             "It deletes `run()` from `report.py` and moves its work (reading with error handling, computing, printing) into the CLI's `report` command, so `report.py` is a pure core and only the CLI touches the terminal.",
             [
                 "Says the reading, error handling and printing moved from `run()` in `report.py` into the CLI command, and `run()` is gone",
                 "Names the purpose: `report.py` becomes pure (functional core) and the I/O lives in the shell",
             ],
             "\"It refactors the report\" names a kind of change without saying what moved. \"It adds error handling\" is wrong: the `try` and `except` already existed in `run()`; they moved. The marks are for where the reading, error handling and printing went (the CLI) and why (`report.py` becomes pure)."),
        part("2", "Is it a pure refactoring? Name the one thing a user or a script could notice.", 2,
             "Almost: the report and exit code 1 are unchanged, but the error message moved from stdout (`print`) to stderr (`err=True`). A script that redirects output with `>` no longer captures it.",
             [
                 "Says the report and the exit code 1 are unchanged",
                 "Spots that the error message now goes to stderr instead of stdout, visible when output is redirected",
             ],
             "\"Yes, nothing changes\" misses the stream. \"No, it changes the output\" without saying how is too vague. The precise answer: the report and exit code are the same; the error message now goes to stderr, which a user only notices when redirecting output."),
        part("3", "Which message is better for someone reading the history six months later, and why?", 2,
             "B: it says what moved and from where, so `git log --oneline` answers why `report.py` has no `print`. `Refactor` fits half the history and says nothing.",
             [
                 "Chooses B and says it names what changed (printing and exiting moved out of `report.py`), so the log line alone answers a future question",
                 "Says A fits almost any commit and tells the reader nothing specific",
             ],
             "\"B is more descriptive\" is true but does not explain the reader's benefit. Say what the reader can do with B (find when printing left `report.py`) and what is wrong with A (it fits most commits in the history)."),
        part("4", "Name one test you would add, in words.", 1,
             "With `CliRunner`, run `report` on a missing file: exit code 1, and `could not read` on stderr.",
             ["A CLI test (`CliRunner`) on a missing file expecting exit code 1 and the message on stderr (also accepted: a pure test of `total_by_category` with a plain list, now that it needs no file)"],
             "\"Test the CLI\" names no input or result. Give the input (a file that does not exist), the action (run `report` with `CliRunner`) and the expected result (exit code 1, message on stderr)."),
    ],
    """
This is commit `15836e1`, the step from `v0.2` to `v0.3` that session 7 announced: "Moving this to the edge is v0.3". Running both versions on a missing file shows the one visible difference: at `04d699f` the message `could not read nosuch.csv` arrives on stdout, at `15836e1` on stderr; the exit code is 1 in both. The demo's later commit `f3d9870` (*Test reading a file and the missing-file exit code*) adds the test from part 4, checking `result.exit_code == 1` and the message in `result.stderr`.
""",
    7, "expense-tracker 15836e1, f3d9870; S7 slides 13, 19; S8 slide 21", "teacher-variant", "run", lines="6–8", variant_of=8,
))

questions.append(mcq(
    31, "exam", ["read-diff", "compare"],
    """
Which commit message is best for this change, for someone reading the history six months later?

```diff
 def remove_duplicates(expenses: list[Expense]) -> list[Expense]:
-    seen: set[Expense] = set()
-    unique: list[Expense] = []
-    for expense in expenses:
-        if expense not in seen:
-            seen.add(expense)
-            unique.append(expense)
-    return unique
+    return list(dict.fromkeys(expenses))
```
""",
    [
        opt("`Refactor`",
            "True, and useless: most of the clean-code commits are refactorings. The reader learns nothing they could search for."),
        opt("`Improve how remove_duplicates works`",
            "It names the function but not what changed; \"improve\" could mean faster, fixed or rewritten."),
        opt("`Use dict.fromkeys to drop duplicates in order`",
            "It says what the code now does and keeps the important property visible: order is preserved. It is the demo's real message for `d3df52b`.", True),
        opt("`Small changes after Friday's TDD class`",
            "It records when, which `git log` already shows, and not what. Six months later nobody remembers which Friday."),
    ],
    """
Sample Q8's part 2 as a multiple-choice question. The reader six months later sees one line in `git log --oneline` and needs to know whether this is the commit they are looking for. A good message states what the change does, in words they would search for, and keeps anything surprising visible: here, that duplicates are dropped in order (`dict.fromkeys` keeps the first occurrence, which the tests from `e1b96de` pin). Option c is the demo's real message. The diff is a refactoring, but the word "Refactor" alone tells the reader nothing the diff does not.
""",
    7, "expense-tracker d3df52b, e1b96de; S8 slide 16; S4 slide 25", "teacher-variant", "run", variant_of=8,
))

questions.append(open_q(
    32, "beyond", ["read-diff", "compare", "judgement"],
    """
Back to sample Q8's change: `load_expenses` now raises `ValueError` when any amount is negative, with message B, `Reject negative amounts when loading expenses`. The demo project already has this test (commit `d38d9e6`):

```python
def test_a_refund_reduces_its_category_total() -> None:
    expenses = [
        Expense("2025-07-01", "Zara", "clothing", 40.0),
        Expense("2025-07-09", "Zara", "clothing", -15.0),
    ]

    assert total_by_category(expenses, category="", minimum=-100.0) == [("clothing", 25.0)]
```
""",
    [
        part("1", "A user's bank export contains a refund, `Zara,-15.00`. What happens with the new loader, and how does that sit with this test?", 2,
             "The whole file fails: `load_expenses` raises `ValueError`, so the user gets no report at all. Yet the test shows the team decided a refund is a negative amount that reduces its category. The loader now rejects data the core was built to handle.",
             [
                 "Says the whole file is rejected with `ValueError` (no report at all), not just the refund row",
                 "Spots the contradiction: the test shows negative amounts are valid refunds by design",
             ],
             "\"The refund is skipped\" misreads the diff: nothing is skipped, the whole file is refused with `ValueError`. Answers that describe the loader correctly but never connect it to the test miss the second mark: the test shows the team already decided that negative amounts are refunds."),
        part("2", "Message B is clear and specific. Does a good message make it a good change? Explain.", 2,
             "No. A good message makes the decision visible and findable, which is how we spotted the problem; it does not make the decision right. The change still breaks a rule the team agreed.",
             [
                 "Separates the quality of the message (accurate, findable) from the correctness of the change",
                 "Says the change contradicts an agreed rule even though the message describes it well",
             ],
             "\"Yes, B is a good message, so it is a good commit\" confuses documentation with correctness. \"No, B is a bad message\" is also wrong: B is accurate. The mark is for separating the two: the message is good because it makes the decision visible; the decision itself conflicts with the rule."),
        part("3", "What would you do before accepting the change?", 2,
             "Ask the Product Owner what negative amounts mean before merging. If refunds are valid, keep them; then add a loader test: a CSV in `tmp_path` with a refund row loads, and the refund lowers its category's total.",
             [
                 "Checks the rule with the Product Owner or the backlog before merging",
                 "Proposes a test with a refund row that must load (for example in `tmp_path`), with input and expected result stated",
             ],
             "\"Merge it and fix later\" ignores the conflict. \"Delete the refund test\" changes the rule to fit the code. Strong answers check the rule first and name a test with a refund row and its expected result."),
    ],
    """
This is where comparing a diff becomes judging it. Running the sample's loader on a file with `Zara,-15.00` ends in `ValueError: Negative amount in refund.csv`, while the demo's tests already treat `-15.0` as a refund that brings the clothing total to 25.0. Both cannot be the rule. The skills are sample Q8's, one step further: read what the change does for a concrete input, remember that a commit message documents a decision without justifying it, and name the test that would have caught the clash.
""",
    7, "sample Q8; expense-tracker d38d9e6; S4 slides 6–7, 9; S8 slides 11, 20", "teacher-variant", "run", lines="6–8", variant_of=8,
))

# ---------------------------------------------------------------------------
# Variants of Q9 (read tool output)
# ---------------------------------------------------------------------------

questions.append(open_q(
    33, "hard", ["read-tool-output", "judgement"],
    """
Your teammate says "pytest passes on my laptop, so the tests are fine" (`1 passed`). CI is red at the **Types** step, which runs `uv run mypy src tests` with `strict = true`:

```text
src/expense_tracker/report.py:13: error: Function is missing a type annotation  [no-untyped-def]
src/expense_tracker/report.py:20: error: Need type annotation for "totals" (hint: "totals: dict[<type>, <type>] = ...")  [var-annotated]
src/expense_tracker/report.py:35: error: Incompatible types in assignment (expression has type "float", variable has type "int")  [assignment]
src/expense_tracker/report.py:36: error: Item "None" of "Expense | None" has no attribute "merchant"  [union-attr]
src/expense_tracker/report.py:41: error: Call to untyped function "read_expenses" in typed context  [no-untyped-call]
src/expense_tracker/report.py:42: error: Argument 1 to "total_by_category" has incompatible type "str"; expected "list[Expense]"  [arg-type]
tests/test_report.py:4: error: Function is missing a return type annotation  [no-untyped-def]
tests/test_report.py:4: note: Use "-> None" if function does not return a value
Found 7 errors in 2 files (checked 3 source files)
```

Line 13 is `def read_expenses(path):`, line 36 builds the `Largest single expense` line from `largest.merchant`, and line 42 is `totals = total_by_category(path)`.
""",
    [
        part("1", "Sort the seven errors into the three kinds from session 7 (line numbers are enough).", 3,
             "Missing annotation: 13, 20, 41 and the test at line 4. Types disagree: 35 and 42. None not handled: 36.",
             [
                 "Missing annotation: lines 13, 20, 41 and the test at line 4",
                 "Types disagree: lines 35 and 42",
                 "None not handled: line 36",
             ],
             "Sorting by code instead of by kind, or leaving out the test file's error. Line 41 is often missed: \"Call to untyped function\" is still a missing annotation, seen from the caller. Line 35 is sometimes put under None: nothing in its message mentions `None`."),
        part("2", "Two of them can crash the program for a user. Which two, and which one crashes on every run?", 2,
             "Line 42 crashes on every run: it passes the path, a string, where a list is expected, and a character has no `.category` (`AttributeError`). Line 36 crashes only on an empty file, when `largest` is `None`.",
             [
                 "Names line 42 (`arg-type`) and line 36 (`union-attr`) as the crashes",
                 "Says 42 crashes on every call (a string instead of a list) while 36 only on input with no expenses (`None`)",
             ],
             "Naming only line 36, the obvious `None`, misses line 42, which crashes on every call. Naming both without saying which is certain and which depends on the input loses the second mark."),
        part("3", "Why is CI red when pytest passes, and what fixes the error in `tests/`?", 2,
             "pytest runs the tests but does not check types. CI also runs strict mypy on `src` and `tests`, and the test function has no return type. Add `-> None` to it.",
             [
                 "Says pytest does not check types, while CI also runs strict mypy on `src` and `tests`",
                 "Gives the fix: add `-> None` to the test function",
             ],
             "\"CI is broken\" or \"mypy is too strict\" blames the referee. The answer is that pytest and mypy check different things and CI runs both, on `src` and `tests`; the fix is `-> None` on the test."),
        part("4", "Which error do you fix first, and which other error should disappear with it?", 1,
             "The first one, line 13: annotate `read_expenses`. Line 41 is the same problem seen from its caller, so it goes away with it.",
             ["Starts with the first error (line 13) and says line 41 is a consequence of it"],
             "Starting with the scariest-looking error (line 36) instead of the first. Session 7's advice is mechanical on purpose: fix the first, run again. Missing that line 41 depends on line 13 loses the mark."),
    ],
    """
This is sample Q9 at full size, from a real `mypy --strict` run on a broken copy of the demo. The kinds come from the messages: "missing ... annotation", "Need type annotation" and "Call to untyped function" are the first kind; "Incompatible types" and "incompatible type" the second; anything naming `None` the third. Running the code confirms the two crashes: `report_lines` fails on every call with `AttributeError: 'str' object has no attribute 'category'`, and `format_report` with no largest expense fails with `'NoneType' object has no attribute 'merchant'`. Meanwhile pytest reports `1 passed`: tests and types are two different checks, and CI runs both.
""",
    8, "S7 slides 9–11; S8 slide 28; labs/07-refactor.md and labs/08-tdd.md troubleshooting", "teacher-variant", "run", lines="6–8", variant_of=9,
))

questions.append(sort_q(
    34, "exam", ["read-tool-output", "concept"],
    "Sample Q9, part 1, as a sorting exercise, with more errors from real runs. Put each mypy error into the kind of problem it reports.",
    [("missing", "Missing annotation"), ("disagree", "Types disagree"), ("none", "None not handled")],
    [
        ("`src/report.py:8: error: Function is missing a type annotation  [no-untyped-def]`", "missing",
         "mypy does not know the types of this function's parameters or result, so it cannot check how the function is called or what it returns."),
        ("`src/report.py:15: error: Item \"None\" of \"Expense | None\" has no attribute \"category\"  [union-attr]`", "none",
         "The value can be `None`, and the code asks it for `.category`: the crash-at-2-a.m. kind."),
        ("`src/report.py:22: error: Returning Any from function declared to return \"float\"  [no-any-return]`", "disagree",
         "Promised `float`, returns `Any` from something untyped such as `json`. Sample Q9 has one error of each kind, so types disagree is the intended answer, even though lab 07 also allows annotating the variable."),
        ("`tests/test_report.py:4: error: Function is missing a return type annotation  [no-untyped-def]`", "missing",
         "A test function without `-> None`; strict mode wants every function annotated, tests included."),
        ("`src/expense_tracker/report.py:20: error: Need type annotation for \"totals\" (hint: \"totals: dict[<type>, <type>] = ...\")  [var-annotated]`", "missing",
         "An empty `{}` has no type yet; write what it will hold."),
        ("`totals.py:12: error: Missing type arguments for generic type \"dict\"  [type-arg]`", "missing",
         "The hint is there but incomplete: a dict of what to what?"),
        ("`src/expense_tracker/report.py:35: error: Incompatible types in assignment (expression has type \"float\", variable has type \"int\")  [assignment]`", "disagree",
         "Session 7's \"int here, float there\": start the total at `0.0`."),
        ("`src/expense_tracker/report.py:42: error: Argument 1 to \"total_by_category\" has incompatible type \"str\"; expected \"list[Expense]\"  [arg-type]`", "disagree",
         "The caller passes a path where the function wants a list of expenses."),
        ("`src/budget.py:19: error: Unsupported operand types for - (\"float\" and \"None\")  [operator]`", "none",
         "The right side can be `None` (mypy's note says `float | None`), and subtracting `None` crashes."),
    ],
    """
Read the message, not only the code. "Missing ... annotation", "Need type annotation" and "Missing type arguments" are all mypy asking "what type is this?". "Incompatible", "incompatible type" and "Returning Any ... declared to return" are two sides that do not match. Any message that names `None` is the third kind. The first three items are the three lines of sample Q9. In the exam, a phrase per error is enough: the line number and the kind.
""",
    8, "S7 slide 10; labs/07-refactor.md troubleshooting; sample Q9", "teacher-variant", "run", variant_of=9,
))

questions.append(mcq(
    35, "beyond", ["read-diff", "judgement"],
    """
To get CI green before the `v0.5` tag, a teammate pushes this change to `.github/workflows/check.yml` with the message `Fix CI`:

```diff
       - name: Types
-        run: uv run mypy src tests
+        run: uv run mypy src
```

The red errors were all `Function is missing a return type annotation` in `tests/`. What do you do?
""",
    [
        opt("Accept it: test files are not shipped to users, so their types do not matter",
            "Session 7 switched strict on for `src` and `tests` deliberately: \"from now on it enforces strict, tests included\". Type errors in tests hide real mistakes in how they call the code."),
        opt("Accept it until the tag is pushed, then put `tests` back afterwards",
            "The tag is what gets marked, and it would point at a commit whose referee was weakened. A temporary change to the rules is still a change to the rules."),
        opt("Reject it, because mypy needs `--strict` on the command line to check tests",
            "Wrong reason: `strict = true` lives in `pyproject.toml` and applies to whatever mypy is asked to check. The command was fine as it was."),
        opt("Reject it: add `-> None` to each test and keep `mypy src tests`",
            "The errors are the first of session 8's three that bite, and each fix is two words. Changing the referee to match the code is the opposite of a Definition of Done.", True),
    ],
    """
Sample Q9's part 3 asked about `# type: ignore`; this is the same shortcut one level up. Instead of silencing three lines, the teammate stops the referee from looking at a whole folder. The course is explicit: CI runs `mypy src tests`, "from now on it enforces strict, tests included", and every test function needs `-> None`. The partial-submission rubric also requires CI to be green on the tagged commit, and a green check that no longer checks the tests is not the green the Definition of Done means. The honest fix is small and keeps the referee as it was.
""",
    8, "S7 slide 11; S8 slide 28; slides/partial-rubric.txt; expense-tracker 0e05065", "teacher-variant", "source", variant_of=9,
))

# ---------------------------------------------------------------------------
# Exam technique (core)
# ---------------------------------------------------------------------------

questions.append(mcq(
    36, "core", ["concept"],
    "Which statement about the mid-term is true?",
    [
        opt("One question may ask you to write a short function by hand",
            "The teacher is explicit: \"You will not write code.\" Refactoring is asked as \"Describe (in words, do not write code) how you would change it\" (sample Q7.3)."),
        opt("Open answers should fill about a page, to show everything you know",
            "Open questions are answered in 5–8 lines. A page wastes time you need elsewhere and buries the points the rubric looks for."),
        opt("It covers sessions 1–14, including branching and merging",
            "It covers sessions 1–10: starting a project, clean code and tests, the terminal. Git in depth comes in sessions 11–14, after the mid-term."),
        opt("A wrong multiple-choice answer costs nothing, so you answer every one",
            "\"No penalty for wrong.\" A blank is the only guaranteed zero.", True),
    ],
    """
The facts come from the teacher's slide in session 6 and the sample paper: one hour, sessions 1–10, pen and paper, multiple choice with no penalty for a wrong answer, open questions answered in 5–8 lines, and no code writing: "Judgement, not memorised flags." Knowing the format changes how you work: answer every multiple-choice question, keep open answers short and numbered, and spend revision time on reading artefacts rather than on syntax or flags.
""",
    1, "S6 slide 4; moodle/midterm-sample-questions.md", "slides", "source",
))

questions.append(mcq(
    38, "core", ["read-tool-output"],
    """
```text
src/report.py:15: error: Item "None" of "Expense | None" has no attribute "category"  [union-attr]
```

Which reading of this line is correct?
""",
    [
        opt("Line 15 of `src/report.py`; the value may be `None`; search for `union-attr`",
            "Session 7's three parts: where (file and line), what (the message), and the code in brackets to search for.", True),
        opt("Fifteen errors in `src/report.py`; `union-attr` is how severe the error is",
            "The number after the colon is a line number; mypy counts errors in its last line (`Found 3 errors ...`). The code in brackets is a name, not a severity."),
        opt("Column 15 of `src/report.py`; the class `Expense` has no field `category`",
            "mypy prints the line here, not the column. And `Expense` does have `category`: the message is about the `None` half of `Expense | None`."),
        opt("Line 15 of `src/report.py`; mypy could not find the module `report`",
            "A missing module has its own message (`Cannot find implementation or library stub ...`). This one is about an attribute on a value that might be `None`."),
    ],
    """
Session 7, "Reading an error without panic": 1. file and line: where; 2. message: what is wrong, in plain words; 3. `[code]`: what to search for. Here the message says the variable's type is `Expense | None`, and the code uses `.category` without checking which half it got. The `Expense` half has a `category`; the `None` half does not. That makes it the None-not-handled kind, and the fix is a check before the use.
""",
    3, "S7 slides 8–9", "slides", "run",
))

questions.append(mcq(
    39, "exam", ["read-tool-output"],
    """
A teammate changed one comparison in `total_by_category`. The demo's tests now print (trimmed):

```text
____________ test_minimum_keeps_amounts_equal_to_it[10.0-expected2] ____________
>       assert total_by_category(dining, category="", minimum=minimum) == expected
E       AssertionError: assert [] == [('dining', 10.0)]
E
E         Right contains one more item: ('dining', 10.0)

tests/test_report.py:64: AssertionError
=========================== short test summary info ============================
FAILED tests/test_report.py::test_minimum_keeps_amounts_equal_to_it[5.0-expected1]
FAILED tests/test_report.py::test_minimum_keeps_amounts_equal_to_it[10.0-expected2]
2 failed, 22 passed in 0.07s
```

Which reading is correct?
""",
    [
        opt("Two whole test files failed, and the other 22 tests were skipped",
            "`2 failed, 22 passed`: the others ran and passed. Both failures are cases of one test function."),
        opt("Two cases of one test failed; with minimum 10.0 the result was `[]`",
            "The square brackets name the `parametrize` case, and the left side of the `assert` is the result: `[]`, where the test expected `[('dining', 10.0)]`.", True),
        opt("Two cases failed; with minimum 10.0 the result was `[('dining', 10.0)]`",
            "That swaps the sides. The test writes `total_by_category(...) == expected`, so the left value is what the function returned."),
        opt("The test file has an error at line 64, so pytest stopped there",
            "pytest did not stop: it ran 24 tests. Line 64 is the `assert` that failed, not a broken file."),
    ],
    """
Three things to read. The `FAILED` lines: the same test function twice, with the `parametrize` case in square brackets (`5.0` and `10.0`, the cases where an amount equals the minimum). The `E` line: both sides of the `assert` in the test's order, result first: the function returned `[]` and the test expected `[('dining', 10.0)]`. The last line: `2 failed, 22 passed`. Together they point at the boundary: the change turned `<` into `<=`, so an amount exactly equal to the minimum is now dropped. "Read the diff; it usually tells you the bug."
""",
    4, "S8 slides 7, 10–11; expense-tracker d38d9e6", "slides", "run",
))

questions.append(mcq(
    40, "core", ["read-tool-output", "judgement"],
    """
```text
>       assert grand_total([10.10, 20.20]) == 30.30
E       assert 30.299999999999997 == 30.3
E        +  where 30.299999999999997 = grand_total([10.1, 20.2])
```

`grand_total` returns `sum(amounts)`. What is the right fix?
""",
    [
        opt("Compare with `pytest.approx(30.30)` in the test",
            "Floats cannot store most decimals exactly, so `10.10 + 20.20` lands a hair away from `30.30`. Money in floats needs a tolerance, and session 8 uses `pytest.approx`.", True),
        opt("Change the expected value to `30.299999999999997`",
            "It passes today but writes a float accident into the specification: the test now pins a rounding error instead of the rule, and any change to the amounts or to how they are summed breaks it again."),
        opt("Rerun the test, since float errors come and go",
            "Float arithmetic is deterministic: the same sum gives the same `30.299999999999997` every time."),
        opt("Make `grand_total` return a whole number of euros",
            "That throws away the cents, which changes the program's behaviour just to make a test pass."),
    ],
    """
`0.1 + 0.2 == 0.3` is `False` in Python, and so is this comparison: binary floats cannot represent most decimal amounts exactly. The function is right; the comparison is too strict. Session 8: "Floats: compare with approx. Money in floats needs a tolerance." Lab 08's troubleshooting table lists the same symptom (`assert 0.30000000000000004 == 0.3`) with the same fix. Real money code uses `Decimal`, which the slide calls another course.
""",
    4, "S8 slide 8; labs/08-tdd.md troubleshooting", "slides", "run",
))

questions.append(mcq(
    41, "core", ["judgement"],
    "Sample Q7, part 2 asks for two problems a teammate would face when reading, testing or changing the function. Which answer is strongest when it is judged on its reasons, not on its wording?",
    [
        opt("The names are bad, so the function is hard to follow.",
            "One vague opinion with no evidence: which names, and what can a teammate not do because of them? A verdict is not yet a problem."),
        opt("It uses a `for` loop, which is slow, and `float` can lose precision.",
            "Neither is a problem the course raises for this code: a loop over rows is fine, and precision is not what makes it hard to read or test."),
        opt("`r[1]` and `r[2]` hide the amount; the `print` runs on every call, wanted or not.",
            "Two concrete problems, each pointing at the code with its consequence for a teammate: guessing the columns, and a calculation that always writes to the screen, so it cannot be reused in another report without that output.", True),
        opt("There are no comments explaining the code, so nobody knows what it does.",
            "One problem, and it points at the wrong fix: comments that explain what the code does are \"a failure of naming\" (rename instead)."),
    ],
    """
Rubric points are concrete and checkable: they look for the thing in the code and its consequence. Option c names `r[1]` and `r[2]` (a tuple is a missing type, so the reader has to guess which is the amount) and the `print` (computation is not output: every call also prints, so the total cannot be reused quietly and the wording is welded to the arithmetic. A test can still assert on the returned total, so "it cannot be tested" would be the wrong reason). The other three are the typical weak answers: a verdict without evidence (a), problems the course does not care about here (b), and advice that contradicts session 6 (d). The question is marked on reasons, so judge each option by what it points at in the code.
""",
    5, "sample Q7; S6 slides 11, 13, 20, 22", "slides", "source",
))

questions.append(mcq(
    42, "core", ["compare", "judgement"],
    "Sample Q8, part 2, asks which message is better \"from the point of view of someone reading the history six months later\". A is `Fix stuff in loader`; B is `Reject negative amounts when loading expenses`. Which reason for choosing B earns the mark?",
    [
        opt("It names the behaviour that changed, so the log line is enough",
            "That is the six-months reader's need: from `git log --oneline` they can tell this is where negative amounts started being rejected.", True),
        opt("It is longer than A, so it must carry more information",
            "Length is not the point: `Fix the loader so that it is better now` is longer than A and just as empty."),
        opt("It contains the word expenses, which matches the project's name",
            "Matching the project name helps nobody find anything; every commit in the repository is about expenses."),
        opt("It sounds more professional, which matters in a public repository",
            "Tone is a side effect. The mark is for what the reader gains: knowing what changed without opening the diff."),
    ],
    """
The question gives you the criterion: the reader six months later. Answer from that reader's position. They scan one line per commit, often searching for when a behaviour started. B tells them that (negative amounts are rejected at load time); A tells them a fix happened somewhere in a loader. Session 4 showed the demo's history as a list of such lines, each readable without its diff. Reasons such as length or tone may be true, but they do not answer the question asked.
""",
    7, "sample Q8; S4 slide 25", "slides", "source",
))

questions.append(mcq(
    43, "core", ["judgement"],
    "Fifty-two minutes in, you have answered all the multiple choice (two are dotted as unsure) and two of three open questions. The third open question has three parts and is untouched. What is the best use of the last eight minutes?",
    [
        opt("Re-check the two dotted multiple-choice answers, then start the open question",
            "The dotted questions already have an answer, so re-checking can gain little, while three open parts sit at zero."),
        opt("One or two concrete lines on each of the three parts, then the dotted ones",
            "Each part is marked on its own, so a short answer on all three earns more than a perfect answer on one. The dotted questions already have letters.", True),
        opt("Write a full, polished answer to part 1 only, so one part is perfect",
            "Parts 2 and 3 would score zero. Spread before you polish."),
        opt("Rewrite the first two open answers more neatly",
            "Neatness does not score; the untouched parts are the only place left where marks are still at zero."),
    ],
    """
Marks sit in parts, and the first lines of any part are the cheapest marks on the paper: one concrete sentence often earns a rubric point. The two dotted multiple-choice questions already have a letter, so they only gain if you change a wrong letter into a right one. The plan from this section holds: answer everything once, then improve. With eight minutes, that means roughly two minutes per open part and whatever is left for the dotted questions.
""",
    9, "S6 slide 4 (format); moodle/midterm-sample-questions.md", "slides", "reasoning",
))

questions.append(mcq(
    44, "core", ["judgement"],
    "It is the evening before the mid-term. Which plan matches what the teacher said to prepare with?",
    [
        opt("Redo the sample on paper, timed, then walk the demo's history",
            "\"Prepare with the session slides and the expense-tracker history on GitHub\"; \"answer on paper first, then open the answers\".", True),
        opt("Memorise the flags of `ls`, `grep`, `uv` and `pytest`",
            "\"Judgement, not memorised flags.\" A flag may appear in an artefact; you are asked what the command means, not what a letter stands for."),
        opt("Learn branching, merging and pull requests, which come next",
            "That is module 4, sessions 11–14, after the mid-term."),
        opt("Practise writing the expense-tracker's functions from memory",
            "\"You will not write code.\" Reading and judging code is what scores."),
    ],
    """
The teacher's own instructions are short: the session slides, the expense-tracker history on GitHub, and the nine sample questions answered on paper before you look at any answers ("judge your reasons, not the letter"). Each distractor spends the evening on something the paper excludes: flags, code writing, or material after session 10. A good last evening rehearses the three open shapes on real artefacts and the few tables you must apply without thinking.
""",
    9, "S6 slide 4; S8 slide 31; S9 slide 2", "slides", "source",
))

questions.append(sort_q(
    45, "core", ["read-tool-output"],
    "Each line below was printed by one of the course's tools during a real run. Which tool printed it?",
    [("uv", "uv"), ("ruff", "ruff"), ("mypy", "mypy"), ("pytest", "pytest")],
    [
        ("`` error: Failed to parse: `pyproject.toml` ``", "uv",
         "uv's layout: `error: Failed to parse:` with the file name in backticks. ruff (`ruff failed`), mypy and pytest (`ERROR:`) also complain about a broken `pyproject.toml`, each in its own words."),
        ("``error: The lockfile at `uv.lock` needs to be updated, but `--locked` was provided.``", "uv",
         "Only uv knows about `uv.lock` and `--locked`; this is CI's install step failing."),
        ("`` error: Failed to spawn: `expense` ``", "uv",
         "`uv run` could not start a command with that name."),
        ("`` E722 Do not use bare `except` ``", "ruff",
         "A letter-and-number rule code at the start of the line is ruff's layout (session 6 showed `E501` and `F401`)."),
        ("`All checks passed!`", "ruff",
         "ruff's message for a clean run; it says nothing about types or tests."),
        ("`Success: no issues found in 2 source files`", "mypy",
         "mypy's clean run; it counts the source files it checked."),
        ("`src/report.py:22: error: Returning Any from function declared to return \"float\"  [no-any-return]`", "mypy",
         "`file:line: error: message [code]` is mypy's layout."),
        ("`FAILED tests/test_totals.py::test_total_with_discount - assert 90.0 == 95.0`", "pytest",
         "`FAILED path::test_name` followed by the failing `assert`: pytest's summary line."),
        ("`no tests ran in 0.00s`", "pytest",
         "pytest found nothing to collect (exit code 5): the wrong folder, file name or function name."),
    ],
    """
Knowing which tool is talking tells you which file to open. uv talks about `pyproject.toml`, `uv.lock` and commands; ruff starts with a rule code and talks about style and simple mistakes; mypy uses `file:line: error: message [code]` and ends with `Found N errors` or `Success`; pytest talks about tests, `FAILED` lines and counts of passed and failed. All nine lines come from real runs of the course's toolchain.
""",
    3, "S6 slide 27; S7 slide 9; S8 slide 7; labs/01-scaffold.md and labs/08-tdd.md troubleshooting", "slides", "run",
))

# ---------------------------------------------------------------------------
# Added after review: Q7's print-and-return trap, the rubric's check line,
# judging a judgement answer, and what the sample leaves out
# ---------------------------------------------------------------------------

questions.append(mcq(
    46, "hard", ["read-code", "judgement"],
    """
Sample Q7 again:

```python
def process(rows):
    total = 0
    for r in rows:
        if r[2] == "food":
            total += float(r[1])
    print("Food total:", total)
    return total
```

For part 2 a classmate writes: "The `print` means a test cannot check the total." Judge the reason, not the letter. Which comment on that answer is right?
""",
    [
        opt("It is right: pytest refuses to run a function that calls `print`",
            "pytest runs it and captures what it prints; the test passes or fails on the value the function returns."),
        opt("It is right: any function that calls `print` gives back `None`",
            "That is true only when there is no `return`, as in a function that prints instead of returning. Here `return total` hands the number back."),
        opt("It is wrong: a `print` inside a calculation never costs a teammate anything",
            "Computation is not output: every caller gets the line whether it wants it or not, and changing the wording means editing the calculation."),
        opt("It is wrong: the function returns the total, so a test can assert on it",
            "`return total` is still there: `assert process(rows) == 12.5` passes (we ran it: `1 passed`). The real cost is that every call writes to the screen and the wording is welded to the arithmetic.", True),
    ],
    """
Session 8's "You cannot assert on a print" is about a function that prints instead of returning, such as a `largest_expense` that only prints its line and so gives the test `None`. Sample Q7 prints and returns, so its total can be tested. The problem is still real, but its consequence is different: every call writes `Food total: ...` to the screen, so the function cannot be reused quietly (in another report, or in a loop over categories), and the report's wording lives inside the arithmetic. Name that consequence in part 2 and the marker sees that you read the code, not just the pattern.
""",
    6, "sample Q7; S6 slide 20; S8 slide 28", "teacher-variant", "run", variant_of=7,
))

questions.append(mcq(
    47, "hard", ["read-tool-output", "predict-output"],
    """
The partial-submission rubric gives you one line to check yourself before the deadline. You run it on your branch:

```console
$ uv run ruff check . && uv run ruff format --check . && uv run mypy src tests && uv run pytest
All checks passed!
7 files already formatted
tests/test_report.py:67: error: Function is missing a return type annotation  [no-untyped-def]
tests/test_report.py:67: note: Use "-> None" if function does not return a value
Found 1 error in 1 file (checked 6 source files)
$ echo $?
1
```

What can you conclude about the tests?
""",
    [
        opt("pytest ran and passed, since no `FAILED` line appears",
            "No pytest line appears at all: no dots, no `passed` count. Silence here means it never started, not that it passed."),
        opt("ruff failed, since its lines come first in the output",
            "`All checks passed!` and `7 files already formatted` are ruff's two successes; they come first because they ran first."),
        opt("pytest never ran: `&&` only continues after a success",
            "Both ruff commands succeeded and mypy exited with 1, so the chain stopped there. Run on its own, pytest prints `24 passed`.", True),
        opt("The tests fail, so CI will be red at the pytest step",
            "Nothing here ran the tests. CI goes red at the Types step, because it runs `mypy src tests` and the test is missing `-> None`."),
    ],
    """
`cmd1 && cmd2` starts `cmd2` only if `cmd1` exits with 0: session 5's exit code is the number that "the shell, `&&`, CI" all read. Both ruff commands succeeded, mypy found one error and exited with 1, so `pytest` was never started, and the whole line's status is 1 (`echo $?`). Run alone on the same branch, pytest prints `24 passed`: tests and types are separate checks, the first of session 8's "three that will bite". That is why the rubric chains them: the line succeeds only if every check does, which is what CI must show at the `v0.5` tag. The fix is `-> None` on line 67, then run the line again.
""",
    8, "slides/partial-rubric.txt (check yourself before the deadline); S5 slide 9; S8 slide 28", "slides", "run",
))

questions.append(mcq(
    48, "core", ["judgement"],
    "Sample Q9, part 3: your teammate proposes silencing all three errors with `# type: ignore` \"to get CI green\". Which answer judges the reason, not the letter, best?",
    [
        opt("No: ignore comments are not allowed in a public repository.",
            "An invented rule: nothing in the course says so. A \"no\" needs the reason, which is that the ignore hides the `None` crash on line 15 without fixing it."),
        opt("Yes, for now: CI must be green at the tag, and the ignores can go later.",
            "A green tick on code that still crashes is the referee misleading the whole group, and the tag is what gets marked."),
        opt("No: change the CI step to `mypy src`, so only the program is checked.",
            "Right verdict, wrong fix: all three errors are in `src/report.py`, so `mypy src` still reports them. Narrowing the referee is the same shortcut one level up."),
        opt("No: the line 15 crash survives the ignore; fix the `None`, hints and `Any`.",
            "Verdict, reason and real fix in one line: the ignore hides a crash on an empty list, and each of the three causes has a small fix.", True),
    ],
    """
Judgement parts are judged on the reason, not on the yes or no. Write the verdict first, then the reason in the course's terms, then what you would do instead. Option d does all three in one line: no; the crash on line 15 is still there behind a green tick; fix each cause. Option a gives a verdict without a reason, b gives the wrong verdict, and c gives the right verdict with a fix that does not even work, since every error is in `src`.
""",
    5, "sample Q9 part 3; S7 slides 8, 10; moodle/project-pages.md", "slides", "source",
))

questions.append(mcq(
    49, "core", ["judgement"],
    "None of the nine sample questions is about Scrum, Waterfall or the Agile Manifesto. What should you conclude?",
    [
        opt("Revise them anyway: the sample's topics are not a full list",
            "The paper covers sessions 1–10. The sample shows \"the kind of question, not the exam\", and its topics \"are not a full list of what is covered\".", True),
        opt("They are not examined, since none of the nine questions uses them",
            "That reads the sample as a syllabus. Sessions 2 and 4 are inside sessions 1–10, and the sample only had nine slots."),
        opt("They can appear in open questions only, never in multiple choice",
            "Nothing ties a topic to a question type; any session can supply the scenario for a multiple-choice question."),
        opt("Only the parts the group project uses, such as the backlog, can appear",
            "The paper covers the sessions, and session 4 taught Scrum's roles, artifacts, events and time-boxes, not only the parts your project uses."),
    ],
    """
The teacher's words settle it: the sample shows "the kind of question, not the exam", and "the topics are not a full list of what is covered". The nine questions draw almost entirely on sessions 3–10, so the lifecycle (session 1), Waterfall and Agile (session 2), Scrum (session 4) and paths and permissions (session 9) are in scope but not rehearsed here. Revise them with their own modules and expect the same shape: a scenario, an artefact and a judgement.
""",
    9, "moodle/midterm-sample-questions.md; S8 slide 31; S6 slide 4; S1 slides 15, 19; S2 slide 11; S4 slides 3–11", "slides", "source",
))

questions.sort(key=lambda q: q["id"])

questions.append(mcq(
    50, "exam", ["read-tool-output", "judgement"],
    """
Sample Q1's shape with a different uv message. Alice opens a new terminal and types:

```console
$ pwd
/home/alice
$ uv sync
error: No `pyproject.toml` found in current directory or any parent directory
```

What should she do next?
""",
    [
        opt("Run `uv init` to create the `pyproject.toml` that uv is asking for",
            "That creates a new, empty project in her home folder. The project she wants already has its own `pyproject.toml`, somewhere else."),
        opt("Go to the cloned project folder, the one that holds `pyproject.toml`, and run it again",
            "The message says uv looked in the current folder and its parents. `pwd` shows she is in `/home/alice`, not in the clone, so she changes folder first.", True),
        opt("Run `uv lock`, which generates the project files that are missing",
            "`uv lock` needs a `pyproject.toml` too: in the same folder it prints the same error. We ran both commands."),
        opt("Reinstall uv, because it cannot find its own project file",
            "uv is working: it ran, read the folder and told her what it found. Reinstalling it changes nothing about where she stands."),
    ],
    """
Decide what the output names before reading the options. It names a file, `pyproject.toml`, and a place, the current directory and its parents. The `pwd` line shows the current directory, `/home/alice`, which is not the clone. The fix acts on the place the message names. The wrong options act on something it never mentions: creating a new project, generating a lockfile, reinstalling the tool. We ran `uv sync` and `uv lock` in a folder without a project, and both printed the same error. The same habit works in the exam: find the clue in the artefact (here the `pwd` line) and cross out the options that act somewhere else.
""",
    2, "S4 slides 19-23; moodle/midterm-sample-questions.md Q1; run in calibration-fix/outside", "teacher-variant", "run", variant_of=1,
))

module: dict[str, Any] = {
    "id": MID,
    "order": 12,
    "module": "X",
    "title": "The teacher's sample paper, solved and extended",
    "sessions": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "predicted": False,
    "sources": [
        "moodle/midterm-sample-questions.md",
        "moodle/session6-midterm-slide.md",
        "slides-session-1",
        "slides-session-2",
        "slides-session-3",
        "slides-session-4",
        "slides-session-5",
        "slides-session-6",
        "slides-session-7",
        "slides-session-8",
        "slides-session-9",
        "labs/00-setup.md",
        "labs/01-scaffold.md",
        "labs/07-refactor.md",
        "labs/08-tdd.md",
        "moodle/project-pages.md",
        "slides/partial-rubric.txt",
        "expense-tracker v0.0..v0.4",
    ],
    "summary_md": md("""
This module takes the teacher's nine sample questions, answers each one fully, and explains what it really tests, where the trap is and how the teacher could make it harder within his own limits. Each original then gets two or three variants, most of them built from real runs of the course's tools: the same idea at its worst, and one small step beyond. The sections teach exam technique for this paper: how it works, how to answer multiple choice with no penalty, how to read tool output fast, how to write a 5–8 line answer, the three open-question shapes, and a plan for the hour and for the night before.
"""),
    "exam_focus_md": md("""
- The real paper keeps the sample's shapes: a scenario, an artefact (uv, mypy, ruff or pytest output, a shell pipeline, code, a diff) and a judgement.
- Multiple choice asks what to do next, what you can conclude, which fix is right or what a command prints; the distractors are careless moves.
- Open questions come in three shapes: read code and say what is wrong, compare a diff and two commit messages, read tool output and judge a shortcut.
- Answers are judged on reasons, in the course's terms: refactoring keeps behaviour; one function, one job; computation is not output; the three kinds of mypy error.
- Expect worse artefacts than the sample: longer logs, noisier pytest output, real commits from the expense-tracker history.
- No code writing, no flag recall, no syntax tricks: you describe changes in words.
"""),
    "sections": sections,
    "terms": [
        {"term": t, "definition_md": d, "section_ref": sid(s)} for t, d, s in terms
    ],
    "traps": traps,
    "flashcards": [
        {
            "id": f"{MID}-f{i:02d}",
            "front_md": front,
            "back_md": back,
            "kind": kind,
            "section_ref": sid(s),
        }
        for i, (front, back, kind, s) in enumerate(cards, start=1)
    ],
    "questions": questions,
}

with OUT.open("w", encoding="utf-8") as f:
    json.dump(module, f, ensure_ascii=False, indent=1)
    f.write("\n")

print(f"wrote {OUT} ({len(questions)} questions)")
