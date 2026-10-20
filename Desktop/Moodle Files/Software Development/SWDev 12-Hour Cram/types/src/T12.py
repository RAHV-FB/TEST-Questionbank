"""Generator for CRAM/types/T12.json: Writing the open answers.

The sample questions (Q7, Q8, Q9) are copied from the teacher's document
(SITE/sources/moodle/midterm-sample-questions.md). Tool output, commit messages and
the mypy lines come from the verified question bank (SITE/content/sample-paper.json,
history.json) or from the session 6 and 7 slides. Nothing is invented. The asserts at the
bottom check every copied line against its source before the file is written.
"""

import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CRAM = HERE.parent.parent
SITE = CRAM.parent / "study-site"
OUT = HERE.parent / "T12.json"

# ---------------------------------------------------------------------------------------------
# Basics
# ---------------------------------------------------------------------------------------------

B1 = r"""The teacher describes the open questions in one line: you "explain, compare, or read a piece of code or tool output and say what it does or what is wrong". You do not write code. Each question is answered in 5–8 lines, about 60–120 words for the whole question, not per part.

The sample splits every open question into three numbered parts. The marks are most likely set per part, so a marker looks for each part's points under that part's number. The first rule is structural: write "1.", "2.", "3." in the margin and answer each part on its own.

The second rule is to do exactly what the verb in the part asks.

| The part says | You write |
|---|---|
| In one sentence, what does it do? | one sentence: which input, what it computes, what comes out or is printed |
| Name two problems | two, kept apart, each with its consequence |
| Describe in words how you would change it | one change per problem, saying which problem it solves |
| Which is better, and why? | the choice, then the reason from the reader's position |
| Do you accept? | yes or no, the reason in the course's terms, the real fix |
| Name one test | the input, the action, the expected result |

The third rule earns the marks. For every problem give the place in the code, the consequence for a teammate, and the change.

| Weak | Strong |
|---|---|
| The names are bad. | `r[1]` and `r[2]` do not say which field is the amount, so a teammate must guess. |
| It could be better. | The `print` sits inside the calculation, so every call writes to the screen. |

The weak column is an opinion. The strong column points at a line and says what it costs, which is what a rubric checks. Last, spread before you polish: one concrete line on every part beats a perfect answer to one part and two blanks."""

B2 = r"""You get a short function and three tasks: say what it does, name the problems, describe the change. The problems come from sessions 6 and 7, so check the code against this list, top to bottom.

| Look for | The course's words | Consequence for a teammate |
|---|---|---|
| `d`, `t`, `x`, `process`, `calc` | a name that needs a comment is not finished | they must trace the code to learn what a thing holds or returns |
| `r[1]`, `e[3]` | a tuple is a missing type | nobody can tell what position 3 is |
| `print` beside a calculation | computation is not output | every call writes to the screen and the wording is welded to the arithmetic |
| reads, calculates and prints | one function, one job | to test one job you must run them all |
| `5`, `40`, `"food"` inside the code | magic number | a rule change means hunting through the code |
| no type hints | type hints are contracts | mypy and the editor cannot help |
| bare `except:`, `return -1` | failing well | a bug becomes a silent wrong answer |

Each problem needs a change in words, and the change must name the problem it solves:

| Problem | Change, in words |
|---|---|
| positions and vague names | an `Expense` dataclass with named fields, and a name that says what the function returns |
| `print` inside the calculation | return the value and let the CLI print it |
| magic value | a named constant |
| bare `except` and `-1` | raise in the core; the shell prints on stderr and exits non-zero |

Two cautions. `ruff check` prints `All checks passed!` on a function like sample Q7, so "ruff is happy" is no argument: a linter checks style and simple mistakes, not design. And two problems named precisely beat seven named vaguely."""

B3 = r"""You get a diff and two candidate messages. Three parts follow: what the change does, which message is better, which test you would add.

**Reading the diff.** A line starting with `-` was removed, `+` was added, and a space is unchanged context. Read the removed and added lines as a pair: what did the code do before, and what does it do now? Answer in behaviour, for a concrete input: "a file with a negative amount now raises `ValueError`; files without one load as before". Then ask whether the output changed. Session 7's rule: if the output changes, it was not a refactoring.

**Choosing the message.** Take the position of the reader six months later, scanning `git log --oneline`. They see one line per commit. A good message says what the change does, in words they would search for. These are real messages from the expense-tracker history:

```text
5e9466d Replace magic numbers with named constants
f3bb801 Rename calculate_totals to total_by_category
bc9ef3d Add an add command that writes to data/
0e05065 Run ruff, mypy and pytest on every push
```

`Fix stuff in loader`, `Refactor` and `WIP` tell that reader nothing the diff would not. Longer is not the reason, and neither is "more professional". The reason is what the reader learns without opening the diff.

**Naming a test, in words.** Give three things: the input, the action and the expected result. For example: a CSV with one negative amount in `tmp_path`; call `load_expenses`; it raises `ValueError`. Pick the edge the change created: empty, zero, negative, duplicate or missing. "Test that it works" names none of the three."""

B4 = r"""You get a log and three jobs: sort the errors, find the one that can crash, judge a shortcut. Every tool line tells you where, what, and a name to search for. Session 7 teaches the reading on mypy (slide 9). Here it is on a line from sample Q9:

```text
src/report.py:15: error: Item "None" of "Expense | None" has no attribute "category"  [union-attr]
```

`src/report.py:15` is where. The message is what: the value can be `None` and the code asks it for `.category`. `[union-attr]` is the name to search for. Read the first error, fix it, run again.

Session 7 sorts every mypy error into three kinds:

| Kind | mypy is asking | Fix |
|---|---|---|
| Missing annotation | "what type is this?" | write the hint |
| Types disagree | "int here, float there" | make them agree |
| None not handled | "this can be missing" | check it, or change the type |

Read the message, not only the code. Anything that names `None` is the third kind, and it is the one that crashes for a user: "Empty list → None → crash at 2 a.m." A missing annotation crashes nothing by itself; it means mypy cannot check that function.

**The shortcut question.** A teammate wants CI green and proposes `# type: ignore`, changing a type to `Any`, `strict = false`, or checking `src` only. The answer has one shape: verdict, reason, real fix. "No. The ignore hides the crash on an empty list, and CI is the referee the whole group relies on. Check for `None` before using the value." The shortcut makes the referee quiet, not the code correct.

A failing test line works the same way. `assert 90.0 == 95.0` says the code and the test disagree. It does not say which one is right: the specification decides."""

# ---------------------------------------------------------------------------------------------
# Quick checks
# ---------------------------------------------------------------------------------------------

C1_Q = r"""This is the slide 8 function from session 6. Part 2 of an open question asks: *Name two problems a teammate would face when reading, testing or changing it.* Which of these is a point a marker can tick?

```python
def calc(c, i, d):
    t = 0
    for p in c:
        t += p[1] * p[2]
    if d > 0:
        t = t - (t * d)
    if i > 0:
        t = t + (t * i)
    return t
```"""

C4_Q = r"""A commit adds a `--month` option to the `report` command, with its test. Which message serves a reader scanning `git log --oneline` six months later?"""

C5_Q = r"""Four lines from different `mypy --strict` runs. Which one points at a bug that can crash the program for a real user?"""

C0_Q = r"""This is the clean version from session 6, slide 9. Part 1 of an open question asks: *In one sentence, what does this function do?* Which answer earns the mark?

```python
def invoice_total(lines, tax_rate, discount_rate):
    subtotal = 0
    for line in lines:
        subtotal += line.price * line.quantity
    discounted = subtotal * (1 - discount_rate)
    return discounted * (1 + tax_rate)
```"""

CHECKS: list[dict[str, Any]] = [
    {
        "id": "T12-c1",
        "q_md": C0_Q,
        "options": [
            "It is a function that calculates things for an invoice.",
            "It adds up price times quantity for the lines, applies the discount rate and then the tax rate, and returns the result.",
            "First it sets the subtotal to 0. Then it loops over the lines. Then it adds price times quantity. Then it applies the discount. Then it applies the tax.",
            "The names are clear and nothing is printed, which makes it easy to test.",
        ],
        "answer": 1,
        "why_md": "One sentence with the three facts: what goes in, what is computed, what comes out. The first option is one sentence but says nothing. The third walks through the lines in five sentences. The fourth judges the code, which a different part would ask for.",
    },
    {
        "id": "T12-c2",
        "q_md": C1_Q,
        "options": [
            "The code is not clean enough for a business project.",
            "It uses a `for` loop, which is slow.",
            "`c`, `i`, `d` and `p[1]` say nothing about what they hold, so a teammate must trace the code to find the tax rate.",
            "There are no comments, so nobody knows what it does.",
        ],
        "answer": 2,
        "why_md": "The third option points at the code and gives the cost for a teammate. The first is an opinion with no evidence, a loop over lines is fine here, and a comment that explains what code does is a failure of naming: rename instead.",
    },
    {
        "id": "T12-c3",
        "q_md": "A function uses `e[3]` and `row[2]` throughout. Which of the course's phrases names the problem?",
        "options": [
            "Computation is not output.",
            "A tuple is a missing type.",
            "Fail loudly at the boundary.",
            "The referee, not the judge.",
        ],
        "answer": 1,
        "why_md": "`e[3]` says nothing about what it holds. An `Expense` dataclass with named fields turns it into `expense.amount`. The other three phrases are about printing, errors and CI.",
    },
    {
        "id": "T12-c4",
        "q_md": C4_Q,
        "options": [
            "Update cli.py",
            "More work on reports",
            "Changes from Tuesday",
            "Add a --month option to the report command",
        ],
        "answer": 3,
        "why_md": "It says what the change does, in words someone would search for, and it names the option as the user types it. The others name a file, a vague area or a day, and the reader learns nothing without opening the diff.",
    },
    {
        "id": "T12-c5",
        "q_md": C5_Q,
        "options": [
            "`src/report.py:8: error: Function is missing a type annotation  [no-untyped-def]`",
            "`src/budget.py:19: error: Unsupported operand types for - (\"float\" and \"None\")  [operator]`",
            "`totals.py:12: error: Missing type arguments for generic type \"dict\"  [type-arg]`",
            "`src/expense_tracker/report.py:20: error: Need type annotation for \"totals\" (hint: \"totals: dict[<type>, <type>] = ...\")  [var-annotated]`",
        ],
        "answer": 1,
        "why_md": "The right side can be `None`, and subtracting `None` raises an error at run time: the None-not-handled kind. The other three are the missing-annotation kind, where mypy asks 'what type is this?' and nothing crashes by itself.",
    },
]

# ---------------------------------------------------------------------------------------------
# Method
# ---------------------------------------------------------------------------------------------

METHOD = [
    "**Skim every part first.** Count the numbered parts and read each verb: *one sentence*, *name two*, *describe in words*, *which is better*, *do you accept*. The verb sets the shape of the lines you write. The paper's exact mix is not published; with three open questions, plan about 8–9 minutes each.",
    "**Read the artefact once and say it in a sentence.** For code: what goes in, what happens, what comes out or is printed. For a diff: the before and the after as a pair. For tool output: which tool, which file and line, which kind of problem.",
    "**Put the part numbers in the margin and answer in order.** One to three lines per part, exactly what the verb asks. Number the problems inside a part as (a) and (b) so the marker can find each one.",
    "**For every problem give three things:** the place in the code, the consequence for a teammate, the change in words with the problem it solves. For a judgement part: verdict first, then the reason in the course's terms, then the real fix.",
    "**Write the course's phrases and no code.** \"A tuple is a missing type\", \"computation is not output\", \"the referee, not the judge\". Name an identifier if it helps (`r[1]`, `total_by_category`), never a block of code, and never a flag to be recalled.",
    "**Spread before you polish.** If a part is stuck, write the one concrete line you have and move on. In the last two minutes check that every part has at least one line.",
]

# ---------------------------------------------------------------------------------------------
# Worked examples (the teacher's Q7 and Q9, verbatim)
# ---------------------------------------------------------------------------------------------

Q7_QUESTION = r"""**Q7. Read code and say what is wrong**

```python
def process(rows):
    total = 0
    for r in rows:
        if r[2] == "food":
            total += float(r[1])
    print("Food total:", total)
    return total
```

1. In one sentence, what does this function do?
2. Name two problems a teammate would face when reading, testing or changing it.
3. Describe (in words, do not write code) how you would change it, and which of the two problems each change solves."""

Q7_STEPS = [
    "Read the verbs before the code. Part 1 is *one sentence*. Part 2 is *two* problems, about reading, testing or changing. Part 3 is *in words, do not write code*, and each change must say which problem it solves. Three numbered parts, so three numbered blocks of lines.",
    "Read the code once and say it aloud. It loops over `rows`, keeps the rows whose third field is `\"food\"`, adds up the second field as a float, prints the total and returns it. Notice the last two verbs together: it prints and it returns.",
    "Part 1: one sentence with three facts. Which rows (the food ones), what it adds up (the amounts), what it does with the result (prints and returns).",
    "Part 2: run down the course's list: names, positions, `print`, jobs, magic values, hints, failure. Pick the two with the clearest cost for a teammate. `r[1]`, `r[2]` and `process` hide what the data is. The `print` writes to the screen on every call. Skip \"a test cannot check it\": the function returns the total, so a test can assert on it.",
    "Part 3: one change per problem, in words, each linked to its problem. A dataclass with named fields and a name that says what it returns solve the reading problem. Returning only, and letting the CLI print, solves the output problem.",
    "Count the lines. This answer is about seven. Stop when each part has its point.",
]

Q7_ANSWER = r"""1. It adds up the amounts of the rows whose third field is `"food"`, prints that total and returns it.

2. (a) `r[1]`, `r[2]` and the name `process` do not say what they hold, so a teammate has to guess which field is the amount (a tuple is a missing type). (b) The `print` is inside the calculation, so every call writes to the screen and the wording is welded to the arithmetic (computation is not output).

3. An `Expense` dataclass with named fields, so `r[1]` becomes `expense.amount`, and a name such as `food_total`: this solves (a). Return only the total and let the CLI print the line: this solves (b).

*Why it scores:* one sentence with three facts; two problems that each point at the code and give a consequence; two changes, each tied to its problem. About 105 words, seven or eight handwritten lines."""

Q9_QUESTION = r"""**Q9. Read tool output (harder)**

You run `uv run mypy --strict src` on a teammate's branch:

```text
src/report.py:8: error: Function is missing a type annotation  [no-untyped-def]
src/report.py:15: error: Item "None" of "Expense | None" has no attribute "category"  [union-attr]
src/report.py:22: error: Returning Any from function declared to return "float"  [no-any-return]
```

1. Sort the three errors into the kinds we discussed in session 7.
2. Which one points to a bug that could crash the program for a real user, and why?
3. Your teammate proposes silencing all three with `# type: ignore` "to get CI green". Do you accept? Give your reasoning."""

Q9_STEPS = [
    "Read the three parts first: *sort* by the kinds from session 7, *which can crash* and why, *do you accept* with reasoning. The last two are judgements, so each needs a reason, not only a line number or a yes.",
    "Part 1: read the message, not only the code. Line 8 says *missing a type annotation*: missing annotation. Line 15 names `None`: None not handled. Line 22 says the function is *declared to return* `float` but returns `Any`: types disagree, because the promise and the value do not match. One phrase per line is enough.",
    "Part 2: only the `None` line crashes by itself. Give the mechanism: the value is `None` when nothing is found, for example an empty list, and asking `None` for `.category` raises `AttributeError`. A missing annotation and an `Any` mean mypy cannot check something; they crash nothing.",
    "Part 3: verdict, reason, real fix. No: `# type: ignore` silences mypy but the crash on line 15 stays. CI is the shared referee, and a green tick on code that still crashes misleads the whole group. Then name the fix for each cause.",
    "If time is short, write the three kinds, the crash line with its mechanism, and the verdict with one reason. That is a point in every part.",
]

Q9_ANSWER = r"""1. Line 8: missing annotation. Line 15: None not handled. Line 22: types disagree (the function promises a `float` but returns `Any`).

2. Line 15. The value can be `None`, for example for an empty list, and asking `None` for `.category` raises `AttributeError`, which stops the program for a real user. The other two only mean mypy cannot check something.

3. No. `# type: ignore` silences mypy, but line 15 still crashes on an empty list, now behind a green tick from the shared referee. I would fix the causes: add the hints (line 8), check for `None` before using the value (line 15), convert with `float(...)` (line 22).

*Why it scores:* each part has a verdict and a reason in the course's terms. About 110 words, seven handwritten lines."""

WORKED = [
    {
        "title": "Sample Q7: read code and say what is wrong",
        "question_md": Q7_QUESTION,
        "steps_md": Q7_STEPS,
        "answer_md": Q7_ANSWER,
    },
    {
        "title": "Sample Q9: read tool output and judge a shortcut",
        "question_md": Q9_QUESTION,
        "steps_md": Q9_STEPS,
        "answer_md": Q9_ANSWER,
    },
]

# ---------------------------------------------------------------------------------------------
# Twists, traps, phrases
# ---------------------------------------------------------------------------------------------

TWISTS = [
    {
        "twist_md": "A longer function with three problems, one of which only shows when you run it (sample Q7 made harder).",
        "how_md": "After the names, the positions and the `print`, ask the edge questions: what does an empty input do, a zero, a negative, a duplicate, a missing value? A division by a count or by a sum of weights is the usual suspect, because it raises `ZeroDivisionError` on an empty list. Name the input that crashes it and say what you would decide for that case: raise in the core and let the shell report it. A width or a rate written into the code is a magic number: a named constant.",
    },
    {
        "twist_md": "Failing well inside the code: a bare `except:` that returns a sentinel such as `-1`, in a function whose results are added up or compared later.",
        "how_md": "Say what the sentinel does downstream. It is treated as a real value, so the total is silently wrong, with no error and no exit code. A bare `except` also hides every other bug, such as a misspelt key. The change, in words: remove the bare `except` and the sentinel; treat a normal \"no result\" as `None` or empty, with an honest type; raise for bad input in the core; the shell prints on stderr and exits non-zero.",
    },
    {
        "twist_md": "A diff that looks like a pure refactoring, with the question \"Is it a refactoring? Name the one thing a user or a script could notice.\"",
        "how_md": "Compare what a user or a script can see before and after: the printed report, the exit code, and which stream (stdout or stderr) each message uses. If all three match, it is a refactoring. If one differs, answer \"almost\" and name that one difference. Redirecting with `>` and `2>` makes the streams visible.",
    },
    {
        "twist_md": "A good message on a doubtful change: the new code refuses an input that an existing test accepts.",
        "how_md": "Separate the message from the change. A good message makes the decision visible and findable; it does not make the decision right. Say what happens to a real input that is now refused, point at the test or rule it conflicts with, and say you would settle with the team what is intended before merging. Then name a test for the input that must keep working.",
    },
    {
        "twist_md": "A real mypy log of six or seven errors across `src` and `tests`, with a teammate who says \"pytest passes, so the tests are fine\".",
        "how_md": "Sort by the message, not the code: \"missing\" or \"need type annotation\" is the first kind, \"incompatible\" the second, anything naming `None` the third. Read the first error, fix it and run again, because later errors are often the same one repeating (slide 9). pytest runs the code and mypy reads it, so they check different things. CI runs both, on `src` and on `tests`.",
    },
    {
        "twist_md": "A different shortcut for a green CI: `strict = false`, a folder dropped from the mypy command, or `|| true` added to a step.",
        "how_md": "The answer keeps the same shape. No: the referee goes quiet and the code is unchanged. Session 7 switched strict on for `src` and `tests`, tests included, and the real fix is the small change the error asks for. A tag on a commit with a weakened referee is not the green that the Definition of Done means.",
    },
    {
        "twist_md": "A classmate's answer is printed and you must judge the reason, not the letter.",
        "how_md": "Check the claim against the code, not against how it sounds. \"The `print` means a test cannot check the total\" is wrong for sample Q7, because the function also returns the total and a test can assert on it. The real cost of the `print` is output on every call. Name the correct consequence and the marker sees that you read the code.",
    },
]

TRAPS = [
    "**Writing code in part 3.** You will not write code. Describe the change in words and say which problem it solves, for example \"return the total and let the CLI print it\".",
    "**Verdicts without evidence, or many vague problems.** \"The names are bad\" and \"it is not clean\" name no line and no cost. Two problems that point at the code, each with its consequence for a teammate, beat seven vague ones.",
    "**\"A test cannot check the total\" for sample Q7.** The function returns the total, so a test can assert on it. The cost of the `print` is output on every call and wording welded to the arithmetic.",
    "**Choosing the message because it is longer or sounds professional.** The question names the reader: someone six months later scanning `git log --oneline`. Say what the message lets them learn without opening the diff.",
    "**\"Test that it works\" as the test you would add.** Give the input (a CSV with one negative amount), the action (call `load_expenses`) and the expected result (it raises `ValueError`).",
    "**Accepting `# type: ignore` \"just for now\", or refusing with no reason.** Verdict, reason, fix: no, the crash on line 15 is still there behind a green tick, so fix the `None`, the hints and the `Any`.",
    "**Adding comments to cure unclear code.** \"A comment that explains what the code does is a failure of naming.\" Rename instead, and say so.",
    "**Polishing one part and leaving another blank.** Each part is marked on its own. A short concrete line on every part earns more than a perfect answer to one.",
]

SAY_MD = r"""**Any open answer**
- Number every part: "1.", "2.", "3."
- Problem, consequence for a teammate, change in words
- Verdict first, then the reason, then the real fix
- Link each change to its problem: "this solves the reading problem", "this solves the output problem"

**Read the code**
- "A tuple is a missing type": `r[1]` and `r[2]` do not say what they hold
- "Computation is not output": the `print` runs on every call
- "One function, one job": it reads, calculates and prints
- "A name that needs a comment is not finished": rename instead
- "Magic number": a `40` in the middle of the code has no name
- "Type hints are contracts": with none, mypy cannot check it
- "A bare `except` hides every bug"; "do not return `-1` and hope somebody checks"
- Fixes: an `Expense` dataclass with named fields; return the value and let the CLI print; a named constant; raise in the core, and the shell prints on stderr and exits non-zero

**Diffs and commit messages**
- "Change the structure, keep the behaviour: if the output changes, it was not a refactoring"
- "The reader six months later, scanning `git log --oneline`": the message says what changed, in words they would search for
- "A good message makes the decision visible; it does not make it right"
- A test in words: the input, the action, the expected result (a CSV in `tmp_path` with one negative amount; `load_expenses` raises `ValueError`)

**Tool output**
- Where, what, and a name to search for: file and line, message, `[code]`
- Three kinds: missing annotation, types disagree, None not handled
- "Empty list → None → crash at 2 a.m.": the None kind crashes for a user
- "`# type: ignore` makes the referee quiet, not the code correct"
- "The referee, not the judge": CI is shared, and a green tick on code that still crashes misleads the group
- "pytest and mypy check different things; CI runs both"
- A failing test: the code and the test disagree, and the specification decides
"""

PRACTICE = [
    "sample-paper-q43",
    "sample-paper-q41",
    "sample-paper-q34",
    "sample-paper-q08",
    "sample-paper-q39",
    "sample-paper-q28",
    "sample-paper-q33",
    "sample-paper-q35",
    "sample-paper-q29",
    "sample-paper-q32",
]

SHAPE_MD = (
    "Mirrors sample Q7 (read code and say what is wrong), Q8 (compare a diff and two commit messages) "
    "and Q9 (read tool output and judge a shortcut). On the sample paper each is a short scenario with an "
    "artefact and three numbered parts, answered in 5–8 lines with no code."
)

ONE_MD = (
    "Each part is marked on its own reasons: say what the code or output does, name the problem with its "
    "consequence for a teammate, and describe the fix in words."
)

SPOT_MD = r"""- A scenario with an artefact (a short function, a diff with two commit messages, a mypy log), then two to four numbered parts.
- The verbs give it away: *In one sentence, what does this do?*, *Name two problems a teammate would face*, *Describe in words (do not write code) how you would change it*, *Which message is better, and why?*, *Do you accept? Give your reasoning.*
- The paper says "5–8 lines" and "you will not write code". The marks sit in the parts, not in the length.
- It asks for judgement on reasons ("judge your reasons, not the letter"): a verdict is never enough alone.
- The artefact comes from the course: the expense-tracker, its history, the output of `uv`, `ruff`, `mypy` and `pytest`."""

TYPE = {
    "tid": "T12",
    "name": "Writing the open answers",
    "shape_md": SHAPE_MD,
    "minutes": 40,
    "one_md": ONE_MD,
    "spot_md": SPOT_MD,
    "basics": [
        {"id": "T12-b1", "heading": "What an open answer is marked on", "body_md": B1},
        {"id": "T12-b2", "heading": "Shape 1: read code and say what is wrong", "body_md": B2},
        {
            "id": "T12-b3",
            "heading": "Shape 2: compare a diff and two commit messages",
            "body_md": B3,
        },
        {
            "id": "T12-b4",
            "heading": "Shape 3: read tool output and judge a shortcut",
            "body_md": B4,
        },
    ],
    "checks": CHECKS,
    "method": METHOD,
    "worked": WORKED,
    "twists": TWISTS,
    "traps": TRAPS,
    "say_md": SAY_MD,
    "practice": PRACTICE,
}


# ---------------------------------------------------------------------------------------------
# Self-checks against the sources before writing
# ---------------------------------------------------------------------------------------------


def check_sources() -> None:
    sample = (SITE / "sources" / "moodle" / "midterm-sample-questions.md").read_text("utf-8")
    bank = json.loads((SITE / "content" / "sample-paper.json").read_text("utf-8"))
    history = json.loads((SITE / "content" / "history.json").read_text("utf-8"))

    # Q7 and Q9: every line of the verbatim question must be in the teacher's document.
    for block in (Q7_QUESTION, Q9_QUESTION):
        for line in block.splitlines():
            text = line.strip()
            if not text or text.startswith("**Q") or text == "```" or text.startswith("```"):
                continue
            body = text.split(". ", 1)[1] if text[:2] in {"1.", "2.", "3."} else text
            assert body in sample, f"not verbatim: {line!r}"

    # Commit messages shown in B3 are real history subjects.
    subjects = {c["hash"]: c["message"] for c in history["commits"]}
    for line in B3.splitlines():
        if len(line) > 8 and line[7] == " " and line[:7] in subjects:
            assert line[8:] == subjects[line[:7]], line
    assert {"5e9466d", "f3bb801", "bc9ef3d", "0e05065"} <= set(subjects)

    # The mypy lines used in check c5 come from the bank's verified sort question.
    q34 = next(q for q in bank["questions"] if q["id"] == "sample-paper-q34")
    items = {item["text_md"].strip("`") for item in q34["items"]}
    for option in CHECKS[4]["options"]:
        assert option.strip("`") in items, option

    # Practice ids exist in pools.json for T12.
    pools = json.loads((CRAM / "pools.json").read_text("utf-8"))["pools"]["T12"]
    ids = {q["id"] for q in pools}
    missing = [i for i in PRACTICE if i not in ids]
    assert not missing, missing
    assert len(set(PRACTICE)) == len(PRACTICE)


def main() -> None:
    check_sources()
    OUT.write_text(json.dumps(TYPE, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
