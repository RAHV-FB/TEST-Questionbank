"""Generate content/history.json: the expense-tracker history, commit by commit.

Run from the study-site folder:
    uv run python content/src/history.py
Every diff, --stat, log and tool output in this file was produced by running git or the
course's tools on the demo repository, at that commit or on a copy changed for the scenario a
question describes (evidence in the scratchpad work/history and work/history-fix folders).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MID = "history"
OUT = Path(__file__).resolve().parent.parent / f"{MID}.json"


def fence(lang: str, body: str) -> str:
    """A fenced block. In diffs an empty line is a blank context line, which git prints as one space."""
    body = body.strip("\n")
    if lang == "diff":
        body = "\n".join(line if line else " " for line in body.split("\n"))
    return f"```{lang}\n{body}\n```"


def md(*parts: str) -> str:
    return "\n\n".join(p.strip("\n") for p in parts)


def sid(n: int) -> str:
    return f"{MID}-s{n}"


# --------------------------------------------------------------------------------------
# Real artefacts (copied from git / tool runs; see work/history/*.out)
# --------------------------------------------------------------------------------------

LOG_ONELINE = """
$ git log --oneline --decorate
8a8903d (HEAD -> main, tag: v0.5, origin/main, origin/HEAD) Revert "Run scripts/check.sh in CI instead of four separate steps"
416604b Add a --month option to the report command
d814ca9 Add filter_by_month and a validator for month strings
8fabdb3 Run scripts/check.sh in CI instead of four separate steps
8492f59 Add scripts/check.sh to run every check with one command
d3df52b (tag: v0.4) Use dict.fromkeys to drop duplicates in order
1e421bc Remove duplicates with a seen-set
e1b96de Add failing tests for remove_duplicates
0e05065 Run ruff, mypy and pytest on every push
f3d9870 Test reading a file and the missing-file exit code
d38d9e6 Test the pure core
88b83c3 (tag: v0.3) Add pytest and turn on strict type checking
15836e1 Move printing and exiting out of the report module
04d699f (tag: v0.2) Add type hints and make the code ruff clean
017f926 Give an expense a type instead of a tuple
9d6c607 Separate reading and printing from the calculation
f3bb801 Rename calculate_totals to total_by_category
5e9466d Replace magic numbers with named constants
89afbe1 (tag: v0.1) Add a README and the MIT licence
bc9ef3d Add an add command that writes to data/
2ecad20 Move the report into the package behind a typer CLI
a953d05 Turn the script into a uv package
c746d38 (tag: v0.0) Print the largest expense
6efdf9d Filter by category and ignore small amounts
3e0834f Add a script that totals expenses by category
"""

LOG_ONELINE_V04 = """
$ git log --oneline --decorate v0.4
d3df52b (tag: v0.4) Use dict.fromkeys to drop duplicates in order
1e421bc Remove duplicates with a seen-set
e1b96de Add failing tests for remove_duplicates
0e05065 Run ruff, mypy and pytest on every push
f3d9870 Test reading a file and the missing-file exit code
d38d9e6 Test the pure core
88b83c3 (tag: v0.3) Add pytest and turn on strict type checking
15836e1 Move printing and exiting out of the report module
04d699f (tag: v0.2) Add type hints and make the code ruff clean
017f926 Give an expense a type instead of a tuple
9d6c607 Separate reading and printing from the calculation
f3bb801 Rename calculate_totals to total_by_category
5e9466d Replace magic numbers with named constants
89afbe1 (tag: v0.1) Add a README and the MIT licence
bc9ef3d Add an add command that writes to data/
2ecad20 Move the report into the package behind a typer CLI
a953d05 Turn the script into a uv package
c746d38 (tag: v0.0) Print the largest expense
6efdf9d Filter by category and ignore small amounts
3e0834f Add a script that totals expenses by category
"""

TAG_N = """
$ git tag -n
v0.0            The messy original, before any structure
v0.1            Packaged: uv, src layout, typer CLI
v0.2            Clean code: names, responsibilities, a type for an expense
v0.3            Functional core, imperative shell, strict types
v0.4            Tested core: pytest, CI and one red-green-refactor cycle
v0.5            check.sh, a --month filter, and a second author
"""

# v0.5 (8492f59..8a8903d): every block below was copied from git or from running the tools in a
# clone checked out at the commit named (evidence in the scratchpad work/history-v05 folder).

LOG_V05 = """
$ git log --oneline v0.4..v0.5
8a8903d Revert "Run scripts/check.sh in CI instead of four separate steps"
416604b Add a --month option to the report command
d814ca9 Add filter_by_month and a validator for month strings
8fabdb3 Run scripts/check.sh in CI instead of four separate steps
8492f59 Add scripts/check.sh to run every check with one command
"""

LOG_WORKFLOW = """
$ git log --oneline -- .github/workflows/check.yml
8a8903d Revert "Run scripts/check.sh in CI instead of four separate steps"
8fabdb3 Run scripts/check.sh in CI instead of four separate steps
0e05065 Run ruff, mypy and pytest on every push
"""

DIFF_8FABDB3 = """
diff --git a/.github/workflows/check.yml b/.github/workflows/check.yml
index eb2e436..eb59e60 100644
--- a/.github/workflows/check.yml
+++ b/.github/workflows/check.yml
@@ -24,14 +24,5 @@ jobs:
       - name: Install dependencies from the lockfile
         run: uv sync --locked

-      - name: Lint
-        run: uv run ruff check .
-
-      - name: Formatting
-        run: uv run ruff format --check .
-
-      - name: Types
-        run: uv run mypy src tests
-
-      - name: Tests
-        run: uv run pytest
+      - name: Run the checks
+        run: scripts/check.sh
"""

REVERT_MSG = """
$ git log -1 --format=%B 8a8903d
Revert "Run scripts/check.sh in CI instead of four separate steps"

This reverts commit 8fabdb3a838c588819a7b7a031f5e3b0ef20d5ce.

One step called "Run the checks" hides which check failed: a red run means opening
the log to find out whether it was ruff, mypy or pytest. Separate named steps say it
in the Actions summary. scripts/check.sh stays, for running the same checks before a
push.
"""

DIFF_416604B_CLI = """
@@ -26,16 +28,22 @@ def report(
     path: str = typer.Argument("expenses.csv", help="CSV file to read."),
     category: str = typer.Option("", help="Only this category."),
     minimum: float = typer.Option(0.0, "--minimum", "--min", help="Ignore amounts below this."),
+    month: str = typer.Option("", help="Only this month, as YYYY-MM."),
 ) -> None:
+    if month != "" and not is_valid_month(month):
+        typer.echo(f"month must look like 2025-07, not {month}", err=True)
+        raise typer.Exit(2)
     try:
         expenses = read_expenses(path)
     except (OSError, ValueError):
         typer.echo(f"could not read {path}", err=True)
         raise typer.Exit(1) from None

+    if month != "":
+        expenses = filter_by_month(expenses, month)
     totals = total_by_category(expenses, category, minimum)
     largest = largest_expense(expenses)
-    for line in format_report(path, category, minimum, totals, largest):
+    for line in format_report(path, category, minimum, totals, largest, month):
         typer.echo(line)
"""

RUN_LARGEST = """
$ uv run expenses report --month 2025-09 | tail -2
Largest single expense:
Abacus (education) on 2025-09-15 for 239.63
$ uv run expenses report --category dining --min 20 | tail -2
Largest single expense:
Ferreteria Mas (home) on 2025-11-17 for 296.49
"""

RUN_BAD_MONTH = """
$ uv run expenses report nosuch.csv --month 2025-13
month must look like 2025-07, not 2025-13
$ echo $?
2
"""

DIFF_6EFDF9D_H1 = """
diff --git a/tracker.py b/tracker.py
index 9c0e9dc..4f20aac 100644
--- a/tracker.py
+++ b/tracker.py
@@ -2,9 +2,13 @@ import sys
 import csv


-def calculate_totals(x):
+def calculate_totals(x, y, z):
     d = {}
     for e in x:
+        if y != "" and e[2] != y:
+            continue
+        if e[3] < z:
+            continue
         if e[2] not in d:
             d[e[2]] = 0
         d[e[2]] = d[e[2]] + e[3]
"""

DIFF_6EFDF9D_NAME = """
@@ -2,9 +2,13 @@ import sys
 import csv


-def calculate_totals(x):
+def calculate_totals(x, y, z):
     d = {}
     for e in x:
+        if y != "" and e[2] != y:
+            continue
+        if e[3] < z:
+            continue
         if e[2] not in d:
             d[e[2]] = 0
         d[e[2]] = d[e[2]] + e[3]
@@ -46,4 +54,10 @@ if __name__ == "__main__":
     path = "expenses.csv"
     if len(sys.argv) > 1:
         path = sys.argv[1]
-    run(path)
+    cat = ""
+    if len(sys.argv) > 2:
+        cat = sys.argv[2]
+    minimum = 0.0
+    if len(sys.argv) > 3:
+        minimum = float(sys.argv[3])
+    run(path, cat, minimum)
"""

DIFF_6EFDF9D_OPEN = """
--- a/tracker.py
+++ b/tracker.py
@@ -2,9 +2,13 @@ import sys
 import csv


-def calculate_totals(x):
+def calculate_totals(x, y, z):
     d = {}
     for e in x:
+        if y != "" and e[2] != y:
+            continue
+        if e[3] < z:
+            continue
         if e[2] not in d:
             d[e[2]] = 0
         d[e[2]] = d[e[2]] + e[3]
@@ -31,9 +35,13 @@ def run(path):
         sys.exit(1)

     print("Expense report for " + path)
+    if cat != "":
+        print("category: " + cat)
+    if minimum > 0.0:
+        print("only amounts of " + ("%.2f" % minimum) + " or more")
     print("-" * 40)

-    totals = calculate_totals(rows)
+    totals = calculate_totals(rows, cat, minimum)
     grand = 0
     for t in totals:
         print(t[0].ljust(20) + ("%.2f" % t[1]).rjust(10))
"""

DIFF_5E9466D_ROW = """
@@ -26,9 +36,8 @@ def run(path, cat, minimum):
         reader = csv.reader(f)
         next(reader)
         for row in reader:
-            # skip rows that do not have all four fields
-            if len(row) == 4:
-                rows.append((row[0], row[1], row[2], float(row[3])))
+            if len(row) == FIELDS_PER_ROW:
+                rows.append((row[DATE], row[MERCHANT], row[CATEGORY], float(row[AMOUNT])))
         f.close()
     except:
         print("could not read " + path)
"""

DIFF_0E05065_NEW = """
diff --git a/.github/workflows/check.yml b/.github/workflows/check.yml
new file mode 100644
index 0000000..eb2e436
--- /dev/null
+++ b/.github/workflows/check.yml
@@ -0,0 +1,37 @@
+name: check
+
+on:
+  push:
+  pull_request:
"""

DIFF_0E05065_STEPS = """
--- /dev/null
+++ b/.github/workflows/check.yml
+name: check
+
+on:
+  push:
+  pull_request:
...
+      - name: Install dependencies from the lockfile
+        run: uv sync --locked
+
+      - name: Lint
+        run: uv run ruff check .
+
+      - name: Formatting
+        run: uv run ruff format --check .
+
+      - name: Types
+        run: uv run mypy src tests
+
+      - name: Tests
+        run: uv run pytest
"""

DIFF_9D6C607_RUN = """
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
"""

DIFF_15836E1_CLI = """
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
"""

DIFF_15836E1_REPORT = """
diff --git a/src/expense_tracker/report.py b/src/expense_tracker/report.py
index 94ea535..a96299b 100644
--- a/src/expense_tracker/report.py
+++ b/src/expense_tracker/report.py
@@ -1,5 +1,4 @@
 import csv
-import sys
 from dataclasses import dataclass

 DATE = 0
@@ -90,16 +89,3 @@ def format_report(
             f"{largest.merchant} ({largest.category}) on {largest.date} for {largest.amount:.2f}"
         )
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
"""

DIFF_BC9EF3D = """
diff --git a/.gitignore b/.gitignore
index 3ddf7e0..8c91599 100644
--- a/.gitignore
+++ b/.gitignore
@@ -4,3 +4,4 @@ __pycache__/
 .ruff_cache/
 .mypy_cache/
 .pytest_cache/
+data/
diff --git a/src/expense_tracker/cli.py b/src/expense_tracker/cli.py
index bb3449a..017e6b0 100644
--- a/src/expense_tracker/cli.py
+++ b/src/expense_tracker/cli.py
@@ -17,3 +21,24 @@ def report(
     minimum: float = typer.Option(0.0, "--minimum", "--min", help="Ignore amounts below this."),
 ) -> None:
     run(path, category, minimum)
+
+
+@app.command()
+def add(
+    merchant: str,
+    category: str,
+    amount: float,
+    date: str = typer.Option("", help="YYYY-MM-DD, defaults to today."),
+) -> None:
+    if date == "":
+        date = datetime.date.today().isoformat()
+    if not os.path.exists("data"):
+        os.makedirs("data")
+    exists = os.path.exists("data/expenses.csv")
+    f = open("data/expenses.csv", "a", newline="")
+    writer = csv.writer(f)
+    if not exists:
+        writer.writerow(["date", "merchant", "category", "amount"])
+    writer.writerow([date, merchant, category, "%.2f" % amount])
+    f.close()
+    print("added " + merchant + " (" + category + ") " + ("%.2f" % amount) + " to data/expenses.csv")
"""

DIFF_2ECAD20_SCRIPTS = """
@@ -7,10 +7,12 @@ authors = [
     { name = "Alberto Camara", email = "camara@protonmail.com" }
 ]
 requires-python = ">=3.13"
-dependencies = []
+dependencies = [
+    "typer>=0.12",
+]

 [project.scripts]
-expense-tracker = "expense_tracker:main"
+expenses = "expense_tracker.cli:app"

 [build-system]
 requires = ["hatchling"]
"""

DIFF_88B83C3 = """
diff --git a/pyproject.toml b/pyproject.toml
index 540b84b..15ad5eb 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -22,6 +22,8 @@ build-backend = "hatchling.build"

 [dependency-groups]
 dev = [
+    "mypy>=1.11",
+    "pytest>=8",
     "ruff>=0.6",
 ]

@@ -30,3 +32,10 @@ line-length = 100

 [tool.ruff.lint]
 select = ["E", "F", "I", "UP", "B", "SIM"]
+
+[tool.mypy]
+python_version = "3.13"
+strict = true
+
+[tool.pytest.ini_options]
+testpaths = ["tests"]
"""

DIFF_1E421BC = """
@@ -92,4 +92,10 @@ def format_report(


 def remove_duplicates(expenses: list[Expense]) -> list[Expense]:
-    return expenses
+    seen: set[Expense] = set()
+    unique: list[Expense] = []
+    for expense in expenses:
+        if expense not in seen:
+            seen.add(expense)
+            unique.append(expense)
+    return unique
"""

DIFF_D3DF52B = """
@@ -92,10 +92,4 @@ def format_report(


 def remove_duplicates(expenses: list[Expense]) -> list[Expense]:
-    seen: set[Expense] = set()
-    unique: list[Expense] = []
-    for expense in expenses:
-        if expense not in seen:
-            seen.add(expense)
-            unique.append(expense)
-    return unique
+    return list(dict.fromkeys(expenses))
"""

DIFF_E1B96DE_STUB = """
@@ -89,3 +89,7 @@ def format_report(
             f"{largest.merchant} ({largest.category}) on {largest.date} for {largest.amount:.2f}"
         )
     return lines
+
+
+def remove_duplicates(expenses: list[Expense]) -> list[Expense]:
+    return expenses
"""

STAT_A953D05 = """
$ git show --stat --format='%h %s' a953d05
a953d05 Turn the script into a uv package

 .gitignore                      |  6 ++++++
 .python-version                 |  1 +
 README.md                       |  0
 pyproject.toml                  | 17 +++++++++++++++++
 src/expense_tracker/__init__.py |  2 ++
 uv.lock                         |  8 ++++++++
 6 files changed, 34 insertions(+)
"""

STAT_A953D05_PLAIN = """
 .gitignore                      |  6 ++++++
 .python-version                 |  1 +
 README.md                       |  0
 pyproject.toml                  | 17 +++++++++++++++++
 src/expense_tracker/__init__.py |  2 ++
 uv.lock                         |  8 ++++++++
 6 files changed, 34 insertions(+)
"""

STAT_2ECAD20 = """
$ git show --stat --format='%h %s' 2ecad20
2ecad20 Move the report into the package behind a typer CLI

 pyproject.toml                              |  6 +-
 src/expense_tracker/__init__.py             |  2 -
 src/expense_tracker/cli.py                  | 19 ++++++
 tracker.py => src/expense_tracker/report.py | 13 -----
 uv.lock                                     | 91 +++++++++++++++++++++++++++++
 5 files changed, 114 insertions(+), 17 deletions(-)
"""

STAT_88B83C3 = """
$ git show --stat --format='%h %s' 88b83c3
88b83c3 Add pytest and turn on strict type checking

 pyproject.toml |   9 ++
 uv.lock        | 280 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++-
 2 files changed, 288 insertions(+), 1 deletion(-)
"""

STAT_V01_V02 = """
$ git diff --stat v0.1 v0.2
 pyproject.toml                |  11 ++++
 src/expense_tracker/cli.py    |  22 +++----
 src/expense_tracker/report.py | 150 +++++++++++++++++++++++++++---------------
 uv.lock                       |  33 ++++++++++
 4 files changed, 152 insertions(+), 64 deletions(-)
"""

STAT_V03_V04 = """
$ git diff --stat v0.3 v0.4
 .github/workflows/check.yml   |  37 ++++++++++++++
 src/expense_tracker/report.py |   4 ++
 tests/test_duplicates.py      |  26 ++++++++++
 tests/test_io.py              |  29 +++++++++++
 tests/test_report.py          | 113 ++++++++++++++++++++++++++++++++++++++++++
 5 files changed, 209 insertions(+)
"""

LOG_V03_V04 = """
$ git log --oneline v0.3..v0.4
d3df52b Use dict.fromkeys to drop duplicates in order
1e421bc Remove duplicates with a seen-set
e1b96de Add failing tests for remove_duplicates
0e05065 Run ruff, mypy and pytest on every push
f3d9870 Test reading a file and the missing-file exit code
d38d9e6 Test the pure core
"""

LOG_V00_V03 = """
$ git log --oneline v0.0..v0.3
88b83c3 Add pytest and turn on strict type checking
15836e1 Move printing and exiting out of the report module
04d699f Add type hints and make the code ruff clean
017f926 Give an expense a type instead of a tuple
9d6c607 Separate reading and printing from the calculation
f3bb801 Rename calculate_totals to total_by_category
5e9466d Replace magic numbers with named constants
89afbe1 Add a README and the MIT licence
bc9ef3d Add an add command that writes to data/
2ecad20 Move the report into the package behind a typer CLI
a953d05 Turn the script into a uv package
"""

REPORT_DINING = """
Expense report for expenses.csv
category: dining
only amounts of 20.00 or more
----------------------------------------
dining                 3157.92
----------------------------------------
TOTAL                  3157.92

Largest single expense:
Ferreteria Mas (home) on 2025-11-17 for 296.49
"""

REFUND_RUN = """
$ uv run expenses report refund.csv
Expense report for refund.csv
----------------------------------------
----------------------------------------
TOTAL                     0.00

Largest single expense:
Zara (clothing) on 2025-08-02 for -35.00
"""

MYPY_017F926 = """
$ uv run --with mypy mypy --strict src
src/expense_tracker/report.py:24: error: Function is missing a type annotation  [no-untyped-def]
src/expense_tracker/report.py:42: error: Function is missing a type annotation  [no-untyped-def]
src/expense_tracker/report.py:59: error: Function is missing a type annotation  [no-untyped-def]
src/expense_tracker/report.py:67: error: Function is missing a type annotation  [no-untyped-def]
src/expense_tracker/report.py:97: error: Function is missing a type annotation  [no-untyped-def]
src/expense_tracker/report.py:99: error: Call to untyped function "read_expenses" in typed context  [no-untyped-call]
src/expense_tracker/report.py:104: error: Call to untyped function "total_by_category" in typed context  [no-untyped-call]
src/expense_tracker/report.py:105: error: Call to untyped function "largest_expense" in typed context  [no-untyped-call]
src/expense_tracker/report.py:106: error: Call to untyped function "format_report" in typed context  [no-untyped-call]
src/expense_tracker/cli.py:23: error: Call to untyped function "run" in typed context  [no-untyped-call]
Found 10 errors in 2 files (checked 3 source files)
"""

RUFF_E501 = """
$ uv run ruff check .
E501 Line too long (115 > 100)
  --> src/expense_tracker/report.py:23:101
Found 1 error.
"""

DIFF_F3D9870 = """
diff --git a/tests/test_io.py b/tests/test_io.py
new file mode 100644
index 0000000..84f0bc4
--- /dev/null
+++ b/tests/test_io.py
@@ -0,0 +1,29 @@
+from pathlib import Path
+
+from typer.testing import CliRunner
+
+from expense_tracker.cli import app
+from expense_tracker.report import read_expenses
+
+runner = CliRunner()
+
+
+def test_rows_that_are_not_four_fields_are_skipped(tmp_path: Path) -> None:
+    csv_file = tmp_path / "expenses.csv"
+    csv_file.write_text(
+        "date,merchant,category,amount\n"
+        "2025-07-01,Bar Ramon,dining,10.00\n"
+        "broken\n"
+        "2025-07-02,Zara,clothing,40.00\n"
+    )
+
+    merchants = [expense.merchant for expense in read_expenses(str(csv_file))]
+
+    assert merchants == ["Bar Ramon", "Zara"]
+
+
+def test_report_on_a_missing_file_exits_with_one_and_explains_on_stderr() -> None:
+    result = runner.invoke(app, ["report", "nosuch.csv"])
+
+    assert result.exit_code == 1
+    assert "could not read nosuch.csv" in result.stderr
"""

DIFF_NOISY_WIDTH = """
diff --git a/src/expense_tracker/report.py b/src/expense_tracker/report.py
index 58aaec4..4f4446a 100644
--- a/src/expense_tracker/report.py
+++ b/src/expense_tracker/report.py
@@ -1,14 +1,14 @@
 import csv
 from dataclasses import dataclass
 
-DATE = 0
-MERCHANT = 1
-CATEGORY = 2
 AMOUNT = 3
+CATEGORY = 2
+DATE = 0
 FIELDS_PER_ROW = 4
+MERCHANT = 1
 
-NAME_WIDTH = 20
 AMOUNT_WIDTH = 10
+NAME_WIDTH = 24
 RULE_WIDTH = 40
 
 
"""

MYPY_V01 = """
$ uv run --with mypy mypy --strict src
src/expense_tracker/report.py:5: error: Function is missing a type annotation  [no-untyped-def]
src/expense_tracker/report.py:22: error: Function is missing a type annotation  [no-untyped-def]
src/expense_tracker/report.py:44: error: Call to untyped function "calculate_totals" in typed context  [no-untyped-call]
src/expense_tracker/cli.py:23: error: Call to untyped function "run" in typed context  [no-untyped-call]
Found 4 errors in 2 files (checked 3 source files)
"""

PYTEST_E1B96DE = """
$ uv run pytest -q
..F.F...................                                                 [100%]
=================================== FAILURES ===================================
__________ test_an_exact_duplicate_is_removed_and_the_first_one_kept ___________

    def test_an_exact_duplicate_is_removed_and_the_first_one_kept() -> None:
>       assert remove_duplicates([BAR, ZARA, BAR]) == [BAR, ZARA]
E       AssertionError: assert [Expense(date... amount=10.0)] == [Expense(date... amount=40.0)]
E
E         Left contains one more item: Expense(date='2025-07-01', merchant='Bar Ramon', category='dining', amount=10.0)
E         Use -v to get more diff

tests/test_duplicates.py:16: AssertionError
_______________ test_many_copies_of_one_expense_collapse_to_one ________________
...
=========================== short test summary info ============================
FAILED tests/test_duplicates.py::test_an_exact_duplicate_is_removed_and_the_first_one_kept
FAILED tests/test_duplicates.py::test_many_copies_of_one_expense_collapse_to_one
2 failed, 22 passed in 0.05s
"""

PYTEST_E1B96DE_SHORT = """
$ uv run pytest -q
..F.F...................                                                 [100%]
...
FAILED tests/test_duplicates.py::test_an_exact_duplicate_is_removed_and_the_first_one_kept
FAILED tests/test_duplicates.py::test_many_copies_of_one_expense_collapse_to_one
2 failed, 22 passed in 0.05s
"""

FROZEN_RUN = """
$ uv run ruff check .
All checks passed!
$ uv run mypy src tests
Success: no issues found in 6 source files
$ uv run pytest -q
...
    def remove_duplicates(expenses: list[Expense]) -> list[Expense]:
>       return list(dict.fromkeys(expenses))
                    ^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: unhashable type: 'Expense'
...
FAILED tests/test_duplicates.py::test_expenses_without_duplicates_are_unchanged
FAILED tests/test_duplicates.py::test_an_exact_duplicate_is_removed_and_the_first_one_kept
FAILED tests/test_duplicates.py::test_same_merchant_on_another_day_is_not_a_duplicate
FAILED tests/test_duplicates.py::test_many_copies_of_one_expense_collapse_to_one
4 failed, 20 passed in 0.06s
"""

RUFF_017F926 = """
$ uv run ruff check --output-format concise src
src/expense_tracker/cli.py:38:9: SIM115 Use a context manager for opening files
src/expense_tracker/cli.py:42:48: UP031 Use format specifiers instead of percent format
src/expense_tracker/cli.py:44:59: UP031 Use format specifiers instead of percent format
src/expense_tracker/cli.py:44:101: E501 Line too long (101 > 100)
src/expense_tracker/report.py:1:1: I001 [*] Import block is un-sorted or un-formatted
src/expense_tracker/report.py:72:44: UP031 Use format specifiers instead of percent format
src/expense_tracker/report.py:77:48: UP031 Use format specifiers instead of percent format
src/expense_tracker/report.py:80:47: UP031 Use format specifiers instead of percent format
src/expense_tracker/report.py:92:16: UP031 Use format specifiers instead of percent format
src/expense_tracker/report.py:100:5: E722 Do not use bare `except`
Found 10 errors.
[*] 1 fixable with the `--fix` option (6 hidden fixes can be enabled with the `--unsafe-fixes` option).
"""

UV_LOCKED = """
$ uv sync --locked
Resolved 20 packages in 5ms
error: The lockfile at `uv.lock` needs to be updated, but `--locked` was provided.

hint: To update the lockfile, run `uv lock`.
"""

SPAWN_2ECAD20 = """
$ uv run expense-tracker
error: Failed to spawn: `expense-tracker`
  cause: No such file or directory (os error 2)
"""

TRANSCRIPT_04D699F = """
$ uv run expenses report nosuch.csv > out.txt 2> err.txt
$ echo $?
1
$ cat out.txt
could not read nosuch.csv
$ cat err.txt
"""

TRANSCRIPT_15836E1 = """
$ uv run expenses report nosuch.csv > out.txt 2> err.txt
$ echo $?
1
$ cat out.txt
$ cat err.txt
could not read nosuch.csv
"""

STDERR_TEST_ON_V02 = """
$ uv run pytest -q tests/test_io.py
.F                                                                       [100%]
...
>       assert "could not read nosuch.csv" in result.stderr
E       AssertionError: assert 'could not read nosuch.csv' in ''
E        +  where '' = <Result SystemExit(1)>.stderr
...
1 failed, 1 passed in 0.04s
"""

TYPO_RUN = """
$ python tracker.py
could not read expenses.csv
$ echo $?
1
"""

V00_ARGS_BLOCK = """
if __name__ == "__main__":
    path = "expenses.csv"
    if len(sys.argv) > 1:
        path = sys.argv[1]
    cat = ""
    if len(sys.argv) > 2:
        cat = sys.argv[2]
    minimum = 0.0
    if len(sys.argv) > 3:
        minimum = float(sys.argv[3])
    run(path, cat, minimum)
"""

V00_CALC = """
def calculate_totals(x, y, z):
    d = {}
    for e in x:
        if y != "" and e[2] != y:
            continue
        if e[3] < z:
            continue
        if e[2] not in d:
            d[e[2]] = 0
        d[e[2]] = d[e[2]] + e[3]
    r = []
    for k in d:
        r.append((k, d[k]))
    r.sort(key=lambda t: -t[1])
    return r


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
"""

V00_TRY = """
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
"""

LARGEST_BEFORE = """
    largest_amount = 0.0
    largest = None
    for expense in expenses:
        if expense[AMOUNT] > largest_amount:
            largest_amount = expense[AMOUNT]
            largest = expense
"""

LARGEST_AFTER = """
def largest_expense(expenses):
    largest = None
    for expense in expenses:
        if largest is None or expense[AMOUNT] > largest[AMOUNT]:
            largest = expense
    return largest
"""

V00_RUN_END = """
    totals = calculate_totals(rows, cat, minimum)
    grand = 0
    for t in totals:
        print(t[0].ljust(20) + ("%.2f" % t[1]).rjust(10))
        grand = grand + t[1]
    print("-" * 40)
    print("TOTAL".ljust(20) + ("%.2f" % grand).rjust(10))

    m = 0.0
    mr = None
    for e in rows:
        if e[3] > m:
            m = e[3]
            mr = e
    if mr is not None:
        print("")
        print("Largest single expense:")
        print(mr[1] + " (" + mr[2] + ") on " + mr[0] + " for " + ("%.2f" % mr[3]))
"""

LOG_TAG_OLDER = """
$ git log --oneline --decorate
37b40e6 (HEAD -> main, origin/main) Fix the failing check
cb5fbf4 (tag: v0.5) Add tests for the pricing bands
0add05d Add a report command for parking tickets
"""

# --------------------------------------------------------------------------------------
# Sections
# --------------------------------------------------------------------------------------

S1_BODY = md(
    """
The teacher's advice for the mid-term is short: "Prepare with the session slides and the expense-tracker history on GitHub." The demo project was built in 25 commits between 9 February and 30 April 2026, and six tags mark the places the sessions stop. Session 4 showed the step from script to project, session 6 replayed the five clean-code commits, session 7 ran `mypy --strict` on v0.1 and moved the I/O out for v0.3, session 8 ran one test-first cycle live, from v0.3 to v0.4, and session 10 wrote `scripts/check.sh` together, the file that v0.5 contains.

A **commit** is a saved snapshot of the whole project plus a message saying what changed. Its **hash** identifies it; `git log --oneline` shows the first seven characters and the first line of the message, newest first. A **tag** is a permanent name for one commit: `(tag: v0.2)` next to `04d699f` means "v0.2 is this snapshot". `HEAD -> main` marks the commit you have checked out, on the branch `main`; `origin/main` is where GitHub's copy of `main` points.
""",
    fence("console", LOG_ONELINE),
    """
| Tag | Commits | What it marks | Sessions |
|---|---|---|---|
| `v0.0` | 3 | The messy script, run with `python tracker.py` | 4 |
| `v0.1` | 4 more | Packaged: uv, `src/` layout, typer CLI, `add`, README and licence | 4, 5 |
| `v0.2` | 5 more | Clean code: names, responsibilities, a type for an expense | 6, 7 |
| `v0.3` | 2 more | Functional core, imperative shell, strict types | 7, 8 |
| `v0.4` | 6 more | Tests, CI and one red-green-refactor cycle | 8 |
| `v0.5` | 5 more | `scripts/check.sh`, a CI change and its revert, a `--month` filter | 10 |

To look around: `git show 5e9466d` prints one commit's message and diff; `git checkout v0.1` puts every file back as it was at that tag (then `uv sync` and run it); `git checkout main` brings you back.

Read every commit by asking two questions. First, what kind of change is it? Session 1 named bugs, features and refactoring; the project's own plumbing adds the rest. A **feature** gives the user new behaviour; a **refactor** changes the structure and keeps the behaviour ("if the output changes, it was not a refactoring"); a **test** commit adds tests; **build** changes packaging or tool settings; **ci** changes the automated check; **docs** changes only documentation; a **fix** repairs a bug. Second, what did it make possible for the next commit? The history is a chain: each step is small, and each one makes the next one easy.
""",
)

S2_BODY = md(
    """
A diff shows what one commit changed, file by file. `git show 6efdf9d` prints the message and then, for each file, a header and one or more **hunks**:
""",
    fence("diff", DIFF_6EFDF9D_H1),
    """
Read it from the top. The first two lines (`diff --git ...` and `index ...`) only name the file and the two stored versions; skip them. `new file mode` or `deleted file mode` says the same as `/dev/null` below.

- `--- a/tracker.py` is the file before the commit and `+++ b/tracker.py` the file after it. A new file has `--- /dev/null`, meaning nothing was there before; a deleted file has `+++ /dev/null`.
- `@@ -2,9 +2,13 @@` opens a hunk. In the old file it covers 9 lines starting at line 2; in the new file, 13 lines starting at line 2. The text after the second `@@` (`import sys`) is only a signpost: a line from above the hunk, often the enclosing `def`, to help you find your place.
- Lines starting with a space are **context**: unchanged, shown for orientation. Lines starting with `-` were removed and lines starting with `+` were added. A changed line appears as a `-` line followed by a `+` line, as `calculate_totals` does here.

So this hunk removes one line and adds five: the new signature and two guard clauses. 9 old lines, minus 1, plus 5, gives the 13 new ones.

In the exam a diff may be trimmed to a few `-`, `+` and context lines with no headers, as in sample question 8. Read it the same way.

A **`--stat`** is the summary you read first. `git show --stat` and `git diff --stat` print one line per file, then the totals. Here is a953d05, the commit session 4 showed:
""",
    fence("text", STAT_A953D05_PLAIN),
    """
The number is how many lines changed in that file and the bar shows the share of `+` and `-`. `README.md | 0` is a file created empty. A move prints `old => new`: in 2ecad20, `tracker.py => src/expense_tracker/report.py | 13 -----` means the file moved into the package and lost 13 lines on the way. The last line counts files, insertions and deletions.

Read the `--stat` before the code. It already tells you a lot: a953d05 does not touch `tracker.py` at all, so whatever it did, it did not change how the report is computed.
""",
)

S3_BODY = md(
    """
The project starts as one file, `tracker.py`, next to `expenses.csv` (a header and 420 expenses). Session 4 calls this a script: it runs with `python tracker.py` and has "no name, no version, no dependencies, no home for tests. Fine for a weekend project."

- `3e0834f` *Add a script that totals expenses by category*: `calculate_totals(x)` adds up `e[3]` for each `e[2]` and sorts the totals largest first; `run(path)` reads the file and prints the report.
- `6efdf9d` *Filter by category and ignore small amounts*: two guard clauses skip rows of another category or below a minimum; the second and third arguments after the script name (`sys.argv[2]` and `sys.argv[3]`) become the filters.
- `c746d38` *Print the largest expense*: a loop with `m` and `mr` finds the biggest amount and prints it. Tagged `v0.0`.

This is the heart of the script at v0.0:
""",
    fence("python", V00_CALC),
    """
It works. On the sample data it prints exactly the report the project still prints at v0.4:
""",
    fence("console", "$ python tracker.py expenses.csv dining 20\n" + REPORT_DINING.strip("\n")),
    """
The problems are the ones later sessions name. `x`, `y`, `z`, `d`, `e`, `r`, `m`, `mr` say nothing. `e[3]` is a magic index into a tuple: "a tuple is a missing type". Session 6 counts five jobs in `run()`: it opens and parses the file, handles the failure, prints the header, totals by category, and finds and prints the largest. The bare `except:` turns every error, a typo included, into "could not read". The interface is positional, so to filter only by amount you must type an empty category: `python tracker.py expenses.csv "" 20`.

Look at the last line of the report too. A dining-only report names a home expense as the largest, because the loop in `c746d38` runs over all rows, not the filtered ones. Every later commit keeps that behaviour, which is exactly what refactoring is supposed to do.

What was good from day one is the history itself: three small commits, each with a message that says what the program can now do.
""",
)

S4_BODY = md(
    """
Four commits turn the script into a project. Session 4's slide on a953d05 says it in a line: "`uv init --package`, and one edit". No code changed; the code became installable.

- `a953d05` *Turn the script into a uv package* adds `pyproject.toml` (identity, what it needs, what it installs as a command, how it is built), `uv.lock` (exact versions, committed), `.python-version`, `.gitignore`, an empty `README.md` and `src/expense_tracker/__init__.py`, whose two lines print `Hello from expense-tracker!`. `tracker.py` is not in the `--stat`: the report still ran as a script.
- `2ecad20` *Move the report into the package behind a typer CLI* moves `tracker.py` to `src/expense_tracker/report.py` and deletes its `sys.argv` block (13 lines with the blank lines above it). A new `cli.py` defines the `report` command, and `[project.scripts]` now reads `expenses = "expense_tracker.cli:app"`: the command `expenses` resolves to module `expense_tracker.cli`, object `app`. typer reads the signature as the specification: `path` stays positional through `typer.Argument("expenses.csv")`, while `category` and `minimum` have defaults, so they become the options `--category` and `--minimum` (or `--min`). An empty `@app.callback()` keeps the word `report` in `expenses report`.
- `bc9ef3d` *Add an add command that writes to data/*: `merchant`, `category` and `amount` have no default, so they are arguments; `--date` is an option that defaults to today. New rows go to `data/expenses.csv`, and `data/` goes into `.gitignore`: the sample file is never modified and personal spending never reaches the public repository. The order matters: once a file is committed and pushed, deleting it in a later commit does not remove it from the history. As the project brief puts it, "I deleted the file" does not remove it from a repository's history.
- `89afbe1` *Add a README and the MIT licence*: what it does, how to install and run it, the two CSV files, and the `LICENSE`. Tagged `v0.1`.

Why move the package under `src/`? Session 4: without `src/`, `import expense_tracker` finds the folder you are standing in; with it, the import only works once the project is installed, so tests exercise what a user would get. Why commit `uv.lock`? `pyproject.toml` says `typer>=0.12`; the lockfile says exactly which version, and CI's `uv sync --locked` fails if the two disagree.

For the user, `python tracker.py expenses.csv dining 20` became `uv run expenses report --category dining --min 20`, and the report text is byte for byte the same. For the developer, the project now has a name, a version, pinned dependencies, an entry point and a home for tests: Checkpoint 1's Definition of Done in miniature.
""",
)

S5_BODY = md(
    """
Session 6 replayed the step from v0.1 to v0.2 as "five commits, one at a time. At each one I stop and ask you for the name." Session 7 then named the moves:

| # | Commit | Message | Move (session 7) | Example |
|---|---|---|---|---|
| 8 | `5e9466d` | Replace magic numbers with named constants | Extract constant | `"-" * 40` becomes `"-" * RULE_WIDTH` |
| 9 | `f3bb801` | Rename calculate_totals to total_by_category | Rename | `d`, `e`, `r` become `totals`, `expense`, `ordered` |
| 10 | `9d6c607` | Separate reading and printing from the calculation | Separate I/O from logic; extract function | `run()` splits into `read_expenses`, `largest_expense`, `format_report` |
| 11 | `017f926` | Give an expense a type instead of a tuple | Introduce a type | `expense[AMOUNT]` becomes `expense.amount` |
| 12 | `04d699f` | Add type hints and make the code ruff clean | Hints and ruff | `def read_expenses(path: str) -> list[Expense]:` |

A refactoring changes the structure and keeps the behaviour: "If the output changes, it was not a refactoring." That is checkable. The session 6 exercise saved the report before and after a change and ran `diff before.txt after.txt`: nothing printed means you are safe. Run on this history, the full report and the `--category dining --min 20` report are identical at every one of the five commits.

The order matters, because each move made the next one mechanical. Named constants gave every tuple position a name, so the code could be read while it was renamed. Readable names made it obvious where `run()` should split. `read_expenses` became the single place that builds an expense, so swapping the tuple for `Expense` touched one constructor and a set of `expense[AMOUNT]` lookups, each replaced one for one. Small functions with one job have obvious signatures, so the hints in 04d699f were short.

The fifth commit does more than its subject says. ruff's rules go into `pyproject.toml`; `%` formatting becomes f-strings; the file in `add` gets a `with`. And the bare `except:` becomes `except (OSError, ValueError):`, the line session 7 shows as "v0.2: only the two we expect". That change is about how the program fails, not about style: a 0-byte file used to print "could not read" and now ends in a traceback whose last line is `StopIteration`. On the sample data nothing changes. The same commit also turns `grand_total = 0` into `grand_total = 0.0`: with hints in place, an `int` that later holds a `float` is session 7's second kind of error, types disagree, and the fix is to make them agree.
""",
)

S6_BODY = md(
    """
Session 7's picture is a core of pure functions, "data in → data out", with no `open`, no `print` and no `sys.exit`, inside a shell, `cli.py`, that "reads files, prints, exits". At v0.2, `run()` in `report.py` still printed and called `sys.exit(1)`; session 7 says "Moving this to the edge is v0.3." Two commits do it.

`15836e1` *Move printing and exiting out of the report module* deletes `run()` from `report.py` (and its `import sys`) and puts its steps into the `report` command:
""",
    fence("diff", DIFF_15836E1_CLI),
    """
`report.py` now has no `print` and no `sys.exit`. One function in it still touches the world: `read_expenses` opens the file. Session 7's slide labels that call "shell: touches a file", and it is the shell that makes the call. `total_by_category` "does not know that a CSV exists. Give it a list and it works."

Is 15836e1 a refactoring? The report is identical and a missing file still exits with code 1. But the message now goes to standard error, not standard output: redirect the two streams (`> out.txt` keeps standard output, `2> err.txt` keeps standard error) and you see the difference. That change is deliberate: session 7's "fail loudly, at the boundary", with session 5's exit code attached.

`88b83c3` *Add pytest and turn on strict type checking* touches only `pyproject.toml` and `uv.lock`: `mypy` and `pytest` join the dev dependencies, `[tool.mypy]` gets `strict = true`, and pytest is told to look in `tests/`. No Python file changes, because none needs to. Session 7 ran the checker live on v0.1:
""",
    fence("console", MYPY_V01),
    """
Four errors, all one kind, missing annotation: "mypy does not look inside a function with no signature". After 04d699f wrote the hints, the same command prints `Success: no issues found in 3 source files`, so switching strict on in v0.3 cost nothing.

The 280 changed lines in `uv.lock` matter too. New dev tools mean new pinned versions, and they are committed in the same commit as the `pyproject.toml` change; otherwise `uv sync --locked` in CI refuses to install.
""",
)

S7_BODY = md(
    """
Session 8 starts at v0.3: "The tests don't exist yet. v0.4 is where I end up." Six commits get there.

- `d38d9e6` *Test the pure core*: `tests/test_report.py`, 17 tests. A fixture supplies Bar Ramon, Zara, Bar Ramon again and Cabify; `parametrize` runs the category and minimum filters over several cases; edge cases are chosen on purpose: no expenses, a minimum exactly equal to an amount (10.0 keeps the 10.0 expense, 10.01 drops it), a refund, a category nobody used, a tie. None of them needs a file, because v0.3's core takes a list and returns a list.
- `f3d9870` *Test reading a file and the missing-file exit code*: the one or two tests at the edge. `tmp_path` builds a CSV with a broken row; `CliRunner` runs `report nosuch.csv` and checks the exit code is 1 and the message is in `result.stderr`. That second test passes only because 15836e1 moved the message to stderr. Run against v0.2's code it fails: stderr is empty.
- `0e05065` *Run ruff, mypy and pytest on every push*: `.github/workflows/check.yml` runs on every push and pull request: check out, install uv and Python 3.13, `uv sync --locked`, `ruff check`, `ruff format --check`, `mypy src tests`, `pytest`. The referee, not the judge.

Then the live cycle from session 8, three commits for three steps. The data has six exact duplicate rows, so the project needs `remove_duplicates(expenses)`.

- `e1b96de` *Add failing tests for remove_duplicates* is **red**: five tests, plus a stub that returns its input "so the failure says something".
""",
    fence("console", PYTEST_E1B96DE_SHORT),
    """
- `1e421bc` *Remove duplicates with a seen-set* is **green**: the smallest code that passes, a loop that remembers what it has seen. 24 passed.
- `d3df52b` *Use dict.fromkeys to drop duplicates in order* is **refactor**: `return list(dict.fromkeys(expenses))`. Dictionaries keep insertion order, and `@dataclass(frozen=True)` makes `Expense` hashable: "Session 6's frozen=True pays off here." Still 24 passed. On the sample file 420 expenses become 414. Tagged `v0.4`.

What changed for the user between v0.3 and v0.4? Nothing. `cli.py` is not in the diff and the report never calls `remove_duplicates`, so `uv run expenses report` prints the same totals. Everything in v0.4 is for the developer: a safety net, and a referee that runs it on every push.
""",
)

S8_BODY = md(
    """
A commit message is written once and read for years, mostly as one line in `git log --oneline`, by someone who was not there: a teammate, a marker, or you six months later. Session 1's list of failures includes "six months on, nobody can read it, not even its author". Almost every subject in the demo history follows three habits:

- **Imperative**: *Add*, *Replace*, *Rename*, *Move*, *Test*, *Run*, *Use*. A quick check: the subject completes the sentence "If applied, this commit will ...".
- **What the change does**, not how the code does it: *Filter by category and ignore small amounts*, not *Add y and z to calculate_totals*. The diff already shows how.
- **Specific**: it names the behaviour or the thing (`total_by_category`, `data/`, `remove_duplicates`), so a search of the log finds it. For a refactoring the move itself is the what: *Rename calculate_totals to total_by_category*.

The TDD pair is the deliberate exception: *Remove duplicates with a seen-set* and *Use dict.fromkeys to drop duplicates in order* name the technique, because in a green step and the refactor after it the technique is what changed.

Sample question 8 compares `Fix stuff in loader` with `Reject negative amounts when loading expenses`. The first fails on every count: "stuff" says nothing, "loader" could be any of several functions, and "Fix" claims a bug without saying which. The second states the new behaviour and turns up in a search for "negative".

**One logical change per commit.** The demo shows the habit: v0.2 is five commits, one per move, and session 8's cycle is three. A commit that mixes a refactoring with a feature cannot be checked with "the output must stay identical", cannot be undone without losing the other half, and usually needs an "and" in its subject. Treat the "and" as a prompt to check: *Add a README and the MIT licence* is one change, the project's public face; *Add --month option and rename variables* is two, because one half changes behaviour and the other must not. The history bends the rule once: 04d699f's subject is about hints and ruff, but the commit also narrowed the bare `except:`, and the log does not say so.

**Tags** are named checkpoints. The labs end with:
""",
    fence("bash", 'git tag -a v0.2 -m "Checkpoint 2: tested core"\ngit push origin v0.2'),
    """
These are your group's tags, not the demo's: `v0.1` for Checkpoint 1, `v0.2` for Checkpoint 2 (tests), `v0.5` for the partial submission. The demo happens to have a `v0.5` too (`check.sh` and `--month`), a different tag in a different repository. Session 6: "The demo's v0.2 is clean code. Yours, on Friday 9 October, is tests."

`-a` makes an annotated tag: it carries its own message, the tagger's name and a date. The tag is pushed on its own; "a missing tag means nothing to mark". Tag a commit CI approved; if CI is red at the tag, fix, push, wait for green, then move the tag. `git tag -n` lists the messages, here the demo's six:
""",
    fence("console", TAG_N),
)

S9_BODY = md(
    """
Session 9 promised it: "We write v0.5's scripts/check.sh together on Friday." Session 10 did, and the demo repository carries the same tag. Five commits, from 20 to 30 April 2026, lead from v0.4 to v0.5, and the tag message reads "check.sh, a --month filter, and a second author": `git log` shows Alberto Camara on the script and the CI commits and Abril on the two month commits.
""",
    fence("console", LOG_V05),
    """
- `8492f59` adds `scripts/check.sh`: 14 lines, committed as an executable (`100755`, the x bit session 9 says CI needs). It runs `ruff check`, `ruff format --check`, `mypy src tests` and `pytest`, announcing each with `echo "==> name"`, and `set -euo pipefail` stops it at the first failure. On v0.5 it ends with `44 passed`, as slide 18 shows.
- `8fabdb3` edits the workflow: the four steps Lint, Formatting, Types and Tests become one, `Run the checks`, that runs `scripts/check.sh`.
- `d814ca9` adds `is_valid_month` and `filter_by_month` to `report.py`, with 18 tests in `tests/test_month.py`. No command calls them, so a user sees nothing: the position of `1e421bc`, a tested function waiting for its caller.
- `416604b` is the caller, `expenses report --month 2025-09`. The command checks the month first and, if it is not `YYYY-MM`, writes a message to standard error and exits with code 2 before it opens the file. Otherwise it filters the list before the totals and the largest are worked out, so `--month` also changes the "Largest single expense" line, which `--category` never does.
- `8a8903d` reverts `8fabdb3`.

A **revert** is a new commit that undoes an earlier one; it does not erase it. `8fabdb3` stays in the log, and the revert's message names it in full and gives the reason:
""",
    fence("console", REVERT_MSG),
    """
The diff of `8fabdb3` shows what was swapped. The revert is the same hunk the other way round, and its `index` line runs backwards (`eb59e60..eb2e436`):
""",
    fence("diff", DIFF_8FABDB3),
    """
`git diff 8fabdb3^ 8a8903d -- .github/workflows/check.yml` prints nothing: after the revert the workflow is byte for byte the one before the switch.

Two statements about CI now meet. Session 10's last slide says "scripts/check.sh is what CI runs", and from `8fabdb3` to `8a8903d` it was. At the v0.5 tag the workflow has its four named steps again, and `check.sh` is what you run before a push: the same four checks, the same exit code. Take the idea from the slide (one command, exit code 0 is green, CI reads that same number) and the file from the history (read `check.yml` when a question shows it).

For the user, v0.5 adds one thing, `--month`. In the teacher's sample question 2, "Adding a `--month` option to the report command" is the option that is not a refactoring: the program now does something new.
""",
)

sections: list[dict[str, Any]] = [
    {
        "id": sid(1),
        "heading": "Reading the history: log, tags and kinds of commit",
        "body_md": S1_BODY,
        "key_points": [
            "25 commits, six tags: `v0.0` script, `v0.1` project, `v0.2` clean code, `v0.3` core and shell with strict types, `v0.4` tests and CI, `v0.5` `check.sh` and `--month`.",
            "A tag is a permanent name for one commit. `git show <hash>` shows a commit; `git checkout <tag>` shows the project as it was.",
            "Ask of every commit: what kind of change is it, and what did it make possible next?",
        ],
        "exam_note_md": "Expect a real commit, diff, `--stat` or log excerpt from this history with a judgement attached: what kind of change, is it a refactoring, which message fits, what changed for the user.",
        "source_ref": "S6 slide 4; S4 slide 25; S7 slide 3; S8 slide 13; S10 slide 17; `git log`, `git tag -n`",
        "check": ["sort-kinds", "sort-tags"],
    },
    {
        "id": sid(2),
        "heading": "Reading a diff and a --stat",
        "body_md": S2_BODY,
        "key_points": [
            "`---` is before, `+++` is after; `/dev/null` means the file did not exist before (or no longer exists).",
            "`@@ -2,9 +2,13 @@`: old start line and length, new start line and length.",
            "Space is context, `-` is removed, `+` is added; a changed line shows as a `-` and a `+`.",
            "`--stat`: which files, how many lines, `old => new` for a move. Read it before the code.",
        ],
        "exam_note_md": "You read diffs, you never write them. The question is always what the change does, whether behaviour changed, or which message fits.",
        "source_ref": "expense-tracker 6efdf9d, a953d05, 2ecad20; S4 slide 26",
        "check": ["hunk-header", "minus-plus", "dev-null"],
    },
    {
        "id": sid(3),
        "heading": "v0.0: the messy script (three commits)",
        "body_md": S3_BODY,
        "key_points": [
            "Three commits, one file: totals by category, filters, the largest expense. Each message says what the program can now do.",
            "The code has every problem the course later fixes: meaningless names, magic indexes, a five-job `run()`, a bare `except:`, positional arguments.",
            "From `c746d38` on, the largest expense ignores the filters. The refactorings keep that behaviour exactly.",
        ],
        "exam_note_md": "Use v0.0 as the 'before' picture: name a problem in it, then the later commit that fixed it.",
        "source_ref": "expense-tracker 3e0834f, 6efdf9d, c746d38; S4 slide 19; S6 slides 13, 18, 22; S7 slide 18",
        "check": ["bare-except-typo", "positional-args", "testable-v00"],
    },
    {
        "id": sid(4),
        "heading": "v0.1: from script to project (four commits)",
        "body_md": S4_BODY,
        "key_points": [
            "a953d05: no code changed; the code became installable.",
            '`expenses = "expense_tracker.cli:app"`: command, then module, then object. Rename either side and the command disappears.',
            "A parameter with a default becomes an option (`--category`, `--min`); `add`'s merchant, category and amount are arguments.",
            "`data/` is git-ignored: `add` never touches the sample file or the public repository.",
        ],
        "exam_note_md": "Typical judgements: what kind of change a `--stat` shows, why a command stopped existing after `[project.scripts]` changed, what changed for the user between v0.0 and v0.1.",
        "source_ref": "expense-tracker a953d05, 2ecad20, bc9ef3d, 89afbe1; S4 slides 19–26; S5 slides 4–8",
        "check": ["stat-a953d05", "src-layout", "entry-point"],
    },
    {
        "id": sid(5),
        "heading": "v0.2: clean code in five commits",
        "body_md": S5_BODY,
        "key_points": [
            "Five commits, five moves: extract constant, rename, separate I/O (and extract function), introduce a type, hints and ruff.",
            "A refactoring keeps the output: `diff before.txt after.txt` prints nothing at every v0.2 commit.",
            "Each move made the next one mechanical.",
            "04d699f also narrowed the bare `except:`, a change in how the program fails, filed under 'ruff clean'.",
        ],
        "exam_note_md": "Session 6 asked for the name of each commit; session 7 named the moves. Expect 'is this a refactoring?' and 'which move is this?' on real lines from these diffs.",
        "source_ref": "S6 slides 16–31; S7 slides 3, 5, 18; expense-tracker 5e9466d..04d699f",
        "check": ["which-refactoring", "sort-moves", "v01-v02-user"],
    },
    {
        "id": sid(6),
        "heading": "v0.3: functional core, imperative shell, strict types (two commits)",
        "body_md": S6_BODY,
        "key_points": [
            "Core: values in, values out. Shell (`cli.py`): reads, prints, exits.",
            "15836e1: identical report, same exit code 1, but the error message now goes to stderr.",
            "88b83c3 is configuration only: strict mode found nothing because v0.2 had typed everything.",
            "Change dependencies in `pyproject.toml`, commit the new `uv.lock` with it.",
        ],
        "exam_note_md": "The careful reading is the one that separates 'the report is unchanged' from 'nothing observable changed': 15836e1 moves the error to stderr on purpose.",
        "source_ref": "S7 slides 8–19; S8 slide 13; expense-tracker 15836e1, 88b83c3",
        "check": ["mypy-v01", "is-15836e1-refactor", "report-py-still"],
    },
    {
        "id": sid(7),
        "heading": "v0.4: tests, CI and one red-green-refactor cycle (six commits)",
        "body_md": S7_BODY,
        "key_points": [
            "Pure core tests first (17), then one or two I/O tests (`tmp_path`, `CliRunner`), then CI on every push.",
            "Red, green, refactor as three commits: failing tests with a stub, the simplest passing loop, then `dict.fromkeys` with the same 24 tests green.",
            "`frozen=True` from v0.2 is what makes `Expense` hashable for the set and the dict.",
            "For the user, v0.4 changes nothing: the report does not call `remove_duplicates` yet.",
        ],
        "exam_note_md": "Expect the red pytest output of e1b96de, the two follow-up diffs, and 'what changed for the user between v0.3 and v0.4'.",
        "source_ref": "S8 slides 5–23; labs/08-tdd.md; expense-tracker d38d9e6..d3df52b",
        "check": ["stub-why", "red-output", "frozen-removed"],
    },
    {
        "id": sid(9),
        "heading": "v0.5: check.sh, a month filter and a revert (five commits)",
        "body_md": S9_BODY,
        "key_points": [
            "Five commits: `scripts/check.sh`, CI switched to it, `filter_by_month` with its validator, the `--month` option, and the revert of the CI switch.",
            "`d814ca9` changes nothing for a user, because no command calls the new functions. `416604b` adds `--month`: a feature, not a refactoring (sample Q2).",
            "Slide 21 says `scripts/check.sh` is what CI runs. At the `v0.5` tag `check.yml` has four named steps again, because `8a8903d` reverted the one-step version.",
            "A revert adds a commit that undoes an earlier one. This one names the commit and gives the reason: a single step hides which check failed.",
        ],
        "exam_note_md": "Expect the `--month` commit as the example of a change that is not a refactoring (sample Q2), a log or workflow excerpt asking what CI runs at v0.5, and 'what changed for the user' between two of these commits.",
        "source_ref": "S9 slides 3, 20; S10 slides 17–21; labs/10-check.sh; sample Q2; expense-tracker 8492f59..8a8903d",
        "check": ["sort-v05-commits", "user-change-v05", "ci-at-v05"],
    },
    {
        "id": sid(8),
        "heading": "Commit messages and tags",
        "body_md": S8_BODY,
        "key_points": [
            "Subject: imperative verb plus what the change does; the diff shows how.",
            "`Fix stuff in loader` names no behaviour, has no searchable word and claims a bug it does not name.",
            "One logical change per commit: refactorings apart from features; red, green and refactor apart.",
            "A tag is a permanent, annotated name for one commit; checkpoints are marked at the tag, on a green commit.",
        ],
        "exam_note_md": "Sample Q8 is the model: a diff, two messages, 'which is better for someone reading the history six months later', and one test in words.",
        "source_ref": "moodle/midterm-sample-questions.md Q8; S6 slide 31; S8 slide 29; labs/01-scaffold.md §9; labs/08-tdd.md §4; partial-rubric",
        "check": ["name-6efdf9d", "sort-subjects", "tag-command"],
    },
]

# --------------------------------------------------------------------------------------
# Terms
# --------------------------------------------------------------------------------------

terms = [
    {"term": "Commit", "definition_md": "A saved snapshot of the whole project, with a message saying what changed. The expense-tracker has 25.", "section_ref": sid(1)},
    {"term": "Short hash", "definition_md": "The first seven characters of a commit's id, as `git log --oneline` prints them: `5e9466d`. Enough to name one commit in `git show`.", "section_ref": sid(1)},
    {"term": "`git log --oneline`", "definition_md": "One line per commit, newest first: short hash and subject. With `--decorate` it also shows tags and branches, such as `(tag: v0.2)`.", "section_ref": sid(1)},
    {"term": "Kind of commit", "definition_md": "What a change is for: feature (new behaviour), refactor (structure only), test, build (packaging, tool settings), ci (the automated check), docs, fix.", "section_ref": sid(1)},
    {"term": "`git show`", "definition_md": "Prints one commit: its message and its diff. With `--stat`, the summary of files changed instead of the lines.", "section_ref": sid(2)},
    {"term": "Diff", "definition_md": "The difference between two versions of the files: `---` and `+++` headers, then hunks of `-` (removed), `+` (added) and context lines.", "section_ref": sid(2)},
    {"term": "Hunk", "definition_md": "One block of changes in a diff, opened by `@@ -old_start,old_len +new_start,new_len @@`.", "section_ref": sid(2)},
    {"term": "Context line", "definition_md": "A diff line starting with a space: unchanged, shown so you can find your place.", "section_ref": sid(2)},
    {"term": "`--stat`", "definition_md": "A per-file summary of a commit or a range: path, lines changed, a bar of `+` and `-`, and a total line. `old => new` marks a move.", "section_ref": sid(2)},
    {"term": "Entry point", "definition_md": 'The `[project.scripts]` line that turns a command into a call: `expenses = "expense_tracker.cli:app"` means command `expenses`, module `expense_tracker.cli`, object `app`.', "section_ref": sid(4)},
    {"term": "Refactoring commit", "definition_md": "A commit that changes the structure and keeps the behaviour. Checked by identical output (`diff before.txt after.txt`) and unchanged passing tests.", "section_ref": sid(5)},
    {"term": "Functional core, imperative shell", "definition_md": "Pure functions that take and return values (the core, `report.py`) inside a thin layer that reads files, prints and exits (the shell, `cli.py`). Reached at v0.3.", "section_ref": sid(6)},
    {"term": "Red, green, refactor", "definition_md": "Write a failing test, write the smallest code that passes, then clean up with the test as a net. In the history: e1b96de, 1e421bc, d3df52b.", "section_ref": sid(7)},
    {"term": "Stub", "definition_md": "A placeholder function that exists but does the wrong thing (`return expenses`), so the new tests import it and fail on their assertions.", "section_ref": sid(7)},
    {"term": "CI workflow", "definition_md": "`.github/workflows/check.yml` (0e05065): on every push and pull request, sync from the lockfile, then ruff, ruff format, mypy and pytest. Any red step marks the commit red.", "section_ref": sid(7)},
    {"term": "Imperative subject line", "definition_md": "A commit subject written as an instruction that says what the change does: *Replace magic numbers with named constants*.", "section_ref": sid(8)},
    {"term": "One logical change per commit", "definition_md": "Each commit does one thing you can name, check and undo on its own; a refactoring never travels with a feature.", "section_ref": sid(8)},
    {"term": "Annotated tag", "definition_md": 'A tag made with `git tag -a v0.2 -m "..."`: a permanent name for one commit that stores its own message, the tagger and a date. Pushed with `git push origin v0.2`.', "section_ref": sid(8)},
    {"term": "`scripts/check.sh`", "definition_md": 'The demo\'s one-command check (`8492f59`, session 10): `set -euo pipefail`, then `ruff check`, `ruff format --check`, `mypy src tests` and `pytest`, each announced by an `echo "==> name"` line. Exit code 0 is green. It is for running the same checks before a push; at v0.5 `check.yml` still lists the four steps.', "section_ref": sid(9)},
    {"term": "Revert", "definition_md": "A new commit that undoes the changes of an earlier one. The earlier commit stays in the log and the revert's message names it. In the demo, `8a8903d` undoes `8fabdb3`.", "section_ref": sid(9)},
]

# --------------------------------------------------------------------------------------
# Traps
# --------------------------------------------------------------------------------------

traps = [
    "**\"a953d05 changed the code.\"** It did not touch `tracker.py` at all. It added the project files around the code: the code became installable, and the report still ran as a script until 2ecad20.",
    "**\"A changed line appears once in a diff.\"** It appears twice: a `-` line with the old text, then a `+` line with the new one.",
    "**\"15836e1 is a pure refactoring.\"** The report is identical and the exit code is still 1, but the error message moved from stdout to stderr. A small, deliberate change in behaviour.",
    "**\"v0.4 removes the duplicates from the report.\"** `remove_duplicates` exists and is tested, but `cli.py` never calls it. The report's totals are the same at v0.3 and v0.4.",
    "**\"Turning on `strict = true` (88b83c3) needed a big clean-up.\"** It needed none: 04d699f had already annotated every function, so `mypy --strict` had nothing to report.",
    "**\"Committing failing tests (e1b96de) is a mistake.\"** It is the red step: the tests define done before the code exists and prove they can fail. The green commit followed the same day.",
    "**\"Narrowing `except:` cannot change behaviour.\"** In 04d699f it did: a 0-byte file used to print \"could not read\" and now crashes with `StopIteration`, a case the bare `except:` had been hiding.",
    "**\"A good subject explains how the code works.\"** The diff shows how. The subject says what the change does for the program or the project, in the imperative.",
    "**\"A tag moves forward with new commits.\"** A tag stays on the commit it was given. If CI is red there, fix, push, wait for green and move the tag yourself.",
    "**\"Identical output on the sample data proves a refactoring.\"** It is evidence for that input only. 9d6c607 prints the same report on the sample, but a file of only refunds now shows a 'largest' line it did not show before.",
    "**\"`scripts/check.sh` is what CI runs, so `check.yml` has one step.\"** It did from `8fabdb3` until `8a8903d` reverted it. At the `v0.5` tag the workflow has the four named steps again, and the script is the same four checks run on your own machine before a push.",
    "**\"Adding `--month` is a refactoring, because the report looks the same without the option.\"** Sample question 2 uses this very option as the change that is not a refactoring: the program now does something new. The commit before it, `d814ca9`, adds the month functions and changes nothing a user can see.",
    "**\"A revert deletes the commit it undoes.\"** It adds one more commit that cancels the change. `8fabdb3` is still in the log, and after `8a8903d` the workflow file is byte for byte the one from before it.",
]

# --------------------------------------------------------------------------------------
# Flashcards
# --------------------------------------------------------------------------------------

_cards = [
    ("recall", 1, "Name the six tags of the expense-tracker and what each marks.", "`v0.0` the messy script; `v0.1` packaged (uv, `src/`, typer CLI); `v0.2` clean code (names, responsibilities, a type); `v0.3` functional core, imperative shell, strict types; `v0.4` tests, CI and one red-green-refactor cycle; `v0.5` `check.sh`, a `--month` filter and a second author."),
    ("recall", 1, "Which session used which part of the history?", "Session 4: a953d05, script to project. Session 6: the five v0.2 commits, replayed. Session 7: `mypy --strict` on v0.1, moving I/O out for v0.3. Session 8: the live TDD cycle from v0.3 to v0.4. Session 10: `scripts/check.sh`, the file v0.5 contains."),
    ("reading", 2, "What does `@@ -2,9 +2,13 @@` say?", "The hunk covers 9 lines from line 2 in the old file and 13 lines from line 2 in the new one: 4 lines more."),
    ("reading", 2, "In a diff, what do a leading space, `-` and `+` mean?", "Space: unchanged context. `-`: removed. `+`: added. A changed line is a `-` line followed by a `+` line."),
    ("reading", 2, "`--- /dev/null` then `+++ b/.github/workflows/check.yml`: what happened?", "The file was created: nothing existed before. (A deleted file has `+++ /dev/null`.)"),
    ("reading", 2, "`tracker.py => src/expense_tracker/report.py | 13 -----` in a `--stat`?", "The file was moved (renamed) into the package and 13 of its lines were deleted: the `sys.argv` block typer replaced, with the two blank lines above it."),
    ("concept", 3, "Name four problems of the v0.0 script that later commits fix.", "Meaningless names (`x`, `d`, `e`, `mr`), magic indexes (`e[3]`), a `run()` with five jobs, a bare `except:` that hides every bug, positional arguments."),
    ("concept", 3, "Why does the v0.0 script print \"could not read expenses.csv\" when the file is fine but the code has a typo?", "The bare `except:` catches every error, the typo's included, and reports it as a file problem."),
    ("concept", 4, "What did a953d05 change, in session 4's words?", "\"`uv init --package`, and one edit.\" No code changed; the code became installable."),
    ("recall", 4, 'What does `expenses = "expense_tracker.cli:app"` mean?', "The command `expenses` runs the object `app` in the module `expense_tracker.cli`. Rename either side and the command disappears."),
    ("distinction", 4, "In bc9ef3d's `add`, why are merchant, category and amount arguments but date an option?", "A parameter without a default is an argument (required, positional); one with a default is an option (`--date`, falls back to today)."),
    ("concept", 4, "Why is `data/` in `.gitignore` since bc9ef3d?", "`add` writes real spending there. The sample `expenses.csv` is never modified, and personal data must never enter the public repository."),
    ("recall", 5, "The five v0.2 commits, in order?", "Replace magic numbers with named constants; rename `calculate_totals` to `total_by_category`; separate reading and printing from the calculation; give an expense a type instead of a tuple; add type hints and make the code ruff clean."),
    ("concept", 5, "How do you check that a commit is a refactoring?", "Same output before and after (`diff before.txt after.txt` prints nothing) and the same tests still pass. If the output changes, it was not a refactoring."),
    ("distinction", 5, "In 9d6c607, which part is 'separate I/O from logic' and which is 'extract function'?", "`format_report` returning lines instead of printing them, and `read_expenses`, separate I/O from logic. `largest_expense` pulled out of `run()` is extract function."),
    ("concept", 5, "What did 04d699f do that its subject does not mention?", "It replaced the bare `except:` with `except (OSError, ValueError):`. That changes how the program fails: a 0-byte file now crashes with `StopIteration`."),
    ("concept", 6, "What did 15836e1 move, and what did that change for a user?", "`run()`'s reading, printing and exiting moved from `report.py` into the `report` command in `cli.py`. Same report, same exit code 1; the error message is now on stderr."),
    ("distinction", 6, "After v0.3, what is in `report.py` and what is in `cli.py`?", "`report.py`: the core (totals, largest, formatting) plus `read_expenses`, with no `print` or `sys.exit`. `cli.py`: the shell that reads, echoes and exits."),
    ("reading", 6, "`mypy --strict` on v0.1 reports four `no-untyped-def` / `no-untyped-call` errors. What kind, and what fixes them?", "One kind, missing annotation: mypy cannot see inside a function with no signature. Writing the hints (04d699f) fixes all four."),
    ("concept", 6, "Why did 88b83c3 turn on `strict = true` without changing any `.py` file?", "v0.2 had already annotated every function, so strict mypy had nothing to report."),
    ("recall", 7, "What does the CI workflow from 0e05065 run, in order?", "Install the exact versions from the lockfile, lint with ruff, check formatting with ruff, type-check `src` and `tests` with mypy, run pytest. On every push and pull request; any red step makes the commit red."),
    ("concept", 7, "Why was e1b96de committed with failing tests and a stub that returns its input?", "It is the red step: the tests say what done means before the code exists. With the stub they can import the function, so the failure is about behaviour, not an import error."),
    ("concept", 7, "Why does `list(dict.fromkeys(expenses))` work, and keep the first copy?", "Dict keys must be hashable and `frozen=True` makes `Expense` hashable; dicts keep insertion order, so the first occurrence stays where it was."),
    ("concept", 7, "What changed for the user between v0.3 and v0.4?", "Nothing: `cli.py` is not in the diff and the report does not call `remove_duplicates`. v0.4 is tests, CI and a tested function."),
    ("concept", 8, "What makes a good commit subject, judging by this history?", "Imperative, says what the change does (not how), specific enough to search: *Separate reading and printing from the calculation*."),
    ("distinction", 8, "`Fix stuff in loader` vs `Reject negative amounts when loading expenses`?", "The first names no behaviour and claims an unnamed bug; the reader must open the diff. The second states the new behaviour and can be found by searching."),
    ("concept", 8, "Why one logical change per commit?", "So each commit can be named, checked (a refactoring by unchanged output) and undone on its own. Mixing a feature into a refactoring breaks all three."),
    ("reading", 8, 'What do `git tag -a v0.2 -m "Checkpoint 2: tested core"` and `git push origin v0.2` do?', "Give the current commit a permanent, annotated name with a message, then send that tag to GitHub. Checkpoints are marked at the tag."),
    ("recall", 9, "Which five commits lie between `v0.4` and `v0.5`?", "`8492f59` adds `scripts/check.sh`; `8fabdb3` makes CI run it as one step; `d814ca9` adds `filter_by_month` and `is_valid_month`; `416604b` adds `--month`; `8a8903d` reverts `8fabdb3`."),
    ("concept", 9, "Slide 21 says `scripts/check.sh` is what CI runs. What does `check.yml` run at the `v0.5` tag?", "The four named steps again: Lint, Formatting, Types, Tests. `8fabdb3` had replaced them with one `scripts/check.sh` step and `8a8903d` reverted it. The script stays for running the same checks before a push."),
    ("concept", 9, "Why was `8fabdb3` reverted?", "One step called \"Run the checks\" hides which check failed: a red run means opening the log to see whether it was ruff, mypy or pytest. Separate named steps say it in the Actions summary."),
    ("reading", 9, "What does `scripts/check.sh` run, and when does it stop?", "`ruff check`, `ruff format --check`, `mypy src tests` and `pytest`, in that order, each announced by `==> name`. `set -e` stops it at the first failure and the exit code is then non-zero; with everything green it is 0, and that number is what CI reads too."),
    ("reading", 9, "What does `d814ca9` change for someone running `uv run expenses report`?", "Nothing. It adds `is_valid_month` and `filter_by_month` with 18 tests, but `cli.py` is not in the diff, so no command calls them. `--month` is still \"No such option\" until `416604b`."),
    ("concept", 9, "Why does `--month` change the \"Largest single expense\" line when `--category` does not?", "`cli.py` filters the list by month before it works out the totals and the largest. The category and minimum filters run only inside `total_by_category`, so the largest still comes from every expense: a v0.0 behaviour that was never changed."),
    ("reading", 9, "`expenses report nosuch.csv --month 2025-13` exits with which code, and why not 1?", "2. The month is checked first, before the file is opened, and `cli.py` raises `typer.Exit(2)` after a message on standard error. A missing file with a valid month gives 1."),
    ("distinction", 9, "Is adding `--month` a refactoring? Which sample question says so?", "No: the program does something new, so it is a feature. Sample question 2 lists \"Adding a `--month` option to the report command\" as the option that is not a refactoring."),
]

flashcards = [
    {
        "id": f"{MID}-f{i:02d}",
        "front_md": front,
        "back_md": back,
        "kind": kind,
        "section_ref": sid(sec),
    }
    for i, (kind, sec, front, back) in enumerate(_cards, start=1)
]

# --------------------------------------------------------------------------------------
# Questions
# --------------------------------------------------------------------------------------

questions: list[dict[str, Any]] = []
keys: dict[str, str] = {}


def _add(key: str, q: dict[str, Any]) -> None:
    qid = f"{MID}-q{len(questions) + 1:02d}"
    keys[key] = qid
    q = {"id": qid, **q}
    questions.append(q)


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
    source: str,
    origin: str,
    verified: str,
    variant_of: str | None = None,
) -> None:
    assert len(wrong) == 3
    options = [{"text_md": t, "correct": False, "why_md": w} for t, w in wrong]
    options.insert("abcd".index(pos), {"text_md": right[0], "correct": True, "why_md": right[1]})
    q: dict[str, Any] = {
        "type": "mcq",
        "level": level,
        "skills": skills,
        "stem_md": stem,
        "options": options,
        "explanation_md": explanation,
        "section_ref": sid(section),
        "source_ref": source,
        "origin": origin,
        "verified_by": verified,
    }
    if variant_of:
        q["variant_of"] = variant_of
    _add(key, q)


def open_q(
    key: str,
    *,
    level: str,
    skills: list[str],
    stem: str,
    parts: list[dict[str, Any]],
    explanation: str,
    section: int,
    source: str,
    origin: str,
    verified: str,
    variant_of: str | None = None,
    lines: str = "5–8",
) -> None:
    q: dict[str, Any] = {
        "type": "open",
        "level": level,
        "skills": skills,
        "stem_md": stem,
        "parts": parts,
        "lines": lines,
        "explanation_md": explanation,
        "section_ref": sid(section),
        "source_ref": source,
        "origin": origin,
        "verified_by": verified,
    }
    if variant_of:
        q["variant_of"] = variant_of
    _add(key, q)


def part(label: str, prompt: str, marks: int, model: str, rubric: list[str], weak: str) -> dict[str, Any]:
    return {
        "label": label,
        "prompt_md": prompt,
        "marks": marks,
        "model_answer_md": model,
        "rubric": rubric,
        "weak_answers_md": weak,
    }


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
    source: str,
    origin: str,
    verified: str,
) -> None:
    _add(
        key,
        {
            "type": "sort",
            "level": level,
            "skills": skills,
            "stem_md": stem,
            "categories": [{"id": c, "label": label} for c, label in categories],
            "items": [{"text_md": t, "category": c, "why_md": w} for t, c, w in items],
            "explanation_md": explanation,
            "section_ref": sid(section),
            "source_ref": source,
            "origin": origin,
            "verified_by": verified,
        },
    )


# ---------------- s1: the history, tags and kinds ----------------

sort_q(
    "sort-kinds",
    level="core",
    skills=["concept", "judgement"],
    stem="Sort these ten commits from the expense-tracker history by the kind of change they make.",
    categories=[
        ("feature", "Feature: new behaviour"),
        ("refactor", "Refactor: structure only"),
        ("test", "Test"),
        ("buildci", "Build or CI: packaging, tools, the check"),
        ("docs", "Docs"),
    ],
    items=[
        ("`3e0834f` Add a script that totals expenses by category", "feature", "The first behaviour the program ever had: a report of totals per category."),
        ("`bc9ef3d` Add an add command that writes to data/", "feature", "A new command a user can run; before this commit there was no way to add an expense."),
        ("`1e421bc` Remove duplicates with a seen-set", "feature", "The green step: `remove_duplicates` goes from returning its input to actually dropping duplicates, which is new behaviour."),
        ("`f3bb801` Rename calculate_totals to total_by_category", "refactor", "Only names change; the report is identical before and after."),
        ("`d3df52b` Use dict.fromkeys to drop duplicates in order", "refactor", "Same behaviour in one line; the same 24 tests stay green."),
        ("`d38d9e6` Test the pure core", "test", "Adds `tests/test_report.py` and touches no source file."),
        ("`e1b96de` Add failing tests for remove_duplicates", "test", "Its purpose is the five new tests; the stub only exists so they can import the function."),
        ("`a953d05` Turn the script into a uv package", "buildci", "Adds `pyproject.toml`, `uv.lock` and the package folder; no report code changes."),
        ("`0e05065` Run ruff, mypy and pytest on every push", "buildci", "Adds the CI workflow: it changes how the project is checked, not what the program does."),
        ("`89afbe1` Add a README and the MIT licence", "docs", "Documentation and a licence; no code changes."),
    ],
    explanation="Ask what each commit does to the program's behaviour. New behaviour is a feature even when it is small, no command uses it yet, or the tests came first: 1e421bc gives `remove_duplicates` its behaviour, though the report does not call it. A refactor keeps the output: f3bb801 and d3df52b change how the code reads, not what it prints. Test commits add tests. Packaging and the CI workflow change the project's tooling, and the README and licence are documentation. Notice that the history has no fix commit: none of the 25 repairs a bug.",
    section=1,
    source="`git log`; S1 slide 19; S7 slide 5; S8 slides 14–16",
    origin="history",
    verified="source",
)

sort_q(
    "sort-tags",
    level="hard",
    skills=["read-tool-output", "concept"],
    stem=md(
        "The history of the expense-tracker up to its fifth tag, `v0.4`:",
        fence("console", LOG_ONELINE_V04),
        "Which tag first contains each of these? Use the log, then put each one under the earliest tag at which it exists.",
    ),
    categories=[("v00", "`v0.0`"), ("v01", "`v0.1`"), ("v02", "`v0.2`"), ("v03", "`v0.3`"), ("v04", "`v0.4`")],
    items=[
        ("Filtering the report by category and a minimum amount", "v00", "6efdf9d, before any structure: the two arguments after the path."),
        ("The `expenses` command with a generated `--help`", "v01", "2ecad20 put the report behind a typer CLI."),
        ("The `add` command", "v01", "bc9ef3d, just before the v0.1 tag."),
        ("A README that says how to install and run the program", "v01", "89afbe1 is the commit tagged v0.1."),
        ("The `Expense` dataclass", "v02", "017f926, the fourth of the five clean-code commits."),
        ("Named constants such as `RULE_WIDTH`", "v02", "5e9466d, the first of the five clean-code commits."),
        ("`strict = true` for mypy in `pyproject.toml`", "v03", "88b83c3, the commit tagged v0.3."),
        ("The error message for a missing file going to standard error", "v03", "15836e1 moved it into `cli.py` with `typer.echo(..., err=True)`."),
        ("Tests that use `CliRunner`", "v04", "f3d9870 added `tests/test_io.py`."),
        ("A CI workflow that runs on every push", "v04", "0e05065 added `.github/workflows/check.yml`. Before it, the demo had no automated check."),
    ],
    explanation="The tags are cumulative checkpoints: each one contains everything before it, so read the log from the bottom and a commit belongs to the first tag at or above it. The script already filtered (v0.0); packaging brought the command, `add` and the README (v0.1); clean code brought constants and the dataclass (v0.2); v0.3 moved the I/O to the shell and turned strict mypy on; v0.4 brought the tests and CI. Two easy slips: the error going to stderr arrives with the core/shell split (v0.3), not with the tests, and CI arrives last, after the first tests.",
    section=1,
    source="`git log --oneline --decorate`; `git tag -n`",
    origin="history",
    verified="run",
)

# ---------------- s2: reading a diff ----------------

mcq(
    "hunk-header",
    level="core",
    skills=["read-diff"],
    stem=md(
        "This is the first hunk of `6efdf9d` *Filter by category and ignore small amounts*:",
        fence("diff", DIFF_6EFDF9D_H1),
        "What does the line `@@ -2,9 +2,13 @@ import sys` tell you? (After `@@`, the pair with `-` describes the old file and the pair with `+` the new file: a start line, a comma, then a number of lines.)",
    ),
    right=(
        "Old file: 9 lines starting at line 2; new file: 13 lines starting at line 2",
        "`-2,9` is the old start line and length, `+2,13` the new ones. One line removed and five added turn 9 lines into 13.",
    ),
    wrong=[
        ("Lines 2 to 9 were deleted, and lines 2 to 13 were written in their place instead", "This reads the numbers as ranges of deleted and added lines. Most lines in the hunk are context: unchanged, shown with a leading space."),
        ("The commit changed 9 files and 13 lines in total across the project", "File counts belong to `--stat`. A hunk header only describes one region of one file."),
        ("The commit made `tracker.py` grow from 9 lines to 13 lines", "9 and 13 are the lengths of this hunk, not of the file. `tracker.py` went from 49 to 63 lines in this commit."),
    ],
    pos="b",
    explanation="A hunk header has the form `@@ -old_start,old_length +new_start,new_length @@`. Count the hunk to check: 8 context lines plus 1 removed line make the 9 old lines; 8 context lines plus 5 added lines make the 13 new ones. The words after the header are a signpost to help you place the hunk, not part of the change. You will never be asked to write a header, but reading one tells you quickly whether a change grew or shrank the code and where it sits.",
    section=2,
    source="expense-tracker 6efdf9d (`git show 6efdf9d`)",
    origin="history",
    verified="run",
)

mcq(
    "minus-plus",
    level="core",
    skills=["read-diff"],
    stem=md(
        "A hunk from `5e9466d` *Replace magic numbers with named constants*:",
        fence("diff", DIFF_5E9466D_ROW),
        "Which statement reads this hunk correctly?",
    ),
    right=(
        "Three old lines became two: the comment went, the code now uses constants",
        "Three `-` lines, two `+` lines. The `+` lines are the same code with `4`, `0`, `1`, `2`, `3` replaced by names.",
    ),
    wrong=[
        ("Only the comment was deleted; the two `+` lines were already in the file before", "A `+` line is new in this commit. The old versions of those lines are the `-` lines just above them."),
        ("The lines without a sign were deleted and the marked lines were kept", "Lines with a leading space are context: unchanged, shown so you can find your place."),
        ("The constants `DATE` to `AMOUNT` are defined inside this hunk, above the loop", "They are defined in the first hunk, at the top of the file. That is why this hunk starts at line 26 in the old file but at line 36 in the new one: ten lines were added above it."),
    ],
    pos="a",
    explanation="In a diff, a changed line never appears once: git shows the old text as a `-` line and the new text as a `+` line. Here `if len(row) == 4:` became `if len(row) == FIELDS_PER_ROW:` and the tuple indexes became `DATE`, `MERCHANT`, `CATEGORY`, `AMOUNT`. The comment disappeared because the constant now says what it said. The context lines (`next(reader)`, `f.close()`, the bare `except:`) did not change in this commit, which is why the bare `except:` survives until 04d699f. The header's `-26` against `+36` shows that ten lines, the constants, were added above this hunk.",
    section=2,
    source="expense-tracker 5e9466d; S6 slides 14, 16",
    origin="history",
    verified="run",
)

mcq(
    "dev-null",
    level="core",
    skills=["read-diff"],
    stem=md(
        "The diff of `0e05065` begins like this:",
        fence("diff", DIFF_0E05065_NEW),
        "What does the header tell you about `check.yml`? (`/dev/null` is git's name for 'nothing': a side that shows it has no file.)",
    ),
    right=(
        "It is a new file, created by this commit with 37 lines",
        "`--- /dev/null` means there was no old version; `@@ -0,0 +1,37 @@` means zero old lines became 37 new ones.",
    ),
    wrong=[
        ("It was deleted: this commit moved its contents to `/dev/null`", "That would be the reverse: `--- a/...` with `+++ /dev/null`. Here the old side is empty."),
        ("It already existed and 37 of its lines were edited", "An edit shows `--- a/.github/workflows/check.yml` and an old length above zero."),
        ("It was renamed, from an old file called `/dev/null` to its new path", "`/dev/null` is not a file in the project; git writes it to say 'nothing on this side'. A rename shows `old => new` in `--stat`."),
    ],
    pos="c",
    explanation="`---` is the before side and `+++` the after side. When the before side is `/dev/null`, the file did not exist, so every line of the hunk is a `+` line and the header starts at `-0,0`. The same pattern opens every new file with content in this history: `tracker.py` in 3e0834f, `pyproject.toml` in a953d05, `cli.py` in 2ecad20, each test file in v0.4.",
    section=2,
    source="expense-tracker 0e05065",
    origin="history",
    verified="run",
)

mcq(
    "stat-2ecad20",
    level="exam",
    skills=["read-tool-output", "read-diff"],
    stem=md(
        "You look at one commit's summary:",
        fence("console", STAT_2ECAD20),
        "What happened to `tracker.py` in this commit? (In `--stat`, `a => b` means the file named `a` is now named `b`.)",
    ),
    right=(
        "It moved into the package as `report.py` and lost 13 lines on the way",
        "`old => new` is how `--stat` shows a move, and `13 -----` says 13 lines were removed. The full diff calls it a rename with 84% similarity.",
    ),
    wrong=[
        ("It was deleted, and a new `report.py` of 13 lines was written from scratch", "The arrow means git recognised the same file under a new name. 13 is the number of changed lines, not the size of the file."),
        ("It was copied into the package, and the original stays at the project root", "A move leaves nothing behind. After 2ecad20 there is no `tracker.py` at the root."),
        ("It moved into the package, and 13 lines were added to it there", "The bar is all `-`: 13 lines were removed and none added. They are the `sys.argv` block typer replaced."),
    ],
    pos="d",
    explanation="Read `--stat` line by line. The `=>` line is a move: `tracker.py` became `src/expense_tracker/report.py`, and the 13 deleted lines are the 11-line `if __name__ == \"__main__\":` block that read `sys.argv`, plus the two blank lines above it. typer in the new `cli.py` (19 lines) now does that job. `pyproject.toml` changed in 6 lines (typer as a dependency, the new `expenses` command), and `uv.lock` grew because typer and its dependencies are now pinned.",
    section=2,
    source="expense-tracker 2ecad20 (`git show --stat`)",
    origin="history",
    verified="run",
)

# ---------------- s3: v0.0 ----------------

mcq(
    "bare-except-typo",
    level="core",
    skills=["read-code", "predict-output"],
    stem=md(
        "This is the reading part of the v0.0 script:",
        fence("python", V00_TRY),
        "A teammate edits it and mistypes `rows.append(` as `rows.apend(`. The sample `expenses.csv` is in place. They run it:",
        fence("console", TYPO_RUN),
        "What is going on?",
    ),
    right=(
        "The bare `except:` caught the typo's error and reported it as a file problem",
        "`rows.apend` raises `AttributeError` inside the `try`. A bare `except:` catches everything, so the typo is printed as \"could not read\".",
    ),
    wrong=[
        ("The file really is unreadable, so the message is accurate", "The same file reads fine with the original code. The message is the only thing the `except:` branch can print, whatever went wrong."),
        ("Python spotted the typo before running and printed this instead of starting", "Python does not check attribute names before running. The message comes from the script's own `print` in the `except:` branch."),
        ("The exit code 1 is Python's way of reporting the typo", "1 comes from the script's own `sys.exit(1)` in the `except:` branch, which runs for any error."),
    ],
    pos="c",
    explanation="Session 7 uses this exact code: \"A bare except hides every bug: a typo, a missing import, Ctrl-C. All become 'could not read'.\" The fix is to catch only what you can handle. In the history it arrives in 04d699f as `except (OSError, ValueError):`, the two errors a missing file or a bad amount actually raise. With that line, the typo would surface as an `AttributeError` with a traceback pointing at the misspelt line.",
    section=3,
    source="expense-tracker v0.0 `tracker.py`; S7 slide 18",
    origin="history",
    verified="run",
)

mcq(
    "positional-args",
    level="exam",
    skills=["read-code", "predict-output"],
    stem=md(
        "The v0.0 script reads its arguments like this:",
        fence("python", V00_ARGS_BLOCK),
        "You want the report for every category, but only amounts of 20 or more. Which command gives it?",
    ),
    right=(
        '`python tracker.py expenses.csv "" 20`',
        "The category is the second argument after the script name, so you must fill its place with an empty string before the minimum can be the third.",
    ),
    wrong=[
        ("`python tracker.py expenses.csv 20`", "`20` lands in the category position: the report says `category: 20` and every total is filtered out, so it shows `TOTAL 0.00`."),
        ("`python tracker.py 20`", "`20` is read as the path: the script prints `could not read 20` and exits with 1."),
        ("`python tracker.py --min 20`", "v0.0 knows nothing about options: `--min` is taken as the file name, so it prints `could not read --min`."),
    ],
    pos="a",
    explanation="With positional arguments, the order is the interface. To give the third value you must give the second, even when you want 'no category'. 2ecad20 fixes this with typer: `category` and `minimum` have defaults, so they become the options `--category` and `--min`, and `uv run expenses report --min 20` works on its own. Session 5's rule: an argument is what the command acts on, an option is how it behaves, and a missing option falls back to its default.",
    section=3,
    source="expense-tracker 6efdf9d, 2ecad20; S5 slide 8",
    origin="history",
    verified="run",
)

mcq(
    "testable-v00",
    level="exam",
    skills=["read-code", "judgement"],
    stem=md(
        "Look again at the v0.0 code (the full file also has a `__main__` block that reads `sys.argv`):",
        fence("python", V00_CALC),
        "Without changing any code, which part could you already test by passing in a list and checking the answer?",
    ),
    right=(
        "`calculate_totals`: it takes rows and returns totals",
        "Badly named, but pure: no file, no `print`, no `sys.exit`. A test could pass three tuples and assert on the result.",
    ),
    wrong=[
        ("`run`, because it does the real work of the report", "`run` opens a file, prints and may call `sys.exit`. You can only look at what it prints, not assert on a returned value."),
        ("None of it: code in a script cannot be tested until it is packaged", "Packaging makes imports reliable, but a pure function is testable wherever it lives."),
        ("The `__main__` block, because it decides the inputs", "That block reads `sys.argv` and calls `run`; it returns nothing and cannot be called from a test."),
    ],
    pos="b",
    explanation="Bad names and testability are different problems. `calculate_totals(x, y, z)` reads terribly, but it takes data and returns data, which is all a test needs: \"A function that returns can be tested, reused and read on its own. A function that prints can only be looked at.\" The rest of the script is tangled with the file and the screen. The history fixes the names in f3bb801, splits `run()` in 9d6c607 and moves the I/O out in 15836e1, and only then do the v0.4 tests arrive.",
    section=3,
    source="expense-tracker v0.0; S6 slide 20; S8 slide 19",
    origin="history",
    verified="reasoning",
)

open_q(
    "open-6efdf9d",
    level="exam",
    skills=["read-diff", "compare", "judgement"],
    stem=md(
        "A teammate shows you this diff from the expense-tracker history (trimmed: the hunks that add `cat` and `minimum` to `run`'s parameters and read them from the command line are not shown):",
        fence("diff", DIFF_6EFDF9D_OPEN),
        "Two candidate commit messages:\n\n- A: `Add y and z to calculate_totals`\n- B: `Filter by category and ignore small amounts`",
    ),
    parts=[
        part(
            "1",
            "What does this change do?",
            2,
            "The report can now be limited to one category and can skip amounts below a minimum. `calculate_totals` skips rows of another category or below the minimum, and the report header says which filters are on.",
            [
                "Says the report can be filtered to one category (rows of other categories are skipped).",
                "Says amounts below a minimum are left out, or that the header now shows the filters in use.",
            ],
            "Weak answers paraphrase the code line by line (\"it adds two parameters and two ifs\") without saying what the user gets. Another slip is reading `if e[3] < z: continue` backwards and saying small amounts are kept: `continue` skips the row. Answers that say 'it fixes the totals' miss that this is new behaviour, not a repair.",
        ),
        part(
            "2",
            "Which message is better for someone reading the history six months later, and why?",
            2,
            "B. It says what the program can now do in a user's words, so a search for 'filter' or 'category' finds it. A describes the mechanics with names that mean nothing out of context; the reader would have to open the diff to learn what `y` and `z` are.",
            [
                "Chooses B.",
                "Reason: B states the behaviour or effect, while A describes how (or uses meaningless names), so the reader must open the diff.",
            ],
            "Choosing A because it is 'more precise' misses that `y` and `z` are only precise to someone reading the code; the subject is for the person who is not. Answers that only say 'B is clearer' without saying what it makes clear score one mark.",
        ),
        part(
            "3",
            "Name one test you would add for this change, in words.",
            2,
            "An expense exactly equal to the minimum is kept: with dining amounts 10 and 5 and a minimum of 10, the dining total is 10. (Or: filtering on a category nobody used gives an empty result.)",
            [
                "Describes a concrete input and the expected result.",
                "Targets an edge case of the new behaviour: the boundary (amount equal to the minimum), a category nobody used, or no expenses.",
            ],
            "'Test that filtering works' names no input and no expected result. Writing test code instead of words is not what is asked. A test of the happy path only (one dining expense, filter dining) earns one mark: the boundary is where this code can be wrong, which is why v0.4 tests exactly that case.",
        ),
    ],
    explanation="This is sample Q8's shape on a real commit. Part 1 asks for the effect, not a reading of each line. Part 2 rewards the message that says what changed for the program, which is the real one. Part 3 should pick a case that could break: `if e[3] < z: continue` keeps an amount equal to `z`, and d38d9e6 later pins that down with `test_minimum_keeps_amounts_equal_to_it` (10.0 kept, 10.01 dropped).",
    section=3,
    source="expense-tracker 6efdf9d, d38d9e6; sample Q8; S8 slide 11",
    origin="teacher-variant",
    variant_of="sample-paper-q08",
    verified="run",
)

# ---------------- s4: v0.1 ----------------

mcq(
    "stat-a953d05",
    level="core",
    skills=["read-tool-output", "concept"],
    stem=md(
        "Session 4 showed this commit as \"the moment it became a project\":",
        fence("console", STAT_A953D05),
        "What kind of change was it?",
    ),
    right=(
        "Packaging: it added the project's files and changed no report code",
        "`tracker.py` is not in the list. Everything here is project anatomy: identity, pinned versions, ignore rules, a package folder.",
    ),
    wrong=[
        ("A refactoring of `tracker.py`, because the code was reorganised into the `src/` folder", "`tracker.py` does not appear in the `--stat`, so it was not touched. It only moves into `src/` in the next commit, 2ecad20."),
        ("A new feature, because 34 lines of new content were inserted", "Inserted lines are not new behaviour. The two lines in `__init__.py` are the template's `main()` that prints `Hello from expense-tracker!`."),
        ("A bug fix, because the file `README.md` shows 0 changed lines", "`README.md | 0` is a file created empty, not a repair of anything."),
    ],
    pos="b",
    explanation="Session 4's own words: \"`uv init --package`, and one edit. No code changed\"; the code became installable. A `--stat` is enough to see it: the six files are `.gitignore`, `.python-version`, an empty `README.md`, `pyproject.toml`, a placeholder package and `uv.lock`. Running `uv run expense-tracker` at this commit prints the template's greeting, while `python tracker.py` still prints the report. The report code joins the package in 2ecad20.",
    section=4,
    source="S4 slides 25–26; expense-tracker a953d05",
    origin="slides",
    verified="run",
)

mcq(
    "src-layout",
    level="core",
    skills=["concept"],
    stem="From v0.1 the code lives in `src/expense_tracker/`, not in a folder at the project root. What is the reason session 4 gives for the `src/` layout?",
    right=(
        "With `src/`, the package imports only when installed, so tests see what users get",
        "Session 4: without `src/`, the import finds the folder you are standing in, whether or not the package is installed.",
    ),
    wrong=[
        ("Python can only import a package that sits inside a folder called `src`, so it is required", "Python imports from any folder on its path; that is exactly why a package at the root gets imported by accident."),
        ("uv compiles everything under `src/` in advance, so the installed program starts faster", "Nothing is compiled; the layout is about what gets imported, not speed."),
        ("It hides the source code from the people who install the package from the repository", "The source is installed and readable either way. The split is between deployable code in `src/` and the tests in `tests/`."),
    ],
    pos="d",
    explanation="The `src/` layout is a guard against a test passing for the wrong reason. If `expense_tracker/` sat at the root, `import expense_tracker` in a test would find the folder next to it even if the project were not installed or `pyproject.toml` were broken. Under `src/`, the import only works through the installed project, so the tests see what a user gets. Session 4 adds the second benefit: deployable code in `src/`, tests in `tests/`, which are typically not included in the build.",
    section=4,
    source="S4 slide 22",
    origin="slides",
    verified="source",
)

mcq(
    "entry-point",
    level="exam",
    skills=["read-diff", "read-tool-output"],
    stem=md(
        "Part of `pyproject.toml` in `2ecad20` *Move the report into the package behind a typer CLI*:",
        fence("diff", DIFF_2ECAD20_SCRIPTS),
        "A teammate who has not read the diff pulls the commit and types the command they used last week:",
        fence("console", SPAWN_2ECAD20),
        "Why?",
    ),
    right=(
        "The command is now called `expenses`; `expense-tracker` is gone",
        "`[project.scripts]` maps command names to objects. The old line was removed, so uv has no `expense-tracker` to start.",
    ),
    wrong=[
        ("`uv.lock` is out of date, so they should run `uv sync --upgrade`", "Nothing in the message is about versions or the lockfile; it names a command that does not exist."),
        ("typer is not installed yet, so they should reinstall uv and try again", "Reinstalling the tool never fixes a name that the project no longer defines."),
        ("`main()` was deleted from `__init__.py`, so Python crashed while starting", "`main()` did go, but Python never started: uv could not find a command with that name to spawn."),
    ],
    pos="a",
    explanation="Session 5: `expenses = \"expense_tracker.cli:app\"` reads as command `expenses`, module `expense_tracker.cli`, object `app`; \"rename either side and the command disappears.\" 2ecad20 replaced the line, so `uv run expenses report` works and `uv run expense-tracker` fails to spawn. Lab 01 lists the same symptom: `Failed to spawn` means `[project.scripts]` does not match the command you typed. Read the message, read the diff, fix the cause; deleting things or reinstalling tools is the careless student's move.",
    section=4,
    source="expense-tracker 2ecad20; S5 slide 5; labs/01-scaffold.md troubleshooting",
    origin="history",
    verified="run",
)

mcq(
    "v00-v01-user",
    level="exam",
    skills=["compare", "predict-output"],
    stem=md(
        "At v0.0 a user typed:",
        fence("bash", 'python tracker.py expenses.csv dining 20'),
        "Which statement is true for the same user at v0.1?",
    ),
    right=(
        "They type `uv run expenses report --category dining --min 20`: same report",
        "The report code moved but did not change, so the output is identical. What changed is how it is called; `add` is new as well.",
    ),
    wrong=[
        ("The report text changes, because typer now formats what the command prints", "typer only reads the arguments. The same report code builds and prints the lines, so the v0.0 and v0.1 reports are byte for byte the same."),
        ("The old command still works, because `tracker.py` stays at the root for compatibility", "2ecad20 moved `tracker.py` into `src/expense_tracker/report.py`; there is no script left at the root."),
        ("They must put the options before the path, because typer reads options first", "Options can go before or after the path; `uv run expenses report --category dining --min 20` uses the default path."),
    ],
    pos="c",
    explanation="Between v0.0 and v0.1 the user-facing change is the interface: a named command with options and a generated `--help` instead of positional words, and a second command, `add`. The report text is the same, which you can check by saving both outputs and comparing them. For the developer the change is bigger: a name, a version, pinned dependencies, an entry point, a `src/` layout and a README. Keeping 'what the user sees' apart from 'what the developer gets' is the habit the exam asks for.",
    section=4,
    source="expense-tracker v0.0..v0.1; S4 slide 23; S5 slide 4",
    origin="history",
    verified="run",
)

open_q(
    "open-bc9ef3d",
    level="exam",
    skills=["read-diff", "compare", "judgement"],
    stem=md(
        "A diff from the expense-tracker history (trimmed: the hunk that adds `import csv`, `import datetime` and `import os` is not shown):",
        fence("diff", DIFF_BC9EF3D),
        "Two candidate commit messages:\n\n- A: `Update cli.py`\n- B: `Add an add command that writes to data/`",
    ),
    parts=[
        part(
            "1",
            "What does this change do?",
            2,
            "It adds an `add` command: merchant, category and amount are required and the date defaults to today. It appends a row to `data/expenses.csv`, writing the header first if the file is new, and git now ignores `data/`.",
            [
                "Names a new `add` command that appends an expense to `data/expenses.csv`.",
                "Mentions one detail of its behaviour: the header written only for a new file, the date defaulting to today, or `data/` being git-ignored.",
            ],
            "Answers that list every line ('it imports os, it checks if data exists, it opens a file') describe the code, not the change. Missing the `.gitignore` hunk is common: it is the reason real spending never reaches the public repo. Saying it 'changes the report' is wrong: `report` is untouched.",
        ),
        part(
            "2",
            "Which message is better for someone reading the history six months later, and why?",
            2,
            "B. It says what a user can now do, so someone looking for when `add` arrived, or why `data/` exists, finds it in the log. A names a file that changes in many commits and says nothing without the diff.",
            [
                "Chooses B.",
                "Reason: B states the new behaviour (and where it writes); A names only the file, so it cannot be told apart from other commits and forces the reader into the diff.",
            ],
            "'B is longer so it is better' gives the wrong reason; length is not the point. Choosing A because 'it says which file changed' misses that `--stat` already shows the file; the subject is for what changed.",
        ),
        part(
            "3",
            "Name one test you would add for this change, in words.",
            2,
            "In an empty temporary folder, run `add \"Bar Ramon\" dining 12.50` through the command-line runner and check that `data/expenses.csv` exists with the header and one row ending in 12.50; running it twice still gives one header.",
            [
                "Runs the test in a fresh temporary directory (not the real `data/` folder).",
                "States what is checked: the file exists with a header and the new row, or the header appears only once after two adds.",
            ],
            "A test that reads the real `data/expenses.csv` passes only on the author's laptop: session 8 calls these 'tests that need your laptop'. Answers that check only 'it prints added' miss the file, which is the behaviour that matters.",
        ),
    ],
    explanation="Sample Q8's shape again. The key judgement in part 2 is the same: a subject that names a file instead of a behaviour fails the reader. Part 3 is session 8's 'parts that touch the world': `add` writes a file, so a good test uses `tmp_path` with `monkeypatch.chdir` and `CliRunner`, exactly the slide-22 example, and never depends on files that only exist on one machine.",
    section=4,
    source="expense-tracker bc9ef3d; sample Q8; S8 slides 20–22",
    origin="teacher-variant",
    variant_of="sample-paper-q08",
    verified="run",
)

# ---------------- s5: v0.2 ----------------

mcq(
    "which-refactoring",
    level="exam",
    skills=["concept", "judgement"],
    stem="Which of these commits from the expense-tracker history is a refactoring?",
    right=(
        "`5e9466d` Replace magic numbers with named constants",
        "Numbers get names; the program prints exactly the same report before and after.",
    ),
    wrong=[
        ("`bc9ef3d` Add an add command that writes to data/", "A new command is new behaviour: a feature."),
        ("`6efdf9d` Filter by category and ignore small amounts", "It adds guard clauses, the shape session 6 recommends, but they skip rows that used to be counted. The report changes, so it is a feature."),
        ("`1e421bc` Remove duplicates with a seen-set", "The green step: the stub returned its input, and now duplicates are dropped. Two tests that failed now pass, so behaviour changed."),
    ],
    pos="d",
    explanation="Session 7: \"Refactoring: change the structure, keep the behaviour. If the output changes, it was not a refactoring.\" 5e9466d changes the code's structure (constants instead of literal `20`, `40`, `e[3]`) and the report is identical, so it is session 7's *extract constant* move. Adding a command or a filter changes what the program does, and so does turning a stub into working code; naming the numbers does not. Sample question 2 asks the same thing with invented changes.",
    section=5,
    source="S7 slide 5; S6 slide 16; sample Q2",
    origin="teacher-variant",
    variant_of="sample-paper-q02",
    verified="source",
)

mcq(
    "deleted-comment",
    level="exam",
    skills=["read-diff", "concept"],
    stem=md(
        "`5e9466d` deletes a comment while it adds a constant:",
        fence("diff", "-            # skip rows that do not have all four fields\n-            if len(row) == 4:\n+            if len(row) == FIELDS_PER_ROW:"),
        "Why was deleting the comment the right call?",
    ),
    right=(
        "It said what the next line does, and the constant now says that itself",
        "Session 6: a comment that explains what the code does is a failure of naming. Fix the name, delete the comment.",
    ),
    wrong=[
        ("Every comment is a failure of naming, so all of the comments in a file should go", "Session 6 keeps comments for why: a business rule, a workaround with its reason, a deliberate oddity."),
        ("ruff reported the comment as an error that had to be fixed", "ruff was not configured in this project until 04d699f, and it does not flag comments like this one."),
        ("Comments slow Python down, so clean code keeps them to a minimum", "Comments cost nothing at run time; the argument is about the reader, not speed."),
    ],
    pos="a",
    explanation="Session 6's rule is narrow: \"A comment that explains what the code does is a failure of naming.\" `# skip rows that do not have all four fields` restates `if len(row) == 4:`, so once `4` has a name the comment adds nothing and can drift out of date. Session 6 also shows a legitimate comment on this very line, one that says why: \"Suppose the bank's export sometimes ends with a summary row with fewer fields.\" That one would stay, because the code cannot say it.",
    section=5,
    source="expense-tracker 5e9466d; S6 slides 11, 13–14",
    origin="history",
    verified="run",
)

mcq(
    "v01-v02-user",
    level="hard",
    skills=["read-tool-output", "compare"],
    stem=md(
        "Five commits separate v0.1 from v0.2:",
        fence("console", STAT_V01_V02),
        "You run `uv run expenses report --category dining --min 20` on the sample data at v0.1 and again after each of the five commits, saving each output and comparing them with `diff`. What do you find?",
    ),
    right=(
        "Identical every time: on this data nothing a user sees changes",
        "These are refactorings: every output matches v0.1 byte for byte, while the developer gets constants, names, small functions, a type and hints.",
    ),
    wrong=[
        ("The output changes at `017f926`, because a dataclass prints differently from a tuple", "`format_report` builds each line from fields with an f-string or `+`, never by printing the object, so the text is the same."),
        ("The output changes at `04d699f`, because f-strings round differently from `%.2f`", "`f\"{amount:.2f}\"` and `\"%.2f\" % amount` give the same two-decimal text."),
        ("The output changes at `9d6c607`, because the largest expense is now found in its own function", "Moving a loop into a function does not change its answer here; the sample data has positive amounts."),
    ],
    pos="b",
    explanation="This is the session 6 exercise run on the real history: \"The output must stay identical\", checked with `diff before.txt after.txt`. 150 changed lines in `report.py` and nothing changes on screen, which is exactly what a refactoring promises. The developer gains everything: names that say what they hold, functions with one job, an `Expense` type, hints that mypy can check. One limit: identical output on one input is evidence, not proof (see the refunds question in this module).",
    section=5,
    source="S6 slide 30; S7 slide 5; expense-tracker v0.1..v0.2",
    origin="history",
    verified="run",
)

sort_q(
    "sort-moves",
    level="exam",
    skills=["read-diff", "concept"],
    stem="Each line below is a real change from the five v0.2 commits. Put each under the refactoring move from session 7 that it is.",
    categories=[
        ("constant", "Extract constant"),
        ("rename", "Rename"),
        ("separate", "Separate I/O from logic"),
        ("extract", "Extract function"),
        ("type", "Introduce a type"),
    ],
    items=[
        ('`print("-" * 40)` becomes `print("-" * RULE_WIDTH)`', "constant", "A bare number gets a name that says what it is (5e9466d)."),
        ("`if len(row) == 4:` becomes `if len(row) == FIELDS_PER_ROW:`", "constant", "Same move: the 4 now has a name, and the comment can go (5e9466d)."),
        ("`def calculate_totals(x, y, z):` becomes `def total_by_category(expenses, category, minimum):`", "rename", "The function says what it returns and the parameters say what they hold (f3bb801)."),
        ("`grand` becomes `grand_total`", "rename", "A variable renamed so it says what it holds (f3bb801)."),
        ("The `print` calls in `run()` become `lines.append(...)` in `format_report`, which returns the lines", "separate", "Computation is not output: the formatting returns data and only `run()` prints (9d6c607)."),
        ("The loop that finds the biggest amount leaves `run()` and becomes `largest_expense(expenses)`", "extract", "Session 7's own example of extract function: `largest_expense` out of `run()` (9d6c607)."),
        ("`(row[DATE], row[MERCHANT], row[CATEGORY], float(row[AMOUNT]))` becomes `Expense(date=..., merchant=..., category=..., amount=...)`", "type", "A tuple is a missing type; the frozen dataclass names the fields (017f926)."),
        ("`expense[AMOUNT]` becomes `expense.amount`", "type", "Once `Expense` exists, every index lookup becomes a named field (017f926)."),
    ],
    explanation="Session 7's table names the moves you watched in session 6: extract constant (magic numbers to `STANDARD_VAT_RATE`-style names), rename (`calculate_totals` to `total_by_category`), separate I/O from logic (`run()` split into read, compute, format), introduce a type (tuple to `Expense`), extract function (`largest_expense` out of `run()`). Each item keeps the report identical, which is what makes it a refactoring and not a feature.",
    section=5,
    source="S7 slides 3, 5; S6 slide 31; expense-tracker 5e9466d, f3bb801, 9d6c607, 017f926",
    origin="history",
    verified="run",
)

mcq(
    "refunds-only",
    level="hard",
    skills=["read-code", "read-tool-output"],
    stem=md(
        "At `v0.2`, a group member records a refund. `refund.csv` has a single data row, `2025-08-02,Zara,clothing,-35.00`. In `report.py`, `total_by_category` skips an expense when `expense.amount < minimum`, the `--minimum` option defaults to `0.0`, and `largest_expense` compares the amounts of all rows with no filter. The report prints:",
        fence("console", REFUND_RUN),
        "What explains a total of `0.00` next to a largest expense of `-35.00`?",
    ),
    right=(
        "The refund is below the default minimum of `0.0`, so `total_by_category` drops it, but `largest_expense` sees every row",
        "Two functions apply two different rules to the same file. `-35.00 < 0.0` makes the totals guard skip the row, and `largest_expense` has no guard.",
    ),
    wrong=[
        ("`format_report` hides negative categories when it prints, but still adds them to the total", "The total is computed from the list `total_by_category` returns, which is empty here. `format_report` prints what it is given."),
        ("The refund and the total cancel out, because `total_by_category` adds the `-35.00` to zero", "A single refund would give a total of `-35.00`, not `0.00`. The row never reached the sum."),
        ("`read_expenses` skips the row, and `largest_expense` reads it again from the file", "Both functions work on the same list. If `read_expenses` had skipped the row, the largest line would not appear."),
    ],
    pos="a",
    explanation="Read the code against the output. `total_by_category` has two guards: the category filter, which is off when the category is empty, and `if expense.amount < minimum: continue`. With the default minimum of `0.0`, a negative amount fails that test, so no category is built and the total is `0.00`. `largest_expense` has no filter, so it reports the refund as the largest of one. Real run on v0.2. A `diff before.txt after.txt` check could never reveal this: the sample file has no refund. Choosing edge cases on purpose, as session 8 teaches, is how a test would.",
    section=5,
    source="expense-tracker v0.2 report.py; S6 slide 30; S8 slide 11",
    origin="history",
    verified="run",
)

mcq(
    "empty-file",
    level="beyond",
    skills=["read-diff", "judgement"],
    stem=md(
        "`04d699f` changed the error handling around reading the file:",
        fence("diff", "-    except:\n-        print(\"could not read \" + path)\n+    except (OSError, ValueError):\n+        print(f\"could not read {path}\")"),
        "`read_expenses` starts with `next(reader)` to skip the header. Before this commit, a completely empty (0-byte) `expenses.csv` printed `could not read expenses.csv`. After it, the command ends in a long traceback whose last line is `StopIteration`. What is the best reading?",
    ),
    right=(
        "Narrowing was right: it exposed a case that now needs a decision and a test",
        "`next()` on an empty file raises `StopIteration`, which is neither `OSError` nor `ValueError`. The bare `except:` had been hiding it.",
    ),
    wrong=[
        ("Go back to the bare `except:`, because it used to handle every case gracefully", "It 'handled' a typo or Ctrl-C the same way, as \"could not read\". Hiding the crash does not fix it."),
        ("Add `StopIteration` to the tuple and move on, since the crash is gone", "That silences one symptom without deciding what an empty file should mean, and without a test the next change can break it again."),
        ("Nothing to do: the commit is a refactoring, so its behaviour cannot have changed", "The subject says hints and ruff, but this line changes how the program fails. Being filed under 'ruff clean' does not make it behaviour-free."),
    ],
    pos="a",
    explanation="Session 7: \"Catch only what you can handle\" and \"fail loudly\". The bare `except:` turned every failure into the same message; narrowing it is correct, and the first thing it reveals is an input the code never considered. The good next step is to decide what an empty file means (no expenses, or a clear error on stderr with exit 1) and add a test that pins it, the way v0.4 pins the missing-file case. Even at v0.4 a 0-byte file still ends in `StopIteration`: no test covers it.",
    section=5,
    source="expense-tracker 04d699f; S7 slides 17–19",
    origin="history",
    verified="run",
)

open_q(
    "open-ruff",
    level="hard",
    skills=["read-tool-output", "judgement"],
    stem=md(
        "Take the code at `017f926` and add what `04d699f` adds to `pyproject.toml`: ruff as a dev dependency, `select = [\"E\", \"F\", \"I\", \"UP\", \"B\", \"SIM\"]` and line length 100. ruff then reports:",
        fence("console", RUFF_017F926),
    ),
    parts=[
        part(
            "1",
            "Which of these findings point at a risk to correctness, and which are about layout or style? Give a reason for each group.",
            2,
            "`E722` (bare `except`) is a real risk: it turns every bug, a typo or Ctrl-C included, into \"could not read\". `SIM115` too: a file opened without `with` may stay open. `UP031`, `I001` and `E501` are style: the program behaves the same.",
            [
                "Names `E722` as a correctness risk with the reason (it hides every error behind one message).",
                "Names the `UP031` / `I001` / `E501` group as layout or style that does not change behaviour (or names `SIM115` as a risk with a reason).",
            ],
            "Treating all ten as equal ('fix them all, they are all errors') misses the judgement asked for. Some students call `E501` dangerous because of the word 'error'; a long line runs exactly like a short one. Saying `E722` is 'bad style' without the consequence earns one mark at most.",
        ),
        part(
            "2",
            "04d699f's subject is `Add type hints and make the code ruff clean`. Six months later you want the commit that removed the bare `except:`. Will the log help? What would have been better?",
            2,
            "No. The subject names tools, not the behaviour change, so a search for 'except' or 'error' finds nothing. The narrowing deserved its own commit, such as `Catch only file and number errors when reading`.",
            [
                "Says the subject does not mention the `except` change, so the reader cannot find it from the log.",
                "Proposes a separate commit (or a subject) that names the change in behaviour.",
            ],
            "'Yes, ruff clean implies the except was fixed' assumes the reader knows ruff's rule codes and still does not tell them which commit. Proposing a longer subject that lists every ruff rule fixed misses one logical change per commit.",
        ),
        part(
            "3",
            "After 04d699f ruff reports nothing. Name one kind of problem ruff cannot tell you about, with an example from this history.",
            2,
            "Whether the program does the right thing. At v0.2 ruff is clean, yet a `--category dining` report still names a home expense as the largest, and a 0-byte file crashes. That is what tests are for.",
            [
                "Names behaviour or logic errors (or type errors) as outside ruff's reach.",
                "Gives a concrete example from the history: the largest expense ignoring the filter, the 0-byte file crash, or a `None` that is not handled.",
            ],
            "'Ruff catches everything important' is the misconception this part targets. An answer naming a generic 'logic bug' with no example earns one mark.",
        ),
    ],
    explanation="Session 6: \"Read the code, read the message, fix the cause.\" Reading ruff output well means telling a style rule from a rule that guards behaviour. E722 is the one that matters here, and fixing it changed how the program fails, which the commit subject does not say. The CI referee runs ruff, mypy and pytest because each catches a different kind of problem.",
    section=5,
    source="expense-tracker 017f926, 04d699f; S6 slide 27; S7 slide 18",
    origin="history",
    verified="run",
)

# ---------------- s6: v0.3 ----------------

mcq(
    "mypy-v01",
    level="exam",
    skills=["read-tool-output", "judgement"],
    stem=md(
        "Midway through v0.2, at commit `017f926` (the `Expense` dataclass exists, the type hints are not written yet), the same command from session 7 prints:",
        fence("console", MYPY_017F926),
        "What is the right reading, and how much work is it?",
    ),
    right=(
        "One cause: five functions have no signature; hinting them clears the five calls as well",
        "Five `no-untyped-def` errors name the functions. The five `no-untyped-call` errors only repeat that a call goes to one of them, so they vanish with the signatures.",
    ),
    wrong=[
        ("Ten separate problems, so each of the ten lines needs its own fix", "Half of the lines are consequences. A call is untyped only because the function it calls has no signature."),
        ("Five real bugs for users and five style warnings that ruff would also report", "None of them is a bug: v0.2 runs fine. And `ruff check` does not read types, so it would not report them."),
        ("Write the five signatures and silence the five calls with `# type: ignore[no-untyped-call]`", "The five calls clear on their own once the functions are hinted. Adding ignores keeps comments that would hide a real problem later."),
    ],
    pos="d",
    explanation="Session 7's method: read the first error, find the kind, fix the cause, run again. Here there are two codes but one cause. `no-untyped-def` marks a function whose signature has no hints (`read_expenses`, `total_by_category`, `largest_expense`, `format_report`, `run`), and `no-untyped-call` marks each place that calls one of them from typed code. Add the five signatures and all ten lines go. In the history, `04d699f` does exactly that, and the same command then prints `Success: no issues found in 3 source files`. Work the kinds, not every line.",
    section=6,
    source="S7 slides 9-10; expense-tracker 017f926, 04d699f",
    origin="history",
    verified="run",
)

mcq(
    "strict-no-code",
    level="hard",
    skills=["read-tool-output", "read-diff"],
    stem=md(
        "The commit tagged `v0.3`:",
        fence("console", STAT_88B83C3),
        fence("diff", DIFF_88B83C3),
        "Strict type checking is switched on, yet no `.py` file changes. Why could the author do that?",
    ),
    right=(
        "v0.2 had already annotated every function, so strict mode found nothing",
        "Run at v0.2, `mypy --strict src` already prints `Success: no issues found in 3 source files`.",
    ),
    wrong=[
        ("`strict = true` applies only to the `tests` folder, which does not exist yet", "The setting applies to everything mypy checks; CI runs `mypy src tests`."),
        ("The setting is ignored unless you also type `--strict` on the command line each time", "Session 7: `strict = true` in `[tool.mypy]` turns strict mode on for every run, which is why CI enforces it."),
        ("The type fixes are hidden in the 280 changed lines of `uv.lock`", "`uv.lock` pins package versions: here mypy, pytest and their dependencies. It holds no code."),
    ],
    pos="c",
    explanation="Strict mode reports missing annotations, types that disagree and `None` that is not handled. v0.1 had four errors of the first kind; v0.2's hints removed them, and 04d699f also made the types agree (`grand_total = 0.0`, `totals.get(..., 0.0)`), the fix session 7 gives for the second kind. So v0.3 could turn strict on as pure configuration. The `uv.lock` lines are there because two new dev tools now have pinned versions, committed with the `pyproject.toml` change so `uv sync --locked` agrees.",
    section=6,
    source="expense-tracker 88b83c3; S7 slides 10–11",
    origin="history",
    verified="run",
)

mcq(
    "is-15836e1-refactor",
    level="hard",
    skills=["read-diff", "read-tool-output", "judgement"],
    stem=md(
        "`15836e1` *Move printing and exiting out of the report module* deletes `run()` from `report.py` (where it used `print` and `sys.exit(1)`) and changes the `report` command:",
        fence("diff", DIFF_15836E1_CLI),
        "The same command, run just before and just after the commit (`> out.txt` saves what goes to standard output, `2> err.txt` what goes to standard error). Before:",
        fence("console", TRANSCRIPT_04D699F),
        "After:",
        fence("console", TRANSCRIPT_15836E1),
        "Is 15836e1 a refactoring?",
    ),
    right=(
        "Mostly: same report and exit code, but the error now goes to stderr on purpose",
        "The transcripts show it: same exit code 1, message in `out.txt` before and in `err.txt` after.",
    ),
    wrong=[
        ("Yes, purely: nothing that a user or a script could observe has changed at all", "A script that captures standard output used to see the message and now does not."),
        ("No, it is a feature: the `report` command now does more than before", "It does exactly the same work; only where the code lives and where the error goes changed."),
        ("No, it is a bug fix: a missing file used to exit with 0 and now exits with 1", "Both transcripts show exit code 1: `sys.exit(1)` before, `typer.Exit(1)` after."),
    ],
    pos="b",
    explanation="Read the diff for observable effects. `typer.echo(line)` prints the report exactly as `print` did, and `typer.Exit(1)` exits with the same code as `sys.exit(1)`. The one difference is `err=True`: the message now goes to standard error. That is session 7's \"fail loudly, at the boundary: the shell catches it, prints to stderr, exits non-zero\". So the commit is a structural move plus one small, intended change. The careful answer names both; v0.4's CliRunner test then checks the stderr message, and that test fails against v0.2's code.",
    section=6,
    source="expense-tracker 04d699f, 15836e1; S7 slides 5, 19",
    origin="history",
    verified="run",
)

mcq(
    "report-py-still",
    level="hard",
    skills=["read-code", "concept"],
    stem="After `15836e1`, session 8 describes v0.3 as \"the functional core from Tuesday: `report.py` has no `print`, no `sys.exit`.\" Which of these does `report.py` still do at v0.3?",
    right=(
        "Open and read the CSV file, inside `read_expenses`",
        "`read_expenses(path)` still contains `with open(path)`. It lives in `report.py`, but it is the shell that calls it.",
    ),
    wrong=[
        ("Print the report lines with `print`, as `run()` did", "The shell does that now: `typer.echo(line)` in `cli.py`."),
        ("Call `sys.exit(1)` when the file is missing", "That moved to `cli.py` as `raise typer.Exit(1)`, and `import sys` was deleted from `report.py`."),
        ("Write the `could not read` message to standard error", "Also the shell's job now: `typer.echo(..., err=True)` in the `report` command."),
    ],
    pos="a",
    explanation="The slide's claim is exact: no `print`, no `sys.exit`. It does not say no I/O at all. Session 7's 'on the demo' slide marks `expenses = read_expenses(path)` as \"shell: touches a file\" and `total_by_category` and `format_report` as \"core: pure\". The reading function sits in the same module but belongs to the edge, which is why v0.4 tests it separately with `tmp_path` while the pure functions are tested with plain lists.",
    section=6,
    source="S8 slide 13; S7 slides 13–14; expense-tracker 15836e1",
    origin="history",
    verified="source",
)

mcq(
    "lockfile",
    level="exam",
    skills=["read-tool-output", "judgement"],
    stem=md(
        "The workflow added in `0e05065` runs five steps in order. A job stops at its first failing step, and the steps after it are shown as skipped. After your push the run shows:",
        "| Step | Result |\n|---|---|\n| Install dependencies from the lockfile | passed |\n| Lint (`uv run ruff check .`) | failed |\n| Formatting (`uv run ruff format --check .`) | skipped |\n| Types (`uv run mypy src tests`) | skipped |\n| Tests (`uv run pytest`) | skipped |",
        "The log of the Lint step ends with:",
        fence("console", RUFF_E501),
        "A teammate says: \"It is only a long comment line, the code is fine, merge it.\" What do you conclude?",
    ),
    right=(
        "Nothing is known yet about Formatting, Types or Tests; fix the line, push, and read the next run",
        "Skipped means not run. The first red step hides everything after it, so the next run may show another failure.",
    ),
    wrong=[
        ("Skipped steps count as passed, so only the long comment stands between you and green", "Skipped is not passed: those three checks have not looked at the code in this run."),
        ("Re-run the job once, since a skipped step is a flaky step and usually runs the second time", "The steps are skipped because Lint failed. Another run stops at the same place."),
        ("Remove the Lint step from the workflow so that the later steps run and show what else is wrong", "That weakens the referee to get a different answer. Fix the finding instead; the group promised these checks."),
    ],
    pos="a",
    explanation="The workflow in `0e05065` installs from the lockfile and then runs Lint, Formatting, Types and Tests as separate steps. A job stops at its first failing step, so a red Lint step hides the other three. Skipped does not mean passed. The honest reading is that only the lockfile install and Lint are known, and Lint failed. Shorten the comment (the finding names the file, line 23, and the column where the limit of 100 is crossed), push, and read what the new run says; it may be red at a later step. Do not remove a step to see more: the checks are the group's Definition of Done. Real run: ruff 0.16.9 printed the finding on a copy of v0.4 with a long comment added.",
    section=7,
    source="expense-tracker 0e05065; S3 slide 14; S6 slide 27",
    origin="history",
    verified="run",
)

open_q(
    "open-15836e1",
    level="hard",
    skills=["read-diff", "concept", "judgement"],
    stem=md(
        "A commit from the expense-tracker history, `f3d9870`. It adds one file:",
        fence("diff", DIFF_F3D9870),
        "Two candidate commit messages:\n\n- A: `Add tests`\n- B: `Test reading a file and the missing-file exit code`",
    ),
    parts=[
        part(
            "1",
            "What do the two new tests check, in words?",
            2,
            "The first writes a CSV with one broken row and checks that only the two good rows are read. The second runs `report` on a missing file and checks for exit code 1 and the message on stderr.",
            [
                "First test: a row that does not have four fields is skipped, the other rows are read",
                "Second test: a missing file gives exit code 1 and the explanation on stderr",
            ],
            "\"It tests the code\" says nothing. Saying the second test checks the report output misses that it checks the exit code and the stream the message uses, the two things session 7 cares about.",
        ),
        part(
            "2",
            "Why does the first test use `tmp_path` and the second does not need it? What does the second test rely on from an earlier commit?",
            2,
            "The first needs a real file, so it writes one in a temporary folder that disappears afterwards; a missing file needs no setup. The second relies on `15836e1`, which moved the error to stderr with exit code 1.",
            [
                "`tmp_path` gives a throwaway folder for a file the test must create; a missing file needs no setup",
                "Relies on the earlier change that moved the error to stderr with exit code 1 (functional core, imperative shell)",
            ],
            "\"tmp_path makes it faster\" misses the point: it keeps the test independent of anything on disk. For the second half, the marker wants the earlier commit named or described, since this test would fail against v0.2's `print` and `sys.exit`.",
        ),
        part(
            "3",
            "Which message is better for a reader six months later, and why? Name one more test the file deserves, in words.",
            2,
            "B: it says what is covered, so someone looking for where a missing file is tested finds it. A fits any test commit. Another test: a non-numeric amount gives exit code 1 and the same message.",
            [
                "Chooses B because it states what the tests cover; A does not distinguish this commit",
                "A sensible extra test in words (a bad amount, an empty file, a header-only file) with the expected result",
            ],
            "\"B is longer\" is not a reason. A test with no expected result (\"test a bad file\") earns nothing: say what should happen, such as exit code 1.",
        ),
    ],
    explanation="Sample Q8's shape on a commit that adds tests instead of code. A test commit is read for what it pins down: here a rule about bad input (rows with the wrong number of fields are skipped) and a boundary rule (a missing file ends in exit code 1 with the message on stderr). The second test only makes sense after `15836e1`, which is why the history is worth reading in order. Part 2 is session 8's tools: `tmp_path` for a file you create, the command-line runner for the shell.",
    section=7,
    source="expense-tracker f3d9870, 15836e1; S8 slides 20-21; sample Q8 shape",
    origin="history",
    verified="run",
)

open_q(
    "open-story",
    level="hard",
    skills=["compare", "concept", "judgement"],
    stem=md(
        "The eleven commits after v0.0, up to v0.3:",
        fence("console", LOG_V00_V03),
        "Using the history, explain how the code changed and why each step made the next one possible.",
    ),
    parts=[
        part(
            "1",
            "From v0.0 to v0.1: what changed, and what did it make possible?",
            2,
            "The script became a project: `pyproject.toml`, a committed `uv.lock`, a `src/` package, an `expenses` command with options, `add`, a README. It made the code installable from a clean clone with pinned versions, which every later tool and test relies on.",
            [
                "Names the packaging step (uv project, `src/` layout, typer CLI or entry point, lockfile).",
                "Says what it enabled: installable, importable package with pinned tools, so linters, type checks and tests can run the same everywhere.",
            ],
            "Listing files without saying why they matter earns one mark. Saying the report changed is wrong: its output is identical.",
        ),
        part(
            "2",
            "From v0.1 to v0.2: what changed, and what did it make possible?",
            2,
            "Five refactorings with identical output: constants, real names, `run()` split into read, compute and format, a frozen `Expense` instead of a tuple, hints. Small typed functions with one job are what can be checked strictly and moved apart.",
            [
                "Names at least two of the clean-code moves and says the output stayed the same.",
                "Says what it enabled: functions with one job and hints, so strict mypy passes and the I/O can be moved out (or tests can call them).",
            ],
            "'Made the code nicer' names no move and no consequence. Forgetting that behaviour was kept misses what makes these refactorings.",
        ),
        part(
            "3",
            "From v0.2 to v0.3: what changed, and what did it make possible?",
            2,
            "Printing and exiting moved from `report.py` into `cli.py`, so the core only takes and returns values; strict mypy and pytest were switched on. That let v0.4 test the core with plain lists and check the error on stderr with `CliRunner`.",
            [
                "Names the core and shell split (print and exit moved to `cli.py`) or strict mode switched on.",
                "Says what it enabled: tests on plain data without files, or the stderr test at the edge.",
            ],
            "Mixing up the order (saying tests came before the core and shell split) misreads the history. Naming strict mode alone without the move of the I/O misses the main change.",
        ),
    ],
    explanation="The history is a chain, and each link is small. Packaging gives tools something stable to run on; clean code gives them something checkable; the core and shell split gives tests something they can call without the outside world. The full-marks answer names each step and its consequence for the next one, in the course's own terms.",
    section=6,
    source="expense-tracker v0.0..v0.3; S4 slides 19–26; S6 slides 18–31; S7 slides 3, 13–15",
    origin="history",
    verified="run",
)

# ---------------- s7: v0.4 ----------------

mcq(
    "stub-why",
    level="core",
    skills=["read-diff", "concept"],
    stem=md(
        "`e1b96de` *Add failing tests for remove_duplicates* adds five tests and this to `report.py`:",
        fence("diff", DIFF_E1B96DE_STUB),
        "Why add a function that obviously does the wrong thing?",
    ),
    right=(
        "So the tests import it and fail on their assertions, not on an import",
        "Session 8: \"First a stub, return expenses, so the failure says something.\"",
    ),
    wrong=[
        ("So CI stays green while the real code is being written", "Two of the five tests fail against the stub; CI would be red for this commit."),
        ("Because the seen-set version was too slow to commit yet", "Speed never comes into it; the stub exists before any real version does."),
        ("Because mypy refuses to check a test for a function that has not been written", "mypy does check the test. Without the stub it reports the missing name as an error, and pytest stops at collection with an `ImportError` before running a single test. The stub is there so the failure is about duplicates, not about a missing name."),
    ],
    pos="d",
    explanation="Red means a test fails for the right reason. Without the stub, `from expense_tracker.report import Expense, remove_duplicates` fails and pytest reports an import error: true, but useless. With `return expenses`, the tests run and the two that matter fail on their assertions, showing exactly what the function does not yet do. \"Red is information, not a problem.\" The next commit, 1e421bc, replaces the stub with the smallest code that passes.",
    section=7,
    source="S8 slides 5, 14; expense-tracker e1b96de",
    origin="slides",
    verified="source",
)

mcq(
    "red-output",
    level="exam",
    skills=["read-tool-output"],
    stem=md(
        "The tests from `e1b96de`, run against the stub that returns its input:",
        fence("console", PYTEST_E1B96DE),
        "What can you conclude?",
    ),
    right=(
        "The two failing tests have a duplicate in their input; the other three pass by luck",
        "Session 8: \"two fail, the others pass by luck.\" The `E` lines show the stub left the extra `Bar Ramon` in place.",
    ),
    wrong=[
        ("The stub is broken, so it must be fixed before anything is committed to the repository", "The stub is wrong on purpose. This output is the red step, and it is the information the tests were written to produce."),
        ("The tests are flaky, so rerun them until all five new ones pass", "Nothing here is random. The same input gives the same failure every time."),
        ("22 passed, so `remove_duplicates` is already correct for most inputs", "19 of the 22 are the older tests of the core and the I/O. Of the five new ones, three pass by luck."),
    ],
    pos="a",
    explanation="Read the summary line and the `E` lines. `Left contains one more item: Expense(... 'Bar Ramon' ...)` says the result kept a duplicate the test expected to be removed. The passing tests (an empty list, two different expenses, the same merchant on another day) have no duplicates, so a function that returns its input happens to pass them. That is why session 8 adds edge cases on purpose: the many-copies case fails with the stub, so it earns its place.",
    section=7,
    source="S8 slides 7, 14; expense-tracker e1b96de",
    origin="history",
    verified="run",
)

mcq(
    "next-two",
    level="exam",
    skills=["read-diff", "concept"],
    stem=md(
        "The two commits after the red step. `1e421bc`:",
        fence("diff", DIFF_1E421BC),
        "then `d3df52b`:",
        fence("diff", DIFF_D3DF52B),
        "`uv run pytest -q` ends with `24 passed` after each of them. Which describes them?",
    ),
    right=(
        "1e421bc is the simplest passing code; d3df52b restructures it, tests still green",
        "Green, then refactor: first make it work, then make it clean, with the tests as the net.",
    ),
    wrong=[
        ("1e421bc is a refactoring of the stub, and d3df52b fixes a bug in the seen-set", "The stub did nothing, so 1e421bc adds behaviour; and nothing was broken at 1e421bc, all 24 passed."),
        ("d3df52b changes behaviour: a dict does not keep order, so expenses come back shuffled", "Dictionaries keep insertion order, which is why the 'first one kept' test still passes."),
        ("d3df52b was needed because the seen-set version in 1e421bc still failed two tests", "The suite was green at 1e421bc; d3df52b is the clean-up step, not a repair."),
    ],
    pos="d",
    explanation="Session 8's cycle: red (write the test, watch it fail), green (\"the smallest code that passes. Not elegant. Nobody asked for elegant yet\"), refactor (\"clean up, with the test as your safety net... Run the tests: still green. That is what 'refactoring' means\"). Three commits, three steps, each one logical change. `dict.fromkeys` keeps the first occurrence in order because dict keys are unique and insertion order is preserved; it works on `Expense` only because the dataclass is frozen.",
    section=7,
    source="S8 slides 15–16; expense-tracker 1e421bc, d3df52b",
    origin="history",
    verified="run",
)

mcq(
    "frozen-removed",
    level="hard",
    skills=["read-tool-output", "read-code"],
    stem=md(
        "At v0.4 a teammate deletes `frozen=True` from `@dataclass(frozen=True) class Expense`, saying \"nothing changes an expense anyway\". They run the checks:",
        fence("console", FROZEN_RUN),
        "What explains this?",
    ),
    right=(
        "Without `frozen=True`, `Expense` is unhashable, so `dict.fromkeys` fails",
        "A plain dataclass with equality is unhashable. Session 8: frozen makes `Expense` hashable, and `remove_duplicates` depends on it.",
    ),
    wrong=[
        ("The tests compare expenses with `==`, which only works on frozen dataclasses", "Equality works on any dataclass; the 20 passing tests compare expenses with `==` too."),
        ("mypy should have flagged an unhashable `Expense`, so its settings must be wrong", "mypy runs strict and reports no issues; this is a run-time property the type hints do not express here. The tests are the check that catches it."),
        ("The four tests are flaky: run the suite again and they will pass", "The error is deterministic: `TypeError: unhashable type: 'Expense'` every time."),
    ],
    pos="c",
    explanation="Two sessions meet here. Session 6 chose `frozen=True` (\"it does not change after creation\"); session 8 cashed it in: \"Dictionaries keep insertion order, and `@dataclass(frozen=True)` makes `Expense` hashable. Session 6's frozen=True pays off here.\" Remove it and every test that puts an expense into `dict.fromkeys` fails. The fifth duplicate test passes only because an empty list hashes nothing. ruff and mypy are both green, which is why the referee runs pytest as well.",
    section=7,
    source="S6 slides 23–24; S8 slide 16; expense-tracker 017f926, d3df52b",
    origin="history",
    verified="run",
)

mcq(
    "v03-v04-user",
    level="hard",
    skills=["read-tool-output", "compare"],
    stem=md(
        "Everything between v0.3 and v0.4:",
        fence("console", STAT_V03_V04),
        "What changed for someone who only ever runs `uv run expenses report`?",
    ),
    right=(
        "Nothing: the report never calls the new function, so its output is the same",
        "The report prints the same totals at v0.3 and v0.4. The only source change is the new function, which nothing in the CLI calls.",
    ),
    wrong=[
        ("The totals drop, because six duplicate rows are now removed before totalling", "`remove_duplicates` works (420 rows become 414 when you call it), but the `report` command does not call it."),
        ("The report now refuses to run unless the whole test suite passes", "CI runs the tests on GitHub after a push; the program itself does not run them."),
        ("Errors now go to standard error instead of standard output", "That arrived at v0.3, with 15836e1, not in this range."),
    ],
    pos="b",
    explanation="Read the `--stat`: one workflow, three test files and four lines in `report.py`. `cli.py`, the only code the user runs, is untouched, so v0.4 is for the developer: a tested core, I/O tests at the edge, CI on every push, and a tested `remove_duplicates` ready to be wired in. Wiring it into the report would be a separate feature commit, with its own message and a test that the totals change.",
    section=7,
    source="expense-tracker v0.3..v0.4; S8 slides 13, 16",
    origin="history",
    verified="run",
)

open_q(
    "open-tdd",
    level="exam",
    skills=["read-tool-output", "concept"],
    stem=md(
        "The last three commits of the history:",
        fence("console", "$ git log --oneline --decorate -3\nd3df52b (HEAD -> main, tag: v0.4, origin/main, origin/HEAD) Use dict.fromkeys to drop duplicates in order\n1e421bc Remove duplicates with a seen-set\ne1b96de Add failing tests for remove_duplicates"),
        "At `e1b96de`, the tests run against a stub `remove_duplicates` that returns its input:",
        fence("console", PYTEST_E1B96DE_SHORT),
    ),
    parts=[
        part(
            "1",
            "Why were these tests committed failing, with a stub?",
            2,
            "It is the red step: the tests say what done means before the code exists, and watching them fail proves they can fail. With the stub they can import the function, so the failure is about behaviour (duplicates not removed), not an import error.",
            [
                "Red step: the tests define the behaviour before the code (they say what done means).",
                "The stub makes the failure informative (fails on the assertion, not on an import), or seeing it fail proves the test can catch the bug.",
            ],
            "'Because the author ran out of time' or 'to show CI working' miss the method. An answer that says only 'TDD' without what the red step achieves earns one mark.",
        ),
        part(
            "2",
            "What did each of the next two commits do?",
            2,
            "`1e421bc` is green: the smallest code that passes, a loop with a `seen` set that keeps the first of each expense. `d3df52b` is refactor: the same behaviour in one line with `dict.fromkeys`, and the same 24 tests stay green.",
            [
                "1e421bc: green, simplest code that makes the tests pass (the seen-set loop).",
                "d3df52b: refactor, same behaviour in cleaner code, tests still passing.",
            ],
            "Calling d3df52b a bug fix is the classic slip: nothing failed at 1e421bc. Describing both as 'improvements' without green and refactor misses the cycle.",
        ),
        part(
            "3",
            "d3df52b depends on a decision made much earlier, in v0.2. Which one, and why?",
            2,
            "`@dataclass(frozen=True)` in 017f926. `dict.fromkeys`, like the set in 1e421bc, needs hashable items, and a frozen dataclass is hashable. Without it, every `remove_duplicates` test with a non-empty list (four of the five) fails with `unhashable type: 'Expense'`.",
            [
                "Names `frozen=True` on `Expense` (017f926).",
                "Says why: dict keys and set members must be hashable, and frozen makes `Expense` hashable.",
            ],
            "'Because Expense is a dataclass' is half right: a non-frozen dataclass is not hashable. Pointing at the type hints misses it: hints do not make anything hashable.",
        ),
    ],
    explanation="Session 8's live cycle, as it sits in the history: red (e1b96de), green (1e421bc), refactor (d3df52b), three commits and three logical changes. The full-marks answer uses the cycle's names, says what each commit's tests showed, and connects the final one-liner back to session 6's `frozen=True`.",
    section=7,
    source="S8 slides 5, 13–16; expense-tracker e1b96de, 1e421bc, d3df52b, 017f926",
    origin="history",
    verified="run",
)

open_q(
    "open-v03-v04",
    level="hard",
    skills=["read-tool-output", "compare", "judgement"],
    stem=md(
        "Between the last two tags:",
        fence("console", LOG_V03_V04),
        fence("console", STAT_V03_V04),
    ),
    parts=[
        part(
            "1",
            "What changed for a user who runs `uv run expenses report`?",
            1,
            "Nothing: `cli.py` is not in the diff and the report does not call `remove_duplicates`, so the output is identical.",
            ["Says nothing changed for the user, with the reason (CLI untouched or `remove_duplicates` not called)."],
            "'The duplicates are gone from the report' is the tempting wrong answer: the function exists and is tested, but nothing calls it.",
        ),
        part(
            "2",
            "What changed for the developer?",
            2,
            "The core is covered by tests (a fixture, `parametrize`, edge cases), two tests check the edge (`tmp_path`, `CliRunner`), a CI workflow runs ruff, mypy and pytest on every push, and `remove_duplicates` exists with its tests.",
            [
                "Tests of the pure core plus one or two I/O tests.",
                "CI on every push (or the tested `remove_duplicates`).",
            ],
            "Listing file names from the `--stat` without saying what they give the developer earns one mark.",
        ),
        part(
            "3",
            "A teammate changes `if expense.amount < minimum:` to `<=` in `total_by_category`, thinking it reads better, and pushes. What happens now that could not have happened at v0.3?",
            2,
            "CI runs `pytest` on the push and two cases of `test_minimum_keeps_amounts_equal_to_it` fail, because an amount equal to the minimum is now dropped. The commit goes red for everyone to see. At v0.3 there were no tests and no CI, so every report with a minimum would quietly have lost any amount equal to it.",
            [
                "CI runs the tests on the push and the check goes red on that commit.",
                "Names the boundary test (an amount equal to the minimum is kept) as what catches it, and says that at v0.3 nothing would have.",
            ],
            "'The program crashes' is wrong: it runs and prints smaller totals, which is worse. 'mypy or ruff catches it' is wrong: `<=` is as well typed and as tidy as `<`.",
        ),
    ],
    explanation="Keep the two audiences apart. For the user, v0.4 is invisible. For the developer it is a safety net and a referee: \"the referee, not the judge\" runs on every push and turns a silent wrong answer into a red check. The boundary is one of the edge cases session 8 asks for on purpose (\"Zero: the boundary? an amount exactly equal to minimum\"), and d38d9e6 pins it down.",
    section=7,
    source="expense-tracker v0.3..v0.4, d38d9e6, 0e05065; S8 slides 11, 23; S3 CI",
    origin="history",
    verified="run",
)

# ---------------- s8: commit messages and tags ----------------

mcq(
    "name-6efdf9d",
    level="exam",
    skills=["read-diff", "compare"],
    stem=md(
        "A real commit from the history, with its message hidden (two of its four hunks; the other two give `run` the new parameters and print the filters in the header):",
        fence("diff", DIFF_6EFDF9D_NAME),
        "Which message fits it best for a reader six months later?",
    ),
    right=(
        "Filter by category and ignore small amounts",
        "Imperative, and it says what the program can now do: limit the report to a category and skip small amounts.",
    ),
    wrong=[
        ("Update calculate_totals", "Says which function was touched but nothing about what changed; the reader must open the diff."),
        ("Add y and z parameters and read two more arguments", "Describes how, in names that mean nothing out of context. The diff already shows the mechanics."),
        ("Refactor the totals loop", "The output changes when the new arguments are given, so this is a feature, not a refactoring."),
    ],
    pos="c",
    explanation="This is 6efdf9d. A good subject says what the change does for the program, in the imperative, specifically enough to search for. 'Update' names no change, 'add y and z' names the mechanics, and 'refactor' names the wrong kind of change: it would tell a reviewer to expect identical output, which is false. The real message passes every test, and it is the one the history uses.",
    section=8,
    source="expense-tracker 6efdf9d; sample Q8",
    origin="history",
    verified="run",
)

mcq(
    "name-0e05065",
    level="exam",
    skills=["read-diff", "compare"],
    stem=md(
        "Another hidden message. The commit adds one 37-line file (trimmed: the lines between `pull_request:` and the dependency step, which set up the job, check out the code and install uv, are not shown):",
        fence("diff", DIFF_0E05065_STEPS),
        "Which message fits it best?",
    ),
    right=(
        "Run ruff, mypy and pytest on every push",
        "Says what the project now does and when, which is what the workflow is for.",
    ),
    wrong=[
        ("Add check.yml", "Names the file, which `--stat` already shows, and not what it does."),
        ("Fix CI", "There was no CI before this commit, so there is nothing to fix; 'fix' also sends readers looking for a bug."),
        ("Add YAML steps for uv sync and four run commands", "Describes the file's mechanics and still does not say what is checked or when."),
    ],
    pos="b",
    explanation="This is 0e05065. The workflow's job is the referee: lint, format check, types and tests on every push and pull request. The best subject says exactly that. 'Fix' is a word to reserve for repairs, because readers search for it when hunting a bug. A file name or a description of YAML steps forces the reader into the diff to learn what the change means.",
    section=8,
    source="expense-tracker 0e05065; S3 (CI referee)",
    origin="history",
    verified="run",
)

mcq(
    "name-9d6c607",
    level="exam",
    skills=["read-diff", "compare"],
    stem=md(
        "A third hidden message. The commit's first and last hunks:",
        fence("diff", DIFF_9D6C607_RUN),
        "The report printed on the sample data is identical before and after. Which message fits best?",
    ),
    right=(
        "Separate reading and printing from the calculation",
        "Says what was pulled apart from what, which is the point of the change, and tells the reader to expect the same output.",
    ),
    wrong=[
        ("Add read_expenses, largest_expense and format_report", "Lists names the diff already shows and hides the reason: the calculation no longer prints or reads."),
        ("Fix the largest expense calculation", "Nothing was broken, and the output is identical; 'fix' would mislead a reader looking for a bug."),
        ("Update report.py", "Names a file that changes in most commits; it tells the reader nothing."),
    ],
    pos="a",
    explanation="This is 9d6c607, the third of the five clean-code commits. Session 6 calls it 'computation is not output': `format_report` returns lines, `read_expenses` returns expenses, and only `run()` prints. A subject that names the separation tells a reader both what moved and why it is safe (a refactoring). Listing the new functions is accurate but describes how; the reader still has to infer the intent.",
    section=8,
    source="expense-tracker 9d6c607; S6 slides 18, 20, 31",
    origin="history",
    verified="run",
)

mcq(
    "fix-stuff",
    level="core",
    skills=["judgement"],
    stem="Sample question 8 offers two messages for the same diff: `Fix stuff in loader` and `Reject negative amounts when loading expenses`. What is the main problem with the first, for someone reading the history six months later?",
    right=(
        "It does not say what changed, so the reader must open the diff",
        "'Stuff' names nothing and 'loader' is vague, so the subject neither explains the change nor turns up in a search.",
    ),
    wrong=[
        ("It sounds informal, and swapping `stuff` for a more formal word would fix it", "Tone is not the issue: `Reject negative amounts when loading expenses` is plain language too. What matters is whether the subject says what changed."),
        ("It names the file's area but not the author, so the reader cannot ask who made the change", "git records the author of every commit separately. The subject line is for what the change does."),
        ("It is too short to appear on one line of `git log --oneline`", "Short subjects fit easily. `--oneline` shows only the subject, which is exactly why the subject has to carry the meaning."),
    ],
    pos="b",
    explanation="A reader six months on sees subjects in `git log --oneline` and decides from them which commit to open. `Reject negative amounts when loading expenses` says the new behaviour (a negative amount now raises `ValueError`) and is found by searching 'negative'. `Fix stuff in loader` says neither, and 'Fix' also claims a bug without naming it. Judge a message by whether the reader can act on it without opening the diff.",
    section=8,
    source="moodle/midterm-sample-questions.md Q8",
    origin="teacher-variant",
    variant_of="sample-paper-q08",
    verified="source",
)

mcq(
    "split-commit",
    level="exam",
    skills=["judgement"],
    stem="Before pushing, a teammate shows you one commit, `Add --month option and rename variables in report.py`. Its diff adds the new option and renames six variables across the same file. What do you suggest?",
    right=(
        "Split it in two, rename first, so each can be checked alone",
        "One logical change per commit. The rename goes first and is checked by unchanged output; the option follows as a feature, reviewed on its own.",
    ),
    wrong=[
        ("Keep it: one commit per working session is the usual convention", "Commits follow logical changes, not sessions. The demo history has two commits on 13 April for the red and green steps."),
        ("Keep it, but list all six renamed variables in the subject", "A longer subject does not separate the changes; the diff still mixes a feature into a refactoring."),
        ("Merge it into the previous commit so the history is shorter", "That mixes even more into one commit; a short history is not the goal."),
    ],
    pos="a",
    explanation="A commit that mixes a refactoring with a feature defeats the refactoring's own check. \"If the output changes, it was not a refactoring\", but this commit's output changes because of the new option, so nobody can tell whether the renames were safe. The 'and' is what prompts the check (session 6 asks the same of functions), and here the check fails: one half changes behaviour, the other must not. The history shows the habit: v0.2 as five separate moves, session 8's cycle as three commits.",
    section=8,
    source="S6 slides 18, 31; S7 slide 5; S8 slides 14–16",
    origin="history",
    verified="reasoning",
)

mcq(
    "tag-command",
    level="core",
    skills=["concept"],
    stem=md(
        "The last step of the Checkpoint 2 lab, run in your group's repository (not the demo):",
        fence("bash", 'git tag -a v0.2 -m "Checkpoint 2: tested core"\ngit push origin v0.2'),
        "What does the first command do?",
    ),
    right=(
        "It gives the current commit a permanent name with a stored message",
        "An annotated tag: a fixed name for one commit, carrying its own message. The checkpoint is marked at that commit.",
    ),
    wrong=[
        ("It creates a new branch called `v0.2` for the group to keep working on", "A tag does not move when you commit again; it stays on the commit it was given."),
        ("It commits all staged changes with the message \"Checkpoint 2: tested core\"", "That is `git commit -m`. A tag names a commit that already exists."),
        ("It sends the latest commit to GitHub so that CI can run on it", "Sending is `git push`; the second line pushes the tag itself."),
    ],
    pos="d",
    explanation="Lab 01: \"A tag is a permanent name for one commit.\" With `-a` and `-m` it is annotated, storing a message, the tagger and a date; `git tag -n` lists the messages, as it does for the demo's six tags. The tag has to be pushed on its own (`git push origin v0.2`): \"A missing tag means nothing to mark.\" The flags are in the artefact so you can read it, not to be memorised.",
    section=8,
    source="labs/01-scaffold.md §9; labs/08-tdd.md §4; S8 slide 29",
    origin="lab",
    verified="source",
)

mcq(
    "tag-older",
    level="exam",
    skills=["read-tool-output", "judgement"],
    stem=md(
        "Your group tagged the partial submission, then saw CI go red on that commit. You pushed a fix, and CI is now green on the new commit:",
        fence("console", LOG_TAG_OLDER),
        "The partial submission is marked at `v0.5`. What should you do?",
    ),
    right=(
        "Move `v0.5` onto `37b40e6`, the commit CI approved, and push the tag again",
        "The tag still points at the red commit `cb5fbf4`. The partial rubric says: fix, push, wait for green, then move the tag.",
    ),
    wrong=[
        ("Nothing: the marker will look at the latest commit on `main` anyway", "Submissions are marked at the tag, and the tag is on the red commit."),
        ("Delete the red commit from the history so the tag has nothing wrong under it", "Rewriting history is not needed and does not move the tag; the fix is already pushed."),
        ("Create a second tag, `v0.5-fixed`, on the green commit", "The marker looks for `v0.5`; a differently named tag is not the submission."),
    ],
    pos="c",
    explanation="`--decorate` shows where every name points: `HEAD -> main` and `origin/main` on the green fix, `tag: v0.5` one commit below. A tag does not follow new commits. The partial rubric's procedure is to fix, commit and push, wait for the green tick on the new commit, then move the tag onto it and push it again, and finally check with `git log -1 --oneline v0.5` that it shows the green commit. Lab 08 lists the same symptom: \"CI is green but `git tag` points at an older commit.\"",
    section=8,
    source="partial-rubric (If CI is red on the tag); labs/08-tdd.md troubleshooting",
    origin="lab",
    verified="run",
)

mcq(
    "largest-ignores-filter",
    level="beyond",
    skills=["read-tool-output", "judgement"],
    stem=md(
        "Every tag from v0.0 to v0.4 prints this for `uv run expenses report --category dining --min 20` (v0.0: `python tracker.py expenses.csv dining 20`):",
        fence("text", REPORT_DINING),
        "Your team decides the largest expense should come from the chosen category. How should the fix enter the history?",
    ),
    right=(
        "As its own commit, test first, named for the new behaviour",
        "A behaviour change travels alone: a test that fails first, then the change, under a subject such as `Show the largest expense within the chosen category`.",
    ),
    wrong=[
        ("Inside the next refactoring commit, since it touches `largest_expense` anyway", "Then that commit's output changes, so nobody can check the refactoring by comparing outputs, and the fix is invisible in the log."),
        ("Not at all: five refactorings kept this output, so it must be intended", "Refactorings keep behaviour, bugs included. Keeping it unchanged is their job, not a verdict on it."),
        ("As a quick commit called `Fix stuff in report`, so the log stays short and tidy", "That is sample Q8's bad message: the reader learns nothing without opening the diff."),
    ],
    pos="d",
    explanation="The oddity dates from c746d38, whose loop searched every row, not the filtered ones. All the clean-code commits preserved it, correctly: a refactoring must not change output. Changing it is a decision about behaviour, so it travels alone: a failing test (a dining filter whose largest dining expense is not the overall largest), the smallest change that passes, and an imperative subject that names the new behaviour. It would be the history's first fix commit.",
    section=8,
    source="expense-tracker c746d38..d3df52b; S7 slide 5; S8 slide 5; sample Q8",
    origin="history",
    verified="run",
)

# ---------------- added after review (q45 onwards) ----------------

mcq(
    "ci-red-step",
    level="exam",
    skills=["judgement", "concept"],
    stem="Your group's `.github/workflows/check.yml` runs the same steps as the demo's (`0e05065`), in this order: `uv sync --locked`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src tests`, `uv run pytest`. On your push the Actions tab shows the **Formatting** step red, and the two steps after it never ran. On your laptop `ruff check`, `mypy` and `pytest` all pass. What should you conclude and do?",
    right=(
        "Run `ruff format .`, commit the result and push again",
        "Lab 01 lists this exact symptom, red at Formatting and green locally: you ran `ruff format .` after committing, or never did. Commit the formatted files, push, and read the new run.",
    ),
    wrong=[
        ("Nothing: mypy and pytest are not marked red, so they passed on CI", "They were skipped, not passed. A failed step stops the job, so CI never checked them on this commit."),
        ("Delete the Formatting step, since layout never changes behaviour", "That weakens the referee to get a green tick. Session 6: nobody argues about layout again, because \"the tool decides, and CI enforces it.\""),
        ("Re-run the job until it goes green, since it passes on your laptop", "Nothing here is random. The committed files are not formatted, and re-running checks the same files."),
    ],
    pos="d",
    explanation="The workflow is a chain: each step must exit 0 for the next one to run. That is session 5's exit codes put to work: \"Every tool downstream reads that number: the shell, &&, CI.\" A red Formatting step means `ruff format --check` found files it would reformat. It also means types and tests have not been checked on this commit at all. Lab 01's troubleshooting table names the cause and the cure: run `ruff format .`, commit the result, push. Then read the new run from the top, because the steps that were skipped may now show problems of their own.",
    section=7,
    source="expense-tracker 0e05065 (`.github/workflows/check.yml`); labs/01-scaffold.md §8 and troubleshooting; S5 slide 9; S6 slide 27",
    origin="history",
    verified="source",
)

mcq(
    "uvlock-2ecad20",
    level="core",
    skills=["read-tool-output", "concept"],
    stem=md(
        "The `--stat` of `2ecad20` *Move the report into the package behind a typer CLI*:",
        fence("console", STAT_2ECAD20),
        "The same commit adds `\"typer>=0.12\"` to `dependencies` in `pyproject.toml`. Why did `uv.lock` grow by 91 lines?",
    ),
    right=(
        "It pins the exact typer version and the packages typer needs",
        "`pyproject.toml` says what is needed (`typer>=0.12`). The lockfile records exactly which versions: typer and its own dependencies, such as `rich` and `shellingham`.",
    ),
    wrong=[
        ("uv rewrites the whole lockfile from scratch on every commit you make", "uv knows nothing about commits. It changes the lockfile only when what the project needs changes; a953d05's lockfile had just 8 lines because there were no dependencies."),
        ("The moved report code is stored in `uv.lock` so that it installs faster", "The lockfile holds package names, versions and hashes, never your code. The code moved to `src/expense_tracker/report.py`."),
        ("It keeps a copy of the 13 lines that were deleted from `tracker.py`", "git keeps old versions in the history; the lockfile has nothing to do with deleted code."),
    ],
    pos="c",
    explanation="Session 4: `pyproject.toml` says `typer>=0.12`; the lockfile says \"exactly which typer, and which of its dependencies, down to the hash.\" Adding typer therefore adds typer and everything it pulls in. In the real commit the lockfile gains `annotated-doc`, `colorama`, `markdown-it-py`, `mdurl`, `pygments`, `rich`, `shellingham` and `typer`. Committing `uv.lock` in the same commit keeps every teammate, and later CI's `uv sync --locked`, on the same versions.",
    section=4,
    source="expense-tracker 2ecad20 (`git show --stat`, `git show 2ecad20:uv.lock`); S4 slide 24",
    origin="history",
    verified="run",
)

open_q(
    "open-v00-run",
    level="exam",
    skills=["read-code", "judgement"],
    stem=md(
        "The end of `run()` in the v0.0 script. `rows` is the list of 4-tuples `(date, merchant, category, amount)` read from the CSV; `cat` and `minimum` are the filters from the command line.",
        fence("python", V00_RUN_END),
    ),
    parts=[
        part(
            "1",
            "In one sentence, what does this part of `run()` do?",
            1,
            "It prints each category's total and the grand total, then finds the largest expense in the whole file and prints it.",
            ["Says it prints the totals per category with a grand total, then finds and prints the largest single expense."],
            "Reading it line by line ('it loops over `t`, then sets `m` to 0.0') describes the code, not what it does. Saying it 'calculates the totals' misses that `calculate_totals` does that; this part prints them. Saying the largest comes from the filtered rows misreads the loop: it runs over `rows`, every expense in the file.",
        ),
        part(
            "2",
            "Name two problems a teammate would face when reading, testing or changing it.",
            2,
            "Computing and printing are mixed, so no test can check the grand total or the largest without capturing the screen. And nothing has a name: `t[1]`, `mr[3]`, `m` and the widths 20, 10 and 40 must be looked up.",
            [
                "Names computation mixed with output: you cannot assert on what is printed, so the total or the largest cannot be tested on its own.",
                "Names meaningless names, magic indexes or magic numbers (`t[1]`, `mr[3]`, `m`, 20, 10, 40) and what they cost a reader. Also credit: the largest is searched over all rows, so a filtered report can name an expense from another category.",
            ],
            "'Bad names' with no example and no consequence earns one mark at most. 'It needs comments' is the wrong cure: session 6 calls a comment that says what the code does a failure of naming. 'It is too long' names nothing a teammate can act on. Two problems of the same kind, such as two bad names, count once.",
        ),
        part(
            "3",
            "Describe in words (do not write code) how you would change it, and which of your two problems each change solves.",
            3,
            "Name the numbers and variables and give the expense a type, so `mr[3]` reads `largest.amount`: that fixes reading. Move the search into a function that returns the largest, and build the report as lines that one place prints: a test can then pass a list and check the result.",
            [
                "Proposes names for the numbers or variables, or a dataclass instead of the tuple, and links it to the reading problem.",
                "Proposes a function that returns the largest expense (or the total) instead of printing it.",
                "Says the report should be returned as lines or values and printed in one place, and links that to testing.",
            ],
            "'Refactor it' or 'make it cleaner' describes no change. Writing code instead of words is not what is asked. A common gap is listing changes without saying which problem each solves, which is half the part. Making the largest respect the filters changes behaviour: it fixes neither problem and belongs in its own commit, with its own test.",
        ),
    ],
    explanation="This is sample Q7's shape on the demo's own code, and the history answers part 3 commit by commit: `5e9466d` names the numbers, `f3bb801` names the variables, `9d6c607` pulls out `largest_expense` and makes `format_report` return lines, and `017f926` turns the tuple into `Expense`. Each of those commits kept the report identical, which is what made them refactorings. The quirk you may spot, the largest expense ignoring the filters, is behaviour: the history keeps it on purpose, and changing it would be a separate commit with a test.",
    section=3,
    source="expense-tracker v0.0 `tracker.py` lines 44–61; S6 slides 16, 18, 20, 22; sample Q7",
    origin="teacher-variant",
    variant_of="sample-paper-q07",
    verified="source",
)

sort_q(
    "sort-subjects",
    level="core",
    skills=["compare", "judgement"],
    stem="You are reading commit subjects before they are pushed. Some are real ones from the demo history or sample question 8, some are a teammate's. Put each under what a reader six months later would say about it.",
    categories=[
        ("keep", "Says what the change does: keep it"),
        ("how", "Says how the code changed, not what for"),
        ("vague", "Too vague to find or act on"),
        ("split", "Two changes: split the commit"),
    ],
    items=[
        ("`Give an expense a type instead of a tuple`", "keep", "Real (017f926). For a refactoring the move is the what, and it names the reason: a type instead of a tuple."),
        ("`Reject negative amounts when loading expenses`", "keep", "Sample Q8's message B: the new behaviour, in the imperative, and a search for 'negative' finds it."),
        ("`Print the largest expense`", "keep", "Real (c746d38): an imperative verb and what the user now sees."),
        ("`Add y and z to calculate_totals`", "how", "Mechanics in names that mean nothing outside the diff. What it does is filter by category and ignore small amounts."),
        ("`Add YAML steps for uv sync and four run commands`", "how", "Describes the file's contents. What it is for, running the checks on every push, is missing."),
        ("`Fix stuff in loader`", "vague", "Sample Q8's message A: 'stuff' names nothing, and 'Fix' claims a bug it does not name."),
        ("`Update cli.py`", "vague", "Names a file that changes in many commits; `--stat` already shows the file."),
        ("`Various improvements`", "vague", "Nothing to search for, and it hides whether behaviour changed."),
        ("`Add --month option and rename variables in report.py`", "split", "A feature and a refactoring together: the renames can no longer be checked by unchanged output."),
        ("`Add type hints and narrow the bare except`", "split", "Hints keep behaviour; narrowing the `except` changes how the program fails. Apart, each can be found and checked."),
    ],
    explanation="Judge a subject by what a reader can do with it in `git log --oneline` without opening the diff. A good one is imperative and names what the change does; for a refactoring, the move itself is the what. Subjects that describe mechanics or name a file send the reader into the diff, and vague ones cannot be found at all. An 'and' is a prompt to check: `Add a README and the MIT licence` is one change, while a feature joined to a rename is two, because one half changes behaviour and the other must not.",
    section=8,
    source="moodle/midterm-sample-questions.md Q8; S6 slide 31; expense-tracker `git log --oneline`",
    origin="history",
    verified="reasoning",
)

mcq(
    "deleted-data",
    level="beyond",
    skills=["concept", "judgement"],
    stem="Your group repository is public. While trying out an `add` command, a teammate commits `data/expenses.csv`, which holds their real spending, and pushes. Two commits later they notice, delete the file, add `data/` to `.gitignore`, commit and push again. What is true now?",
    right=(
        "The spending is still public: the earlier commits still contain the file",
        "A commit is a snapshot of the whole project. Deleting the file makes a new snapshot without it; the earlier ones keep it.",
    ),
    wrong=[
        ("The spending is gone: the latest commit no longer contains the file", "The latest snapshot does not, but the earlier commits are unchanged. Anyone can open the commit that added the file on GitHub, or check it out."),
        ("The spending is gone: `.gitignore` now hides `data/` in every commit", "`.gitignore` tells git which new files to leave alone from now on. It never changes commits that already exist."),
        ("The spending was never public: GitHub only shows each file's newest version", "GitHub shows every commit and its diff to anyone who can see the repository, and the course's group repositories are public."),
    ],
    pos="b",
    explanation="The demo put `data/` in `.gitignore` in the same commit that introduced `add` (bc9ef3d), before any real spending could be written: the order matters. The history keeps every snapshot, so a file that was committed and pushed stays readable even after a later commit deletes it. The project brief says it plainly: no data about real people in the repository, and \"I deleted the file\" does not remove it from a repository's history. Removing it for good needs tools beyond the survival kit; the habit to learn now is to ignore the folder before anything is added.",
    section=4,
    source="moodle/project-pages.md (public repository; 'I deleted the file'); expense-tracker bc9ef3d; S4 slide 20",
    origin="history",
    verified="source",
)

open_q(
    "open-noisy-diff",
    level="hard",
    skills=["read-diff", "compare", "judgement"],
    stem=md(
        "A teammate pushes this commit on top of `v0.4`. Ruff, mypy and pytest are all green in CI.",
        fence("diff", DIFF_NOISY_WIDTH),
        "Two candidate commit messages:\n\n- A: `Sort the constants`\n- B: `Widen the name column of the report to 24`",
    ),
    parts=[
        part(
            "1",
            "Which line really changes what the program does, and what will a user notice?",
            2,
            "`NAME_WIDTH` goes from 20 to 24, on a line that was also moved; the rest is the same assignments reordered. Every report line with a name or `TOTAL` puts its amount four characters further right.",
            [
                "Finds the `NAME_WIDTH` line (20 changed to 24) among the moved lines",
                "Says what changes for the user: the amounts in the report move four columns to the right",
            ],
            "\"The constants were reordered\" sees only the noise. Seeing that `DATE`, `MERCHANT` and the rest keep their values is the check: only one number is different.",
        ),
        part(
            "2",
            "A teammate says: \"The three checks are green, so this is a safe tidy-up.\" Is the commit a refactoring? Explain.",
            2,
            "No. A refactoring keeps the behaviour, and the report changes, so `diff before.txt after.txt` would print lines. The checks are green only because no test pins the column width. The reorder alone would be a refactoring.",
            [
                "Says no, with the definition: the output of the program must stay identical",
                "Explains green checks: no test covers the width (or: green shows no test failed, not that nothing changed)",
            ],
            "\"Yes, it only moves constants\" ignores the one changed number. \"No, because the checks are green\" has the logic backwards: green checks cannot tell you whether the behaviour changed unless a test covers it.",
        ),
        part(
            "3",
            "Which message is better, and what would you ask the author to change about the commit?",
            2,
            "B, because it names the change a user will see; A hides it. Better, ask the author to split the commit: one that only sorts the constants, a refactoring, and one that only widens the column, with its own message.",
            [
                "Chooses B because A hides the behaviour change",
                "Asks for two commits, one per kind of change (the reorder and the new width)",
            ],
            "\"B is better\" without a reason earns one mark at most. Wanting a message that lists both changes is a reasonable second best, but the course's habit is one idea per commit, so that the history can be read and reverted in pieces.",
        ),
    ],
    explanation="Sample Q8's shape with a harder diff. When a commit mixes a harmless reorder with one real change, the real change can hide among the moved lines: a `-` line and a `+` line that look like a pair differ in one number. Session 6's check (`diff before.txt after.txt`) settles it: the output differs, so the commit is not a refactoring, whatever the checks say. Real run on a copy of v0.4: ruff, mypy and pytest passed, and `diff` printed the `dining` and `TOTAL` lines with the amounts moved four columns.",
    section=8,
    source="S6 slides 23, 30; S8 slide 11; expense-tracker v0.4 report.py (changed copy)",
    origin="teacher-variant",
    verified="run",
    variant_of="sample-paper-q08",
)

# ---------------- s9: v0.5 (added with the five commits after v0.4) ----------------

sort_q(
    "sort-v05-commits",
    level="exam",
    skills=["read-diff", "concept"],
    stem=md(
        "Each statement describes exactly one of the five commits between `v0.4` and `v0.5`:",
        fence("console", LOG_V05),
        "Put each statement under the commit it describes.",
    ),
    categories=[
        ("script", "8492f59 Add scripts/check.sh"),
        ("ci", "8fabdb3 Run scripts/check.sh in CI"),
        ("filter", "d814ca9 Add filter_by_month and a validator"),
        ("option", "416604b Add a --month option"),
        ("revert", "8a8903d Revert the CI change"),
    ],
    items=[
        ("The only commit that touches `scripts/`, and it creates the file as an executable (`100755`)", "script", "`git show --stat` lists one file, `scripts/check.sh | 14 ++++++++++++++`, and the file mode is part of what git stores."),
        ("Puts `ruff check`, `ruff format --check`, `mypy src tests` and `pytest` in one script, each announced by an `echo`", "script", "That is the content of `scripts/check.sh`. Nothing else changes: CI does not call it yet."),
        ("Two lines added and eleven deleted in `.github/workflows/check.yml`, ending in a step named `Run the checks`", "ci", "The `--stat` total is `2 insertions(+), 11 deletions(-)`: four steps become one."),
        ("Makes CI call the script, so a red run no longer says whether it was ruff, mypy or pytest", "ci", "That is the cost the revert's message names for the one-step workflow."),
        ("Adds `is_valid_month`, true only when the whole string looks like `2025-07`, with 18 tests", "filter", "`fullmatch` rejects `2025-07-01` and `2025-13`; the tests are in `tests/test_month.py`."),
        ("Changes `report.py` and adds tests but leaves `cli.py` alone, so `--month` is still 'No such option'", "filter", "Nothing calls `filter_by_month` yet: a tested function waiting for its caller, like `1e421bc` in v0.4."),
        ("Adds a `month: 2025-07` line to the report header and an exit code of 2 for a bad month", "option", "The header line comes from `format_report` and the exit from `cli.py`: the first commit a user can run with `--month`."),
        ("Adds two `CliRunner` tests, one checking the exit code and the message on standard error", "option", "`tests/test_cli_month.py` tests at the edge, as `f3d9870` did for the missing file."),
        ("Puts the four named steps Lint, Formatting, Types and Tests back, and carries the tag `v0.5`", "revert", "The workflow is again the one from `0e05065`; `git tag -n` and `git log` put `v0.5` on this commit."),
        ("Has an `index` line that runs backwards, `eb59e60..eb2e436`, and a message naming the commit it undoes", "revert", "A revert is the original diff turned round: `eb2e436` is the workflow as it was before `8fabdb3`."),
    ],
    explanation="Sorting by commit means knowing what each one touched, and `git show --stat` answers it fast. `8492f59` is one new script. `8fabdb3` and `8a8903d` touch only `check.yml`, with 2 insertions and 11 deletions, then 11 and 2. `d814ca9` touches `report.py` and one test file. `416604b` is the only one that edits `cli.py` and the README. The two month commits follow the pattern of v0.4's last three: the function and its tests first, the caller after. The revert and the commit it undoes are mirror images, which is why a revert's `index` line runs backwards.",
    section=9,
    source="expense-tracker `git show --stat` of 8492f59, 8fabdb3, d814ca9, 416604b, 8a8903d; `git log --oneline v0.4..v0.5`",
    origin="history",
    verified="run",
)

mcq(
    "user-change-v05",
    level="exam",
    skills=["judgement", "read-diff"],
    stem=md(
        "The five commits between `v0.4` and `v0.5`:",
        fence("console", LOG_V05),
        "Which one is the first that changes what a person running `uv run expenses report` can do or see?",
    ),
    right=(
        "`416604b` Add a --month option to the report command",
        "It edits `cli.py`: the `report` command gets `--month`, a `month:` line in the header and an exit code of 2 for a bad month.",
    ),
    wrong=[
        ("`8492f59` Add scripts/check.sh to run every check with one command", "The script is for the developer. It adds nothing to `expenses`, and the report at that commit is identical to the v0.4 report."),
        ("`8fabdb3` Run scripts/check.sh in CI instead of four separate steps", "A workflow edit changes how GitHub checks the code, not what the program prints."),
        ("`d814ca9` Add filter_by_month and a validator for month strings", "The functions exist and are tested, but no command calls them. Run at that commit, `expenses report --month 2025-09` answers `No such option: --month`."),
    ],
    pos="c",
    explanation="Ask what a user could do after the commit that they could not do before. Two commits touch only tooling, the script and the workflow. `d814ca9` is the position of `1e421bc` in v0.4: the code exists and is tested, and nothing calls it. `416604b` is the caller, so it is the first change a user can see, and it is also why sample question 2 treats \"adding a `--month` option\" as the change that is not a refactoring: the behaviour is new. I ran the report without `--month` at v0.4, `8492f59`, `d814ca9` and v0.5: the output was identical each time.",
    section=9,
    source="expense-tracker v0.4..v0.5 (`git log`; reports run at v0.4, 8492f59, d814ca9, v0.5); sample Q2",
    origin="history",
    verified="run",
)

mcq(
    "ci-at-v05",
    level="hard",
    skills=["read-tool-output", "judgement"],
    stem=md(
        "Session 10's last slide says \"scripts/check.sh is what CI runs.\" In the demo repository at the `v0.5` tag, you list the commits that changed the workflow:",
        fence("console", LOG_WORKFLOW),
        "What does CI run on the commit tagged `v0.5`?",
    ),
    right=(
        "The four named steps: `ruff check`, `ruff format --check`, `mypy src tests` and `pytest`",
        "`8fabdb3` replaced them with one step that ran `scripts/check.sh`, and `8a8903d`, the commit that carries the tag, reverted it. The workflow is the one from v0.4.",
    ),
    wrong=[
        ("One step, `Run the checks`, that calls `scripts/check.sh`, as the slide says", "That was true from `8fabdb3` until the revert. The tag sits on the revert, so it describes the commits in between, not `v0.5`."),
        ("Nothing: the revert deleted the workflow, so the tagged commit has no CI", "A revert undoes one change. It put the four steps back; the file was never deleted."),
        ("The four steps and then `scripts/check.sh` once more, to confirm them", "No version of `check.yml` has both: it lists either the four steps or the one script step."),
    ],
    pos="d",
    explanation="Read the log from the top: the newest commit to touch the workflow is a revert, and a revert undoes what the commit under it did. So the workflow at `v0.5` is the one from `0e05065`, with four named steps. Session 10's slide gives the idea, one command that runs the four checks with exit code 0 as green, and for a while the repository did exactly that. The revert's message gives the reason it did not last: one step hides which check failed. `scripts/check.sh` stays for running the same checks before a push. When a question shows `check.yml` or a log, answer from what it shows.",
    section=9,
    source="S10 slide 21; expense-tracker `git log --oneline -- .github/workflows/check.yml`, `git show v0.5:.github/workflows/check.yml`; 8fabdb3, 8a8903d",
    origin="history",
    verified="run",
)

mcq(
    "revert-reason",
    level="exam",
    skills=["judgement", "read-tool-output"],
    stem=md(
        "The message of `8a8903d`, the commit tagged `v0.5`:",
        fence("console", REVERT_MSG),
        "According to the message, why was `8fabdb3` reverted?",
    ),
    right=(
        "One step hides which check failed, so a red run means opening the log",
        "The message says it in one sentence: with a single step called \"Run the checks\", you must open the log to learn whether ruff, mypy or pytest was red.",
    ),
    wrong=[
        ("`scripts/check.sh` lost its executable bit, so the step failed in CI", "Session 9's x-bit failure is a real one, but the message does not mention it, and the script is committed as `100755`."),
        ("`scripts/check.sh` was too slow to run on every push", "Speed is not mentioned. The step ran the same four commands as the four steps it replaced."),
        ("`scripts/check.sh` was wrong, so it was deleted with the CI change", "The message says the opposite: `scripts/check.sh` stays, for running the same checks before a push."),
    ],
    pos="b",
    explanation="The message is the evidence, and it states one reason, about diagnosis. Four named steps show in the Actions summary which one is red; one step called \"Run the checks\" shows only that something is. The message also settles what happens to the script: it stays, for use before a push. The tempting wrong answers bring in other lessons (the x bit from session 9, speed) that the message never mentions, so answer from the artefact you are shown. A good revert message does what this one does: it names the commit and gives the reason the original, which has no body, never gave.",
    section=9,
    source="expense-tracker 8a8903d (`git log -1 --format=%B`); S9 slide 20",
    origin="history",
    verified="run",
)

mcq(
    "month-largest",
    level="hard",
    skills=["read-diff", "read-tool-output"],
    stem=md(
        "In `416604b`, the `report` command in `cli.py` changes like this:",
        fence("diff", DIFF_416604B_CLI),
        "Two runs on the sample data:",
        fence("console", RUN_LARGEST),
        "Why does `--month` change the largest expense when `--category` does not?",
    ),
    right=(
        "The month filter shortens the list before `largest_expense` runs; the category filter does not",
        "In `cli.py` the month filter replaces `expenses`, so everything after it sees one month. `category` and `minimum` go to `total_by_category` alone, while `largest_expense(expenses)` still gets every row.",
    ),
    wrong=[
        ("`format_report` now searches the chosen month for the largest expense", "`format_report` only builds lines to print: the diff adds a `month:` header line and one parameter. The largest is found by `largest_expense` in `cli.py`."),
        ("`read_expenses` stops reading at the end of the month, so later rows never exist", "`read_expenses` is not in the diff: it still reads the whole file. The month filter runs afterwards, on the list."),
        ("`416604b` fixes the v0.0 largest-expense behaviour, and the category option was left out", "The commit touches neither `total_by_category` nor `largest_expense`. The category quirk is the one v0.0 began and every commit since has kept."),
    ],
    pos="a",
    explanation="Follow the list through `cli.py`. `read_expenses` returns every row. With `--month`, `expenses` is then replaced by the filtered list, and both `total_by_category(expenses, category, minimum)` and `largest_expense(expenses)` read the shorter one. `category` and `minimum` go to `total_by_category` alone, so the largest line still comes from all 420 rows: that is why a dining-only report names `Ferreteria Mas`, a home expense from November. Neither result is a regression of this commit. It is where each filter was placed, and the sample runs show both.",
    section=9,
    source="expense-tracker 416604b `cli.py` (`git show`); runs at v0.5 on the sample `expenses.csv`",
    origin="history",
    verified="run",
)

mcq(
    "month-exit-code",
    level="hard",
    skills=["read-code", "read-tool-output"],
    stem=md(
        "`nosuch.csv` does not exist. After `416604b`:",
        fence("console", RUN_BAD_MONTH),
        "Why is the exit code 2 and not 1, the code `cli.py` uses for a file that cannot be read?",
    ),
    right=(
        "The month is checked before the file is opened, and that check exits with 2",
        "`cli.py` validates `--month` first and raises `typer.Exit(2)` after writing to standard error. The file is never opened, so the 1 for an unreadable file never happens.",
    ),
    wrong=[
        ("Exit code 2 means a missing file and 1 is kept for a bad month", "It is the other way round in this command: 1 for `could not read`, 2 for a bad month. Only 0 has the same meaning everywhere."),
        ("typer exits with 2 for any wrong value, whatever `cli.py` says", "typer does use 2 for its own usage errors, such as an unknown option, but this check is written in `cli.py`: `raise typer.Exit(2)`."),
        ("The shell adds up the errors: a bad month and a missing file make 2", "Exit codes are not counts. Only one failure was reached: the command stopped at the month check."),
    ],
    pos="c",
    explanation="The order of the checks decides which failure the user hears about. `cli.py` tests the month first, so a bad month stops the command before `read_expenses` runs. With a valid month and no file, the same command prints `could not read nosuch.csv` and exits with 1. The test for the bad month, `test_invalid_month_exits_with_two_and_explains_on_stderr`, never gets as far as the file. Session 5: 0 means success and anything else means failure; here the two non-zero numbers tell the two failures apart, as `grep` does with 1 and 2.",
    section=9,
    source="expense-tracker 416604b (`cli.py`, `tests/test_cli_month.py`); S5 slide 9; run at v0.5",
    origin="history",
    verified="run",
)

mcq(
    "revert-history",
    level="beyond",
    skills=["concept", "read-tool-output"],
    stem=md(
        "The last five commits of the demo repository:",
        fence("console", LOG_V05),
        "What does the revert `8a8903d` do to this history?",
    ),
    right=(
        "It adds a commit that undoes `8fabdb3`, and `8fabdb3` stays in the log",
        "That is the log above: both commits are listed. The revert is a new snapshot whose workflow file matches the one from before `8fabdb3`.",
    ),
    wrong=[
        ("It deletes `8fabdb3` from the history, so `git log` no longer lists it", "The log lists `8fabdb3` three lines below the revert. A revert adds to the history and never removes a commit."),
        ("It sets the whole project back to `v0.4`, so `--month` is lost as well", "A revert undoes one named commit. `d814ca9` and `416604b` sit between the two and stay: `--month` works at the `v0.5` tag."),
        ("It moves the tag `v0.4` forward, so `v0.4` now points at the revert", "A tag stays on the commit it was given: `v0.4` is still on `d3df52b`. The new tag, `v0.5`, is on the revert."),
    ],
    pos="d",
    explanation="A commit is a snapshot, so the way to undo an earlier one without rewriting history is another snapshot. `git revert` makes a commit that applies the opposite change: the revert's diff is the original hunk turned round, and the log shows both commits. This is why a revert is safe on a branch others have already pulled: nobody's history changes. Not on the slides (the next class, on 27 October, is Git), so the exam would not ask for the command, but the log is yours to read.",
    section=9,
    source="expense-tracker 8a8903d, `git log --oneline v0.4..v0.5`; not on the slides (S10 slide 21: next class is Git)",
    origin="history",
    verified="run",
)

mcq(
    "split-revert",
    level="exam",
    skills=["judgement", "concept"],
    stem="Suppose the team had made the CI switch and the month filter in one commit, `Add month filtering and run check.sh in CI`, instead of in `8fabdb3` and `d814ca9`. Later they want the CI change gone and the month filter kept. What would that have cost them?",
    right=(
        "A revert would remove the month filter too, unless someone separated the two by hand",
        "One logical change per commit is what let `8a8903d` undo the CI change alone. A commit that mixes two changes can only be undone as a whole.",
    ),
    wrong=[
        ("Nothing: a revert only undoes the lines that are about CI", "A revert undoes everything its target changed. It cannot tell which lines belong to which idea."),
        ("The month filter would have survived, because passing tests protect code from a revert", "A revert applies the opposite of the commit's diff and never looks at tests. The filter would go, and its tests with it if they sat in the same commit."),
        ("Only the message would suffer, because a revert needs a longer subject", "The cost is not in the subject. A revert undoes a commit's whole diff, so mixing changes decides what you lose, whatever the message says."),
    ],
    pos="b",
    explanation="Session 8's habit, one logical change per commit, pays when something has to be undone. `8a8903d` changed one file and left `d814ca9` and `416604b` alone, because the CI switch was a commit of its own. A commit that also held the month filter could be reverted only whole: the filter would go with it, or someone would pull the CI hunk apart by hand. It is the same argument as for keeping a refactoring apart from a feature: each can be checked, and undone, on its own.",
    section=9,
    source="S6 slide 31; expense-tracker 8fabdb3, d814ca9, 8a8903d (`git show --stat`)",
    origin="history",
    verified="reasoning",
)

open_q(
    "open-ci-slide",
    level="hard",
    skills=["read-tool-output", "judgement"],
    stem=md(
        "Session 10's last slide says: \"scripts/check.sh is what CI runs. Exit code 0 is green.\" A classmate opens the demo repository at the `v0.5` tag and shows you two things:",
        fence("console", LOG_WORKFLOW),
        fence("console", REVERT_MSG),
    ),
    parts=[
        part(
            "1",
            "What does CI run at the `v0.5` tag, and what in the log tells you?",
            2,
            "The four named steps, Lint, Formatting, Types and Tests. The newest commit to change the workflow is a revert of the one that had replaced them with a single `scripts/check.sh` step.",
            [
                "Says the workflow has the four separate steps (ruff check, ruff format check, mypy, pytest) at v0.5",
                "Uses the log: the top commit is the revert of the commit that switched to one script step",
            ],
            "\"CI runs `scripts/check.sh`\" repeats the slide and ignores the log. \"CI runs the tests\" names one of four steps. Saying the revert \"deleted CI\" misreads it: it put the four steps back. Listing the three commits without saying which one decides the answer earns nothing for the evidence.",
        ),
        part(
            "2",
            "Why was the change reverted?",
            2,
            "One step called \"Run the checks\" hides which check failed, so a red run means opening the log to see whether it was ruff, mypy or pytest. Named steps show it in the Actions summary.",
            [
                "Names the problem: a single step does not say which check failed",
                "Contrasts it with named steps, which show the failing check in the summary without opening the log",
            ],
            "\"It did not work\" or \"it was a mistake\" is not what the message says: the problem is diagnosis, not correctness. \"The script was slow\" or \"it lost its x bit\" bring in reasons the artefact does not give. The problem without the contrast earns one mark.",
        ),
        part(
            "3",
            "In what sense is the slide still right? Give two things `scripts/check.sh` and CI have in common.",
            2,
            "Both run the same four checks, ruff check, ruff format check, mypy and pytest. Both pass or fail by exit code, with 0 as green, so the script run before a push predicts what CI will say.",
            [
                "The same four checks (named or counted)",
                "Both are judged by the exit code, 0 being green, so running the script first predicts CI",
            ],
            "\"They both check the code\" is too general for a mark. \"CI runs `check.sh`\" repeats the claim the log disproves. Mentioning `set -e` without the exit code misses what CI actually reads, which is the number the last command returns.",
        ),
    ],
    explanation="This has the compare shape of sample Q8: two sources that seem to disagree, and a judgement. Read the repository first and take the idea from the slide. `8fabdb3` made the slide literally true; `8a8903d` ended that, for a reason its message states. What survives is what the slide's sentence is about: one command, the same four checks, exit code 0 as green, and CI reading that same number. In the exam, answer from the artefact in front of you.",
    section=9,
    source="S10 slide 21; expense-tracker `git log -- .github/workflows/check.yml`, 8a8903d; sample Q8 (shape)",
    origin="history",
    verified="run",
    lines="5–8",
)

# --------------------------------------------------------------------------------------
# Commits (all 25, oldest first)
# --------------------------------------------------------------------------------------

commits: list[dict[str, Any]] = [
    {
        "hash": "3e0834f",
        "tag": None,
        "message": "Add a script that totals expenses by category",
        "kind": "feature",
        "summary_md": "The first commit creates `tracker.py` (49 lines) and the sample `expenses.csv` (a header and 420 expenses). `calculate_totals(x)` adds up the amounts per category and sorts them largest first; `run(path)` reads the CSV, skips rows without four fields and prints a report with a grand total. The path comes from the first argument after the script name, or defaults to `expenses.csv`.",
        "concepts_md": "Session 4's *script*: it runs with `python tracker.py` and has no name, no version, no dependencies and no home for tests. It is also session 6's 'before' picture: names like `x`, `d`, `e`, `r`, indexes like `e[2]` and `e[3]`, and a bare `except:`.",
        "message_md": "Good. Imperative, and it says what the program does in the words a user would use. Nothing about how.",
        "section_ref": sid(3),
    },
    {
        "hash": "6efdf9d",
        "tag": None,
        "message": "Filter by category and ignore small amounts",
        "kind": "feature",
        "summary_md": "Adds two filters: the report can be limited to one category and can skip amounts below a minimum. `calculate_totals(x, y, z)` gains two guard clauses, `run` prints which filters are on, and the second and third arguments after the script name become the category and the minimum. An amount equal to the minimum is kept, the boundary v0.4 later tests.",
        "concepts_md": "Positional arguments: to filter by minimum alone you must type an empty category, `python tracker.py expenses.csv \"\" 20`. Session 5's options with defaults fix that in v0.1. The guard clauses already have the shape session 6 recommends; the names `y` and `z` do not.",
        "message_md": "Good. It names both new behaviours from the user's side. *Add y and z to calculate_totals* would describe the mechanics and mean nothing later. The 'and' joins two halves of one feature: filtering the report.",
        "section_ref": sid(3),
    },
    {
        "hash": "c746d38",
        "tag": "v0.0",
        "message": "Print the largest expense",
        "kind": "feature",
        "summary_md": "After the totals, the report prints the single largest expense, found with a loop over all rows (`m`, `mr`). Because it loops over every row, not the filtered ones, a dining-only report still names a home expense as the largest; every later commit keeps that behaviour. Tagged `v0.0`: \"The messy original, before any structure\".",
        "concepts_md": "A function that does too much: `run()` now opens, parses, handles the failure, prints, totals and finds the largest. Session 6 counts the jobs of this `run()` and asks: can I describe it without the word 'and'?",
        "message_md": "Good: short, imperative, and it says what the user sees. 'Print' is accurate here, because printing is exactly what this code does.",
        "section_ref": sid(3),
    },
    {
        "hash": "a953d05",
        "tag": None,
        "message": "Turn the script into a uv package",
        "kind": "build",
        "summary_md": "In session 4's words, \"`uv init --package`, and one edit.\" The commit adds `pyproject.toml`, `uv.lock`, `.python-version`, `.gitignore`, an empty `README.md` and a two-line `src/expense_tracker/__init__.py` whose `main()` prints `Hello from expense-tracker!`. `tracker.py` is untouched: no code changed, the code became installable.",
        "concepts_md": "Script versus project (session 4): a name, a version, dependencies, an entry point, a `src/` layout and a committed lockfile. Session 4 calls it \"the moment it became a project\" and shows its `--stat`.",
        "message_md": "Good. It states the outcome (the folder is now a uv package) rather than the list of files, which `--stat` already shows.",
        "section_ref": sid(4),
    },
    {
        "hash": "2ecad20",
        "tag": None,
        "message": "Move the report into the package behind a typer CLI",
        "kind": "feature",
        "summary_md": "`tracker.py` moves to `src/expense_tracker/report.py` (git reports a rename, 84% similar) and loses its `sys.argv` block (13 lines with the blank lines above it). A new `cli.py` defines a typer app with a `report` command: the path is an argument defaulting to `expenses.csv`, and `--category` and `--minimum`/`--min` are options. `[project.scripts]` now maps the `expenses` command to `expense_tracker.cli:app`, and typer becomes a dependency. The report text is unchanged; the way you call it is new.",
        "concepts_md": "Session 5: a program, not a script; how `[project.scripts]` resolves (command, module, object); typer reads the type hints as the specification; a parameter with a default becomes an option; the empty `@app.callback()` that keeps the command name.",
        "message_md": "Good. It says both halves: where the report went and what now stands in front of it. A reader looking for when the CLI appeared finds it.",
        "section_ref": sid(4),
    },
    {
        "hash": "bc9ef3d",
        "tag": None,
        "message": "Add an add command that writes to data/",
        "kind": "feature",
        "summary_md": "A second command, `add`, appends one expense to `data/expenses.csv`, writing the header row first if the file is new; the date defaults to today. `data/` goes into `.gitignore`, so the sample `expenses.csv` is never modified and personal spending never reaches the public repository.",
        "concepts_md": "Arguments versus options (session 5): `merchant`, `category` and `amount` have no default, so they are arguments; `--date` has one, so it is an option. The project brief's rule: no data about real people in a public repository.",
        "message_md": "Good. 'an add command' names the feature and 'that writes to data/' tells the reader where files appear. *Update cli.py* would name a file that changes in half the history.",
        "section_ref": sid(4),
    },
    {
        "hash": "89afbe1",
        "tag": "v0.1",
        "message": "Add a README and the MIT licence",
        "kind": "docs",
        "summary_md": "Adds `README.md` (what the program does, how to install and run it, the two CSV files) and the MIT `LICENSE`, and declares the licence in `pyproject.toml`. No code changes. Tagged `v0.1`: \"Packaged: uv, src layout, typer CLI\".",
        "concepts_md": "Checkpoint 1's Definition of Done (sessions 4 and 5): runs from a clean clone, `src/` layout, a README that says what it does and how to run it. Session 4's anatomy: README is 'what it is, how to run it', LICENSE is 'what others may do with it'.",
        "message_md": "Good: it names exactly what was added. The 'and' joins two parts of one change, the project's public face.",
        "section_ref": sid(4),
    },
    {
        "hash": "5e9466d",
        "tag": None,
        "message": "Replace magic numbers with named constants",
        "kind": "refactor",
        "summary_md": "Bare numbers get names: `DATE`, `MERCHANT`, `CATEGORY`, `AMOUNT` for the tuple positions, `FIELDS_PER_ROW` for the 4, and `NAME_WIDTH`, `AMOUNT_WIDTH`, `RULE_WIDTH` for the 20, 10 and 40 of the layout. The comment 'skip rows that do not have all four fields' goes, because `len(row) == FIELDS_PER_ROW` now says it. The report is identical.",
        "concepts_md": "Session 6's magic numbers (\"change the width once, in one place, with a name that says what it is\") and session 7's *extract constant*. The first of the five v0.2 commits replayed in session 6.",
        "message_md": "Good: the move and its target in one line. For a refactoring the move itself is the 'what', since behaviour does not change.",
        "section_ref": sid(5),
    },
    {
        "hash": "f3bb801",
        "tag": None,
        "message": "Rename calculate_totals to total_by_category",
        "kind": "refactor",
        "summary_md": "Renames throughout `report.py`: `calculate_totals(x, y, z)` becomes `total_by_category(expenses, category, minimum)`, and `d`, `r`, `e`, `rows`, `cat`, `grand`, `m`, `mr` become `totals`, `ordered`, `expense`, `expenses`, `category`, `grand_total`, `largest_amount`, `largest`. The loop over totals unpacks `for name, amount in totals`. The report is identical.",
        "concepts_md": "Session 6's naming table: a function name says what it returns (`calculate_totals` becomes `total_by_category`), a variable says what it holds. Session 7's move *rename*.",
        "message_md": "Good. It names the headline rename, so a search for either name finds it. The other renames are the same move and the diff shows them.",
        "section_ref": sid(5),
    },
    {
        "hash": "9d6c607",
        "tag": None,
        "message": "Separate reading and printing from the calculation",
        "kind": "refactor",
        "summary_md": "`run()` is split: `read_expenses(path)` reads and parses, `largest_expense(expenses)` finds the largest, and `format_report(...)` returns the report lines instead of printing them. `run()` now only calls them, prints the lines and handles the failure. On the sample data the output is identical. One detail: `largest_expense` starts from `None` instead of `0.0`, so a file of only refunds now gets a 'largest' line it did not get before.",
        "concepts_md": "Session 6: one function, one job, and computation is not output (\"a function that returns can be tested, reused and read on its own\"). Session 7's moves *separate I/O from logic* and *extract function* (`largest_expense` out of `run()`).",
        "message_md": "Good. It says what was separated from what, which is the point. *Add read_expenses, largest_expense and format_report* would list how and hide why.",
        "section_ref": sid(5),
    },
    {
        "hash": "017f926",
        "tag": None,
        "message": "Give an expense a type instead of a tuple",
        "kind": "refactor",
        "summary_md": "Introduces `@dataclass(frozen=True) class Expense` with `date`, `merchant`, `category` and `amount`. `read_expenses` builds `Expense` objects, and every `expense[CATEGORY]` or `largest[AMOUNT]` becomes `expense.category` or `largest.amount`. The report is identical.",
        "concepts_md": "Session 6's 'a tuple is a missing type' and 'dataclass is a naming tool'; session 7's *introduce a parameter object / type*. `frozen=True` makes `Expense` hashable, which `remove_duplicates` relies on in v0.4.",
        "message_md": "Good. It states the change and its reason in one line: a type instead of a tuple.",
        "section_ref": sid(5),
    },
    {
        "hash": "04d699f",
        "tag": "v0.2",
        "message": "Add type hints and make the code ruff clean",
        "kind": "refactor",
        "summary_md": "Adds type hints to every function (`list[Expense]`, `Expense | None`, `list[tuple[str, float]]`), adds ruff as a dev dependency with its rules in `pyproject.toml`, and fixes what ruff reported: f-strings instead of `%`, sorted imports, a `with` around the file in `add`. `grand_total = 0` becomes `0.0` so the types agree. It also replaces the bare `except:` with `except (OSError, ValueError):`. The report is identical on the sample data, but a 0-byte file, which used to print 'could not read', now crashes with `StopIteration`. Tagged `v0.2`.",
        "concepts_md": "Session 6: type hints are contracts, and the linter is the arbiter. Session 7: catch only what you can handle; its slide shows `except (OSError, ValueError):` as 'v0.2: only the two we expect'.",
        "message_md": "Accurate but incomplete. The subject names hints and ruff; it does not mention the narrowed `except`, which changes how the program fails. Someone searching the log for that change will not find it here.",
        "section_ref": sid(5),
    },
    {
        "hash": "15836e1",
        "tag": None,
        "message": "Move printing and exiting out of the report module",
        "kind": "refactor",
        "summary_md": "Deletes `run()` from `report.py` and moves its steps into the `report` command in `cli.py`: read, total, find the largest, format, echo each line. On a read error the shell writes the message to standard error with `typer.echo(..., err=True)` and exits with `raise typer.Exit(1)`. The report text and the exit code are unchanged; the error message now goes to stderr instead of stdout.",
        "concepts_md": "Session 7's functional core, imperative shell, and 'fail loudly, at the boundary': the core never prints an error; the shell prints to stderr and exits non-zero. Session 8 starts from here: '`report.py` has no `print`, no `sys.exit`'.",
        "message_md": "Good. It says what moved and out of where. It could add 'into the CLI', but `--stat` shows that at a glance.",
        "section_ref": sid(6),
    },
    {
        "hash": "88b83c3",
        "tag": "v0.3",
        "message": "Add pytest and turn on strict type checking",
        "kind": "build",
        "summary_md": "Configuration only: `mypy` and `pytest` join the dev dependencies, `[tool.mypy]` sets `strict = true`, and pytest is told to look in `tests/`. 280 lines of `uv.lock` change (279 added, 1 removed) to pin the new tools. No Python file changes, because `mypy --strict` already passed after v0.2. Tagged `v0.3`: \"Functional core, imperative shell, strict types\".",
        "concepts_md": "Session 7's 'your repo turns strict on today' and the three kinds of mypy error; session 4's lockfile, committed with the change so `uv sync --locked` agrees.",
        "message_md": "Good. Two settings joined with 'and', both in one file and both about tooling, so splitting them would add little. Imperative and specific.",
        "section_ref": sid(6),
    },
    {
        "hash": "d38d9e6",
        "tag": None,
        "message": "Test the pure core",
        "kind": "test",
        "summary_md": "Adds `tests/test_report.py`: 17 tests (each `parametrize` case counts) of `total_by_category`, `largest_expense` and `format_report`. A fixture provides four expenses; `parametrize` covers the category and minimum filters; edge cases include no expenses, an amount equal to the minimum, a refund, a category nobody used and ties. No test touches a file.",
        "concepts_md": "Session 8: Arrange-Act-Assert, fixtures, `parametrize`, choosing edge cases on purpose, and 'pure functions test themselves', the pay-off of v0.3's core.",
        "message_md": "Good and short. 'the pure core' tells the reader what kind of tests these are, which matters for Checkpoint 2's 'mostly pure' rule.",
        "section_ref": sid(7),
    },
    {
        "hash": "f3d9870",
        "tag": None,
        "message": "Test reading a file and the missing-file exit code",
        "kind": "test",
        "summary_md": "Adds `tests/test_io.py`, the two tests at the edge: `tmp_path` builds a CSV with a broken row and checks only the two good rows are read; `CliRunner` runs `report nosuch.csv` and checks exit code 1 and the message on stderr. The second test passes only because 15836e1 moved the message to stderr.",
        "concepts_md": "Session 8's 'the parts that touch the world': `tmp_path` for the one file, `CliRunner` for the command line, one or two I/O tests chosen on purpose.",
        "message_md": "Good. It names both behaviours tested, so a reader knows what is covered without opening the file.",
        "section_ref": sid(7),
    },
    {
        "hash": "0e05065",
        "tag": None,
        "message": "Run ruff, mypy and pytest on every push",
        "kind": "ci",
        "summary_md": "Adds `.github/workflows/check.yml`: on every push and pull request, GitHub checks out the code, installs uv and Python 3.13, runs `uv sync --locked`, then `ruff check`, `ruff format --check`, `mypy src tests` and `pytest`. A failing step stops the run and marks the commit red.",
        "concepts_md": "Session 3's CI referee (the project brief: 'the referee, not the judge'), session 4's `uv sync --locked`, and session 5's exit codes: each step passes or fails by its exit code.",
        "message_md": "Good. It says what runs and when, from the project's side. *Add check.yml* would name the file and leave the reader to open it.",
        "section_ref": sid(7),
    },
    {
        "hash": "e1b96de",
        "tag": None,
        "message": "Add failing tests for remove_duplicates",
        "kind": "test",
        "summary_md": "The red step of session 8's live cycle. Five tests in `tests/test_duplicates.py` say what `remove_duplicates` must do, and a stub in `report.py` (`return expenses`) gives them something to import. Two tests fail (an exact duplicate, many copies) and three pass by luck, because returning the input is right when there is nothing to remove.",
        "concepts_md": "Session 8's red, green, refactor: write a test for behaviour that does not exist and watch it fail; 'first a stub, return expenses, so the failure says something'; 'red is information, not a problem'.",
        "message_md": "Good and plain: it says the tests fail, so nobody mistakes the red check for an accident.",
        "section_ref": sid(7),
    },
    {
        "hash": "1e421bc",
        "tag": None,
        "message": "Remove duplicates with a seen-set",
        "kind": "feature",
        "summary_md": "The green step: the smallest code that passes. A loop keeps a `seen` set and appends each expense the first time it appears. All 24 tests pass. `remove_duplicates` exists and is tested, but the report does not call it yet.",
        "concepts_md": "Session 8: 'Green: write the smallest code that makes it pass.' 'Not elegant. Nobody asked for elegant yet.' The set needs hashable items, which `frozen=True` provides.",
        "message_md": "Good: what it does and, in two words, how. Naming the approach is fair here, because the next commit replaces it.",
        "section_ref": sid(7),
    },
    {
        "hash": "d3df52b",
        "tag": "v0.4",
        "message": "Use dict.fromkeys to drop duplicates in order",
        "kind": "refactor",
        "summary_md": "The refactor step: the loop becomes `return list(dict.fromkeys(expenses))`. Dictionaries keep insertion order, so the first of each expense stays in place, and `Expense` is hashable because it is frozen. The same 24 tests stay green. On the sample file 420 expenses become 414. Tagged `v0.4`: \"Tested core: pytest, CI and one red-green-refactor cycle\".",
        "concepts_md": "Session 8: 'Refactor: clean up, with the test as your safety net', and 'session 6's frozen=True pays off here'.",
        "message_md": "Good. It names the technique and the behaviour it keeps ('in order'), which is what a reader needs to trust a one-line change.",
        "section_ref": sid(7),
    },
    {
        "hash": "8492f59",
        "tag": None,
        "message": "Add scripts/check.sh to run every check with one command",
        "kind": "build",
        "summary_md": "Adds `scripts/check.sh`, 14 lines, committed as an executable (`100755`). With `set -euo pipefail` it runs `ruff check`, `ruff format --check`, `mypy src tests` and `pytest` in that order, printing `==> name` before each, and stops at the first one that fails. It is developer tooling: nothing runs it automatically, CI does not call it yet and the report is identical. At this commit it ends with `24 passed`.",
        "concepts_md": "Session 10's `scripts/check.sh` (slides 17 and 18) and session 9's x bit (\"In CI it needs the x bit too, and git remembers it\"). The same four commands as lab 01's \"If they pass here, they pass there\", behind one name; exit code 0 is green.",
        "message_md": "Good. It says what the script is for, not what is inside it, and 'every check' and 'one command' are the words someone searching the log would use. Filed as build because it is a tool for the developer and no automated check runs it.",
        "section_ref": sid(9),
    },
    {
        "hash": "8fabdb3",
        "tag": None,
        "message": "Run scripts/check.sh in CI instead of four separate steps",
        "kind": "ci",
        "summary_md": "In `.github/workflows/check.yml` the four steps after `uv sync --locked` (Lint, Formatting, Types, Tests) are replaced by one, `Run the checks`, that runs `scripts/check.sh`: 2 lines added, 11 deleted. The commands are the same four; what changes is that GitHub now shows one step instead of four. From here until `8a8903d` reverts it, session 10's \"scripts/check.sh is what CI runs\" is literally true.",
        "concepts_md": "Session 9's \"CI is a terminal\": a step is a command, red when it exits non-zero, and the steps after a red one are skipped. Session 10's takeaway that `scripts/check.sh` is what CI runs and exit code 0 is green. One script and four steps give the same verdict; they differ in what the Actions page shows.",
        "message_md": "Clear: it names what runs and what it replaces. It does not say what the single step gives up (separate names for the four checks), which the revert's message supplies eight days later.",
        "section_ref": sid(9),
    },
    {
        "hash": "d814ca9",
        "tag": None,
        "message": "Add filter_by_month and a validator for month strings",
        "kind": "feature",
        "summary_md": "Adds two functions to `report.py`: `is_valid_month`, true only when the whole string matches `\\d{4}-(0[1-9]|1[0-2])` (`fullmatch`, so `2025-07-01` and `2025-13` are rejected), and `filter_by_month`, which keeps the expenses whose date starts with the month and a hyphen. `tests/test_month.py` adds 18 tests: four filter cases, an empty list, four valid months and nine invalid ones. `cli.py` is not in the diff, so no command calls the functions and the report is the same; `--month` is still 'No such option'.",
        "concepts_md": "The pattern of `d38d9e6` and `1e421bc`: pure functions in the core, tested with a list and a string and no file, before the shell uses them. Session 8's `parametrize` and edge cases chosen on purpose (`2025-00`, `2025-13`, the first and last day of a month, a month of another year).",
        "message_md": "Good. It names both additions, and the 'and' joins two halves of one feature, month filtering, each tested in the same commit. Someone looking for where the month check came from finds it.",
        "section_ref": sid(9),
    },
    {
        "hash": "416604b",
        "tag": None,
        "message": "Add a --month option to the report command",
        "kind": "feature",
        "summary_md": "Adds `--month` to the `report` command, a `month: 2025-07` line to the header and an example to the README. `cli.py` checks the month first: one that is not `YYYY-MM` prints `month must look like 2025-07, not 2025-13` to standard error and exits with code 2, before the file is opened, while a missing file is still 1. A valid month filters the list before the totals and the largest are worked out, so with `--month 2025-09` the largest expense is that month's (Abacus, 2025-09-15), where `--category dining` still names `Ferreteria Mas` from November. `tests/test_cli_month.py` adds two `CliRunner` tests, 44 in all.",
        "concepts_md": "Sample question 2: \"Adding a `--month` option to the report command\" is the option that is not a refactoring, because the program now does something new. Session 5's options with defaults and exit codes (a different number for a different failure, as `grep` does), session 7's 'fail loudly, at the boundary', and session 8's edge tests with `CliRunner`.",
        "message_md": "Good. Imperative, and it names the option as the user types it and the command it belongs to, so a search for `--month` finds it. The README line and the tests belong to the same feature and travel with it.",
        "section_ref": sid(9),
    },
    {
        "hash": "8a8903d",
        "tag": "v0.5",
        "message": "Revert \"Run scripts/check.sh in CI instead of four separate steps\"",
        "kind": "ci",
        "summary_md": "Undoes `8fabdb3`: `check.yml` has the four named steps again, byte for byte as at v0.4, and `scripts/check.sh` stays \"for running the same checks before a push\". The subject (`Revert \"...\"`) and the line `This reverts commit 8fabdb3...` are the form `git revert` writes by default; the paragraph under them is the author's reason: one step called \"Run the checks\" hides which check failed, so a red run means opening the log, while separate steps say it in the Actions summary. `8fabdb3` is not removed from the history. Tagged `v0.5`: \"check.sh, a --month filter, and a second author\".",
        "concepts_md": "Session 9's \"CI is a terminal\": the Actions summary shows one line per step, so one step hides which of ruff, mypy and pytest failed. Slide 21's \"scripts/check.sh is what CI runs\" gives the idea; at this commit the repository's CI does not call the script, and the script is the local rehearsal of the same four checks (lab 01: \"If they pass here, they pass there\").",
        "message_md": "A model revert. The subject says what is undone, and the body gives the reason that the original message left out, so whoever finds `8fabdb3` in the log knows what the one-step version costs.",
        "section_ref": sid(9),
    },
]

# --------------------------------------------------------------------------------------
# Module
# --------------------------------------------------------------------------------------

for sec in sections:
    sec["check"] = [keys[k] for k in sec["check"]]

module: dict[str, Any] = {
    "id": MID,
    "order": 11,
    "module": "X",
    "title": "The expense-tracker history, commit by commit",
    "sessions": [4, 5, 6, 7, 8, 10],
    "predicted": False,
    "sources": [
        "expense-tracker git history (25 commits, tags v0.0–v0.5)",
        "sources/expense-tracker-history.patch",
        "slides-session-4 (slides 19–26)",
        "slides-session-5 (slides 4–13)",
        "slides-session-6 (slides 13–31)",
        "slides-session-7 (slides 3–19)",
        "slides-session-8 (slides 5–29)",
        "slides-session-10 (slides 17–21)",
        "labs/10-check.sh",
        "labs/01-scaffold.md",
        "labs/08-tdd.md",
        "moodle/midterm-sample-questions.md (Q2, Q8)",
        "slides/partial-rubric.txt",
    ],
    "summary_md": "The teacher's advice for the mid-term is to prepare with the slides and \"the expense-tracker history on GitHub\". This module walks through all 25 commits of that history, tag by tag: a one-file, 74-line script (v0.0), an installable project (v0.1), clean code (v0.2), a functional core with strict types (v0.3), a tested core with CI (v0.4), and a `check.sh`, a `--month` filter and a CI change that was reverted (v0.5). It also teaches the two reading skills the exam assumes: reading a diff or a `--stat`, and judging a commit message. Every diff, log and tool output here comes from really running git or the course's tools: on the project at that commit or, where a question says so, on a copy changed for the scenario.",
    "exam_focus_md": md(
        """
- A real diff from the history with candidate messages: pick the one a reader six months later needs, and say why (sample Q8).
- "Is this commit a refactoring?" on real commits: decide from the diff whether the output could change (sample Q2).
- A `--stat` or `git log --oneline` excerpt: what kind of change it was, which tag it belongs to, what it made possible.
- What changed between two tags for the user, and what changed for the developer.
- The v0.5 commits: `--month` is a feature and not a refactoring (sample Q2), `d814ca9` changes nothing for a user, and CI runs four named steps at v0.5 although slide 21 says `scripts/check.sh` is what CI runs.
- The red-green-refactor commits: why the tests were committed failing, what the next two commits did, what made `dict.fromkeys` work.
- Open answers in the compare shape: what does the change do, which message is better, one test you would add, in words.
- Never: writing a diff, recalling git flags, or reproducing code.
"""
    ),
    "sections": sections,
    "terms": terms,
    "traps": traps,
    "flashcards": flashcards,
    "questions": questions,
    "commits": commits,
}

if __name__ == "__main__":
    with OUT.open("w", encoding="utf-8") as f:
        json.dump(module, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"wrote {OUT} ({len(questions)} questions, {len(flashcards)} cards, {len(commits)} commits)")
