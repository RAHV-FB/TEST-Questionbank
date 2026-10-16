"""Generate content/core-shell-failing.json: functional core, imperative shell, and failing well.

Session 7, slides 12-20; expense-tracker commits 04d699f (v0.2) and 15836e1 (between v0.2 and v0.3);
partial-rubric Structure criterion; session 8 slides 17-24.

Run from the study-site folder:
    uv run python content/src/core-shell-failing.py

Every program, tool and shell output shown below was produced by a real run in
$SCRATCH/work/core-shell-failing/ (inputs and raw outputs are kept there), then trimmed.
Runs for the review fixes (q13 re-check, q46, q48, ruff F821/B904, q47 snippet) are in
$SCRATCH/work/core-shell-failing-fix/.
Scratch path prefixes were rewritten to the project-relative paths a student would see.
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path
from typing import Any

MID = "core-shell-failing"
OUT = Path(__file__).resolve().parent.parent / f"{MID}.json"


def T(s: str) -> str:
    """Dedent and strip a Markdown block."""
    return textwrap.dedent(s).strip("\n").rstrip()


def sid(n: int) -> str:
    return f"{MID}-s{n}"


def qid(n: int) -> str:
    return f"{MID}-q{n:02d}"


def fid(n: int) -> str:
    return f"{MID}-f{n:02d}"


Q: list[dict[str, Any]] = []


def mcq(
    n: int,
    level: str,
    skills: list[str],
    section: int,
    source: str,
    origin: str,
    verified: str,
    stem: str,
    correct: tuple[str, str],
    wrong: list[tuple[str, str]],
    pos: str,
    explanation: str,
) -> None:
    assert len(wrong) == 3
    opts: list[dict[str, Any]] = [
        {"text_md": T(t), "correct": False, "why_md": T(w)} for t, w in wrong
    ]
    opts.insert(
        "abcd".index(pos), {"text_md": T(correct[0]), "correct": True, "why_md": T(correct[1])}
    )
    Q.append(
        {
            "id": qid(n),
            "type": "mcq",
            "level": level,
            "skills": skills,
            "stem_md": T(stem),
            "explanation_md": T(explanation),
            "section_ref": sid(section),
            "source_ref": source,
            "origin": origin,
            "verified_by": verified,
            "options": opts,
        }
    )


def part(
    label: str, prompt: str, marks: int, model: str, rubric: list[str], weak: str
) -> dict[str, Any]:
    return {
        "label": label,
        "prompt_md": T(prompt),
        "marks": marks,
        "model_answer_md": T(model),
        "rubric": [T(r) for r in rubric],
        "weak_answers_md": T(weak),
    }


def open_q(
    n: int,
    level: str,
    skills: list[str],
    section: int,
    source: str,
    origin: str,
    verified: str,
    stem: str,
    parts: list[dict[str, Any]],
    explanation: str,
    lines: str,
) -> None:
    Q.append(
        {
            "id": qid(n),
            "type": "open",
            "level": level,
            "skills": skills,
            "stem_md": T(stem),
            "explanation_md": T(explanation),
            "section_ref": sid(section),
            "source_ref": source,
            "origin": origin,
            "verified_by": verified,
            "parts": parts,
            "lines": lines,
        }
    )


def sort_q(
    n: int,
    level: str,
    skills: list[str],
    section: int,
    source: str,
    origin: str,
    verified: str,
    stem: str,
    categories: list[tuple[str, str]],
    items: list[tuple[str, str, str]],
    explanation: str,
) -> None:
    Q.append(
        {
            "id": qid(n),
            "type": "sort",
            "level": level,
            "skills": skills,
            "stem_md": T(stem),
            "explanation_md": T(explanation),
            "section_ref": sid(section),
            "source_ref": source,
            "origin": origin,
            "verified_by": verified,
            "categories": [{"id": c, "label": label} for c, label in categories],
            "items": [{"text_md": T(t), "category": c, "why_md": T(w)} for t, c, w in items],
        }
    )


# ---------------------------------------------------------------------------
# Shared artefacts (all copied from real runs; see the work folder)
# ---------------------------------------------------------------------------

DIAGRAM = """\
```text
        ┌─────────────────────────────┐
        │  shell: cli.py              │   reads files, prints, exits
        │  ┌───────────────────────┐  │
        │  │  core: pure functions │  │   data in → data out
        │  └───────────────────────┘  │
        └─────────────────────────────┘
```"""

# git show 9d6c607 (trimmed: three hunks of report.py; format_report is not shown)
DIFF_9D6C607 = """\
```diff
--- a/src/expense_tracker/report.py
+++ b/src/expense_tracker/report.py
@@ -12,6 +12,17 @@ AMOUNT_WIDTH = 10
 RULE_WIDTH = 40
 
 
+def read_expenses(path):
+    expenses = []
+    with open(path) as handle:
+        reader = csv.reader(handle)
+        next(reader)
+        for row in reader:
+            if len(row) == FIELDS_PER_ROW:
+                expenses.append((row[DATE], row[MERCHANT], row[CATEGORY], float(row[AMOUNT])))
+    return expenses
+
+
 def total_by_category(expenses, category, minimum):
     totals = {}
     for expense in expenses:
@@ -29,45 +40,33 @@ def total_by_category(expenses, category, minimum):
     return ordered
 
 
-def run(path, category, minimum):
-    expenses = []
-    try:
-        f = open(path)
-        reader = csv.reader(f)
-        next(reader)
-        for row in reader:
-            if len(row) == FIELDS_PER_ROW:
-                expenses.append((row[DATE], row[MERCHANT], row[CATEGORY], float(row[AMOUNT])))
-        f.close()
-    except:
-        print("could not read " + path)
-        sys.exit(1)
+def largest_expense(expenses):
+    largest = None
+    for expense in expenses:
+        if largest is None or expense[AMOUNT] > largest[AMOUNT]:
+            largest = expense
+    return largest
 
@@ -76,3 +75,17 @@ def run(path, category, minimum):
             + " for "
             + ("%.2f" % largest[AMOUNT])
         )
+    return lines
+
+
+def run(path, category, minimum):
+    try:
+        expenses = read_expenses(path)
+    except:
+        print("could not read " + path)
+        sys.exit(1)
+
+    totals = total_by_category(expenses, category, minimum)
+    largest = largest_expense(expenses)
+    for line in format_report(path, category, minimum, totals, largest):
+        print(line)
```
"""

# git show 15836e1 (trimmed: the import hunk of cli.py and some context lines)
DIFF_15836E1 = """\
```diff
--- a/src/expense_tracker/cli.py
+++ b/src/expense_tracker/cli.py
@@ -22,7 +27,16 @@ def report(
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
--- a/src/expense_tracker/report.py
+++ b/src/expense_tracker/report.py
@@ -1,5 +1,4 @@
 import csv
-import sys
 from dataclasses import dataclass
@@ -90,16 +89,3 @@ def format_report(
     return lines
-
-
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
```"""

# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------

SECTIONS: list[dict[str, Any]] = []


def section(
    n: int,
    heading: str,
    body: str,
    key_points: list[str],
    exam_note: str,
    source_ref: str,
    check: list[int],
) -> None:
    SECTIONS.append(
        {
            "id": sid(n),
            "heading": heading,
            "body_md": T(body),
            "key_points": [T(k) for k in key_points],
            "exam_note_md": T(exam_note),
            "source_ref": source_ref,
            "check": [qid(c) for c in check],
        }
    )


section(
    1,
    "Where the I/O lives: core and shell",
    """
Every program does two kinds of work. It **decides** things: a total per category, the fee for a parking ticket, whether a student passed. And it **touches the world**: it reads a file, prints to the terminal, ends with an exit code. Session 7 keeps the two apart, in two layers drawn one inside the other:

"""
    + DIAGRAM
    + """

The **functional core** takes values and returns values. No `open`, no `print`, no `sys.exit`. Give it a list of expenses and it hands back a list of totals. It does not know where the list came from or where the answer will go, and it gives the same answer every time it gets the same values. Functions like that are called **pure**: data in, data out.

The **imperative shell** is the only place that touches the world. It reads the input, calls the core, shows what the core returned and decides the exit code. It should be thin: a few lines of calls, very little logic of its own.

What counts as touching the world? Part 2 of lab 07 gives the checklist you used on your own repo: every place your code reads or writes a file, calls `print`, or calls `sys.exit`, and typer's `typer.echo` and `raise typer.Exit` count too. Lab 08 adds the network. Reading the clock counts as well: the demo's `add` command calls `datetime.date.today()` in `cli.py`, the shell, and a core function that read the clock would give a different answer tomorrow for the same arguments. A function that does any of these is shell. A function that only computes from its arguments and returns the result can be core.

The lab asked each group to write that list down, because it is the shell of the project: "next week's tests will want everything else to be pure." If the I/O turns out to be spread across many functions, the lab calls that "a finding, not a failure". Finding it is the first step to fixing it.
""",
    [
        "Core: takes values, returns values. No `open`, no `print`, no `sys.exit`.",
        "Shell: the only place that touches the world (files, the terminal, the exit code). Keep it thin.",
        "`typer.echo` and `raise typer.Exit` are I/O too: they belong in the shell.",
        "Quick test for core: could a test call it with values typed into the test and check what it returns?",
    ],
    "Expect to sort functions (or single lines) into core and shell, or to spot the one `print` or `open` hiding inside a function that should be pure.",
    "S7 slides 12–13; labs/07-refactor.md Part 2 step 3; labs/08-tdd.md step 1",
    [1, 2],
)

section(
    2,
    "The demo: four lines, two layers",
    """
The expense-tracker shows the split in a handful of lines. This is slide 14, the `report` command at v0.3:

```python
expenses = read_expenses(path)                       # shell: touches a file
totals = total_by_category(expenses, category, minimum)   # core: pure
lines = format_report(path, category, minimum, totals, largest)  # core: pure
for line in lines:
    print(line)                                      # shell: prints
```

Read it top to bottom. The shell fetches data from the world: `read_expenses` opens the CSV and turns each row into an `Expense`. It hands plain values to the core: `total_by_category` takes the list and returns `(category, total)` pairs, and `format_report` turns the totals into the report's lines and returns them without printing. Only then does the shell touch the world again: the loop prints. (The repo's loop calls `typer.echo(line)`, typer's version of `print`, and the slide leaves out one more pure call, `largest = largest_expense(expenses)`.)

The slide's key sentence: `total_by_category` does not know that a CSV exists. Give it a list and it works. The list could come from a CSV file, a database, a web form or a test that types three `Expense` objects by hand. The function cannot tell the difference, and that is the point.

How the demo got here:

- **v0.1**: one `run()` did five jobs: opened and parsed the file, handled the failure, printed the header, totalled by category, found the largest and printed it (session 6).
- **`9d6c607`** "Separate reading and printing from the calculation": `read_expenses`, `largest_expense` and `format_report` appear beside the existing `total_by_category`, and a short `run()` reads, calls and prints.
- **v0.2**: that `run()` still lives in `report.py` and still calls `print` and `sys.exit(1)`.
- **`15836e1`** "Move printing and exiting out of the report module": the reading, printing and exiting move into the `report` command in `cli.py`. The next commit switches on strict type checking, and the tag v0.3 marks both: "Functional core, imperative shell, strict types". Since then `report.py` has no `print` and no `sys.exit`.

One detail to read carefully: `read_expenses` is still defined in `report.py`, yet slide 14 labels it shell, because it opens a file. Core or shell is decided by what a function does, not by the file it lives in.
""",
    [
        "Shell reads, core computes and formats, shell prints: in that order.",
        "`total_by_category` does not know that a CSV exists. Give it a list and it works.",
        "`format_report` returns lines; it does not print them. Computation is not output.",
        "Core or shell is decided by what a function does, not by the file it lives in.",
    ],
    "A likely artefact: these lines, or the v0.2 → v0.3 diff, with the question 'which lines touch the world?' or 'what moved, and why?'.",
    "S7 slide 14; expense-tracker 9d6c607, 04d699f, 15836e1; S6 slide 18",
    [3, 4],
)

section(
    3,
    "Why we care: testable, reusable, replaceable",
    """
Slide 15 gives three reasons for the split.

**Testable.** You test a core function by passing a list and checking the answer: no file, no setup, no clean-up. Session 8 called it "pure functions test themselves", and its first test does just that:

```python
def test_totals_are_grouped_by_category() -> None:
    expenses = [
        Expense("2025-07-01", "Bar Ramon", "dining", 10.0),
        Expense("2025-07-02", "Zara", "clothing", 40.0),
        Expense("2025-07-03", "Bar Ramon", "dining", 5.0),
    ]
    result = total_by_category(expenses, category="", minimum=0.0)
    assert result == [("clothing", 40.0), ("dining", 15.0)]
```

A function that prints its answer instead of returning it can only be looked at. Its result is `None`, and session 8's "three that will bite" puts it plainly: you cannot assert on a `print`. Make it return, and print in the shell. If a function you want to test needs a file, ask: can I split the file reading out?

**Reusable.** The same core can serve a CLI today and a web page later. The web page brings its own shell (read a form, show a page) and calls the same `total_by_category`.

**Replaceable.** In session 17 the data moves into a database. Only the shell's reading changes: something that queries the database and still returns a `list[Expense]`. The core, and every test of the core, stay as they are.

The shell still deserves a test or two, but they are the expensive kind. Session 8's 2×2 diagram rates code by the benefit of unit-testing it (how non-obvious it is) against the cost (how many dependencies it has):

| | Few dependencies (cheap to test) | Many dependencies (expensive to test) |
|---|---|---|
| Non-obvious code (high benefit) | **Algorithms**: pure logic such as `total_by_category` | **Overcomplicated code – needs refactoring**: logic mixed with I/O, like v0.1's `run()` |
| Obvious code (low benefit) | **Trivial code** | **Coordinators**: code that only calls other parts, like the `report` command |

That is why Checkpoint 2 wants most tests on pure functions with plain data, and at most one or two with `tmp_path`, `CliRunner` or `monkeypatch`, chosen on purpose.
""",
    [
        "Testable: pass a list, check the answer. No file needed.",
        "Reusable: the same core behind a CLI today and a web page later.",
        "Replaceable: session 17's database only changes the shell.",
        "You cannot assert on a `print`. Make it return, and print in the shell.",
    ],
    "The three words are easy marks in an open answer, but only when tied to the code in front of you: say which test becomes possible, or which part a database would change.",
    "S7 slide 15; S8 slides 17–23, 28; slides/image-only-slides.md (S8 slide 18)",
    [5, 7, 8],
)

section(
    4,
    "Structure in your project: Checkpoint 2 and the rubric",
    """
The course marks the split twice.

**Checkpoint 2, item 3** (session 8 slide 29): most tests call pure functions with plain data; at most one or two use `tmp_path`, `CliRunner` or `monkeypatch`, on purpose. Session 7 slide 15 states the same item from the code's side: the code your tests call has no `print` and no file I/O.

**The partial submission's Structure criterion** (marked at your `v0.5` tag):

| Score | What the rubric says |
|---|---|
| 3 | `src/<package>/` layout. Computation lives in functions that take and return plain data; reading files and printing live in a thin outer layer. No module does both. |
| 2 | Layout is right, but one function still mixes computing with reading or printing. |
| 1 | Layout is right, but logic is mostly inside the command functions. |
| 0 | A script, or code outside `src/`. |

"No module does both" is the strict version of the rule: modules of pure functions on one side; on the other, a thin layer that does the I/O (your `cli.py`, perhaps with a small module that reads and writes your data files). The demo keeps `read_expenses` inside `report.py`; in your own project, giving the file reading a module of its own is the simplest way to meet the criterion. Session 6's naming table even has a name of the right kind: `storage.py`, a module name that says what it is for.

**The refactoring that gets you there.** Slide 5's list of refactoring moves includes *separate I/O from logic*: the demo's `run()` split into read, compute, format. Described in words, as the exam will ask for it, for any function that reads, decides and prints:

1. Find the decision inside it: the total, the fee, the grade.
2. Move it into a new function whose parameters are the values it needs and which returns the answer.
3. Leave the reading and printing in a thin function that calls the new one.
4. Run the program: the output must not change, or it was not a refactoring. Then write the first test for the new function.

Session 8's lab slide says the same: if your logic is tangled up with `print` or `open`, split it first. "That is refactoring under test."
""",
    [
        "CP2 item 3: the code your tests call has no `print` and no file I/O.",
        "Structure 3: computation in functions that take and return plain data, I/O in a thin outer layer, no module does both.",
        "Structure 2: one function still mixes computing with reading or printing. Structure 1: logic mostly inside the commands.",
        "The fix is a refactoring (separate I/O from logic), so the output does not change.",
    ],
    "The 'describe in words how you would change it' part of an open question (sample Q7.3) is this refactoring: name the pure function, what it takes and returns, and what stays in the shell.",
    "partial-rubric.txt (Structure, Tests); S7 slides 5, 15, 22; S8 slides 27–29; labs/08-tdd.md; S6 slide 15",
    [10, 11, 12],
)

section(
    5,
    "Exceptions or return codes",
    """
When something goes wrong, or there is nothing to return, how does a function say so? Slide 17:

| Situation | What the function does |
|---|---|
| The caller can't carry on | `raise` an exception |
| A normal "no result" | return `None` or empty |
| Crossing to the shell | translate to an exit code |

**Raise** when going on would produce nonsense. Give `read_expenses` a path that does not exist and `open` raises `FileNotFoundError`, a kind of `OSError`; give it a row whose amount is `forty` and `float` raises `ValueError`. No report can be built, so the exception travels up to code that can decide what to do.

**Return `None` or empty** when "nothing" is a normal answer. `largest_expense([])` returns `None`: there is no largest of nothing. `total_by_category` for a category nobody used returns `[]`. The return type says so (`-> Expense | None`), and `mypy --strict` then refuses code that uses the result without checking it: session 7's `Item "None" of "Expense | None" has no attribute "amount"`.

**Translate at the shell.** The edge of the program turns an exception into what users and scripts understand: a message and a non-zero exit code. That is the section "Fail loudly, at the boundary".

**Do not return -1 and hope somebody checks.** A value like `-1` looks like an ordinary number, so it flows into sums without complaint, and the type checker cannot help, since mypy accepts `-1` wherever a `float` is promised. We ran this:

```python
PRICES = {"rice": 1.20, "tomatoes": 2.10, "olive oil": 6.50}


def price_of(item: str) -> float:
    if item not in PRICES:
        return -1
    return PRICES[item]
```

A shopping list of rice, tomatoes and saffron totals `2.30` (1.20 + 2.10 − 1), and `mypy --strict` says `Success: no issues found in 1 source file`. Declare `-> float | None`, return `None`, and mypy stops at the line that adds the price: `Unsupported operand types for + ("float" and "None")`. The missing case can no longer be forgotten.

The opposite mistake is as bad. If `read_expenses` returned `[]` for a missing file, a misspelt file name would print a tidy report with `TOTAL 0.00` and exit 0. A missing file is a failure, not an empty month.
""",
    [
        "Caller can't carry on → raise. Normal \"no result\" → `None` or empty. Crossing to the shell → exit code.",
        "Do not return -1 and hope somebody checks: it adds up like any other number.",
        "`-> X | None` makes mypy force every caller to handle the missing case.",
        "A failure is not an empty result: a missing file must not become `[]`.",
    ],
    "Typical questions: 'should this not-found raise or return None?', and a function returning -1 whose caller forgets to check. Justify with the table's words.",
    "S7 slides 17, 8; expense-tracker report.py (v0.3)",
    [15, 16, 19],
)

section(
    6,
    "Catch only what you can handle",
    """
v0.1 wrapped its file reading like this (slide 18):

```python
try:
    ...
except:                       # ← v0.1
    print("could not read " + path)
    sys.exit(1)
```

An `except:` with nothing after it is a **bare except**: it catches every exception raised inside its `try`, whatever its kind. It feels safe and is the opposite. Whatever goes wrong inside the `try`, the user reads the same sentence. In the slide's words, a bare except hides every bug: a typo, a missing import, Ctrl-C. All become "could not read".

We tried it. Misspell `float` as `flaot` in v0.1's reading loop and run the report on a perfectly good file:

```console
$ uv run expenses report expenses.csv
could not read expenses.csv
$ echo $?
1
```

The file is fine and the code is broken, yet the message blames the file. Ctrl-C does the same: pressing it raises `KeyboardInterrupt` inside the program, the bare except catches it, and v0.1 prints `could not read big.csv` as if the file were damaged.

v0.2 (commit `04d699f`) names the two failures it expects:

```python
except (OSError, ValueError):     # ← v0.2: only the two we expect
```

- `OSError`: the file is missing, is a folder, or cannot be read.
- `ValueError`: an amount is not a number, as in `float("forty")`.

Both are problems with the input, which the user can fix, and for both the right reaction is a message and exit code 1. Everything else is a bug in the code, or the user stopping the program, and must not be disguised. With the same typo, v0.2 crashes with a traceback that points at the line and ends `NameError: name 'flaot' is not defined`. For a bug, that is the right result: it is addressed to the developer and names what to fix. From v0.2 the project runs ruff, which flags `flaot` before anything runs (`F821 Undefined name`), and a missing import the same way. The bare except does most harm with the bugs no tool sees, such as reading `row[4]` from a four-column file.

Ruff also has a rule against the bare except itself: the course's rule set includes `E722` (Do not use bare `except`), and v0.2 had to be ruff clean. Silencing it with `except Exception:` is not a fix: ruff passes, but a typo or a wrong column number is an `Exception` too and still comes out as "could not read". Of the slide's three, only Ctrl-C escapes, because `KeyboardInterrupt` is not an `Exception`.
""",
    [
        "A bare `except:` turns everything raised inside its `try` (a typo, a missing import, Ctrl-C) into the same misleading message.",
        "Catch only what you can handle: v0.2 names `(OSError, ValueError)`, the two failures it expects.",
        "Bad input gets a clear message; a bug gets a traceback that names the line.",
        "`except Exception:` silences ruff's `E722` but still hides typos.",
    ],
    "Expect a short program with a bare except and a typo or Ctrl-C: predict the misleading output, then judge a proposed fix such as `except Exception:`.",
    "S7 slide 18; expense-tracker v0.1, 04d699f; ruff E722 and F821 (run)",
    [21, 22, 48],
)

section(
    7,
    "Fail loudly, at the boundary",
    """
Slide 19 divides the work:

- **Core**: raises on bad input, never prints an error.
- **Shell**: catches it, prints to stderr, exits non-zero.

```python
try:
    expenses = read_expenses(path)
except (OSError, ValueError) as error:
    typer.echo(f"could not read {path}: {error}", err=True)
    raise typer.Exit(code=1)
```

`typer.echo(..., err=True)` writes the message to **stderr**; you first wrote it in lab 01: `typer.echo("amount must be positive", err=True)`. `raise typer.Exit(code=1)` ends the command with exit code 1. Session 5's exit code, with the reason attached: on a missing file this prints `could not read nosuch.csv: [Errno 2] No such file or directory: 'nosuch.csv'`. (The repo prints just `could not read nosuch.csv` and ends with `raise typer.Exit(1) from None`. The `from None` keeps ruff quiet: its rule `B904`, in the course's rule set, flags raising a new exception inside an `except` without `from`.)

Why not let the core print the error? Because the core does not know who called it. The CLI wants stderr and exit code 1, a web page would want a message on the page, a test wants the exception itself. The core raises; each shell translates.

**v0.2 → v0.3.** At v0.2 this code still sat in `run()` inside `report.py`, with `print` and `sys.exit(1)`. Commit `15836e1` moved it into the `report` command in `cli.py` and switched to `typer.echo(..., err=True)`: "Moving this to the edge is v0.3."

**Why stderr.** A program has two output streams: **stdout** for its output (the report) and **stderr** for messages to the person. When the user sends the output to a file with `>`, or into another program with a pipe, only stdout goes; stderr still reaches the screen. We ran both versions on a missing file:

| What the user typed | v0.2 (`print`) | v0.3 (`err=True`) |
|---|---|---|
| the report, sent to `report.txt` | screen silent; the error is inside `report.txt` | error on screen; `report.txt` empty |
| the report, piped into `wc -l` | prints `1`: the error counted as a line | error on screen, then `0` |

Tests can check the streams separately as well: `tests/test_io.py` asserts that the exit code is 1 and that `could not read nosuch.csv` is in `result.stderr`.

**Why the exit code.** 0 means success, anything else failure, and `&&`, scripts and CI all read that number. Session 5: a program that prints an error and exits 0 is a program that lies.
""",
    [
        "Core raises, never prints an error. Shell catches, writes to stderr, exits non-zero.",
        "`typer.echo(..., err=True)` plus `raise typer.Exit(code=1)`: session 5's exit code with the reason attached.",
        "stdout is the program's output; stderr is for the person. Redirect or pipe stdout and errors still reach the screen.",
        "A program that prints an error and exits 0 is a program that lies.",
        "v0.2 still printed and exited inside `report.py`; v0.3 moved that to the edge.",
    ],
    "Expect a transcript with `>` or a pipe, or the v0.2 → v0.3 diff: say where the message went, why, and what the exit code tells a script.",
    "S7 slide 19; S5 slide 9; labs/01-scaffold.md; expense-tracker 15836e1; tests/test_io.py (v0.4); runs on v0.2 and v0.3; ruff B904 (run)",
    [27, 28, 30],
)

section(
    8,
    "print is not logging",
    """
Some messages are neither the program's output nor an error: "skipped malformed row 3", "read 420 rows", "entering the discount rules". They are the program's diary: useful when you are hunting a problem, noise the rest of the time. Slide 20 says they belong in **logging**, not `print`:

```python
import logging
logger = logging.getLogger(__name__)
logger.warning("skipped malformed row %d in %s", line_number, path)
```

What logging gives you that `print` does not:

- **A level** on every message: `debug`, `info`, `warning`, `error`, from chatty to serious.
- **Control without editing the code**: messages can be silenced, filtered by level or sent to a file by changing the configuration, without touching the dozens of lines that log.
- **A separate channel**: `print` is for the program's output; logging is for its diary.

**Configure once, in the shell**: `logging.basicConfig(level=logging.INFO)`, for example in the CLI's typer callback. Modules only ask for a logger with `logging.getLogger(__name__)` and log; they never decide where messages go.

We added the slide's warning to `read_expenses`, plus an `info` line counting the rows read, and put `logging.basicConfig(level=logging.WARNING)` in `cli.py`. On a file with one broken row, with the report sent to a file:

```console
$ uv run expenses report small.csv > report.txt
WARNING:expense_tracker.report:skipped malformed row 3 in small.csv
```

The report went into `report.txt` untouched, and the warning still reached the screen, because `basicConfig` writes to stderr unless told otherwise. The `info` line stayed silent at level `WARNING`; changing the level to `INFO` in that one place made it appear. Nothing else in the code changed.

Compare that with the `print("DEBUG ...")` lines a teammate leaves behind while hunting a bug. They land in the report, in anything piped from it and in every test's output, and the only way to turn them off is to find and delete each one.
""",
    [
        "`print` is for the program's output; logging is for its diary.",
        "Levels: debug, info, warning, error. Silence, filter or send to a file without editing the code.",
        "Configure once, in the shell: `logging.basicConfig(level=logging.INFO)`.",
        "Modules log through `logging.getLogger(__name__)`; only the shell decides where messages go.",
    ],
    "Expect a scenario ('the team wants to know how many rows are skipped each night') and a choice between `print`, raising, stderr and logging, or a question on where logging is configured.",
    "S7 slide 20; runs on a logging variant of v0.3",
    [39, 41, 44],
)

# ---------------------------------------------------------------------------
# Questions
# ---------------------------------------------------------------------------

# ---- s1 ----
mcq(
    1, "core", ["concept"], 1, "S7 slide 13", "slides", "source",
    """
Session 7 draws the functional core inside the imperative shell. Which description of the **core** matches the slides?
""",
    (
        "Functions that take values and return values, with no `open`, `print` or `sys.exit`",
        "Slide 13 word for word: data in, data out. Such a function can be called from a test, a CLI or a web page.",
    ),
    [
        (
            "Functions that open the CSV file and turn each row into an `Expense`",
            "Opening a file is touching the world. Slide 14 labels `read_expenses` \"shell: touches a file\", even though it returns a value.",
        ),
        (
            "The typer commands, because they are what the user runs first and they call the rest",
            "The commands in `cli.py` are the shell: they read, print and exit. Being the entry point makes them the outer layer.",
        ),
        (
            "Any function short enough to read on one screen, since a short function has one job",
            "Length is a clean-code concern (one function, one job). A three-line function that calls `print` is still shell.",
        ),
    ],
    "b",
    """
Slide 13: "Core: takes values, returns values. No `open`, no `print`, no `sys.exit`. Shell: the only place that touches the world." What makes a function core is what it does; its size, its file and its place in the call chain do not matter. Reading the CSV and the typer commands both touch the world, so they belong to the shell that wraps the core. The core is what is left when every read, print and exit has been pushed outwards: plain computation from arguments to a returned result.
""",
)

sort_q(
    2, "exam", ["read-code", "judgement"], 1, "S7 slides 13–14; labs/07-refactor.md Part 2; project brief (parking lot)", "slides", "reasoning",
    """
A parking-lot group lists some functions from their project. Put each one where it belongs **as it is written now**. "Mixed" means the function does both kinds of work and needs splitting before its logic can be tested with plain data.
""",
    [
        ("core", "Core: takes values, returns values"),
        ("shell", "Shell: touches the world, little logic"),
        ("mixed", "Mixed: needs splitting"),
    ],
    [
        (
            "`fee(minutes: int) -> float` applies the pricing bands to a number of minutes and returns the fee",
            "core",
            "Number in, number out. A test calls `fee(45)` or `fee(125)` and checks the answer; no file, no terminal.",
        ),
        (
            "`load_tickets(path: str) -> list[Ticket]` opens `tickets.json` and builds a `Ticket` for each entry",
            "shell",
            "It opens a file. Like `read_expenses`, it is shell work even though it returns a value.",
        ),
        (
            "`find_ticket(tickets: list[Ticket], plate: str) -> Ticket | None` returns the ticket for a plate, or `None`",
            "core",
            "It searches a list it was given. `None` is the normal \"no result\".",
        ),
        (
            "`free_spaces(tickets: list[Ticket], capacity: int) -> int`",
            "core",
            "Computes from its arguments and returns a number.",
        ),
        (
            "`receipt_lines(ticket: Ticket, amount: float) -> list[str]` builds the receipt's lines and returns them",
            "core",
            "Like `format_report`: it builds text and returns it. Printing is the shell's job.",
        ),
        (
            "The typer command `leave(plate: str)` calls `load_tickets`, `find_ticket`, `fee` and `receipt_lines`, echoes the lines, and raises `typer.Exit(code=1)` for an unknown plate",
            "shell",
            "It reads, prints and sets the exit code, and leaves every decision to the core: the shape of v0.3's `report` command.",
        ),
        (
            "`save_ticket(path: str, ticket: Ticket) -> None` appends a ticket to `tickets.json`",
            "shell",
            "Writing a file is touching the world.",
        ),
        (
            "`charge(path: str, plate: str) -> None` opens `tickets.json`, works out the fee with its own `if`/`elif` bands and prints the amount",
            "mixed",
            "Reading, the pricing rules and printing in one function: the rules cannot be tested without a file, and the result can only be looked at.",
        ),
        (
            "`busiest_hour(log_path: str) -> int` reads the entry log and returns the hour with the most arrivals",
            "mixed",
            "It returns a value, but it opens a file to get its data. Split the counting (a list of arrival times in, an hour out) from the reading.",
        ),
    ],
    """
The test is the slide's: does the function take values and return values with no `open`, `print` or `sys.exit`? Then it is core, whatever file it sits in. Does it only touch the world and call the core (read, write, echo, exit)? Then it is shell, and it should stay thin. Does it do both? Then it is mixed, and the first refactoring is to pull the decision out into a pure function and leave the I/O in a thin wrapper. Returning a value is not enough to be core: `busiest_hour` returns an `int` but still opens a file.
""",
)

# ---- s2 ----
mcq(
    3, "core", ["read-code"], 2, "S7 slide 14", "slides", "source",
    """
This is the expense-tracker's `report` command at v0.3, slightly simplified:

```python
expenses = read_expenses(path)
totals = total_by_category(expenses, category, minimum)
largest = largest_expense(expenses)
lines = format_report(path, category, minimum, totals, largest)
for line in lines:
    print(line)
```

Which parts touch the world?
""",
    (
        "The first line and the `for` loop at the end",
        "`read_expenses` opens the CSV and the loop prints. Everything in between takes values and returns values.",
    ),
    [
        (
            "The calls to `total_by_category`, `largest_expense` and `format_report`",
            "These are the core: slide 14 labels them \"core: pure\". They receive a list and return lists or an `Expense`.",
        ),
        (
            "Only the `for` loop, because it is the only line that prints",
            "Printing is one way to touch the world; reading a file is another. `read_expenses` is \"shell: touches a file\".",
        ),
        (
            "Only the first line, because `format_report` already printed the report",
            "`format_report` returns a list of strings and prints nothing. Computation is not output (session 6).",
        ),
    ],
    "a",
    """
Slide 14 annotates these lines: `read_expenses` is "shell: touches a file", `total_by_category` and `format_report` are "core: pure", and the loop is "shell: prints". `largest_expense` is pure too. This is the shape of every well-split command: the shell gets data from the world, passes plain values through the core, then shows the result. Reading counts as touching the world just as much as printing does.
""",
)

mcq(
    4, "core", ["concept"], 2, "S7 slide 14; S8 slides 6, 19", "slides", "source",
    """
Slide 14 says: "`total_by_category` does not know that a CSV exists. Give it a list and it works." What does this mean in practice?
""",
    (
        "A test can pass it a few `Expense` objects built by hand, with no file anywhere",
        "That is what session 8's first test does: pass a list, check the answer. No setup, no clean-up.",
    ),
    [
        (
            "It can read any file format, so CSV, JSON and Excel files all work without changes",
            "It reads no file at all, so the file format never reaches it.",
        ),
        (
            "It skips malformed CSV rows, so a broken file cannot make it fail",
            "Skipping rows that are not four fields is `read_expenses`'s job. `total_by_category` never sees a row, only `Expense` objects.",
        ),
        (
            "It has to be called after `read_expenses`, so that the CSV is already open",
            "It needs a list, and the list can come from a CSV, a database or a test.",
        ),
    ],
    "c",
    """
The function's parameters are a `list[Expense]`, a category and a minimum; it returns a list of pairs. Nothing in it opens, reads or parses. That is why session 8's first test builds three `Expense` objects by hand and checks the result, and why session 17's database will not touch this function. A function that knows nothing about where its data came from can be fed from anywhere, including a test.
""",
)

# ---- s3 ----
mcq(
    5, "core", ["concept"], 3, "S7 slide 15", "slides", "source",
    """
In session 17 the expense-tracker will keep its expenses in a database instead of `expenses.csv`. If the v0.3 split is kept, what has to change?
""",
    (
        "Only the reading at the edge: a database query that still returns a `list[Expense]`",
        "Slide 15: \"Replaceable: session 17's database only changes the shell.\"",
    ),
    [
        (
            "`total_by_category` and `format_report`, which must learn to read database rows",
            "They never read anything: they take a `list[Expense]`. That is why they survive the change.",
        ),
        (
            "Every test in `tests/test_report.py`, because the data no longer comes from a file",
            "Those tests build their lists by hand and never touched a file, so they keep passing untouched.",
        ),
        (
            "Nothing at all, because a functional core makes a program independent of its storage",
            "Something still has to fetch the data. Replaceable means only the shell changes.",
        ),
    ],
    "d",
    """
The core's contract is a `list[Expense]` in and plain values out. Swap the CSV reader for a database query that returns the same list, and `total_by_category`, `largest_expense`, `format_report` and all their plain-list tests are untouched. Without the split, the database change would mean rewriting the one big function that reads, computes and prints, and every test that went through it.
""",
)

mcq(
    6, "exam", ["judgement"], 3, "S7 slide 15", "slides", "reasoning",
    """
Later in the course the team wants a small web page that shows the same expense report. Which v0.3 code can the web page reuse unchanged?
""",
    (
        "`total_by_category`, `largest_expense` and `format_report`, called from the web page's own shell",
        "Slide 15: the same core can serve a CLI today and a web page later. Only the shell is new.",
    ),
    [
        (
            "The `report` command in `cli.py`, because it already produces the whole report from start to end",
            "That command is the CLI's shell: it echoes to a terminal and ends with exit codes. A web page needs its own way to show results and errors.",
        ),
        (
            "None of it, because a web page needs its own version of every function in the project",
            "That is the situation the split avoids. The computations do not depend on how the result is shown.",
        ),
        (
            "Only `read_expenses`, because a report is computed differently on a web page than in a terminal",
            "Backwards: the computation is the same everywhere; the I/O around it is what differs between a terminal and a page.",
        ),
    ],
    "b",
    """
"Reusable: the same core can serve a CLI today and a web page later" (slide 15). The core functions take values and return values, so any shell can call them: the CLI's `report` command prints the lines and sets an exit code; a web page would read its input from a form and put the lines on a page. What cannot be reused is the CLI's own shell, because `typer.echo` and `typer.Exit` only make sense in a terminal. It is also why the core must never print or exit: a `sys.exit` inside a reused function would end whatever program called it.
""",
)

mcq(
    7, "exam", ["read-tool-output"], 3, "S8 slides 19, 28; S6 slide 20", "slides", "run",
    """
A gradebook teammate writes a first test for this function:

```python
def print_final_grade(marks: list[float], weights: list[float]) -> None:
    grade = sum(mark * weight for mark, weight in zip(marks, weights, strict=True))
    print(f"Final grade: {grade:.1f}")
```

```python
def test_final_grade_is_the_weighted_average() -> None:
    assert print_final_grade([80.0, 60.0], [0.5, 0.5]) == 70.0
```

`uv run pytest` shows (trimmed):

```text
    def test_final_grade_is_the_weighted_average() -> None:
>       assert print_final_grade([80.0, 60.0], [0.5, 0.5]) == 70.0
E       assert None == 70.0
E        +  where None = print_final_grade([80.0, 60.0], [0.5, 0.5])

tests/test_grades.py:5: AssertionError
----------------------------- Captured stdout call -----------------------------
Final grade: 70.0
=========================== short test summary info ============================
FAILED tests/test_grades.py::test_final_grade_is_the_weighted_average - asser...
1 failed in 0.01s
```

What can you conclude?
""",
    (
        "The sum is right, but the function prints it and returns `None`: return it, print in the shell",
        "Session 8: you cannot assert on a `print`. Make it return, and print in the shell.",
    ),
    [
        (
            "The calculation is wrong, because the function produced `None` instead of 70.0",
            "The captured output shows `Final grade: 70.0`: the arithmetic is right. `None` is what any function without a `return` gives back.",
        ),
        (
            "The test needs `pytest.approx`, because a float such as 70.0 cannot be compared with `==`",
            "A tolerance helps when two floats are nearly equal. Here one side is `None`, which no tolerance turns into 70.0.",
        ),
        (
            "The test should use `tmp_path`, so that the function has a real file to work with",
            "The function reads no file. `tmp_path` is for the one place you read or write a file.",
        ),
    ],
    "d",
    """
pytest shows both sides of the assert: the left side is `None`, and the "Captured stdout call" section shows that the function printed `Final grade: 70.0`. The rule is right, but its result went to the screen instead of back to the caller. This is session 6's "computation is not output" and session 8's "the function prints" trap. The fix is a refactoring: a function that returns the grade, tested with plain lists, and a shell that prints it. (`mypy --strict` flags the test as well: `"print_final_grade" does not return a value (it only ever returns None)  [func-returns-value]`.)
""",
)

mcq(
    8, "hard", ["concept", "judgement"], 3, "S8 slide 18 (2×2 diagram, image-only-slides.md); S8 slides 19, 23", "slides", "source",
    """
Session 8's 2×2 diagram rates code by the benefit of unit-testing it (how non-obvious the code is) against the cost (how many dependencies it has). Where does the v0.3 `report` command in `cli.py` belong?
""",
    (
        "Coordinators: low benefit, high cost",
        "It only calls the core and does I/O around it: little to get wrong, much to set up. One or two `CliRunner` tests, on purpose.",
    ),
    [
        (
            "Algorithms: high benefit, low cost",
            "That is `total_by_category`: real decisions, no dependencies. The command decides almost nothing itself.",
        ),
        (
            "Trivial code: low benefit, low cost",
            "Its cost is not low: it depends on a file, the terminal and the exit code, so testing it needs `CliRunner` and a real or temporary file.",
        ),
        (
            "Overcomplicated code – needs refactoring: high benefit, high cost",
            "That was v0.1's `run()`, which mixed the decisions with the I/O. After the split, the command holds no logic worth that cost.",
        ),
    ],
    "c",
    """
The diagram's corners map onto the core/shell split. Pure core functions are Algorithms: worth testing and cheap to test with a plain list. The shell is a Coordinator: it wires the core to the file and the terminal, so its tests need `CliRunner` or `tmp_path`, and each one checks little logic. A function that mixes both is Overcomplicated code: valuable logic locked behind expensive dependencies, which is why session 8 says to split the file reading out first. Hence Checkpoint 2's rule: most tests on pure functions, one or two I/O tests on purpose.
""",
)

mcq(
    9, "hard", ["read-tool-output", "judgement"], 3, "S7 slide 19; expense-tracker v0.2 report.py (run)", "history", "run",
    """
Before v0.3 existed, a teammate tried to test the missing-file path by calling v0.2's `run()` directly:

```python
from expense_tracker.report import run


def test_a_missing_file_is_reported() -> None:
    run("nosuch.csv", "", 0.0)
```

`uv run pytest` shows (trimmed):

```text
    def run(path: str, category: str, minimum: float) -> None:
        try:
            expenses = read_expenses(path)
        except (OSError, ValueError):
            print(f"could not read {path}")
>           sys.exit(1)
E           SystemExit: 1

src/expense_tracker/report.py:100: SystemExit
----------------------------- Captured stdout call -----------------------------
could not read nosuch.csv
=========================== short test summary info ============================
FAILED tests/test_run.py::test_a_missing_file_is_reported - SystemExit: 1
1 failed in 0.01s
```

What does this show about v0.2's `report.py`?
""",
    (
        "`sys.exit` inside `report.py` ends whatever calls `run()`, a test or another front end",
        "pytest caught the `SystemExit`; a caller that does not catch it, such as a script or a web page, is ended by it. v0.3 moves the exit to the CLI.",
    ),
    [
        (
            "The test is flaky: nothing in it changed, so rerun it a few times until it passes",
            "Nothing random happened: the file does not exist, and `run()` ends with `sys.exit(1)` every time.",
        ),
        (
            "pytest cannot run functions that print, so the `print` must be removed before testing",
            "pytest captured the print without trouble (\"Captured stdout call\"). The failure is the `SystemExit`; the print did no harm.",
        ),
        (
            "`nosuch.csv` is missing from the repo, and adding it to `tests/` would make the test pass",
            "The test is about a missing file. Creating the file would stop testing that case at all.",
        ),
    ],
    "b",
    """
The failure is `SystemExit: 1`, raised by `sys.exit(1)` inside `report.py`. At v0.2 the module still decided how the program ends, so any caller (a test, a web page, another command) is ended by it, and its message went to stdout with `print`. Slide 19: "v0.2 still prints and exits inside `report.py`. Moving this to the edge is v0.3." After `15836e1` there is no `run()`: the `FileNotFoundError` from `read_expenses` goes straight up to the `report` command in `cli.py`, which translates it. The missing-file behaviour is then tested where it belongs, at the command line with `CliRunner`, as `tests/test_io.py` does.
""",
)

# ---- s4 ----
mcq(
    10, "exam", ["read-code", "judgement"], 4, "S7 slide 5; labs/08-tdd.md step 1; S8 slide 27", "slides", "reasoning",
    """
A gradebook group has this function (`grades.csv` has the columns `student,assignment,mark,weight`):

```python
def report_final_grade(path: str, student: str) -> None:
    with open(path) as handle:
        rows = list(csv.reader(handle))
    grade = 0.0
    for row in rows[1:]:
        if row[0] == student:
            grade += float(row[2]) * float(row[3])
    print(f"{student}: {grade:.1f}")
```

You want to test the weighted-average rule. What should the first change be?
""",
    (
        "Move the loop into a function that takes the rows and returns the grade; keep the I/O outside it",
        "Separate I/O from logic: the new function takes values and returns a value, so a test passes a list and checks the answer.",
    ),
    [
        (
            "Write a test that runs it on `data/grades.csv` and compares what it prints with the grade you expect",
            "A test that needs your laptop's file passes only on your machine, and you cannot assert on a print.",
        ),
        (
            "Add a comment above the loop that explains, step by step, how the weighted average is calculated",
            "Comments are for why, and a comment makes nothing testable.",
        ),
        (
            "Add `return grade` and a `float` return type, and keep the `open` and the `print` where they are",
            "A half-step: the result can now be asserted, but every test must still create a CSV, and the function still prints. It still mixes computing with reading and printing.",
        ),
    ],
    "d",
    """
The rule you want to test is buried between an `open` and a `print`. The refactoring move is "separate I/O from logic" (slide 5): extract the decision into a pure function (rows, or marks and weights, in; the grade out) and keep a thin shell that reads the file, calls it and prints. The output must not change. Then the first tests are plain-list tests, for example marks of 80 and 60 with weights of 0.5 give 70.0. Lab 08 in one line: if your logic is tangled up with `print` or `open`, split it first.
""",
)

mcq(
    11, "hard", ["judgement"], 4, "partial-rubric.txt (Structure)", "slides", "source",
    """
A parking-lot group's repository at its `v0.5` tag (the group's partial submission, not one of the demo's tags). Everything is under `src/parking_lot/`. `pricing.py` holds `fee(minutes)`, `find_ticket(tickets, plate)` and `free_spaces(tickets, capacity)`, which take and return plain data. `cli.py` holds the typer commands, each a few lines that read `tickets.json`, call `pricing.py` and echo the result. One exception: `pricing.py` also contains `print_receipt(path, plate)`, which opens `tickets.json`, works out the fee and prints the receipt.

Which **Structure** score from the partial-submission rubric fits best?
""",
    (
        "2: the layout is right, but one function still mixes computing with I/O",
        "The rubric's 2: one function still mixes computing with reading or printing, and `print_receipt` is that function.",
    ),
    [
        (
            "3: the layout is right and nearly all of the computation is in pure functions",
            "3 requires \"No module does both\". `pricing.py` now reads a file and prints, so it does both.",
        ),
        (
            "1: the commands in `cli.py` read `tickets.json` and print, so logic is in the commands",
            "Reading and printing in the commands is what the thin outer layer is for. 1 is when the logic itself sits in the commands.",
        ),
        (
            "0: a module inside `src/` that reads files breaks the layout the rubric asks for",
            "0 means a script, or code outside `src/`. The shell lives in `src/` too.",
        ),
    ],
    "b",
    """
Read the rubric's levels against the facts. Layout: right. Computation: in functions that take and return plain data, except `print_receipt`, which reads, computes and prints. That is "one function still mixes computing with reading or printing": a 2. To reach 3, the usual refactoring: `print_receipt` becomes a pure `receipt_lines(ticket, amount)` in `pricing.py`, and the reading and printing move into the command that calls it. Then no module does both.
""",
)

mcq(
    12, "exam", ["judgement"], 4, "S8 slides 23, 29; labs/08-tdd.md step 3; partial-rubric.txt (Tests)", "lab", "source",
    """
A group's test suite has nine tests. Each one writes a CSV with `tmp_path`, runs a command with `CliRunner` and checks the printed output. All pass and CI is green. Which requirement does this suite go against?
""",
    (
        "Checkpoint 2, item 3: most tests should call pure functions with plain data",
        "Session 8: \"Eight tests that all need a file is the opposite of what we practised.\"",
    ),
    [
        (
            "Checkpoint 2, item 1, because `CliRunner` tests do not count towards the eight tests required",
            "They do count towards the eight (lab 08 says so). They count against \"mostly pure\".",
        ),
        (
            "No requirement: a green CI run shows that the suite meets every checkpoint item",
            "CI checks that the tests pass; it does not check what kind of tests they are. It is the referee, not the judge.",
        ),
        (
            "Checkpoint 2, item 2, because tests that build their own CSV cannot count as edge cases",
            "Item 2 asks for tests aimed at edge cases, and a test that builds its own CSV can be one. The problem is that all nine are I/O tests.",
        ),
    ],
    "a",
    """
Checkpoint 2's third item, and the partial rubric's Tests criterion (a suite where "most of them go through the file system or the command line" scores at most 2), ask for the opposite balance. Nine I/O tests usually mean the logic sits inside the commands, where nothing else can reach it. The remedy is structural: split the computation into pure functions ("the code your tests call has no print and no file I/O"), test those with plain lists, and keep one or two `CliRunner` or `tmp_path` tests for the edge.
""",
)

open_q(
    13, "exam", ["read-code", "judgement"], 4, "S7 slides 13, 15, 17, 18; sample Q7 shape", "slides", "run",
    """
A gradebook group's function, from their repository. `grades.csv` has the columns `student,assignment,mark,weight`.

```python
def show_final_grade(path, student):
    try:
        rows = list(csv.reader(open(path)))
    except:
        print("error")
        return -1
    total = 0
    for row in rows[1:]:
        if row[0] == student:
            total += float(row[2]) * float(row[3])
    if total >= 50:
        print(student, "PASS", round(total, 1))
    else:
        print(student, "FAIL", round(total, 1))
    return total
```
""",
    [
        part(
            "1",
            "In one sentence, what does this function do?",
            1,
            "It reads the file, sums one student's marks times weights, prints PASS (50 or more) or FAIL and returns the total; if reading fails, it prints `error` and returns -1.",
            [
                "Says it reads the file and computes the student's weighted total (mark times weight, summed)",
                "Mentions that it prints PASS or FAIL against 50 and returns the total (or -1 when the file cannot be read)",
            ],
            "\"It calculates the final grade\" misses that the same function also reads the file and prints the verdict. The one-sentence summary should make the several jobs visible, because part 2 is about them. Leaving out the `-1` path loses the detail part 2 needs. \"On any error it returns -1\" overstates it: only the reading line is inside the `try`.",
        ),
        part(
            "2",
            "Name two problems a teammate would face when testing or changing it, using session 7's ideas.",
            2,
            "It mixes reading, computing and printing, so the rule cannot be tested without a CSV. The bare except turns any failure on the reading line (missing file, typo, Ctrl-C) into `error`, and -1 can be averaged like a grade.",
            [
                "The mix of I/O and logic (it opens the file and prints inside the calculation), with the consequence: the rule cannot be tested with plain data, or you cannot assert on a print",
                "The bare `except:` around the reading line: any failure there (a missing file, a typo or a missing `import csv`, Ctrl-C) becomes the same `error`, with no reason given",
                "The `-1` return: a caller can add or average it as if it were a grade, and nothing forces anyone to check",
                "The error goes to stdout as a bare `error`, with no reason and no non-zero exit code, so neither the user nor a script learns what failed",
            ],
            "Naming a problem without its consequence (\"it prints\") scores less than \"it prints instead of returning, so a test cannot check the PASS/FAIL\". Session 6 points (the name `show_final_grade`, the magic number 50, missing type hints) are true but are not what this question asks for. Two points about the same issue (\"it prints\" and \"it does not return\") count once. Saying the bare except also hides a short row's `IndexError` or a mark of `sixty` misreads the code: the loop is outside the `try`, so those stop with a traceback.",
        ),
        part(
            "3",
            "Describe, in words, how you would split it, and name two tests that become possible.",
            3,
            "One pure function takes marks and weights and returns the total; another turns a total into PASS or FAIL. A thin shell reads the file, catches only `OSError` and `ValueError` (stderr, non-zero exit) and prints. Tests: 80 and 60 weighted 0.5 give 70; a total of 50 passes.",
            [
                "Describes a pure function that takes values (rows, or marks and weights) and returns the total, with no `open` and no `print`",
                "Leaves reading and printing in a thin outer function (the shell) that calls it",
                "Replaces the bare except and the -1: specific exceptions caught in the shell, a message on stderr and a non-zero exit code",
                "Names a concrete plain-data test, such as two marks with weights 0.5 giving their average",
                "Names an edge-case test, such as a total of exactly 50 passing, or a student with no rows",
            ],
            "\"Split it into smaller functions\" without saying which part takes values and returns a value, or where the printing goes, earns little: the marker wants the core/shell line drawn. \"Test it on the real `grades.csv`\" is a test that needs your laptop. Writing code instead of words loses time and is not asked for.",
        ),
    ],
    """
A full answer reads the function the way session 7 does: what touches the world (`open`, `print`) and what decides (the weighted sum, the 50 threshold), then how it fails (bare except, `-1`, `error` on stdout). Read where the `try` ends: it covers only the reading line, so a short row or a mark such as `sixty` fails inside the loop and still crashes with a traceback. We ran it: a missing file printed `error` and returned -1; a short row stopped with `IndexError`. The split is the refactoring "separate I/O from logic": pure functions for the total and the verdict, a thin shell for the file and the screen, and failure translated at the boundary. The tests you name must be plain-data tests, because that is what the split makes possible.
""",
    "6–8",
)

open_q(
    14, "hard", ["judgement", "compare"], 4, "partial-rubric.txt (Structure, Tests); S8 slides 23, 29", "slides", "reasoning",
    """
A parking-lot group's repository at its `v0.5` tag (the group's partial submission, not one of the demo's tags). Everything is under `src/parking_lot/`. `pricing.py` holds `fee(minutes)`, `find_ticket(tickets, plate)` and `minutes_parked(ticket, now)`, all taking and returning plain data, and every command in `cli.py` is a few lines that read `tickets.json`, call `pricing.py` and echo the result.

Except one. The `leave` command is 30 lines: it opens `tickets.json`, loops to find the plate, works out the minutes, applies the pricing bands with its own `if`/`elif` chain (it never calls `fee`), prints the receipt, and calls `sys.exit(1)` when the plate is unknown.

Their tests: eight `CliRunner` tests, each of which writes a `tickets.json` with `tmp_path` and runs `leave`.
""",
    [
        part(
            "1",
            "Which score would you expect on the rubric's **Structure** criterion, and why?",
            2,
            "2. The layout is right and most computation is pure, but one function, `leave`, still mixes computing (the ticket search, the minutes, its own pricing bands) with reading and printing. A 3 needs every command thin.",
            [
                "Gives 2",
                "Justifies it with the rubric's words: layout right, but one function still mixes computing with reading or printing (and names `leave`)",
                "Explains why not 3 (the outer layer is not thin, or `pricing.py`'s rules are duplicated inside `leave`) or why not 1 (most logic is in pure functions, not in the commands)",
            ],
            "\"1, because the logic is in the commands\" misreads the facts: only one command holds logic. \"3, because `pricing.py` is pure\" ignores that `leave` re-implements the bands and reads, computes and prints. A score with no reason earns at most one mark.",
        ),
        part(
            "2",
            "Describe, in words, the change that would reach a 3.",
            2,
            "Make `leave` call the existing `fee`, `find_ticket` and `minutes_parked` and delete its own bands. What remains is shell: read, call, echo the receipt, and for an unknown plate a stderr message and `typer.Exit(code=1)`. Receipts must not change.",
            [
                "Has `leave` call the existing pure functions (removing the duplicated pricing rules)",
                "Leaves `leave` as a thin shell: read, call, print, and an unknown plate becomes a stderr message and a non-zero exit (rather than `sys.exit` buried in the logic)",
                "Says it is a refactoring: the receipts and exit codes stay the same, checked by running it or by the existing tests",
            ],
            "\"Clean up `leave`\" or \"make it shorter\" says nothing about what moves where. Moving all 30 lines into `pricing.py` unchanged just moves the mix into another module, which is still \"a module that does both\".",
        ),
        part(
            "3",
            "How does that change help with the **Tests** criterion and Checkpoint 2's item 3?",
            2,
            "Today all eight tests go through a file and the command line, which CP2 item 3 rejects and the Tests criterion caps at 2. After the split most tests call pure functions, such as `fee(125)`, with one or two `CliRunner` tests kept on purpose.",
            [
                "Notes that the current suite is all I/O tests (`CliRunner` plus `tmp_path`), which CP2 item 3 and the Tests criterion count against",
                "Explains that after the split most tests call pure functions with plain data, with a concrete example",
                "Keeps one or two `CliRunner` tests on purpose, for example the unknown plate's exit code",
            ],
            "\"More tests\" misses the point: the number is fine, their kind is wrong. Saying \"use `tmp_path` less\" without saying what replaces it (plain-data tests of the pure functions) is half an answer.",
        ),
    ],
    """
This question reads the partial rubric the way a marker does. Structure: one function mixing computing with reading and printing is the definition of a 2. The route to 3 is the course's refactoring, which here mostly means deleting duplicated logic and calling the core that already exists. The payoff is in the Tests criterion and Checkpoint 2: once the decisions are pure, most tests become plain-data tests, and the eight expensive coordinator tests shrink to the one or two that check the edge on purpose.
""",
    "6–8",
)

# ---- s5 ----
mcq(
    15, "core", ["concept"], 5, "S7 slides 17, 8", "slides", "source",
    """
`largest_expense` is declared `-> Expense | None` and returns `None` when it is given an empty list. Which row of slide 17's table does this follow?
""",
    (
        "A normal \"no result\", so return `None` or empty",
        "There is no largest of nothing, and that is not a failure. `| None` in the type makes mypy insist that callers check.",
    ),
    [
        (
            "The caller can't carry on, so raise an exception",
            "An empty month is not an error. Raising would force every caller to wrap a normal case in `try`/`except`.",
        ),
        (
            "Crossing to the shell, so translate to an exit code",
            "`largest_expense` is core and crosses nothing, and an empty file is not a failure that deserves exit code 1.",
        ),
        (
            "It breaks the table's advice, since returning `None` is as risky as returning `-1`",
            "The difference is that `None` is in the type: mypy forces every caller to check, and `None` cannot quietly be added to a total.",
        ),
    ],
    "c",
    """
Slide 17's middle row: a normal "no result" means return `None` or empty. The largest of nothing does not exist, and that is not a failure. The design is safe because of the type: `-> Expense | None` tells mypy, and `mypy --strict` reports `Item "None" of "Expense | None" has no attribute "amount"` wherever a caller uses the result without checking (slide 8). Returning `-1` or a fake `Expense` would hide the case; raising would treat a normal situation as an error.
""",
)

mcq(
    16, "exam", ["read-code", "judgement"], 5, "S7 slide 17", "slides", "run",
    """
A meal-planner group prices a shopping list:

```python
PRICES = {"rice": 1.20, "tomatoes": 2.10, "olive oil": 6.50}


def price_of(item: str) -> float:
    if item not in PRICES:
        return -1
    return PRICES[item]


def shopping_total(items: list[str]) -> float:
    total = 0.0
    for item in items:
        total += price_of(item)
    return total


print(f"{shopping_total(['rice', 'tomatoes', 'saffron']):.2f}")
```

```console
$ uv run python prices.py
2.30
$ uv run mypy --strict prices.py
Success: no issues found in 1 source file
```

Saffron is not in `PRICES`. What is the best fix?
""",
    (
        "Declare `-> float | None` and return `None`, so mypy makes callers handle a missing price",
        "The missing case becomes part of the contract, and mypy refuses `total += price_of(item)` until the caller decides.",
    ),
    [
        (
            "Keep `-1` and add a comment above `price_of` asking callers to check for it",
            "What slide 17 warns against: \"Do not return -1 and hope somebody checks.\" A comment does not stop the addition.",
        ),
        (
            "Return `0.0` for unknown items, so the total is never pulled below the real amount",
            "Saffron becomes free. The total is still wrong, and now nothing anywhere shows it.",
        ),
        (
            "Print `unknown item` inside `price_of` and still return `-1`, so that the user is at least warned",
            "The core now prints, the message lands in the program's output, and the total is still 1 too low.",
        ),
    ],
    "d",
    """
Slide 17: "Do not return -1 and hope somebody checks." The run shows why: 1.20 + 2.10 − 1 = 2.30, a believable number, and mypy is satisfied because `-1` is acceptable where a `float` is promised. With `-> float | None` the missing case is in the type, so mypy rejects the addition until the caller decides what a missing price means: skip it and report it, or raise because a total without a price is meaningless. Either way the decision is made on purpose, in one place, instead of by accident in a sum.
""",
)

mcq(
    17, "exam", ["read-tool-output"], 5, "S7 slides 8–10, 17; sample Q3 shape", "slides", "run",
    """
The meal-planner group changes `price_of` to `-> float | None` and returns `None` for unknown items. `shopping_total` is unchanged, and `uv run mypy --strict prices.py` now reports:

```text
prices.py:13: error: Unsupported operand types for + ("float" and "None")  [operator]
prices.py:13: note: Right operand is of type "float | None"
Found 1 error in 1 file (checked 1 source file)
```

Line 13 is `total += price_of(item)`. What should you do?
""",
    (
        "Decide in `shopping_total` what a missing price means (skip and report it, or raise)",
        "mypy has found the exact place where the missing case must be handled. That is the point of the change.",
    ),
    [
        (
            "Nothing yet: unknown items are rare, so the warning can wait until a user complains",
            "Saffron is already in the list, and with `None` the program now crashes with a `TypeError`. Waiting for a complaint is the -1 strategy again.",
        ),
        (
            "Add `# type: ignore` to line 13, because the program ran without errors before the change",
            "It ran and printed a wrong total. Silencing the checker brings back the bug in a new form: a crash on `None` instead of a quiet `-1`.",
        ),
        (
            "Change `price_of` back to returning `-1`, since that version passed `mypy --strict` cleanly",
            "It passed because the checker could not see the problem. The new error is the point of the change.",
        ),
    ],
    "b",
    """
This is the "None not handled" kind of mypy error from session 7: "this can be missing; check it, or change the type". The error names the file, the line and the reason: a value that may be `None` is being added to a `float`. Running the program confirms it: with saffron in the list it now stops with `TypeError: unsupported operand type(s) for +=: 'float' and 'NoneType'` instead of printing a wrong total. The right move is to handle the case where it occurs, which is what returning `-1` let everyone forget.
""",
)

mcq(
    18, "hard", ["read-code", "judgement"], 5, "S7 slides 17, 19; run on a variant of v0.3", "slides", "run",
    """
A teammate makes `read_expenses` "friendlier":

```python
def read_expenses(path: str) -> list[Expense]:
    expenses: list[Expense] = []
    if not os.path.exists(path):
        return []
    with open(path) as handle:
        ...
```

A user then mistypes the file name:

```console
$ uv run expenses report expnses.csv
Expense report for expnses.csv
----------------------------------------
----------------------------------------
TOTAL                     0.00
$ echo $?
0
```

What is the main problem with this change?
""",
    (
        "A missing file now looks like an empty month: no message, exit code 0, nobody can tell it failed",
        "Slide 17: the caller can't carry on, so the exception should go up and the shell should translate it.",
    ),
    [
        (
            "The header still names `expnses.csv`, which is confusing for a reader when the file does not exist",
            "Cosmetic. The real problem is that a failed run looks like a successful one.",
        ),
        (
            "Nothing serious: an empty list is slide 17's normal \"no result\", so returning `[]` follows the table",
            "That row is for a genuine nothing, such as a category nobody used. A missing file means no report can be built: the caller can't carry on, so the exception should go up.",
        ),
        (
            "The function now has two `return` statements, which breaks the rule of one function, one job",
            "Early returns are fine (guard clauses, session 6). The problem is what this one returns.",
        ),
    ],
    "d",
    """
The teammate turned a failure into a normal "no result". Slide 17 keeps those apart: an empty list is right when there is genuinely nothing (a category nobody used); a missing file means the report cannot be produced at all. Our run shows the damage: a mistyped name gives a tidy report with `TOTAL 0.00` and exit code 0, so the user may believe they spent nothing, and `&&` or CI would carry on. In the real v0.3, `open` raises `FileNotFoundError`, the `report` command catches it as an `OSError`, writes `could not read expnses.csv` to stderr and exits with 1.
""",
)

sort_q(
    19, "exam", ["judgement"], 5, "S7 slide 17; S5 slide 9; S8 slide 11", "slides", "reasoning",
    """
For each situation, which row of slide 17's table applies?
""",
    [
        ("raise", "Raise: the caller can't carry on"),
        ("none", "Return None or empty: a normal \"no result\""),
        ("exit", "Exit code: crossing to the shell"),
    ],
    [
        (
            "`find_ticket(tickets, plate)` is asked for a plate that is not in the car park",
            "none",
            "A search that finds nothing is a normal answer. `-> Ticket | None` makes the caller check.",
        ),
        (
            "`fee(minutes)` is called with `-30` minutes",
            "raise",
            "Negative parking time is nonsense; any fee computed from it would be wrong. Raise `ValueError`.",
        ),
        (
            "`total_by_category(expenses, \"pets\", 0.0)` when nobody has a `pets` expense",
            "none",
            "Session 8's \"missing\" edge case: a category nobody used gives `[]`, and the demo's tests check that case.",
        ),
        (
            "`read_expenses(\"nosuch.csv\")` when the file does not exist",
            "raise",
            "No report can be built. `open` raises `FileNotFoundError`; let it go up rather than returning `[]`.",
        ),
        (
            "The `report` command receives that `OSError` from `read_expenses`",
            "exit",
            "The boundary: write `could not read nosuch.csv` to stderr and raise `typer.Exit(code=1)`.",
        ),
        (
            "`largest_expense([])`",
            "none",
            "There is no largest of nothing; the demo returns `None`.",
        ),
        (
            "`weighted_average(marks, weights)` receives weights that add up to 1.3",
            "raise",
            "The input is inconsistent, so any average would be meaningless. The caller cannot carry on.",
        ),
        (
            "A user types `expenses add \"Bar Ramon\" 0` at the terminal",
            "exit",
            "Session 5's example: the shell prints `amount must be positive` and the exit code is 1.",
        ),
    ],
    """
Ask two questions. Is "nothing" a normal answer here (a search with no match, an empty list, an unused category)? Then return `None` or empty and let the type tell the caller. Would carrying on produce nonsense (a negative duration, inconsistent weights, a file that is not there)? Then raise. And where the program meets the user, every failure becomes a message on stderr and a non-zero exit code. The same exception can sit in two rows: `read_expenses` raises, and the `report` command translates.
""",
)

open_q(
    20, "exam", ["read-code", "judgement"], 5, "S7 slide 17; S7 slides 8–10", "slides", "run",
    """
A library group computes overdue fines (`FINE_PER_DAY = 0.20`). The library charges a fine only when a book comes back:

```python
@dataclass(frozen=True)
class Loan:
    title: str
    due: date
    returned: date | None


def days_late(loan: Loan) -> int:
    if loan.returned is None:
        return -1
    return max(0, (loan.returned - loan.due).days)


def total_fines(loans: list[Loan]) -> float:
    return sum(days_late(loan) * FINE_PER_DAY for loan in loans)
```

With two loans, Dune (due 1 October, returned 11 October) and Emma (due 5 October, still on loan), the program prints `1.80`, and `uv run mypy --strict fines.py` says `Success: no issues found in 1 source file`.
""",
    [
        part(
            "1",
            "Explain what went wrong, and why neither mypy nor a quick look at the output caught it.",
            2,
            "Emma is still on loan, so `days_late` returns -1, and `total_fines` multiplies it by 0.20 like any number: Dune's 2.00 becomes 1.80. mypy accepts it because -1 is a valid `int`, and 1.80 looks believable, so nothing signals the mistake.",
            [
                "Traces the -1 into the sum: -1 times 0.20 takes 0.20 off Dune's 2.00, giving 1.80",
                "Explains that mypy cannot see it, because -1 is a valid `int` that matches the declared type",
                "Notes that the wrong total looks plausible, so nobody notices: the \"hope somebody checks\" problem",
            ],
            "\"The -1 is a bug\" without showing how it reaches the total misses the mark the question gives for tracing it. Saying \"mypy is wrong\" misreads the tool: it checks types, and -1 is the right type. Blaming the date arithmetic or the `max` is looking in the wrong place.",
        ),
        part(
            "2",
            "Using session 7's table, what should `days_late` do for a book that is still on loan, and why?",
            2,
            "Return `None`, declared `int | None`: a book still on loan is a normal \"no result\", so raising would be wrong. mypy then rejects `total_fines` until it decides what to do with loans still out, for example skip them.",
            [
                "Chooses return `None` (or another explicit \"no result\") and justifies it as a normal situation, not a failure",
                "Says the return type becomes `int | None`, so mypy forces every caller, such as `total_fines`, to handle the case",
                "Explains why raising does not fit: a book on loan is not something the caller cannot carry on from",
            ],
            "\"Return 0\" fixes this total but hides the case again: a book on loan and a book returned on time become indistinguishable. \"Raise an exception\" treats the most ordinary state of a library book as an error, so every caller needs a `try`. An answer that names `None` but never mentions the type or mypy misses why `None` is safer than -1.",
        ),
        part(
            "3",
            "When *would* raising be the right choice in this program? Give one example.",
            1,
            "When the program cannot carry on: for example, the loans file holds a date like `2026-02-30`. Parsing it raises `ValueError`, which goes up to the shell; the shell writes the reason to stderr and exits non-zero.",
            [
                "Gives a case where the caller can't carry on (an unreadable or missing loans file, an impossible date, a negative fine rate) and says the exception goes up to the shell, which turns it into a message and an exit code",
            ],
            "\"When the book is late\" is the normal business of the function, not a failure. An example without saying who handles the exception (the shell, with a message and an exit code) is incomplete.",
        ),
    ],
    """
The table in slide 17 decides each case by asking whether the caller can carry on. A book still on loan is ordinary, so `None` (with the type saying so) is right, and mypy then makes `total_fines` choose what to do. A broken input file is not ordinary, so it raises and the shell translates. Returning -1 mixes the two: it is neither a value nor an error, and it adds up silently, which our run shows as a fine of 1.80 instead of 2.00.
""",
    "5–7",
)

# ---- s6 ----
mcq(
    21, "core", ["concept"], 6, "S7 slide 18", "slides", "source",
    """
Slide 18 shows v0.1's error handling, an `except:` with nothing after it. What is the problem with this bare except?
""",
    (
        "It catches everything, so a typo, a missing import or Ctrl-C all say \"could not read\"",
        "Slide 18: a bare except hides every bug.",
    ),
    [
        (
            "It is a syntax error in Python 3, so the program will not even start",
            "It is valid Python, and v0.1 runs. That is what makes it dangerous: nothing stops you writing it.",
        ),
        (
            "It only catches `OSError`, so a bad amount still crashes the report",
            "The opposite: it catches everything, including errors it has no business handling.",
        ),
        (
            "It makes the program slower, because Python has to check every kind of exception it might meet",
            "Speed is not the issue. The issue is what the user is told and what the developer never sees.",
        ),
    ],
    "d",
    """
An `except:` with nothing after it matches any exception. In v0.1 that meant one message for every possible problem: a missing file (fair enough), but also a misspelt name inside the `try`, a forgotten import, or the user pressing Ctrl-C. The message blames the file every time, so the developer never sees the bug and the user is misled. v0.2 replaced it with `except (OSError, ValueError):`, the two failures the code expects, and ruff's `E722` (Do not use bare `except`) flags the bare form.
""",
)

mcq(
    22, "exam", ["predict-output", "read-code"], 6, "S7 slide 18; expense-tracker v0.1 report.py (run with a typo)", "history", "run",
    """
Someone edits v0.1's reading code and misspells `float`:

```python
def run(path, cat, minimum):
    rows = []
    try:
        f = open(path)
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            # skip rows that do not have all four fields
            if len(row) == 4:
                rows.append((row[0], row[1], row[2], flaot(row[3])))
        f.close()
    except:
        print("could not read " + path)
        sys.exit(1)
    ...
```

`expenses.csv` exists and every row is well formed. What happens when you run `uv run expenses report expenses.csv`?
""",
    (
        "It prints `could not read expenses.csv` and exits with code 1",
        "The `NameError` from `flaot` is raised inside the `try`, and the bare except catches it like any other exception.",
    ),
    [
        (
            "It stops with a traceback ending in `NameError: name 'flaot' is not defined`",
            "That is what v0.2 shows with the same typo. Here the bare except catches the `NameError` before any traceback appears.",
        ),
        (
            "It prints the full report, because rows that raise an error are skipped",
            "Python does not skip lines that fail. The very first data row raises, and the whole `try` is abandoned.",
        ),
        (
            "It prints nothing and exits with code 0, because the error was handled",
            "The handler prints a message and calls `sys.exit(1)`. Handled is not the same as hidden.",
        ),
    ],
    "c",
    """
We ran this code. The first data row reaches `flaot(row[3])`, Python raises `NameError`, and the bare `except:` catches it: `could not read expenses.csv`, exit code 1. The file is fine, the code is broken, and the message blames the file. With v0.2's `except (OSError, ValueError):` the `NameError` is not caught, so the program stops with a traceback that points at the line and ends `NameError: name 'flaot' is not defined`. That is slide 18's point: a bare except turns a typo into "could not read".
""",
)

mcq(
    23, "hard", ["read-tool-output", "concept"], 6, "S7 slide 18; expense-tracker v0.1 (run with a simulated Ctrl-C)", "history", "run",
    """
On v0.1 you start a report on a large file, change your mind while it is still reading, and press Ctrl-C. The program prints:

```text
could not read big.csv
```

and `echo $?` shows `1`. The file is fine. What happened?
""",
    (
        "Ctrl-C raised `KeyboardInterrupt` inside the `try`, and the bare except caught it",
        "Slide 18 lists Ctrl-C among the things a bare except hides.",
    ),
    [
        (
            "Ctrl-C cut the file short partway through, so the rest of it really could not be read",
            "Ctrl-C does not touch files. It interrupts the running program.",
        ),
        (
            "The terminal printed the message itself, as it does for every interrupted program",
            "No terminal prints such a message: those words come from v0.1's own `print` in its `except`.",
        ),
        (
            "The file was still open, so the operating system refused to read it and raised `OSError`",
            "Nothing tried to read the file twice. The exception came from the keyboard.",
        ),
    ],
    "b",
    """
Ctrl-C makes Python raise `KeyboardInterrupt` wherever the program happens to be. v0.1 was inside its `try`, so the bare `except:` caught it, printed "could not read" and exited with 1, as it would for a broken file. We reproduced it on v0.1: `could not read big.csv`, exit code 1. From v0.2, `except (OSError, ValueError)` no longer catches the interrupt, and the program stops (our run ended with exit status 130, the usual status for an interrupted program). A user who presses Ctrl-C should see the program stop, with no false claim about their file.
""",
)

mcq(
    24, "hard", ["read-tool-output", "judgement"], 6, "S7 slide 18; ruff E722 (run)", "slides", "run",
    """
ruff flags a teammate's loader:

```text
E722 Do not use bare `except`
  --> loader.py:11:5
   |
 9 |             next(reader)
10 |             return [float(row[4]) for row in reader]
11 |     except:
   |     ^^^^^^
12 |         print("could not read " + path)
13 |         sys.exit(1)
   |

Found 1 error.
```

The teammate changes line 11 to `except Exception:`, and `uv run ruff check loader.py` now says `All checks passed!`. The code also has a bug ruff cannot see: in this CSV the amount is in `row[3]`, not `row[4]`.

What does `uv run python loader.py` print on a good `expenses.csv`, and why?
""",
    (
        "`could not read expenses.csv`, because the `IndexError` from `row[4]` is an `Exception` and is still caught",
        "Nearly every error a bug can cause is an `Exception`; of the slide's three examples, only Ctrl-C escapes.",
    ),
    [
        (
            "A traceback ending in `IndexError`, because `except Exception` only catches operating-system errors",
            "That would be `except OSError`. `Exception` is the parent of almost every error, `IndexError` included.",
        ),
        (
            "The sum of the amounts, because code that passes ruff no longer swallows errors",
            "Ruff checked the rule it knows (no bare except). It cannot know which column holds the amount, or what the handler hides.",
        ),
        (
            "`could not read expenses.csv`, because `except Exception` catches everything a bare except did, Ctrl-C included",
            "Right output, wrong reason: `KeyboardInterrupt` is not an `Exception`, so Ctrl-C now escapes. The `IndexError` is caught because it is an `Exception`.",
        ),
    ],
    "a",
    """
We ran both versions: with `except:` and with `except Exception:` the program prints `could not read expenses.csv` and exits 1, although the file is fine. Ruff's `E722` is satisfied by the new spelling, but the judgement behind it (catch only what you can handle) is not. The course's fix is to name the failures you expect, `except (OSError, ValueError):`. With that, our run stopped with a traceback ending `IndexError: list index out of range` at `float(row[4])`: the bug is visible and fixable. Ruff is the referee for its rules; it does not judge your error handling for you.
""",
)

mcq(
    25, "hard", ["judgement", "compare"], 6, "S7 slide 18; partial-rubric.txt (Functionality); runs on v0.1 and v0.2 with a typo", "slides", "run",
    """
With the `flaot` typo, v0.1 printed a tidy `could not read expenses.csv`; v0.2 stops with a traceback ending in `NameError: name 'flaot' is not defined`. A teammate says v0.2 is worse, because the partial-submission rubric says: "Bad input gives a clear message and a non-zero exit code, not a traceback." Which reply is best?
""",
    (
        "Bad input still gets a clear message; a typo is a bug, and its traceback points to the line to fix",
        "Catch only what you can handle: input problems get a message, bugs are not disguised.",
    ),
    [
        (
            "Agree, and wrap the whole command in a bare except again so that users never see any traceback",
            "That brings back v0.1's problem: every bug disguised as a reading error.",
        ),
        (
            "The rubric only applies to the partial submission at `v0.5`, so a traceback is acceptable at `v0.2`",
            "Dodges the question. The difference between bugs and bad input holds at every tag.",
        ),
        (
            "A traceback carries more detail than a message, so v0.2 should show one for a missing file too",
            "A missing file or a bad amount is the user's input, and the rubric wants a clear message and exit code for those. v0.2 does that.",
        ),
    ],
    "c",
    """
Two kinds of failure, two audiences. Bad input (a missing file, an amount that is not a number) is the user's to fix, so it gets a clear message and a non-zero exit code: that is the rubric's Functionality criterion, and v0.2 still does it for `OSError` and `ValueError`. A typo is the developer's to fix: a traceback pointing at the line is the fastest route to the fix, and running the program or the tests should surface it long before a user does. v0.1's tidy message helped nobody: the user was told the file was broken, and the developer was told nothing. (At v0.2, ruff's `F821` would flag `flaot` before anyone ran it; the point stands for bugs no tool sees.)
""",
)

open_q(
    26, "hard", ["read-tool-output", "judgement"], 6, "S7 slides 18–19; ruff E722 (run); sample Q9 shape", "slides", "run",
    """
A user of your group's gradebook reports: "I run `uv run gradebook report grades.csv` and it says `could not read grades.csv`, but the file opens fine in Excel." The reading code on `main`:

```python
def read_marks(path: str) -> list[Mark]:
    try:
        with open(path) as handle:
            reader = csv.reader(handle)
            next(reader)
            return [Mark(row[0], row[1], float(row[2]), float(row[4])) for row in reader]
    except:
        print("could not read " + path)
        sys.exit(1)
```

`grades.csv` has four columns: `student,assignment,mark,weight`. `uv run ruff check src` reports:

```text
E722 Do not use bare `except`
  --> src/gradebook/marks.py:20:5
   |
18 |             next(reader)
19 |             return [Mark(row[0], row[1], float(row[2]), float(row[4])) for row in reader]
20 |     except:
   |     ^^^^^^
21 |         print("could not read " + path)
22 |         sys.exit(1)
   |

Found 1 error.
```
""",
    [
        part(
            "1",
            "How are the user's report and ruff's `E722` connected? What is most likely happening?",
            2,
            "The file is fine; the code is not. `row[4]` does not exist in a four-column file, so every row raises `IndexError`, and the bare except that ruff flags turns that bug into \"could not read\".",
            [
                "Identifies the real bug: `row[4]` is out of range in a four-column file (an `IndexError`), not a problem with the file",
                "Connects it to `E722`: the bare except catches that bug and disguises it as \"could not read\"",
            ],
            "\"The file is corrupted\" or \"Excel saved it wrongly\" believes the misleading message, which is the trap. \"Ruff found a style problem\" misses that this style rule exists because of this kind of bug.",
        ),
        part(
            "2",
            "Which exceptions should the handler name, why those, and where should the message and the exit happen?",
            2,
            "`OSError` (missing or unreadable file) and `ValueError` (a mark that is not a number): input problems the user can fix. `read_marks` just raises; the CLI command catches those two, writes the reason to stderr and raises `typer.Exit(code=1)`.",
            [
                "Names `OSError` and `ValueError` and links each to a real input problem (missing or unreadable file; a value that is not a number)",
                "Moves the message and exit to the shell: the core raises, the command catches, writes to stderr and exits non-zero",
            ],
            "Naming `IndexError` as an exception to catch would hide this very bug again. Keeping `print` and `sys.exit` inside `read_marks` repeats v0.2's mistake, which v0.3 fixed by moving them to the edge. Naming only one of the two exceptions leaves the other input problem unhandled.",
        ),
        part(
            "3",
            "A teammate proposes `except Exception:` \"because ruff accepts it\". Do you accept? Give your reasoning.",
            2,
            "No. Ruff would pass, but `IndexError` is an `Exception`, so the bug would still print \"could not read\". A green ruff is not the goal; with the two named exceptions the `IndexError` surfaces as a traceback at `row[4]` and gets fixed.",
            [
                "Rejects it and explains that `except Exception` still catches the `IndexError` (or any bug), so the message stays misleading",
                "Argues that passing the tool is not the goal: ruff is the referee for its rule, not for whether the error handling is right",
            ],
            "\"Yes, CI will be green\" is the sample paper's `# type: ignore` trap in another form. \"No, because ruff will still complain\" is factually wrong: ruff accepts `except Exception:`. The mark is for the reason.",
        ),
    ],
    """
This mirrors the sample paper's tool-output question: read the output, connect it to a real failure, and refuse a fix that only silences the tool. The bare except turns `row[4]`'s `IndexError` into a false "could not read". Naming `OSError` and `ValueError` handles the input problems the user can fix and leaves the bug to crash where the developer will see it, and moving the message to stderr and the exit to the CLI is v0.3's "fail loudly, at the boundary". `except Exception:` passes ruff and fixes nothing.
""",
    "6–8",
)

# ---- s7 ----
mcq(
    27, "core", ["concept"], 7, "S7 slide 19", "slides", "source",
    """
A user runs the report on a file that does not exist. According to slide 19, how should the work be divided between the core and the shell?
""",
    (
        "The core raises; the shell catches it, writes the message to stderr and exits with a non-zero code",
        "Slide 19: core raises on bad input, never prints an error; shell catches it, prints to stderr, exits non-zero.",
    ),
    [
        (
            "The core catches it, prints a friendly message and returns an empty list so the report still appears",
            "The user gets a report of nothing and exit code 0. A failure has been dressed up as a normal \"no result\".",
        ),
        (
            "The core writes the message to stderr and calls `sys.exit(1)`, so the shell can stay short",
            "Close to v0.2, which printed and exited inside `report.py` (with `print` and `sys.exit(1)`); v0.3 undid it, because a core that prints and exits cannot be tested or reused.",
        ),
        (
            "The shell prints the message and ends the program normally, so the user is not alarmed by an error code",
            "Exit code 0 after a failure lies to `&&`, scripts and CI.",
        ),
    ],
    "a",
    """
Slide 19 splits failing well between the layers. The core knows something went wrong but not who is asking, so it raises (or passes `open`'s `FileNotFoundError` up). The shell knows it is a terminal program, so it catches the expected exceptions, writes a message with the reason to stderr (`typer.echo(..., err=True)`) and ends with `raise typer.Exit(code=1)`. Each of the other options puts I/O in the core, hides the failure, or lies with exit code 0.
""",
)

mcq(
    28, "core", ["concept"], 7, "S7 slide 19; tests/test_io.py; runs on v0.2 and v0.3", "slides", "source",
    """
Why does the course send error messages to stderr rather than stdout?
""",
    (
        "Errors still reach the screen when output is redirected or piped, and tests can check them",
        "stdout is the program's output; stderr is for the person. `tests/test_io.py` checks `result.stderr`.",
    ),
    [
        (
            "Writing a message to stderr is what makes the program end with a non-zero exit code",
            "They are independent: `err=True` decides where the message goes, `typer.Exit(code=1)` decides the exit code. You need both.",
        ),
        (
            "stderr is copied to a log file automatically by the system, so an error message is never lost",
            "Nothing is saved automatically. stderr goes to the terminal unless someone redirects it.",
        ),
        (
            "stdout is reserved for logging messages, so errors need a stream of their own",
            "Backwards: stdout carries the program's output, such as the report.",
        ),
    ],
    "b",
    """
A program has two output streams. stdout carries the program's output: the report, which a user may send to a file with `>` or into another program with a pipe. stderr carries messages meant for the person at the terminal, and it is not redirected along with stdout. So when the file is missing, the user still sees `could not read nosuch.csv` on screen while `report.txt` stays clean. Tests benefit too: `CliRunner` gives `result.stdout` and `result.stderr` separately, and the demo's `test_io.py` asserts the message is in `result.stderr`.
""",
)

mcq(
    29, "core", ["judgement"], 7, "S7 slides 18–19; expense-tracker 15836e1", "slides", "source",
    """
In v0.3, `read_expenses` can raise `OSError` (missing file) or `ValueError` (an amount that is not a number). Where should the `try`/`except` that turns these into a message live?
""",
    (
        "In the `report` command in `cli.py`, around the call to `read_expenses`: the shell picks the message and exit code",
        "That is v0.3: catch only what you can handle, at the boundary.",
    ),
    [
        (
            "Inside `read_expenses` itself, which prints the message for the user and then returns `[]`",
            "Printing inside the reading function (v0.3 took every `print` out of `report.py`), and a failure disguised as an empty list: the report shows `TOTAL 0.00` and exits 0.",
        ),
        (
            "Inside `total_by_category`, since that is the function where the amounts are finally added up",
            "`total_by_category` never sees a bad amount: `float()` fails while reading, before any `Expense` exists.",
        ),
        (
            "Around the whole program in `__main__.py`, as one bare except that prints a general apology such as `something went wrong`",
            "A bare except hides every bug, and \"something went wrong\" tells the user nothing.",
        ),
    ],
    "d",
    """
The exception should travel from where it happens (`open` or `float` inside `read_expenses`) to the first place that knows what to do about it. That is the shell's `report` command: it knows this is a terminal program, so it can write `could not read nosuch.csv` to stderr and end with exit code 1. Commit `15836e1` put the `try`/`except` there. Catching it lower down forces `report.py` to print or to fake a result; catching it higher up with a bare except hides bugs along with input problems.
""",
)

mcq(
    30, "exam", ["predict-output", "read-tool-output"], 7, "S7 slide 19; runs on v0.2 and v0.3", "history", "run",
    """
At v0.2, a user saves a report to a file but mistypes the input's name. Nothing appears on the screen:

```console
$ uv run expenses report nosuch.csv > report.txt
$ cat report.txt
could not read nosuch.csv
```

Why did the error end up in `report.txt`, and what changes at v0.3?
""",
    (
        "v0.2's `print` writes to stdout, which `>` sends to the file; v0.3 writes the error to stderr",
        "Only stdout is redirected by `>`. At v0.3 the error stays on screen and `report.txt` is empty.",
    ),
    [
        (
            "`>` sends everything a program writes into the file, so no version can show the error on screen while redirecting",
            "`>` redirects stdout only. stderr still goes to the terminal, which is the whole reason v0.3 uses it.",
        ),
        (
            "The exit code was 0, so the shell treated the message as normal output; v0.3 fixes this by exiting with 1",
            "v0.2 already exited with 1 (`sys.exit(1)`). The exit code does not decide where text goes.",
        ),
        (
            "Because `nosuch.csv` did not exist, `>` created it and wrote the error into it; v0.3 checks the path first",
            "`>` created `report.txt`, the output file, not the input. v0.3 does not check paths; it changes the stream.",
        ),
    ],
    "a",
    """
We ran both tags. At v0.2, `run()` in `report.py` handled the failure with `print(f"could not read {path}")`, and `print` writes to stdout. `> report.txt` sends stdout to the file, so the user sees nothing and the "report" they saved is an error message. At v0.3, commit `15836e1` moved the handling to the CLI and used `typer.echo(..., err=True)`: the same command shows `could not read nosuch.csv` on screen and leaves `report.txt` empty. In both versions the exit code is 1; what changed is which stream the message uses.
""",
)

mcq(
    31, "exam", ["read-diff"], 7, "expense-tracker 15836e1; S7 slide 19", "history", "run",
    """
This is commit `15836e1`, "Move printing and exiting out of the report module" (trimmed):

"""
    + DIFF_15836E1
    + """

Which description of the commit is accurate?
""",
    (
        "It moves reading, printing and exiting from `report.py` to the `report` command, with errors on stderr",
        "`run()` and `import sys` disappear from `report.py`; the same steps reappear in `cli.py`, with `typer.echo(..., err=True)` for the error.",
    ),
    [
        (
            "It changes how `total_by_category` works, so the report for a valid file changes",
            "No line of `total_by_category` appears in the diff. For a valid file the output is the same.",
        ),
        (
            "It adds error handling for missing files, which v0.2 did not have at all",
            "v0.2 already caught `(OSError, ValueError)` inside `run()`. The commit moves that handling; it does not invent it.",
        ),
        (
            "It removes the `try`/`except`, so a missing file now ends the whole program with a traceback",
            "The `try`/`except` is still there, now in `cli.py`. A missing file still gives a message and exit code 1.",
        ),
    ],
    "c",
    """
Read the diff file by file. In `report.py`, `run()` and `import sys` are deleted: the module now has no `print` and no `sys.exit`. In `cli.py`, the `report` command stops calling `run()` and does its work itself: `try` around `read_expenses`, catch the two expected exceptions, `typer.echo(..., err=True)` and `raise typer.Exit(1)`, then the same calls to the pure functions and a loop of `typer.echo(line)`. Nothing about the calculation changes. This is slide 19's "Moving this to the edge is v0.3" in one commit.
""",
)

mcq(
    32, "exam", ["predict-output", "judgement"], 7, "S5 slide 9; S7 slide 19; run on a variant of v0.3", "slides", "run",
    """
A teammate changes the `report` command's error handling to:

```python
    except (OSError, ValueError):
        typer.echo(f"could not read {path}", err=True)
        return
```

"so users do not see an error code". A script then runs:

```console
$ uv run expenses report nosuch.csv && echo "report ready"
could not read nosuch.csv
report ready
```

What has gone wrong?
""",
    (
        "The command now exits with 0 after failing, so `&&`, scripts and CI think it worked",
        "Session 5: a program that prints an error and exits 0 is a program that lies.",
    ),
    [
        (
            "`&&` always runs the second command, so the script should have used `;` between the two",
            "`&&` runs the second command only when the first exits with 0. It did its job; the exit code was the lie.",
        ),
        (
            "The message should have gone to stdout, so that the script could read it and stop",
            "Scripts decide by the exit code; they do not read the text. On stdout the error would also pollute the output.",
        ),
        (
            "typer prints `report ready` by itself whenever a command returns early without an error",
            "`report ready` comes from the `echo` after `&&`, which ran because the exit code was 0.",
        ),
    ],
    "c",
    """
We ran this variant: the message still goes to stderr, but `return` ends the command normally, so the exit code is 0 and `&&` runs `echo "report ready"`. In a check script or in CI the next step would run on bad data, and the run would show green. The real v0.3 ends with `raise typer.Exit(1)`, and the same line prints only the error. A clear message for the person and a non-zero exit code for the machines are two separate jobs, and failing well needs both.
""",
)

mcq(
    33, "hard", ["read-tool-output", "read-diff"], 7, "expense-tracker tests/test_io.py (v0.4); S7 slide 19; S8 slide 21", "history", "run",
    """
On the v0.4 demo, a teammate makes this change and runs the tests:

```diff
     except (OSError, ValueError):
-        typer.echo(f"could not read {path}", err=True)
+        print(f"could not read {path}")
         raise typer.Exit(1) from None
```

```text
>       assert "could not read nosuch.csv" in result.stderr
E       AssertionError: assert 'could not read nosuch.csv' in ''
E        +  where '' = <Result SystemExit(1)>.stderr

tests/test_io.py:29: AssertionError
=========================== short test summary info ============================
FAILED tests/test_io.py::test_report_on_a_missing_file_exits_with_one_and_explains_on_stderr
1 failed, 23 passed in 0.06s
```

What can you conclude?
""",
    (
        "The message now goes to stdout, so `result.stderr` is empty: put `err=True` back",
        "The test encodes the requirement that errors go to stderr, and it caught the regression.",
    ),
    [
        (
            "The test is flaky: `CliRunner` sometimes misses output, so rerun it until it passes",
            "The failure is deterministic: stderr is empty every time, because nothing writes to it any more.",
        ),
        (
            "`CliRunner` cannot capture `print`, so the command must use `typer.echo` everywhere",
            "`CliRunner` captures `print` fine: the message is in `result.stdout`. The problem is which stream it went to.",
        ),
        (
            "The test should look in `result.stdout` instead, since the message is still printed",
            "Editing the test to match the new behaviour throws away the requirement: a user who redirects the report would lose the error.",
        ),
    ],
    "b",
    """
pytest shows the comparison: the expected text was searched for in `''`, the captured stderr. The exit code assertion passed (it came first), so only the stream changed. We checked: with `print`, the message is in `result.stdout` and `result.stderr` is empty. The test exists to pin slide 19's rule that the shell prints errors to stderr, and it did its job. Rewriting the test to match the change is the careless move; reverting to `typer.echo(..., err=True)` is the fix.
""",
)

mcq(
    34, "hard", ["predict-output"], 7, "S7 slide 19; sample Q6 (pipes); runs on v0.2 and v0.3", "history", "run",
    """
A script counts the lines of a report with `uv run expenses report nosuch.csv | wc -l`. The file does not exist. What do v0.2 and v0.3 show?
""",
    (
        "v0.2 prints `1`; v0.3 shows `could not read nosuch.csv` on screen, then `0`",
        "Only stdout goes into the pipe. v0.2's error is on stdout and is counted; v0.3's is on stderr and is not.",
    ),
    [
        (
            "Both print `1`, because the error message is a single line of text in both versions",
            "Same text, different stream. v0.3's message never enters the pipe.",
        ),
        (
            "Both print `0`, because a failing command stops the whole pipe before `wc` can run",
            "`wc` runs whatever the first command does, and counts what arrives on its input.",
        ),
        (
            "v0.2 prints `0` and v0.3 prints `1`, because only stderr is sent into a pipe by the shell",
            "Backwards: a pipe carries stdout. stderr goes straight to the screen.",
        ),
    ],
    "a",
    """
A pipe connects the first program's stdout to the second program's input, just as `>` connects it to a file. We ran both tags: at v0.2 the error is printed with `print`, so `wc -l` counts it and prints `1`, as if the report had one line. At v0.3 the error goes to stderr: it appears on the screen, nothing enters the pipe, and `wc -l` prints `0`. A script that trusted the count would be fooled by v0.2; the person at the terminal is only told the truth by v0.3.
""",
)

mcq(
    35, "exam", ["compare", "read-tool-output"], 7, "S7 slide 19; runs on v0.3 and the slide's variant", "slides", "run",
    """
The repo's `report` command catches the error with `except (OSError, ValueError):` and prints `could not read {path}`. Slide 19's version is `except (OSError, ValueError) as error:` and prints `could not read {path}: {error}`. On a file whose second row has the amount `forty`:

```console
$ uv run expenses report bad.csv
could not read bad.csv
```

with the repo's version, and with the slide's:

```console
$ uv run expenses report bad.csv
could not read bad.csv: could not convert string to float: 'forty'
```

What does the user gain from the slide's version?
""",
    (
        "The reason: they can tell a missing file from a bad amount, and they see which value to fix",
        "Slide 19: \"Session 5's exit code, with the reason attached.\"",
    ),
    [
        (
            "A different exit code for each kind of error, so scripts can tell them apart",
            "Both versions end with exit code 1. Only the text differs.",
        ),
        (
            "A traceback, which names the file and line where the error happened and so is more precise",
            "There is no traceback: `{error}` is the exception's own one-line message, written to stderr.",
        ),
        (
            "Nothing useful: the message is longer, but it tells the user the same thing",
            "The repo's message is identical for a missing file and a bad amount. The slide's names the cause and the value.",
        ),
    ],
    "a",
    """
`as error` keeps the caught exception, and `{error}` puts its message into the line. For a missing file that reads `[Errno 2] No such file or directory: 'nosuch.csv'`; for a bad amount, `could not convert string to float: 'forty'`. Both runs exit with 1, so scripts behave the same, but the person now knows whether to check the file name or the amount `forty`. Failing loudly includes saying why something failed, and it costs one variable.
""",
)

open_q(
    36, "exam", ["read-diff", "compare", "judgement"], 7, "S7 slides 18–19; sample Q8 shape", "slides", "run",
    """
A library group's commit changes how the book list is loaded. `overdue_report(books, today)` returns `["No overdue books."]` when it gets an empty list.

In `src/library/books.py`:

```diff
-def load_books(path):
-    try:
-        with open(path) as handle:
-            return [parse_book(line) for line in handle]
-    except:
-        print("Library file is broken")
-        return []
+def load_books(path: str) -> list[Book]:
+    with open(path) as handle:
+        return [parse_book(line) for line in handle]
```

In `src/library/cli.py`:

```diff
 @app.command()
 def overdue(path: str = typer.Argument("books.csv")) -> None:
-    books = load_books(path)
+    try:
+        books = load_books(path)
+    except (OSError, ValueError) as error:
+        typer.echo(f"could not read {path}: {error}", err=True)
+        raise typer.Exit(code=1) from None
     for line in overdue_report(books, date.today()):
         typer.echo(line)
```
""",
    [
        part(
            "1",
            "What does this change do?",
            1,
            "It moves the error handling out of `load_books`, which now just reads, into the `overdue` command: an unreadable file or a bad line now gives the reason on stderr and exit code 1.",
            [
                "Says the handling moves out of `load_books` (which now only reads and lets `OSError` or `ValueError` go up) into the `overdue` command at the boundary, with only those two caught, a stderr message and exit code 1",
            ],
            "\"It improves error handling\" is too vague to mark. Describing only one file (\"it deletes the try in `load_books`\") misses that the handling reappears in `cli.py`, so nothing is lost: it has moved from the reading function to the command at the boundary, and a full answer names both ends of the move.",
        ),
        part(
            "2",
            "Name one situation the old version handled badly, and say what the librarian would have seen.",
            2,
            "A mistyped file name: it printed \"Library file is broken\", returned an empty list, and the report said \"No overdue books.\" with exit code 0, a false all-clear.",
            [
                "Names a concrete case (missing file, misspelt name, a bad date in a line, or a bug in `parse_book`) and says it was reported as \"Library file is broken\"",
                "Explains the consequence of `return []`: the program carries on and reports \"No overdue books.\" with exit code 0, a wrong answer that looks right",
            ],
            "Stopping at \"it prints a vague message\" misses the worse half: `return []` makes the program carry on with a false all-clear. Answers that only say \"bare except is bad\" without a situation and what the user sees do not answer the question asked.",
        ),
        part(
            "3",
            "The author offers two commit messages: A `Fix error handling` and B `Exit with an error when the books file cannot be read`. Which is better for someone reading the history six months later, and why?",
            2,
            "B. It names what changed: an unreadable books file now ends in an error instead of a false all-clear. A reader finds the commit from the log line alone; A fits almost any commit.",
            [
                "Chooses B and says it names the behaviour that changed (an unreadable file now fails with an error instead of an empty report)",
                "Explains why A fails a later reader: it is too vague to find in the log or to understand without opening the diff",
            ],
            "\"B, because it is longer\" gives no reason a marker can credit. \"A, because short messages are better\" ignores the reader six months later, who cannot tell from `Fix error handling` what was broken or what changed. Judging grammar or length misses the question: what the message lets a future reader find and understand.",
        ),
        part(
            "4",
            "Name one test you would add for this change, in words.",
            1,
            "With `CliRunner`, run `overdue` on a missing file and check for exit code 1 and `could not read` in `result.stderr`.",
            [
                "A concrete test of the boundary: a missing (or malformed, via `tmp_path`) file gives exit code 1 and a message on stderr",
            ],
            "\"Test that it works\" is not a test. A test that reads the group's real `books.csv` passes only on one laptop; build the bad file with `tmp_path` or use a name that does not exist.",
        ),
    ],
    """
This is the course's failing-well review in miniature. The old `load_books` combined a bare except, a message on stdout and a disguised failure (`return []`), so a misspelt file name produced a cheerful "No overdue books." with exit code 0; we ran it. In the new version `load_books` raises and the command catches only `OSError` and `ValueError`, writes the reason to stderr and exits with 1. The better commit message names that behaviour change, which is what someone searching the history later needs. The test to add is one of the course's "one or two I/O tests on purpose": `CliRunner` checking the exit code and `result.stderr`.
""",
    "6–8",
)

open_q(
    37, "exam", ["read-diff", "compare"], 7, "expense-tracker 9d6c607; S7 slides 15, 19; S8 slide 13", "history", "run",
    """
This is the expense-tracker's commit `9d6c607`, "Separate reading and printing from the calculation", from the work between v0.1 and v0.2 (trimmed: the new `format_report` is not shown; it builds the same report as before, but returns it as a list of lines instead of printing each line):

"""
    + DIFF_9D6C607,
    [
        part(
            "1",
            "What does this commit do to `run()`, and what stays the same?",
            2,
            "It gives each job its own function: `read_expenses` reads the file, `largest_expense` finds the biggest expense, `format_report` builds the lines. `run()` now only calls them in order, and the report is the same.",
            [
                "Names at least two of the new functions with their jobs (reading, finding the largest, building the report lines)",
                "Says `run()` now just calls them in order, and that the behaviour for the user is unchanged",
            ],
            "\"It adds functions\" names no jobs and no direction. \"It fixes the error handling\" misreads the diff: the `try` and the `sys.exit(1)` are still in `run()`, only the reading moved out of it.",
        ),
        part(
            "2",
            "`run()` still has a problem that makes it hard to test. Which, and where should that part go?",
            2,
            "It still prints and ends the program with `sys.exit(1)`, so a test would have to capture output and catch the exit. Those belong to the shell, the command in `cli.py`; `report.py` should keep only functions that take and return data.",
            [
                "Identifies `print` and `sys.exit` still inside `run()` in `report.py`",
                "Says they belong in the outer layer (the command in `cli.py`, the shell) so that the module is left with pure functions",
            ],
            "\"`run()` is too long\" is a symptom, not the problem the course names. \"It needs more functions\" repeats what this commit already did. The marks are for the two calls that touch the world and for where they should live.",
        ),
        part(
            "3",
            "Describe in words one test that this commit makes possible and that `run()` alone did not.",
            2,
            "Call `format_report` with a small list of totals and assert on the lines it returns, or call `largest_expense` with an empty list and assert that it returns `None`. Neither needs a file on disk or captured output.",
            [
                "A test of `format_report` or `largest_expense` (or `read_expenses` with a small file) that uses plain data",
                "States what it no longer needs: no captured printing, no exit to catch",
            ],
            "\"Test that the program still works\" is not a test of the new structure. A test that calls `run()` still has to capture `print` and catch `SystemExit`, so it gains nothing from this commit.",
        ),
    ],
    """
Reading a diff means saying what moved and what is still wrong. The structure moved: reading, searching and formatting left `run()`. What stayed is the part that touches the world, `print` and `sys.exit`, which is why v0.2 is not yet the finished shape (slide 19: \"v0.2 still prints and exits inside report.py\"). The next commit, `15836e1`, moves them to `cli.py`. The payoff of this commit is already testable: functions that take and return plain data can be called with a plain list.
""",
    "6–8",
)

open_q(
    38, "hard", ["read-tool-output", "predict-output"], 7, "S7 slide 19; S5 slide 9; runs on v0.2 and v0.3", "history", "run",
    """
The same commands, run on the v0.2 and the v0.3 tags of the demo. `nosuch.csv` does not exist.

v0.2:

```console
$ uv run expenses report nosuch.csv > report.txt
$ cat report.txt
could not read nosuch.csv
$ uv run expenses report nosuch.csv | wc -l
1
$ uv run expenses report nosuch.csv; echo $?
could not read nosuch.csv
1
```

v0.3:

```console
$ uv run expenses report nosuch.csv > report.txt
could not read nosuch.csv
$ cat report.txt
$ uv run expenses report nosuch.csv | wc -l
could not read nosuch.csv
0
$ uv run expenses report nosuch.csv; echo $?
could not read nosuch.csv
1
```
""",
    [
        part(
            "1",
            "Explain why the v0.2 user saw nothing on the screen after the first command, and why `wc -l` printed `1`.",
            2,
            "v0.2 prints the error with `print`, which writes to stdout. `>` sent stdout into `report.txt`, so the message went into the file; the pipe sent it into `wc -l`, which counted it as a line of report.",
            [
                "v0.2's message is on stdout (via `print`)",
                "Both `>` and the pipe take stdout, so the error went into the file and was counted by `wc -l`",
            ],
            "\"The program crashed silently\" is wrong: it wrote the message, just into the file. \"The file was not found, so nothing was printed\" also misses that the message exists. Explaining only one of the two commands (the file or the count) earns one mark.",
        ),
        part(
            "2",
            "Explain what v0.3 does differently, using the words stdout and stderr.",
            2,
            "v0.3 writes the error to stderr and keeps stdout for the report. Redirection and pipes take only stdout, so the message appears on screen, `report.txt` stays empty and `wc -l` counts 0.",
            [
                "v0.3 writes the error to stderr (`typer.echo(..., err=True)`) and keeps stdout for the report",
                "Explains the transcript: stderr is not redirected or piped, so the message reaches the screen, the file stays empty and `wc -l` counts 0",
            ],
            "Saying \"v0.3 shows the error\" without the two stream names misses what the part asks. \"stderr is for errors and stdout for output\" is the rule; the marks are for applying it to these lines.",
        ),
        part(
            "3",
            "Both versions print `1` for `echo $?`. Why does that number matter to a script, and did v0.3 change it?",
            2,
            "The exit code is how scripts, `&&` and CI know the command failed: with 1, a following `&& echo saved` would not run. v0.2 already exited with 1 via `sys.exit(1)`; v0.3 keeps it with `typer.Exit`. What v0.3 fixed was where the message goes.",
            [
                "Explains that scripts, `&&` and CI decide by the exit code (non-zero means failure)",
                "Notes that the exit code was already 1 in v0.2: the improvement in v0.3 is the stream, not the code",
            ],
            "\"1 means there was one error\" misreads the number: it is a status, not a count. Claiming v0.3 introduced the non-zero exit code misreads the transcripts, where both show `1`.",
        ),
    ],
    """
These transcripts are real runs of the two tags. The lesson is in the two streams: v0.2's `print` put the error on stdout, so redirection hid it in the file and a pipe counted it as data; v0.3's `typer.echo(..., err=True)` keeps it on stderr, where it always reaches the person. The exit code, which machines read, was already right in v0.2. Failing well needs both: the message on stderr for people, a non-zero exit code for programs.
""",
    "6–8",
)

# ---- s8 ----
mcq(
    39, "core", ["concept"], 8, "S7 slide 20", "slides", "source",
    """
Slide 20 says "print is not logging". Which is a reason it gives for using `logging` for a message like "skipped malformed row 3"?
""",
    (
        "Each message has a level and can be silenced, filtered or sent to a file without code edits",
        "Slide 20: \"Can be silenced, filtered, sent to a file: without editing the code.\" Changing one line of configuration changes what you see.",
    ),
    [
        (
            "Logged messages become part of the program's output, so the user sees them inside the saved report",
            "The opposite: `print` is for the program's output; logging is for its diary.",
        ),
        (
            "`logging` calls are checked by mypy and ruff, while `print` calls are ignored by both",
            "mypy and ruff check both calls the same way; neither tool decides between them.",
        ),
        (
            "`logging` stops the program when a warning is logged, so problems cannot be ignored",
            "Logging never stops anything. Stopping is what raising an exception does.",
        ),
    ],
    "c",
    """
Slide 20 lists what logging has and `print` lacks: a level (debug, info, warning, error), and control without editing the code (silence it, filter it, send it to a file). It also separates two kinds of text: "print is for the program's output; logging is for its diary." A skipped malformed row is diary: worth knowing when you investigate, noise inside the report.
""",
)

mcq(
    40, "exam", ["judgement"], 8, "S7 slide 20; S6 slide 14", "slides", "reasoning",
    """
`read_expenses` silently skips rows that do not have four fields. The team wants to know how many rows are skipped when the nightly report runs, without changing the report itself and without editing code to turn the messages on and off. Which change fits?
""",
    (
        "`logger.warning(...)` for each skipped row, with `logging.basicConfig` once in the shell",
        "Slide 20's own example. The level decides what is shown, set in one place.",
    ),
    [
        (
            "Raise `ValueError` on the first malformed row, so nobody can miss it",
            "That changes the behaviour: one bad row would stop the whole report. Session 6's comment explains the skipping is deliberate (a bank export's summary row).",
        ),
        (
            "Add `print(f\"skipped row {line_number}\")` in `read_expenses` for each skipped row",
            "The diary ends up inside the report and anything piped from it, and turning it off means editing the code.",
        ),
        (
            "Call `typer.echo(..., err=True)` inside `read_expenses`, so each message goes to stderr instead",
            "stderr is right for errors, but this puts terminal I/O back into `report.py`, which v0.3 removed, and it cannot be silenced without editing.",
        ),
    ],
    "a",
    """
The requirements are three: record the skipped rows, leave the report unchanged, and switch the messages on or off without touching code. `print` fails the second and third; raising fails the second (the report would stop); `typer.echo` inside the module fails the third and drags I/O back into the core's module. A logger call at `warning` level, with the configuration done once in the shell, meets all three: the warning goes to stderr, the report on stdout is untouched, and changing the level in `basicConfig` controls what appears.
""",
)

mcq(
    41, "exam", ["predict-output", "read-code"], 8, "S7 slide 20; run on a logging variant of v0.3", "slides", "run",
    """
A team adds logging to the demo. In `report.py`:

```python
logger = logging.getLogger(__name__)
...
        for line_number, row in enumerate(reader, start=2):
            if len(row) != FIELDS_PER_ROW:
                logger.warning("skipped malformed row %d in %s", line_number, path)
                continue
            ...
    logger.info("read %d expenses from %s", len(expenses), path)
```

In `cli.py`, the typer callback:

```python
@app.callback()
def main() -> None:
    logging.basicConfig(level=logging.WARNING)
```

`small.csv` has a header, two good rows and one broken row (`broken`, on line 3). Besides the report itself, which log messages appear when you run `uv run expenses report small.csv`?
""",
    (
        "Only the warning about row 3",
        "Level `WARNING` shows warnings and errors and hides `info` and `debug`.",
    ),
    [
        (
            "The warning about row 3 and the line saying two expenses were read",
            "The second one is `info`, which is below `WARNING`, so it is filtered out.",
        ),
        (
            "None, because logging writes to a log file, not to the terminal",
            "`basicConfig` without a file name writes to the terminal (stderr). Sending logs to a file is an option you have to ask for.",
        ),
        (
            "Only the line saying two expenses were read, because `basicConfig` shows messages up to the level given",
            "Backwards: the level is a minimum. Messages at that level and above are shown.",
        ),
    ],
    "a",
    """
The level in `basicConfig` is a threshold: messages at that level or more serious pass, the rest are dropped. We ran it: at `WARNING` the only log line is `WARNING:expense_tracker.report:skipped malformed row 3 in small.csv`. Changing the callback to `level=logging.INFO` added `INFO:expense_tracker.report:read 2 expenses from small.csv`, with no change to `report.py`. That is slide 20's point: what you see is controlled in one place, in the shell.
""",
)

mcq(
    42, "beyond", ["predict-output", "concept"], 8, "S7 slides 19–20; run on a logging variant of v0.3", "slides", "run",
    """
The demo now logs `skipped malformed row ...` as a warning from `read_expenses`, and the shell calls `logging.basicConfig(level=logging.WARNING)` with nothing else configured. A user runs:

```console
$ uv run expenses report small.csv > report.txt
```

`small.csv` has one broken row. Where does the warning end up?
""",
    (
        "On the screen, because `basicConfig` writes to stderr unless told otherwise",
        "Log messages and the report travel on different streams, so redirecting one leaves the other alone.",
    ),
    [
        (
            "In `report.txt`, above the report, because `>` captures everything the program writes",
            "`>` captures stdout only. The log handler writes to stderr.",
        ),
        (
            "Nowhere, because logging is switched off while the output is redirected",
            "Redirection changes where stdout goes; it does not switch logging on or off.",
        ),
        (
            "In a file named after the logger, `expense_tracker.report`, because each module logs to its own file",
            "`getLogger(__name__)` names the logger; it does not create files. Without a file name, `basicConfig` writes to stderr.",
        ),
    ],
    "d",
    """
This is one step past the slide. We ran it: the terminal showed `WARNING:expense_tracker.report:skipped malformed row 3 in small.csv`, and `report.txt` held the clean report. `basicConfig` sets up a handler that writes to stderr by default, so the diary follows the same rule as error messages: it reaches the person, and it never pollutes the program's output. Had the team used `print` for the warning, it would be sitting in the middle of `report.txt`.
""",
)

mcq(
    43, "beyond", ["judgement"], 8, "S7 slide 20; S5 slides 7–8 (options); run on a variant of v0.3", "slides", "run",
    """
The team wants a `--verbose` option that also shows `info` messages such as "read 420 expenses from expenses.csv". The core modules already log with `logging.getLogger(__name__)`. Where does the change belong?
""",
    (
        "In the shell: the typer callback reads `--verbose` and sets the level in `basicConfig`",
        "Configure once, in the shell. The modules keep logging as before; only the threshold moves.",
    ),
    [
        (
            "In the core: wrap every `logger.info(...)` call in `if verbose:`",
            "Every core function would need to know about a command-line option, and the level mechanism already does this filtering.",
        ),
        (
            "In the core: add a `verbose: bool` parameter to every function that logs, and pass it down",
            "That threads a terminal concern through pure functions and changes every call and every test.",
        ),
        (
            "In the shell: each command takes `--verbose` and, when it is set, prints the row counts itself",
            "That repeats in every command what one logging level already does, and turns diary messages into program output, which slide 20 says to avoid.",
        ),
    ],
    "c",
    """
Slide 20: configure once, in the shell. A command-line option is shell business anyway, so the callback reads it and sets the level: `logging.basicConfig(level=logging.INFO if verbose else logging.WARNING)`. We tried it on a copy of the demo: without the option only the warning appears; with `expenses --verbose report small.csv` the `info` line appears too, and `report.py` was not touched. Every alternative pushes knowledge of the terminal into the core, which is what the split exists to prevent.
""",
)

sort_q(
    44, "hard", ["judgement"], 8, "S7 slides 19–20; S5 slide 9; expense-tracker cli.py; labs/01-scaffold.md", "slides", "reasoning",
    """
For each message from an expense-tracker run, where should it go?
""",
    [
        ("stdout", "stdout: the program's output"),
        ("stderr", "stderr: an error for the person"),
        ("log", "logging: the program's diary"),
    ],
    [
        (
            "The report's line `TOTAL                    50.00`",
            "stdout",
            "It is the result the user asked for: the program's output, which they may redirect to a file.",
        ),
        (
            "`could not read nosuch.csv`",
            "stderr",
            "A failure the person must see even when the output is redirected. Paired with exit code 1.",
        ),
        (
            "`skipped malformed row 3 in small.csv`",
            "log",
            "Slide 20's own example: diary, at warning level.",
        ),
        (
            "`amount must be positive`, after `expenses add \"Bar Ramon\" 0`",
            "stderr",
            "Session 5's bad-input message: an error for the person, with exit code 1.",
        ),
        (
            "`read 420 rows in 0.03 s`",
            "log",
            "Useful when investigating, noise otherwise: `info` or `debug`.",
        ),
        (
            "`added Bar Ramon (dining) 12.50 to data/expenses.csv`, after a successful `add`",
            "stdout",
            "The confirmation is what the command produces when it succeeds; the demo's `add` and lab 01's example print it to stdout.",
        ),
        (
            "`entering total_by_category with 414 expenses`",
            "log",
            "A developer's trace: `debug`, off unless you are hunting a problem.",
        ),
        (
            "The CSV lines an `export` command writes for the user to save with `>`",
            "stdout",
            "That is the output itself; anything else on stdout would corrupt the exported file.",
        ),
    ],
    """
Three channels, three readers. stdout is the program's output, what the user asked for and may send into a file or a pipe. stderr is for messages the person must see about a failure, and it travels with a non-zero exit code. Logging is the diary for whoever investigates, with levels that decide what is shown. The test for each message: would it corrupt a saved report (then not stdout), is the run a failure (then stderr), is it only useful when investigating (then logging)?
""",
)

open_q(
    45, "exam", ["read-code", "judgement"], 8, "S7 slide 20; S8 slide 28", "slides", "reasoning",
    """
While hunting a pricing bug, a parking-lot teammate added these lines and pushed them:

```python
def fee(minutes: int) -> float:
    print("DEBUG fee called with", minutes)
    band = band_for(minutes)
    print("DEBUG band chosen:", band)
    return band.price_per_hour * hours_charged(minutes)
```

Since then the `report` command's output starts with dozens of `DEBUG` lines, and a `CliRunner` test that compares the command's output has started failing.
""",
    [
        part(
            "1",
            "Name two problems these `print` lines cause.",
            2,
            "They put diary messages into the program's output: the report, any file or pipe it is sent to, and the output the `CliRunner` test compares. They also make `fee`, a core function, touch the world, and the only way to turn them off is to find and delete each one.",
            [
                "Debug text is mixed into the program's output (the report, redirected files or pipes, tests that compare output)",
                "A core function now does I/O, breaking the core rule (it is noisy everywhere it is called, including every test)",
                "They cannot be switched off or filtered without editing the code",
            ],
            "\"Prints are ugly\" names no consequence, so it earns nothing. Two points that say the same thing (\"the report is messy\" and \"the output has extra lines\") count once. The strongest answers name one effect on the output or the tests and one on how the messages are controlled.",
        ),
        part(
            "2",
            "What should the teammate use instead, and where is it configured?",
            2,
            "A module logger, `logging.getLogger(__name__)`, with `logger.debug(...)` for these messages. Logging is configured once, in the shell (for example the typer callback) with `logging.basicConfig`: normally at `WARNING`, lowered to `DEBUG` only while hunting the bug.",
            [
                "`logging.getLogger(__name__)` and `logger.debug` (a debug level) for the messages",
                "Configured once, in the shell, with `logging.basicConfig`",
                "Explains that the level hides the debug messages normally and shows them when lowered, without editing `fee`",
            ],
            "\"Use logging\" without a level or a place to configure it is half an answer. Configuring logging inside `fee` or in every module repeats the mistake in a new form. Swapping `print` for `typer.echo(..., err=True)` moves the noise to stderr but still puts terminal I/O in the core and still cannot be switched off.",
        ),
        part(
            "3",
            "Which output of this program should still go through `print` or `typer.echo`?",
            1,
            "The program's real output: the report lines and receipts, printed by the shell. Diary messages go to logging, and errors to stderr.",
            [
                "The program's output (the report lines, the receipt) printed by the shell, as distinct from diary messages and errors",
            ],
            "\"Nothing should use print\" goes too far: the program still has to show its result to the user. \"Everything except DEBUG\" misses that errors belong on stderr, not on stdout with the report.",
        ),
    ],
    """
Slide 20 in a real situation. The `print` lines broke two rules at once: computation is not output (the core now prints), and print is for the program's output, not its diary. The fix keeps the messages but moves them to a channel with levels: `logger.debug` in the module, `basicConfig` in the shell. The report and the receipts stay on stdout, which is what the `CliRunner` test was checking all along.
""",
    "5–7",
)

# ---- added after review (runs in $SCRATCH/work/core-shell-failing-fix/) ----
mcq(
    46, "beyond", ["read-tool-output", "judgement"], 7, "S8 slides 21, 24; S7 slide 19; expense-tracker tests/test_io.py (v0.4); run on a variant of v0.4", "slides", "run",
    """
Suppose the v0.4 demo's missing-file test were slide 21's version, which checks only the exit code:

```python
def test_missing_file_exits_with_one() -> None:
    result = runner.invoke(app, ["report", "nosuch.csv"])
    assert result.exit_code == 1
```

A teammate changes the error line in `report` from `typer.echo(f"could not read {path}", err=True)` to `print(f"could not read {path}")`, keeping `raise typer.Exit(1) from None`. Then:

```console
$ uv run ruff check . && uv run mypy src tests && uv run pytest -q
All checks passed!
Success: no issues found in 6 source files
........................                                                 [100%]
24 passed in 0.05s
```

What can you conclude?
""",
    (
        "A regression got through: the test checks the exit code but not the stream; check `result.stderr` too",
        "The test runs the error path but asserts only `exit_code == 1`, so moving the message to stdout passes. The repo's `test_io.py` also asserts that the message is in `result.stderr`, and that line would have failed.",
    ),
    [
        (
            "The change is safe: ruff, mypy and pytest are all green, so the behaviour of `report` is unchanged",
            "CI is the referee, not the judge: it reports what the tests check. Nothing here checks which stream the message uses, so green says nothing about it.",
        ),
        (
            "The change is safe, because scripts and `&&` read the exit code, and the exit code is still 1 after the change",
            "Scripts read the exit code, but people read the message. With `print`, `> report.txt` hides the error inside the file and a pipe counts it as data.",
        ),
        (
            "The checks missed it because `CliRunner` does not capture text that a command writes with `print`",
            "`CliRunner` captures `print` without trouble: the message is in `result.stdout`. The test never looks at either stream.",
        ),
    ],
    "d",
    """
We ran this on a copy of the v0.4 demo, with the error line changed to `print` and the missing-file test cut down to slide 21's exit-code check: ruff, mypy and all 24 tests passed, while `uv run expenses report nosuch.csv > report.txt` hid the error inside `report.txt`. A test protects only what it asserts. Session 8's warning about coverage applies: the error path ran, and nothing checked where its message went. The repo's real `test_io.py` adds `assert "could not read nosuch.csv" in result.stderr`, the line that pins slide 19's rule that errors go to stderr.
""",
)

mcq(
    47, "beyond", ["read-code", "judgement"], 1, "S7 slides 13, 15; labs/08-tdd.md step 1; expense-tracker cli.py (`add` reads the clock in the shell)", "slides", "reasoning",
    """
A library group's core function:

```python
def overdue_books(books: list[Book], today: date) -> list[Book]:
    return [book for book in books if book.due < today]
```

The `overdue` command calls it as `overdue_books(books, date.today())`. A teammate proposes dropping the `today` parameter and calling `date.today()` inside the function, "so callers have one less argument to pass". The function would still have no `open`, no `print` and no `sys.exit`. What is the strongest objection?
""",
    (
        "Reading the clock touches the world: the same books give a different answer tomorrow",
        "Today's date is input from outside, like a file. Passed in, a test can use `date(2026, 10, 22)` and know the answer; read inside, the expected result changes as the calendar moves.",
    ),
    [
        (
            "None: with no `open`, `print` or `sys.exit` it is still core, and a shorter call is cleaner",
            "The slide's list names the usual ways to touch the world, but the rule behind it is data in, data out. A function that reads the clock answers differently tomorrow for the same arguments.",
        ),
        (
            "`date.today()` is slow, so calling it inside a function that runs in a loop wastes time on every call",
            "Speed is not the issue; a call to the clock is cheap. The issue is that the result no longer depends only on the arguments.",
        ),
        (
            "mypy cannot check `date.today()`, so the function's return type would no longer be verified at all",
            "`date.today()` is fully typed, and mypy checks it like any other call. Types do not change here; testability does.",
        ),
    ],
    "b",
    """
Slide 13's core is data in, data out: the same values always give the same answer. `open`, `print` and `sys.exit` are the obvious ways to touch the world, and lab 08 adds the network, but the clock is one too. With `today` as a parameter, the shell reads the clock once, as the demo's `add` command does in `cli.py` with `datetime.date.today()`, and a test passes a fixed date and checks a fixed list. With `date.today()` inside, a test that passes today can fail next week unless it fakes the date: the expensive kind of test the split exists to avoid.
""",
)

sort_q(
    48, "hard", ["read-code", "predict-output"], 6, "S7 slide 18; expense-tracker v0.1 report.py (run with each change)", "history", "run",
    """
This is v0.1's `run()` (shortened; the rest prints the report):

```python
def run(path, cat, minimum):
    rows = []
    try:
        f = open(path)
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            # skip rows that do not have all four fields
            if len(row) == 4:
                rows.append((row[0], row[1], row[2], float(row[3])))
        f.close()
    except:
        print("could not read " + path)
        sys.exit(1)

    print("Expense report for " + path)
    ...
    totals = calculate_totals(rows, cat, minimum)
    ...
```

Each line below is one change to a working v0.1, or one event, taken on its own. What does the user get from `uv run expenses report`?
""",
    [
        ("message", "`could not read ...` and exit code 1"),
        ("traceback", "A traceback that names the bug"),
        ("report", "A normal report and exit code 0"),
    ],
    [
        (
            "The file name is misspelt, so the file does not exist",
            "message",
            "`open` raises `FileNotFoundError` inside the `try`. This is the case the handler was written for, and the message is fair.",
        ),
        (
            "An amount in the file reads `forty`",
            "message",
            "`float(\"forty\")` raises `ValueError` inside the `try`: bad input, reported as a reading problem.",
        ),
        (
            "Someone deletes `import csv` from the top of `report.py`",
            "message",
            "`csv.reader` raises `NameError` inside the `try`, and the bare except reports a missing import as a problem with the file.",
        ),
        (
            "Someone mistypes `float` as `flaot` in the reading loop",
            "message",
            "Another `NameError` inside the `try`, disguised the same way: the file is fine and the message blames it.",
        ),
        (
            "The user presses Ctrl-C while a large file is still being read",
            "message",
            "`KeyboardInterrupt` is raised inside the `try`, and a bare except catches even that.",
        ),
        (
            "Someone mistypes `path` as `pth` in the `Expense report for` line",
            "traceback",
            "That line runs after the `try` has finished, so nothing catches the `NameError`: the program stops with a traceback naming the line.",
        ),
        (
            "Someone mistypes `calculate_totals` as `calculate_total`",
            "traceback",
            "The call is after the `try`, so the `NameError` escapes as a traceback, after the header has already been printed.",
        ),
        (
            "One row in the file has only three fields",
            "report",
            "Not an error at all: the length check skips the row and the report covers the others.",
        ),
        (
            "The file has its header line and no expenses",
            "report",
            "`next(reader)` reads the header, the loop has nothing to do, and the report shows `TOTAL 0.00` with exit code 0.",
        ),
    ],
    """
A bare `except:` catches everything raised inside its `try`, and nothing outside it. In v0.1 the `try` covers opening and parsing the file, so real input problems (a missing file, `forty`), bugs that surface on those lines (a missing `import csv`, `flaot`) and even Ctrl-C all end in the same `could not read` and exit code 1. The header `print` and the call to `calculate_totals` come after the `try`, so a typo there escapes as a traceback. We ran every case on v0.1. Reading where a `try` starts and ends is part of judging what a handler hides.
""",
)

open_q(
    49, "hard", ["read-tool-output", "judgement"], 6, "S7 slides 17-18; S8 slides 7, 9, 20", "slides", "run",
    """
After a change to the reading code, CI prints this (trimmed: the long path and the list of available fixtures are shortened):

```text
tests/test_amounts.py FFE.                                               [ 80%]
tests/test_extra.py .                                                    [100%]

==================================== ERRORS ====================================
_____________________ ERROR at setup of test_reads_a_file ______________________
file tests/test_amounts.py, line 17
  def test_reads_a_file(tmp_pth: Path) -> None:
E       fixture 'tmp_pth' not found
>       available fixtures: capfd, caplog, capsys, monkeypatch, tmp_path, tmp_path_factory, ...
=================================== FAILURES ===================================
________________________ test_a_bad_amount_is_rejected _________________________

    def test_a_bad_amount_is_rejected() -> None:
>       with pytest.raises(ValueError):
             ^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE ValueError

tests/test_amounts.py:9: Failed
___________________________ test_largest_of_nothing ____________________________

    def test_largest_of_nothing() -> None:
>       assert largest_expense([]) == 0
E       assert None == 0
E        +  where None = largest_expense([])

tests/test_amounts.py:14: AssertionError
=========================== short test summary info ============================
FAILED tests/test_amounts.py::test_a_bad_amount_is_rejected - Failed: DID NOT...
FAILED tests/test_amounts.py::test_largest_of_nothing - assert None == 0
ERROR tests/test_amounts.py::test_reads_a_file
===================== 2 failed, 2 passed, 1 error in 0.01s =====================
```

In the code, `parse_amount` wraps `float(text)` in a bare `except:` that returns `0.0`, and `largest_expense` returns `None` for an empty list, as the course's table says for "no result".
""",
    [
        part(
            "1",
            "For each of the three problems, say whether the test, the code or the setup is at fault, in one phrase each.",
            3,
            "`test_a_bad_amount_is_rejected`: the code is at fault, because the bare `except` swallows the bad amount and returns `0.0`. `test_largest_of_nothing`: the test is wrong, because an empty list should give `None`, not `0`. `test_reads_a_file`: the setup, because the test asks for a fixture called `tmp_pth` that does not exist.",
            [
                "DID NOT RAISE: the code is at fault, since the bare `except` hides the bad input",
                "assert None == 0: the test is wrong, since `None` is the right answer for no result",
                "fixture 'tmp_pth' not found: a setup error, the test never ran (the fixture name is wrong)",
            ],
            "\"Three failing tests\" misses that the summary line says 2 failed and 1 error: an error at setup means the test body never ran. Blaming the code for `None == 0` ignores the course's table, where \"no result\" is `None` rather than a made-up number.",
        ),
        part(
            "2",
            "Which one do you fix first, and why?",
            2,
            "The swallowed error in `parse_amount`. It is the only fault in the program itself: a user who types `twelve` gets `0.0` and no message. The other two are mistakes in the tests, which cannot hurt anyone.",
            [
                "Chooses the bare `except` in the code (or the setup error, with the reason that a test which never ran proves nothing)",
                "Gives a reason in terms of the user or of what the evidence shows",
            ],
            "\"The first one in the list\" is an order with no reason. \"Fix whichever is quickest\" is a plan for a green run, not for the program. A good order says which failure can hurt a user.",
        ),
        part(
            "3",
            "A teammate marks the two failing tests with `skip` so that CI turns green. Do you accept that?",
            1,
            "No. Skipping hides the evidence: one of them is a real bug in the code, and the other should be corrected, not removed. CI would be green and the bug would still be there.",
            [
                "Refuses, because skipping hides a real failure instead of fixing the cause (the referee, not the judge)",
            ],
            "\"Yes, because the tests are probably wrong\" accepts a green run without reading the failures. The course answer for tests is the same as for `# type: ignore`: a quiet check means nothing if the fault is still there.",
        ),
    ],
    """
Sample Q9's shape on pytest output instead of mypy. Read the last line first: 2 failed, 1 error. The error is a setup problem, the test body never ran. The two failures differ in who is wrong. `DID NOT RAISE` points at the code, which is the bare `except` of session 7: it hides a bad amount and replaces it with a number. `assert None == 0` points at the test, which disagrees with the course's table (nothing found: return `None`). The order of work follows from who can be hurt, and skipping tests to get green is the same shortcut as ignoring a type error.
""",
    "6–8",
)

# ---------------------------------------------------------------------------
# Terms, traps, flashcards
# ---------------------------------------------------------------------------

TERMS = [
    ("Functional core", "The inner layer of a program: pure functions that take values and return values. No `open`, no `print`, no `sys.exit`.", 1),
    ("Imperative shell", "The thin outer layer and the only place that touches the world: it reads files, prints, and sets the exit code. In the demo, the commands in `cli.py`.", 1),
    ("Pure function", "A function whose result depends only on its arguments and which touches nothing outside itself: data in, data out. `total_by_category` is one.", 1),
    ("Separate I/O from logic", "The refactoring move that pulls the decision out of a function that reads and prints, leaving a pure function and a thin wrapper. The demo's `run()` split into read, compute, format.", 4),
    ("Structure criterion", "Partial-submission rubric criterion: 3 means computation in functions that take and return plain data, reading and printing in a thin outer layer, and no module doing both.", 4),
    ("Exception", "An object a function raises when it cannot carry on. It travels up through the callers until one catches it, or the program stops with a traceback.", 5),
    ("Return code (`-1`)", "A special value returned to mean failure. It looks like data and adds up silently: \"Do not return -1 and hope somebody checks.\"", 5),
    ("Bare except", "`except:` with no exception named. It catches everything raised inside its `try`, so a typo, a missing import or Ctrl-C all produce the same handler's message.", 6),
    ("`OSError`", "The family of operating-system failures: file not found (`FileNotFoundError`), permission denied, a folder where a file was expected.", 6),
    ("`ValueError`", "Raised when a value has the right type but unusable content, such as `float(\"forty\")`.", 6),
    ("`KeyboardInterrupt`", "What Ctrl-C raises inside a Python program. It is not an `Exception`, but a bare `except:` still catches it.", 6),
    ("Traceback", "Python's report of an uncaught exception: the chain of calls with files and lines, and the exception's name and message at the bottom.", 6),
    ("The boundary", "Where the core meets the shell and the outside world: the place where exceptions are caught and turned into a message on stderr and a non-zero exit code.", 7),
    ("stdout", "Standard output: the stream for the program's output, such as the report. `>` and pipes send it elsewhere.", 7),
    ("stderr", "Standard error: the stream for messages to the person. It still reaches the screen when stdout is redirected or piped.", 7),
    ("Exit code", "The number a program ends with: 0 means success, anything else failure. The shell, `&&` and CI read it.", 7),
    ("`typer.echo(..., err=True)`", "typer's print, sent to stderr. With `raise typer.Exit(code=1)` it is how the course's shell reports a failure.", 7),
    ("Logging level", "The seriousness of a log message: debug, info, warning, error. The configured level is a threshold; less serious messages are hidden.", 8),
    ("`logging.basicConfig`", "Sets up logging (level, destination) in one call. Called once, in the shell; modules only use `logging.getLogger(__name__)`.", 8),
]

TRAPS = [
    "`read_expenses` lives in `report.py`, so it is part of the core. **Wrong:** it opens a file, and slide 14 labels it shell. Core or shell is decided by what a function does, not by the file it is in.",
    "A function that prints its result is fine as long as it also returns it. **Wrong:** it still mixes computation with output, so every caller and every test gets the printing too, and a web page cannot reuse it cleanly. Return the value; print in the shell.",
    "A bare `except:` is the safe choice, because the program never crashes. **Wrong:** it hides every bug raised inside its `try` (a typo, a missing import, even Ctrl-C) behind one misleading message, and code after the `try` still crashes. Catch only what you can handle.",
    "`except Exception:` fixes a bare except. **Wrong:** ruff's `E722` goes quiet, but a typo or an `IndexError` is an `Exception` too and is still disguised. Name the failures you expect: `(OSError, ValueError)`.",
    "Returning `-1`, `0` or `[]` on failure is a simple way to report errors. **Wrong:** these look like data and flow into totals unnoticed, and mypy cannot help. Raise when the caller can't carry on; use `None` with `| None` in the type for a normal \"no result\".",
    "If the error message is printed, the exit code does not matter. **Wrong:** `&&`, scripts and CI read the exit code, not the text. A program that prints an error and exits 0 is a program that lies.",
    "Writing to stderr makes the exit code non-zero. **Wrong:** they are separate. `typer.echo(..., err=True)` decides where the message goes; `raise typer.Exit(code=1)` decides how the program ends. Failing well needs both.",
    "The core should catch its own errors and print a friendly message. **Wrong:** the core does not know who is calling. It raises; each shell (CLI, web page, test) decides how to show the failure.",
    "A traceback always means the error handling failed. **Wrong:** for a bug, a traceback that names the line is what the developer needs. The rubric's \"not a traceback\" is about bad input, which gets a clear message.",
    "Logging is `print` with a prefix. **Wrong:** messages have levels, can be silenced, filtered or sent to a file without editing the code, and go to stderr by default, away from the program's output.",
]

CARDS = [
    ("concept", "What does the functional core do, and what does it never do?", "Takes values, returns values. Never `open`, `print` or `sys.exit`.", 1),
    ("concept", "What is the imperative shell?", "The only place that touches the world: it reads files, prints, and sets the exit code. It should be thin.", 1),
    ("recall", "Lab 07's checklist: what counts as your project's I/O?", "Every place that reads or writes a file, calls `print`, or calls `sys.exit`. `typer.echo` and `raise typer.Exit` count too.", 1),
    ("reading", "`expenses = read_expenses(path)`: core or shell?", "Shell: it touches a file (slide 14), even though it lives in `report.py` and returns a value.", 2),
    ("reading", "`totals = total_by_category(expenses, category, minimum)`: core or shell?", "Core: pure. It does not know that a CSV exists; give it a list and it works.", 2),
    ("concept", "What did the commit \"Move printing and exiting out of the report module\" (between v0.2 and v0.3) change?", "The reading, error handling and printing moved from `run()` in `report.py` to the `report` command in `cli.py`, and the error now goes to stderr. Since then `report.py` has no `print` and no `sys.exit`. The next commit added pytest and strict mypy; the tag v0.3 sits on that one.", 2),
    ("concept", "Slide 15's three reasons for a functional core?", "Testable (pass a list, check the answer), reusable (CLI today, web page later), replaceable (session 17's database only changes the shell).", 3),
    ("concept", "Why can't you test a function that prints its result?", "It returns `None`; you cannot assert on a `print`. Make it return, and print in the shell.", 3),
    ("distinction", "Session 8's 2×2: Algorithms vs Coordinators?", "Algorithms: high benefit, low cost to test (pure logic). Coordinators: low benefit, high cost (code that only wires parts together, like the shell).", 3),
    ("recall", "Partial rubric, Structure 3?", "`src/` layout; computation in functions that take and return plain data; reading files and printing in a thin outer layer; no module does both.", 4),
    ("distinction", "Structure 2 vs Structure 1?", "2: one function still mixes computing with reading or printing. 1: logic is mostly inside the command functions.", 4),
    ("concept", "First refactoring for a function that reads, computes and prints?", "Move the decision into a function that takes values and returns the answer; leave reading and printing in a thin wrapper; check the output is unchanged; then test the new function.", 4),
    ("recall", "Slide 17's table: three situations and what to do.", "Caller can't carry on: raise. A normal \"no result\": return `None` or empty. Crossing to the shell: translate to an exit code.", 5),
    ("concept", "Why not return `-1` on failure?", "It looks like a number, so it flows into totals silently, and mypy cannot see it. \"Do not return -1 and hope somebody checks.\"", 5),
    ("distinction", "`return None` vs `raise`?", "`None`: nothing is a normal answer (largest of an empty list, a plate not in the car park). Raise: going on would be nonsense (a missing file, an amount of `forty`).", 5),
    ("concept", "What does a bare `except:` hide?", "Every error raised inside its `try`: a typo, a missing import, even Ctrl-C. All become \"could not read\".", 6),
    ("recall", "Which exceptions does v0.2 catch, and what does each mean?", "`OSError`: the file is missing or unreadable. `ValueError`: an amount is not a number.", 6),
    ("distinction", "Bad input vs a bug: what should each produce?", "Bad input: a clear message on stderr and a non-zero exit code. A bug: a traceback naming the line, for the developer.", 6),
    ("reading", "ruff says `E722 Do not use bare except`. Is `except Exception:` the fix?", "No. Ruff passes, but bugs such as `NameError` or `IndexError` are still `Exception`s and still disguised. Name `(OSError, ValueError)`.", 6),
    ("concept", "Fail loudly at the boundary: who does what?", "Core: raises on bad input, never prints an error. Shell: catches it, prints to stderr, exits non-zero.", 7),
    ("reading", "`typer.echo(msg, err=True)` and `raise typer.Exit(code=1)`: what does each do?", "The first writes the message to stderr; the second ends the command with exit code 1.", 7),
    ("concept", "Why do errors go to stderr?", "Redirecting or piping stdout leaves stderr on screen, so the person still sees the error; and tests can check `result.stderr` separately.", 7),
    ("concept", "Complete session 5's line: \"A program that prints an error and exits 0...\"", "\"...is a program that lies.\" `&&`, scripts and CI trust the exit code.", 7),
    ("distinction", "`print` vs logging?", "`print` is for the program's output; logging is for its diary, with levels and control without editing the code.", 8),
    ("recall", "The logging levels, from chatty to serious?", "debug, info, warning, error.", 8),
    ("concept", "Where and how is logging configured?", "Once, in the shell: `logging.basicConfig(level=logging.INFO)`. Modules only call `logging.getLogger(__name__)` and log.", 8),
]

# ---------------------------------------------------------------------------
# Module
# ---------------------------------------------------------------------------

module: dict[str, Any] = {
    "id": MID,
    "order": 7,
    "module": "M2",
    "title": "Functional core, imperative shell, and failing well",
    "sessions": [7],
    "predicted": False,
    "sources": [
        "slides-session-7 (slides 12–20)",
        "slides-session-8 (slides 17–23, 28–29)",
        "slides-session-5 (slide 9)",
        "partial-rubric.txt (Structure, Tests, Functionality)",
        "labs/07-refactor.md Part 2",
        "labs/08-tdd.md",
        "expense-tracker v0.1, 9d6c607, 04d699f (v0.2), 15836e1, tests/test_io.py (v0.4)",
    ],
    "summary_md": T(
        """
This module covers the second half of session 7: where a program's input and output should live, and what it should do when something goes wrong. The rule is functional core, imperative shell: pure functions that take values and return values in the middle, and a thin outer layer that reads files, prints and exits. Failing well follows from it: the core raises, the shell catches only what it can handle, writes the reason to stderr and exits non-zero, and the program's diary goes to logging, not `print`. The expense-tracker's commit `15836e1` (between v0.2 and v0.3) is the worked example, and the partial submission's Structure criterion marks this split.
"""
    ),
    "exam_focus_md": T(
        """
- Sort functions from a project like the parking lot or the gradebook into core, shell, or "mixed: needs splitting", and say what the first refactoring is.
- Read a function that reads, computes and prints (the sample paper's Q5 and Q7 shape): describe the split in words and the tests it makes possible.
- Decide between raising, returning `None` or empty, and an exit code; spot the `-1` that nobody checks.
- Predict what a bare `except:` does with a typo or Ctrl-C, and judge `except Exception:` offered as a fix.
- Read the v0.2 → v0.3 diff, or a transcript with `>` or a pipe, and explain where the error went and why stderr matters.
- Judge an exit code: a program that prints an error and exits 0 is a program that lies.
- Choose between `print` and logging, and say where logging is configured.
"""
    ),
    "sections": SECTIONS,
    "terms": [
        {"term": t, "definition_md": T(d), "section_ref": sid(s)} for t, d, s in TERMS
    ],
    "traps": [T(t) for t in TRAPS],
    "flashcards": [
        {
            "id": fid(i),
            "front_md": T(front),
            "back_md": T(back),
            "kind": kind,
            "section_ref": sid(s),
        }
        for i, (kind, front, back, s) in enumerate(CARDS, start=1)
    ],
    "questions": sorted(Q, key=lambda q: q["id"]),
}


def main() -> None:
    ids = [q["id"] for q in Q]
    assert len(ids) == len(set(ids)), "duplicate question ids"
    OUT.write_text(json.dumps(module, ensure_ascii=False, indent=1) + "\n")
    print(f"wrote {OUT} ({len(Q)} questions, {len(CARDS)} cards, {len(TERMS)} terms)")


if __name__ == "__main__":
    main()
