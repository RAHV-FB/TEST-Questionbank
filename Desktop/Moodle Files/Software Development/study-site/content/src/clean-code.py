"""Generate content/clean-code.json (session 6: clean code, naming and responsibility).

Every tool output quoted below was produced by running the tool in the course sandbox
(ruff 0.16.9, mypy 2.4.0, Python 3.13, pytest) from the work folder
scratchpad/work/clean-code/runs/, then trimmed. Paths were rewritten to project-relative ones.

Run:  uv run python content/src/clean-code.py
"""

from __future__ import annotations

import json
import textwrap
from collections import Counter
from pathlib import Path
from typing import Any

MID = "clean-code"
OUT = Path(__file__).resolve().parent.parent / f"{MID}.json"


def md(text: str) -> str:
    """Dedent a triple-quoted block and strip the surrounding blank lines."""
    return textwrap.dedent(text).strip("\n")


def sec(n: int) -> str:
    return f"{MID}-s{n}"


# ---------------------------------------------------------------------------
# Shared artefacts (code from the slides, the history patch, and real runs)
# ---------------------------------------------------------------------------

CALC = md(
    """
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
    ```
    """
)

INVOICE_TOTAL = md(
    """
    ```python
    def invoice_total(lines, tax_rate, discount_rate):
        subtotal = 0
        for line in lines:
            subtotal += line.price * line.quantity
        discounted = subtotal * (1 - discount_rate)
        return discounted * (1 + tax_rate)
    ```
    """
)

PYRAMID = md(
    """
    ```python
    for expense in expenses:
        if expense.category == category:
            if expense.amount >= minimum:
                totals[expense.category] += expense.amount
    ```
    """
)

GUARDS = md(
    """
    ```python
    for expense in expenses:
        if category != "" and expense.category != category:
            continue
        if expense.amount < minimum:
            continue
        totals[expense.category] += expense.amount
    ```
    """
)

# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------

SECTIONS: list[dict[str, Any]] = [
    {
        "id": sec(1),
        "heading": "The same logic, twice: an economic argument",
        "body_md": md(
            """
            Session 6 is about what happens after code runs. It opens with a puzzle: what does this function do?

            """
        )
        + "\n\n"
        + CALC
        + "\n\n"
        + md(
            """
            You can work it out, but only by tracing it: `c` is a list of something, `p[1] * p[2]` multiplies two fields of each item, `d` is taken off as a fraction and `i` is added on as one. Now the same logic, rewritten:
            """
        )
        + "\n\n"
        + INVOICE_TOTAL
        + "\n\n"
        + md(
            """
            For rates of zero or more, both give the same answer. Lab 07 uses this exact case: a pencil line (10 × 5) and a book line (50 × 2), 21% tax and a 10% discount, and both return 163.35. The slide's question is: **which one would you dare to change?** If the tax rule changes tomorrow, in `invoice_total` you find the line in seconds. In `calc` you first have to rebuild what `i` means, and you are never quite sure you got it right.

            That is why the course calls clean code **an economic argument, not an aesthetic one**:

            - Code is read far more often than it is written.
            - The cost of maintaining a codebase is the cost of understanding it.
            - The next reader is a teammate, or you in the future.

            Clean code is cheap to change. Unclean code is expensive to change, and the only code that never changes is the code that never runs. Session 1 listed the failure this prevents: "Six months on, nobody can read it, not even its author."

            Notice that nothing in `calc` is a bug. It runs and returns the right number. The problem is the price of every future change, and that price is paid by whoever reads it next.
            """
        ),
        "key_points": [
            "Same behaviour, different cost: the readable version is the one you dare to change.",
            "Code is read far more often than it is written; the cost of maintaining it is the cost of understanding it.",
            "The next reader is a teammate, or you in six months.",
            "Unclean code is not wrong code. It is expensive code.",
        ],
        "exam_note_md": "Expect a 'which one would you rather change, and why' question. Answer with the economic argument (reading cost, the next reader), not with 'it looks nicer'.",
        "source_ref": "S6 slides 6, 8–10; labs/07-refactor.md; S1 slide 6",
        "check": ["k_dare", "k_econ"],
    },
    {
        "id": sec(2),
        "heading": "Comments are for why",
        "body_md": md(
            """
            Introductory courses usually tell you to comment liberally, and in a learning context that is good advice: explaining what each line does helps you learn. Session 6 states a disagreement out loud and applies a different rule:

            > A comment that explains what the code does is a failure of naming.

            The reason, quoting Robert C. Martin: "Truth can only be found in one place: the code." Nothing checks a comment. When the code changes and the comment does not, the comment lies, and the reader trusts the wrong one. The slide adds the caveat: the advice makes sense depending on context; never follow it blindly.

            **Rename instead of comment.** In the slide's example the comment is a symptom:

            ```python
            # total of all expenses in this category above the threshold
            d[e[2]] = d[e[2]] + e[3]
            ```

            The fix is a name:

            ```python
            totals[expense.category] += expense.amount
            ```

            The new line says what the comment said, and it cannot drift out of date because it *is* the code. The demo did exactly this: v0.1 had `# skip rows that do not have all four fields` above `if len(row) == 4:`, and commit `5e9466d` deleted the comment and wrote `if len(row) == FIELDS_PER_ROW:`.

            **Legitimate comments explain what the code cannot say:** a business rule, a workaround with its reason, a deliberate oddity. The slide's example:

            ```python
            # Suppose the bank's export sometimes ends with a summary row with fewer fields.
            if len(row) == FIELDS_PER_ROW:
            ```

            The line tells you *what* happens (only rows with four fields are kept). Only the comment tells you *why* (the bank's file can end with a shorter summary row). Delete that comment and the next reader may remove the check as pointless.

            The test for any comment: if it restates the next line, delete the comment and improve the line.
            """
        ),
        "key_points": [
            "A comment that explains what the code does is a failure of naming.",
            "\"Truth can only be found in one place: the code.\"",
            "Keep comments that say why: a business rule, a workaround with its reason, a deliberate oddity.",
            "Commenting every line is advice for learners; never follow any of these rules blindly.",
        ],
        "exam_note_md": "Typical questions: pick the one comment worth keeping, or sort comments into keep and delete. The keeper always says something the code cannot.",
        "source_ref": "S6 slides 11, 13, 14; expense-tracker 5e9466d",
        "check": ["k_comment_rule", "k_legit", "s_comments"],
    },
    {
        "id": sec(3),
        "heading": "Names that work",
        "body_md": md(
            """
            The slide's table gives one rule per kind of name:

            | Kind | Bad | Better | Rule |
            |---|---|---|---|
            | Variable | `d`, `t`, `x` | `totals`, `expense` | says what it holds |
            | Function | `calculate_totals` | `total_by_category` | says what it returns |
            | Boolean | `flag` | `is_duplicate` | reads as a yes/no question |
            | Module | `utils.py` | `storage.py` | says what it is for |

            Each name is a promise to the reader. `totals` holds totals. `total_by_category` returns a total per category, while `calculate_totals` only says that some calculating happens and leaves "totals of what, grouped how?" for the reader to find out. Read the rule as: the name tells the caller what they get back. The demo's v0.2 functions `read_expenses` and `format_report` start with a verb but still name what comes back. `if is_duplicate:` reads as a sentence; `if flag:` tells you nothing. `utils.py` can hold anything, so over time it does; `storage.py` says what belongs in it and, by implication, what does not.

            The slide's rule of thumb: **a name that needs a comment is not finished.** The partial-submission rubric uses the same idea and lists `data`, `x` and `process` as vague names.

            Commit `f3bb801` ("Rename calculate_totals to total_by_category") is a whole commit of renaming and nothing else:

            ```diff
            -def calculate_totals(x, y, z):
            -    d = {}
            -    for e in x:
            -        if y != "" and e[CATEGORY] != y:
            +def total_by_category(expenses, category, minimum):
            +    totals = {}
            +    for expense in expenses:
            +        if category != "" and expense[CATEGORY] != category:
            ```

            The same commit turned `rows` into `expenses`, `cat` into `category`, `grand` into `grand_total`, `t` into `name, amount`, and `m`, `mr` into `largest_amount`, `largest`. The report it printed did not change by a single character. Only the cost of reading the code did.
            """
        ),
        "key_points": [
            "Variables say what they hold; functions say what they return.",
            "Booleans read as yes/no questions: `is_duplicate`, not `flag`.",
            "Modules say what they are for: `storage.py`, not `utils.py`.",
            "A name that needs a comment is not finished.",
        ],
        "exam_note_md": "Expect 'which name is best' with four candidates. Apply the rule for that kind of name; vague verbs (`process`, `handle`, `check`) and grab-bag modules (`utils`, `helpers`) are the usual distractors.",
        "source_ref": "S6 slide 15; expense-tracker f3bb801; partial-rubric criterion 3",
        "check": ["k_fname", "k_bool", "k_module"],
    },
    {
        "id": sec(4),
        "heading": "Magic numbers become named constants",
        "body_md": md(
            """
            A **magic number** is a constant that appears in the code without a name. The slide's example, simplified from v0.1's report:

            ```python
            print("-" * 40)
            print(name.ljust(20) + amount.rjust(10))
            ```

            What is 40? The width of the rule line. 20? The width of the category column. 10? The width of the amount column. The reader has to work that out, and if you want wider columns you must find every 20 in the file and decide, one by one, whether it is the same 20. In general it is better to name them as constants:

            ```python
            RULE_WIDTH = 40
            NAME_WIDTH = 20
            AMOUNT_WIDTH = 10
            ```

            Now you change the width once, in one place, with a name that says what it is.

            Commit `5e9466d` ("Replace magic numbers with named constants") also named the positions inside the expense tuple, plus the row length:

            ```python
            DATE = 0
            MERCHANT = 1
            CATEGORY = 2
            AMOUNT = 3
            FIELDS_PER_ROW = 4
            ```

            So `if e[3] < z:` became `if e[AMOUNT] < z:`, and after the renaming commit that followed, `if expense[AMOUNT] < minimum:`. Each step made the line say what it means, and none of them changed what it does.

            Two cautions. First, the name must say what the number *means*, not what it *is*: `FORTY = 40` is as magic as 40, and it becomes a lie the day the width changes to 50. Second, the same digits can mean two different things. If `0.21` is the VAT rate in one function and a savings target in another, two names (session 7 uses `STANDARD_VAT_RATE` as its example) make sure a change to one cannot silently change the other.
            """
        ),
        "key_points": [
            "A magic number is a constant in the code without a name.",
            "Name it once, at the top: then you change it once, in one place.",
            "The name says what the number means (`RULE_WIDTH`), never what it is (`FORTY`).",
            "`if e[3] < z` becomes `if expense[AMOUNT] < minimum`.",
        ],
        "exam_note_md": "In a 'what is wrong with this code' answer, a bare number such as 100 or 0.21 is an easy problem to name. Say what the name should express, not just 'make it a constant'.",
        "source_ref": "S6 slide 16; expense-tracker 5e9466d, f3bb801; S7 slide 5",
        "check": ["k_forty", "k_vat"],
    },
    {
        "id": sec(5),
        "heading": "One function, one job",
        "body_md": md(
            """
            The slide lists what `run()` did in v0.1:

            1. opens and parses the file
            2. handles the failure
            3. prints the header
            4. totals by category
            5. finds the largest and prints it

            Five jobs in one function. The course's test: **can I describe it without the word "and"?** "It reads the file and handles errors and prints a header and..." fails at the first "and". The idea has a name, the **Single Responsibility Principle**: a function should have one job, and so only one reason to change.

            Why it matters, in the economic terms of the first section:

            - To check the totals you would need a real CSV file on disk, and you would have to read the totals out of printed text.
            - To change the layout of the report you edit the same function that reads the file, so a layout change can break the reading.
            - To reuse the totals somewhere else (a web page, another report) you cannot, because they only exist inside `run()`.

            Commit `9d6c607` ("Separate reading and printing from the calculation") split `run()` into functions that each pass the test:

            | Function | Its one job |
            |---|---|
            | `read_expenses(path)` | returns the expenses in a file |
            | `total_by_category(expenses, category, minimum)` | returns the total per category |
            | `largest_expense(expenses)` | returns the largest expense |
            | `format_report(...)` | returns the lines of the report |
            | `run(...)` | calls the others in order; the only one that prints |

            Each piece can now be read, changed and tested on its own. The dining report still printed exactly the same text.

            The teacher's sample Q5 is this idea in one sentence: a function `process(rows)` that "reads a file, validates each row, calculates totals and prints a report" does several jobs at once, so it is hard to test and to change. Its name is a clue too: when the only honest verb is `process`, the function is probably doing several things.
            """
        ),
        "key_points": [
            "Describe the function without 'and'. If you cannot, it has more than one job.",
            "Single Responsibility Principle: one job, one reason to change.",
            "`run()` in v0.1 did five things; `9d6c607` split it into read, total, largest, format and run.",
            "Several jobs in one function: hard to test, hard to change, hard to reuse.",
        ],
        "exam_note_md": "Sample Q5 and Q7 both test this. Name the jobs, then the consequence (hard to test, hard to change); 'it is too long' is not the reason.",
        "source_ref": "S6 slide 18; expense-tracker 9d6c607; sample Q5",
        "check": ["k_q5var", "k_and", "s_jobs"],
    },
    {
        "id": sec(6),
        "heading": "Guard clauses, and computation is not output",
        "body_md": md(
            """
            **Guard clauses, not pyramids.** Nested conditions build a pyramid. The slide's version:

            ```python
            if e[2] == category:
                if e[3] >= minimum:
                    totals[e[2]] += e[3]
            ```

            Every level is one more condition you hold in your head before you reach the line that matters. The guard-clause version deals with the exceptions first and gets out:

            ```python
            if category != "" and expense.category != category:
                continue
            if expense.amount < minimum:
                continue
            totals[expense.category] += expense.amount
            ```

            "Deal with the exceptions first and get out. What is left is the main path." Each guard reads as one sentence (wrong category: skip; too small: skip), and the line that does the work sits at the outer level. Look closely and the guard version also gives an empty `category` a meaning, "no filter", which the pyramid did not have. When you reshape a condition, check that it still means what it meant.

            **Computation is not output.** The slide shows the shape v0.2 reached:

            ```python
            def total_by_category(expenses, category, minimum):   # returns data
                ...
            def format_report(...):                               # returns lines
                ...
            def run(...):                                         # the only one that prints
                ...
            ```

            "A function that returns can be tested, reused and read on its own. A function that prints can only be looked at." If `total_by_category` printed its totals, a test would have nothing to compare: the numbers would be on the screen, not in a value. Because it returns a list, a test can pass three expenses and check the answer, and a web page could reuse the same function later. That is why `9d6c607` turned every `print(...)` of the report into `lines.append(...)` inside `format_report`, and left a single loop of `print(line)` in `run()`.

            Session 7 names this shape (functional core, imperative shell), and v0.3 finishes the job by moving the last `print` and `sys.exit` out of `report.py`.
            """
        ),
        "key_points": [
            "Deal with the exceptions first and get out; what is left is the main path.",
            "A function that returns can be tested, reused and read on its own.",
            "A function that prints can only be looked at.",
            "In v0.2 only `run()` prints; `format_report` returns lines.",
        ],
        "exam_note_md": "When a function both computes and prints, say the consequence: a test has no return value to check. The fix in words: one function returns the data, the caller prints it.",
        "source_ref": "S6 slides 19–20; expense-tracker 9d6c607; S7 slides 6, 13",
        "check": ["k_guard", "k_testprint", "k_guard_diff"],
    },
    {
        "id": sec(7),
        "heading": "A tuple is a missing type",
        "body_md": md(
            """
            In v0.1 an expense was a tuple. Slide 22 shows how it was built (in `run()`) and how another function, `calculate_totals`, used it:

            ```python
            rows.append((row[0], row[1], row[2], float(row[3])))
            ...
            if e[3] < z:
            ```

            What is `e[3]`? Impossible to tell without looking up the line that built the tuple. The first two commits helped with index constants and names (`expense[AMOUNT] < minimum`), but the tuple itself still does not know what it holds. **A tuple is a missing type**: the program has a concept, an expense, that has no name in the code.

            Commit `017f926` ("Give an expense a type instead of a tuple") gave it one:

            ```python
            @dataclass(frozen=True)
            class Expense:
                date: str
                merchant: str
                category: str
                amount: float
            ```

            `e[3]` becomes `expense.amount`. The name is documentation, and the type checker knows it too.

            The slide insists that a dataclass is **a naming tool**, not a Python feature to memorise: it is how you give a name to a business domain concept. What you get:

            - `frozen=True`: it does not change after creation. Once read from the file, an expense stays as it was read; trying to assign to a field stops the program with `FrozenInstanceError: cannot assign to field 'amount'`.
            - The editor autocompletes `expense.` with its four fields.
            - A typo in a field name is an error, not a silent wrong answer. `expense.categroy` stops with `AttributeError: 'Expense' object has no attribute 'categroy'. Did you mean: 'category'?`, and mypy reports it before the program even runs. With a tuple, `e[1] == "dining"` (the merchant instead of the category) runs to the end and quietly reports 0.00.

            Every group project has concepts like this that can be modelled with a dataclass: a booking, a product, a match, a reading.
            """
        ),
        "key_points": [
            "`e[3]` means nothing; `expense.amount` explains itself.",
            "A dataclass is a naming tool for domain concepts.",
            "`frozen=True`: it does not change after creation.",
            "A typo in a field name is an error, not a silent wrong answer.",
        ],
        "exam_note_md": "Expect code with `row[2]`, `r[3]` and similar. Name it as 'a tuple is a missing type' and the fix as a dataclass with named fields; say what `frozen=True` buys you.",
        "source_ref": "S6 slides 22–24; expense-tracker 017f926",
        "check": ["k_e3", "k_reasons", "k_frozen"],
    },
    {
        "id": sec(8),
        "heading": "Type hints are contracts; the linter is the arbiter",
        "body_md": md(
            """
            **Type hints are contracts.** Commit `04d699f` added hints to every function:

            ```python
            def total_by_category(
                expenses: list[Expense], category: str, minimum: float
            ) -> list[tuple[str, float]]:
            ```

            The signature says what goes in (a list of `Expense`, a category, a minimum) and what comes out (a list of category and total pairs). It is read by the next person and by mypy. Call it with `minimum` and `category` swapped and mypy reports the mistake before the program runs:

            ```text
            src/expense_tracker/weekly.py:34: error: Argument 2 to "total_by_category" has incompatible type "float"; expected "str"  [arg-type]
            ```

            Python itself does not check hints while the program runs: the same wrong call runs and quietly returns an empty list. The contract pays off because someone, or something, reads it. Session 7 turns the checker up; in session 6 you only write the hints.

            **The linter is the arbiter.**

            ```bash
            uv run ruff check .     # finds problems
            uv run ruff format .    # fixes layout
            ```

            The rules are configured once, in `pyproject.toml`; `04d699f` added `line-length = 100` and `select = ["E", "F", "I", "UP", "B", "SIM"]`. Nobody argues about quotes or line length again: the tool decides, and CI enforces it. Two findings you will meet often:

            ```text
            F401 [*] `os` imported but unused
             --> src/gym/bookings.py:2:8
            E501 Line too long (112 > 100)
              --> src/gym/bookings.py:23:101
            ```

            **Reading a finding.** In ruff's full output each finding starts with the rule code and a message, and the next line gives the place as file, line and column: `src/gym/bookings.py:2:8` is line 2, column 8. Then ruff quotes the lines around it, marks the spot with `^^^`, and may add a `help:` line. `[*]` means ruff can fix that one itself with `--fix`, and the summary says how many are fixable. The one-line format shows the same parts, place first. The help line says how to make the finding go away, which is not always the fix: when `F841` says a computed value is never used, the cause may be that someone forgot to use it.

            The slide's method: **read the code, read the message, fix the cause.** `F401` is an import nobody uses, so you remove it (after checking nobody meant to use it). `E501` is a line over the agreed 100 characters, so you shorten or split it. Run against the code just before `04d699f`, ruff with the new settings reported ten findings, among them `E722` ("Do not use bare `except`"). The commit did not silence it; it caught only what reading a file can raise: `except (OSError, ValueError):`.
            """
        ),
        "key_points": [
            "Type hints say what goes in and what comes out; people and mypy read them.",
            "A wrong call becomes an error before the program runs.",
            "`ruff check` finds problems; `ruff format` fixes layout.",
            "Rules are set once in `pyproject.toml` and CI enforces them. Read the code, read the message, fix the cause.",
        ],
        "exam_note_md": "Tool-output questions reward the careful move: read the finding, find the cause in the code, fix that. `# noqa`, raising `line-length` or deleting the line the tool points at are the careless answers.",
        "source_ref": "S6 slides 26–27; expense-tracker 04d699f",
        "check": ["k_checkformat", "k_contract", "k_format_f401"],
    },
    {
        "id": sec(9),
        "heading": "The pair exercise and the five commits to v0.2",
        "body_md": md(
            """
            The lab turns the session into practice. In pairs, 12 minutes, on `src/expense_tracker/report.py` at v0.1. First record what the program prints:

            ```bash
            uv run expenses report --category dining --min 20 > before.txt
            ```

            Then:

            1. Rename three things (variables, a function).
            2. Extract one function out of `run()`.
            3. The output must stay identical. Check it:

            ```bash
            uv run expenses report --category dining --min 20 > after.txt
            diff before.txt after.txt   # nothing printed = you're safe
            ```

            This is the course's definition of a refactoring: the structure changes, the behaviour stays the same. `diff` compares the two files line by line and prints only the lines that differ, so an empty result means this command, on this data, printed exactly what it printed before. If `diff` prints anything, the behaviour changed: undo the last step and try again.

            Then the class replays the demo's own path from v0.1 to v0.2, one commit at a time:

            | # | Commit | Idea |
            |---|---|---|
            | 8 | `5e9466d` Replace magic numbers with named constants | magic numbers |
            | 9 | `f3bb801` Rename calculate_totals to total_by_category | names |
            | 10 | `9d6c607` Separate reading and printing from the calculation | one job; computation is not output |
            | 11 | `017f926` Give an expense a type instead of a tuple | a tuple is a missing type |
            | 12 | `04d699f` Add type hints and make the code ruff clean | contracts; the linter |

            Run the dining report at v0.1 and after each of the five commits, and `diff` against v0.1's output prints nothing every time. Five small steps, each with a message that says what it did. Session 7 later gives each step the name of a refactoring move.

            One limit to keep in mind: a check is only as wide as its input. An empty `diff` on the dining report proves that report is unchanged, not that every possible input behaves the same. Edge cases are what session 8's tests are for.
            """
        ),
        "key_points": [
            "Refactoring: the structure changes, the output stays identical.",
            "`diff before.txt after.txt` prints nothing = you're safe for that input.",
            "If `diff` prints anything, undo the last step.",
            "v0.1 to v0.2 in five commits: constants, names, separate computation, a type, hints and ruff.",
        ],
        "exam_note_md": "Expect a `diff` result or a commit diff to judge: is it a refactoring, and which commit message fits it? An empty `diff` is the evidence; a changed line means it was not a pure refactoring.",
        "source_ref": "S6 slides 30–31; expense-tracker 5e9466d..04d699f; S7 slide 3",
        "check": ["k_diff_empty", "k_diff_width", "s_commits"],
    },
]

# ---------------------------------------------------------------------------
# Terms
# ---------------------------------------------------------------------------

TERMS = [
    ("Clean code", "Code that is cheap to change because it is cheap to understand: names that say what things are, functions with one job, no unexplained numbers. The course's case for it is economic, not aesthetic.", 1),
    ("Economic argument", "Code is read far more often than it is written, so the cost of maintaining a codebase is the cost of understanding it; the next reader is a teammate or you in the future.", 1),
    ("Failure of naming", "The course's verdict on a comment that explains what the code does: the code should have said it with better names.", 2),
    ("Comment for why", "A legitimate comment: it says what the code cannot, such as a business rule, a workaround with its reason, or a deliberate oddity.", 2),
    ("Magic number", "A constant that appears in the code without a name, such as `40` in `print(\"-\" * 40)`. The reader has to guess what it means.", 4),
    ("Named constant", "A value given a name once, usually at the top of the module (`RULE_WIDTH = 40`), so it is changed in one place and the name says what it means.", 4),
    ("Single Responsibility Principle", "A function (or module) should have one job, and so one reason to change. Test: describe it without the word 'and'.", 5),
    ("Guard clause", "A check at the top of a function or loop body that deals with an exception and gets out (`continue`, `return`), so the main path is not buried in nested `if`s.", 6),
    ("Computation is not output", "The rule that functions which compute should return values, and only an outer function prints: 'a function that prints can only be looked at'.", 6),
    ("A tuple is a missing type", "The course's diagnosis for data passed around as tuples (`e[3]`): the program has a concept with no name. The fix is a dataclass.", 7),
    ("Dataclass", "A class declared with `@dataclass` and named, typed fields (`Expense` with `date`, `merchant`, `category`, `amount`). In the course, a naming tool for business concepts.", 7),
    ("`frozen=True`", "Option on `@dataclass`: an instance does not change after creation. Assigning to a field raises `FrozenInstanceError`.", 7),
    ("Type hint", "An annotation on a parameter or return value (`minimum: float`, `-> list[Expense]`). A contract read by people and by mypy; Python does not enforce it while running.", 8),
    ("Linter", "A tool that reads code without running it and reports problems against agreed rules. In the course: ruff, the arbiter whose rules live in `pyproject.toml` and are enforced by CI.", 8),
    ("`ruff check` / `ruff format`", "`ruff check` finds problems (unused imports, bare `except`, long lines); `ruff format` rewrites layout (spacing, quotes, line wrapping) and never changes what the code does.", 8),
    ("Rule code", "The code at the start of a ruff finding, such as `E501` (line too long) or `F401` (imported but unused). The letters are rule families the project selects in `pyproject.toml`.", 8),
    ("Refactoring", "Changing the structure of code while keeping its behaviour: the output must stay identical. Renaming, extracting a function and introducing a type are refactoring moves.", 9),
    ("`before.txt` / `after.txt` check", "Save the program's output before and after a change and run `diff before.txt after.txt`: nothing printed means the output is identical for that input.", 9),
]

# ---------------------------------------------------------------------------
# Traps
# ---------------------------------------------------------------------------

TRAPS = [
    "\"Clean code is about style and taste.\" The course's case is economic: code is read far more often than it is written, and every change starts with understanding it. Unclean code is expensive, not ugly.",
    "\"Good code has a comment on every line.\" That is advice for learners. In a codebase, a comment that explains what the code does is a failure of naming: rename, then delete the comment.",
    "\"So delete every comment.\" Comments that say why stay: a business rule, a workaround with its reason, a deliberate oddity. Delete the bank-export comment and someone may remove the check it protects.",
    "\"`FORTY = 40` fixes a magic number.\" The name must say what the number means (`RULE_WIDTH`), not what it is. `FORTY` is still magic, and becomes a lie when the width changes.",
    "\"`calculate_totals` is a good name because it says what the function does.\" Function names say what they return: `total_by_category` answers 'totals of what, grouped how?'.",
    "\"`frozen=True` makes the class a constant, or makes the code faster.\" It means an instance cannot change after creation: assigning to a field raises `FrozenInstanceError`.",
    "\"Type hints make Python check the types when the program runs.\" Python ignores them at run time: a wrong call runs and can return a silent wrong answer. mypy and the next reader are what use them.",
    "\"`ruff format` fixes everything `ruff check` reports.\" It fixes layout only. An unused import (`F401`) or a bare `except` (`E722`) is a problem in the code that you fix by reading it.",
    "\"If ruff complains, add `# noqa` or raise `line-length` to get CI green.\" The rules were agreed once in `pyproject.toml` and CI enforces them for everyone. Read the message and fix the cause.",
    "\"An empty `diff` proves the refactored code is correct.\" It proves the output is identical for the command and data you ran, nothing more. Edge cases need their own checks.",
]

# ---------------------------------------------------------------------------
# Flashcards
# ---------------------------------------------------------------------------

CARDS = [
    ("Why is clean code 'an economic argument, not an aesthetic one'?", "Code is read far more often than it is written; the cost of maintaining a codebase is the cost of understanding it; the next reader is a teammate or you in the future. Clean code is cheap to change.", "concept", 1),
    ("`calc(c, i, d)` and `invoice_total(lines, tax_rate, discount_rate)` return the same number for the lab's invoice. What question does the slide ask?", "\"Which one would you dare to change?\" Same behaviour, different cost: only the readable one can be changed without decoding it first.", "recall", 1),
    ("When is a comment 'a failure of naming'?", "When it explains what the code does. The fix is to rename until the line says it, then delete the comment.", "concept", 2),
    ("Robert C. Martin's line, quoted on the slide about comments?", "\"Truth can only be found in one place: the code.\" Nothing checks that a comment is still true.", "recall", 2),
    ("The three kinds of legitimate comment?", "A business rule; a workaround, with its reason; a deliberate oddity. All say why, which the code cannot.", "recall", 2),
    ("`# total of all expenses in this category above the threshold` sits above `d[e[2]] = d[e[2]] + e[3]`. What do you do?", "Rename instead of comment: `totals[expense.category] += expense.amount`, then delete the comment. \"The comment is a symptom. The fix is a name.\"", "reading", 2),
    ("The naming table: what should a variable, a function, a boolean and a module name say?", "Variable: what it holds. Function: what it returns. Boolean: a yes/no question (`is_duplicate`). Module: what it is for (`storage.py`).", "recall", 3),
    ("`calculate_totals` vs `total_by_category`", "`calculate_totals` says that some calculating happens; `total_by_category` says what you get back: a total per category. Functions say what they return.", "distinction", 3),
    ("`utils.py` vs `storage.py`", "`utils.py` can hold anything, so it ends up holding everything. `storage.py` says what the module is for, and what does not belong in it.", "distinction", 3),
    ("What is a magic number?", "A constant that appears in the code without a name, such as `40` in `print(\"-\" * 40)`. Name it once (`RULE_WIDTH = 40`) and change it in one place.", "concept", 4),
    ("`FORTY = 40` vs `RULE_WIDTH = 40`", "`FORTY` names the value, so it is still magic and becomes a lie when the width changes. `RULE_WIDTH` names the meaning.", "distinction", 4),
    ("The five things `run()` did in v0.1", "Opened and parsed the file; handled the failure; printed the header; totalled by category; found the largest and printed it.", "recall", 5),
    ("The course's test for 'one function, one job'?", "Can I describe it without the word \"and\"? If not, it has more than one job (Single Responsibility Principle).", "concept", 5),
    ("Why does the Single Responsibility Principle make code cheaper to change?", "Each job lives in one place: changing the layout cannot break the reading, and each piece can be tested and reused on its own.", "concept", 5),
    ("What is a guard clause?", "A check that deals with an exception first and gets out (`continue`, `return`). What is left is the main path, at the outer level instead of inside a pyramid of `if`s.", "concept", 6),
    ("Why can a function that prints 'only be looked at'?", "Its result goes to the screen, not into a value, so a test has nothing to compare and other code cannot reuse it. A function that returns can be tested, reused and read on its own.", "concept", 6),
    ("In v0.2, which function is the only one that prints?", "`run()`. `total_by_category` returns data, `format_report` returns lines.", "recall", 6),
    ("`if e[3] < z:` What is the problem?", "You cannot tell what `e[3]` (or `z`) is without finding the code that built the tuple. A tuple is a missing type; `if expense.amount < minimum:` explains itself.", "reading", 7),
    ("What does `frozen=True` mean on `@dataclass(frozen=True)`?", "The object does not change after creation. Assigning to a field raises `FrozenInstanceError: cannot assign to field ...`.", "recall", 7),
    ("A typo in a field: tuple vs dataclass", "Tuple: `e[1]` instead of `e[2]` runs and gives a silent wrong answer. Dataclass: `expense.categroy` is an `AttributeError` (and a mypy error before running).", "distinction", 7),
    ("Why does the slide call a dataclass 'a naming tool'?", "It is how you give a name to a business concept (an expense, a booking, a product), with named fields the editor autocompletes and the type checker knows.", "concept", 7),
    ("Why are type hints called contracts?", "They say what goes in and what comes out. The next person and mypy read them, and a wrong call becomes an error before the program runs.", "concept", 8),
    ("`ruff check` vs `ruff format`", "`ruff check` finds problems (unused imports, bare `except`, long lines). `ruff format` fixes layout. Format never removes an unused import for you.", "distinction", 8),
    ("ruff reports:\n\n```text\nF401 [*] `os` imported but unused\n```\n\nWhat does it tell you?", "The module imports `os` and never uses it. Read the code to confirm nobody meant to use it, then remove the import.", "reading", 8),
    ("`E501 Line too long (112 > 100)` What does it tell you?", "The line is 112 characters; the project's limit, set once in `pyproject.toml`, is 100. Shorten or split it. `ruff format` fixes it only when re-wrapping the code is enough: it does not split a long string for you.", "reading", 8),
    ("Where do ruff's rules live, and who enforces them?", "In `pyproject.toml` (`line-length`, `select`), agreed once by the team. CI runs ruff on every push, so the tool decides and nobody argues.", "recall", 8),
    ("`diff before.txt after.txt` prints nothing. What does it mean?", "The program printed exactly the same output, for that command on that data, before and after your change: the refactoring kept that behaviour.", "reading", 9),
    ("The five commits from v0.1 to v0.2, in order", "Replace magic numbers with named constants; rename `calculate_totals` to `total_by_category`; separate reading and printing from the calculation; give an expense a type instead of a tuple; add type hints and make the code ruff clean.", "recall", 9),
    ("What does an empty `diff` not prove?", "That other inputs behave the same, or that the code is correct. It only covers the command and data you ran; edge cases need their own checks.", "concept", 9),
]

# ---------------------------------------------------------------------------
# Questions (keys are turned into ids in order at the end)
# ---------------------------------------------------------------------------

QUESTIONS: list[dict[str, Any]] = []


def mcq(
    key: str,
    *,
    level: str,
    skills: list[str],
    stem: str,
    right: tuple[str, str],
    wrong: list[tuple[str, str]],
    pos: str,
    explanation: str,
    section: int,
    source_ref: str,
    origin: str,
    verified_by: str,
) -> None:
    assert len(wrong) == 3
    opts = [{"text_md": t, "correct": False, "why_md": w} for t, w in wrong]
    opts.insert("abcd".index(pos), {"text_md": right[0], "correct": True, "why_md": right[1]})
    QUESTIONS.append(
        {
            "key": key,
            "type": "mcq",
            "level": level,
            "skills": skills,
            "stem_md": stem,
            "options": opts,
            "explanation_md": explanation,
            "section_ref": sec(section),
            "source_ref": source_ref,
            "origin": origin,
            "verified_by": verified_by,
        }
    )


def part(label: str, prompt: str, marks: int, model: str, rubric: list[str], weak: str) -> dict[str, Any]:
    return {
        "label": label,
        "prompt_md": prompt,
        "marks": marks,
        "model_answer_md": model,
        "rubric": rubric,
        "weak_answers_md": weak,
    }


def open_q(
    key: str,
    *,
    level: str,
    skills: list[str],
    stem: str,
    parts: list[dict[str, Any]],
    explanation: str,
    section: int,
    source_ref: str,
    origin: str,
    verified_by: str,
    lines: str = "5–8",
) -> None:
    QUESTIONS.append(
        {
            "key": key,
            "type": "open",
            "level": level,
            "skills": skills,
            "stem_md": stem,
            "parts": parts,
            "lines": lines,
            "explanation_md": explanation,
            "section_ref": sec(section),
            "source_ref": source_ref,
            "origin": origin,
            "verified_by": verified_by,
        }
    )


def sort_q(
    key: str,
    *,
    level: str,
    skills: list[str],
    stem: str,
    categories: list[tuple[str, str]],
    items: list[tuple[str, str, str]],
    explanation: str,
    section: int,
    source_ref: str,
    origin: str,
    verified_by: str,
) -> None:
    QUESTIONS.append(
        {
            "key": key,
            "type": "sort",
            "level": level,
            "skills": skills,
            "stem_md": stem,
            "categories": [{"id": i, "label": label} for i, label in categories],
            "items": [{"text_md": t, "category": c, "why_md": w} for t, c, w in items],
            "explanation_md": explanation,
            "section_ref": sec(section),
            "source_ref": source_ref,
            "origin": origin,
            "verified_by": verified_by,
        }
    )


# ----- Section 1: economics --------------------------------------------------

mcq(
    "k_dare",
    level="core",
    skills=["concept", "compare"],
    stem="Session 6 shows the same logic twice. For the lab's invoice (a pencil line 10 × 5, a book line 50 × 2, 21% tax, 10% discount) both functions return 163.35.\n\n"
    + CALC
    + "\n\n"
    + INVOICE_TOTAL
    + "\n\nThe slide asks: which one would you dare to change? Which answer follows the course's reasoning?",
    right=(
        "`invoice_total`, because its names tell you what each value means before you touch it",
        "Right: the cost of a change is the cost of understanding the code first. `subtotal`, `tax_rate` and `line.price` tell you what you are touching; in `calc` you must decode `i`, `d` and `p[1]` before you dare edit a line.",
    ),
    wrong=[
        (
            "`calc`, because it is shorter, so there is less code that a change could break",
            "Fewer characters is not cheaper to understand. Every letter in `calc` has to be decoded before you can change it safely, which is exactly the cost the course is talking about.",
        ),
        (
            "Either one, because they return the same result, so changing either costs the same effort",
            "Same behaviour, different cost. The economic argument is that the price of a change is the time spent understanding the code, and that price is very different here.",
        ),
        (
            "`calc`, because its `if d > 0` and `if i > 0` checks protect it from bad input",
            "The checks are not what makes code safe to change. A reader still has to work out what `d` and `i` are before trusting them, and the question is about understanding, not input validation.",
        ),
    ],
    pos="b",
    explanation="Both functions compute the same total, so neither is more correct. The difference is what a change costs. Code is read far more often than it is written, and the cost of maintaining it is the cost of understanding it. In `invoice_total`, the names `subtotal`, `discounted`, `tax_rate` and `line.quantity` tell the next reader what each line means, so a change to the tax rule takes seconds and the reader knows what else it affects. In `calc`, the reader first has to reconstruct that `c` is a list of invoice lines, `p[1] * p[2]` is price times quantity, and `i` is the tax. That is why the slide asks which one you would *dare* to change.",
    section=1,
    source_ref="S6 slides 8–10; labs/07-refactor.md",
    origin="slides",
    verified_by="run",
)

mcq(
    "k_econ",
    level="core",
    skills=["concept"],
    stem="A teammate says: \"It works, so renaming everything is a waste of time. Clean code is just a matter of taste.\" Which reply states the course's argument?",
    right=(
        "Code is read far more than written, so its cost is the cost of understanding it",
        "Right: this is the slide's economic argument. Every future change starts with someone reading the code, a teammate or you in six months, so unclear code makes every change slower and riskier.",
    ),
    wrong=[
        (
            "Clean code runs faster, so the program costs the company less to run on its servers",
            "The argument is not about speed. `calc` and `invoice_total` run the same logic; the difference is the cost of reading and changing them.",
        ),
        (
            "Reviewers and teachers reward code that looks tidy, so clean code earns better marks",
            "That is the aesthetic argument the course explicitly rejects. The case for clean code is the cost of reading and changing it, not how it looks to a marker.",
        ),
        (
            "Code written in a clean style cannot contain bugs, so the team can write fewer tests",
            "Clean code can be wrong, and `calc` is ugly but correct. Clean code makes bugs easier to find and fix; it does not prevent them or replace tests.",
        ),
    ],
    pos="d",
    explanation="The slide is titled \"An economic argument, not an aesthetic one\". Its three points: code is read far more often than it is written; the cost of maintaining a codebase is the cost of understanding it; the next reader is a teammate, or you in the future. The teammate is right that the code works, but that is not the question. The question is what the next change will cost. Clean code is cheap to change and unclean code is expensive to change, and the only code that never changes is code that never runs.",
    section=1,
    source_ref="S6 slide 10",
    origin="slides",
    verified_by="source",
)

open_q(
    "k_open_dare",
    level="exam",
    skills=["compare", "concept", "judgement"],
    stem="Look again at the two functions from the start of session 6. They return the same result for the lab's invoice (163.35).\n\n"
    + CALC
    + "\n\n"
    + INVOICE_TOTAL,
    parts=[
        part(
            "1",
            "Which one would you dare to change, and why?",
            2,
            "`invoice_total`. Its names tell me what each value is, so I can find the line to change (say, the tax) and see what depends on it. In `calc` I would first have to decode `c`, `i`, `d` and `p[1]`.",
            [
                "Chooses `invoice_total`",
                "Reason is about understanding before changing: the names say what each value is, while `calc` has to be decoded first",
            ],
            "Choosing `invoice_total` with 'it is cleaner' or 'it looks better' earns one mark: that is the aesthetic reason the course rejects. Saying `calc` because it is shorter misses the point that shorter is not cheaper to read. The second mark needs the link to understanding: you cannot safely change what you have not understood.",
        ),
        part(
            "2",
            "Give two things a reader of `calc` has to work out that `invoice_total` tells them directly.",
            2,
            "That `i` is the tax rate and `d` the discount rate, and that the discount is applied before the tax; and that `p[1] * p[2]` is the price times the quantity of an invoice line, with `t` the running subtotal.",
            [
                "`i` and `d` are the tax and discount rates (or the order in which they are applied)",
                "`p[1] * p[2]` is price × quantity of an invoice line",
                "`c` is the list of invoice lines, or `t` is the running subtotal",
            ],
            "Weak answers say 'what the variables mean' without naming one. The marker wants two specific facts the reader must reconstruct, such as what `p[1]` is or which rate `i` holds. Listing the names from `invoice_total` without saying what they replace in `calc` shows reading, not comparison.",
        ),
        part(
            "3",
            "Why does the course call this an economic argument rather than an aesthetic one?",
            2,
            "Both are correct, so the difference is cost. Code is read far more often than it is written, and every change starts with understanding it. A teammate, or I in six months, pays that cost on every change.",
            [
                "Code is read far more often than it is written",
                "The cost of maintaining code is the cost of understanding it, so unclear code makes every change expensive",
                "The next reader is a teammate or your future self",
            ],
            "Answers such as 'clean code is more professional' or 'it is easier on the eye' are the aesthetic argument. Saying 'clean code has fewer bugs' is not the course's claim either: `calc` has no bug. Full marks need the cost of reading and who pays it.",
        ),
    ],
    explanation="This is the slide's own question turned into a short answer. The judgement is easy; the marks are in the reasons. Name the economic argument in the course's words (read far more than written; cost of maintenance is cost of understanding; the next reader), and show you have actually compared the two by naming what `calc` hides.",
    section=1,
    source_ref="S6 slides 8–10",
    origin="slides",
    verified_by="source",
)

# ----- Section 2: comments ---------------------------------------------------

mcq(
    "k_comment_rule",
    level="core",
    skills=["concept"],
    stem="Which statement matches the rule on comments that session 6 adopts, including its context?",
    right=(
        "A comment explaining what the code does is a failure of naming; one explaining why may stay",
        "Right: that is the rule, with its exception. The slide also says commenting liberally is reasonable in a learning context, and that the advice should never be followed blindly.",
    ),
    wrong=[
        (
            "Comment every line, as introductory courses do, because readers of your project may not know Python well",
            "That is the learning-context habit the slide discusses and disagrees with for real codebases. Readers of your project need names that say what the code does, not a running translation.",
        ),
        (
            "Avoid comments altogether, because the truth can only be found in one place: the code",
            "The quote is real, but the course keeps comments that say why: a business rule, a workaround with its reason, a deliberate oddity. Deleting those loses information the code cannot hold.",
        ),
        (
            "Any comment is fine as long as someone remembers to update it when the code changes",
            "Nothing checks that a comment is updated, which is why restating comments drift and lie. The course's fix is to put the meaning into names, where it cannot fall out of date.",
        ),
    ],
    pos="a",
    explanation="Slide 11 is \"A disagreement, out loud\". It is standard in introductory courses to comment liberally, and in a learning context it is good to explain what the code does. The course nevertheless applies the rule \"A comment that explains what the code does is a failure of naming\", quoting Robert C. Martin: \"Truth can only be found in one place: the code.\" Slide 14 then lists the comments that are legitimate because they explain what the code cannot say: a business rule, a workaround with its reason, a deliberate oddity. And the slide's last line: the advice depends on context; never follow it blindly.",
    section=2,
    source_ref="S6 slides 11, 14",
    origin="slides",
    verified_by="source",
)

mcq(
    "k_rename",
    level="exam",
    skills=["read-code", "judgement"],
    stem="A teammate's checkout code contains:\n\n```python\n# price after the student discount\np = b * 0.85\n```\n\nFollowing session 6, what is the best fix?",
    right=(
        "Rename `p` and `b`, name the `0.85` as a constant, then delete the comment",
        "Right: rename instead of comment, for example `price_after_discount = base_price * (1 - STUDENT_DISCOUNT)`. The names carry what the comment said, the magic `0.85` gets a name that says what it means, and nothing is left to drift out of date.",
    ),
    wrong=[
        (
            "Keep the comment and add a second one above it explaining that `0.85` means a 15% discount",
            "Two comments for one unclear line is the same failure twice. The course's fix for a 'what' comment is a better name, not more explanation beside the code.",
        ),
        (
            "Delete the comment and leave `p = b * 0.85` as it is, since comments are a failure of naming",
            "The comment was the only place the meaning lived. Deleting it without renaming makes the line less clear. The rule is: delete the comment and improve the line.",
        ),
        (
            "Move the comment to the end of the line so that it sits closer to the code it explains",
            "Where the comment sits changes nothing: it still restates the code and can still go stale. The problem is the names `p`, `b` and the bare `0.85`.",
        ),
    ],
    pos="c",
    explanation="The comment is a symptom: it exists because `p`, `b` and `0.85` say nothing. Slide 13's fix is a name, as in `d[e[2]] = d[e[2]] + e[3]` becoming `totals[expense.category] += expense.amount`. Here the same move gives `price_after_discount`, `base_price` and a named constant for the discount, which also removes a magic number (slide 16). After the rename the comment restates the line, and slide 14's test applies: if the comment restates the next line, delete it and improve the line. Note that `1 - 0.15` and `0.85` are the same number in Python, so the behaviour does not change.",
    section=2,
    source_ref="S6 slides 13, 14, 16",
    origin="slides",
    verified_by="run",
)

mcq(
    "k_legit",
    level="exam",
    skills=["read-code", "judgement"],
    stem="Which of these comments would the course keep?",
    right=(
        "`# finance nets refunds into the monthly total` above `total += expense.amount`",
        "Right: it states a business rule the line cannot express: refunds are negative amounts and finance wants them netted off. Without it, a teammate might start filtering out negative amounts and break the finance figures.",
    ),
    wrong=[
        (
            "`# Loop over every expense in the list.` above `for expense in expenses:`",
            "It restates the line word for word. With good names the loop already says this, so the comment is noise that can only go stale.",
        ),
        (
            "`# add this amount to the category's total` above `totals[expense.category] += expense.amount`",
            "This is the slide's 'what' comment again: the names `totals`, `expense.category` and `expense.amount` already say it. Delete it.",
        ),
        (
            "`# check whether this row is a duplicate` above `if is_duplicate:`",
            "The boolean already reads as a yes/no question, as the naming table asks. The comment adds nothing the name does not say.",
        ),
    ],
    pos="d",
    explanation="Slide 14: legitimate comments explain what the code cannot say. The three kinds are a business rule, a workaround with its reason, and a deliberate oddity. The refund comment is a business rule: the code can add a negative number, but it cannot say that finance wants refunds netted off rather than reported separately. The other three restate their line, and slide 14's instruction for those is to delete the comment and improve the line. Here the lines are already good, so the comments just go.",
    section=2,
    source_ref="S6 slide 14",
    origin="slides",
    verified_by="source",
)

mcq(
    "k_bank_keep",
    level="exam",
    skills=["read-diff", "judgement"],
    stem="Your group's copy of the expense-tracker has slide 14's bank-export comment in `read_expenses`. A teammate prepares a commit titled `Remove comments (a comment is a failure of naming)`. One hunk:\n\n```diff\n         for row in reader:\n-            # The bank's export sometimes ends with a summary row with fewer fields.\n             if len(row) == FIELDS_PER_ROW:\n```\n\nWhat should you tell them about this hunk?",
    right=(
        "Keep the comment: it gives the reason for the check, which the line cannot say",
        "Right: it is the slide's own example of a comment for why. The line says what happens (short rows are skipped); only the comment says the bank's file can end with a shorter summary row.",
    ),
    wrong=[
        (
            "Let it go in: the course's rule says comments that explain code are a failure of naming",
            "That applies the rule blindly. The rule is about comments that say *what* the code does; this one says *why* the check exists, which slide 14 lists as a legitimate comment.",
        ),
        (
            "Replace it with a longer constant name that mentions the bank's summary row",
            "A name can say what a value is, not the reason behind a check. `FIELDS_PER_ROW_EXCEPT_BANK_SUMMARY` is harder to read and still does not say why.",
        ),
        (
            "Let it go in, as long as the same sentence goes into the commit message instead",
            "The next reader of `read_expenses` reads the code, not the log. The reason belongs beside the line it protects, where nobody can miss it.",
        ),
    ],
    pos="b",
    explanation="Slide 11 states the rule, \"a comment that explains what the code does is a failure of naming\", and adds that the advice depends on context: never follow it blindly. Slide 14 lists what stays: a business rule, a workaround with its reason, a deliberate oddity, with this very bank-export comment as its example. Commit `5e9466d` deleted a different comment, `# skip rows that do not have all four fields`, because `FIELDS_PER_ROW` now said the same thing. This hunk deletes the reason instead. Without it, the next reader sees a length check with no visible purpose and may remove it, and the report breaks on the bank's file. Ask of every comment: does it say something the code cannot?",
    section=2,
    source_ref="S6 slides 11, 14; expense-tracker 5e9466d",
    origin="slides",
    verified_by="source",
)

sort_q(
    "s_comments",
    level="exam",
    skills=["read-code", "judgement"],
    stem="Sort each comment, shown with the line below it, by what you should do with it.",
    categories=[
        ("keep", "Keep: it says why"),
        ("delete", "Delete: it says what the code does (rename if needed)"),
        ("wrong", "Fix now: it contradicts the code"),
    ],
    items=[
        (
            "```python\n# The bank's export sometimes ends with a summary row with fewer fields.\nif len(row) == FIELDS_PER_ROW:\n```",
            "keep",
            "The slide's own example of a legitimate comment: it explains why rows can be short, which the line cannot say.",
        ),
        (
            "```python\n# Loop over the expenses.\nfor expense in expenses:\n```",
            "delete",
            "It repeats the line in English. The names already say it.",
        ),
        (
            "```python\n# total of all expenses in this category above the threshold\nd[e[2]] = d[e[2]] + e[3]\n```",
            "delete",
            "A failure of naming: rename to `totals[expense.category] += expense.amount` and the comment has nothing left to add.",
        ),
        (
            "```python\n# Bicing exports dates as DD/MM/YYYY; convert them so they sort with the rest.\ndate = to_iso_date(row[DATE])\n```",
            "keep",
            "A workaround with its reason: the code shows the conversion, only the comment says why one supplier needs it.",
        ),
        (
            "```python\n# ignore amounts below 20\nMINIMUM_AMOUNT = 10.0\n```",
            "wrong",
            "The comment and the code disagree. Truth is in the code, so find out which value is intended, fix it, and delete the comment: the name already says what it is.",
        ),
        (
            "```python\n# keep the file's order on purpose: finance checks this report line by line against the statement\nreturn expenses\n```",
            "keep",
            "A deliberate oddity: without it, a teammate might sort the report to tidy it and break finance's check.",
        ),
        (
            "```python\n# Check if it is a duplicate.\nif is_duplicate:\n```",
            "delete",
            "The boolean name already reads as the question. The comment says nothing more.",
        ),
        (
            "```python\n# Dining only.\nif expense.category == \"transport\":\n```",
            "wrong",
            "A misleading comment: the code counts transport. One of them is wrong, and a reader who trusts the comment is misled. Settle which category is meant, then let the code say it.",
        ),
    ],
    explanation="Slide 14 sorts comments by one question: does it explain something the code cannot say? Business rules, workarounds with their reason and deliberate oddities pass and stay. Comments that restate the line are a failure of naming and go. Comments that contradict the code are the reason for the rule: \"Truth can only be found in one place: the code.\" They need fixing now, because someone will trust them.",
    section=2,
    source_ref="S6 slides 11, 13, 14",
    origin="slides",
    verified_by="source",
)

# ----- Section 3: names --------------------------------------------------------

mcq(
    "k_fname",
    level="core",
    skills=["concept", "judgement"],
    stem="A function takes a list of `Expense` and returns how much was spent in each month. Which name follows the course's rule for functions?",
    right=(
        "`total_by_month`",
        "Right: it says what the function returns, a total per month, just as `total_by_category` does in the demo.",
    ),
    wrong=[
        (
            "`process_expenses`",
            "`process` is the vague verb the rubric warns about: it says something happens to expenses, not what you get back.",
        ),
        (
            "`calculate`",
            "Calculate what? Like `calculate_totals`, it names an activity and leaves the result for the reader to discover.",
        ),
        (
            "`monthly_helper`",
            "'Helper' says nothing about the result; it is the function-level version of `utils.py`.",
        ),
    ],
    pos="c",
    explanation="The naming table on slide 15: a function says what it returns. The demo's example is `calculate_totals` becoming `total_by_category` in commit `f3bb801`. A caller reading `totals = total_by_month(expenses)` knows what they get without opening the function. `process_expenses`, `calculate` and `monthly_helper` all describe the function as an activity, so the reader still has to read its body to learn what comes back, and a name that needs that much help is not finished.",
    section=3,
    source_ref="S6 slide 15; expense-tracker f3bb801",
    origin="slides",
    verified_by="source",
)

mcq(
    "k_bool",
    level="core",
    skills=["concept", "judgement"],
    stem="In a group project's booking app, a variable holds whether a booking has already been paid. Which name follows the course's rule for booleans?",
    right=(
        "`is_paid`",
        "Right: it reads as a yes/no question, so `if is_paid:` reads as a sentence. Same pattern as the slide's `is_duplicate`.",
    ),
    wrong=[
        (
            "`payment`",
            "It sounds like it holds a payment (an amount, a record), not a yes/no answer. A reader would expect `payment.amount`.",
        ),
        (
            "`status_flag`",
            "This is the slide's bad example, `flag`, with a prefix. It says there is a flag, not what question it answers.",
        ),
        (
            "`check_payment`",
            "It reads like a function that does something, not a value that holds an answer. `if check_payment:` is confusing.",
        ),
    ],
    pos="d",
    explanation="Slide 15's table: a boolean reads as a yes/no question, and the example is `flag` becoming `is_duplicate`. The test is to read the condition aloud: `if is_paid:` is a sentence. `if status_flag:` asks the reader to find out what the flag means; `payment` suggests the wrong type; `check_payment` suggests an action. Each needs a comment to be understood, and a name that needs a comment is not finished.",
    section=3,
    source_ref="S6 slide 15",
    origin="slides",
    verified_by="source",
)

mcq(
    "k_module",
    level="core",
    skills=["concept", "judgement"],
    stem="Your group is splitting a long `main.py`. One new module will hold only the functions that read bookings from the JSON file and write them back. Which module name follows the course's rule?",
    right=(
        "`storage.py`",
        "Right: it says what the module is for, so everyone knows what belongs in it and what does not. It is the slide's own 'better' example.",
    ),
    wrong=[
        (
            "`utils.py`",
            "The slide's bad example: a utilities module can hold anything, so over time it holds everything, and its name tells you nothing.",
        ),
        (
            "`common.py`",
            "'Common' describes who uses it, not what it does. It invites the same grab-bag as `utils.py`.",
        ),
        (
            "`functions.py`",
            "Every module holds functions; the name says nothing about this module's purpose.",
        ),
    ],
    pos="a",
    explanation="The naming table's last row: a module says what it is for, and the example is `utils.py` becoming `storage.py`. A purpose-named module is also a boundary: a function that formats a report clearly does not belong in `storage.py`, but it could end up in `utils.py`, `common.py` or `functions.py` without anyone noticing. Good module names keep the one-job idea at the level of files.",
    section=3,
    source_ref="S6 slide 15",
    origin="slides",
    verified_by="source",
)

mcq(
    "k_vars",
    level="core",
    skills=["read-code", "judgement"],
    stem=md(
        """
        In v0.1, `run()` found the largest expense with:

        ```python
        m = 0.0
        mr = None
        for e in rows:
            if e[3] > m:
                m = e[3]
                mr = e
        ```

        Commit `f3bb801` renamed `m` and `mr`. Which pair follows the naming table's rule for variables?
        """
    ),
    right=(
        "`largest_amount` and `largest`",
        "Right: each says what it holds, the biggest amount so far and the expense it came from. It is what `f3bb801` chose.",
    ),
    wrong=[
        (
            "`m` and `mr`, kept short, with a comment above the loop explaining each",
            "That is the comment the course calls a failure of naming. A name that needs a comment is not finished.",
        ),
        (
            "`float_value` and `tuple_row`",
            "These name the type of the value. Every amount is a float; the name should say which amount this is.",
        ),
        (
            "`temp` and `result`",
            "These name the role in the loop. A reader still has to trace the loop to learn what the result is.",
        ),
    ],
    pos="b",
    explanation="Slide 15's table: a variable says what it holds, and the bad examples are `d`, `t` and `x`. `m` and `mr` are the same kind of name: you must read the loop to learn that `m` is the biggest amount seen so far and `mr` the expense it came from. `largest_amount` and `largest` put that in the name, so the line that prints the largest expense reads on its own. Names built from types (`float_value`) or roles (`temp`, `result`) say something about the value, but not which value it is. A comment would only cover the gap, and a name that needs a comment is not finished.",
    section=3,
    source_ref="S6 slide 15; expense-tracker v0.1 report.py, f3bb801",
    origin="history",
    verified_by="source",
)

# ----- Section 4: magic numbers -------------------------------------------------

mcq(
    "k_forty",
    level="core",
    skills=["read-code", "judgement"],
    stem="v0.1's report draws its separator line with:\n\n```python\nprint(\"-\" * 40)\n```\n\nWhich change follows the course's advice on magic numbers?",
    right=(
        "Define `RULE_WIDTH = 40` at the top and write `print(\"-\" * RULE_WIDTH)`",
        "Right: this is commit `5e9466d`. The name says what 40 means, and the width is changed once, in one place.",
    ),
    wrong=[
        (
            "Add the comment `# 40 dashes` at the end of the line",
            "It restates the code, and the reader still does not know why 40. A comment that explains what the code does is a failure of naming.",
        ),
        (
            "Define `FORTY = 40` at the top and write `print(\"-\" * FORTY)`",
            "The name says what the number is, not what it means. It is still magic, and it becomes a lie when the width changes to 50.",
        ),
        (
            "Write out the 40 dashes as one string literal so that no number appears in the code",
            "The magic number is still there, now hidden in a long string that is harder to count and harder to change.",
        ),
    ],
    pos="c",
    explanation="Slide 16: a magic number is a constant that appears in the code without a name, and it is better to name it. The demo did exactly this in `5e9466d`: `RULE_WIDTH = 40`, `NAME_WIDTH = 20`, `AMOUNT_WIDTH = 10`. The point of the name is meaning. `RULE_WIDTH` tells you this 40 is the width of the rule line, so if the table gets wider you change one line and know nothing else moves by accident. `FORTY` gives you none of that.",
    section=4,
    source_ref="S6 slide 16; expense-tracker 5e9466d",
    origin="history",
    verified_by="source",
)

mcq(
    "k_vat",
    level="hard",
    skills=["read-code", "judgement"],
    stem="A teammate's module contains:\n\n```python\ndef price_with_vat(price: float) -> float:\n    return price * (1 + 0.21)\n\n\ndef invoice_total(prices: list[float]) -> float:\n    return sum(prices) * 1.21\n\n\ndef savings_goal(income: float) -> float:\n    return income * 0.21\n```\n\nThe VAT rate changes to 10%. The teammate plans to search the project for `0.21` and replace it with `0.10`. What is the best response?",
    right=(
        "Name the VAT rate once and use it in both VAT functions; leave savings alone",
        "Right: the search would change the savings goal by mistake and miss the `1.21`. One named VAT constant (for example `STANDARD_VAT_RATE`) used in both places makes the change one line that cannot touch anything else.",
    ),
    wrong=[
        (
            "Go ahead: search-and-replace is quick and changes every place where the rate appears",
            "It changes the wrong place (`savings_goal`'s 0.21 is not VAT) and misses one (`1.21` contains the rate but not the text `0.21`).",
        ),
        (
            "Add a `# VAT` comment beside each `0.21` so the next search finds the right ones",
            "Comments do not fix the `1.21` hidden in `invoice_total`, and you still edit several places by hand. A name, not a comment, is the fix.",
        ),
        (
            "Change `0.21` only in `price_with_vat`, since it is the one with VAT in its name",
            "`invoice_total` also applies VAT, as the bare `1.21`. Leaving it means invoices and single prices disagree after the change.",
        ),
    ],
    pos="a",
    explanation="This is the point of slide 16, \"change the width once, in one place, with a name that says what it is\", applied to a rate. Read carefully: the VAT rate appears twice in two disguises (`0.21` and `1.21`), and the same digits `0.21` appear a third time meaning something unrelated. A search for the digits catches the wrong one and misses a right one. Naming the meaning, as session 7 does with `STANDARD_VAT_RATE`, makes the VAT change a one-line edit and keeps the savings rate untouched.",
    section=4,
    source_ref="S6 slide 16; S7 slide 5",
    origin="slides",
    verified_by="reasoning",
)

# ----- Section 5: one function, one job ----------------------------------------

mcq(
    "k_q5var",
    level="exam",
    skills=["concept", "judgement"],
    stem="A function called `import_bookings(path)` opens a JSON file, checks that every booking has a member and a date, works out the revenue for each class and prints a table of the results. Which clean-code problem does this describe best?",
    right=(
        "It does several jobs at once, so it is hard to test and to change",
        "Right: four jobs in one function (read, check, compute, print). You cannot test the revenue without a file, and changing the table layout means editing the function that reads the data.",
    ),
    wrong=[
        (
            "Its name is too short to describe everything the function does",
            "A longer name would only list the jobs ('import_check_compute_print'). The problem is the number of jobs.",
        ),
        (
            "It should read a CSV file instead of JSON, which is simpler to parse",
            "The file format is a design choice, not a clean-code problem. The same four jobs in one function would be just as hard to test with CSV.",
        ),
        (
            "It needs more type hints so that mypy can check each step",
            "Hints make the contract clear but do not separate the jobs. A fully hinted four-job function is still hard to test and to change.",
        ),
    ],
    pos="a",
    explanation="This is sample Q5 in new clothes. Apply the slide's test: describe it without 'and'. It \"opens a file and checks bookings and computes revenue and prints a table\" fails three times. That breaks the Single Responsibility Principle, and the consequences are the ones the course names: you cannot check the revenue without a real file and without reading printed text, and a change to one job (the table layout) risks breaking another (the reading). The fix in words is the split `9d6c607` made: one function per job, with only the outermost one printing.",
    section=5,
    source_ref="S6 slide 18; sample Q5",
    origin="teacher-variant",
    verified_by="source",
)

mcq(
    "k_and",
    level="core",
    skills=["concept"],
    stem="You describe four functions to a teammate in one sentence each. Which description passes the course's test for a function with one job?",
    right=(
        "Returns the total spent per category for a list of expenses",
        "Right: one sentence, no 'and', and it says what comes back. This is `total_by_category`.",
    ),
    wrong=[
        (
            "Reads the bookings file and returns the bookings of one member",
            "Two jobs joined by 'and': reading a file and filtering. Split them and the filter can be tested with a plain list.",
        ),
        (
            "Prints the total spent per category for a list of expenses",
            "No 'and', yet two jobs: it computes the totals and prints them. The test only works on an honest description; computation is not output.",
        ),
        (
            "Totals the expenses by category and formats them as a table",
            "Computation and formatting are separate jobs; in v0.2 they are `total_by_category` and `format_report`.",
        ),
    ],
    pos="b",
    explanation="Slide 18 gives the test: can I describe it without the word \"and\"? A description that needs 'and' usually names two jobs, and the Single Responsibility Principle says each should be its own function. The v0.2 split shows what that looks like in practice: `read_expenses` returns the expenses in a file, `total_by_category` returns the totals, `format_report` returns the lines, and `run` is the only one that prints. The test needs an honest description: 'prints the totals' hides a second job, because computing and printing are separate (slide 20).",
    section=5,
    source_ref="S6 slides 18, 20",
    origin="slides",
    verified_by="source",
)

sort_q(
    "s_jobs",
    level="exam",
    skills=["read-code"],
    stem="In v0.1, `run()` did everything. After commit `9d6c607` and the rest of v0.2, each job lives in one function. Sort each job into the v0.2 function that now does it.",
    categories=[
        ("read", "`read_expenses`"),
        ("total", "`total_by_category`"),
        ("largest", "`largest_expense`"),
        ("format", "`format_report`"),
        ("run", "`run`"),
    ],
    items=[
        ("Skips rows that do not have four fields", "read", "`read_expenses` keeps a row only `if len(row) == FIELDS_PER_ROW`."),
        ("Turns each CSV row into an `Expense`", "read", "Building the `Expense` from the row's fields is part of reading the file."),
        ("Leaves out expenses below the minimum", "total", "The guard `if expense.amount < minimum: continue` is inside `total_by_category`."),
        ("Sorts the categories from the highest total down", "total", "`total_by_category` returns the pairs already ordered by `-pair[1]`."),
        ("Picks the expense with the highest amount", "largest", "That is the whole job of `largest_expense`, which returns it."),
        ("Builds the `Expense report for ...` header line", "format", "`format_report` starts its list of lines with the header; it returns text, it does not print it."),
        ("Returns `None` when the list of expenses is empty", "largest", "`largest_expense` starts from `None` and returns it unchanged when there is nothing to compare; `format_report` then leaves out the largest-expense block."),
        ("Prints each line to the terminal", "run", "`run` is the only function that prints: `for line in format_report(...): print(line)`."),
        ("Catches the error when the file cannot be read and exits with code 1", "run", "In v0.2 the `try`/`except (OSError, ValueError)` and `sys.exit(1)` are still in `run`; v0.3 moves them to the CLI."),
    ],
    explanation="The slide listed `run()`'s five jobs in v0.1: open and parse the file, handle the failure, print the header, total by category, find the largest and print it. Commit `9d6c607` gave each its own function, and every function except `run` returns a value instead of printing. Sorting the jobs shows the payoff: `total_by_category`, `largest_expense` and `format_report` can be checked with plain data and an assert, `read_expenses` needs only a small file, and the printing and exiting are confined to `run`.",
    section=5,
    source_ref="S6 slides 18, 20; expense-tracker 9d6c607, v0.2 report.py",
    origin="history",
    verified_by="source",
)

open_q(
    "k_open_q7",
    level="exam",
    skills=["read-code", "judgement"],
    stem="A teammate wrote this for the group project:\n\n```python\ndef check(rows):\n    n = 0\n    for r in rows:\n        # if the amount is big\n        if r[3] > 100:\n            n = n + 1\n    print(\"Big expenses:\", n)\n    return n\n```\n\nEach row is a tuple `(date, merchant, category, amount)`.",
    parts=[
        part(
            "1",
            "In one sentence, what does this function do?",
            1,
            "It counts the expenses whose amount (the fourth field) is over 100, prints that count, and returns it.",
            ["Says it counts the rows whose amount `r[3]` is greater than 100, and prints and returns the count"],
            "'It checks the rows' repeats the name and earns nothing. 'It finds big expenses' is vague: say what it counts and against which value. Missing that it both prints and returns the number loses the detail that part 2 builds on.",
        ),
        part(
            "2",
            "Name two problems a teammate would face when reading, testing or changing it.",
            2,
            "The names say nothing: `check`, `r`, `n`, `r[3]` and the bare 100 force you to trace the code, and the comment only restates the `if`. It also prints as well as computing, so every caller and test gets output it did not ask for.",
            [
                "A naming problem with its consequence: `check`, `r`, `n` or `r[3]` do not say what they hold or return, so you must trace the code",
                "The magic number 100 or the comment that restates the `if` (a failure of naming)",
                "It mixes computation with output: the `print` means it cannot be reused or tested quietly",
            ],
            "'Bad names' with no example and no consequence scores at most one. 'It needs more comments' is the opposite of the course's rule. 'It is too long' is not a problem here: it is eight lines. Two separate problems are needed; naming `r` and `n` as two problems counts once.",
        ),
        part(
            "3",
            "Describe in words (do not write code) how you would change it, and which of your two problems each change solves.",
            3,
            "Rename it after what it returns, such as `count_large_expenses`, and use an `Expense` dataclass so `r[3]` becomes `expense.amount`; then the comment can go. Name the 100 or make it a parameter. Remove the `print` and let the caller print the count, so a test can check the returned number.",
            [
                "Rename the function after what it returns and the variables after what they hold",
                "Replace the tuple index with a dataclass field, or 100 with a named constant or parameter",
                "Move the `print` to the caller so the function only returns the count",
                "Links each change to the problem it solves",
            ],
            "Describing the new code line by line, or writing it, misses the instruction 'in words'. Weak answers fix one problem and forget the link to part 2. 'Add a docstring' or 'add comments' does not solve the naming problem; renaming does.",
        ),
    ],
    explanation="This is sample Q7's shape with new code. The function is short but shows four session 6 ideas at once: a vague function name, a tuple indexed by number with a magic threshold, a comment that restates the code, and computation mixed with output. A full answer names two of them with their consequence for a teammate, then fixes each in words and says which fix answers which problem.",
    section=5,
    source_ref="sample Q7; S6 slides 13, 15, 16, 20, 22",
    origin="teacher-variant",
    verified_by="run",
)

# ----- Section 6: guard clauses, computation is not output ---------------------

mcq(
    "k_guard",
    level="core",
    skills=["read-code", "concept"],
    stem="Slide 19's two shapes of a loop body, the pyramid and the guard clauses:\n\n"
    + PYRAMID
    + "\n\n"
    + GUARDS
    + "\n\nWhat does the second version (guard clauses) make easier, according to the course?",
    right=(
        "The exceptions are handled first, so the main path reads on its own",
        "Right: \"Deal with the exceptions first and get out. What is left is the main path.\" The line that adds to the total no longer sits inside a nested condition you must hold in your head.",
    ),
    wrong=[
        (
            "The program runs faster, because `continue` skips the remaining checks",
            "Both versions evaluate about the same conditions. The benefit is for the reader.",
        ),
        (
            "The code is shorter, because guard clauses need fewer lines than nested `if`s",
            "The guard version is actually longer here. The gain is in readability.",
        ),
        (
            "The filters no longer need to be tested, because each guard is too simple to fail",
            "Simple code can still be wrong, and guards still need checking. They make the code easier to read, not exempt from tests.",
        ),
    ],
    pos="d",
    explanation="Slide 19, \"Guard clauses, not pyramids\": each nested `if` is one more level of indentation and one more condition the reader must keep in mind to understand the line at the bottom. Guard clauses turn each exception into a short sentence (wrong category: skip; below the minimum: skip) and leave the real work, `totals[expense.category] += expense.amount`, at the outer level. Same idea, applied to any function: deal with the exceptions first and get out.",
    section=6,
    source_ref="S6 slide 19",
    origin="slides",
    verified_by="source",
)

mcq(
    "k_guard_diff",
    level="hard",
    skills=["read-code", "predict-output"],
    stem="A teammate rewrites version 1 as version 2 and calls the commit a refactoring. `category` and `minimum` come from the report's options, where an empty `category` means no category was given. `totals` is a `defaultdict(float)`, so a new category starts at 0.\n\nVersion 1:\n\n"
    + PYRAMID
    + "\n\nVersion 2:\n\n"
    + GUARDS
    + "\n\nFor which report do the two versions produce different totals?",
    right=(
        "`category=\"\"` (no category given) and `minimum=20.0`",
        "Right: version 2's first guard skips nothing when `category` is empty; version 1 needs `expense.category == \"\"`, which never happens, so it totals nothing.",
    ),
    wrong=[
        (
            "`category=\"dining\"` and `minimum=20.0`",
            "Both keep dining expenses of 20 or more. With a real category the two filters agree.",
        ),
        (
            "`category=\"dining\"` and `minimum=0.0`",
            "Both keep every dining expense. The minimum guard and the nested `>=` agree for any value.",
        ),
        (
            "`category=\"dining\"` and `minimum` equal to one expense's amount",
            "`>= minimum` keeps that expense and `< minimum: continue` keeps it too. The boundary is handled identically.",
        ),
    ],
    pos="a",
    explanation="Read the first guard carefully: `category != \"\" and expense.category != category`. When `category` is empty, the left side is false, so nothing is skipped and all categories are totalled. Version 1 has no such case: it only adds expenses whose category equals `category`, and none equals the empty string. Run on four sample expenses with `category=\"\"`, version 1 returned `{}` and version 2 returned a total for every category. So this rewrite changed behaviour and was not a pure refactoring. Guard clauses are the right shape; reshaping a condition is still a change that needs a behaviour check.",
    section=6,
    source_ref="S6 slide 19; S6 slide 30",
    origin="slides",
    verified_by="run",
)

mcq(
    "k_testprint",
    level="exam",
    skills=["judgement", "concept"],
    stem="A teammate's `show_totals(expenses)` adds up the amounts per category and prints one line per category. It returns nothing. You want a test that checks the transport total. What does the course suggest?",
    right=(
        "Split it: one function returns the totals and the caller prints them",
        "Right: computation is not output. Once the totals are a returned value, a test can pass a few expenses and check the transport total directly.",
    ),
    wrong=[
        (
            "Run the program before each commit and check the printed transport line by eye",
            "That is looking, not testing: it depends on someone remembering and reading carefully every time. \"A function that prints can only be looked at.\"",
        ),
        (
            "Write the expected totals in a comment above the `print` so reviewers can compare",
            "A comment is not checked by anything. It cannot fail when the totals go wrong.",
        ),
        (
            "Change the return hint to `dict[str, float]` so the test can read the totals",
            "A hint does not change what the function does: it still returns `None`. mypy would now flag the function, and the test would still have nothing to check.",
        ),
    ],
    pos="b",
    explanation="Slide 20: \"A function that returns can be tested, reused and read on its own. A function that prints can only be looked at.\" `show_totals` computes and prints in one place, so the totals never exist as a value a test can compare. The course's fix is the split `9d6c607` made in the demo: `total_by_category` returns data, `format_report` returns lines, and only `run` prints. After the split, the test is plain: build three expenses, call the function, compare the transport total.",
    section=6,
    source_ref="S6 slide 20; expense-tracker 9d6c607",
    origin="slides",
    verified_by="source",
)

mcq(
    "k_noreturn",
    level="hard",
    skills=["read-tool-output", "read-code"],
    stem="A teammate tries to test `show_totals`, which prints a table and is declared `-> None`:\n\n```python\ndef test_transport_total() -> None:\n    expenses = [\n        Expense(\"2025-07-01\", \"Cabify\", \"transport\", 36.25),\n        Expense(\"2025-07-03\", \"Can Recasens\", \"dining\", 33.02),\n        Expense(\"2025-07-03\", \"Cabify\", \"transport\", 30.57),\n    ]\n    totals = show_totals(expenses)\n    assert totals[\"transport\"] == pytest.approx(66.82)\n```\n\n`uv run pytest` prints (trimmed):\n\n```text\n>       assert totals[\"transport\"] == pytest.approx(66.82)\n               ^^^^^^^^^^^^^^^^^^^\nE       TypeError: 'NoneType' object is not subscriptable\n\ntests/test_totals.py:13: TypeError\n----------------------------- Captured stdout call -----------------------------\ndining                   33.02\ntransport                66.82\n=========================== short test summary info ============================\nFAILED tests/test_totals.py::test_transport_total - TypeError: 'NoneType' obj...\n============================== 1 failed in 0.01s ===============================\n```\n\nWhat does this output tell you?",
    right=(
        "The function prints the right totals but returns `None`, so the test has nothing to check",
        "Right: the captured output shows `transport 66.82`, yet `totals` is `None`. The numbers were printed, never returned. Computation is not output: split computing from printing.",
    ),
    wrong=[
        (
            "The function computes the wrong transport total, so the bug is in the adding",
            "The captured stdout shows `transport 66.82`, exactly the expected value. The arithmetic is fine.",
        ),
        (
            "The test expects the wrong number and should compare against the printed text instead",
            "66.82 is correct. Comparing printed text would tie the test to spacing and layout, which is the problem the course's split avoids.",
        ),
        (
            "`pytest` cannot test code that uses dataclasses, so `Expense` should go back to being a tuple",
            "The error is about `None`, not about dataclasses. Tuples would make the code harder to read and fix nothing.",
        ),
    ],
    pos="c",
    explanation="Read the output from the bottom: one test failed with a `TypeError` because `totals` is `None`, and the `Captured stdout call` block shows the function printed the correct totals. So the computation works but its result only exists as text on the screen. That is slide 20 exactly: a function that prints can only be looked at. mypy says the same before running: `\"show_totals\" does not return a value (it only ever returns None)`. The fix is to have one function return the totals and let the caller print them.",
    section=6,
    source_ref="S6 slide 20; S8 reading pytest output",
    origin="slides",
    verified_by="run",
)

mcq(
    "k_sim102",
    level="beyond",
    skills=["read-tool-output", "judgement"],
    stem="With the course's ruff settings (`select = [\"E\", \"F\", \"I\", \"UP\", \"B\", \"SIM\"]`), `uv run ruff check .` reports:\n\n```text\nSIM102 Use a single `if` statement instead of nested `if` statements\n  --> src/expense_tracker/totals.py:7:9\n   |\n 5 |       total = 0.0\n 6 |       for expense in expenses:\n 7 | /         if expense.category == \"dining\":\n 8 | |             if expense.amount >= minimum:\n   | |_________________________________________^\n 9 |                   total += expense.amount\n10 |       return total\n   |\nhelp: Combine `if` statements using `and`\n```\n\nWhat is ruff telling you, in session 6's terms?",
    right=(
        "The nested `if` is a small pyramid that can be flattened without changing behaviour",
        "Right: SIM rules suggest simpler shapes for the same logic. Combining with `and`, or turning the conditions into guards, leaves the main path flatter and the result unchanged.",
    ),
    wrong=[
        (
            "The function produces wrong totals and must be fixed before it can be merged",
            "Nothing in the finding says the result is wrong; the nested and combined forms compute the same total. It is about the shape of the code.",
        ),
        (
            "The nesting is needed for correctness here, so silence this finding with a `# noqa` comment",
            "The two conditions are independent, so combining them changes nothing. Silencing a rule you have not understood is the careless move.",
        ),
        (
            "The function does two jobs and must be split into two separate functions",
            "That is the Single Responsibility Principle, a different idea. This function has one job; ruff is commenting on how its condition is written.",
        ),
    ],
    pos="b",
    explanation="`SIM` is one of the rule families the demo selected in `04d699f`. SIM102 fires on an `if` whose only content is another `if`: the same pyramid slide 19 warns about. The help line suggests one fix (combine with `and`); the course's guard clauses are another. Either way the behaviour stays the same, which is what makes it a refactoring. The general lesson from slide 27 still applies: read the code, read the message, fix the cause.",
    section=6,
    source_ref="S6 slides 19, 27; expense-tracker 04d699f",
    origin="slides",
    verified_by="run",
)

open_q(
    "k_open_output",
    level="exam",
    skills=["read-code", "judgement"],
    stem="A teammate wrote this and wants to add a test for it:\n\n```python\nNAME_WIDTH = 20\nAMOUNT_WIDTH = 10\n\n\ndef show_totals(expenses: list[Expense]) -> None:\n    totals: dict[str, float] = {}\n    for expense in expenses:\n        totals[expense.category] = totals.get(expense.category, 0.0) + expense.amount\n    for category, amount in sorted(totals.items()):\n        print(category.ljust(NAME_WIDTH) + f\"{amount:.2f}\".rjust(AMOUNT_WIDTH))\n```\n\nFor the expenses Cabify (transport) 36.25, Can Recasens (dining) 33.02 and Cabify (transport) 30.57 it prints `dining` 33.02 and `transport` 66.82.",
    parts=[
        part(
            "1",
            "Why is this function hard to test as it is?",
            2,
            "It computes the totals and prints them, and returns nothing. A test has no value to compare: the totals only exist as text on the screen, so the function can only be looked at.",
            [
                "It returns `None`, so there is nothing for an assert to check",
                "It mixes computation with output: the numbers only exist as printed text",
            ],
            "'It has no test yet' or 'it uses a dictionary' miss the point. Saying 'it prints' without the consequence (no returned value to compare) earns one mark. Suggesting the test should compare the printed text describes a workaround, not why the design is hard to test.",
        ),
        part(
            "2",
            "Describe in words how you would change it, following 'computation is not output'.",
            2,
            "Split it in two: a function such as `category_totals` that takes the expenses and returns a dictionary of category to total, without printing, and a separate step (in `run`, or a formatting function that returns lines plus `run`) that prints them.",
            [
                "A function that returns the totals (data) and does not print",
                "Printing moves to the caller, possibly via a function that returns the lines",
            ],
            "Weak answers keep the `print` and 'also return the totals': better, but the function still prints for every caller and test. Writing the code instead of describing it ignores 'in words'. Renaming alone does not fix the design.",
        ),
        part(
            "3",
            "Describe one test you would then write, in words.",
            2,
            "Pass the totals function the three expenses above and check that it returns 66.82 for transport and 33.02 for dining. No file and no printed output are involved.",
            [
                "A concrete input: a small list of `Expense` values",
                "A concrete expected result checked on the returned value (transport 66.82)",
            ],
            "'Test that it works' or 'test the totals' is too vague to mark. The marker wants an input and an expected result. A test that runs the whole program and reads the screen goes back to the problem in part 1.",
        ),
    ],
    explanation="Slide 20's slogan is the whole answer: a function that returns can be tested, reused and read on its own; a function that prints can only be looked at. The demo made this exact move in `9d6c607`. Part 3 is the payoff, and it mirrors sample Q8's 'one test you would add, in words': a concrete input and the expected returned value.",
    section=6,
    source_ref="S6 slide 20; expense-tracker 9d6c607; sample Q8 part 3",
    origin="slides",
    verified_by="run",
)

# ----- Section 7: a tuple is a missing type ------------------------------------

mcq(
    "k_e3",
    level="core",
    skills=["read-code", "concept"],
    stem="v0.1 builds each expense like this in `run()`, and uses it in another function:\n\n```python\nrows.append((row[0], row[1], row[2], float(row[3])))\n...\nif e[3] < z:\n```\n\nWhat is the main problem the course points to in the last line?",
    right=(
        "Nobody can tell what `e[3]` holds without finding where the tuple was built",
        "Right: \"What is `e[3]`? Impossible to tell without looking it up.\" A tuple is a missing type.",
    ),
    wrong=[
        (
            "`e[3]` could be out of range and crash the program on rows that are too short",
            "Rows with the wrong number of fields are skipped before the tuple is built, so index 3 always exists. The problem is what index 3 means.",
        ),
        (
            "`z` should be in capital letters because it never changes",
            "`z` is a parameter (the minimum), not a constant, so capitals would be wrong. Its problem is that it says nothing; `minimum` does.",
        ),
        (
            "A tuple cannot hold a `float`, so the amount is lost when the row is stored",
            "Tuples hold any values; the amount is stored correctly. It is just hidden behind a position number.",
        ),
    ],
    pos="a",
    explanation="Slide 22 asks \"`row[2]` or `expense.category`?\" and answers its own question about `e[3]`: impossible to tell without looking it up. The tuple holds the right data, but the code that reads it has to remember that position 3 is the amount. The demo first named the positions (`e[AMOUNT]`, commit `5e9466d`) and then gave the concept a type (`Expense`, commit `017f926`), so the line became `if expense.amount < minimum:`.",
    section=7,
    source_ref="S6 slide 22",
    origin="slides",
    verified_by="source",
)

mcq(
    "k_frozen",
    level="exam",
    skills=["read-tool-output", "concept"],
    stem="A teammate adds a function to correct a misspelt merchant. `Expense` is the course's `@dataclass(frozen=True)` with `date`, `merchant`, `category`, `amount`.\n\n```python\ndef fix_merchant(expense: Expense) -> None:\n    if expense.merchant == \"Mercadna\":\n        expense.merchant = \"Mercadona\"\n```\n\nRunning it prints:\n\n```text\nTraceback (most recent call last):\n  File \"fix_merchant.py\", line 17, in <module>\n    fix_merchant(Expense(\"2025-07-07\", \"Mercadna\", \"groceries\", 21.50))\n    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"fix_merchant.py\", line 14, in fix_merchant\n    expense.merchant = \"Mercadona\"\n    ^^^^^^^^^^^^^^^^\n  File \"<string>\", line 18, in __setattr__\ndataclasses.FrozenInstanceError: cannot assign to field 'merchant'\n```\n\nWhat does this tell you?",
    right=(
        "`Expense` is frozen: it cannot change after creation, so build a new one instead",
        "Right: `frozen=True` means it does not change after creation. To correct the merchant, create a new `Expense` with the right name and return it.",
    ),
    wrong=[
        (
            "Strings stored inside a dataclass cannot be compared with `==` in an `if`",
            "The comparison on line 13 worked: the error is raised on line 14, the assignment. Fields can be read and compared freely.",
        ),
        (
            "The `merchant` field was declared with the wrong type and should be something other than `str`",
            "The type is fine; the new value is a string too. The message is about assigning at all, not about types.",
        ),
        (
            "Python found a typo in the field name `merchant` and suggests a different one",
            "The field name is correct. A typo would give `AttributeError ... has no attribute`; this is `cannot assign to field`.",
        ),
    ],
    pos="d",
    explanation="Read the last line first: `FrozenInstanceError: cannot assign to field 'merchant'`, raised from line 14, the assignment. Slide 24: `frozen=True` means the object does not change after creation. That is a feature: once an expense is read from the file, every part of the program that holds it can trust it stays as it was read. A function that needs a corrected value builds and returns a new `Expense` (here, with the merchant fixed) and leaves the original alone. mypy also catches this before running, as a read-only property error.",
    section=7,
    source_ref="S6 slides 23–24",
    origin="slides",
    verified_by="run",
)

mcq(
    "k_typo",
    level="hard",
    skills=["read-code", "read-tool-output", "compare"],
    stem="Two versions of the same dining total, each with one mistake. The tuples are `(date, merchant, category, amount)`.\n\nVersion A (tuples):\n\n```python\nfor e in expenses:\n    if e[1] == \"dining\":\n        dining += e[3]\nprint(f\"dining: {dining:.2f}\")\n```\n\n```text\ndining: 0.00\n```\n\nVersion B (the `Expense` dataclass):\n\n```python\nfor expense in expenses:\n    if expense.categroy == \"dining\":\n        dining += expense.amount\nprint(f\"dining: {dining:.2f}\")\n```\n\n```text\nTraceback (most recent call last):\n  File \"dataclass_version.py\", line 20, in <module>\n    if expense.categroy == \"dining\":\n       ^^^^^^^^^^^^^^^^\nAttributeError: 'Expense' object has no attribute 'categroy'. Did you mean: 'category'?\n```\n\nBoth ran on the same three expenses, two of them dining. What do the two runs illustrate?",
    right=(
        "A tuple turns a wrong index into a silent wrong answer; a dataclass turns a typo into an error",
        "Right: version A reads the merchant instead of the category and happily reports 0.00. Version B stops at the exact line and even suggests `category`.",
    ),
    wrong=[
        (
            "Version A is safer, because it ran to the end and printed a result without crashing",
            "Running to the end with the wrong answer is worse than stopping: 0.00 looks plausible and could be reported, while the crash is noticed at once.",
        ),
        (
            "Both versions have the same kind of bug, so using a tuple or a dataclass makes no real difference",
            "The mistakes are similar, but the consequences are opposite: one silent, one loud with the fix suggested. That difference is the slide's point.",
        ),
        (
            "Version B crashed because `frozen=True` stops fields being read inside a loop",
            "Frozen stops fields being assigned, not read. The error says the attribute does not exist, because of the typo.",
        ),
    ],
    pos="d",
    explanation="Slide 24: \"A typo in a field name is an error, not a silent wrong answer.\" In version A, `e[1]` is the merchant, which is never \"dining\", so the loop adds nothing and prints 0.00 with no complaint. In version B, the misspelt field is caught immediately, with the file, the line and the suggestion `Did you mean: 'category'?`. mypy catches it even earlier, before running: `\"Expense\" has no attribute \"categroy\"; maybe \"category\"?`, while it reports nothing at all on version A. And with a dataclass the editor autocompletes `expense.`, so the typo is less likely in the first place.",
    section=7,
    source_ref="S6 slide 24; expense-tracker 017f926",
    origin="slides",
    verified_by="run",
)

mcq(
    "k_concept",
    level="exam",
    skills=["concept", "judgement"],
    stem="Your group's project is a gym class booking app. Following slide 24 ('a dataclass is a naming tool'), which is the best candidate for a `@dataclass(frozen=True)`?",
    right=(
        "A booking: member, class, date and time, fixed once it is made",
        "Right: a business concept with named parts that should not change after creation. `booking.member` beats `b[0]` for the same reasons `expense.amount` beats `e[3]`.",
    ),
    wrong=[
        (
            "The function that prints the weekly timetable to the terminal",
            "A dataclass names data, not behaviour. A printing function is output; it belongs in the shell, not in a type.",
        ),
        (
            "The path of the JSON file where the bookings are stored",
            "One string with one meaning needs a good variable or constant name, not a type with fields.",
        ),
        (
            "A running count of bookings that goes up every time someone books",
            "It changes all the time, and frozen means it does not change after creation. It is a number, not a domain concept with parts.",
        ),
    ],
    pos="c",
    explanation="Slide 24: a dataclass is \"how you give a name to business domain concepts\", and \"every group project has concepts that can be modelled with a dataclass: a booking, a product, a match, a reading...\". A booking has several named parts, it is passed around the program, and once made it should stay as it is, which is what `frozen=True` guarantees. Without the type it would be a tuple such as `(\"Ana\", \"spinning\", \"Mon 18:00\")`, and a missing type.",
    section=7,
    source_ref="S6 slide 24",
    origin="slides",
    verified_by="source",
)

open_q(
    "k_open_frozen",
    level="hard",
    skills=["read-tool-output", "judgement"],
    stem="A teammate wants every amount rounded to whole euros before the report is built. `Expense` is `@dataclass(frozen=True)`.\n\n```python\ndef round_amounts(expenses: list[Expense]) -> None:\n    for expense in expenses:\n        expense.amount = round(expense.amount)\n```\n\nRunning the program prints:\n\n```text\nTraceback (most recent call last):\n  File \"round_amounts.py\", line 21, in <module>\n    round_amounts(expenses)\n    ~~~~~~~~~~~~~^^^^^^^^^^\n  File \"round_amounts.py\", line 14, in round_amounts\n    expense.amount = round(expense.amount)\n    ^^^^^^^^^^^^^^\n  File \"<string>\", line 18, in __setattr__\ndataclasses.FrozenInstanceError: cannot assign to field 'amount'\n```",
    parts=[
        part(
            "1",
            "What does the error tell you?",
            1,
            "Line 14 tries to change the `amount` of an existing `Expense`, and because `Expense` is frozen Python refuses: a frozen object cannot change after it is created.",
            ["Says the function tries to assign to a field of a frozen dataclass, which is not allowed after creation"],
            "'There is a bug on line 14' without saying why earns nothing. Blaming `round` misreads the message: the error is the assignment, `cannot assign to field`. Calling it a typo confuses it with `AttributeError`, which is a different message.",
        ),
        part(
            "2",
            "Why might the team have made `Expense` frozen in the first place? Give one concrete risk it removes.",
            2,
            "Frozen means an expense does not change after creation, so once read from the file it stays as read. Without it, `round_amounts` would silently change the caller's list: anything computed later from that list would see rounded amounts that no longer match the bank's file.",
            [
                "Frozen: an expense does not change after creation, so it stays as it was read",
                "A concrete risk: a function quietly changes data that the caller or another part of the program still uses (for example totals computed from altered amounts)",
            ],
            "'Frozen is safer' or 'to avoid errors' is too vague. The marker wants the meaning (no change after creation) and a specific harm it prevents. Saying 'for performance' is wrong: frozen is about trust in the data.",
        ),
        part(
            "3",
            "Describe in words how you would change `round_amounts` so it works with a frozen `Expense`, and how you would rename it.",
            2,
            "Instead of editing each expense, build a new `Expense` with the same date, merchant and category and the rounded amount, collect them in a new list and return it. Name it after what it returns, such as `rounded_expenses`, with return type `list[Expense]`.",
            [
                "Builds and returns new `Expense` objects in a new list instead of changing the existing ones",
                "Renames it after what it returns (for example `rounded_expenses`) and returns `list[Expense]` instead of `None`",
            ],
            "'Remove `frozen=True`' makes the error go away by removing the protection; it is the dataclass version of `# type: ignore`. Answers that return a new list but keep the name `round_amounts` and `-> None` miss the naming half.",
        ),
    ],
    explanation="The traceback is the type doing its job: slide 24, `frozen=True` means it does not change after creation. The judgement is not to switch the protection off but to change the function's shape: compute a new value and return it. That also fixes the name (functions say what they return) and makes the function easy to test, which links back to computation is not output.",
    section=7,
    source_ref="S6 slides 15, 20, 23–24",
    origin="slides",
    verified_by="run",
)

mcq(
    "k_reasons",
    level="core",
    skills=["concept"],
    stem="A teammate objects to commit `017f926`: \"Turning the expense tuple into a dataclass is just extra typing. The tuple already holds the same four values.\" Which reply uses slide 24's reasons?",
    right=(
        "Named fields: the editor autocompletes `expense.`, and a misspelt field becomes an error",
        "Right: slide 24 lists both. The editor offers `date`, `merchant`, `category` and `amount`, and `expense.categroy` stops the program instead of quietly giving a wrong total.",
    ),
    wrong=[
        (
            "A dataclass stores the four values in less memory, so the report runs noticeably faster",
            "The course never argues for dataclasses on speed or memory. The case is the economic one again: the code becomes cheaper to read and harder to get wrong.",
        ),
        (
            "A tuple cannot be described with type hints, so mypy cannot check any code that uses one",
            "It can: slide 26's own signature returns `list[tuple[str, float]]`. The tuple's problem is that `e[3]` says nothing to the reader.",
        ),
        (
            "A dataclass checks each value's type when it is created, so a text amount is rejected",
            "It does not: `Expense(\"2025-07-01\", \"Cabify\", \"transport\", \"36.25\")` runs and stores the text. Hints are read by mypy and by people; Python does not check them while running.",
        ),
    ],
    pos="a",
    explanation="Slide 24 calls a dataclass a naming tool: it is how you give a name to a business concept. It lists what you get: `frozen=True` means it does not change after creation, the editor autocompletes `expense.` with its fields, and a typo in a field name is an error, not a silent wrong answer. With the tuple, `e[3]` has to be looked up, and `e[1]` instead of `e[2]` quietly gives the wrong total. The teammate is right that the values are the same. The difference is how much the next reader has to remember, which is the economic argument from the start of the session.",
    section=7,
    source_ref="S6 slides 23–24, 26",
    origin="slides",
    verified_by="run",
)

mcq(
    "k_ammount",
    level="beyond",
    skills=["read-code", "read-tool-output", "judgement"],
    stem=md(
        """
        To make a rounding function work, a teammate removes `frozen=True` from the course's `Expense` dataclass (fields `date`, `merchant`, `category`, `amount`) and writes:

        ```python
        def round_amounts(expenses: list[Expense]) -> None:
            for expense in expenses:
                expense.ammount = round(expense.amount)
        ```

        The teammate misspelt the attribute name as `ammount`. The program calls the function on two expenses and then prints each merchant and amount:

        ```console
        $ uv run python rounding.py
        Cabify: 36.25
        Can Recasens: 33.02
        ```

        No error appears, and nothing was rounded. What happened?
        """
    ),
    right=(
        "Python created a new attribute `ammount`; the real `amount` field was never touched",
        "Right: on a dataclass that is not frozen, assigning to any name is allowed, so the typo quietly adds an attribute. Frozen would have stopped it with `FrozenInstanceError: cannot assign to field 'ammount'`.",
    ),
    wrong=[
        (
            "The loop changed copies of the expenses, so the originals in the list kept their amounts",
            "The loop gets the same objects that are in the list. A correctly spelt `expense.amount = ...` would have changed them.",
        ),
        (
            "`round` keeps two decimals unless told otherwise, so 36.25 was stored as 36.25 again",
            "`round(36.25)` with no second argument gives `36`. The rounding happened; the result was stored under the wrong name.",
        ),
        (
            "The `:.2f` in the f-string puts back the decimals that `round` removed before printing",
            "Formatting shows the stored value with two decimals, so a rounded 36 would print as `36.00`. The output shows the original amounts because they never changed.",
        ),
    ],
    pos="c",
    explanation="Slide 24 says a typo in a field name is an error, not a silent wrong answer. That holds when you read a field: `expense.categroy` raises `AttributeError`. Writing is different. On a dataclass that is not frozen, Python lets you assign any name, so `expense.ammount = ...` creates a new attribute and leaves `amount` as it was. The run ends normally with the original amounts: a silent wrong answer. Two things would have caught it. With `frozen=True` the same line stops with `FrozenInstanceError: cannot assign to field 'ammount'`. And `mypy --strict` reports `\"Expense\" has no attribute \"ammount\"; maybe \"amount\"?` before the program runs. Removing `frozen` to allow changes in place also removed a safety net; the course's shape is to keep it frozen and return new `Expense` objects.",
    section=7,
    source_ref="S6 slides 23–24; beyond: assigning a misspelt field on a dataclass that is not frozen",
    origin="slides",
    verified_by="run",
)

# ----- Section 8: type hints and ruff -------------------------------------------

mcq(
    "k_contract",
    level="exam",
    skills=["read-tool-output", "read-code"],
    stem="`total_by_category` has v0.2's hints:\n\n```python\ndef total_by_category(\n    expenses: list[Expense], category: str, minimum: float\n) -> list[tuple[str, float]]:\n    ...\n\ncategory = \"dining\"\nminimum = 20.0\ntotals = total_by_category(expenses, minimum, category)\n```\n\n`uv run mypy src` reports:\n\n```text\nsrc/expense_tracker/weekly.py:34: error: Argument 2 to \"total_by_category\" has incompatible type \"float\"; expected \"str\"  [arg-type]\nsrc/expense_tracker/weekly.py:34: error: Argument 3 to \"total_by_category\" has incompatible type \"str\"; expected \"float\"  [arg-type]\nFound 2 errors in 1 file (checked 4 source files)\n```\n\nWhat does mypy tell you?",
    right=(
        "The call on line 34 passes two arguments in the wrong order, caught before running",
        "Right: argument 2 should be the category (a `str`) and argument 3 the minimum (a `float`). The signature is the contract and this call breaks it.",
    ),
    wrong=[
        (
            "The hints on `total_by_category` are too strict and should accept any type at all",
            "The hints are correct; the call is wrong. Loosening the contract to fit a wrong call hides the bug instead of fixing it.",
        ),
        (
            "The function has a bug inside: it compares an amount with a string",
            "Both errors point at line 34, the call, and talk about arguments 2 and 3. The function body is fine when called correctly.",
        ),
        (
            "mypy cannot handle `float` values, so these two errors can be safely ignored",
            "mypy handles floats perfectly well; it is reporting that a `float` arrived where a `str` was promised. Ignoring it ships the bug.",
        ),
    ],
    pos="c",
    explanation="Slide 26: type hints are contracts. They say what goes in and what comes out, they are read by the next person and by mypy, and a wrong call becomes an error before the program runs. Read the message in the order session 7 teaches: file and line (`weekly.py:34`, the call), the message (argument 2 got a `float` where a `str` is expected, and argument 3 the reverse), and the code in brackets. Together they say the two arguments are swapped. The fix is to swap them back in the call.",
    section=8,
    source_ref="S6 slide 26; S7 slide 9",
    origin="slides",
    verified_by="run",
)

mcq(
    "k_runtime",
    level="beyond",
    skills=["predict-output", "concept"],
    stem="Same code as before: `total_by_category` is fully hinted, its body is v0.2's (the category guard runs before the minimum guard), and the call swaps the arguments:\n\n```python\ncategory = \"dining\"\nminimum = 20.0\ntotals = total_by_category(expenses, minimum, category)\nprint(totals)\n```\n\nThe expenses include Can Recasens (dining) 33.02 and Bo de B (dining) 33.94. Nobody runs mypy; the program is started with `uv run python src/expense_tracker/weekly.py`. What happens?",
    right=(
        "It runs without an error and prints `[]`, because Python does not check hints while running",
        "Right: hints are read by people and mypy, not enforced by Python. The swapped call runs, every expense is skipped, and you get an empty list: a silent wrong answer.",
    ),
    wrong=[
        (
            "Python stops at the call with a `TypeError`, because the hints say `category` must be a `str`",
            "Python does not enforce hints at run time. Only a checker such as mypy, run before the program, turns a broken contract into an error.",
        ),
        (
            "It prints the correct dining total, because Python matches the arguments by their names",
            "Arguments are matched by position here, not by the variable names in the caller. `minimum` lands in the `category` slot.",
        ),
        (
            "It prints `[]` and that is fine: no dining expense in the data reaches 20",
            "Two dining expenses are over 20 (33.02 and 33.94). The empty list is wrong; it comes from the swapped arguments.",
        ),
    ],
    pos="b",
    explanation="This run printed `[]` and exited normally. Inside the function, `category` is `20.0`, which is not empty and matches no expense's category, so the first guard skips every expense. Python never looked at the hints. That is the small step past slide 26: hints are a contract only because someone reads them. Read by mypy, the same call is two errors before the program runs; unread, it is a quiet wrong answer, the kind a reviewer would only notice if they knew the expected total.",
    section=8,
    source_ref="S6 slide 26",
    origin="slides",
    verified_by="run",
)

mcq(
    "k_checkformat",
    level="core",
    skills=["concept"],
    stem="Which pair describes the two ruff commands as session 6 uses them?",
    right=(
        "`ruff check` finds problems; `ruff format` fixes layout",
        "Right: that is the slide word for word. Formatting changes spacing and wrapping; checking reports problems such as unused imports for you to fix.",
    ),
    wrong=[
        (
            "`ruff check` fixes layout; `ruff format` finds bugs",
            "Swapped. `ruff format` only rewrites layout and never reports bugs; `ruff check` is the one that reports findings.",
        ),
        (
            "`ruff check` runs the tests; `ruff format` checks the types",
            "Tests are pytest's job and types are mypy's. ruff is the linter and formatter.",
        ),
        (
            "Both do the same thing; `format` is just the newer name",
            "They do different jobs, which is why the course runs both, and why CI runs both `ruff check .` and `ruff format --check .`.",
        ),
    ],
    pos="d",
    explanation="Slide 27: `uv run ruff check .` finds problems, `uv run ruff format .` fixes layout. The settings for both live once in `pyproject.toml` (`line-length = 100`, the selected rule families), so the tool decides and CI enforces. The difference matters when you read output: a formatter can wrap a long line, but it will never decide for you that an import is unused and delete it.",
    section=8,
    source_ref="S6 slide 27; partial-rubric check commands",
    origin="slides",
    verified_by="source",
)

mcq(
    "k_format_f401",
    level="exam",
    skills=["read-tool-output", "judgement"],
    stem="A teammate runs:\n\n```console\n$ uv run ruff check .\nF401 [*] `os` imported but unused\n --> src/expense_tracker/budget.py:2:8\nE501 Line too long (102 > 100)\n  --> src/expense_tracker/budget.py:14:101\nFound 2 errors.\n[*] 1 fixable with the `--fix` option.\n$ uv run ruff format .\n1 file reformatted, 4 files left unchanged\n$ uv run ruff check .\nF401 [*] `os` imported but unused\n --> src/expense_tracker/budget.py:2:8\nFound 1 error.\n[*] 1 fixable with the `--fix` option.\n```\n\n(Output trimmed: the code excerpts under each finding are not shown.) What does the second `ruff check` tell you?",
    right=(
        "Formatting fixed the long line; the unused import is a code problem for you to remove",
        "Right: `ruff format` wrapped the long line, so `E501` is gone. Deciding that `import os` is not needed is not a layout question; you check and remove it.",
    ),
    wrong=[
        (
            "ruff is broken, because `format` should have removed the unused import; run `uv sync` first",
            "Nothing is broken: a formatter never removes code. Reinstalling or syncing is the careless move the course warns about.",
        ),
        (
            "The long line was a false alarm, since formatting made the finding go away",
            "The line really was 102 characters. Formatting fixed it by wrapping it, which is exactly the layout job `ruff format` exists for.",
        ),
        (
            "Both findings are about layout, so run `ruff format` again until nothing is left",
            "Running the formatter again changes nothing (the file is already formatted). `F401` is about what the code uses, not how it looks.",
        ),
    ],
    pos="a",
    explanation="Slide 27 splits the work: `ruff check` finds problems, `ruff format` fixes layout. The transcript shows it. `E501` was a layout problem (a line over the project's 100 characters), and the formatter wrapped it. `F401` reports an import nobody uses; that is about the code's content, so it survives formatting. The slide's method applies: read the code (is `os` really unused, or did someone forget to finish a feature?), read the message, fix the cause by removing the import. The formatter worked here because wrapping the `return` in brackets was enough to get under 100. It does not split a long string, so a long message line still needs you to split it.",
    section=8,
    source_ref="S6 slide 27",
    origin="slides",
    verified_by="run",
)

mcq(
    "k_f841",
    level="hard",
    skills=["read-tool-output", "read-code", "judgement"],
    stem="A teammate's pricing code:\n\n```python\nSTUDENT_DISCOUNT = 0.15\n\n\ndef basket_total(prices: list[float], is_student: bool) -> float:\n    total = sum(prices)\n    if is_student:\n        discounted = total * (1 - STUDENT_DISCOUNT)\n    return total\n```\n\n`uv run ruff check .` reports (mypy reports no issues):\n\n```text\nF841 Local variable `discounted` is assigned to but never used\n --> src/shop/pricing.py:7:9\n  |\n5 |     total = sum(prices)\n6 |     if is_student:\n7 |         discounted = total * (1 - STUDENT_DISCOUNT)\n  |         ^^^^^^^^^^\n8 |     return total\n  |\nhelp: Remove assignment to unused variable `discounted`\n```\n\nWhat should you do?",
    right=(
        "Read the code: the discount is never applied, so return the discounted total for students",
        "Right: the finding is the symptom of a real bug, and students pay full price. `basket_total([10.0, 30.0], is_student=True)` returns 40.0. The fix is to use the value, not to delete it.",
    ),
    wrong=[
        (
            "Follow the help line: delete the `discounted = ...` line and commit the fix",
            "That makes ruff quiet and the bug permanent: students would never get the discount, and the evidence would be gone.",
        ),
        (
            "Add `# noqa: F841` to the line, since mypy reports no type problems in this file",
            "mypy checks types, and the types here are fine. Silencing the linter hides the only tool that noticed the bug.",
        ),
        (
            "Rename `discounted` to `_discounted` so ruff treats it as a value that is deliberately unused",
            "ruff does accept the underscore name, but the discount is still never applied. It silences the message and keeps the bug.",
        ),
    ],
    pos="c",
    explanation="Slide 27: read the code, read the message, fix the cause. The message says a value was computed and thrown away. Reading the code shows why it matters: the function was meant to return the discounted total for students, and it returns `total` for everyone. Run with two prices for a student, it returns 40.0 instead of 34.0. The help line describes how to make the finding go away, not what the code should do; following it blindly, adding `# noqa`, or renaming to `_discounted` all leave the bug in place.",
    section=8,
    source_ref="S6 slide 27",
    origin="slides",
    verified_by="run",
)

mcq(
    "k_fmtcheck",
    level="hard",
    skills=["read-tool-output", "judgement"],
    stem="You add a budget module to the expense-tracker and push. CI runs the demo's workflow: `uv run ruff check .`, then `uv run ruff format --check .`, then mypy and pytest. The job is red at the second step. You run the first two steps locally:\n\n"
    + md(
        """
        ```console
        $ uv run ruff check .
        All checks passed!
        $ uv run ruff format --check .
        unformatted: File would be reformatted
         --> src/expense_tracker/budget.py:5:17
          |
        4 | def is_over_budget(spent: float, budget: float) -> bool:
          -     return spent>budget*BUDGET_WARNING_SHARE
        5 +     return spent > budget * BUDGET_WARNING_SHARE
        6 |
        7 |
        8 | def budget_message(category: str, spent: float) -> str:
          -     return 'Budget for ' + category + ': ' + f'{spent:.2f}'
        9 +     return "Budget for " + category + ": " + f"{spent:.2f}"
          |

        1 file would be reformatted, 7 files already formatted
        ```
        """
    )
    + "\n\nWhat can you conclude?",
    right=(
        "`budget.py` is not in the agreed layout; `ruff format .` would change only spacing and quotes",
        "Right: `--check` reports what the formatter would change and exits with an error code, which turns the step red. Run `uv run ruff format .`, look at what changed, then commit and push.",
    ),
    wrong=[
        (
            "`budget.py` has a bug that `ruff check` missed and the format step has now caught",
            "The preview shows only spaces around `>` and `*` and single quotes becoming double. The program does the same thing either way: this is layout, the job slide 27 gives to `ruff format`.",
        ),
        (
            "The `--check` run has already reformatted the file, so pushing again turns CI green",
            "`--check` changes no files; it only reports. Nothing is fixed until someone runs `ruff format .` and commits the result.",
        ),
        (
            "The two ruff commands contradict each other, so one is misconfigured in `pyproject.toml`",
            "They do different jobs and read the same settings. `ruff check` found no problems and `ruff format --check` found layout that is not the agreed one: both can be right at once.",
        ),
    ],
    pos="b",
    explanation="Read the transcript in order. `ruff check` passed: no unused import, no bare `except`, nothing it calls a problem. `ruff format --check` changes no files; it reports the file that would change and ends with a non-zero exit code, which is what turns the CI step red. The preview shows what would change: spaces around `>` and `*`, and single quotes turned into double. That is layout, the job slide 27 gives to `ruff format`. The fix is to run the formatter, look at what it changed, and commit. This is the arbiter at work: the layout is settled once for the project, the tool decides and CI enforces it, so nobody has to argue about quotes.",
    section=8,
    source_ref="S6 slide 27; S3 (CI is the referee); expense-tracker 0e05065",
    origin="slides",
    verified_by="run",
)

mcq(
    "k_ten",
    level="hard",
    skills=["read-tool-output", "judgement"],
    stem="Commit `04d699f` added the ruff settings to `pyproject.toml` and fixed every finding. Run with those settings on the code just before it (`017f926`), ruff reports, one line per finding:\n\n```text\nsrc/expense_tracker/cli.py:38:9: SIM115 Use a context manager for opening files\nsrc/expense_tracker/cli.py:42:48: UP031 Use format specifiers instead of percent format\nsrc/expense_tracker/cli.py:44:59: UP031 Use format specifiers instead of percent format\nsrc/expense_tracker/cli.py:44:101: E501 Line too long (101 > 100)\nsrc/expense_tracker/report.py:1:1: I001 [*] Import block is un-sorted or un-formatted\nsrc/expense_tracker/report.py:72:44: UP031 Use format specifiers instead of percent format\nsrc/expense_tracker/report.py:77:48: UP031 Use format specifiers instead of percent format\nsrc/expense_tracker/report.py:80:47: UP031 Use format specifiers instead of percent format\nsrc/expense_tracker/report.py:92:16: UP031 Use format specifiers instead of percent format\nsrc/expense_tracker/report.py:100:5: E722 Do not use bare `except`\nFound 10 errors.\n```\n\nWhich finding points to code that can hide a bug from you, and what did the commit do about it?",
    right=(
        "`E722`: every error became 'could not read'; the commit narrowed it to two exceptions",
        "Right: a bare `except` turns every failure, including a typo or a missing import, into the same message. Once only the two expected exceptions are caught, anything else surfaces as the bug it is.",
    ),
    wrong=[
        (
            "`I001`: unsorted imports can make Python load the wrong module; the commit sorted them",
            "Import order is tidiness: the same modules load either way. The commit sorted them so every file looks the same, not to fix a bug.",
        ),
        (
            "`UP031`: percent formatting can print amounts wrongly; the commit switched to f-strings",
            "`\"%.2f\" % amount` and `f\"{amount:.2f}\"` print the same text. The report after the commit is identical to v0.1's, so nothing was printing wrongly.",
        ),
        (
            "`E501`: a line over 100 characters can break on narrow terminals; the commit shortened it",
            "Line length is about reading the source, not running it. The program behaves the same; the agreed limit keeps the code readable side by side.",
        ),
    ],
    pos="d",
    explanation="Ask of each finding what it changes when the program runs. `I001` (import order), `UP031` (old-style `%` formatting) and `E501` (line length) are about how the code reads and which style the team agreed; `SIM115` asks for `with` so the file is always closed. `04d699f` fixed all of them and the dining report stayed byte for byte the same as v0.1's. `E722` is the one that hides problems: `except:` catches everything, so a typo, a missing import or Ctrl-C would all appear as 'could not read'. The commit narrowed it to the two errors reading a CSV can really raise. Read the code, read the message, fix the cause.",
    section=8,
    source_ref="expense-tracker 017f926..04d699f; S6 slide 27",
    origin="history",
    verified_by="run",
)

mcq(
    "k_arbiter",
    level="exam",
    skills=["judgement"],
    stem="Two teammates keep rewriting each other's files: one prefers single quotes and 80-character lines, the other double quotes and 120. Every pull request is full of these changes. What does session 6 say should settle it?",
    right=(
        "Agree the rules once in `pyproject.toml`; ruff applies them and CI enforces them",
        "Right: \"Nobody argues about quotes or line length again; the tool decides, and CI enforces it.\"",
    ),
    wrong=[
        (
            "Whoever wrote the file decides its style, since they understand it best",
            "Then the style changes from file to file and the arguments move to every review. The point is one rule for the whole repo.",
        ),
        (
            "Each teammate sets up their own editor the way they prefer and ignores the other's changes",
            "That is what causes the churn: two editors reformatting each other's lines. A shared configuration in the repo removes it.",
        ),
        (
            "Vote on the style at each Sprint Review and use the winner for the next sprint",
            "It turns a settled question into a recurring meeting topic. The course's answer is to configure it once and let the tool decide.",
        ),
    ],
    pos="b",
    explanation="Slide 27, \"The linter is the arbiter\": the rules are configured once in `pyproject.toml` (the demo uses `line-length = 100` and a `select` list), nobody argues about quotes or line length again, the tool decides, and CI enforces it. 'Arbiter' is the word to remember: like 'the referee, not the judge' for CI, it takes a dispute off the people and gives it to an agreed rule. Teammates then spend review time on names and responsibilities, which a tool cannot judge.",
    section=8,
    source_ref="S6 slide 27; expense-tracker 04d699f",
    origin="slides",
    verified_by="source",
)

open_q(
    "k_open_ruff",
    level="hard",
    skills=["read-tool-output", "read-code", "judgement"],
    stem="Your teammate's file in the group project:\n\n```python\nimport json\nimport os\nfrom dataclasses import dataclass\n\n\n@dataclass(frozen=True)\nclass Booking:\n    member: str\n    session: str\n    day: str\n\n\ndef load_bookings(path: str) -> list[Booking]:\n    try:\n        with open(path) as handle:\n            rows = json.load(handle)\n    except:\n        return []\n    return [Booking(row[\"member\"], row[\"session\"], row[\"day\"]) for row in rows]\n\n\ndef confirmation(booking: Booking) -> str:\n    return f\"{booking.member} is booked on {booking.session} on {booking.day}. Please arrive ten minutes early.\"\n```\n\nCI fails at the ruff step. `uv run ruff check .` reports (code excerpts trimmed):\n\n```text\nF401 [*] `os` imported but unused\n --> src/gym/bookings.py:2:8\nE722 Do not use bare `except`\n  --> src/gym/bookings.py:17:5\nE501 Line too long (112 > 100)\n  --> src/gym/bookings.py:23:101\nFound 3 errors.\n[*] 1 fixable with the `--fix` option.\n```",
    parts=[
        part(
            "1",
            "In plain words, what does each finding tell you?",
            3,
            "F401: the file imports `os` but never uses it. E722: line 17 catches every possible error with a bare `except`. E501: line 23 is 112 characters long, over the 100 the project agreed in `pyproject.toml`.",
            [
                "F401: `os` is imported but never used",
                "E722: a bare `except` catches every error, whatever it is",
                "E501: the line is longer than the project's agreed limit (100 characters, set in `pyproject.toml`)",
            ],
            "Repeating the message ('line too long') without the meaning earns little: say too long compared with what, and where the limit comes from. Calling E722 a 'syntax error' is wrong; the code runs. Each finding is one mark, so skipping one caps the part at two.",
        ),
        part(
            "2",
            "Which finding could hurt a real user, and how?",
            2,
            "E722. If the bookings file is missing or invalid, or someone mistypes a name inside the `try`, `load_bookings` quietly returns an empty list. The member is told they have no bookings instead of being told something went wrong.",
            [
                "Picks E722",
                "Consequence: any failure (missing file, bad JSON, even a bug inside the `try`) becomes an empty list, so the user sees 'no bookings' instead of an error",
            ],
            "Choosing E501 or F401 shows the student has not separated style from behaviour: neither changes what the program does. 'E722 is dangerous' without saying what the user would see earns one mark of two.",
        ),
        part(
            "3",
            "Your teammate proposes adding `# noqa` to all three lines and raising `line-length` to 120 'to get CI green before the deadline'. Do you accept? Give your reasoning.",
            2,
            "No. The rules were agreed once and CI enforces them for everyone; changing them to pass moves the goalposts, and silencing would hide a real bug (E722). The fixes are quick: delete the import, catch only `OSError` and `ValueError`, split the long string.",
            [
                "Rejects the proposal",
                "Reason: the rules are agreed once and enforced by CI; silencing or loosening them to pass hides the cause (read the message, fix the cause)",
                "Notes that E722 hides a real problem, or that the real fixes are small",
            ],
            "'Yes, CI must be green' misses that green with silenced rules proves nothing. 'No, rules are rules' without a reason earns one mark. The strongest answers name the real bug that `# noqa` would hide.",
        ),
    ],
    explanation="This is sample Q9's shape applied to ruff instead of mypy: read each finding, separate the one that changes behaviour from the ones about tidiness, and refuse to silence the referee. Slide 27's method, read the code, read the message, fix the cause, gives all three answers. Note that `load_bookings(\"data/bookings.json\")` on a missing file really does return `[]` with no message.",
    section=8,
    source_ref="S6 slide 27; sample Q9 shape; S7 slide 18",
    origin="teacher-variant",
    verified_by="run",
)

# ----- Section 9: pair exercise and the five commits ----------------------------

mcq(
    "k_diff_empty",
    level="core",
    skills=["read-tool-output", "judgement"],
    stem="In the pair exercise you saved the report, renamed three things, extracted a function out of `run()`, then ran:\n\n```console\n$ uv run expenses report --category dining --min 20 > after.txt\n$ diff before.txt after.txt\n$\n```\n\nWhat can you conclude?",
    right=(
        "For this command and data the output is identical: the behaviour you checked is kept",
        "Right: `diff` prints only the differences, and it printed nothing. \"Nothing printed = you're safe\" for this report.",
    ),
    wrong=[
        (
            "The refactored code is now free of bugs and ready for any input you give it",
            "`diff` compared one report on one file. It says nothing about correctness, or about inputs you did not run.",
        ),
        (
            "The code is now ruff clean, since `diff` found nothing to report",
            "`diff` compares two text files; it does not lint code. Run `ruff check` for that.",
        ),
        (
            "The renames need no review now, because `diff` has already checked them",
            "`diff` checks that the output is the same on one input. Whether the new names say what they hold, or the extracted function has one job, is for a reader to judge.",
        ),
    ],
    pos="a",
    explanation="Slide 30: the output must stay identical, check it with `diff before.txt after.txt`, and \"nothing printed = you're safe\". That is the definition of a refactoring: the structure changed, the behaviour did not. Read the claim precisely: safe for what you compared. The empty `diff` shows this command printed the same text before and after; it does not prove other options or other files behave the same, or that the code is right.",
    section=9,
    source_ref="S6 slide 30",
    origin="slides",
    verified_by="run",
)

mcq(
    "k_diff_width",
    level="exam",
    skills=["read-tool-output", "judgement"],
    stem="Your partner replaced the magic numbers in `run()` with constants, then ran the check:\n\n```console\n$ uv run expenses report --category dining --min 20 > after.txt\n$ diff before.txt after.txt\n5c5\n< dining                 3157.92\n---\n> dining                   3157.92\n7c7\n< TOTAL                  3157.92\n---\n> TOTAL                    3157.92\n```\n\nWhat do you conclude?",
    right=(
        "The output changed, so it is not a refactoring yet: fix the step that moved the amounts",
        "Right: lines 5 and 7 differ, so behaviour changed. The amounts moved right by two spaces, which points at a width constant with the wrong value.",
    ),
    wrong=[
        (
            "Only spaces changed and the totals are the same, so the refactoring is fine to commit as it is",
            "A refactoring keeps the output identical, spaces included. Anyone or anything reading those columns would see a different report.",
        ),
        (
            "`diff` is too strict about whitespace, so compare the two files by eye instead",
            "The strictness is the point: it caught a change you would miss by eye. Switching to eyeballing throws away the check.",
        ),
        (
            "Save the new output as `before.txt` so that the next `diff` comes out empty",
            "That makes the check pass by changing the reference, not the code. The bug in the constant stays.",
        ),
    ],
    pos="c",
    explanation="Read the `diff`: `5c5` means line 5 changed; `<` is the old line from `before.txt` and `>` the new one. Both changed lines have the amount two spaces further right, and the total is unchanged. In the real run this came from typing `AMOUNT_WIDTH = 12` instead of 10. Slide 30's rule: the output must stay identical, and if it does not, you have not refactored. Undo or correct the last step and run the check again until `diff` prints nothing.",
    section=9,
    source_ref="S6 slides 16, 30; labs/07-refactor.md",
    origin="slides",
    verified_by="run",
)

mcq(
    "k_commitmsg",
    level="exam",
    skills=["read-diff"],
    stem="This hunk is from one of the five commits between v0.1 and v0.2:\n\n```diff\n-    print(\"Expense report for \" + path)\n+\n+def format_report(path, category, minimum, totals, largest):\n+    lines = [\"Expense report for \" + path]\n     if category != \"\":\n-        print(\"category: \" + category)\n+        lines.append(\"category: \" + category)\n     if minimum > 0.0:\n-        print(\"only amounts of \" + (\"%.2f\" % minimum) + \" or more\")\n-    print(\"-\" * RULE_WIDTH)\n+        lines.append(\"only amounts of \" + (\"%.2f\" % minimum) + \" or more\")\n+    lines.append(\"-\" * RULE_WIDTH)\n```\n\nWhich commit message belongs to it?",
    right=(
        "Separate reading and printing from the calculation",
        "Right: `print(...)` becomes `lines.append(...)` inside a new `format_report`, which returns lines instead of printing. That is commit `9d6c607`.",
    ),
    wrong=[
        (
            "Rename calculate_totals to total_by_category",
            "That commit only renamed things. Here code moves into a new function and stops printing, which is more than a rename.",
        ),
        (
            "Give an expense a type instead of a tuple",
            "That commit replaced `expense[AMOUNT]` with `expense.amount`. No tuple or dataclass appears in this hunk.",
        ),
        (
            "Add type hints and make the code ruff clean",
            "That commit added annotations and f-strings. This hunk has no hints and still uses `\"%.2f\" %` formatting, so it comes before it.",
        ),
    ],
    pos="d",
    explanation="Read what changed, not what stayed: every `-` line is a `print`, and every `+` line appends the same text to a list inside the new `format_report`. That is computation (here, building text) separated from output, the job of `9d6c607`. Two clues rule out the last commit: no type hints, and the old `%` formatting that `04d699f` replaced with f-strings. The constant `RULE_WIDTH` shows it comes after `5e9466d`. Good commit messages make this matching possible six months later.",
    section=9,
    source_ref="expense-tracker 9d6c607",
    origin="history",
    verified_by="source",
)

sort_q(
    "s_commits",
    level="hard",
    skills=["read-diff"],
    stem="Each fragment comes from one of the five commits that took the expense-tracker from v0.1 to v0.2. Sort each into its commit.",
    categories=[
        ("c8", "`5e9466d` Replace magic numbers with named constants"),
        ("c9", "`f3bb801` Rename calculate_totals to total_by_category"),
        ("c10", "`9d6c607` Separate reading and printing from the calculation"),
        ("c11", "`017f926` Give an expense a type instead of a tuple"),
        ("c12", "`04d699f` Add type hints and make the code ruff clean"),
    ],
    items=[
        ("```diff\n-    print(\"-\" * 40)\n+    print(\"-\" * RULE_WIDTH)\n```", "c8", "A bare 40 gets a name that says what it is."),
        ("```diff\n-        if e[3] < z:\n+        if e[AMOUNT] < z:\n```", "c8", "The tuple position gets a name; `e` and `z` are still unrenamed, so this is before the renaming commit."),
        ("```diff\n-def calculate_totals(x, y, z):\n+def total_by_category(expenses, category, minimum):\n```", "c9", "The commit's title in one line: the function now says what it returns, and the parameters say what they hold."),
        ("```diff\n-    grand = 0\n+    grand_total = 0\n```", "c9", "Pure renaming of a variable, part of the same commit."),
        ("```diff\n-        print(\"category: \" + category)\n+        lines.append(\"category: \" + category)\n```", "c10", "Printing becomes building lines: computation is separated from output."),
        ("```diff\n+def read_expenses(path):\n+    expenses = []\n+    with open(path) as handle:\n```", "c10", "Reading the file is extracted out of `run()` into its own function."),
        ("```diff\n-        if expense[AMOUNT] < minimum:\n+        if expense.amount < minimum:\n```", "c11", "Index access becomes a named field: the tuple has been replaced by `Expense`."),
        ("```diff\n+@dataclass(frozen=True)\n+class Expense:\n```", "c11", "The new type itself."),
        ("```diff\n-def largest_expense(expenses):\n+def largest_expense(expenses: list[Expense]) -> Expense | None:\n```", "c12", "Type hints added to an existing function: the contract."),
        ("```diff\n-    except:\n-        print(\"could not read \" + path)\n+    except (OSError, ValueError):\n+        print(f\"could not read {path}\")\n```", "c12", "The bare `except` that ruff flags as E722 is narrowed to the two expected errors; the message moves to an f-string, as everywhere in that commit."),
    ],
    explanation="Each commit does one kind of change, which is what makes the history readable. Clues to use: bare numbers becoming names (constants); single letters becoming words (rename); `print` becoming `lines.append` or a new `read_` function (separating computation from output); `[AMOUNT]` becoming `.amount` (the type); annotations, f-strings and a narrower `except` (hints and ruff). Slide 31 replays them in this order, asking for the name at each step.",
    section=9,
    source_ref="S6 slide 31; expense-tracker 5e9466d, f3bb801, 9d6c607, 017f926, 04d699f",
    origin="history",
    verified_by="source",
)

open_q(
    "k_open_compare",
    level="exam",
    skills=["read-diff", "compare"],
    stem="A teammate shows you this part of a commit from the expense-tracker history:\n\n```diff\n+@dataclass(frozen=True)\n+class Expense:\n+    date: str\n+    merchant: str\n+    category: str\n+    amount: float\n...\n def total_by_category(expenses, category, minimum):\n     totals = {}\n     for expense in expenses:\n-        if category != \"\" and expense[CATEGORY] != category:\n+        if category != \"\" and expense.category != category:\n             continue\n-        if expense[AMOUNT] < minimum:\n+        if expense.amount < minimum:\n             continue\n```\n\nTwo candidate commit messages:\n\n- A: `Update report.py`\n- B: `Give an expense a type instead of a tuple`",
    parts=[
        part(
            "1",
            "What does this change do?",
            2,
            "It introduces a frozen `Expense` dataclass with named fields and makes `total_by_category` read `expense.category` and `expense.amount` instead of tuple positions. What the function computes does not change.",
            [
                "Introduces a frozen dataclass `Expense` with four named fields",
                "Replaces index access with named fields, and says behaviour is unchanged (a refactoring)",
            ],
            "'It adds a class' is half an answer: say what the class replaces. Missing that the output stays the same misses the point that this is a refactoring, not a feature.",
        ),
        part(
            "2",
            "Which message is better for someone reading the history six months later, and why?",
            2,
            "B. It says what changed and why it matters, so someone scanning `git log` finds this step without opening the diff. A only names the file, which the diff shows anyway.",
            [
                "Chooses B",
                "Reason: B states the intent of the change; A names only the file, which the history already shows",
            ],
            "'B is longer' is not a reason. 'A is too vague' earns one mark; say what the reader of the history gains from B: the intent of the change, readable in one line without opening the diff.",
        ),
        part(
            "3",
            "How would you check, before committing, that this change did not alter what the program does?",
            2,
            "Save the output of the same report before and after the change, for example the dining report with minimum 20, into `before.txt` and `after.txt`, and run `diff` on them. If it prints nothing, the output is identical for that report.",
            [
                "The same command run before and after, with the output saved",
                "`diff` printing nothing means identical output; any difference means behaviour changed",
            ],
            "'Run it and see if it works' is not a check: works compared with what? 'Run ruff' checks style, not behaviour. The marker wants a before and after comparison of the actual output.",
        ),
    ],
    explanation="This follows sample Q8's shape (a diff, two commit messages) on commit `017f926`. Part 1 rewards recognising the move (a tuple is a missing type) and that it is a refactoring. Part 2 is about history as documentation for the next reader. Part 3 replaces Q8's 'test you would add' with the check session 6 actually teaches: before, after, `diff`.",
    section=9,
    source_ref="expense-tracker 017f926; S6 slides 23, 30; sample Q8 shape",
    origin="teacher-variant",
    verified_by="source",
)

open_q(
    "k_open_pair",
    level="hard",
    skills=["read-tool-output", "judgement"],
    stem="During the pair exercise on v0.1, your partner extracts `largest_expense` out of `run()`. While doing it, they make it look only at the expenses that pass the category and minimum filters, \"because a dining report that shows a home expense as the largest is obviously wrong\". You run the check:\n\n```console\n$ uv run expenses report --category dining --min 20 > after.txt\n$ diff before.txt after.txt\n10c10\n< Ferreteria Mas (home) on 2025-11-17 for 296.49\n---\n> Bar Alegria (dining) on 2025-11-13 for 73.20\n```",
    parts=[
        part(
            "1",
            "What does the `diff` output tell you?",
            1,
            "Only line 10 changed: the largest expense was Ferreteria Mas (home) for 296.49 and is now Bar Alegria (dining) for 73.20. Everything else in the report is identical.",
            ["Line 10, the largest-expense line, changed from the home expense to a dining one, and nothing else changed"],
            "'The output is different' without saying which line and how earns nothing. Reading `<` and `>` the wrong way round (thinking the dining line was the old one) is a common slip.",
        ),
        part(
            "2",
            "Is your partner's change a refactoring? Explain using the course's definition.",
            2,
            "No. A refactoring changes the structure and keeps the behaviour: the output must stay identical and `diff` must print nothing. Extracting `largest_expense` is a refactoring; making it use only filtered expenses changes behaviour, even if it is an improvement.",
            [
                "No, with the definition: structure changes, behaviour (output) stays identical, so `diff` must be empty",
                "Separates the extraction (refactoring) from the new filtering (a behaviour change)",
            ],
            "'Yes, because it improves the code' confuses better with unchanged. 'No, because it is wrong' misses the point: the change may well be right, it just is not a refactoring.",
        ),
        part(
            "3",
            "What do you do with the change?",
            2,
            "Keep the extraction but undo the filtering, so the refactoring step ends with an empty `diff`. Then raise the filtering with the team as its own change, and if agreed, make it in a separate commit whose message says the report's behaviour changes.",
            [
                "Undo the behaviour change inside the refactoring step until `diff` is empty",
                "Make the filtering a separate, agreed change with its own commit and message",
            ],
            "Keeping both in one commit 'because it is better' mixes a refactoring with a behaviour change, so nobody can review either properly. Throwing the idea away is also weak: it may be a real improvement, it just needs its own step.",
        ),
    ],
    explanation="The demo really does this: with `--category dining --min 20`, v0.1 to v0.4 print the largest expense of the whole file, which is a home expense. Whether that is a bug is a product question. The exam question is about discipline: slide 30 says the output must stay identical, so a refactoring step never carries a behaviour change, however good. Session 1's distinction between a bug fix, a feature and a refactoring is why they go in separate commits.",
    section=9,
    source_ref="S6 slide 30; S1 bugs/features/refactor; expense-tracker v0.1 run",
    origin="slides",
    verified_by="run",
)

open_q(
    "k_open_process",
    level="hard",
    skills=["read-code", "judgement"],
    stem="A teammate's function, run on the course's `expenses.csv`, prints `Total: 2852.91`.\n\n```python\nimport csv\n\n\ndef process(path):\n    data = []\n    f = open(path)\n    reader = csv.reader(f)\n    next(reader)\n    for row in reader:\n        if len(row) == 4:\n            data.append((row[0], row[1], row[2], float(row[3])))\n    f.close()\n    # total spent on dining\n    t = 0\n    for d in data:\n        if d[2] == \"transport\" and d[3] >= 15:\n            t += d[3]\n    print(\"Total: \" + str(round(t, 2)))\n```",
    parts=[
        part(
            "1",
            "In one sentence, what does this function really do?",
            1,
            "It reads the CSV at `path` (skipping the header and rows without four fields), adds up the transport expenses of 15 or more, and prints that total rounded to two decimals; it returns nothing.",
            ["Says it totals transport expenses of 15 or more (not dining) and prints the result"],
            "Answers that say 'it totals dining expenses' trusted the comment instead of the code, which is exactly the trap this question sets. 'It processes the file' repeats the name. Forgetting the minimum of 15 or that it prints rather than returns loses precision.",
        ),
        part(
            "2",
            "Name three problems a teammate would face.",
            3,
            "The comment says dining but the code counts transport, so a reader who trusts it is misled. It does several jobs (read, total, print), so the total cannot be checked without a file. And it prints instead of returning.",
            [
                "The comment contradicts the code (dining vs transport): the truth is only in the code",
                "Several jobs in one function (reading, computing, printing), so it is hard to test or change",
                "It prints and returns nothing, so it can only be looked at",
                "Tuple indexes, magic numbers or vague names (`d[3]`, 15, `process`, `data`, `t`) hide the meaning",
            ],
            "Weak answers list three naming complaints (`t`, `d`, `data`) as three problems; they count as one. Missing the contradicting comment is the most common gap, because most readers trust it. 'No error handling' may be true but is not what session 6 asks you to see.",
        ),
        part(
            "3",
            "Describe in words how you would restructure it, and which problem each change fixes.",
            3,
            "Split it: `read_expenses(path)` returns a list of `Expense`, `transport_total(expenses, minimum)` returns the number, and only the caller prints, so the total is testable with a plain list. Name 15, use `expense.amount`, ask which category was meant, then delete the comment.",
            [
                "Separates reading, computing and printing into functions with one job each",
                "The computing function returns the total and only the outer function prints",
                "Replaces tuple indexes with a dataclass and/or magic numbers with named constants",
                "Resolves the comment: find out which category is meant, then delete the comment",
            ],
            "Answers that only rename variables leave the structure untouched. 'Fix the comment to say transport' is half right: first find out which is intended, because the code might be the wrong one. Writing code instead of describing it ignores the instruction.",
        ),
    ],
    explanation="A harder Q7: 18 lines, several session 6 problems layered together, and a comment that lies. The careful reader's first move is to trust the code, not the comment (\"Truth can only be found in one place: the code\"), which part 1 checks. Parts 2 and 3 reward naming distinct problems with consequences and fixes that mirror the demo's v0.2 split.",
    section=5,
    source_ref="sample Q7 shape; S6 slides 11, 18, 20, 22",
    origin="teacher-variant",
    verified_by="run",
)

# ----- Added by the calibration pass: more Q5-shaped items, hints, ruff --fix -----

mcq(
    "k_q5jobs",
    level="hard",
    skills=["read-code", "judgement"],
    stem=md(
        """
        Read this function from a teammate's branch. `ruff check` and `mypy --strict` both pass on it.

        ```python
        import json

        MEMBER_DISCOUNT = 0.85


        def print_member_total(path: str) -> None:
            with open(path) as file:
                prices: list[float] = json.load(file)
            total = 0.0
            for price in prices:
                total += price * MEMBER_DISCOUNT
            # The till cannot take fractions of a cent
            print(f"Total for members: {total:.2f}")
        ```

        Which clean-code problem does it have?
        """
    ),
    right=(
        "It does several jobs: it reads a file, computes a total and prints it",
        "Right: you cannot test the total without a JSON file on disk and a way to capture the printed line. Describing it needs the word \"and\" twice.",
    ),
    wrong=[
        (
            "A magic number: the discount is a bare literal inside the calculation",
            "`MEMBER_DISCOUNT` is already a named constant at the top of the file. The line `total += price * MEMBER_DISCOUNT` has no magic number.",
        ),
        (
            "A comment that says what the code does, so the comment should be deleted",
            "The comment gives a reason the code cannot show (what the till accepts). Slide 14 keeps exactly that kind: comments are for why.",
        ),
        (
            "Duplicated logic: the price calculation is written twice and must be shared",
            "Nothing is repeated. The loop applies the discount once per price, in one place.",
        ),
    ],
    pos="a",
    explanation="Session 6's test: describe the function without the word \"and\". This one reads a file and computes a total and prints it. The visible things that tempt you are fine: the discount already has a name, the comment explains a reason, nothing is copied. What is left is the Single Responsibility Principle, with the usual price. To test the total you need a real file and captured output, and a new discount rule means touching the reading code. The demo's path is the same as for sample Q5: reading (`read_expenses`), computing (`total_by_category`) and printing (`format_report`) each get a function, and only the caller prints.",
    section=5,
    source_ref="sample Q5 shape; S6 slides 14, 16, 18",
    origin="teacher-variant",
    verified_by="run",
)

mcq(
    "k_q5name",
    level="exam",
    skills=["read-code", "read-tool-output", "judgement"],
    stem=md(
        """
        A teammate's budget check crashes. The end of `budget_check.py` (the `Expense` dataclass is defined above it), and the run:

        ```python
        def get_total(expenses: list[Expense]) -> None:
            total = 0.0
            for expense in expenses:
                total += expense.amount
            print(f"Total: {total:.2f}")


        budget = 100.0
        spent = get_total(dining)
        if spent > budget:
            print("Over budget")
        ```

        ```console
        $ uv run python budget_check.py
        Total: 118.95
        Traceback (most recent call last):
          File "budget_check.py", line 22, in <module>
            if spent > budget:
               ^^^^^^^^^^^^^^
        TypeError: '>' not supported between instances of 'NoneType' and 'float'
        ```

        Which clean-code problem sits behind the crash?
        """
    ),
    right=(
        "The name promises a value, but the function only prints the total and returns nothing",
        "Right: a function name says what it returns, and `get_total` reads as \"gives me the total\". The caller trusted the name and received `None`.",
    ),
    wrong=[
        (
            "A magic number: `100.0` should be a named constant so the comparison works",
            "`budget = 100.0` already has a name, and a better name would not turn `None` into a number. The crash is about the value `spent`.",
        ),
        (
            "Its comments say what the code does instead of why, and mislead the next reader",
            "The function has no comments. Nothing in the code or the traceback points at comments.",
        ),
        (
            "A tuple is used where a type is needed, so the caller cannot tell the fields apart",
            "No tuple appears. The data is a list of `Expense` objects, which is the course's own fix for tuples.",
        ),
    ],
    pos="d",
    explanation="Session 6's naming table asks a function name to say what it returns: `calculate_totals` became `total_by_category` in the demo. `get_total` borrows the look of a function that hands back a number, while the signature (`-> None`) and the last line (`print`) say it hands back nothing. The caller reads the name, assumes a number, and `spent` is `None`; `None > 100.0` is the `TypeError` in the traceback. The fix is to return the total and let the caller print it, which also repairs the mixed jobs. Naming is the first thing a reader meets, so it is the first thing to correct.",
    section=3,
    source_ref="S6 slides 15, 20; sample Q5 shape",
    origin="slides",
    verified_by="run",
)

mcq(
    "k_q5tuple",
    level="hard",
    skills=["read-code", "judgement"],
    stem=md(
        """
        This function totals one category. The tools are green. Every line has a comment, and the author says: "I need them, otherwise nobody can follow it."

        ```python
        def total_for(category: str, rows: list[tuple[str, str, str, float]]) -> float:
            total = 0.0
            for row in rows:
                # check the category
                if row[2] == category:
                    # add the amount
                    total += row[3]
            # give back the total
            return total
        ```

        Which problem, fixed at its root, removes the need for those comments?
        """
    ),
    right=(
        "A tuple stands in for a type: `row[2]` and `row[3]` mean nothing until a comment says so",
        "Right: session 6's \"a tuple is a missing type\". With `Expense`, `expense.category` and `expense.amount` explain themselves and the comments have nothing left to do.",
    ),
    wrong=[
        (
            "The comments say what the code does, so deleting them is all that is needed",
            "Deleting them leaves `row[2]` and `row[3]` unexplained. The comments are a symptom: they patch over a tuple nobody can read.",
        ),
        (
            "The function does several jobs, so each step needs a comment of its own",
            "It does one job: it totals one category. The comments follow lines, not jobs.",
        ),
        (
            "The name `total_for` says too little, and a longer name would replace the comments",
            "The name says what comes back (a total) and for what (a category). A longer name would not tell anyone what `row[3]` is.",
        ),
    ],
    pos="c",
    explanation="Two problems are visible here and one is the cause of the other. The comments restate the code, which slide 13 treats as a failure of naming. They exist because `row[2]` and `row[3]` carry no meaning: v0.1 used exactly these positions before commit `017f926` replaced the tuple with `@dataclass(frozen=True) class Expense`. After that commit the loop reads `if expense.category == category: total += expense.amount`, and none of the comments would be worth writing. Fix the tuple and the comments disappear; delete the comments and the reader is worse off than before.",
    section=7,
    source_ref="S6 slides 13, 21-22; expense-tracker 017f926",
    origin="history",
    verified_by="run",
)

mcq(
    "k_q5neg",
    level="hard",
    skills=["read-code", "compare"],
    stem=md(
        """
        Read this function. `ruff check` and `mypy --strict` pass.

        ```python
        def count_large_expenses(expenses: list[Expense]) -> int:
            count = 0
            # loop over the expenses
            for expense in expenses:
                if expense.amount > 25:
                    count += 1
                    print(f"Large: {expense.merchant}")
            return count
        ```

        Which of these problems does it **not** have?
        """
    ),
    right=(
        "A name that does not say what the function returns",
        "Right, it does not have this one: `count_large_expenses` returns a count of large expenses, and the signature says `-> int`.",
    ),
    wrong=[
        (
            "A magic number: the limit is written as a bare `25`",
            "It has this one. `25` has no name, so a reader cannot tell whether it is a euro limit or a policy.",
        ),
        (
            "A comment that repeats what the code already says",
            "It has this one. `# loop over the expenses` repeats the line below it and adds nothing.",
        ),
        (
            "Computation mixed with output",
            "It has this one. The function counts and also prints a line for every large expense, so callers get output they did not ask for.",
        ),
    ],
    pos="a",
    explanation="A negative question is the same judgement run four times, so check each option against the code. `25` is a magic number (slide 16: name it). `# loop over the expenses` says what, not why (slides 13-14). The `print` inside the loop mixes computation with output (slide 20). The name is the one thing done right: it says what comes back, and the type hint agrees. Reading the options as a checklist, and ticking only what you can point at, is the safe method when two or three of them are true.",
    section=5,
    source_ref="S6 slides 13-14, 16, 20; sample Q5 shape",
    origin="slides",
    verified_by="run",
)

mcq(
    "k_hint_contract",
    level="exam",
    skills=["read-tool-output", "judgement"],
    stem=md(
        """
        Four branches each define `summarise` for the same job: take the expenses, return the totals per category, optionally including refunds. `mypy --strict` rejects two of them:

        ```text
        branch_c.py:1: error: Missing type arguments for generic type "list"  [type-arg]
        branch_c.py:1: error: Missing type arguments for generic type "dict"  [type-arg]
        branch_a.py:1: error: Function is missing a type annotation  [no-untyped-def]
        Found 3 errors in 2 files (checked 4 source files)
        ```

        and accepts the other two. A teammate who must call `summarise` without opening its body asks you which signature to merge. Which one?
        """
    ),
    right=(
        "`def summarise(expenses: list[Expense], include_refunds: bool = False) -> dict[str, float]:`",
        "Right: it says what goes in and what comes back, and mypy can check every call against it. This is slide 26's contract.",
    ),
    wrong=[
        (
            "`def summarise(expenses, include_refunds=False):  # takes Expense objects, returns totals`",
            "The contract is only a comment, which mypy cannot check and nobody keeps up to date. This is the branch mypy rejects as `no-untyped-def`.",
        ),
        (
            "`def summarise(expenses: Any, include_refunds: Any = False) -> Any:  # accepts anything`",
            "mypy accepts it, but `Any` switches the checking off: any call passes. Passing the tool is not the same as having a contract.",
        ),
        (
            "`def summarise(expenses: list, include_refunds: bool = False) -> dict:  # list in, dict out`",
            "A bare `list` and `dict` say nothing about what they hold, so mypy under `--strict` rejects them with `type-arg`.",
        ),
    ],
    pos="a",
    explanation="Slide 26: type hints are contracts. They say what goes in and what comes out, and they are read by the next person and by mypy. Elimination does most of the work. The unannotated branch has no contract, only a comment. The bare `list` and `dict` branch is rejected because the container's contents are missing. Of the two that mypy accepts, `Any` is a hint in form only: it promises nothing, so mypy has nothing to check. Only `list[Expense]` and `dict[str, float]` let a caller and the checker know what to pass and what to expect. Real run: mypy 2.4.0 with `--strict` gave exactly these three errors.",
    section=8,
    source_ref="S6 slide 26; S7 slide 9 (--strict)",
    origin="slides",
    verified_by="run",
)

mcq(
    "k_fix_ci",
    level="exam",
    skills=["read-tool-output", "judgement"],
    stem=md(
        """
        Your group's CI step `uv run ruff check .` turns red:

        ```text
        I001 [*] Import block is un-sorted or un-formatted
         --> src/expense_tracker/budget.py:1:1
        F401 [*] `os` imported but unused
         --> src/expense_tracker/budget.py:2:8
        Found 2 errors.
        [*] 2 fixable with the `--fix` option.
        ```

        (Output trimmed: the code excerpts are not shown.) A teammate proposes: "Change the CI step to `ruff check --fix .` and the pipeline repairs this itself." What do you answer?
        """
    ),
    right=(
        "No: CI only reports. Run `--fix` on your laptop, read `git diff`, re-run the checks and commit",
        "Right: CI is the referee, not the judge. On your machine the change is yours to read before it enters the history.",
    ),
    wrong=[
        (
            "Yes: `[*]` marks a safe fix, so CI can apply it and the code is repaired for everyone",
            "A fix applied on the runner is thrown away with the runner's checkout. The pushed code stays broken, and nobody read the change.",
        ),
        (
            "Yes, but first add `# noqa` to both lines so that the fix cannot touch the code",
            "A `# noqa` silences the findings; with nothing reported, there is nothing left to fix. It hides the problem it was meant to cure.",
        ),
        (
            "No: never use `--fix`, because a tool must not edit code, so delete each line by hand",
            "Using `--fix` on your own machine is fine. The care is in reading the diff afterwards, since a fix can remove something that was needed.",
        ),
    ],
    pos="b",
    explanation="Session 3 sets the roles: the four checks in CI report, and the person fixes. `ruff check --fix` is a tool for your laptop: it rewrites files (here it sorts the imports and removes `os`), so you read `git diff`, ask whether each change is what you meant, run the checks again and commit what you have understood. The session 6 method is the same for every finding: read the code, read the message, fix the cause. A fix that CI applies to its own copy changes nothing in the repository, and an auto-fix nobody reads is how a needed import disappears. Real run: on the laptop, `ruff check --fix` printed `Found 2 errors (2 fixed, 0 remaining)` and `git diff` showed the single removed `import os` line.",
    section=8,
    source_ref="S3 slides 3, 14; S6 slide 27",
    origin="slides",
    verified_by="run",
)

# ---------------------------------------------------------------------------
# Assign stable ids, resolve section checks
# ---------------------------------------------------------------------------

# Questions built on the shape of a teacher's sample question point to that original
# (the sample-paper module keeps the nine originals as sample-paper-q01..q09).
VARIANT_OF = {
    "k_q5var": "sample-paper-q05",
    "k_open_q7": "sample-paper-q07",
    "k_open_process": "sample-paper-q07",
    "k_open_compare": "sample-paper-q08",
    "k_open_ruff": "sample-paper-q09",
    "k_q5jobs": "sample-paper-q05",
}

# Ids are fixed once published: q01..q45 keep their slots (a replaced question takes over
# the id of the one it replaced), and new questions continue the numbering from q46.
ID_ORDER = [
    "k_dare", "k_econ", "k_open_dare",  # q01-q03
    "k_comment_rule", "k_rename", "k_legit", "k_bank_keep", "s_comments",  # q04-q08 (q07 replaced)
    "k_fname", "k_bool", "k_module",  # q09-q11
    "k_forty", "k_vat",  # q12-q13
    "k_q5var", "k_and", "s_jobs", "k_open_q7", "k_open_process",  # q14-q18
    "k_guard", "k_guard_diff", "k_testprint", "k_noreturn", "k_sim102", "k_open_output",  # q19-q24
    "k_e3", "k_frozen", "k_typo", "k_concept", "k_open_frozen",  # q25-q29
    "k_contract", "k_runtime", "k_checkformat", "k_format_f401", "k_f841",  # q30-q34
    "k_fmtcheck", "k_ten", "k_arbiter", "k_open_ruff",  # q35-q38 (q35 replaced)
    "k_diff_empty", "k_diff_width", "k_commitmsg", "s_commits",  # q39-q42
    "k_ammount", "k_open_compare", "k_open_pair",  # q43-q45 (q43 replaced)
    "k_reasons", "k_vars",  # q46-q47 (added)
    "k_q5jobs", "k_q5name", "k_q5tuple", "k_q5neg",  # q48-q51 (calibration pass: Q5 shape)
    "k_hint_contract", "k_fix_ci",  # q52-q53 (calibration pass: hints as contracts, ruff --fix)
]
assert len(ID_ORDER) == len(set(ID_ORDER)) == len(QUESTIONS)
assert set(ID_ORDER) == {q["key"] for q in QUESTIONS}
key_to_id: dict[str, str] = {k: f"{MID}-q{n:02d}" for n, k in enumerate(ID_ORDER, start=1)}
for q in QUESTIONS:
    key = q.pop("key")
    q["id"] = key_to_id[key]
    if q["origin"] == "teacher-variant":
        q["variant_of"] = VARIANT_OF[key]
QUESTIONS.sort(key=lambda q: q["id"])
# put id first for readability
QUESTIONS[:] = [{"id": q["id"], **{k: v for k, v in q.items() if k != "id"}} for q in QUESTIONS]

for s in SECTIONS:
    s["check"] = [key_to_id[k] for k in s["check"]]

MODULE: dict[str, Any] = {
    "id": MID,
    "order": 5,
    "module": "M2",
    "title": "Clean code: naming and responsibility",
    "sessions": [6],
    "predicted": False,
    "sources": [
        "slides-session-6",
        "expense-tracker v0.1..v0.2 (5e9466d, f3bb801, 9d6c607, 017f926, 04d699f)",
        "moodle/midterm-sample-questions.md (Q5, Q7)",
        "labs/07-refactor.md",
        "partial-rubric (naming and clean code)",
    ],
    "summary_md": md(
        """
        Session 6 is about what happens after code runs. The same logic can be cheap or expensive to change, and the course treats that as an economic argument: code is read far more often than it is written, so the cost of maintaining it is the cost of understanding it. You learn to rename instead of comment and keep comments for why, to name magic numbers, to give each function one job and keep computation apart from output, to replace a tuple with a frozen dataclass, and to treat type hints as contracts and ruff as the arbiter. The expense-tracker reaches v0.2 in five small commits, and the dining report prints exactly the same text after each one.
        """
    ),
    "exam_focus_md": md(
        """
        - Read a short function (sample Q7's shape) and say what it does, two or three problems a teammate would face, and how you would change it, in words.
        - Name the clean-code problem a description shows (sample Q5): several jobs in one function, a name that says nothing, a magic number, a tuple indexed by position, a comment that restates or contradicts the code.
        - Pick the best name for a function, a boolean or a module, or the one comment worth keeping.
        - Read ruff output (`E501`, `F401`, `E722`, `F841`) and say what it means and what you do; `# noqa` or loosening the rules is the careless answer.
        - Read a traceback or mypy message involving a dataclass or a hinted call, and say what `frozen=True` or the contract bought you.
        - Judge a refactoring from `diff before.txt after.txt`: empty means safe for that input; a changed line means it was not a refactoring.
        - Match a diff to one of the five commits from v0.1 to v0.2, or judge two commit messages for the same change.
        """
    ),
    "sections": SECTIONS,
    "terms": [
        {"term": t, "definition_md": d, "section_ref": sec(s)} for t, d, s in TERMS
    ],
    "traps": TRAPS,
    "flashcards": [
        {
            "id": f"{MID}-f{n:02d}",
            "front_md": front,
            "back_md": back,
            "kind": kind,
            "section_ref": sec(s),
        }
        for n, (front, back, kind, s) in enumerate(CARDS, start=1)
    ],
    "questions": QUESTIONS,
}


def report() -> None:
    types = Counter(q["type"] for q in QUESTIONS)
    levels = Counter(q["level"] for q in QUESTIONS)
    pos = Counter(
        "abcd"[[o["correct"] for o in q["options"]].index(True)]
        for q in QUESTIONS
        if q["type"] == "mcq"
    )
    print(f"sections {len(SECTIONS)}, terms {len(TERMS)}, traps {len(TRAPS)}, cards {len(CARDS)}")
    print(f"questions {len(QUESTIONS)}: {dict(types)}")
    print(f"levels: {dict(levels)}")
    print(f"mcq correct positions: {dict(sorted(pos.items()))}")


if __name__ == "__main__":
    with OUT.open("w", encoding="utf-8") as f:
        json.dump(MODULE, f, ensure_ascii=False, indent=1)
        f.write("\n")
    report()
    print(f"wrote {OUT}")
