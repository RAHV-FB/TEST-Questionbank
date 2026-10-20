"""Exercise type T11, "Diffs and commit messages": writes ../T11.json.

Artefacts (diffs, logs, stats, transcripts) are copied from the bank (history.json), the sample
questions and the expense-tracker patch, never invented. Run: python T11.py
"""

import json
from pathlib import Path

# ---------------------------------------------------------------- real artefacts, copied

LOG_TOP = """$ git log --oneline --decorate
8a8903d (HEAD -> main, tag: v0.5, origin/main, origin/HEAD) Revert "Run scripts/check.sh in CI instead of four separate steps"
416604b Add a --month option to the report command
d814ca9 Add filter_by_month and a validator for month strings
..."""

HUNK_04D699F = "\n".join(
    [
        "--- a/src/expense_tracker/report.py",
        "+++ b/src/expense_tracker/report.py",
        "@@ -21,8 +21,8 @@ class Expense:",
        "     amount: float",
        " ",  # a blank context line is a single space
        " ",
        "-def read_expenses(path):",
        "-    expenses = []",
        "+def read_expenses(path: str) -> list[Expense]:",
        "+    expenses: list[Expense] = []",
        "     with open(path) as handle:",
        "         reader = csv.reader(handle)",
        "         next(reader)",
    ]
)

STAT_A953D05 = """ .gitignore                      |  6 ++++++
 .python-version                 |  1 +
 README.md                       |  0
 pyproject.toml                  | 17 +++++++++++++++++
 src/expense_tracker/__init__.py |  2 ++
 uv.lock                         |  8 ++++++++
 6 files changed, 34 insertions(+)"""

Q8_DIFF = """ def load_expenses(path):
     with open(path) as file:
         rows = list(csv.reader(file))
-    return [Expense(row[0], float(row[1])) for row in rows]
+    expenses = [Expense(row[0], float(row[1])) for row in rows]
+    if any(expense.amount < 0 for expense in expenses):
+        raise ValueError("Negative amount in " + path)
+    return expenses"""

# 15836e1 (history-q25): the diff and the two transcripts, exactly as the bank shows them
Q25_DIFF = """@@ -22,7 +27,16 @@ def report(
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
+        typer.echo(line)"""

Q25_BEFORE = """$ uv run expenses report nosuch.csv > out.txt 2> err.txt
$ echo $?
1
$ cat out.txt
could not read nosuch.csv
$ cat err.txt"""

Q25_AFTER = """$ uv run expenses report nosuch.csv > out.txt 2> err.txt
$ echo $?
1
$ cat out.txt
$ cat err.txt
could not read nosuch.csv"""

# ---------------------------------------------------------------- basics

B1 = (
    "A **commit** is a saved snapshot of the whole project plus a message that says what changed. "
    "Its **hash** names it. `git log --oneline` shows the first seven characters of the hash and the "
    "subject line, newest commit first, so the oldest commit is at the bottom.\n\n"
    "```console\n" + LOG_TOP + "\n```\n\n"
    "`HEAD -> main` marks the commit you have checked out. A **tag** such as `v0.5` is a permanent "
    "name for one commit. A commit is a snapshot of everything, so a tag also contains every commit "
    "below it. The demo has six tags: `v0.0` the messy script, `v0.1` packaged, `v0.2` clean code, "
    "`v0.3` functional core with strict types, `v0.4` tests and CI, `v0.5` `check.sh` and `--month`. "
    "Your own group's tags mark other checkpoints, so read what the question says.\n\n"
    "Ask two things of every commit: what kind of change is it, and what did it make possible next?\n\n"
    "| Kind | What it does | Demo example |\n"
    "|---|---|---|\n"
    "| feature | gives the user new behaviour | `416604b` Add a --month option to the report command |\n"
    "| refactor | changes the structure, output identical | `5e9466d` Replace magic numbers with named constants |\n"
    "| test | adds tests only | `f3d9870` Test reading a file and the missing-file exit code |\n"
    "| build or CI | packaging, tool settings, the automated check | `88b83c3` Add pytest and turn on strict type checking |\n"
    "| docs | README, licence | `89afbe1` Add a README and the MIT licence |\n"
    "| fix | repairs a bug | none in the demo history |"
)

B2 = (
    "`git show <hash>` prints a commit's message, then its diff, file by file. Skip the `diff --git` "
    "and `index` lines. This is one hunk of `04d699f` *Add type hints and make the code ruff clean*, with "
    "the file header above it (the file's other hunks are not shown):\n\n"
    "```diff\n" + HUNK_04D699F + "\n```\n\n"
    "| You see | It means |\n"
    "|---|---|\n"
    "| `--- a/...` and `+++ b/...` | the file before and after the commit |\n"
    "| `--- /dev/null` | a new file: there was nothing before |\n"
    "| `+++ /dev/null` | a deleted file |\n"
    "| `@@ -21,8 +21,8 @@` | old file: 8 lines from line 21. New file: 8 lines from line 21 |\n"
    "| the words after the second `@@` | a signpost only, a line from above the hunk |\n"
    "| a line starting with a space | context: unchanged, shown so you can find your place |\n"
    "| a line starting with `-` | removed |\n"
    "| a line starting with `+` | added |\n\n"
    "A changed line appears twice: the `-` line carries the old text and the `+` line the new text. "
    "Here two lines are removed and two are added, so the hunk stays 8 lines long. When a hunk adds "
    "more than it removes, the second length is bigger: `@@ -40,6 +40,9 @@` means 6 old lines became "
    "9 new ones.\n\n"
    "On the paper a diff is often trimmed to a few lines with no headers, as in sample Q8. Read it "
    "the same way. You read diffs. You never write them."
)

B3 = (
    "Read `git show --stat` before you read any code. It prints one line per file and then totals. "
    "This is `a953d05`, which session 4 showed as the moment the code became a project:\n\n"
    "```text\n" + STAT_A953D05 + "\n```\n\n"
    "The number is how many lines changed in that file, and the signs show the share of `+` and `-`. "
    "`README.md | 0` is an empty file that was created. `old => new` is a move. `tracker.py` is not "
    "listed, so this commit changed no report code.\n\n"
    "Then ask what changed for a user who runs `uv run expenses report`. The files tell you.\n\n"
    "| The stat lists | What the user sees |\n"
    "|---|---|\n"
    "| only `tests/` | nothing; the developer gets a safety net (`d38d9e6`) |\n"
    "| only `.github/workflows/` or `scripts/` | nothing; the checks change, the program does not (`0e05065`, `8492f59`) |\n"
    "| `report.py` only, a function no command calls | nothing yet (`1e421bc`) |\n"
    "| `cli.py` with a new command, option or output | something: new behaviour (`bc9ef3d`) |\n"
    "| `pyproject.toml` | read the hunk: tool settings change nothing (`88b83c3`), but `[project.scripts]` can rename the command (`2ecad20`) |\n\n"
    "Session 7 gives the test for a refactoring: \"If the output changes, it was not a refactoring.\" "
    "Session 6 checked it by saving the report before and after and running `diff before.txt after.txt`; "
    "nothing printed means safe. Green CI is weaker evidence. It says no test failed, not that nothing changed."
)

B4 = (
    "A commit message is written once and read for years, mostly as one line in `git log --oneline`, "
    "by someone who was not there. Session 1 lists \"six months on, nobody can read it, not even its "
    "author\" among the ways working code fails. Judge a subject by what that reader can do without "
    "opening the diff.\n\n"
    "Three habits cover almost every subject in the demo. It is **imperative**: *Add*, *Reject*, "
    "*Move*, *Rename*, so it completes \"If applied, this commit will ...\". It says **what the change "
    "does**, because the diff already shows how. It is **specific**: it names the behaviour or the "
    "thing, so a search of the log finds it.\n\n"
    "| Subject | Problem | A subject that works |\n"
    "|---|---|---|\n"
    "| `Fix stuff in loader` | \"stuff\" names nothing, \"loader\" is vague, \"Fix\" claims a bug it does not name | `Reject negative amounts when loading expenses` |\n"
    "| `Update cli.py` | names a file the stat already shows | `Add an add command that writes to data/` |\n"
    "| `Add YAML steps for uv sync and four run commands` | mechanics: it describes the file, not what it makes happen | `Run ruff, mypy and pytest on every push` |\n"
    "| `Various improvements` | fits any commit, so a search of the log finds nothing | `Replace magic numbers with named constants` |\n"
    "| `Refactor` | true and useless; it fits half the history | `Rename calculate_totals to total_by_category` |\n\n"
    "For a refactoring the move itself is the \"what\", and it tells the reader to expect identical output.\n\n"
    "**One logical change per commit.** An \"and\" in a subject is a prompt to check. *Add a README and "
    "the MIT licence* is one change. *Add a --sort option and rename variables* would be two: the renames must "
    "keep the output and the option changes it, so you can no longer check the renames, and a revert "
    "would take both away."
)

# ---------------------------------------------------------------- worked examples

Q8_QUESTION = (
    "A teammate shows you this diff from the expense-tracker history:\n\n"
    "```diff\n" + Q8_DIFF + "\n```\n\n"
    "Two candidate commit messages:\n"
    "- A: `Fix stuff in loader`\n"
    "- B: `Reject negative amounts when loading expenses`\n\n"
    "1. What does this change do?\n"
    "2. Which message is better, and why? Answer from the point of view of someone reading the history six months later.\n"
    "3. Name one test you would add for this change, in words."
)

Q8_STEPS = [
    "Read the diff as a before and an after. The `-` line returned the list straight away. The `+` lines "
    "build the same list first, then check whether any amount is below zero and, if so, raise "
    "`ValueError` with the path in the message. Otherwise they return the list as before.",
    "Say the effect for the caller, not the lines. A file with a negative amount is now refused as a "
    "whole. A file without one loads exactly as before, and an amount of exactly 0 still passes, "
    "because the check is `< 0`. New behaviour, so this is not a refactoring.",
    "Judge the messages by the reader named in the question: someone scanning `git log --oneline` six "
    "months later, wondering why a file with a refund now fails. B states the new behaviour and "
    "contains the words they would search for. A says neither what was fixed nor that behaviour "
    "changed, so they would have to open the diff.",
    "A test in words has three parts: the input, the action, the expected result. A small CSV with one "
    "negative amount in a temporary folder; load it; expect `ValueError`.",
    "Write it numbered 1, 2, 3, one or two sentences each. That is 5–8 lines.",
]

Q8_ANSWER = (
    "1. After building the list, `load_expenses` now raises `ValueError` naming the file if any amount "
    "is negative, so the whole file is rejected. Files without negative amounts load as before, and "
    "zero is still accepted.\n"
    "2. B. It says what behaviour changed, so someone who wonders why a negative amount now fails can "
    "find the commit from one log line. A says neither what was fixed nor that behaviour changed, so "
    "the reader must open the diff.\n"
    "3. Write a CSV with one negative amount in a temporary folder, load it and check that "
    "`ValueError` is raised. (A good second test: an amount of exactly 0 still loads.)\n\n"
    "Part 2 needs the reader's benefit (find the commit, understand it without opening the diff), not "
    "\"B is longer\"."
)

Q25_QUESTION = (
    "`15836e1` *Move printing and exiting out of the report module* deletes `run()` from `report.py` "
    "(where it used `print` and `sys.exit(1)`) and changes the `report` command:\n\n"
    "```diff\n" + Q25_DIFF + "\n```\n\n"
    "The same command, run just before and just after the commit (`> out.txt` saves what goes to "
    "standard output, `2> err.txt` what goes to standard error). Before:\n\n"
    "```console\n" + Q25_BEFORE + "\n```\n\n"
    "After:\n\n"
    "```console\n" + Q25_AFTER + "\n```\n\n"
    "Is 15836e1 a refactoring?\n\n"
    "- a) Yes, purely: nothing that a user or a script could observe has changed at all\n"
    "- b) Mostly: same report and exit code, but the error now goes to stderr on purpose\n"
    "- c) No, it is a feature: the `report` command now does more than before\n"
    "- d) No, it is a bug fix: a missing file used to exit with 0 and now exits with 1"
)

Q25_STEPS = [
    "Kind of change first. `run()` is deleted and its steps are written into the `report` command: "
    "the same work, in a different place. That is the shape of a refactoring.",
    "Apply the test: if the output changes, it was not a refactoring. Check each thing a user or a "
    "script can observe. The report: `typer.echo(line)` prints what `print(line)` printed. The exit "
    "code: both transcripts print `1`.",
    "Now compare the transcripts line by line. Before, `could not read nosuch.csv` is in `out.txt` "
    "and `err.txt` is empty. After, the two have swapped. The diff says why: `err=True`.",
    "Test the other options against that. Option a is false because a script that captures standard "
    "output used to see the message and no longer does. Option c is false because the command does "
    "exactly the same work. Option d is false because both exit codes are 1.",
]

Q25_ANSWER = (
    "**b.** The structure moved and the report and exit code are unchanged, so it is a refactoring "
    "with one small, deliberate behaviour change: the error message now goes to standard error "
    "(session 7: fail loudly, at the boundary). The careful answer names both halves."
)

# ---------------------------------------------------------------- the type file

T11 = {
    "tid": "T11",
    "name": "Diffs and commit messages",
    "shape_md": (
        "Mirrors sample Q8 (compare): a diff from the expense-tracker history and two candidate commit "
        "messages, then what the change does, which message is better for someone reading the history "
        "six months later, and one test in words. The multiple-choice versions ask you to read a hunk, "
        "a `--stat` or a `git log` and say what kind of change it is, whether it is a refactoring, or "
        "what changed for the user."
    ),
    "minutes": 35,
    "one_md": (
        "Read a diff, a `--stat` or a log, say what kind of change it is and whether behaviour "
        "changed, and choose the message that tells a reader six months later what the change does."
    ),
    "spot_md": (
        "- A diff with `-` and `+` lines, often trimmed to a few lines with no headers, or a "
        "`git show --stat`, or a `git log --oneline` excerpt from the expense-tracker.\n"
        "- Two or three candidate commit subjects for one change, and the phrase \"someone reading the "
        "history six months later\".\n"
        "- A judgement question: \"what does this change do?\", \"what kind of change is it?\", \"is it "
        "a refactoring?\", \"what changed for the user?\", \"which commit first lets a user see this?\".\n"
        "- A log with tags (`tag: v0.4`), a revert, or a commit message with a body.\n"
        "- The open version has three parts and 5–8 lines: what the change does, which message is "
        "better and why, one test in words."
    ),
    "basics": [
        {
            "id": "T11-b1",
            "heading": "Commits, the log, tags and the kinds of change",
            "body_md": B1,
        },
        {
            "id": "T11-b2",
            "heading": "Reading one diff, line by line",
            "body_md": B2,
        },
        {
            "id": "T11-b3",
            "heading": "Reading a --stat and asking what changed for the user",
            "body_md": B3,
        },
        {
            "id": "T11-b4",
            "heading": "What a commit message must do",
            "body_md": B4,
        },
    ],
    "checks": [
        {
            "id": "T11-c1",
            "q_md": (
                "A log shows:\n\n"
                "```console\n"
                "04d699f (tag: v0.2) Add type hints and make the code ruff clean\n"
                "017f926 Give an expense a type instead of a tuple\n"
                "9d6c607 Separate reading and printing from the calculation\n"
                "```\n\n"
                "You check out `v0.2`. Does the project you see contain the `Expense` dataclass from `017f926`?"
            ),
            "options": [
                "No: a tag shows only the commit it names",
                "Yes: a tag names a snapshot of the whole project, so every commit below it is included",
                "Only after you also check out `017f926`",
            ],
            "answer": 1,
            "why_md": (
                "A commit is a snapshot of the whole project, so the tag on `04d699f` includes "
                "everything from the commits beneath it. `Expense` arrives in `017f926`, which is "
                "below the tag, so it is in `v0.2`."
            ),
        },
        {
            "id": "T11-c2",
            "q_md": (
                "A log shows:\n\n"
                "```console\n"
                "$ git log --oneline\n"
                "89afbe1 (tag: v0.1) Add a README and the MIT licence\n"
                "bc9ef3d Add an add command that writes to data/\n"
                "2ecad20 Move the report into the package behind a typer CLI\n"
                "```\n\n"
                "Which of the three commits was made first?"
            ),
            "options": [
                "`89afbe1`, because it is at the top and carries the tag",
                "`bc9ef3d`, because it is in the middle",
                "`2ecad20`, because `git log` puts the newest commit first, so the oldest is at the bottom",
            ],
            "answer": 2,
            "why_md": (
                "`git log --oneline` lists the newest commit first. The top line is the latest "
                "commit and the bottom line the oldest."
            ),
        },
        {
            "id": "T11-c3",
            "q_md": (
                "The first hunk of `c746d38` *Print the largest expense* opens with this header:\n\n"
                "```diff\n"
                "@@ -49,6 +49,17 @@ def run(path, cat, minimum):\n"
                "```\n\n"
                "What does it tell you?"
            ),
            "options": [
                "6 lines were removed and 17 lines were added",
                "In the old file the hunk covers 6 lines from line 49; in the new file it covers 17 lines from line 49",
                "The file is now 17 lines long, and 49 of them changed",
            ],
            "answer": 1,
            "why_md": (
                "The pair after `-` describes the hunk in the old file (start line, length) and the "
                "pair after `+` the same hunk in the new file. The 6 and the 17 are lengths of the hunk, "
                "not of the file, and they do not say how many lines were added or removed. "
                "`def run(path, cat, minimum)` is only a signpost."
            ),
        },
        {
            "id": "T11-c4",
            "q_md": (
                "The `--stat` of `d38d9e6` *Test the pure core*:\n\n"
                "```text\n"
                " tests/test_report.py | 113 +++++++++++++++++++++++++++++++++++++++++++++++++++\n"
                " 1 file changed, 113 insertions(+)\n"
                "```\n\n"
                "What changed for someone who only runs `uv run expenses report`?"
            ),
            "options": [
                "Nothing: only a test file changed, so the program prints what it printed before",
                "The report is now checked every time it runs",
                "The totals change, because 113 lines were added",
            ],
            "answer": 0,
            "why_md": (
                "Tests are run by pytest, not by the program. No file the command runs is in the "
                "stat, so its output cannot have changed. The developer gains a safety net."
            ),
        },
        {
            "id": "T11-c5",
            "q_md": (
                "A commit renames `calculate_totals` to `total_by_category` and its parameters to "
                "`expenses`, `category` and `minimum`. The report is identical before and after. "
                "Which subject is best for a reader six months later?"
            ),
            "options": [
                "`Update report.py`",
                "`Refactor`",
                "`Rename calculate_totals to total_by_category`",
                "`Fix the names in report.py`",
            ],
            "answer": 2,
            "why_md": (
                "For a refactoring the move is the what, and the new name is something a reader can "
                "search for. `Update report.py` names a file the stat shows, `Refactor` fits half the "
                "history, and `Fix` claims a bug that did not exist."
            ),
        },
    ],
    "method": [
        "**Read the artefact first.** For a log, the newest commit is on top and tags sit on their commits. "
        "For a stat, see which files changed and by how much. For a diff, check whether the file is new "
        "(`/dev/null` before), then read each `-` and `+` as before and after. A slide gives the idea and "
        "the artefact gives the facts, so answer from what you are shown.",
        "**Name the kind of change:** feature, refactor, test, build or CI, docs, fix. Ask whether a user "
        "could see a different output. If the output changes, it was not a refactoring.",
        "**Say what the change does** in one sentence a user would understand, not line by line. Among "
        "moved or reordered lines, hunt for the one value that changed.",
        "**Judge the messages.** Prefer the subject that is imperative, says what the change does and is "
        "specific. Reject a file name, mechanics, vague words, \"Fix\" where nothing was broken and "
        "\"Refactor\" where the output changes. Give the reason as the reader's benefit: they can find "
        "and understand it from the log line without opening the diff.",
        "**Check for a mix.** If one commit holds two kinds of change, say so and ask for a split: one "
        "logical change per commit, so each part can be checked and reverted on its own.",
        "**A test in words** has an input, an action and an expected result, aimed at an edge: the "
        "boundary, an empty input, a missing file. No code. Number the parts 1, 2, 3 and write 5–8 lines.",
    ],
    "worked": [
        {
            "title": "Sample Q8 (compare)",
            "question_md": Q8_QUESTION,
            "steps_md": Q8_STEPS,
            "answer_md": Q8_ANSWER,
        },
        {
            "title": "A real commit: is it a refactoring? (15836e1)",
            "question_md": Q25_QUESTION,
            "steps_md": Q25_STEPS,
            "answer_md": Q25_ANSWER,
        },
    ],
    "twists": [
        {
            "twist_md": (
                "A subject names the technique and not the purpose, as in `Use dict.fromkeys to drop "
                "duplicates in order`. Is it a bad message?"
            ),
            "how_md": (
                "It is the one deliberate exception in the history. In the refactor step of red, green, "
                "refactor the behaviour stays the same and the technique is what changed, so the subject "
                "names it. The pair is `Remove duplicates with a seen-set`, then the `dict.fromkeys` "
                "commit, with the same 24 tests passing. For a feature or a fix, a subject that lists "
                "mechanics instead of behaviour is still the weaker one."
            ),
        },
        {
            "twist_md": (
                "The diff is a refactoring and the choice is between `Refactor` and a subject that "
                "names the move."
            ),
            "how_md": (
                "Pick the one that names the move, such as `Replace magic numbers with named constants` "
                "or `Rename calculate_totals to total_by_category`. `Refactor` is true and useless, "
                "because most of the clean-code commits are refactorings. A good refactoring subject "
                "also tells the reader to expect identical output."
            ),
        },
        {
            "twist_md": (
                "The subject says one thing and the diff does more. `04d699f` is called `Add type hints "
                "and make the code ruff clean`, and the diff also changes `except:` to "
                "`except (OSError, ValueError):`."
            ),
            "how_md": (
                "Read the whole diff, not only the subject. The narrower `except` changes how the "
                "program fails: a 0-byte file used to print `could not read` and now ends in a "
                "traceback. So the commit is not purely a tidy-up, and the log does not say so. Name "
                "the extra change, say it deserves its own commit or a subject that mentions it, and "
                "name a test that would pin it. This is the history's one exception to \"one logical "
                "change per commit\"."
            ),
        },
        {
            "twist_md": (
                "Ruff, mypy and pytest are green, and a teammate says the commit therefore changed "
                "no behaviour."
            ),
            "how_md": (
                "Green means no test failed, not that nothing changed. A refactoring is checked on the "
                "output: run the program before and after on real data and compare, as session 6 did "
                "with `diff before.txt after.txt`. If a changed value or condition would pass every "
                "test, name the test that is missing."
            ),
        },
        {
            "twist_md": (
                "The message is good, but the change is questionable: `Reject negative amounts when "
                "loading expenses`, while the team's tests already treat a negative amount as a refund."
            ),
            "how_md": (
                "Separate the message from the decision. The message is good because it makes the "
                "decision visible and easy to find. The decision conflicts with a rule the team "
                "agreed. Raise it with the team before accepting, and name a test with a "
                "refund row that must still load."
            ),
        },
        {
            "twist_md": (
                "A `--stat` or a log, and the question is \"what changed for the user between these "
                "two tags?\"."
            ),
            "how_md": (
                "Look for `cli.py` or whatever the command runs. Tests, the workflow, `scripts/`, "
                "the README and a function no command calls change nothing a user sees. Read any "
                "`pyproject.toml` hunk: tool settings change nothing, but `[project.scripts]` can "
                "rename the command. Say separately what the developer gained."
            ),
        },
        {
            "twist_md": (
                "A slide says one thing and the log or file in front of you shows another, for "
                "example about what CI runs at a tag."
            ),
            "how_md": (
                "A slide gives the idea and the artefact gives the facts, so answer from what you are "
                "shown. For a file, read the log from the top: the newest commit that touches it "
                "decides what it contains, and a revert cancels the commit it names. Then say what "
                "the slide still gets right."
            ),
        },
        {
            "twist_md": "A commit message with a body, as in a revert, and the question \"according to the message, why?\".",
            "how_md": (
                "Answer only from the text. The message names the commit it undoes and gives one "
                "reason: one step called \"Run the checks\" hides which check failed. Do not bring in "
                "reasons from other lessons, such as speed or the executable bit, that the message "
                "never mentions."
            ),
        },
    ],
    "traps": [
        "**\"B is better because it is longer or more detailed.\"** Length is not the reason, and \"A names the "
        "function, so it is more precise\" is not either. B says what the program now does, so the reader finds "
        "it and understands it from the log line without opening the diff. Always name that reader.",
        "**\"Test that it works.\"** A test in words needs an input, an action and an expected result: a CSV "
        "with one negative amount, load it, expect `ValueError`. Writing code instead of words is not asked for.",
        "**Reading a changed line as one line.** It appears twice: a `-` line with the old text and a `+` "
        "line with the new. Only the `+` line is in the file afterwards.",
        "**Reading `@@ -40,6 +40,9 @@` as \"lines 40 to 46 were deleted\", or as the size of the file.** The pairs "
        "are the start line and length of this hunk, in the old file and in the new file.",
        "**\"The report is identical on the sample data, so it is a refactoring.\"** That is evidence for one "
        "input. Look in the diff for a changed value or condition, and ask which test would catch it. "
        "Green checks show only that no test failed.",
        "**\"v0.4 removed the duplicates from the report.\"** A test or CI commit, or a function no command "
        "calls, changes nothing for the user. Check whether `cli.py` is in the stat.",
        "**\"A revert deletes the commit\" and \"a tag moves forward with new commits\".** A revert adds a commit "
        "that cancels the change, and the original stays in the log. A tag stays on the commit it names. If "
        "CI was red there, fix, push, wait for green, then move the tag yourself.",
        "**\"I deleted the file, so it is gone from the repository.\"** A commit is a snapshot, so the earlier "
        "commits still hold the file, and on a public repository anyone can open them. Ignore `data/` "
        "before anything is added.",
    ],
    "say_md": (
        "- The subject says what the change does for the program. The diff already shows how.\n"
        "- Someone reading `git log --oneline` six months later can find it, and understand it, without "
        "opening the diff.\n"
        "- `Fix stuff in loader` says nothing: \"stuff\" names nothing, \"loader\" is vague, and \"Fix\" "
        "claims a bug it does not name.\n"
        "- If the output changes, it was not a refactoring.\n"
        "- If a commit mixes a refactoring with a behaviour change, split it. One logical change per commit, so "
        "each part can be checked and reverted on its own.\n"
        "- `---` is the file before and `+++` the file after. `-` is removed, `+` is added, a space is "
        "unchanged context. `/dev/null` before means a new file.\n"
        "- `@@ -40,6 +40,9 @@`: the old file has 6 lines from line 40, the new file 9 lines from line 40.\n"
        "- In a `--stat`, `old => new` is a move.\n"
        "- Nothing changed for the user: `cli.py` is untouched, or no command calls the new function.\n"
        "- Green checks mean no test failed. They do not prove the behaviour is the same.\n"
        "- A tag is a permanent name for one commit. A revert adds a commit that undoes an earlier one, "
        "and the original stays in the log.\n"
        "- A test in words: the input, the action, the expected result. A CSV with one negative amount, "
        "load it, expect `ValueError`."
    ),
    "practice": [
        "history-q03",
        "history-q40",
        "history-q01",
        "history-q06",
        "history-q39",
        "history-q10",
        "history-q41",
        "history-q52",
        "history-q43",
        "history-q50",
        "history-q53",
        "history-q36",
        "history-q49",
    ],
}

if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "T11.json"
    out.write_text(json.dumps(T11, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {out}")
