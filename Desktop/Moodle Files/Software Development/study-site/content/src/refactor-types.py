"""Generate content/refactor-types.json (module M2, session 7: refactoring and mypy).

Every tool output below was produced by running it with the course toolchain
(Python 3.13, mypy 2.4.0, ruff 0.16.9, pytest, uv 0.12) in the work folder
scratchpad/work/refactor-types/ (see run_all.sh there). Paths were shortened to
the project-relative form a student sees.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MID = "refactor-types"
OUT = Path(__file__).resolve().parent.parent / f"{MID}.json"


def q(n: int) -> str:
    return f"{MID}-q{n:02d}"


def s(n: int) -> str:
    return f"{MID}-s{n}"


def code(lang: str, body: str) -> str:
    return f"```{lang}\n{body.strip(chr(10))}\n```"


def opt(text: str, why: str, correct: bool = False) -> dict[str, Any]:
    return {"text_md": text, "correct": correct, "why_md": why}


# ---------------------------------------------------------------------------
# Real artefacts (copied from runs; see the work folder)
# ---------------------------------------------------------------------------

V01_PLAIN = """
$ uv run --with mypy mypy src
Success: no issues found in 3 source files
"""

V01_STRICT = """
$ uv run --with mypy mypy --strict src
src/expense_tracker/report.py:5: error: Function is missing a type annotation  [no-untyped-def]
src/expense_tracker/report.py:22: error: Function is missing a type annotation  [no-untyped-def]
src/expense_tracker/report.py:44: error: Call to untyped function "calculate_totals" in typed context  [no-untyped-call]
src/expense_tracker/cli.py:23: error: Call to untyped function "run" in typed context  [no-untyped-call]
Found 4 errors in 2 files (checked 3 source files)
"""

V01_SIGNATURES = """
src/expense_tracker/report.py:16: error: Incompatible types in assignment (expression has type "float", target has type "int")  [assignment]
src/expense_tracker/report.py:21: error: Incompatible return value type (got "list[tuple[str, int]]", expected "list[tuple[str, float]]")  [return-value]
src/expense_tracker/report.py:50: error: Incompatible types in assignment (expression has type "float", variable has type "int")  [assignment]
Found 3 errors in 1 file (checked 3 source files)
"""

LARGEST_CODE = """
def largest_expense(expenses: list[Expense]) -> Expense | None:
    largest = None
    for expense in expenses:
        if largest is None or expense.amount > largest.amount:
            largest = expense
    return largest


expenses: list[Expense] = []
largest = largest_expense(expenses)
print(largest.amount)
"""

LARGEST_RUN = """
$ uv run ruff check largest.py
All checks passed!
$ uv run mypy --strict largest.py
largest.py:22: error: Item "None" of "Expense | None" has no attribute "amount"  [union-attr]
Found 1 error in 1 file (checked 1 source file)
$ uv run python largest.py
Traceback (most recent call last):
  File "largest.py", line 22, in <module>
    print(largest.amount)
          ^^^^^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'amount'
"""

INVOICE_TYPED_CODE = """
def invoice_total(
    lines: list[tuple[str, float, int]], tax_rate: float, discount_rate: float
) -> float:
    total = 0
    for line in lines:
        total += line[1] * line[2]
    if discount_rate > 0:
        total = total - (total * discount_rate)
    if tax_rate > 0:
        total = total + (total * tax_rate)
    return total


def average(values: list[float]) -> float:
    total = 0
    for value in values:
        total += value
    return total / len(values)
"""

INVOICE_TYPED_RUN = """
invoice.py:6: error: Incompatible types in assignment (expression has type "float", variable has type "int")  [assignment]
invoice.py:8: error: Incompatible types in assignment (expression has type "float", variable has type "int")  [assignment]
invoice.py:10: error: Incompatible types in assignment (expression has type "float", variable has type "int")  [assignment]
invoice.py:17: error: Incompatible types in assignment (expression has type "float", variable has type "int")  [assignment]
Found 4 errors in 1 file (checked 1 source file)
"""

CI_RUN = """
$ uv run mypy src
Success: no issues found in 3 source files
$ uv run mypy src tests
tests/test_duplicates.py:7: error: Function is missing a return type annotation  [no-untyped-def]
tests/test_duplicates.py:7: note: Use "-> None" if function does not return a value
tests/test_duplicates.py:25: error: Function is missing a return type annotation  [no-untyped-def]
tests/test_duplicates.py:25: note: Use "-> None" if function does not return a value
Found 2 errors in 1 file (checked 6 source files)
"""

FIXTURE_RUN = """
$ uv run mypy src
Success: no issues found in 3 source files
$ uv run mypy src tests
tests/test_report.py:21: error: Function is missing a type annotation for one or more parameters  [no-untyped-def]
Found 1 error in 1 file (checked 6 source files)
"""

CI_TYPES_ONLY = """
$ uv run mypy src tests
tests/test_duplicates.py:7: error: Function is missing a return type annotation  [no-untyped-def]
tests/test_duplicates.py:7: note: Use "-> None" if function does not return a value
tests/test_duplicates.py:25: error: Function is missing a return type annotation  [no-untyped-def]
tests/test_duplicates.py:25: note: Use "-> None" if function does not return a value
Found 2 errors in 1 file (checked 6 source files)
"""

INVOICE_MAIN = """
from code import calc
from utils import x

print(calc([("pencil",10,5),("book",50,2)],0.21,0.1))
print(x([10,20,30]))
"""

INVOICE_CODE = """
def calc(c, i, d):
    t=0
    for p in c:
        t+=p[1]*p[2]
    if d>0:
        t=t-(t*d)
    if i>0:
        t=t+(t*i)
    return t
"""

INVOICE_UTILS = """
def x(l):
    s=0
    for i in l:
        s+=i
    return s/len(l)
"""

REFUNDS_CODE = """
from dataclasses import dataclass


@dataclass(frozen=True)
class Expense:
    date: str
    merchant: str
    category: str
    amount: float


def to_cents(euros):
    return round(euros * 100)


def refund_total(expenses: list[Expense]) -> float:
    total = 0
    for expense in expenses:
        if expense.amount < 0:
            total += expense.amount
    return total


def refund_cents(expenses: list[Expense]) -> int:
    return to_cents(refund_total(expenses))


def first_refund(expenses: list[Expense]) -> Expense | None:
    for expense in expenses:
        if expense.amount < 0:
            return expense
    return None


def refund_merchant(expenses: list[Expense]) -> str:
    return first_refund(expenses).merchant
"""

REFUNDS_RUN = """
$ uv run mypy --strict src
src/tracker/refunds.py:12: error: Function is missing a type annotation  [no-untyped-def]
src/tracker/refunds.py:20: error: Incompatible types in assignment (expression has type "float", variable has type "int")  [assignment]
src/tracker/refunds.py:25: error: Returning Any from function declared to return "int"  [no-any-return]
src/tracker/refunds.py:25: error: Call to untyped function "to_cents" in typed context  [no-untyped-call]
src/tracker/refunds.py:36: error: Item "None" of "Expense | None" has no attribute "merchant"  [union-attr]
Found 5 errors in 1 file (checked 1 source file)
"""

LONGLOG_CODE = """
from dataclasses import dataclass


@dataclass(frozen=True)
class Expense:
    date: str
    merchant: str
    category: str
    amount: float


def parse_amount(text):
    return float(text.replace(",", "."))


def to_expense(row: list[str]) -> Expense:
    return Expense(row[0], row[1], row[2], parse_amount(row[3]))


def budget_left(budget: str, spent: float) -> float:
    return parse_amount(budget) - spent


def over_budget(budget: str, expenses: list[Expense]) -> bool:
    spent = 0
    for expense in expenses:
        spent += expense.amount
    return spent > parse_amount(budget)


def find_by_merchant(expenses: list[Expense], merchant: str) -> Expense | None:
    for expense in expenses:
        if expense.merchant == merchant:
            return expense
    return None


def last_visit(expenses: list[Expense], merchant: str) -> str:
    return find_by_merchant(expenses, merchant).date
"""

LONGLOG_RUN = """
$ uv run mypy --strict src
src/tracker/budget.py:12: error: Function is missing a type annotation  [no-untyped-def]
src/tracker/budget.py:17: error: Call to untyped function "parse_amount" in typed context  [no-untyped-call]
src/tracker/budget.py:21: error: Returning Any from function declared to return "float"  [no-any-return]
src/tracker/budget.py:21: error: Call to untyped function "parse_amount" in typed context  [no-untyped-call]
src/tracker/budget.py:27: error: Incompatible types in assignment (expression has type "float", variable has type "int")  [assignment]
src/tracker/budget.py:28: error: Returning Any from function declared to return "bool"  [no-any-return]
src/tracker/budget.py:28: error: Call to untyped function "parse_amount" in typed context  [no-untyped-call]
src/tracker/budget.py:39: error: Item "None" of "Expense | None" has no attribute "date"  [union-attr]
Found 8 errors in 1 file (checked 1 source file)
"""

LONGLOG_AFTER = """
$ uv run mypy --strict src
src/tracker/budget.py:27: error: Incompatible types in assignment (expression has type "float", variable has type "int")  [assignment]
src/tracker/budget.py:39: error: Item "None" of "Expense | None" has no attribute "date"  [union-attr]
Found 2 errors in 1 file (checked 1 source file)
"""

Q9_CODE = """
import json

from tracker.expense import Expense


def load_budgets(path: str) -> dict[str, float]:
    with open(path) as handle:
        return json.load(handle)


def spent_in(expenses: list[Expense], category: str) -> float:
    spent = 0
    for expense in expenses:
        if expense.category == category:
            spent += expense.amount
    return spent


def biggest_category(totals: dict[str, float]) -> str | None:
    if not totals:
        return None
    return max(totals, key=lambda name: totals[name])


def headline(totals: dict[str, float]) -> str:
    return "Most spent on " + biggest_category(totals).upper()


def warn_if_over(budgets, category: str, spent: float) -> str:
    if spent > budgets[category]:
        return f"{category}: over budget"
    return f"{category}: fine"
"""

Q9_RUN = """
src/tracker/budgets.py:8: error: Returning Any from function declared to return "dict[str, float]"  [no-any-return]
src/tracker/budgets.py:15: error: Incompatible types in assignment (expression has type "float", variable has type "int")  [assignment]
src/tracker/budgets.py:26: error: Item "None" of "str | None" has no attribute "upper"  [union-attr]
src/tracker/budgets.py:29: error: Function is missing a type annotation for one or more parameters  [no-untyped-def]
Found 4 errors in 1 file (checked 3 source files)
"""

LABELS_CODE = """
from expense import Expense


def category_of(expenses: list[Expense], merchant: str) -> str | None:
    for expense in expenses:
        if expense.merchant == merchant:
            return expense.category
    return None


def label_for(expenses: list[Expense], merchant: str) -> str:
    return merchant + " [" + category_of(expenses, merchant).upper() + "]"
"""

LABELS_RUN = """
labels.py:12: error: Item "None" of "str | None" has no attribute "upper"  [union-attr]
"""

PR_DIFF = """
diff --git a/src/tracker/labels.py b/src/tracker/labels.py
index c9aa76d..72289e4 100644
--- a/src/tracker/labels.py
+++ b/src/tracker/labels.py
@@ -1,7 +1,9 @@
+from typing import Any
+
 from tracker.expense import Expense


-def category_of(expenses: list[Expense], merchant: str) -> str | None:
+def category_of(expenses: list[Expense], merchant: str) -> Any:
     for expense in expenses:
         if expense.merchant == merchant:
             return expense.category
@@ -22,4 +24,4 @@ def largest_expense(expenses: list[Expense]) -> Expense | None:

 def largest_line(expenses: list[Expense]) -> str:
     largest = largest_expense(expenses)
-    return f"Largest: {largest.merchant} {largest.amount:.2f}"
+    return f"Largest: {largest.merchant} {largest.amount:.2f}"  # type: ignore
"""

PR_FILE = """
from tracker.expense import Expense


def category_of(expenses: list[Expense], merchant: str) -> str | None:
    for expense in expenses:
        if expense.merchant == merchant:
            return expense.category
    return None


def label_for(expenses: list[Expense], merchant: str) -> str:
    return merchant + " [" + category_of(expenses, merchant).upper() + "]"


def largest_expense(expenses: list[Expense]) -> Expense | None:
    largest = None
    for expense in expenses:
        if largest is None or expense.amount > largest.amount:
            largest = expense
    return largest


def largest_line(expenses: list[Expense]) -> str:
    largest = largest_expense(expenses)
    return f"Largest: {largest.merchant} {largest.amount:.2f}"
"""

PR_BEFORE = """
$ uv run mypy --strict src
src/tracker/labels.py:12: error: Item "None" of "str | None" has no attribute "upper"  [union-attr]
src/tracker/labels.py:25: error: Item "None" of "Expense | None" has no attribute "merchant"  [union-attr]
src/tracker/labels.py:25: error: Item "None" of "Expense | None" has no attribute "amount"  [union-attr]
Found 3 errors in 1 file (checked 3 source files)
"""

PR_AFTER = """
$ uv run mypy --strict src
src/tracker/labels.py:14: error: Returning Any from function declared to return "str"  [no-any-return]
Found 1 error in 1 file (checked 3 source files)
"""

def _context_spaces(diff: str) -> str:
    """Give empty lines inside a unified diff their leading context space back."""
    body = diff.strip("\n").split("\n")
    return "\n" + "\n".join(line if line else " " for line in body) + "\n"


PR_DIFF = _context_spaces(PR_DIFF)

IS_WANTED = """
def is_wanted(expense: Expense, category: str, minimum: float) -> bool:
    matches_category = category == "" or expense.category == category
    return matches_category and expense.amount >= minimum
"""

PROJ3_DIFF = """
diff --git a/src/expense_tracker/report.py b/src/expense_tracker/report.py
index 58aaec4..d5692c2 100644
--- a/src/expense_tracker/report.py
+++ b/src/expense_tracker/report.py
@@ -38,16 +38,18 @@ def read_expenses(path: str) -> list[Expense]:
     return expenses


+def is_wanted(expense: Expense, category: str, minimum: float) -> bool:
+    matches_category = category == "" or expense.category == category
+    return matches_category and expense.amount >= minimum
+
+
 def total_by_category(
     expenses: list[Expense], category: str, minimum: float
 ) -> list[tuple[str, float]]:
     totals: dict[str, float] = {}
     for expense in expenses:
-        if category != "" and expense.category != category:
-            continue
-        if expense.amount < minimum:
-            continue
-        totals[expense.category] = totals.get(expense.category, 0.0) + expense.amount
+        if is_wanted(expense, category, minimum):
+            totals[expense.category] = totals.get(expense.category, 0.0) + expense.amount
     ordered = list(totals.items())
     ordered.sort(key=lambda pair: -pair[1])
     return ordered
"""

PROJ3_DIFF = _context_spaces(PROJ3_DIFF)

# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------

S1_BODY = (
    """Session 7 opens by giving a name to what you watched in session 6, when the expense-tracker went from `v0.1` to `v0.2` in five commits. The name is **refactoring**, and the slide defines it in one line: **change the structure, keep the behaviour.** The test that follows is just as short: **if the output changes, it was not a refactoring.**

Behaviour is what the program does from the outside: what it prints, what it writes to a file, its exit code, and the results its tests already check. Structure is everything a user cannot see: names, how the code is split into functions, which function does the printing, which type carries the data. A refactoring makes the code cheaper to read and change, and leaves every observable result as it was.

The moves are **small on purpose**. You make one, run the program, compare, and only then make the next. If the output changes, you know which move did it, and you undo that one step. The session 6 pairs exercise turned this into commands:

"""
    + code(
        "bash",
        """
uv run expenses report --category dining --min 20 > before.txt
# ... rename three things, extract one function ...
uv run expenses report --category dining --min 20 > after.txt
diff before.txt after.txt   # nothing printed = you're safe
""",
    )
    + """

Tests give the same evidence in a stronger form. In sample Q2 the refactoring is the change made "with every test still passing unchanged": if you had to edit a test to make it pass, the behaviour that test pins down has changed.

What is **not** a refactoring, even if the code looks tidier afterwards:

- a new feature, such as a `--month` option: new behaviour;
- a bug fix, such as counting the last row that used to be skipped: different output, on purpose;
- a different storage format, CSV to JSON: the program reads and writes something else;
- a rename that also changed a printed label: the output moved.

Features and fixes are good work. They are different work, and they belong in their own commits with honest messages, so a reviewer knows which commits should change the output and which should not.

Keep one limit in mind. A `diff` that prints nothing proves the behaviour is the same **for the input you ran**. An empty file, or a file with only refunds, may still behave differently, which is why the lab also asks you to name edge cases."""
)

S2_BODY = (
    """The five session 6 commits each did one thing: constants, better names, computation apart from output, a type for complex data, hints and ruff. Session 7 turns them into a table of named **refactoring moves**. Learn each move together with the example you saw, because the exam can name a move and show code, or show code and ask which move it needs.

| Move | You saw it as | In the history |
|---|---|---|
| Extract constant | magic numbers → `STANDARD_VAT_RATE` (the slide's name); in the demo, `40` → `RULE_WIDTH` | `5e9466d` |
| Rename (replace comment with a name) | `calculate_totals` → `total_by_category` | `f3bb801` |
| Separate I/O from logic | `run()` split into read, compute, format | `9d6c607` |
| Introduce a parameter object / type | tuple → `Expense` | `017f926` |
| Extract function | `largest_expense` out of `run()` | `9d6c607` |
| Decompose conditional | a nested `if` → guard clauses | session 6, slide 19 |

What each move fixes:

- **Extract constant.** A bare number gets a name and a single place to change it: `print("-" * 40)` becomes `print("-" * RULE_WIDTH)`. In `5e9466d` the comment `# skip rows that do not have all four fields` went at the same time, because `if len(row) == FIELDS_PER_ROW:` now says it.
- **Rename.** A name that says what it holds or returns replaces a comment: `x, y, z` became `expenses, category, minimum`. "A name that needs a comment is not finished."
- **Separate I/O from logic.** `read_expenses` touches the file, `total_by_category` and `format_report` only compute and return, and one place prints. A function that returns can be tested; a function that prints can only be looked at.
- **Introduce a type.** `e[3]` becomes `expense.amount`. "A tuple is a missing type."
- **Extract function.** A block inside a long function becomes a function whose name says what it returns. `run()` in `v0.1` did five jobs; the question to ask is "can I describe it without the word *and*?"
- **Decompose conditional.** A tangle of conditions becomes guard clauses or a condition with a name (next section).

The last session 6 commit, `04d699f` ("Add type hints and make the code ruff clean"), is the bridge to the rest of session 7: hints such as `-> Expense | None` are what a type checker reads."""
)

S3_BODY = (
    """The before/after slide shows decompose conditional in its smallest form. Before, the rule "which expenses count" is buried in two nested `if`s that index a tuple:

"""
    + code(
        "python",
        """
if e[2] == category:
    if e[3] >= minimum:
        totals[e[2]] += e[3]
""",
    )
    + """

After, the rule has a name and a function of its own:

"""
    + code("python", IS_WANTED)
    + """

Read it the way you read any function, with one sentence for what it returns. `is_wanted` answers yes or no for one expense: yes when its category matches (an empty `category` means "no filter", which is what the CLI passes when you give no `--category`) **and** its amount is at least the minimum. Note the `>=`: an amount equal to the minimum is kept. The `v0.4` tests pin that down in `test_minimum_keeps_amounts_equal_to_it`.

The slide's last line is the reason for the move: **"A condition with a name is a condition you can test."** Buried inside `total_by_category`, the rule can only be tested indirectly: build a list, compute the totals, and work out from the totals whether one expense was counted. As `is_wanted` it is one call, with one expense, and one `True` or `False` to check. Its name reads like a yes/no question, which is the session 6 naming rule for booleans (`is_duplicate`, not `flag`).

Two related ideas sit next to it:

- **Guard clauses** (session 6): deal with the exceptions first and get out with `continue` or `return`, so the main path is not buried in a pyramid of `if`s.
- **Names for parts of a condition**: `matches_category` exists only to explain the left half of the `and`.

It is still a refactoring, so the outside behaviour must not move. If you change the demo's `total_by_category` at `v0.4` to call `is_wanted`, the 24 existing tests still pass without a single edit (we ran it). That is your evidence. What you gain is a smaller piece you can test on its own on Friday."""
)

S4_BODY = (
    """You already run two checkers on every push. **ruff** is the linter: it reads how the code is written and flags style and simple mistakes, such as `F401` (`os` imported but unused) or `E501` (line too long). **mypy** is the type checker: it follows the types through the code and checks that every use of a value fits what that value can be. The session 7 slide shows a mistake only the second one can see:

"""
    + code("python", LARGEST_CODE)
    + """

`largest_expense` returns `Expense | None`: an expense, or `None` when the list is empty. The last line assumes it is always an expense. We ran the three tools on this file (it starts with the frozen `Expense` dataclass, so the `print` is line 22):

"""
    + code("console", LARGEST_RUN)
    + """

ruff is happy: the line is well formatted and every name exists. mypy reads the return type, knows a `None` can arrive, and reports it on line 22 before the program has ever run. Python only finds out at run time, on the day the list is empty. The slide says it in one line: "Empty list → None → crash at 2 a.m. The checker finds it before anyone runs the program."

This is why the hints added in `04d699f` matter. `-> Expense | None` is a contract: it tells the next reader, and mypy, that "no result" is a normal answer. mypy then makes every caller deal with it, for example the way `format_report` does with `if largest is not None:`.

Tests do not replace this. A test checks the inputs somebody wrote down; if nobody wrote a test with an empty list, the tests stay green. mypy reasons about every value the type allows, including the one nobody thought of. The three tools in CI answer three different questions:

- ruff: is it written cleanly?
- mypy: do the types fit everywhere?
- pytest: does it give the right answer for these cases?

None of them answers the others' question, which is why CI runs all three."""
)

S5_BODY = (
    """A mypy error has three parts, and the slide numbers them on this example (printed over two lines on the slide):

"""
    + code(
        "text",
        """
src/app/report.py:12: error:
  Function is missing a return type annotation  [no-untyped-def]
""",
    )
    + """

1. **File and line**: where. `src/app/report.py`, line 12.
2. **Message**: what is wrong, in plain words.
3. **`[code]`**: what to search for. `no-untyped-def` names the check, so it is what you look up in the mypy documentation or in the lab's troubleshooting table when the message alone does not help.

The last line of a run, such as `Found 4 errors in 1 file (checked 1 source file)`, is the count. Then comes the routine from the slide: **read the first error, fix it, run again. Later errors are often the same one repeating.** One cause can be reported many times, once for every place it touches. Here is the invoice code from lab 07 (section 8 shows the original `calc` and `x`), renamed and given hints, before any other cleaning:

"""
    + code("python", INVOICE_TYPED_CODE)
    + "\n\n"
    + code("text", INVOICE_TYPED_RUN)
    + """

Four errors, two causes. Each function starts with `total = 0`, so mypy decides `total` holds an `int`, and every later line that stores a float in it is reported. The fix is `total = 0.0` in two places, and all four errors disappear (we ran it: `Success`). Notice that the reported lines (6, 8, 10 and 17) are not the lines you change (4 and 15). The file and line say where mypy *noticed* the problem; the cause can sit a few lines above.

Three habits follow:

- Start at the top, not at random. The first error is often the cause of several after it.
- Run again after each fix. The count usually drops by more than one.
- A message you do not understand is a message to search by its `[code]`, never one to silence."""
)

S6_BODY = (
    """mypy without options is polite: **it does not look inside a function with no signature.** mypy treats a function with no hints at all as unfinished and skips its body. `--strict` turns that politeness off and adds stricter checks. Session 7 ran it live on the demo at `v0.1`, where `report.py` had no hints at all. We repeated the slide's commands with the course's mypy 2.4.0:

"""
    + code("console", V01_PLAIN + V01_STRICT)
    + """

Four errors, **all one kind**: missing annotations. Two functions in `report.py` have no signature (`calculate_totals` on line 5, `run` on line 22), and the two calls to them are reported as well. Plain `mypy` said `Success` because it never looked inside those functions.

The `--with mypy` is there because at `v0.1` mypy is not yet one of the project's dependencies. It arrives in `88b83c3`, so the slide borrows it for this one run. In your group repo, where `mypy` is in the dev dependencies, the command is plain `uv run mypy --strict src`.

Now add the signatures, so mypy can look inside, and **a second kind appears** (three `note:` lines trimmed):

"""
    + code("text", V01_SIGNATURES)
    + """

These problems were in the code all along. `d[e[2]] = 0` and `grand = 0` start a total as an `int` and then add float amounts to it. The signatures did not create the errors; they let mypy see them. Changing both zeros to `0.0` clears all three (we ran it). (Precisely: `--strict` already reads the bodies, but with no signature every parameter is `Any`, and `Any` agrees with everything. The signatures give mypy real types to compare.)

The slide sorts strict errors into **three kinds**:

| Kind | Meaning | Fix |
|---|---|---|
| Missing annotation | "what type is this?" | write the hint |
| Types disagree | "`int` here, `float` there" | make them agree (`0.0`) |
| None not handled | "this can be missing" | check it, or change the type |

A fourth kind comes from the teacher's official answer to sample Q9, not from the slide: **Any leaks in** ("I gave up on this value"). It is the kind of `Returning Any from function declared to return "float"`: the value was already `Any` (from `json.load`, or from a function with no signature), so mypy stopped checking it, and it leaked into a function that promised a real type. Section 9 shows it in the troubleshooting table.

"We work the kinds, not every line." Sort the log first, then fix one kind at a time. Missing annotations usually come first, because until a function has a signature mypy cannot check what happens inside it with real types. The words of the message are the clue: "missing a type annotation" or "untyped", "Incompatible types", `Item "None" of`, `Returning Any`."""
)

S7_BODY = (
    """Typing `--strict` by hand is easy to forget, so the setting moves into `pyproject.toml`, where everyone and CI read the same rule. Your group repo had:

"""
    + code(
        "toml",
        """
[tool.mypy]
python_version = "3.13"
check_untyped_defs = true
""",
    )
    + """

From session 7 it has:

"""
    + code(
        "toml",
        """
[tool.mypy]
python_version = "3.13"
strict = true
""",
    )
    + """

`check_untyped_defs` told mypy to check the bodies of untyped functions, but it never asked anyone to write a hint. `strict = true` replaces it: every function needs a full signature, and the checks of `--strict` apply on every run without a flag to remember. The demo never had `check_untyped_defs`: it went straight to `strict = true` in `88b83c3` ("Add pytest and turn on strict type checking"), the same commit that added `mypy` and `pytest` to the dev dependencies.

CI already runs `uv run mypy src tests`, so from now on **strict applies to the tests too**. A test returns nothing, and strict wants that said: every `def test_…()` needs `-> None`. The session 8 tests start that way, for example `def test_largest_expense_of_nothing_is_none() -> None:`. With the old `check_untyped_defs` setting, a test without `-> None` passed; with `strict = true` it is an error.

The last row of the lab's troubleshooting table deserves a real example: **CI red at Types, green locally.** This is a real run on a copy of the demo in which two tests lost their `-> None`:

"""
    + code("console", CI_RUN)
    + """

Same code, same configuration, two answers: the first command never opened `tests/`. The lab's advice is "Run it exactly as CI does." The fix is two `-> None`, not a smaller CI command: CI is the referee, and a referee that only watches half the pitch is not doing the job.

Part 2 of the lab, for your group: set `strict = true`, run `uv run mypy src tests`, fix what it reports, mark where your project's I/O lives, push, and keep CI green before the `v0.2` tag that Checkpoint 2 marks."""
)

S8_BODY = (
    """Part 1 of lab 07 hands you code with bad names, on purpose, and asks you to refactor it in pairs without changing what it prints. `main.py`, `code.py` and `utils.py`:

"""
    + code("python", INVOICE_MAIN)
    + "\n\n"
    + code("python", INVOICE_CODE)
    + "\n\n"
    + code("python", INVOICE_UTILS)
    + """

First you **record the behaviour**: `uv run python main.py` prints `163.35` and `20.0`. Work it through once by hand: pencils 10 × 5 = 50, books 50 × 2 = 100, subtotal 150; the 10% discount gives 135; 21% tax on 135 gives 163.35. `x` averages 10, 20 and 30: `20.0`.

Then seven steps, running `main.py` after **every** one. "If the output changes, you have not refactored: undo the last step."

1. **Rename** `calc`, `c`, `i`, `d`, `t`, `p`, `x`, `l` so that no comment is needed. (`code.py` is a poor module name too: Python already has a module called `code`.)
2. **Extract constants**: `0.21` and `0.1` get names.
3. **Replace the tuple with a type**: a small `@dataclass` for an invoice line, so `p[1] * p[2]` becomes named fields, as with `Expense`.
4. **Extract functions**: `calc` sums the lines, applies a discount and applies tax, so it becomes three functions named for what they return.
5. **Remove the duplication**: `x` re-implements a sum; decide whether to use Python's `sum`.
6. **Add types** to every function.
7. **Check**: the same two numbers, `ruff check` passes, `mypy --strict` says `Success: no issues found`.

Each step is a move from the table, so you can name it in an exam answer.

Before finishing, you write down every input that would break the code or give a surprising answer: an empty list, a discount above 100% or below 0, a negative quantity, a price of zero. We ran them on the original code, on one invoice line of pencils at 10 × 5 with the usual 21% tax and 10% discount unless stated. `x([])` crashes with `ZeroDivisionError: division by zero`. A discount of `1.5` gives a negative invoice, `-30.25`. A discount of `-0.2` is silently ignored, giving `60.5`, the same as no discount, because of `if d>0`. A quantity of `-5` gives `-54.45`, and a price of zero gives `0.0`. (On `main.py`'s two lines the same two discounts give `-90.75` and `181.5`.)

You **name** these and do not test or fix them yet. Fixing them changes behaviour, so it is not part of a refactoring; and "Friday is testing": the list is what you turn into tests."""
)

S9_BODY = (
    r"""The lab ends with a troubleshooting table: the messages strict mode produces most often, and what each one means. The third column is not in the lab: it is our mapping of each row to the kinds. Three come from slide 10 (missing annotation, types disagree, None not handled). The fourth, **Any leaks in**, comes from the teacher's official answer to sample Q9.

| Symptom | What it means | Kind |
|---|---|---|
| `Function is missing a return type annotation` in `tests/` | add `-> None` to the test | missing annotation |
| `Function is missing a type annotation for one or more parameters` | hint every parameter and the return | missing annotation |
| `Missing type arguments for generic type "dict"` | write `dict[str, float]`, not `dict` (same for `list`, `tuple`) | missing annotation |
| `Need type annotation for "totals"` | an empty `{}` or `[]` has no type yet: `totals: dict[str, float] = {}` | missing annotation |
| `Returning Any from function declared to return "float"` | the value came from something untyped (`json`, or a function with no signature): convert it, `float(...)`, or annotate the variable | Any leaks in |
| `Item "None" of "… \| None" has no attribute "…"` | a real bug: check for `None` first, or make the function unable to return it | None not handled |
| `Untyped decorator makes function untyped` | a decorator without hints, usually fixed by upgrading the library (`uv lock --upgrade-package typer`) | missing annotation |
| `Library stubs not installed for "…"` | `uv add --dev types-<name>`; the message gives the exact name | missing annotation |
| CI red at **Types**, green locally | you ran `mypy src`; CI runs `mypy src tests` | wrong command |

**Any leaks in** is the one row that is not "types disagree". His official answer to sample Q9 puts `Returning Any` in its own kind: "I gave up on this value". Somewhere upstream a value became `Any` (`json.load` returns `Any`, and so does a call to a function with no signature), mypy stopped checking it, and the `Any` leaked into a function that promised a `float`. mypy has not seen two types that clash. It has seen no type at all. The fix is to give the value a real type where it enters: convert it, or annotate the variable.

One precise note: a field from `csv.reader` is already typed `str`, so returning it where a `float` was promised gives `Incompatible return value type (got "str", expected "float")` instead (we ran it). That one is types disagree, because both types are known. The fix is the same: `float(row[3])`.

Two "fixes" make any message disappear, and both are distractors on the sample paper. `# type: ignore` tells mypy not to report a line; the code is unchanged. A return type of `Any` tells mypy "this could be anything, do not check it", so every use of the value goes unchecked, typos included. We ran both on a lookup that returns `Expense | None`:

"""
    + code(
        "console",
        """
$ uv run mypy --strict ignored.py
Success: no issues found in 1 source file
$ uv run python ignored.py
AttributeError: 'NoneType' object has no attribute 'amount'
$ uv run mypy --strict anyfix.py
Success: no issues found in 1 source file
$ uv run python anyfix.py
AttributeError: 'Expense' object has no attribute 'amout'. Did you mean: 'amount'?
""",
    )
    + """

(Tracebacks trimmed to their last line.) mypy is satisfied and the program still crashes. So ask of any fix: **does it change what happens when the value is missing, or only what mypy says?** A real fix for `Item "None"` decides what the program does with no result: skip the lines, as `format_report` does with `if largest is not None:`, show a message, or change the function so it cannot return `None`. That is sample Q3's answer, and why silencing three errors "to get CI green" (sample Q9) fails: the referee goes quiet and the crash ships."""
)

sections = [
    {
        "id": s(1),
        "heading": "Refactoring: change the structure, keep the behaviour",
        "body_md": S1_BODY,
        "key_points": [
            "Refactoring: change the structure, keep the behaviour. If the output changes, it was not a refactoring.",
            "Moves are small on purpose: one move, run, compare; if the output changed, undo that one step.",
            "Evidence: `diff before.txt after.txt` prints nothing, and every test passes without being edited.",
            "Features, bug fixes and format changes alter behaviour on purpose, so they are not refactorings.",
        ],
        "exam_note_md": "Sample Q2 shape: four changes, one keeps the behaviour. Look for the words that guarantee unchanged behaviour (identical output, tests passing unedited), not for the change that sounds tidiest.",
        "source_ref": "S7 slides 3 and 5; S6 slide 30; labs/07-refactor.md",
        "check": [q(1), q(2), q(35)],
    },
    {
        "id": s(2),
        "heading": "The six moves, and where you saw them",
        "body_md": S2_BODY,
        "key_points": [
            "Six moves: extract constant, rename, separate I/O from logic, introduce a type, extract function, decompose conditional.",
            "The history from `v0.1` to `v0.2` makes five of these moves in small commits, each one checked on its own; decompose conditional comes from the slides.",
            "Name the move and the problem it solves: a magic number, a comment doing a name's job, a function that prints, a tuple, a function with several jobs, a nested `if`.",
        ],
        "exam_note_md": "Sample Q7 part 3 asks you to describe in words how you would change code. Naming the move and the problem it removes (\"extract a constant for the 1.1 tolerance, so it has a name and one place to change\") is what earns the marks.",
        "source_ref": "S7 slides 3 and 5; S6 slides 13–23; expense-tracker 5e9466d–04d699f",
        "check": [q(5), q(46), q(36)],
    },
    {
        "id": s(3),
        "heading": "Decompose conditional: a condition with a name",
        "body_md": S3_BODY,
        "key_points": [
            "\"A condition with a name is a condition you can test.\"",
            "`is_wanted` answers one yes/no question for one expense; `category == \"\"` means no filter, and `>=` keeps an amount equal to the minimum.",
            "Boolean names read as questions: `is_wanted`, `is_duplicate`, not `flag`.",
        ],
        "exam_note_md": "Expect to read a named condition and predict `True` or `False` for a given expense, or to say what the move buys you: a rule you can test with a single call.",
        "source_ref": "S7 slide 6; S6 slides 15 and 19; tests/test_report.py at v0.4",
        "check": [q(7), q(8)],
    },
    {
        "id": s(4),
        "heading": "What a type checker catches that a linter cannot",
        "body_md": S4_BODY,
        "key_points": [
            "ruff checks how the code is written; mypy checks that every use of a value fits its type.",
            "`Expense | None` says \"no result\" is a normal answer, and mypy makes every caller deal with it.",
            "Empty list → `None` → crash at 2 a.m.: the checker finds it before anyone runs the program.",
            "Tests check the cases somebody wrote; mypy checks every value the type allows.",
        ],
        "exam_note_md": "A favourite distractor: \"ruff passes and the tests pass, so the mypy error is a false alarm.\" An `Item \"None\"` error is the one that predicts a real crash.",
        "source_ref": "S7 slide 8; S6 slides 26–27; expense-tracker 04d699f",
        "check": [q(9), q(10)],
    },
    {
        "id": s(5),
        "heading": "Reading an error without panic",
        "body_md": S5_BODY,
        "key_points": [
            "File and line: where. Message: what. `[code]`: what to search for.",
            "Read the first error. Fix it. Run again. Later errors are often the same one repeating.",
            "The reported line is where mypy noticed; the cause can sit above it, as with `total = 0`.",
        ],
        "exam_note_md": "Long logs are a time trap. Group the errors by cause before answering: one missing signature is reported where it is defined, at every typed call, and wherever its result is returned.",
        "source_ref": "S7 slide 9; labs/07-refactor.md Part 2, step 2",
        "check": [q(12), q(13)],
    },
    {
        "id": s(6),
        "heading": "--strict on v0.1: one kind of error, then a second",
        "body_md": S6_BODY,
        "key_points": [
            "Without `--strict`, mypy does not look inside a function with no signature, so untyped code can say `Success`.",
            "On `v0.1`: four errors, all missing annotations. Add signatures and a second kind, types disagree, appears.",
            "Missing annotation → write the hint; types disagree → make them agree; None not handled → check it, or change the type.",
            "His official answer to sample Q9 adds a fourth kind: Any leaks in (`Returning Any`, \"I gave up on this value\").",
            "Work the kinds, not every line.",
        ],
        "exam_note_md": "Sample Q9 part 1 is this table: sort errors into the kinds (his answer uses four). Give the kind and a reason from the message, not just a label.",
        "source_ref": "S7 slide 10; expense-tracker v0.1 run with mypy 2.4.0",
        "check": [q(15), q(18), q(37)],
    },
    {
        "id": s(7),
        "heading": "Strict in your repo: strict = true, CI and -> None",
        "body_md": S7_BODY,
        "key_points": [
            "`strict = true` in `[tool.mypy]` replaces `check_untyped_defs = true`: every function needs a signature, on every run.",
            "CI runs `mypy src tests`, so tests are checked too and every `def test_…()` needs `-> None`.",
            "CI red at Types, green locally: you ran `mypy src`. Run it exactly as CI does.",
        ],
        "exam_note_md": "When your laptop and CI disagree, compare the commands before you suspect the machine. The fix goes into the code, never into a weaker CI step.",
        "source_ref": "S7 slide 11; labs/07-refactor.md Part 2 and troubleshooting; expense-tracker 88b83c3 and 0e05065",
        "check": [q(19), q(20)],
    },
    {
        "id": s(8),
        "heading": "The lab: refactoring the invoice code",
        "body_md": S8_BODY,
        "key_points": [
            "Record the behaviour first (`163.35`, `20.0`), run after every step, and undo a step that changes it.",
            "Each lab step is a named move: rename, extract constants, introduce a type, extract functions, remove duplication, add types.",
            "Done means the same output, `ruff check` passing and `mypy --strict` saying `Success`.",
            "Edge cases are named, not tested or fixed: fixing them changes behaviour, and Friday turns the list into tests.",
        ],
        "exam_note_md": "Expect to compute the invoice by hand for a new input, or to say which edge case crashes (`x([])`) and which only gives a surprising answer.",
        "source_ref": "labs/07-refactor.md Part 1; S7 slide 22; S6 slides 8–9",
        "check": [q(23), q(24), q(25)],
    },
    {
        "id": s(9),
        "heading": "The troubleshooting table, and judging a fix",
        "body_md": S9_BODY,
        "key_points": [
            "Most strict messages are missing hints: `-> None` on tests, parameter hints, `dict[str, float]`, an annotated empty `{}`.",
            "`Returning Any` is the fourth kind, Any leaks in (\"I gave up on this value\"): the value came from something untyped, so convert it or annotate it.",
            "`# type: ignore` and `Any` change what mypy says, not what Python does.",
            "A real fix for `Item \"None\"` decides what the program does when there is no result.",
        ],
        "exam_note_md": "Sample Q3 and Q9 part 3 are this judgement. The right answer handles the `None`; any answer that only makes the message go away is a distractor.",
        "source_ref": "labs/07-refactor.md troubleshooting table; sample Q3 and Q9",
        "check": [q(28), q(30), q(33)],
    },
]

# ---------------------------------------------------------------------------
# Terms
# ---------------------------------------------------------------------------

terms = [
    ("Refactoring", "Changing the structure of code while keeping its behaviour. If the output changes, it was not a refactoring.", 1),
    ("Behaviour", "What a program does from the outside: what it prints, what it writes, its exit code and the results its tests check. A refactoring must leave it unchanged; moving code between functions is structure.", 1),
    ("Refactoring move", "One small, named change to structure (extract constant, rename, separate I/O from logic, introduce a type, extract function, decompose conditional), checked by running the program after it.", 2),
    ("Extract constant", "Give a magic number a name and one place to change it: `40` becomes `RULE_WIDTH`.", 2),
    ("Introduce a parameter object / type", "Replace a tuple or a loose group of values with a named type, such as the `Expense` dataclass, so `e[3]` becomes `expense.amount`.", 2),
    ("Separate I/O from logic", "Split reading, computing and printing so the computing functions take values and return values, as `9d6c607` split `run()` into `read_expenses`, `largest_expense` and `format_report`, leaving `run()` as the one place that prints.", 2),
    ("Extract function", "Move a block out of a long function into a function whose name says what it returns, as `largest_expense` came out of `run()`.", 2),
    ("Decompose conditional", "Turn a tangle of conditions into guard clauses or a named condition such as `is_wanted`, so the rule can be read and tested.", 3),
    ("Guard clause", "An early `continue` or `return` that deals with an exception first, so the main path is not buried in nested `if`s.", 3),
    ("Linter (ruff)", "A tool that checks how code is written: unused imports, line length, import order. It does not follow types through the program.", 4),
    ("Type checker (mypy)", "A tool that follows the types through the code and reports any use of a value that does not fit its type, before the program runs.", 4),
    ("`Expense | None`", "A type meaning \"an `Expense`, or `None`\". mypy makes every caller handle the `None` case before using an attribute such as `.amount`.", 4),
    ("Error code", "The name in square brackets at the end of a mypy error, such as `[union-attr]`: the term to search for in the documentation.", 5),
    ("`--strict`", "mypy's strict mode: every function must be fully annotated and untyped code is no longer skipped.", 6),
    ("`strict = true`", "The `[tool.mypy]` setting in `pyproject.toml` that applies strict mode on every run, for everyone and for CI. It replaced `check_untyped_defs = true` in session 7.", 7),
    ("`check_untyped_defs`", "The earlier mypy setting: check the bodies of functions without hints, but never require the hints themselves.", 7),
    ("Edge case", "An input at the boundary of what the code expects (an empty list, a discount above 100%, a zero price) where it may crash or surprise.", 8),
    ("`# type: ignore`", "A comment that tells mypy not to report a line. It changes nothing at run time.", 9),
    ("`Any`", "The type that switches checking off: mypy accepts any use of a value typed `Any`, typos included.", 9),
    ("Any leaks in", "The fourth kind of mypy error, from the teacher's answer to sample Q9: `Returning Any from function declared to return \"float\"`. A value was already `Any` (from `json` or an untyped function), mypy gave up on it, and it leaked into a function that promised a real type. Fix: convert it or annotate it.", 9),
    ("Library stubs", "A separate package of type hints for a library that ships without them, installed with `uv add --dev types-<name>`.", 9),
]
terms_out = [{"term": t, "definition_md": d, "section_ref": s(n)} for t, d, n in terms]

# ---------------------------------------------------------------------------
# Traps
# ---------------------------------------------------------------------------

traps = [
    "\"Adding type hints made mypy report more errors, so the hints made the code worse.\" The errors were already there. Without a signature, plain mypy skips the body and even `--strict` sees only `Any` there; the hints give it real types to compare.",
    "\"Plain `mypy` says `Success`, so the code is checked.\" Without `--strict` (or `strict = true`), mypy does not look inside functions with no signature. Untyped `v0.1` passed plain mypy and failed strict with four errors.",
    "\"A rename is always a refactoring.\" Only if the output is unchanged. Renaming a printed label, or a constant that ends up with a different value, changes what the user sees.",
    "\"A bug fix that also tidies the code is a refactoring.\" A fix changes the output on purpose. Keep it in its own commit with a message that says so.",
    "\"`diff before.txt after.txt` printed nothing, so the refactoring is correct for every input.\" It is proven for that input. An empty file or a file of refunds can still behave differently.",
    "\"`# type: ignore` fixes the error.\" It hides the report. Python still runs the same line and still crashes on the `None`.",
    "\"Changing the return type to `Any` is a safe way to satisfy mypy.\" `Any` switches checking off for every use of the value, so even a typo like `.amout` is no longer reported.",
    "\"Fix the errors from the bottom of the log, one line at a time.\" Read the first error and fix its cause; later errors are often the same one repeating, and the cause can sit above the reported line.",
    "\"Green on my laptop means green in CI.\" Only if you run the same command. CI runs `mypy src tests`; `mypy src` never opens the tests.",
    "\"`Returning Any` is a types-disagree error.\" His official answer to sample Q9 files it as its own kind, Any leaks in (\"I gave up on this value\"): mypy saw no type at all, not two types that clash.",
]

# ---------------------------------------------------------------------------
# Flashcards
# ---------------------------------------------------------------------------

cards_raw = [
    ("What is a refactoring, in the session 7 slide's words?",
     "Change the structure, keep the behaviour. If the output changes, it was not a refactoring.", "concept", 1),
    ("Why are refactoring moves small on purpose?",
     "So you can run the program after each one. If the output changes, you know which move did it and undo only that step.", "concept", 1),
    ("Refactoring vs bug fix",
     "A bug fix changes the output on purpose: the wrong answer becomes right. A refactoring leaves every output as it was. They go in separate commits.", "distinction", 1),
    ("`diff before.txt after.txt` prints nothing. What do you know?",
     "The report is identical for the input you ran. Other inputs, such as an empty file or a file of refunds, are not covered.", "reading", 1),
    ("The six refactoring moves from session 7",
     "Extract constant; rename (replace comment with a name); separate I/O from logic; introduce a parameter object / type; extract function; decompose conditional.", "recall", 2),
    ("Which move turned `print(\"-\" * 40)` into `print(\"-\" * RULE_WIDTH)`?",
     "Extract constant (`5e9466d`, \"Replace magic numbers with named constants\").", "reading", 2),
    ("Which move turned `expenses.append((row[DATE], row[MERCHANT], row[CATEGORY], float(row[AMOUNT])))` into building an `Expense`?",
     "Introduce a parameter object / type (`017f926`). `e[3]` becomes `expense.amount`: a tuple is a missing type.", "reading", 2),
    ("Separate I/O from logic vs extract function",
     "Both split `run()`. Separating I/O puts reading and printing apart from computing (`format_report` returns lines). Extracting a function moves one block into a named function (`largest_expense`).", "distinction", 2),
    ("\"A condition with a name is a condition you can test\": why?",
     "`is_wanted(expense, category, minimum)` can be called with one expense and checked for `True` or `False`. Inside a loop, the rule can only be tested through the totals.", "concept", 3),
    ("`is_wanted(bar, \"dining\", 10.0)` where `bar` is a 10.0 dining expense: result?",
     "`True`. The category matches and `>=` keeps an amount equal to the minimum.", "reading", 3),
    ("ruff vs mypy",
     "ruff: how the code is written (unused import, line too long, import order). mypy: whether every use of a value fits its type, such as `None` used as an `Expense`.", "distinction", 4),
    ("Why can `largest_expense` cause a crash \"at 2 a.m.\"?",
     "It returns `Expense | None`. On an empty list it returns `None`, and `largest.amount` raises `AttributeError`. mypy reports it before anyone runs the program.", "concept", 4),
    ("The three parts of a mypy error line",
     "File and line (where), message (what is wrong), `[code]` (what to search for).", "recall", 5),
    ("The routine for a long mypy log",
     "Read the first error. Fix it. Run again. Later errors are often the same one repeating.", "concept", 5),
    ("Why did plain `mypy src` say `Success` on the untyped `v0.1`?",
     "Without `--strict`, mypy does not look inside a function with no signature, and `report.py` had none.", "concept", 6),
    ("`--strict` on `v0.1`: what kind were the four errors, and what happened after adding signatures?",
     "All missing annotations (`no-untyped-def`, `no-untyped-call`). With signatures, mypy looked inside and found a second kind: types disagree (`0` then float amounts).", "reading", 6),
    ("The kinds of strict error and their fixes (three on slide 10, a fourth in his answer to Q9)",
     "Missing annotation → write the hint. Types disagree → make them agree (`0.0`). None not handled → check it, or change the type. Any leaks in (`Returning Any`) → give the value a real type: convert it or annotate it.", "recall", 6),
    ("`Incompatible types in assignment (expression has type \"float\", variable has type \"int\")`: kind and usual fix?",
     "Types disagree. Make them agree: start the total at `0.0`, not `0`.", "reading", 6),
    ("What replaced `check_untyped_defs = true` in `[tool.mypy]` in session 7?",
     "`strict = true`. CI already ran `mypy src tests`, so from then on strict applied to the tests too.", "recall", 7),
    ("Why does every `def test_…()` need `-> None` after session 7?",
     "CI runs `mypy src tests` with `strict = true`, and strict wants a full signature on every function. A test returns nothing, so `-> None`.", "concept", 7),
    ("CI is red at Types, green on your laptop. What do you check first?",
     "The command. You ran `mypy src`; CI runs `mypy src tests`. Run it exactly as CI does.", "reading", 7),
    ("What does the invoice lab's original `main.py` print?",
     "`163.35` and `20.0`. That is the behaviour your refactor must keep.", "recall", 8),
    ("Which invoice edge case crashes, and how?",
     "`x([])`: `ZeroDivisionError: division by zero`, from `s/len(l)`. A 150% discount only gives a surprising negative total: `-30.25` for one line of pencils at 10 × 5 with 21% tax (`-90.75` on `main.py`'s two lines).", "reading", 8),
    ("Why are the lab's edge cases named but not fixed?",
     "Fixing them changes behaviour, so it is not part of a refactoring. Friday (testing) turns the list into tests.", "concept", 8),
    ("`Need type annotation for \"totals\"`: fix?",
     "An empty `{}` has no type yet. Write `totals: dict[str, float] = {}`.", "reading", 9),
    ("`Returning Any from function declared to return \"float\"`: which kind is it, where does `Any` come from, and what do you do?",
     "Any leaks in (\"I gave up on this value\"), not types disagree. The `Any` comes from something untyped such as `json.load`. Convert the value (`float(...)`) or annotate the variable with the type you expect.", "reading", 9),
    ("What does `# type: ignore` change when the program runs?",
     "Nothing. mypy stops reporting the line, and the program still crashes on the `None`.", "concept", 9),
    ("`Library stubs not installed for \"yaml\"`: `pip install` from the hint, or `uv add --dev`?",
     "`uv add --dev types-PyYAML`. It records the stubs in `pyproject.toml` and `uv.lock`, so CI and your teammates get them too.", "distinction", 9),
]
cards = [
    {"id": f"{MID}-f{i:02d}", "front_md": f, "back_md": b, "kind": k, "section_ref": s(n)}
    for i, (f, b, k, n) in enumerate(cards_raw, start=1)
]

# ---------------------------------------------------------------------------
# Questions
# ---------------------------------------------------------------------------

questions: list[dict[str, Any]] = []


def mcq(
    n: int,
    level: str,
    skills: list[str],
    sec: int,
    source_ref: str,
    origin: str,
    verified_by: str,
    stem: str,
    options: list[dict[str, Any]],
    explanation: str,
    **extra: Any,
) -> None:
    qd: dict[str, Any] = {
        "id": q(n),
        "type": "mcq",
        "level": level,
        "skills": skills,
        "stem_md": stem,
        "options": options,
        "explanation_md": explanation,
        "section_ref": s(sec),
        "source_ref": source_ref,
        "origin": origin,
        "verified_by": verified_by,
    }
    qd.update(extra)
    questions.append(qd)


# q01 ------------------------------------------------------------------------
mcq(
    1, "core", ["concept", "judgement"], 1, "S7 slide 5; sample Q2", "teacher-variant", "source",
    "Which of these changes to the expense-tracker is a refactoring?",
    [
        opt("Making `--min` default to `5.0` instead of `0.0`, so that small amounts are hidden unless asked for",
            "A new default changes what `uv run expenses report` prints for the same command. That is new behaviour, even though no option was added."),
        opt("Moving the largest-expense loop out of `run()` into `largest_expense`, with the report identical",
            "This is the slide's \"extract function\" move: the structure changes and the report stays identical, so by the slide's test it is a refactoring.",
            True),
        opt("Printing every amount with a euro sign (`12.40 €`) so the report is easier to read",
            "It may be a good idea, but the printed report changes. If the output changes, it was not a refactoring."),
        opt("Fixing `read_expenses` so that a row with a comma in the merchant name is no longer dropped",
            "A bug fix changes the output on purpose: rows that used to vanish now count. Good work, but a fix, in its own commit."),
    ],
    "A refactoring changes the structure and keeps the behaviour, and the slide's test is short: if the output changes, it was not a refactoring. Only the extract-function change leaves the report byte for byte identical; it is the exact example in the session 7 table (`largest_expense` out of `run()`). The other three may all be worth doing, but each one changes what the user sees: a new default, a new format, a fixed bug. They belong in their own commits, with messages that say the output changes.",
    variant_of="sample-paper-q02",
)

# q02 ------------------------------------------------------------------------
mcq(
    2, "exam", ["read-tool-output", "judgement"], 1, "S6 slide 30; S7 slide 5; labs/07-refactor.md", "slides", "run",
    "Your pair is doing the session 6 exercise on `v0.1`. You saved the report with `uv run expenses report --category dining --min 20 > before.txt`, replaced the widths `20`, `10` and `40` with named constants, saved `after.txt` the same way, and compared:\n\n"
    + code("console", """
$ diff before.txt after.txt
5c5
< dining                 3157.92
---
> dining                     3157.92
7c7
< TOTAL                  3157.92
---
> TOTAL                      3157.92
""")
    + "\n\nWhat should you do?",
    [
        opt("Keep the change: only spaces moved, and every amount is still the same",
            "The output is the behaviour, spaces included. A reader, or a script that reads the columns, now gets a different report."),
        opt("Run the report again on the new code to make a fresh `before.txt`, then compare",
            "That throws the evidence away. `before.txt` must come from the code before the move, or the diff compares the new code with itself."),
        opt("Commit it as \"Extract constants\" and fix the column width in a later commit",
            "The commit message would claim a refactoring while the output changed, which misleads anyone who reads the history later."),
        opt("Undo the step and redo it: one constant does not hold the number it replaced",
            "Two lines moved four characters right, so `NAME_WIDTH` or `AMOUNT_WIDTH` no longer holds the number it replaced. A small move tells you where to look.",
            True),
    ],
    "The `diff` shows lines 5 and 7 changed: the amounts sit four characters further right, while the rule lines did not move. Either the name column grew from 20 to 24 or the amount column from 10 to 14; we ran both, and the diffs are identical. Extracting a constant must keep the value it replaces; here one did not, so the output changed and, by the slide's definition, the step was not a refactoring. The lab's rule applies: if the output changes, undo the last step. Because the step was small, the culprit is easy to find: one of the two width constants.",
)

# q03 ------------------------------------------------------------------------
mcq(
    3, "beyond", ["read-code", "predict-output", "judgement"], 8, "labs/07-refactor.md Part 1; S6 slides 8–9", "lab", "run",
    "In the invoice lab, a pair replaces the original `calc` with this version. `main.py` still prints `163.35` and `20.0`.\n\n"
    + code("python", """
def invoice_total(lines: list[InvoiceLine], tax_rate: float, discount_rate: float) -> float:
    subtotal = 0.0
    for line in lines:
        subtotal += line.price * line.quantity
    discounted = subtotal * (1 - discount_rate)
    return discounted * (1 + tax_rate)
""")
    + "\n\nThe original was:\n\n" + code("python", INVOICE_CODE)
    + "\n\nWhich input would show that this is not a pure refactoring of `calc`?",
    [
        opt("An empty list of lines, with the usual 21% tax and 10% discount",
            "Both versions return `0.0`: nothing to sum, and a percentage of zero is zero."),
        opt("Pencils at 10 × 5, the usual 21% tax, and a discount of `1.5` (150%)",
            "Both return `-30.25`. The answer is surprising, a negative invoice, but it is the same in both versions."),
        opt("Pencils at 10 × 5, the usual 21% tax, and a discount of `-0.2`",
            "The original skips the discount because `d>0` is false and returns `60.5`; the new version applies it as a surcharge and returns `72.6`.",
            True),
        opt("One line with a price of zero, with the usual tax and discount",
            "Both return `0.0`. A zero subtotal stays zero whichever way the discount and tax are applied."),
    ],
    "The original applies the discount only `if d>0` and the tax only `if i>0`; the new version applies both every time. For rates of zero or more the two formulas are the same algebra, so the lab's two numbers cannot tell them apart. We ran both versions: with a discount of `-0.2`, `calc` returns `60.5` and `invoice_total` returns `72.6`. Removing a condition changes behaviour wherever that condition used to stop something, here a negative rate. A refactoring keeps the `if`s, or moves them into named functions. Session 6 showed this version as \"the same logic, twice\" to argue for readability, and for ordinary rates it is; in the lab, where the output must not change for any input, the `if`s are part of the behaviour.",
)

# q04 ------------------------------------------------------------------------
mcq(
    4, "beyond", ["read-code", "read-tool-output", "judgement"], 1, "expense-tracker 9d6c607; S7 slide 5", "history", "run",
    "Commit `9d6c607` (\"Separate reading and printing from the calculation\") moved the search for the largest expense out of `run()`.\n\nBefore, inside `run()` (at `f3bb801`, the commit before):\n\n"
    + code("python", """
largest_amount = 0.0
largest = None
for expense in expenses:
    if expense[AMOUNT] > largest_amount:
        largest_amount = expense[AMOUNT]
        largest = expense
""")
    + "\n\nAfter:\n\n"
    + code("python", """
def largest_expense(expenses):
    largest = None
    for expense in expenses:
        if largest is None or expense[AMOUNT] > largest[AMOUNT]:
            largest = expense
    return largest
""")
    + "\n\nOn the sample data, `diff before.txt after.txt` printed nothing (we checked). We then ran `uv run expenses report refunds.csv` with both versions, on a file whose only row is a Zara refund of `-15.00`, and compared:\n\n"
    + code("console", """
$ diff before.txt after.txt
4a5,7
>
> Largest single expense:
> Zara (clothing) on 2026-03-02 for -15.00
""")
    + "\n\nWhat can you conclude?",
    [
        opt("It changed behaviour for files with no positive amount, which the sample data could not reveal",
            "The old loop started from `0.0`, so it never picked an amount at or below zero; the new one starts from the first expense. Different input, different output.",
            True),
        opt("The refund file is malformed, so the difference does not count as a change in behaviour at all",
            "The row has four fields and a valid amount, and `read_expenses` accepts it. Refunds are normal data: a `v0.4` test checks that a refund reduces its category total."),
        opt("`diff` is unreliable for this kind of check, so outputs should be compared by eye instead",
            "`diff` did its job exactly: it showed the three lines that appeared. The limit was the input the first check used, not the tool."),
        opt("The two versions must behave the same, because every test in the `v0.4` suite passes",
            "The `v0.4` tests try an empty list, a normal list and a tie, never a list of only negative amounts, so they cannot see this difference."),
    ],
    "By the slide's definition, if the output changes it was not a refactoring, and for this input it changed: a refund is now reported as the largest single expense. The old loop compared against a running maximum that started at `0.0` (as it had since `v0.0`); the extracted function compares against the first expense. On the sample data, which has positive amounts, both give the same answer, so the first `diff` was empty. The lesson is not that the commit is bad. A `diff` or a test suite proves behaviour only for the inputs it covers, which is why edge cases (empty, zero, negative) have to be checked on purpose.",
)

# q05 ------------------------------------------------------------------------
mcq(
    5, "exam", ["read-diff", "concept"], 2, "expense-tracker 5e9466d; S7 slide 5; S6 slides 14 and 16", "history", "source",
    "This hunk is from commit `5e9466d` of the expense-tracker:\n\n"
    + code("diff", """
         for row in reader:
-            # skip rows that do not have all four fields
-            if len(row) == 4:
-                rows.append((row[0], row[1], row[2], float(row[3])))
+            if len(row) == FIELDS_PER_ROW:
+                rows.append((row[DATE], row[MERCHANT], row[CATEGORY], float(row[AMOUNT])))
""")
    + "\n\nWhich refactoring move is this, and why could the comment go?",
    [
        opt("Introduce a type: each row is now described by named fields instead of positions",
            "The row is still a tuple built with `rows.append((...))`. Introducing a type came three commits later, in `017f926`, with `Expense`."),
        opt("Decompose conditional: the `if` now has a name of its own, so it can be tested",
            "It is the same single condition. Nothing was split, and no condition became a named function."),
        opt("Extract constant: the numbers got names, and the new name says what the comment said",
            "`FIELDS_PER_ROW` makes the rule readable, so the comment only repeated the line and could be deleted.",
            True),
        opt("Separate I/O from logic: reading a row now happens apart from checking its length",
            "The loop still reads and checks in the same place. Reading moved into `read_expenses` later, in `9d6c607`."),
    ],
    "The commit is \"Replace magic numbers with named constants\": `4` became `FIELDS_PER_ROW` and the indexes `0` to `3` became `DATE`, `MERCHANT`, `CATEGORY` and `AMOUNT`. Session 6's rule explains the comment: a comment that restates the next line is a symptom, and the fix is a name. Once the line reads `if len(row) == FIELDS_PER_ROW:`, the comment says nothing the code does not, so it goes. Nothing the program prints changes, so the move is a refactoring.",
)

# q06 ------------------------------------------------------------------------
mcq(
    6, "core", ["concept"], 2, "S6 slides 11, 13 and 14; S7 slide 5", "slides", "source",
    "Session 6 showed this line with a comment above it:\n\n"
    + code("python", """
# total of all expenses in this category above the threshold
d[e[2]] = d[e[2]] + e[3]
""")
    + "\n\nand the refactored line `totals[expense.category] += expense.amount`. In the move \"rename (replace comment with a name)\", what happens to the comment?",
    [
        opt("It is deleted, because the new names now say what it said",
            "\"The comment is a symptom. The fix is a name.\" Once the line reads well, the comment only repeats it.",
            True),
        opt("It stays above the new line, so readers get both the comment and the names",
            "A comment that restates the line is duplication. When someone changes the line and forgets the comment, the two disagree."),
        opt("It moves into a docstring at the top of the function, where comments belong",
            "Moving it does not change what it is: an explanation of *what* the code does, which the names now give."),
        opt("It is rewritten to explain what `d`, `e` and `2` stand for",
            "That keeps the bad names and adds more text to maintain. The move replaces the comment with names, not with a longer comment."),
    ],
    "Session 6's rule: \"A comment that explains what the code does is a failure of naming.\" The rename move puts the explanation into the names (`totals`, `expense.category`, `expense.amount`), so the comment has nothing left to say and is deleted. Comments are still welcome for *why*: a business rule, a workaround with its reason, a deliberate oddity. Those say what the code cannot.",
)

# q07 ------------------------------------------------------------------------
mcq(
    7, "core", ["concept"], 3, "S7 slide 6", "slides", "source",
    "Session 7 replaces two nested `if`s with `is_wanted(expense, category, minimum) -> bool` and says: \"A condition with a name is a condition you can test.\" What does that mean in practice?",
    [
        opt("mypy can now check the condition, which it cannot do while it sits inside a loop",
            "mypy checks code inside loops just as well. The gain is a separately callable rule, not extra type checking."),
        opt("The condition runs faster, because Python can reuse the function's earlier result",
            "Speed is not the point of the move, and Python does not cache a function's result on its own."),
        opt("The report output changes, which proves that the new named rule is really being used",
            "A refactoring must not change the output. If it did, the move went wrong."),
        opt("A test can call `is_wanted` with a single expense and check the `True` or `False` it returns",
            "Inside `total_by_category`, the rule is only visible through the totals. As a function, it is one call and one answer.",
            True),
    ],
    "Before the move, the only way to check \"is a 10.00 dining expense counted when the minimum is 10?\" is to build a list, call `total_by_category`, and work it out from the totals. After it, `is_wanted(expense, \"dining\", 10.0)` answers directly. A named condition is also easier to read: `if is_wanted(expense, category, minimum):` says what the `if` is for. The output of the program does not change; that is what makes it a refactoring.",
)

# q08 ------------------------------------------------------------------------
mcq(
    8, "exam", ["read-code", "predict-output"], 3, "S7 slide 6", "slides", "run",
    "Given the function from the slide and three expenses:\n\n"
    + code("python", IS_WANTED + """

bar = Expense("2026-10-01", "Bar Ramon", "dining", 10.0)
zara = Expense("2026-10-02", "Zara", "clothing", 40.0)
cabify = Expense("2026-10-03", "Cabify", "transport", 15.0)
""")
    + "\n\nWhich call returns `True`?",
    [
        opt("`is_wanted(bar, \"\", 20.0)`",
            "An empty category matches everything, but `10.0 >= 20.0` is false, so the result is `False`."),
        opt("`is_wanted(bar, \"dining\", 10.0)`",
            "The category matches and `10.0 >= 10.0` is true: `>=` keeps an amount equal to the minimum.",
            True),
        opt("`is_wanted(zara, \"dining\", 0.0)`",
            "A minimum of `0.0` accepts any amount, but `\"clothing\"` is not `\"dining\"`, so `matches_category` is false."),
        opt("`is_wanted(cabify, \"transport\", 15.01)`",
            "The category matches, but `15.0 >= 15.01` is false. Close is not enough."),
    ],
    "We ran the four calls: `False`, `True`, `False`, `False`. Read the function in two halves. `matches_category` is true when no category was asked for (`\"\"`) or when the categories are equal. The `and` then also needs `expense.amount >= minimum`. Only the second call passes both: dining matches dining, and 10.0 is not less than 10.0. This is what `test_minimum_keeps_amounts_equal_to_it` pins down in the `v0.4` tests.",
)

# q09 ------------------------------------------------------------------------
mcq(
    9, "core", ["concept"], 4, "S7 slide 8; S6 slide 27", "slides", "source",
    "Which of these problems can mypy find that ruff cannot?",
    [
        opt("`largest.amount` used on a value that is `None` for an empty list",
            "mypy follows the declared return type `Expense | None` and sees that `.amount` is used without handling `None`.",
            True),
        opt("`os` imported at the top of the file but never used anywhere (`F401`)",
            "That is ruff's job: it is one of the two example messages on the session 6 ruff slide."),
        opt("A line of 112 characters when the limit is 100 (`E501`)",
            "Line length is a style rule, and ruff reports it (`E501 Line too long (112 > 100)`)."),
        opt("Imports that are not sorted into the order the team agreed",
            "Import order is a ruff rule (the `I` rules selected in the demo's `pyproject.toml`), not a type question."),
    ],
    "ruff reads how the code is written: unused imports, line length, import order, simple mistakes. mypy reads what types flow through the code. The session 7 slide's example is the one only a type checker can see: `largest_expense` returns `Expense | None`, and `print(largest.amount)` ignores the `None`. On an empty list the program crashes, \"at 2 a.m.\". mypy reports it before anyone runs the program; ruff passes the same file without a word.",
)

# q10 ------------------------------------------------------------------------
mcq(
    10, "exam", ["read-tool-output", "predict-output"], 4, "S7 slide 8", "slides", "run",
    "A teammate's `report.py` (excerpt: the file starts with the frozen `Expense` dataclass from the demo, so the `print` is line 22):\n\n"
    + code("python", """
def largest_expense(expenses: list[Expense]) -> Expense | None:
    largest = None
    for expense in expenses:
        if largest is None or expense.amount > largest.amount:
            largest = expense
    return largest


def print_largest(expenses: list[Expense]) -> None:
    largest = largest_expense(expenses)
    print(largest.amount)
""")
    + "\n\n"
    + code("console", """
$ uv run ruff check report.py
All checks passed!
$ uv run mypy --strict report.py
report.py:22: error: Item "None" of "Expense | None" has no attribute "amount"  [union-attr]
Found 1 error in 1 file (checked 1 source file)
""")
    + "\n\nFor which list does `print_largest` crash when the program runs?",
    [
        opt("A list with a single expense in it, such as one Bar Ramon dinner",
            "With one expense the loop sets `largest` to it, and `.amount` exists. We ran it: it prints `10.0`."),
        opt("A list where two expenses tie for the largest amount",
            "The `>` keeps the first of the two; either way `largest` is an `Expense`. We ran it: it prints `40.0`."),
        opt("An empty list, such as a CSV with only its header row",
            "The loop never runs, `largest_expense` returns `None`, and `None.amount` raises `AttributeError`.",
            True),
        opt("A list whose only expense is a Zara refund of `-15.00`",
            "`largest is None` is true on the first pass, so the refund is chosen and returned. We ran it: it prints `-15.0`."),
    ],
    "The mypy message names the danger: one of the values `largest` can hold is `None`, and `None` has no `amount`. That only happens when the loop never runs, which means an empty list. We ran all four lists; only the empty one crashed: `AttributeError: 'NoneType' object has no attribute 'amount'`. ruff passed the file because nothing is wrong with how it is written. This is the slide's point: the checker finds the empty-list crash before anyone runs the program.",
)

# q11 ------------------------------------------------------------------------
mcq(
    11, "hard", ["read-tool-output", "judgement"], 4, "S7 slide 8; S6 slide 27", "slides", "run",
    "A teammate's branch adds `largest_line` to `src/tracker/summary.py` (excerpt; `largest_expense` returns `Expense | None` as in the demo):\n\n"
    + code("python", """
def largest_line(expenses: list[Expense]) -> str:
    largest = largest_expense(expenses)
    return f"Largest: {largest.merchant} {largest.amount:.2f}"
""")
    + "\n\nand one test for it in `tests/test_summary.py`:\n\n"
    + code("python", """
def test_largest_line_names_the_biggest_expense() -> None:
    expenses = [
        Expense("2026-10-01", "Bar Ramon", "dining", 10.0),
        Expense("2026-10-02", "Zara", "clothing", 40.0),
    ]

    assert largest_line(expenses) == "Largest: Zara 40.00"
""")
    + "\n\n"
    + code("console", """
$ uv run ruff check .
All checks passed!
$ uv run pytest -q
.                                                                        [100%]
1 passed in 0.00s
$ uv run mypy --strict src tests
src/tracker/summary.py:14: error: Item "None" of "Expense | None" has no attribute "merchant"  [union-attr]
src/tracker/summary.py:14: error: Item "None" of "Expense | None" has no attribute "amount"  [union-attr]
Found 2 errors in 1 file (checked 4 source files)
""")
    + "\n\nThe teammate says: \"ruff and pytest are green, so mypy is being pedantic. I'll add `# type: ignore` and merge.\" What do you answer?",
    [
        opt("Agree: two of the three commands pass, which is enough evidence to merge the branch",
            "The three tools answer different questions. The two green ones never looked at an empty list, so they say nothing about it."),
        opt("Agree, as long as a comment next to the `# type: ignore` explains the reason",
            "A comment explains the silence but does not change the code: an empty list still crashes."),
        opt("Disagree: remove the hints from `largest_line` so that mypy stops checking it",
            "Under strict a missing signature is itself an error, and hiding the function from the checker leaves the crash where it is."),
        opt("Disagree: the test never tries an empty list, and with one `largest_line` crashes",
            "mypy reasons about every value `Expense | None` allows, including the `None` the test never tried.",
            True),
    ],
    "The green results are true but narrow. ruff checked the writing, and pytest checked one input, a list of two expenses. mypy checked every value the type allows and found the one nobody tested: an empty list, where `largest_expense` returns `None` and `largest.merchant` raises `AttributeError`. The right response is to decide what the line should say when there are no expenses (as `format_report` does with `if largest is not None:`) and to add a test for the empty list. Silencing the error ships the crash.",
)

# q12 ------------------------------------------------------------------------
mcq(
    12, "core", ["read-tool-output"], 5, "S7 slide 9", "slides", "run",
    "You meet this line in a mypy run and the message means nothing to you:\n\n"
    + code("text", """
src/tracker/budget.py:21: error: Returning Any from function declared to return "float"  [no-any-return]
""")
    + "\n\nFollowing the session 7 slide, which part of the line do you search for?",
    [
        opt("`src/tracker/budget.py:21`, because it is unique to this error",
            "File and line tell you *where* to look in your code. Nobody else's documentation knows your file."),
        opt("`no-any-return`, the code in square brackets",
            "The slide: \"[code]: what to search for\". It names the check, so the docs and the lab table are indexed by it.",
            True),
        opt("`error:`, because it marks how serious the problem is",
            "Every line in the run says `error:`. It tells you nothing about which problem this is."),
        opt("`\"float\"`, because it is the type that went wrong",
            "The type is part of the message, and it appears in hundreds of unrelated errors. It does not identify the check."),
    ],
    "The slide splits an error into three parts: file and line (where), message (what is wrong, in plain words) and `[code]` (what to search for). When the message is unclear, the code is the search term: `no-any-return` leads straight to mypy's explanation, and to the lab's troubleshooting row \"Returning Any from function declared to return float\": the value came from something untyped; convert it or annotate the variable. His name for this kind is Any leaks in.",
)

# q13 ------------------------------------------------------------------------
mcq(
    13, "hard", ["read-tool-output", "predict-output"], 5, "S7 slide 9; labs/07-refactor.md", "lab", "run",
    "A teammate's `src/tracker/budget.py`:\n\n"
    + code("python", LONGLOG_CODE)
    + "\n\n"
    + code("console", LONGLOG_RUN)
    + "\n\nYou change line 12 to `def parse_amount(text: str) -> float:` and run mypy again. What do you expect to see?",
    [
        opt("Two errors: the `int`/`float` assignment on line 27 and the `None` on line 39",
            "Six of the eight lines came from the untyped `parse_amount`. The other two have causes of their own.",
            True),
        opt("Seven errors: only the line 12 error goes, because each line is a separate problem",
            "The `no-untyped-call` and `Returning Any` lines all exist because `parse_amount` had no signature. They go with it."),
        opt("Five errors: lines 12 and 17 go, but line 21 and both errors on line 28 stay",
            "Lines 21 and 28 also call `parse_amount`. Once it returns `float`, the calls are typed and nothing returns `Any`."),
        opt("No errors: all eight came from the missing signature",
            "`spent = 0` followed by float amounts, and the `None` from `find_by_merchant`, have nothing to do with `parse_amount`."),
    ],
    "We made the change and ran mypy again: two errors left, line 27 (`Incompatible types in assignment`) and line 39 (`Item \"None\" of \"Expense | None\"`). An untyped function is reported where it is defined (`no-untyped-def`), at every typed call (`no-untyped-call`, three times), and wherever its unknown result is returned (`Returning Any`, twice: the kind he calls Any leaks in, because the `Any` from the untyped call leaks into a function that promised a `bool` or a `float`). That is \"later errors are often the same one repeating\". Reading the first error and fixing its cause removed six lines; the two left are a types-disagree (`0.0`) and a real crash for an unknown merchant.",
)

# q14 ------------------------------------------------------------------------
mcq(
    14, "core", ["read-tool-output", "read-code"], 5, "labs/07-refactor.md steps 6–7; S7 slides 9–10", "lab", "run",
    "Halfway through the invoice lab, a pair has renamed everything and added hints, but changed nothing else:\n\n"
    + code("python", INVOICE_TYPED_CODE)
    + "\n\n"
    + code("text", INVOICE_TYPED_RUN)
    + "\n\nWhich change fixes the cause of all four errors without changing what the functions return?",
    [
        opt("Wrap the right-hand side of lines 6, 8, 10 and 17 in `int(...)`",
            "That makes every value an `int`, which throws away the decimals: the invoice would no longer be `163.35`."),
        opt("Change both return types from `float` to `int`",
            "The functions really do produce floats (`163.35`, `20.0`); declaring `int` makes the hint lie and leaves the variable problem in place."),
        opt("Start both totals at `0.0` instead of `0` (lines 4 and 15)",
            "mypy infers `int` from `total = 0`. Starting at `0.0` makes it a float from the first line, so every later assignment agrees.",
            True),
        opt("Add `# type: ignore[assignment]` to the four reported lines",
            "It removes the four messages and leaves the cause: `total` still starts as an `int`, and the checker stops watching those lines."),
    ],
    "The four errors have two causes, one per function: `total = 0` makes mypy decide `total` is an `int`, and each line that stores a float in it is then reported. The reported lines (6, 8, 10, 17) are where mypy noticed; the cause is on lines 4 and 15. We changed both to `0.0` and mypy said `Success: no issues found in 1 source file`. This is the slide's \"types disagree, make them agree (`0.0`)\", and it changes nothing the functions return.",
)

# q15 ------------------------------------------------------------------------
mcq(
    15, "core", ["read-tool-output", "concept"], 6, "S7 slide 10", "slides", "run",
    "On the demo at `v0.1` (no type hints in `report.py`):\n\n"
    + code("console", V01_PLAIN + V01_STRICT)
    + "\n\nWhy does plain `mypy` say `Success` when `--strict` finds four errors in the same code?",
    [
        opt("Plain mypy only checks `cli.py`, the one file that already has `typer` hints",
            "The summary says `checked 3 source files` in both runs. The same files were read; what differs is how much of them was checked."),
        opt("`--strict` turns warnings into errors, so the same four problems were warnings before",
            "The first run printed no warnings at all. Plain mypy did not see these problems, because it did not look."),
        opt("The first run used a cache from an earlier run, which hid the four errors",
            "A cache speeds a run up; it does not change the result. Run plain `mypy` again and you get `Success` again."),
        opt("Plain mypy does not look inside a function with no signature, and `report.py` has none",
            "Untyped functions are skipped by default. `--strict` refuses to skip them and reports the missing annotations.",
            True),
    ],
    "This is the slide's live demo. The slide reports 4 errors, all one kind, because mypy does not look inside a function with no signature. Plain mypy treats an untyped function as unfinished and skips its body, so untyped code passes. `--strict` requires every function to be annotated: it reports the two functions with no signature (`no-untyped-def`) and the two calls to them (`no-untyped-call`). All four are the first kind, missing annotation.",
)

# q16 ------------------------------------------------------------------------
mcq(
    16, "exam", ["read-tool-output", "judgement"], 6, "S7 slide 10", "slides", "run",
    "After the four `--strict` errors on `v0.1`, you add signatures to `calculate_totals` and `run`. Now mypy reports (notes trimmed):\n\n"
    + code("text", V01_SIGNATURES)
    + "\n\nA teammate says: \"The hints introduced three new bugs. Revert them.\" What is right?",
    [
        opt("Revert: the code had four errors and now has three different ones, so the hints made it worse",
            "Counting lines misses the point. The new errors describe code that was there before the hints were written."),
        opt("Keep them: the problems were already in the code, and the signatures let mypy look inside",
            "`d[e[2]] = 0` and `grand = 0` were always an `int` that later received floats. mypy could only see it once the functions had signatures.",
            True),
        opt("Keep them, but switch `--strict` off until the next tag",
            "Switching the referee off does not change the code. The same three problems would be waiting at the tag."),
        opt("Revert `run()` only, because errors in a function that prints do not matter",
            "Line 50 is in `run()` and it is the grand total the user reads. Printing functions are code like any other."),
    ],
    "The slide: \"Add the signatures and a second kind appears.\" The first run was all missing annotations; once the functions have signatures, mypy checks their bodies with real types and finds the second kind, types disagree: a total that starts as `0` (an `int`) and then receives float amounts. Those lines did not change; only the checker's view did. The fix is to make the types agree (`0.0` in two places, which we ran: `Success`); removing the hints would only hide the problem again.",
)

# q17 ------------------------------------------------------------------------
mcq(
    17, "exam", ["read-code", "judgement"], 6, "S7 slide 10", "slides", "run",
    "Part of `run()` at `v0.1`, after signatures were added:\n\n"
    + code("python", """
    totals = calculate_totals(rows, cat, minimum)
    grand = 0
    for t in totals:
        print(t[0].ljust(20) + ("%.2f" % t[1]).rjust(10))
        grand = grand + t[1]
""")
    + "\n\n"
    + code("text", """
src/expense_tracker/report.py:50: error: Incompatible types in assignment (expression has type "float", variable has type "int")  [assignment]
""")
    + "\n\nWhich fix is most appropriate?",
    [
        opt("Start the total as `0.0`, so it is a float from the first line",
            "The slide's fix for this kind: make the types agree. Nothing printed changes; `%.2f` formats `0.0` and `0` the same way.",
            True),
        opt("Write `grand = grand + int(t[1])`, so every value is an `int`",
            "The types agree, but every amount loses its cents and the `TOTAL` line prints a different number. That is a behaviour change."),
        opt("Annotate `grand: Any = 0`, so any number is accepted",
            "`Any` turns checking off for `grand`. The disagreement is hidden, not solved, and later mistakes with `grand` go unreported."),
        opt("Add `# type: ignore` to line 50, since the program prints the right total",
            "It does print the right total today. Silencing the line also silences any future real error on it."),
    ],
    "`grand = 0` makes mypy decide `grand` is an `int`; line 50 then stores `int + float`, a float, in it. That is the second kind, types disagree, and the session 7 table gives the fix in brackets: make them agree, `0.0`. We changed it (and the matching `d[e[2]] = 0`) and strict mode reported `Success`. The output is identical, so the fix is also a refactoring. Casting to `int` changes the totals; `Any` and `# type: ignore` change only what mypy says.",
)

# q18 ------------------------------------------------------------------------
mcq(
    18, "core", ["concept"], 6, "S7 slide 10", "slides", "source",
    "Which pairing of error kind and fix matches the session 7 table?",
    [
        opt("Missing annotation → type the value as `Any`, so nothing is missing",
            "`Any` is not a hint about the value, it is permission not to check it. The table's fix is to write the real hint."),
        opt("Types disagree → add `# type: ignore`, since each type is fine on its own",
            "The table says make them agree, for example `0.0` instead of `0`. Ignoring the line leaves the disagreement in the code."),
        opt("None not handled → check for `None` before use, or change the type",
            "Word for word the table: \"check it, or change the type\". Either way, the missing case gets an answer.",
            True),
        opt("None not handled → add `-> None` to the function's signature",
            "`-> None` says a function returns nothing, as tests do. It does nothing about a value that might be `None`."),
    ],
    "The slide's table has three rows. Missing annotation (\"what type is this?\") → write the hint. Types disagree (\"`int` here, `float` there\") → make them agree, as with `0.0`. None not handled (\"this can be missing\") → check it, or change the type. The distractors mix up `-> None`, which is the hint for a function that returns nothing, with a value that can be `None`, and offer `Any` or `# type: ignore`, which only silence the checker. His answer to sample Q9 adds a fourth kind that is not a row of the table: Any leaks in (`Returning Any`).",
)

# q19 ------------------------------------------------------------------------
mcq(
    19, "core", ["concept", "read-tool-output"], 7, "S7 slide 11; labs/07-refactor.md Part 2", "lab", "run",
    "Your group repo has two tests without `-> None`. With the old setting, `[tool.mypy]` holding `check_untyped_defs = true`, `uv run mypy src tests` printed `Success: no issues found in 6 source files`. After the session 7 change to `strict = true`:\n\n"
    + code("console", CI_TYPES_ONLY)
    + "\n\nWhy did the tests pass the old setting and fail the new one?",
    [
        opt("The old setting skipped the `tests/` folder, and `strict = true` is what adds `tests/` to the run",
            "Both runs used the same command, `mypy src tests`, and both checked 6 source files. The command decides the folders, not the setting."),
        opt("The old setting never required hints; `strict = true` requires a full signature on every function",
            "So a test with no return annotation was fine before and is an error now. The note even gives the fix: `-> None`.",
            True),
        opt("The two tests were broken all along, and pytest now reports them as failing tests",
            "These lines come from mypy, not pytest. The tests can pass perfectly and still miss an annotation."),
        opt("`strict = true` needs Python 3.13, and the tests were written for an older version",
            "`python_version = \"3.13\"` was in the section before and after. The change is about annotations, not versions."),
    ],
    "The lab replaces `check_untyped_defs = true` with `strict = true`. The old setting made mypy check inside untyped functions but never asked for the hints themselves, so `def test_...():` was accepted. Strict mode requires every function to say what it takes and returns, tests included, because CI runs `mypy src tests`. A test returns nothing, so the hint is `-> None`, exactly what the `note:` line suggests. We ran both settings on the same files to get these outputs.",
)

# q20 ------------------------------------------------------------------------
mcq(
    20, "exam", ["read-tool-output"], 7, "labs/07-refactor.md troubleshooting; expense-tracker 0e05065", "lab", "run",
    "Your push turns CI red at the step **Types**. On your laptop you had checked first:\n\n"
    + code("console", CI_RUN)
    + "\n\n(The first command is what you ran before pushing; the second is what CI runs.) What happened?",
    [
        opt("The CI machine has a different mypy version, so its result cannot be trusted",
            "The same error appears on your own laptop as soon as you run the CI command. The machine is not the difference."),
        opt("The tests fail on CI, so pytest is the step to fix first",
            "The red step is Types, which runs mypy. These are annotation errors in test files; pytest may well pass."),
        opt("`uv.lock` is out of date, so CI installed different packages",
            "A stale lockfile stops CI at the install step (`uv sync --locked`), before Types ever runs."),
        opt("You ran `mypy src`; CI runs `mypy src tests`, and two tests lack `-> None`",
            "The troubleshooting row: CI red at Types, green locally. Run it exactly as CI does.",
            True),
    ],
    "Same code, same configuration, two results: `mypy src` never opens `tests/`, so it cannot see that two test functions lack a return annotation. CI's Types step runs `uv run mypy src tests` with `strict = true`, and strict requires `-> None` on every test. The lab's troubleshooting table has this exact row, and its advice is to run the check exactly as CI does. The fix is two `-> None`; then both commands agree.",
)

# q21 ------------------------------------------------------------------------
mcq(
    21, "hard", ["read-tool-output", "judgement"], 7,
    "S7 slide 11; labs/07-refactor.md troubleshooting (parameters row, CI row); expense-tracker v0.4 tests/test_report.py",
    "lab", "run",
    "Your group added `-> None` to every test, as the session 7 slide says. CI is still red at **Types**. A teammate runs both commands:\n\n"
    + code("console", FIXTURE_RUN)
    + "\n\nLine 21 of `tests/test_report.py`:\n\n"
    + code("python", """
def test_totals_are_grouped_by_category_and_largest_first(expenses) -> None:
""")
    + "\n\n`expenses` is a pytest fixture that returns `list[Expense]`, and `uv run pytest` prints `24 passed`. The teammate proposes to change the CI step to `uv run mypy src`, \"because tests are not shipped to users\". What do you answer?",
    [
        opt("No: write `expenses: list[Expense]` in the test; CI checks tests because they are code too",
            "The message says a parameter has no hint, and the fixture already says what it returns. One short edit, and the referee keeps watching all the code.",
            True),
        opt("Yes: the 24 tests pass, so a missing hint in a test cannot hurt anyone who uses the program",
            "Passing and being typed answer different questions. A test with a type mistake can pass while checking the wrong thing, and after this change no test would be type-checked at all."),
        opt("No: add `-> None` to the test again, because strict mode only asks tests for their return type",
            "The test already ends in `-> None`. Strict wants every parameter typed as well: read the message, and do not stop at the slide's shortcut."),
        opt("Yes, but only until the `v0.2` tag is marked, and then put `tests` back into the CI step",
            "The lab says strict mode has to be in before the `v0.2` tag that Checkpoint 2 marks, and CI must stay green. A check switched off for a deadline tends to stay off."),
    ],
    "Two rows of the lab's troubleshooting table meet here. `Function is missing a type annotation for one or more parameters` means: write the hint on every parameter, and the return type. `-> None` is only the return half; the fixture parameter `expenses` still has no type, and the fixture's own signature gives it: `list[Expense]`. We removed that hint from the demo's `v0.4` test and ran both commands: `mypy src` passed, `mypy src tests` reported line 21, and pytest still passed 24 tests. The other half is the referee. CI runs `mypy src tests` so the team's rule applies to all the code; changing the step turns CI green by checking less.",
)

# q22 ------------------------------------------------------------------------
mcq(
    22, "exam", ["read-tool-output", "judgement"], 9, "labs/07-refactor.md troubleshooting; S3 slide 3; run in calibration-fix/q22", "lab", "run",
    "The project already depends on PyYAML. A teammate's `uv run mypy --strict src` reported `Library stubs not installed for \"yaml\"`. They ran `uv pip install types-PyYAML`, mypy then printed `Success: no issues found`, and they committed the code that uses `yaml` and pushed. CI's Types step fails:\n\n"
    + code("console", """
$ uv run mypy --strict src
src/expense_tracker/settings.py:1: error: Library stubs not installed for "yaml"  [import-untyped]
src/expense_tracker/settings.py:1: note: Hint: "python3 -m pip install types-PyYAML"
src/expense_tracker/settings.py:1: note: (or run "mypy --install-types" to install all missing stub packages)
src/expense_tracker/settings.py:1: note: See https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports
Found 1 error in 1 file (checked 4 source files)
""")
    + "\n\nWhat is the fix?",
    [
        opt("Add `ignore_missing_imports = true` to the mypy settings, so mypy stops asking for stubs",
            "That loosens the check for every library in the project, to work around one missing package. The stubs are cheap to declare."),
        opt("Declare the stubs for everyone with `uv add --dev types-PyYAML`, and commit `pyproject.toml` and `uv.lock`",
            "`uv pip install` changed only the laptop's `.venv`, so CI builds an environment without the stubs. `uv add --dev` edits both files; commit them together.",
            True),
        opt("Re-run the CI job: mypy downloads missing stubs on its own the second time it runs",
            "mypy never installs packages by itself in a plain run. The fresh checkout is identical, so the second run fails in the same place."),
        opt("Add `# type: ignore` to `import yaml`, because it passes on the laptop already",
            "Passing on one laptop is the \"works on my machine\" trap. The ignore also hides every use of `yaml` from the checker."),
    ],
    "A package installed with `uv pip install` lives only in your own `.venv`. `pyproject.toml` and `uv.lock` are the single source of truth, and CI builds a fresh environment from them, so the stubs that made mypy pass on the laptop are missing there. The error is the same one the teammate saw first, which tells you the situation is back to the start. The lab's way to add stubs is `uv add --dev types-PyYAML`, which records them in `pyproject.toml` and `uv.lock` in one go. Real run: on the laptop copy mypy printed `Success`; on a fresh copy of the same files, built with `uv sync --locked`, it printed the error shown.",
)

# q23 ------------------------------------------------------------------------
mcq(
    23, "core", ["concept"], 8, "labs/07-refactor.md Part 1", "lab", "source",
    "In the invoice lab, after step 4 (extract functions), `main.py` no longer prints the two numbers you wrote down at the start. What does the lab tell you to do?",
    [
        opt("Write down the new numbers as the behaviour, since the new structure is clearer",
            "The behaviour is fixed at the start. Changing the reference to match the new code makes the check meaningless."),
        opt("Carry on with steps 5 to 7 and compare the output once, at the end",
            "Then a change in step 4 could hide behind three more steps. The lab says run `main.py` after every step."),
        opt("Run `ruff check` and `mypy --strict`; if both pass, the change is fine",
            "Both tools check how the code is written and typed. Neither knows that the invoice should be `163.35`."),
        opt("Undo the last step: if the output changes, you have not refactored",
            "The lab's own words. Small steps mean only one step can be responsible, so you undo it and try again.",
            True),
    ],
    "The lab defines the behaviour before you touch anything: `163.35` and `20.0`. It then asks you to run `main.py` after every step, and says: \"If the output changes, you have not refactored: undo the last step.\" Clean, typed code that prints a different invoice is a broken invoice. ruff and mypy are part of the final check (step 7), but only the output tells you whether the behaviour survived.",
)

# q24 ------------------------------------------------------------------------
mcq(
    24, "exam", ["read-code", "predict-output"], 8, "labs/07-refactor.md Part 1", "lab", "run",
    "Using the lab's original `calc`:\n\n" + code("python", INVOICE_CODE)
    + "\n\nWhat does `print(calc([(\"pen\", 2, 3)], 0.0, 0.5))` print?",
    [
        opt("`3.0`", "2 × 3 = 6; `d` is `0.5`, so the discount halves it to 3.0; `i` is `0.0`, so no tax is added.", True),
        opt("`9.0`", "That reads `i` as the discount and `d` as the tax. The parameters are `calc(c, i, d)`: `i` is tax, `d` is discount."),
        opt("`6.0`", "That skips the discount. `d>0` is true for `0.5`, so `t` becomes `6 - 6 × 0.5`."),
        opt("`3.63`", "That adds 21% tax, the rate in `main.py`. Here `i` is `0.0`, so `if i>0` is false and no tax is applied."),
    ],
    "We ran it: `3.0`. Walk the code: `t` starts at `0` and adds `p[1]*p[2]` = 2 × 3 = 6. `d` is `0.5`, so `t = 6 - 6 × 0.5 = 3.0`. `i` is `0.0`, so the tax branch is skipped. The wrong answers are the mistakes the bad names invite: with parameters called `i` and `d`, it is easy to swap tax and discount (`9.0`) or to assume the tax rate from `main.py`. That is the case for step 1 of the lab: rename until no comment is needed.",
)

# q25 ------------------------------------------------------------------------
mcq(
    25, "exam", ["predict-output"], 8, "labs/07-refactor.md edge cases", "lab", "run",
    "The lab asks you to name the edge cases of the original code (below). Which of these calls makes the program crash?\n\n"
    + code("python", INVOICE_CODE) + "\n\n" + code("python", INVOICE_UTILS),
    [
        opt("`calc([(\"pencil\", 10, 5)], 0.21, 1.5)`",
            "A 150% discount gives a negative invoice: we ran it and got `-30.25`. Surprising, but no crash."),
        opt("`x([])`",
            "`s` stays `0` and `len(l)` is `0`, so `s/len(l)` raises `ZeroDivisionError: division by zero`.",
            True),
        opt("`calc([], 0.21, 0.1)`",
            "No lines means `t` stays `0`; the discount and tax of zero are zero. We ran it: `0.0`."),
        opt("`calc([(\"pencil\", 10, -5)], 0.21, 0.1)`",
            "A negative quantity gives a negative total, `-54.45`. Wrong for a real invoice, but the code runs."),
    ],
    "We ran all four. Only `x([])` crashes:\n\n"
    + code("text", """
  File "utils.py", line 5, in x
    return s/len(l)
           ~^~~~~~~
ZeroDivisionError: division by zero
""")
    + "\n\nThe others return a number, and that is what makes them dangerous in a different way: a negative invoice or a negative quantity goes through without complaint. The lab's list (empty list, discount above 100% or below 0, negative quantity, zero price) mixes both: one crash, several surprising answers. You name them now and turn them into tests on Friday.",
)

# q26 ------------------------------------------------------------------------
mcq(
    26, "hard", ["read-tool-output", "judgement"], 8, "labs/07-refactor.md Part 1", "lab", "run",
    "After the seven steps, your pair's version gives:\n\n"
    + code("console", """
$ uv run python main.py
163.35
20.0
$ uv run ruff check .
All checks passed!
$ uv run mypy --strict .
Success: no issues found in 2 source files
""")
    + "\n\nWhich claim does this evidence support?",
    [
        opt("The refactored code now copes with an empty list too, because mypy checked the types",
            "mypy checks that types fit. `average([])` is perfectly typed and still divides by zero."),
        opt("The refactoring also keeps the behaviour for a negative discount, because the output did not change",
            "The output was checked for the two calls in `main.py`. A negative discount was never run, and `if d>0` makes it a likely place for a difference."),
        opt("The behaviour is kept for the two calls in `main.py`, and the code is clean and typed",
            "That is what the three results show, and no more: the lab's definition of done.",
            True),
        opt("The output comparison adds little, because only tests can show that behaviour was kept",
            "The output comparison is the lab's evidence that behaviour was kept for those calls. Friday's tests add more cases; they do not replace it."),
    ],
    "Each result answers one question. The output says the behaviour is the same for the two calls in `main.py`; ruff says the code is written cleanly; mypy says every function is typed and the types fit. Together they meet the lab's definition of done. They do not cover other inputs: the edge cases you named (an empty list, a discount outside 0 to 100%) were not run, and a type checker does not run code at all. That gap is what Friday's tests fill.",
)

# q27 ------------------------------------------------------------------------
mcq(
    27, "exam", ["read-code", "judgement"], 8, "labs/07-refactor.md step 5", "lab", "run",
    "Step 5 of the invoice lab: \"`x` re-implements a sum.\"\n\n" + code("python", INVOICE_UTILS)
    + "\n\n`main.py` prints `x([10,20,30])`, which is `20.0`. Which change removes the duplication and keeps the behaviour?",
    [
        opt("Rename `x` to `average` and compute it as `sum(values) / len(values)`",
            "Python's `sum` replaces the hand-written loop, the name says what it returns, and `main.py` still prints `20.0`.",
            True),
        opt("Make `calc` call `x` to add up the invoice lines",
            "`x` returns the average, not the sum. The invoice would come out as an average of line amounts, not `163.35`."),
        opt("Delete `x` and print `sum([10, 20, 30])` in `main.py` instead",
            "That prints `60`, not `20.0`. The duplication is gone, and so is the behaviour."),
        opt("Keep both loops but give them the same variable names, so the duplication is easy to see",
            "Matching names make the duplication visible; they do not remove it. There are still two hand-written sums."),
    ],
    "The loop in `x` adds the values one by one, which is what Python's built-in `sum` already does. Using it removes the duplication; naming the function `average` says what it returns, the session 6 rule for function names. We ran the refactored version and it printed `20.0`, as before. The distractors either change what is computed (a sum is not an average) or leave the duplication in place.",
)

# q28 ------------------------------------------------------------------------
mcq(
    28, "exam", ["read-tool-output", "judgement"], 9, "sample Q3; labs/07-refactor.md troubleshooting", "teacher-variant", "run",
    "`mypy --strict` reports this error on the code below:\n\n"
    + code("python", LABELS_CODE)
    + "\n\n" + code("text", LABELS_RUN)
    + "\n\nWhich fix is most appropriate?",
    [
        opt("Add `# type: ignore` to the end of line 12 so that CI goes green again",
            "The line still runs the same way: for an unknown merchant, `None.upper()` raises `AttributeError`."),
        opt("Handle the `None` case in `label_for` before calling `.upper()`",
            "This is the table's fix for None not handled. The missing case gets an answer instead of a crash.",
            True),
        opt("Change the return type of `category_of` to `Any` instead",
            "mypy stops checking every use of the result, and the crash is still there for an unknown merchant."),
        opt("Wrap line 12 in `try` / `except Exception: pass` to be safe",
            "That swallows every error, including ones you did not expect, and the function then returns nothing at all instead of a label."),
    ],
    "`category_of` says honestly that it can return `None`: a merchant with no expenses has no category. `label_for` ignores that and calls `.upper()`. We ran `label_for` for `\"Cabify\"` with no Cabify expense: `AttributeError: 'NoneType' object has no attribute 'upper'`. The lab calls this row a real bug. The fix is a decision: what should the label say for an unknown merchant? Check for `None` and answer it. The other options make the message disappear and leave the crash.",
    variant_of="sample-paper-q03",
)

# q29 ------------------------------------------------------------------------
mcq(
    29, "exam", ["read-tool-output", "judgement"], 9, "labs/07-refactor.md troubleshooting", "lab", "run",
    "A teammate's loader, and what strict mypy says about it:\n\n"
    + code("python", """
import json


def load_budgets(path: str) -> dict[str, float]:
    with open(path) as handle:
        return json.load(handle)
""")
    + "\n\n" + code("text", """
budgets_bad.py:6: error: Returning Any from function declared to return "dict[str, float]"  [no-any-return]
""")
    + "\n\nWhich fix is most appropriate?",
    [
        opt("Change the declared return type to `Any`, since JSON can hold anything",
            "Then every caller loses the checks on budgets: a typo or a wrong type in a budget lookup goes unreported."),
        opt("Add `# type: ignore[no-any-return]`, since the code works when the file is right",
            "It hides this line's report, and any later mistake on the same line, when the lab's row offers a real change: convert the value or annotate the variable."),
        opt("Delete the return type, so mypy has nothing to compare the result with",
            "Under strict that is a missing annotation, and callers no longer know what they get back."),
        opt("Annotate the loaded value as `dict[str, float]` before returning it",
            "The lab's fix: annotate the variable. It writes down what you expect the file to hold, so callers keep their checks; converting each value with `float(...)` would also check it at run time.",
            True),
    ],
    "`json.load` has no idea what the file contains, so its result is `Any`, and strict mode will not let a function promise `dict[str, float]` while returning an unknown. The lab's row says: the value came from something untyped; convert it or annotate the variable. This is the kind his answer to sample Q9 calls Any leaks in: mypy gave up on the value, and it leaked into a typed return. Writing `budgets: dict[str, float] = json.load(handle)` and returning `budgets` states what you expect the file to hold. We ran that version: `Success: no issues found in 1 source file`.",
)

# q30 ------------------------------------------------------------------------
mcq(
    30, "core", ["read-tool-output"], 9, "labs/07-refactor.md troubleshooting", "lab", "run",
    "Strict mypy on a new helper:\n\n"
    + code("python", """
from expense import Expense


def total_by_category(expenses: list[Expense]) -> dict[str, float]:
    totals = {}
    for expense in expenses:
        totals[expense.category] = totals.get(expense.category, 0.0) + expense.amount
    return totals
""")
    + "\n\n" + code("text", """
totals_bad.py:5: error: Need type annotation for "totals" (hint: "totals: dict[<type>, <type>] = ...")  [var-annotated]
""")
    + "\n\nWhich fix is right?",
    [
        opt("Write `totals = dict()` instead of `totals = {}`",
            "An empty `dict()` has no type either. We ran it: the same `Need type annotation` error."),
        opt("Delete the return type of the function",
            "The error is about the variable, not the return. Under strict, removing the return type adds a missing-annotation error."),
        opt("Write `totals: dict[str, float] = {}`",
            "An empty `{}` has no type yet, so you say what it will hold. This is the lab's fix and mypy's own hint.",
            True),
        opt("Start with a dummy entry, `totals = {\"\": 0.0}`, so mypy can see the types",
            "mypy is satisfied, but the result now contains a category called `\"\"`: the output changes."),
    ],
    "An empty dictionary tells mypy nothing about what goes in it, so strict mode asks you to say it. The message even shows the shape of the fix, `totals: dict[<type>, <type>] = ...`, and the lab's table gives the full version: `totals: dict[str, float] = {}`. We ran it: `Success`. This is the missing-annotation kind: write the hint. The dummy entry is the dangerous distractor, because it changes the behaviour to please the checker.",
)

# q31 ------------------------------------------------------------------------
mcq(
    31, "hard", ["read-tool-output", "judgement"], 9, "labs/07-refactor.md troubleshooting; S3 works on my machine", "lab", "run",
    "Your group starts reading budgets from a YAML file. CI and your laptop both show:\n\n"
    + code("text", """
src/tracker/budgets.py:1: error: Library stubs not installed for "yaml"  [import-untyped]
src/tracker/budgets.py:1: note: Hint: "python3 -m pip install types-PyYAML"
src/tracker/budgets.py:1: note: (or run "mypy --install-types" to install all missing stub packages)
src/tracker/budgets.py:1: note: See https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports
Found 1 error in 1 file (checked 2 source files)
""")
    + "\n\nWhat do you do?",
    [
        opt("`uv add --dev types-PyYAML`, so it is recorded for the team and CI",
            "The lab's fix. It adds the package to `pyproject.toml` and `uv.lock`, so `uv sync --locked` on CI installs it too.",
            True),
        opt("`python3 -m pip install types-PyYAML`, exactly as mypy's hint says",
            "Even if it lands in the right environment, nothing records it: `pyproject.toml` and `uv.lock` do not change, so CI stays red. Works on my machine."),
        opt("`uv add --dev types-yaml`, because the module is called `yaml`",
            "The stub package is not always named after the module. The message gives the exact name: `types-PyYAML`."),
        opt("Add `# type: ignore` to `import yaml`; the library works at run time",
            "Every use of `yaml` then becomes unchecked `Any`. The stubs exist precisely so those uses can be checked."),
    ],
    "The lab's row: `Library stubs not installed` → `uv add --dev types-<name>`, and \"the error message tells you the exact name\". Here the name is `types-PyYAML`, not `types-yaml`. The hint's `pip install` is generic advice from mypy; in a uv project, a package that is not in `pyproject.toml` and `uv.lock` does not exist for CI or for your teammates. That is session 3's \"works on my machine\" problem, and the reason the course standardises on uv.",
)

# q32 ------------------------------------------------------------------------
mcq(
    32, "hard", ["read-tool-output", "read-code"], 9, "labs/07-refactor.md troubleshooting; S7 slide 9", "lab", "run",
    "A teammate copied a timing decorator from a blog into `timing.py`:\n\n"
    + code("python", """
import time


def timed(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.perf_counter() - start:.3f}s")
        return result

    return wrapper
""")
    + "\n\nand used it in `report.py`:\n\n" + code("python", """
from timing import timed


@timed
def total(amounts: list[float]) -> float:
    return sum(amounts)
""")
    + "\n\n" + code("console", """
$ uv run mypy --strict .
timing.py:4: error: Function is missing a type annotation  [no-untyped-def]
timing.py:5: error: Function is missing a type annotation  [no-untyped-def]
report.py:4: error: Untyped decorator makes function "total" untyped  [untyped-decorator]
Found 3 errors in 2 files (checked 2 source files)
""")
    + "\n\nWhich change clears all three errors?",
    [
        opt("Add `# type: ignore` on the `@timed` line in `report.py`",
            "That hides only the third error, and the two missing annotations in `timing.py` stay. The decorator is still untyped."),
        opt("Remove the hints from `total`, since the decorator makes it untyped anyway",
            "Under strict, `total` would then be reported as missing annotations as well. More errors, not fewer."),
        opt("Change the return type of `total` to `Any`",
            "The problem is not `total`'s return type but the decorator wrapped around it. The decorator error remains."),
        opt("Give `timed` and `wrapper` full type hints in `timing.py`",
            "The first two errors are the cause. Typed so that it keeps the wrapped function's signature, the decorator passes `total`'s types through and the third error goes.",
            True),
    ],
    "Read the first error first. The two lines in `timing.py` say the decorator has no hints; the line in `report.py` is the consequence: a decorator without hints turns the function it wraps into an untyped one. We typed `timed` so that it keeps the wrapped function's parameters and return type, and mypy said `Success`. (Typing it with `Any` everywhere also silences the three errors, but then `total` is no longer checked at all.) When the decorator belongs to a library instead, the lab's advice is to upgrade the library, for example `uv lock --upgrade-package typer`, because newer versions ship with hints.",
)

# q33 ------------------------------------------------------------------------
mcq(
    33, "exam", ["read-code", "predict-output"], 9, "sample Q3 and Q9; labs/07-refactor.md troubleshooting", "slides", "run",
    "To get CI green, a teammate added `# type: ignore` to the last line:\n\n"
    + code("python", """
from expense import Expense


def find_expense(expenses: list[Expense], merchant: str) -> Expense | None:
    for expense in expenses:
        if expense.merchant == merchant:
            return expense
    return None


expenses = [Expense("2026-10-01", "Bar Ramon", "dining", 12.40)]
found = find_expense(expenses, "Cabify")
print(found.amount)  # type: ignore
""")
    + "\n\n" + code("console", """
$ uv run mypy --strict ignored.py
Success: no issues found in 1 source file
""")
    + "\n\nWhat happens when the program runs?",
    [
        opt("It prints `None`, because `# type: ignore` makes the attribute access safe to run",
            "The comment is read by mypy only. Python does not change what `found.amount` does."),
        opt("It crashes with `AttributeError`: the comment changes mypy's report, not Python",
            "There is no Cabify expense, so `found` is `None`, and `None.amount` fails exactly as before.",
            True),
        opt("It prints `0.0`, because mypy fills in a default for a missing value",
            "mypy never runs the program and never changes values. It only reads the code."),
        opt("It does not start: Python refuses to run a file that contains `# type: ignore`",
            "To Python it is an ordinary comment. The program starts and runs until the `None` is used."),
    ],
    "We ran it:\n\n"
    + code("text", """
Traceback (most recent call last):
  File "ignored.py", line 13, in <module>
    print(found.amount)  # type: ignore
          ^^^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'amount'
""")
    + "\n\nmypy said `Success` and the program crashed on the same line. A type checker reads code and reports what it finds; `# type: ignore` only tells it not to report. That is why it is the wrong answer to sample Q3 and to \"silence all three to get CI green\" in sample Q9: the error message goes and the crash stays.",
)

# q34 ------------------------------------------------------------------------
mcq(
    34, "beyond", ["read-tool-output", "judgement"], 9, "sample Q3; labs/07-refactor.md troubleshooting", "slides", "run",
    "To silence an `Item \"None\"` error, a teammate changed a return type from `Expense | None` to `Any`. mypy now passes, and the program fails at run time:\n\n"
    + code("python", """
from typing import Any

from expense import Expense


def find_expense(expenses: list[Expense], merchant: str) -> Any:
    for expense in expenses:
        if expense.merchant == merchant:
            return expense
    return None


expenses = [Expense("2026-10-01", "Bar Ramon", "dining", 12.40)]
found = find_expense(expenses, "Bar Ramon")
print(found.amout)
""")
    + "\n\n" + code("console", """
$ uv run mypy --strict anyfix.py
Success: no issues found in 1 source file
$ uv run python anyfix.py
AttributeError: 'Expense' object has no attribute 'amout'. Did you mean: 'amount'?
""")
    + "\n\nWhat did the change to `Any` cost?",
    [
        opt("Nothing: the crash is a typo, and a type checker cannot catch typos",
            "With the honest return type, mypy reports this typo: `Item \"Expense\" of \"Expense | None\" has no attribute \"amout\"`. We ran it."),
        opt("The crash comes from `Any` itself: a value typed `Any` has no attributes at run time",
            "Annotations do not change values when the program runs. The object is a real `Expense`; it just has no field called `amout`."),
        opt("mypy no longer checks any use of the result, so it let the `amout` typo through",
            "`Any` means \"do not check\". It silenced the `None` warning and every other mistake made with that value.",
            True),
        opt("`Any` is fine, but it must be imported from `typing` in every file that uses the result",
            "Only the file that writes `Any` imports it. The problem is what `Any` does, not where it comes from."),
    ],
    "`Any` is not a type that describes the value; it is permission for mypy to stop checking it. The teammate wanted to silence one warning (the `None` case) and silenced all of them for this value. With the return type left as `Expense | None`, strict mypy reported both problems on that line: the possible `None` and the misspelt attribute (`has no attribute \"amout\"`). This is why sample Q3's option \"change the return type to `Any`\" is wrong: it hides the real bug and any later one.",
)

# q35 sort -------------------------------------------------------------------
questions.append(
    {
        "id": q(35),
        "type": "sort",
        "level": "exam",
        "skills": ["concept", "judgement"],
        "stem_md": "Sort each change to the expense-tracker: is it a refactoring, or does it change behaviour?",
        "categories": [
            {"id": "refactor", "label": "Refactoring: behaviour kept"},
            {"id": "change", "label": "Not a refactoring: behaviour changes"},
        ],
        "items": [
            {"text_md": "Rename `x, y, z` to `expenses, category, minimum` in `total_by_category`; every test passes unedited",
             "category": "refactor",
             "why_md": "Only names changed, and tests that pass without edits are the evidence that behaviour is the same."},
            {"text_md": "Change the report's first line from `Expense report for` to `Expenses for`",
             "category": "change",
             "why_md": "It looks like a rename, but it renames printed text. The output changes."},
            {"text_md": "Replace `\"%.2f\" % amount` with `f\"{amount:.2f}\"` throughout `format_report`; the report is identical",
             "category": "refactor",
             "why_md": "Same formatting, newer syntax, identical output. `04d699f` made this change as part of the clean-up."},
            {"text_md": "Change `grand_total = 0` to `grand_total = 0.0` to satisfy mypy; an empty report still ends `TOTAL 0.00`",
             "category": "refactor",
             "why_md": "A types-disagree fix that changes nothing visible: `0` and `0.0` both format as `0.00`."},
            {"text_md": "Add a `--month` option to the `report` command",
             "category": "change",
             "why_md": "A new feature is new behaviour, the first option of sample Q2."},
            {"text_md": "Make `read_expenses` keep the last row of the file, which it used to skip",
             "category": "change",
             "why_md": "A bug fix: the totals change on purpose, which is sample Q2's option b. Good work, but not a refactoring."},
            {"text_md": "Replace the tuple `(date, merchant, category, amount)` with the `Expense` dataclass; `diff before.txt after.txt` prints nothing",
             "category": "refactor",
             "why_md": "Introduce a type (`017f926`): structure changes, and the empty diff shows the output did not."},
            {"text_md": "Store expenses in `expenses.json` instead of `expenses.csv`",
             "category": "change",
             "why_md": "The program now reads and writes a different file in a different format; sample Q2's last option."},
        ],
        "explanation_md": "The slide's test decides every item: if the output changes, it was not a refactoring. Renames, newer syntax, a type instead of a tuple and `0.0` instead of `0` change the structure while the program prints the same, and the evidence is an empty `diff` or tests that pass unedited. A new option, a bug fix, a new storage format and a changed printed label all change what the user sees. Those can be good changes; they just are not refactorings, and they need commits that say so.",
        "section_ref": s(1),
        "source_ref": "S7 slide 5; sample Q2; expense-tracker 04d699f and 017f926",
        "origin": "slides",
        "verified_by": "reasoning",
    }
)

# q36 sort -------------------------------------------------------------------
questions.append(
    {
        "id": q(36),
        "type": "sort",
        "level": "exam",
        "skills": ["read-code", "concept"],
        "stem_md": "Put each change into the refactoring move it is. The first six come from the expense-tracker and the session 6–7 slides, the last four from the invoice lab.",
        "categories": [
            {"id": "const", "label": "Extract constant"},
            {"id": "rename", "label": "Rename (replace comment with a name)"},
            {"id": "type", "label": "Introduce a parameter object / type"},
            {"id": "func", "label": "Extract function"},
            {"id": "cond", "label": "Decompose conditional"},
        ],
        "items": [
            {"text_md": "`print(\"-\" * 40)` becomes `print(\"-\" * RULE_WIDTH)`",
             "category": "const",
             "why_md": "A magic number gets a name and one place to change it (`5e9466d`)."},
            {"text_md": "`calculate_totals(x, y, z)` becomes `total_by_category(expenses, category, minimum)`",
             "category": "rename",
             "why_md": "The slide's own example of the rename move (`f3bb801`): the function now says what it returns."},
            {"text_md": "`expenses.append((row[DATE], row[MERCHANT], row[CATEGORY], float(row[AMOUNT])))` becomes `expenses.append(Expense(date=row[DATE], ..., amount=float(row[AMOUNT])))`",
             "category": "type",
             "why_md": "A tuple becomes a named type (`017f926`), so `e[3]` becomes `expense.amount`."},
            {"text_md": "Two nested `if`s on `e[2]` and `e[3]` become one named condition, `if is_wanted(expense, category, minimum):`",
             "category": "cond",
             "why_md": "The slide's before/after for decompose conditional: the rule itself gets a name."},
            {"text_md": "Two nested `if`s, `if e[2] == category:` with `if e[3] >= minimum:` inside it, become two early `continue`s that skip the unwanted rows first",
             "category": "cond",
             "why_md": "The session 7 table's own wording for this move: a nested `if` becomes guard clauses. The exceptions are dealt with first, so the main path is no longer buried."},
            {"text_md": "The loop that finds the largest expense moves out of `run()` into `largest_expense(expenses)`",
             "category": "func",
             "why_md": "The table's example of extract function: a block of a long function becomes a named function."},
            {"text_md": "`0.21` in `main.py` becomes `STANDARD_VAT_RATE = 0.21`",
             "category": "const",
             "why_md": "Lab step 2; the slide uses this very name for the move."},
            {"text_md": "`calc(c, i, d)` becomes `invoice_total(lines, tax_rate, discount_rate)`",
             "category": "rename",
             "why_md": "Lab step 1: names that remove the need for a comment, and stop tax and discount being swapped."},
            {"text_md": "`p[1] * p[2]` becomes `line.price * line.quantity`, with an `InvoiceLine` dataclass",
             "category": "type",
             "why_md": "Lab step 3: replace the tuple with a type, as with `Expense`."},
            {"text_md": "The discount part of `calc` becomes its own function, `apply_discount(amount, discount_rate)`",
             "category": "func",
             "why_md": "Lab step 4: `calc` did three jobs, and each becomes a function named for what it returns."},
        ],
        "explanation_md": "Each move fixes one kind of problem. A bare number gets a name (extract constant). A name that needed a comment gets replaced (rename). A tuple becomes a type with named fields (introduce a type). A block of a function that does several jobs becomes a function of its own (extract function). Nested `if`s become guard clauses (session 6) or a condition with a name (`is_wanted`, session 7): both are decompose conditional. The expense-tracker history from `v0.1` to `v0.2` makes four of these moves in small commits (decompose conditional is on the slides), and the invoice lab asks for the same moves in the same spirit.",
        "section_ref": s(2),
        "source_ref": "S7 slides 5–6; S6 slide 19; expense-tracker 5e9466d–017f926; labs/07-refactor.md steps 1–4",
        "origin": "slides",
        "verified_by": "source",
    }
)

# q37 sort -------------------------------------------------------------------
questions.append(
    {
        "id": q(37),
        "type": "sort",
        "level": "hard",
        "skills": ["read-tool-output"],
        "stem_md": "Each line is a real message from `mypy --strict` (file and line removed). Sort it into the kind it reports: the three of session 7 slide 10, and the fourth that the teacher's official answer to sample Q9 adds.",
        "categories": [
            {"id": "missing", "label": "Missing annotation"},
            {"id": "disagree", "label": "Types disagree"},
            {"id": "none", "label": "None not handled"},
            {"id": "leaks", "label": "Any leaks in"},
        ],
        "items": [
            {"text_md": "`Function is missing a type annotation  [no-untyped-def]`",
             "category": "missing",
             "why_md": "A function with no signature: mypy cannot tell what goes in or comes out. Write the hint."},
            {"text_md": "`Call to untyped function \"calculate_totals\" in typed context  [no-untyped-call]`",
             "category": "missing",
             "why_md": "Reported at the call, but the cause is `calculate_totals` having no signature. Annotate it and this goes."},
            {"text_md": "`Need type annotation for \"totals\" (hint: \"totals: dict[<type>, <type>] = ...\")  [var-annotated]`",
             "category": "missing",
             "why_md": "An empty `{}` has no type yet. The fix is a hint: `totals: dict[str, float] = {}`."},
            {"text_md": "`Missing type arguments for generic type \"dict\"  [type-arg]`",
             "category": "missing",
             "why_md": "The hint is incomplete: `dict` must say what it holds, `dict[str, float]`."},
            {"text_md": "`Incompatible types in assignment (expression has type \"float\", variable has type \"int\")  [assignment]`",
             "category": "disagree",
             "why_md": "\"int here, float there\": a total that started at `0`. Make them agree with `0.0`."},
            {"text_md": "`Argument 1 to \"total_by_category\" has incompatible type \"list[tuple[str, str, str, float]]\"; expected \"list[Expense]\"  [arg-type]`",
             "category": "disagree",
             "why_md": "Tuples are passed where `Expense` objects are expected. Build `Expense` values so the two agree."},
            {"text_md": "`Incompatible return value type (got \"str\", expected \"float\")  [return-value]`",
             "category": "disagree",
             "why_md": "A CSV field is a `str`; the function promised a `float`. Convert it with `float(...)`."},
            {"text_md": "`Returning Any from function declared to return \"float\"  [no-any-return]`",
             "category": "leaks",
             "why_md": "\"I gave up on this value\": the value is `Any` (from `json` or an untyped function), so mypy cannot check it. Give it a real type: convert it or annotate it. Not types disagree: no two known types clash."},
            {"text_md": "`Item \"None\" of \"Expense | None\" has no attribute \"amount\"  [union-attr]`",
             "category": "none",
             "why_md": "The value can be missing and the code uses it as if it never is. Check it, or change the type."},
            {"text_md": "`Unsupported operand types for - (\"None\" and \"float\")  [operator]`, with the note `Left operand is of type \"float | None\"`",
             "category": "none",
             "why_md": "The note shows the cause: a value of type `float | None` is used in a subtraction without checking for `None`."},
        ],
        "explanation_md": "Read the message words. \"Missing a type annotation\", \"untyped\", \"Need type annotation\" and \"Missing type arguments\" all ask \"what type is this?\": write the hint. \"Incompatible types\", \"incompatible type\" and \"Incompatible return value\" say two types that should match do not: make them agree. `Returning Any ... declared to return` says the value is already `Any`, so mypy gave up on it before it reached the return: his fourth kind, Any leaks in. `Item \"None\" of` and an operand of type `... | None` say a value can be missing: check it, or change the type. Every line here came from running mypy 2.4.0 on small snippets of expense-tracker code.",
        "section_ref": s(6),
        "source_ref": "S7 slide 10; labs/07-refactor.md troubleshooting",
        "origin": "slides",
        "verified_by": "run",
    }
)

# ---------------------------------------------------------------------------
# Open questions
# ---------------------------------------------------------------------------


def open_q(
    n: int,
    level: str,
    skills: list[str],
    sec: int,
    source_ref: str,
    origin: str,
    verified_by: str,
    stem: str,
    parts: list[dict[str, Any]],
    explanation: str,
    lines: str = "5–8",
    **extra: Any,
) -> None:
    qd: dict[str, Any] = {
        "id": q(n),
        "type": "open",
        "level": level,
        "skills": skills,
        "stem_md": stem,
        "parts": parts,
        "lines": lines,
        "explanation_md": explanation,
        "section_ref": s(sec),
        "source_ref": source_ref,
        "origin": origin,
        "verified_by": verified_by,
    }
    qd.update(extra)
    questions.append(qd)


def part(label: str, prompt: str, marks: int, model: str, rubric: list[str], weak: str) -> dict[str, Any]:
    return {
        "label": label,
        "prompt_md": prompt,
        "marks": marks,
        "model_answer_md": model,
        "rubric": rubric,
        "weak_answers_md": weak,
    }


# q38 (sample Q9 variant) ----------------------------------------------------
open_q(
    38, "exam", ["read-tool-output", "judgement"], 9, "sample Q9; S7 slides 8 and 10; labs/07-refactor.md troubleshooting", "teacher-variant", "run",
    "You run `uv run mypy src` on a teammate's branch (`strict = true` is set in `pyproject.toml`). The file, then the output:\n\n"
    + code("python", Q9_CODE)
    + "\n\n" + code("text", Q9_RUN),
    [
        part("1", "Sort the four errors into the kinds we discussed in session 7.", 2,
             "Line 29 is a missing annotation. Line 15 is types disagree: `spent = 0` is an `int` that receives floats. Line 26 is None not handled. Line 8 is Any leaks in: `json.load` returns `Any`, so mypy gave up on the value, and it leaked into a function that promised a `dict[str, float]`.",
             ["Line 29 (a parameter without a hint) → missing annotation, and line 26 (`Item \"None\" of \"str | None\"`) → None not handled",
              "Line 15 → types disagree (`spent = 0` is an `int` that receives floats), and line 8 → Any leaks in, with the reason: the `Any` from the untyped `json.load` is returned where `dict[str, float]` was promised (different wording is fine if the idea is there)"],
             "Answers that copy the error codes (`no-untyped-def`, `assignment`) without naming the kinds earn nothing for the sort. Line 8 is where students slip: it is not types disagree, because mypy never saw a clashing type, only an `Any`, and it is not a missing annotation, because the function has its hints. A bare label without the reason (the value comes from untyped `json`) earns half. Another slip is to call line 26 \"types disagree\" because a type is mentioned: the words `Item \"None\" of` mark the None kind."),
        part("2", "Which one points to a bug that could crash the program for a real user, and when?", 2,
             "Line 26. `biggest_category` returns `None` for a month with no expenses, and `headline` then calls `.upper()` on it: `AttributeError`. The other three crash nothing by themselves.",
             ["Picks line 26 (`headline`) and says it raises `AttributeError` (crashes) when `.upper()` is called on `None`",
              "Says when: `totals` is empty (no expenses, a new month, an empty file), so `biggest_category` returns `None`"],
             "Weak answers pick line 15 \"because int and float mix\": Python adds a float to an int without complaint, so it does not crash. Others pick line 26 but cannot say when it happens; \"if something is None\" earns less than \"when there are no expenses, so `totals` is empty\". The marks are for the condition a user would actually meet. A student who adds that the `Any` from line 8 lets a budgets file holding strings through, to crash later in `warn_if_over`, has seen something real, but it depends on bad data; line 26 crashes on an ordinary empty month, and that is the answer the marker wants."),
        part("3", "Your teammate proposes silencing all four with `# type: ignore` \"to get CI green\". Do you accept? Give your reasoning.", 2,
             "No. `# type: ignore` changes what mypy reports, not what Python runs: the empty-month crash would ship behind a green CI. Each real fix is one line: hint `budgets`, start `spent` at `0.0`, annotate the JSON, handle the `None`.",
             ["Refuses, because `# type: ignore` hides the report but the code still crashes: the line 26 bug ships behind a misleading green CI",
              "Gives at least one concrete real fix (handle `None` in `headline`, `0.0`, hint `budgets`, annotate the JSON)"],
             "\"No, because it is bad practice\" is a slogan without a reason and scores at most one mark. Answers that accept `# type: ignore` for \"the harmless ones\" but not line 26 are better, but still miss that each of those has a one-line real fix. Full marks need the runtime point (the crash still happens) and a concrete alternative."),
    ],
    "This is sample Q9 with a new log. The kinds come from the message words: \"missing a type annotation\" (write the hint), \"Incompatible types\" (make them agree), `Returning Any` where a type was promised (Any leaks in: give the value a real type), `Item \"None\" of` (check it, or change the type). We ran the module: `headline({})` raises `AttributeError: 'NoneType' object has no attribute 'upper'`, while `spent_in([], \"dining\")` simply returns `0`. A green CI means the referee is satisfied; `# type: ignore` only tells it to look away.",
    lines="6–8",
    variant_of="sample-paper-q09",
)

# q39 (sample Q7 shape: describe the moves) -----------------------------------
open_q(
    39, "exam", ["read-code", "judgement"], 2, "sample Q7; S7 slides 5–6; S6 slides 13–20", "teacher-variant", "run",
    "A teammate wrote this check for the group project:\n\n"
    + code("python", """
def chk(rows, b):
    t = 0
    for r in rows:
        if r[2] == "dining":
            if r[3] >= 5:
                t += r[3]
    if t > b * 1.1:
        print("WARNING: dining over budget")
        return True
    return False
""")
    + "\n\n`rows` are tuples of `(date, merchant, category, amount)`.",
    [
        part("1", "In one sentence, what does this function do?", 1,
             "It adds up the dining amounts of 5 or more and, if that total is more than 10% over the budget `b`, prints a warning and returns `True`; otherwise it returns `False`.",
             ["Says it totals dining expenses of at least 5 and compares the total with the budget plus 10% (warns and returns `True` when over)"],
             "\"It checks the budget\" restates the name and earns nothing: the marker wants the rule (dining only, amounts of 5 or more, 10% tolerance) and the two results (the warning and the `True`/`False`). Missing the 1.1 tolerance is the most common slip."),
        part("2", "Describe in words three refactoring moves you would apply, and the problem each one solves.", 3,
             "Rename `chk`, `b`, `t` and `r` (`budget`, `dining_total`), so no comment is needed. Name the constants `5`, `1.1` and `\"dining\"`. Separate I/O from logic: return the result and let the caller print, so the function can be tested without capturing output.",
             ["A rename with the problem it solves (the names say nothing / need a comment)",
              "Extract constant for a magic number (`5`, `1.1`, `\"dining\"`) with its problem (unnamed rule, changed in one place)",
              "Separate I/O from logic (move the `print` to the caller), or introduce a type (`Expense` instead of `r[2]`, `r[3]`), or decompose the nested `if` into a named condition, each with its problem"],
             "Weak answers list moves without problems (\"rename, constants, dataclass\") and lose most marks: the question asks which problem each solves. Another weak answer writes code; the exam never asks for code, so describe the change in words. \"Add comments explaining the variables\" is the opposite of the rename move."),
        part("3", "How would you show that your changes kept the behaviour?", 2,
             "Before changing anything, record what it prints and returns for a few inputs, including edges (an amount of exactly 5, a total right at the limit). Rerun after each move; a difference means undo that move. Existing tests must pass unedited.",
             ["Record the output and return value before the change, and compare after each small move (undo a move that changes it)",
              "Mentions edge inputs (an amount of exactly 5, a total right at the limit, an empty list) or tests that pass without being edited"],
             "\"Run mypy and ruff\" checks types and style, not behaviour, and earns nothing here. \"Test it at the end\" misses the point of small moves: compare after each one, so you know which move broke it. Full marks need a before/after comparison and some thought about which inputs to compare."),
    ],
    "This is sample Q7's shape applied to session 7's moves. The function has the problems the moves exist for: names that say nothing (`chk`, `b`, `t`, `r`), magic numbers (`5`, `1.1`, `\"dining\"`), tuple indexes (`r[2]`, `r[3]`), a nested `if`, and a `print` inside a calculation. We ran it on a sample with a 120.00 dining expense: with a budget of 100 it printed the warning and returned `True`; with 110 it returned `False`. Each move should be named with the problem it fixes, and the behaviour shown to be the same after each one.",
    lines="6–8",
    variant_of="sample-paper-q07",
)

# q40 (long log) -------------------------------------------------------------
open_q(
    40, "hard", ["read-tool-output", "read-code"], 5, "S7 slides 9–10; labs/07-refactor.md Part 2", "lab", "run",
    "Another file from the same group, `src/tracker/refunds.py`, and the first strict run on it:\n\n"
    + code("python", REFUNDS_CODE)
    + "\n\n" + code("console", REFUNDS_RUN),
    [
        part("1", "In what order do you work through the five lines, and which one do you fix first?", 2,
             "Top down, starting with line 12: `to_cents` has no signature. The two lines on 25 are repeats that come from it, an untyped call and an unknown `Any` result, so they should disappear once it has hints (a `float` in, an `int` out).",
             ["Starts with line 12 (annotate `to_cents`), following \"read the first error\"",
              "Says the two errors on line 25 repeat the same cause and should vanish"],
             "Starting with line 36 \"because it is the real bug\" is a reasonable instinct, but it skips the routine and the time it saves. \"Fix line 12 because it is first\" with no word on why line 25 clears earns one mark."),
        part("2", "Which two errors remain after that, of what kind, and with what fix in words?", 2,
             "Line 20 is types disagree: `total = 0` is an `int` and float amounts are added, so start it at `0.0`. Line 36 is None not handled: `first_refund` returns `None` when there is no refund, so check for it before reading `.merchant`.",
             ["Line 20: types disagree, fix by starting `total` at `0.0` (the cause is the line above)",
              "Line 36: None not handled, fix by checking for `None` before using it"],
             "Casting with `int()` on line 20 drops cents. For line 36, `# type: ignore` or `-> Any` silences mypy; neither is a fix."),
        part("3", "A teammate would add `# type: ignore` to every line that is still red, to get CI green. What do you answer, and which line could crash a user?", 2,
             "No. The ignore on line 36 would ship a crash: `refund_merchant` of a list with no refund raises `AttributeError`. Line 20 is harmless, but both should be fixed rather than hidden.",
             ["Refuses the blanket ignore, because it hides the evidence",
              "Names line 36 and the input (no refund in the list) as the crash"],
             "\"Ignore is fine when it is only a type problem\" misses that the `None` really happens. Naming the line without the input that triggers it earns one mark."),
    ],
    "Same shape as the earlier log, on a different file. We ran mypy before and after annotating `to_cents`: five errors became two, line 20 and line 36. A missing signature is reported where it is defined and again at every typed call and every return that depends on it. Of the two that remain, the `int`/`float` one never crashes, and the `None` one raises `AttributeError: 'NoneType' object has no attribute 'merchant'` for any list with no refund (we ran it).",
    lines="6–8",
)

# q41 (strict on in the repo, CI red) -----------------------------------------
open_q(
    41, "exam", ["read-diff", "read-tool-output", "judgement"], 7, "S7 slide 11; labs/07-refactor.md Part 2 and troubleshooting", "lab", "run",
    "In lab 07 Part 2 your group commits this change:\n\n"
    + code("diff", """
 [tool.mypy]
 python_version = "3.13"
-check_untyped_defs = true
+strict = true
""")
    + "\n\nBefore committing, one teammate ran `uv run mypy src` and got `Success: no issues found in 3 source files`. After the push, CI is red at the step **Types**:\n\n"
    + code("console", CI_TYPES_ONLY),
    [
        part("1", "What does the change in `pyproject.toml` do?", 1,
             "It turns on strict mode for every mypy run: every function now needs a full signature, where `check_untyped_defs` only checked the bodies of untyped functions.",
             ["Says strict now requires hints/signatures on every function (where the old setting only checked bodies and never required hints)"],
             "\"It makes mypy stricter\" restates the word. The mark is for what changed in practice: functions without annotations, tests included, are now errors. Answers that say strict \"adds the tests to the check\" confuse the setting with the command: the folders come from `mypy src tests`."),
        part("2", "Why was the teammate's check green and CI red?", 2,
             "They ran `mypy src`, which never opens `tests/`. CI runs `mypy src tests`, and under strict the two test functions without a return annotation are errors.",
             ["Names the different commands: `mypy src` locally vs `mypy src tests` on CI",
              "Says the errors are in the tests (missing `-> None`), which `mypy src` never checked"],
             "Blaming the CI machine, the mypy version or a cache misses that the same error appears locally with the CI command. \"The tests fail\" confuses mypy with pytest: these are annotation errors in test files."),
        part("3", "What do you change, and what do you not change?", 2,
             "Add `-> None` to the two test functions, as the note says, and run `uv run mypy src tests` exactly as CI does before pushing. Do not change the CI step to `mypy src` or turn strict off: the referee stays as the team agreed.",
             ["Adds `-> None` to the two tests (and runs the same command as CI before pushing)",
              "Keeps CI's command and strict mode as they are (does not weaken the referee)"],
             "Answers that make CI run `mypy src`, or put `check_untyped_defs` back, make CI green by checking less. That is the move the troubleshooting row warns against. Full marks need both the fix and the refusal to weaken CI."),
    ],
    "This is the lab's last troubleshooting row: CI red at Types, green locally, because you ran `mypy src` and CI runs `mypy src tests`. We reproduced it on a copy of the demo: with `check_untyped_defs = true` the same files passed (`Success: no issues found in 6 source files`); with `strict = true`, the two tests without `-> None` failed. Session 7's slide says it directly: every `def test_…()` needs `-> None`.",
    lines="5–7",
)

# q42 (invoice edge cases) ----------------------------------------------------
open_q(
    42, "hard", ["predict-output", "judgement"], 8, "labs/07-refactor.md edge cases", "lab", "run",
    "Before finishing the invoice lab, you run some edge cases on the original code (`calc` and `x` as given in the lab):\n\n"
    + code("python", """
from code import calc
from utils import x

print(calc([], 0.21, 0.1))
print(calc([("pencil", 10, 5)], 0.21, 1.5))
print(calc([("pencil", 10, 5)], 0.21, -0.2))
print(calc([("pencil", 10, -5)], 0.21, 0.1))
print(calc([("pencil", 0, 5)], 0.21, 0.1))
print(x([]))
""")
    + "\n\n" + code("console", """
$ uv run python edge_cases.py
0.0
-30.25
60.5
-54.45
0.0
Traceback (most recent call last):
  File "edge_cases.py", line 9, in <module>
    print(x([]))
          ~^^^^
  File "utils.py", line 5, in x
    return s/len(l)
           ~^~~~~~~
ZeroDivisionError: division by zero
"""),
    [
        part("1", "Which input crashes, and which give an answer that would surprise the person reading the invoice? Say why for each one you pick.", 2,
             "`x([])` crashes: dividing by `len(l)`, which is 0. Surprising answers: a 150% discount gives a negative invoice, `-30.25`; a discount of `-0.2` is silently ignored because of `if d>0`; a negative quantity gives `-54.45`.",
             ["`x([])` crashes with a division by zero (empty list, `len` is 0)",
              "At least two surprising results with the reason: negative total from a discount above 100%, a negative discount silently ignored by `if d>0`, a negative quantity giving a negative total"],
             "Calling the empty `calc([])` result a crash is a misreading: it returns `0.0`, which is reasonable. Listing the surprising numbers without saying why they surprise (a negative invoice, a discount that does nothing) earns half. The `-0.2` case is the one most students miss, because nothing looks wrong."),
        part("2", "The lab says to name these edge cases, but not to fix them during the refactoring. Why?", 2,
             "Fixing them changes what the code returns, so it would no longer be a refactoring. The list is for Friday, when it becomes tests that pin the intended behaviour before anyone changes the code.",
             ["Fixing changes behaviour, which a refactoring must not do",
              "The named cases become Friday's tests (testing first, then the fix)"],
             "\"Because there is no time\" misses the principle. \"Because they are not bugs\" is wrong for the crash. Full marks need the link to the definition of refactoring and to Friday's tests."),
        part("3", "Pick one surprising result and describe in words the test you would write for it on Friday.", 2,
             "For the 150% discount: a test that calls the invoice total with one line of pencils at 10 × 5 and a discount of 1.5, and expects it to be rejected (an error), instead of returning a negative total. The team has to decide the rule first.",
             ["Describes the input of the test precisely (which lines, which rate)",
              "States the expected outcome as a decision (rejected with an error, or clamped to zero), not just \"check it works\""],
             "\"Test that the discount works\" names no input and no expectation. Writing the code of the test is not asked. A strong answer notices that the expected value is a business decision: the test can only be written once the team decides what a 150% discount should do."),
    ],
    "We ran these calls on the lab's original code. Only `x([])` crashes; the others return numbers, and some of those numbers are wrong for an invoice without any warning. That is why the lab asks for both: \"every input that would break your refactored code, or give a surprising answer\". Naming them now and fixing them later keeps the refactoring honest (same output) and gives Friday's testing session its list.",
    lines="6–8",
)

# q43 (v0.1 live) --------------------------------------------------------------
open_q(
    43, "exam", ["read-tool-output", "judgement"], 6, "S7 slide 10; expense-tracker v0.1", "slides", "run",
    "Session 7's live demo on the expense-tracker at `v0.1`, run again with the course's mypy:\n\n"
    + code("console", V01_PLAIN + V01_STRICT)
    + "\n\nAfter signatures were added to `calculate_totals` and `run`, strict mode reported (notes trimmed):\n\n"
    + code("text", V01_SIGNATURES),
    [
        part("1", "Why did plain `mypy` report no problems, and why are all four `--strict` errors the same kind?", 2,
             "Without `--strict`, mypy does not look inside a function with no signature, so the untyped `report.py` was skipped. Strict refuses to skip them: it reports the two functions without signatures and the two calls to them, all missing annotations.",
             ["Plain mypy skips (does not check inside) functions with no signature",
              "All four are missing annotations: the two unannotated functions plus the two calls to them"],
             "\"Strict is stricter\" restates the question. Answers that call the four errors \"four bugs\" miss that they are one kind, and essentially two causes. The slide's sentence is the model: mypy does not look inside a function with no signature."),
        part("2", "None of these seven errors made `uv run expenses report` crash at `v0.1`: the report printed normally. Why not, and why are they still worth fixing?", 2,
             "A missing annotation changes nothing when the program runs, and Python adds floats to a total that started as the `int` `0` without complaint. They are worth fixing because, without signatures, every parameter is `Any`, so mypy cannot check what the functions do with their data: the three types-disagree errors stayed hidden for that reason.",
             ["Says neither kind crashes: hints do not run, and `int` plus `float` works in Python (the total simply becomes a float)",
              "Says why fix them anyway: without signatures mypy sees only `Any` inside the functions, so problems there (such as the three types-disagree errors) go unreported"],
             "\"Because Python is dynamic\" is a slogan: the marker wants the reason for each kind. Answers that say the `int`/`float` errors \"will crash later\" confuse types disagree with None not handled, the only kind that predicts a crash. \"Then they are not worth fixing\" misses that, until the hints are written, the referee cannot check what those functions do with their data."),
        part("3", "What is the fix for these three errors?", 1,
             "Make the types agree: start `d[e[2]]` and `grand` at `0.0` instead of `0`. That clears all three, including the return-value one.",
             ["Start the totals at `0.0` (make the types agree), not `int()` casts, `Any` or `# type: ignore`"],
             "Casting the amounts with `int()` makes the types agree by throwing away the cents, which changes the report, so it is no longer a refactoring. `Any` or `# type: ignore` hide the disagreement and leave it in the code. Only `0.0` fixes the types and keeps the behaviour."),
    ],
    "The slide reports 4 errors, all one kind, because mypy does not look inside a function with no signature, and says a second kind appears once the signatures are added. We ran it on `v0.1` with mypy 2.4.0 and got that result: four missing-annotation errors, then three types-disagree errors once the functions had signatures. Changing both zeros to `0.0` made strict mode report `Success`. The second kind was not created by the hints; it was revealed by them. Neither of these two kinds makes the program crash; only None not handled predicts a crash.",
    lines="5–7",
)

# q44 (sample Q8 shape: compare) ------------------------------------------------
open_q(
    44, "exam", ["read-diff", "compare"], 3, "sample Q8; S7 slide 6", "teacher-variant", "run",
    "A teammate shows you this change to the demo at `v0.4`:\n\n"
    + code("diff", PROJ3_DIFF)
    + "\n\nBefore and after the change, `uv run pytest -q` printed `24 passed`. Two candidate commit messages:\n\n- A: `Refactor`\n- B: `Extract is_wanted from total_by_category`",
    [
        part("1", "What does this change do?", 1,
             "It moves the rule for which expenses count (matching category, amount at least the minimum) out of the loop into its own function, `is_wanted`, and calls it from `total_by_category`, with the same results.",
             ["Says the filtering condition is moved into a named function `is_wanted` that `total_by_category` now calls, without changing results"],
             "\"It adds a function\" is too thin: the mark is for saying which logic moved (the category and minimum filter) and that the results stay the same. Answers that say it \"changes how expenses are filtered\" miss that the 24 unedited tests pass: nothing about the filtering changed."),
        part("2", "Which message is better, and why? Answer from the point of view of someone reading the history six months later.", 2,
             "B. It says what moved and where, so a reader can find the commit that created `is_wanted` and knows the behaviour should not have changed. A says only that something was restructured, somewhere.",
             ["Chooses B",
              "Reason from the later reader's view: B names what changed (the function and where it came from), A gives nothing to search or check"],
             "Choosing B \"because it is longer\" misses the reason. Answers that prefer A \"because it shows it is a refactoring\" ignore that B also implies no behaviour change, and says what was done."),
        part("3", "Name one test you can now write that was awkward before, in words.", 2,
             "A test that calls `is_wanted` with a single 10.00 dining expense, category `\"dining\"` and minimum `10.0`, and checks it returns `True`, pinning down that an amount equal to the minimum is kept.",
             ["Describes a test that calls `is_wanted` directly with one expense and specific arguments",
              "States the expected `True`/`False` and the rule it pins (edge at the minimum, empty category means all, different category is excluded)"],
             "\"Test `is_wanted`\" names no input or expectation. A test of `total_by_category` was possible before, so it does not answer \"now\". The point of the move is \"a condition with a name is a condition you can test\"."),
    ],
    "We made this change on a clone of the demo at `v0.4` and ran the 24 existing tests before and after: all passed both times, without edits, which is the evidence that it is a refactoring. It is the session 7 decompose-conditional move applied to the real `total_by_category`, and its payoff is the slide's line: a condition with a name is a condition you can test. Message B passes the six-months test: it says what was done and where.",
    lines="5–7",
    variant_of="sample-paper-q08",
)

# q45 (judging Any and type: ignore) --------------------------------------------
open_q(
    45, "hard", ["read-diff", "read-tool-output", "judgement"], 9, "sample Q3 and Q9; labs/07-refactor.md troubleshooting", "slides", "run",
    "A teammate's `src/tracker/labels.py`:\n\n"
    + code("python", PR_FILE)
    + "\n\nStrict mypy on it:\n\n"
    + code("console", PR_BEFORE)
    + "\n\nThe pull request, titled \"Fix mypy\":\n\n"
    + code("diff", PR_DIFF)
    + "\n\nAnd after it:\n\n" + code("console", PR_AFTER),
    [
        part("1", "What does each of the two changes do to mypy, and what does it do to the program when it runs?", 2,
             "`Any` tells mypy to stop checking the result of `category_of`; `# type: ignore` tells it not to report line 25. Neither changes the program: an unknown merchant still crashes `label_for`, and an empty list still crashes `largest_line`.",
             ["Says both only change what mypy reports (`Any` turns checking off for that value; `# type: ignore` silences a line)",
              "Says the runtime behaviour is unchanged: both crashes (unknown merchant, empty list) still happen"],
             "Answers that think `Any` or the ignore \"handles\" the `None` have the central misconception: annotations and comments do not run. Describing only the mypy side earns one mark; the question also asks what happens when the program runs, and the answer is that both crashes are still there."),
        part("2", "Why does a new error appear on line 14 (the `return` in `label_for`, line 12 before the import was added)?", 2,
             "`Any` spreads: `.upper()` on an `Any` value is `Any`, so the whole label built from it is `Any`, and strict mode will not let `label_for` return `Any` where it promised `str`.",
             ["Says the `Any` from `category_of` spreads into the label expression",
              "Says strict refuses to return `Any` from a function declared to return `str`"],
             "\"Because the code is wrong\" is not a reason. Saying \"mypy found a new bug\" misses that the error is a side effect of the `Any` itself: hiding one problem created another message."),
        part("3", "What would you ask the teammate to do instead?", 2,
             "Keep the honest types and handle the missing cases: decide what `label_for` shows for an unknown merchant and what `largest_line` says when there are no expenses, check for `None` there, and add a test for each case.",
             ["Keep `str | None` / `Expense | None` (remove `Any` and the ignore)",
              "Handle `None` with a decision for each case (unknown merchant, no expenses), ideally with a test for each"],
             "\"Fix the types\" is too vague. Answers that propose another silencing trick (`cast`, a broader ignore) repeat the mistake. Full marks need the two decisions: what the program does when the value is missing."),
    ],
    "We ran mypy before and after the pull request, and ran the code: `largest_line([])` still raises `AttributeError: 'NoneType' object has no attribute 'merchant'`, and `label_for([], \"Cabify\")` still raises `AttributeError: 'NoneType' object has no attribute 'upper'`. The PR moved the messages; both bugs are still there. `Any` even produced a new message, because strict mode notices when an unchecked value leaks out through a typed return. The real fix is the slide's: check it, or change the type.",
    lines="6–8",
)

# q46 (separate I/O from logic, 9d6c607) ----------------------------------------
mcq(
    46, "exam", ["read-diff", "concept"], 2,
    "S7 slide 5; S6 slide 20; expense-tracker 9d6c607; tests/test_report.py at v0.4", "history", "source",
    "Two excerpts from one commit of the expense-tracker, between `v0.1` and `v0.2`. Every other report line that the old `run()` printed became a `lines.append` in the same way.\n\n"
    + code("diff", _context_spaces("""
-    print("Expense report for " + path)
+
+def format_report(path, category, minimum, totals, largest):
+    lines = ["Expense report for " + path]
     if category != "":
-        print("category: " + category)
+        lines.append("category: " + category)
"""))
    + "\n\n"
    + code("diff", """
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
""")
    + "\n\nWhich refactoring move is this, and what does it make possible?",
    [
        opt("Extract constant: the report's fixed text now sits in one list, so each label changes in one place",
            "Nothing gets a name: the strings are the same literals, now appended to a list. Extract constant was `5e9466d`, where `40` became `RULE_WIDTH`."),
        opt("Introduce a parameter object / type: the report is now a `list[str]`, so mypy can check each line",
            "No new type is defined, and there are no hints yet (they arrive in `04d699f`). Introduce a type was `017f926`, where the tuple became `Expense`."),
        opt("Decompose conditional: `if category != \"\"` now lives inside `format_report`, so the filter can be tested alone",
            "The `if` moved with the block around it, unchanged and without a name. It only decides whether a header line appears; the filter on expenses lives in `total_by_category`."),
        opt("Separate I/O from logic: a test can call `format_report` and check the lines it returns, with no printing",
            "`format_report` takes values and returns lines; only `run()` prints. Session 6: a function that returns can be tested, a function that prints can only be looked at.",
            True),
    ],
    "This is `9d6c607`, the session 7 row \"`run()` split into read, compute, format\". Before, `run()` built the report and printed it line by line, so checking the report meant running the program and looking at the screen. After, `format_report` returns the lines and `run()` is the one place that prints them. On the sample data the printed report is identical (we ran both commits); what moved is where the printing happens. That is what makes the `v0.4` test `test_report_of_nothing_still_has_a_zero_total` possible: it calls `format_report(\"empty.csv\", \"\", 0.0, [], None)` and checks the lines it returns, with no output to capture. The same commit also pulled out `largest_expense`, the table's example of extract function.",
)

# q47 (missing type arguments for dict) -------------------------------------------
COUNTS_CODE = """
from expense import Expense


def count_by_category(expenses: list[Expense]) -> dict:
    counts: dict[str, int] = {}
    for expense in expenses:
        counts[expense.category] = counts.get(expense.category, 0) + 1
    return counts
"""

mcq(
    47, "hard", ["read-tool-output", "read-code"], 9,
    "labs/07-refactor.md troubleshooting (generic type row)", "lab", "run",
    "Strict mypy on a helper for the group project:\n\n"
    + code("python", COUNTS_CODE)
    + "\n\n" + code("text", """
counts.py:4: error: Missing type arguments for generic type "dict"  [type-arg]
""")
    + "\n\nWhich change to line 4 is right?",
    [
        opt("`-> dict[str, float]:`, the version given in the lab's troubleshooting table",
            "It copies the table without reading the function: the values are counts, so `int`. We ran it: `Incompatible return value type (got \"dict[str, int]\", expected \"dict[str, float]\")`."),
        opt("`-> dict[str, int]:`, the key and value types that `counts` already holds",
            "The message asks what the `dict` holds. `counts` is declared `dict[str, int]`, so the return type says the same. We ran it: `Success`.",
            True),
        opt("`-> Any:` (imported from `typing`), since a dictionary can hold any value",
            "mypy says `Success`, but `Any` switches off the checks on every use of the result: we ran a caller with the typo `.itmes()` and nothing was reported."),
        opt("Remove `-> dict` altogether, since mypy cannot use a bare `dict` anyway",
            "Under strict that is a new error, `Function is missing a return type annotation`, and the next reader loses the contract. We ran it."),
    ],
    "A bare `dict` says \"a dictionary\" without saying of what, and strict mode wants the contents. The lab's row gives `dict[str, float]` as its example (same for `list`, `tuple`). What matters is the shape: here the keys are category names and the values are counts, so `dict[str, int]`, which matches the `counts` variable on the next line. It is the missing-annotation kind: write the hint. We ran all four versions with mypy 2.4.0. Only `dict[str, int]` gave `Success` without switching checking off; `dict[str, float]` produced a types-disagree error, and deleting the hint produced a missing-annotation error.",
)

# ---------------------------------------------------------------------------
# Added by the calibration pass
# ---------------------------------------------------------------------------
GRADEBOOK_DIFF = """
diff --git a/src/gradebook/marks.py b/src/gradebook/marks.py
index acbc01b..56dd96f 100644
--- a/src/gradebook/marks.py
+++ b/src/gradebook/marks.py
@@ -1,6 +1,10 @@
+def is_pass(mark: float, pass_mark: float) -> bool:
+    return mark > pass_mark
+
+
 def passing_count(marks: list[float], pass_mark: float) -> int:
     count = 0
     for mark in marks:
-        if mark >= pass_mark:
+        if is_pass(mark, pass_mark):
             count += 1
     return count
"""

PRICES_CODE = r"""
import json
import os
import re


def load_prices(path: str) -> dict[str, float]:
    try:
        with open(path) as file:
            return json.load(file)
    except:
        return {}


def euros(text: str) -> float:
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    return float(match.group(1))
"""

DAILY_CODE = """
from dataclasses import dataclass


@dataclass(frozen=True)
class Expense:
    date: str
    merchant: str
    category: str
    amount: float


def total_for(expenses, day):
    return sum(e.amount for e in expenses if e.date == day)


def day_line(expenses: list[Expense], day: str) -> str:
    return f"{day}: {total_for(expenses, day):.2f}"


def busiest(expenses: list[Expense], days: list[str]) -> float:
    return max(total_for(expenses, day) for day in days)
"""

# q48 (sample Q8 variant: a commit that mixes a refactoring with a change) ----------
open_q(
    48, "hard", ["read-diff", "compare", "judgement"], 3, "S7 slides 5-6; sample Q8 shape; run in calibration-fix/q48rt", "teacher-variant", "run",
    "The gradebook group's `passing_count` counts the marks that reach the pass mark. A teammate commits this change, and the group's two tests still pass:\n\n"
    + code("diff", GRADEBOOK_DIFF)
    + "\n\n" + code("python", """
def test_counts_the_marks_at_or_above_the_pass_mark() -> None:
    assert passing_count([4.0, 6.5, 9.0], 5.0) == 2


def test_no_marks_means_no_passes() -> None:
    assert passing_count([], 5.0) == 0
""")
    + "\n\nTwo candidate commit messages:\n\n- A: `Extract is_pass`\n- B: `Extract is_pass from passing_count`",
    [
        part("1", "What does this change do to the structure of the code?", 1,
             "It moves the comparison out of the loop into a small function, `is_pass`, which the loop now calls.",
             ["Says the comparison is extracted into `is_pass` and called from the loop"],
             "\"It adds a function\" names no purpose. \"It fixes the pass mark\" misses that the structure moved."),
        part("2", "A teammate calls it a pure refactoring. Is it? What would a student with a mark of exactly 5.0 notice?", 2,
             "No. `>=` became `>`, so a mark equal to the pass mark no longer counts. The student with 5.0 passed before and fails now. Both tests stay green because neither uses a mark of exactly 5.0.",
             ["Says no, and finds the changed comparison (`>=` to `>`)",
              "Names the visible effect: a mark equal to the pass mark stops counting; the tests do not cover that mark"],
             "\"Yes, because the tests pass\" has the logic backwards: green tests only cover the inputs they use. Seeing the new function but not the changed operator misses the point of the diff."),
        part("3", "Which message is better, and what is missing from both?", 2,
             "B, because it says where the function came from. But both claim only an extraction: neither mentions that the pass mark rule changed, so the change should be split in two commits or described honestly.",
             ["Chooses B because it is more specific about what moved",
              "Says neither message mentions the changed rule (or asks for two commits)"],
             "\"B is longer\" is not a reason. Choosing A because it is shorter misses what a reader needs from a subject line."),
        part("4", "Describe in words one test that would have caught the change.", 1,
             "Call `passing_count` with a list that contains a mark equal to the pass mark, such as `[4.0, 5.0, 6.5]` with 5.0, and expect 2.",
             ["A test with a mark exactly equal to the pass mark and the expected count"],
             "\"Test more marks\" is not a test. The input has to sit on the boundary, and the answer has to say what is expected."),
    ],
    "Sample Q8's shape with a trap: a commit that looks like an extraction and also changes the rule. A refactoring keeps the behaviour, so the check from session 6 applies: `diff before.txt after.txt` on a list that includes a mark of exactly 5.0 printed `3` before and `2` after (we ran it). The green tests prove only that no test sits on the boundary, which is session 8's \"choose edge cases on purpose\".",
    lines="6–8",
    variant_of="sample-paper-q08",
)

# q49 (sample Q9 variant: ruff and mypy in one transcript, and a justified ignore) ----
open_q(
    49, "hard", ["read-tool-output", "judgement"], 9, "sample Q9; S7 slides 8-10; labs/07-refactor.md troubleshooting; run in calibration-fix/rt", "teacher-variant", "run",
    "You run both tools on a teammate's `src/tracker/prices.py` (`strict = true` is set in `pyproject.toml`). The file, then the output (ruff's code excerpts are trimmed):\n\n"
    + code("python", PRICES_CODE)
    + "\n\n" + code("console", """
$ uv run ruff check src
F401 [*] `os` imported but unused
 --> src/tracker/prices.py:2:8
E722 Do not use bare `except`
  --> src/tracker/prices.py:10:5
Found 2 errors.
[*] 1 fixable with the `--fix` option.
$ uv run mypy src
src/tracker/prices.py:9: error: Returning Any from function declared to return "dict[str, float]"  [no-any-return]
src/tracker/prices.py:16: error: Item "None" of "Match[str] | None" has no attribute "group"  [union-attr]
Found 2 errors in 1 file (checked 1 source file)
"""),
    [
        part("1", "Sort the four findings: which come from the linter as style or code-quality findings, and which kind is each mypy error?", 3,
             "`F401` and `E722` are ruff's: an unused import and a bare `except`. Line 9 is Any leaks in: `json.load` gives `Any`, mypy gave up on the value, and it leaked into a function that promised a `dict[str, float]`. Line 16 is None not handled: `re.search` can return `None`.",
             ["F401 and E722 named as ruff findings (style and code quality), not type errors",
              "Line 9: Any leaks in (`Any` returned where a typed value is promised)",
              "Line 16: None not handled"],
             "Calling all four \"type errors\" misses that ruff does not read types. Calling line 9 \"missing annotation\" confuses it with `no-untyped-def`: the function has hints; the value returned is unknown. Calling it \"types disagree\" misses his fourth kind: mypy saw no type at all."),
        part("2", "Which finding can crash a user, and with what input?", 2,
             "Line 16. `euros(\"free\")` has no digits, so `re.search` returns `None` and `.group` raises `AttributeError` (we ran it).",
             ["Line 16 (the `None` case)",
              "An input with no number in it, such as a price text of \"free\", giving an `AttributeError`"],
             "Choosing the bare `except` names a real smell but not a crash: it swallows errors silently. Naming line 16 without an input earns one mark."),
        part("3", "The teammate adds `# type: ignore[union-attr]  # None cannot happen here` to line 16. Do you accept it?", 2,
             "No. The comment is a claim that nothing checks: no test proves it, and `euros(\"free\")` crashes. Handle `None` (raise a clear error) or show a test that proves it cannot occur.",
             ["Refuses: the comment is an unchecked claim, and a counterexample exists",
              "Proposes handling `None`, or evidence in a test, instead of silencing mypy"],
             "\"Yes, because the comment explains it\" confuses a reason with a guarantee. \"No, ignores are banned\" misses the point: a justified ignore needs evidence."),
    ],
    "Sample Q9's shape with two tools. ruff reports style and simple mistakes, mypy reports what the types allow, and only one of the four findings is a crash waiting for the right input. The ignore comment is the interesting part: a reason in a comment is a claim, and the course's habit is to look for evidence in a test or in the code. We ran both tools and called `euros(\"12.50 EUR\")` (12.5) and `euros(\"free\")` (AttributeError).",
    lines="6–8",
    variant_of="sample-paper-q09",
)

# q50 (reading an error: the first one is the cause) -------------------------------
mcq(
    50, "exam", ["read-tool-output", "judgement"], 5, "S7 slides 9-10; run in calibration-fix/rt", "slides", "run",
    "A new file in the group's repository, and the first strict run on it:\n\n"
    + code("python", DAILY_CODE)
    + "\n\n" + code("console", """
$ uv run mypy --strict src
src/tracker/daily.py:12: error: Function is missing a type annotation  [no-untyped-def]
src/tracker/daily.py:17: error: Call to untyped function "total_for" in typed context  [no-untyped-call]
src/tracker/daily.py:21: error: Returning Any from function declared to return "float"  [no-any-return]
src/tracker/daily.py:21: error: Call to untyped function "total_for" in typed context  [no-untyped-call]
Found 4 errors in 1 file (checked 1 source file)
""")
    + "\n\nHow do you work through the four errors?",
    [
        opt("Fix line 21 first, because `Returning Any` is the most serious, and change the return type to `Any`",
            "`Any` would make the message go away and switch off the checking of every caller. And the `Any` comes from line 12's missing signature."),
        opt("Start at the last line and move up, since the newest errors are the ones that stopped mypy",
            "mypy reports every error it finds; it does not stop at the last one. The cause is higher up, where the function is defined."),
        opt("Give `total_for` a signature on line 12 and run mypy again; the other three should disappear",
            "Right: line 12 is the first error and the cause. Lines 17 and 21 are calls to a function mypy cannot see inside, and the `Any` on line 21 comes from its unknown result.",
            True),
        opt("Add `# type: ignore` to lines 17 and 21 first, to see which errors are real",
            "That hides evidence before reading it. Fixing the cause on line 12 shows which errors are left, at no cost."),
    ],
    "Session 7's method: read the first error, find its cause, fix it, run again. Line 12 is the cause: `total_for` has no signature. Line 17 and line 21 are calls to it from typed code, and line 21 also returns the unknown `Any` that comes out of it. With `(expenses: list[Expense], day: str) -> float` added to line 12, we ran mypy again and it printed `Success: no issues found in 1 source file`. Later errors are often the same one repeating, so one fix removes several lines.",
)

# ---------------------------------------------------------------------------
# Module
# ---------------------------------------------------------------------------

module = {
    "id": MID,
    "order": 6,
    "module": "M2",
    "title": "Refactoring and type checking with mypy",
    "sessions": [7],
    "predicted": False,
    "sources": [
        "slides-session-7 (slides 1–11, 21–23)",
        "labs/07-refactor.md",
        "midterm sample questions Q2, Q3, Q9",
        "expense-tracker 5e9466d–04d699f, 88b83c3",
    ],
    "summary_md": "Session 7 gives names to the clean-code steps of session 6 and adds a second referee. **Refactoring** means changing the structure of code while keeping its behaviour: if the output changes, it was not a refactoring. You learn the six moves (extract constant, rename, separate I/O from logic, introduce a type, extract function, decompose conditional) and where you saw each one: five in the expense-tracker history, decompose conditional on the slides. Then **mypy**: what a type checker catches that a linter cannot, how to read an error, what `--strict` reports on untyped code, the kinds of error and their fixes (three on the slide, and a fourth from the teacher's answer to sample Q9, Any leaks in), and why `strict = true` in `pyproject.toml` means every test needs `-> None`. The invoice lab puts it together, and its troubleshooting table is the vocabulary of the exam's tool-output questions.",
    "exam_focus_md": "\n".join(
        [
            "- \"Which of these changes is a refactoring?\" (sample Q2): the change with identical output and tests passing unedited; features, bug fixes and format changes are not refactorings.",
            "- A `diff` of before and after, or the lab's two numbers: did the behaviour stay the same, and for which inputs do you actually know?",
            "- A short function: name, in words, the moves you would apply and the problem each solves (sample Q7 part 3).",
            "- A mypy log (sample Q9): sort the errors into missing annotation, types disagree, None not handled and Any leaks in; say which one is a real crash and when; judge `# type: ignore`.",
            "- \"Which fix is most appropriate?\" (sample Q3): handle the `None`. `# type: ignore`, `Any` and deleting hints only silence the referee.",
            "- Long or noisy logs: read the first error, spot the lines that repeat one cause, predict what is left after one fix.",
            "- CI red at Types but green locally: compare `mypy src` with `mypy src tests`, and add `-> None` to tests rather than weaken CI.",
            "- The invoice lab: compute an output by hand, and tell the crash (`x([])`) from the surprising answers.",
        ]
    ),
    "sections": sections,
    "terms": terms_out,
    "traps": traps,
    "flashcards": cards,
    "questions": questions,
}

with OUT.open("w") as f:
    json.dump(module, f, ensure_ascii=False, indent=1)
print(f"wrote {OUT} ({len(questions)} questions, {len(cards)} cards, {len(sections)} sections)")
