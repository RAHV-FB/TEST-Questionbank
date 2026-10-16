"""Generator for content/pipes-bash.json (module M3, session 10).

Rebuilt on Fri 16 Oct 2026, after the session, from its slides (sources/slides/slides-session-10.txt),
the labs 10-wrangling.md and 10-bash.md, and v0.5's scripts/check.sh. The first version was written
on Wed 14 Oct, before the slides existed; what the slides confirm is kept.

Every shell, ruff, mypy, pytest, uv and git output below was produced by running it
(LC_ALL=C, bash) in the work folders scratchpad/work/pipes-bash/ (first version, expense-tracker
v0.4) and scratchpad/work/s10/ (session 10, expense-tracker v0.5; run logs: runs/*.out), and is
shown in GNU format: `wc -l` without padding, `uniq -c` counts right-aligned in a 7-wide field.
Pipeline stage outputs were also cross-checked against an independent emulation of GNU semantics
(run_pipelines.py: 0 mismatches).
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path
from typing import Any

MID = "pipes-bash"
OUT = Path(__file__).resolve().parent.parent / f"{MID}.json"


def md(s: str) -> str:
    return textwrap.dedent(s).strip("\n")


# ---------------------------------------------------------------------------
# The sample file (modelled on the real 420-row expenses.csv: same header, same 8
# categories, two exact duplicate rows (one pair adjacent, one not), a merchant whose
# name contains a category word, amounts with 1, 2 and 3 digits before the point).
# ---------------------------------------------------------------------------
SAMPLE = """date,merchant,category,amount
2025-07-01,Cabify,transport,36.25
2025-07-01,Lidl,groceries,56.77
2025-07-02,Abacus,education,137.97
2025-07-03,Can Recasens,dining,33.02
2025-07-03,Can Recasens,dining,33.02
2025-07-05,Ikea,home,91.60
2025-07-05,Spotify,entertainment,11.55
2025-07-06,Sushi at home,dining,24.90
2025-07-07,Mercadona,groceries,21.50
2025-07-07,Bar Ramon,dining,9.80
2025-07-07,Mercadona,groceries,21.50
2025-07-08,Bonpreu,groceries,8.66
2025-07-09,Farmacia Gala,health,14.20
2025-07-10,Federal Cafe,dining,53.82
2025-07-12,Endesa,utilities,62.10
2025-07-14,Leroy Merlin,home,250.83
2025-07-15,Cabify,transport,12.40
2025-07-15,Bicing,transport,50.47
"""

FILE_BLOCK = "```text\n" + SAMPLE + "```"
FILE_INTRO = "The sample `expenses.csv` (a header and 18 expenses):\n\n" + FILE_BLOCK

ROWS = SAMPLE.splitlines()[1:]
HEADER = SAMPLE.splitlines()[0]


def lines(*xs: str) -> str:
    return "\n".join(xs)


# Stage outputs, exactly as run (GNU format).
P_DINING = lines(
    "2025-07-03,Can Recasens,dining,33.02",
    "2025-07-03,Can Recasens,dining,33.02",
    "2025-07-06,Sushi at home,dining,24.90",
    "2025-07-07,Bar Ramon,dining,9.80",
    "2025-07-10,Federal Cafe,dining,53.82",
)
P_HOME = lines(
    "2025-07-05,Ikea,home,91.60",
    "2025-07-06,Sushi at home,dining,24.90",
    "2025-07-14,Leroy Merlin,home,250.83",
)
P_NOT_DINING = lines(
    HEADER,
    "2025-07-01,Cabify,transport,36.25",
    "2025-07-01,Lidl,groceries,56.77",
    "2025-07-02,Abacus,education,137.97",
    "2025-07-05,Ikea,home,91.60",
    "2025-07-05,Spotify,entertainment,11.55",
    "2025-07-07,Mercadona,groceries,21.50",
    "2025-07-07,Mercadona,groceries,21.50",
    "2025-07-08,Bonpreu,groceries,8.66",
    "2025-07-09,Farmacia Gala,health,14.20",
    "2025-07-12,Endesa,utilities,62.10",
    "2025-07-14,Leroy Merlin,home,250.83",
    "2025-07-15,Cabify,transport,12.40",
    "2025-07-15,Bicing,transport,50.47",
)
P_BODY = lines(*ROWS)
P_CATS = lines(*[r.split(",")[2] for r in ROWS])
P_CATS_SORTED = lines(
    "dining", "dining", "dining", "dining", "dining", "education", "entertainment",
    "groceries", "groceries", "groceries", "groceries", "health", "home", "home",
    "transport", "transport", "transport", "utilities",
)
P_CATS_DISTINCT = lines(
    "dining", "education", "entertainment", "groceries", "health", "home", "transport",
    "utilities",
)
P_GROCERIES = lines(
    "2025-07-01,Lidl,groceries,56.77",
    "2025-07-07,Mercadona,groceries,21.50",
    "2025-07-07,Mercadona,groceries,21.50",
    "2025-07-08,Bonpreu,groceries,8.66",
)
P_CATS_COUNTED = lines(
    "      5 dining",
    "      1 education",
    "      1 entertainment",
    "      4 groceries",
    "      1 health",
    "      2 home",
    "      3 transport",
    "      1 utilities",
)
P_CATS_RANKED = lines(
    "      5 dining",
    "      4 groceries",
    "      3 transport",
    "      2 home",
    "      1 utilities",
    "      1 health",
    "      1 entertainment",
    "      1 education",
)
P_AMOUNTS_WITH_HEADER = lines("amount", *[r.split(",")[3] for r in ROWS])
P_AMOUNTS_TEXT_REV = lines(
    "amount", "91.60", "9.80", "8.66", "62.10", "56.77", "53.82", "50.47", "36.25",
    "33.02", "33.02", "250.83", "24.90", "21.50", "21.50", "14.20", "137.97", "12.40",
    "11.55",
)
P_AMOUNTS = lines(*[r.split(",")[3] for r in ROWS])
P_AMOUNTS_NUM_REV = lines(
    "250.83", "137.97", "91.60", "62.10", "56.77", "53.82", "50.47", "36.25", "33.02",
    "33.02", "24.90", "21.50", "21.50", "14.20", "12.40", "11.55", "9.80", "8.66",
)
P_ROWS_BY_AMOUNT = lines(
    "2025-07-14,Leroy Merlin,home,250.83",
    "2025-07-02,Abacus,education,137.97",
    "2025-07-05,Ikea,home,91.60",
    "2025-07-12,Endesa,utilities,62.10",
    "2025-07-01,Lidl,groceries,56.77",
    "2025-07-10,Federal Cafe,dining,53.82",
    "2025-07-15,Bicing,transport,50.47",
    "2025-07-01,Cabify,transport,36.25",
    "2025-07-03,Can Recasens,dining,33.02",
    "2025-07-03,Can Recasens,dining,33.02",
    "2025-07-06,Sushi at home,dining,24.90",
    "2025-07-07,Mercadona,groceries,21.50",
    "2025-07-07,Mercadona,groceries,21.50",
    "2025-07-09,Farmacia Gala,health,14.20",
    "2025-07-15,Cabify,transport,12.40",
    "2025-07-05,Spotify,entertainment,11.55",
    "2025-07-07,Bar Ramon,dining,9.80",
    "2025-07-08,Bonpreu,groceries,8.66",
)
P_SORTED_FILE = lines(
    "2025-07-01,Cabify,transport,36.25",
    "2025-07-01,Lidl,groceries,56.77",
    "2025-07-02,Abacus,education,137.97",
    "2025-07-03,Can Recasens,dining,33.02",
    "2025-07-03,Can Recasens,dining,33.02",
    "2025-07-05,Ikea,home,91.60",
    "2025-07-05,Spotify,entertainment,11.55",
    "2025-07-06,Sushi at home,dining,24.90",
    "2025-07-07,Bar Ramon,dining,9.80",
    "2025-07-07,Mercadona,groceries,21.50",
    "2025-07-07,Mercadona,groceries,21.50",
    "2025-07-08,Bonpreu,groceries,8.66",
    "2025-07-09,Farmacia Gala,health,14.20",
    "2025-07-10,Federal Cafe,dining,53.82",
    "2025-07-12,Endesa,utilities,62.10",
    "2025-07-14,Leroy Merlin,home,250.83",
    "2025-07-15,Bicing,transport,50.47",
    "2025-07-15,Cabify,transport,12.40",
    HEADER,
)
P_DUPES = lines(
    "2025-07-03,Can Recasens,dining,33.02",
    "2025-07-07,Mercadona,groceries,21.50",
)
P_MERCHANTS = lines(*[r.split(",")[1] for r in ROWS])
P_MERCHANTS_SORTED = lines(
    "Abacus", "Bar Ramon", "Bicing", "Bonpreu", "Cabify", "Cabify", "Can Recasens",
    "Can Recasens", "Endesa", "Farmacia Gala", "Federal Cafe", "Ikea", "Leroy Merlin",
    "Lidl", "Mercadona", "Mercadona", "Spotify", "Sushi at home",
)

# Real ruff 0.16.9 output (scripts/check.sh at the v0.5 tag with `import os` added to report.py).
RUFF_F401 = md(
    """
    F401 [*] `os` imported but unused
     --> src/expense_tracker/report.py:2:8
      |
    1 | import csv
    2 | import os
      |        ^^
    3 | import re
    4 | from dataclasses import dataclass
      |
    help: Remove unused import: `os`
      |
    1 | import csv
      - import os
    2 | import re
      |

    Found 1 error.
    [*] 1 fixable with the `--fix` option.
    """
)

# The class version (session 10, slide 17), identical to scripts/check.sh at the v0.5 tag.
CHECK_SH = md(
    """
    #!/usr/bin/env bash
    set -euo pipefail

    echo "==> ruff check"
    uv run ruff check .

    echo "==> ruff format"
    uv run ruff format --check .

    echo "==> mypy"
    uv run mypy src tests

    echo "==> pytest"
    uv run pytest
    """
)

RUBRIC_LINE = (
    "uv run ruff check . && uv run ruff format --check . \\\n"
    "&& uv run mypy src tests && uv run pytest"
)

CHECK_YML_STEPS = md(
    """
    jobs:
      check:
        runs-on: ubuntu-latest

        steps:
          - name: Check out the code
            uses: actions/checkout@v7

          - name: Install uv (and Python 3.13)
            uses: astral-sh/setup-uv@v7
            with:
              python-version: "3.13"

          - name: Install dependencies from the lockfile
            run: uv sync --locked

          - name: Lint
            run: uv run ruff check .

          - name: Formatting
            run: uv run ruff format --check .

          - name: Types
            run: uv run mypy src tests

          - name: Tests
            run: uv run pytest
    """
)

COUNT_SH_UNQUOTED = md(
    """
    #!/usr/bin/env bash
    file=$1
    echo "Dining expenses in $file:"
    grep dining $file | wc -l
    """
)

TOTALS_SH = md(
    """
    #!/usr/bin/env bash
    set -euo pipefail
    file="$1"
    echo "Report for $file"
    dining=$(grep dining "$file" | wc -l)
    clothing=$(grep clothing "$file" | wc -l)
    echo "dining: $dining"
    echo "clothing: $clothing"
    """
)

CHECK_DIFF = md(
    """
    diff --git a/scripts/check.sh b/scripts/check.sh
    index 46245be..46862c3 100755
    --- a/scripts/check.sh
    +++ b/scripts/check.sh
    @@ -1,6 +1,8 @@
     #!/usr/bin/env bash
    +set -euo pipefail
    +
     uv run ruff check .
     uv run ruff format --check .
     uv run mypy src tests
     uv run pytest -q
     echo "Ready to tag"
    """
)

MONTHLY_SH = md(
    """
    #!/usr/bin/env bash
    set -euo pipefail
    file="$1"
    echo "Report for $file"
    dining=$(grep -c dining "$file")
    clothing=$(grep -c clothing "$file")
    echo "dining: $dining"
    echo "clothing: $clothing"
    """
)


def fence(lang: str, body: str) -> str:
    return f"```{lang}\n{body}\n```"


def parts(*ps: str) -> str:
    """Join Markdown parts with blank lines; each part is dedented on its own, so code
    spliced in from constants never breaks the indentation of the surrounding text."""
    return "\n\n".join(md(p) for p in ps)


# ---------------------------------------------------------------------------
# Question builders
# ---------------------------------------------------------------------------
QUESTIONS: list[dict[str, Any]] = []


def common(
    qid: str,
    qtype: str,
    level: str,
    skills: list[str],
    section: int,
    stem: str,
    explanation: str,
    source_ref: str,
    verified_by: str,
    origin: str = "slides",
) -> dict[str, Any]:
    return {
        "id": f"{MID}-{qid}",
        "type": qtype,
        "level": level,
        "skills": skills,
        "stem_md": md(stem),
        "explanation_md": md(explanation),
        "section_ref": f"{MID}-s{section}",
        "source_ref": source_ref,
        "origin": origin,
        "verified_by": verified_by,
    }


def mcq(
    qid: str,
    level: str,
    skills: list[str],
    section: int,
    stem: str,
    options: list[tuple[str, bool, str]],
    explanation: str,
    source_ref: str,
    verified_by: str,
    origin: str = "slides",
) -> None:
    q = common(
        qid, "mcq", level, skills, section, stem, explanation, source_ref, verified_by, origin
    )
    q["options"] = [
        {"text_md": md(t), "correct": c, "why_md": md(w)} for (t, c, w) in options
    ]
    QUESTIONS.append(q)


def openq(
    qid: str,
    level: str,
    skills: list[str],
    section: int,
    stem: str,
    parts: list[dict[str, Any]],
    explanation: str,
    source_ref: str,
    verified_by: str,
) -> None:
    q = common(qid, "open", level, skills, section, stem, explanation, source_ref, verified_by)
    q["parts"] = [
        {
            "label": p["label"],
            "prompt_md": md(p["prompt"]),
            "marks": p["marks"],
            "model_answer_md": md(p["model"]),
            "rubric": [md(r) for r in p["rubric"]],
            "weak_answers_md": md(p["weak"]),
        }
        for p in parts
    ]
    q["lines"] = "5–8"
    QUESTIONS.append(q)


def sortq(
    qid: str,
    level: str,
    skills: list[str],
    section: int,
    stem: str,
    categories: list[tuple[str, str]],
    items: list[tuple[str, str, str]],
    explanation: str,
    source_ref: str,
    verified_by: str,
) -> None:
    q = common(qid, "sort", level, skills, section, stem, explanation, source_ref, verified_by)
    q["categories"] = [{"id": i, "label": label} for (i, label) in categories]
    q["items"] = [{"text_md": md(t), "category": c, "why_md": md(w)} for (t, c, w) in items]
    QUESTIONS.append(q)


# ===========================================================================
# Section 1: streams
# ===========================================================================
mcq(
    "q01", "core", ["concept"], 1,
    """
    A program started from the shell has three standard streams. Which statement about them is right?
    """,
    [
        (
            "stdin holds the command-line arguments, stdout holds the result, and stderr holds the exit code",
            False,
            "Arguments are not read from stdin, and the exit code is a number the program leaves behind, not a stream of text.",
        ),
        (
            "stdout carries the result and stderr the problems; both show in the terminal by default",
            True,
            "Right: two separate output channels that share one window by default. The shell can send each one to a different place.",
        ),
        (
            "stderr is only used when Python crashes with a traceback; normal programs write everything to stdout",
            False,
            "The expense-tracker writes `could not read nosuch.csv` to stderr on purpose with `typer.echo(..., err=True)`; no traceback is involved.",
        ),
        (
            "stdout and stderr are two files that the program creates in the current folder when it runs",
            False,
            "They are streams, not files. They only end up in a file if you redirect them with `>` or `2>`.",
        ),
    ],
    """
    Every program gets stdin (what it reads, the keyboard by default), stdout (its result) and stderr (its complaints). stdout and stderr both show in the terminal, which is why they look like one thing until you redirect or pipe. The expense-tracker uses the split deliberately since session 7: report lines with `typer.echo(line)`, the error with `typer.echo(..., err=True)` plus `typer.Exit(1)`. Arguments such as `nosuch.csv` are not stdin, and the exit code is not a stream.
    """,
    "S7 slide 19; expense-tracker v0.4 cli.py; S10 slide 5",
    "source",
)

mcq(
    "q02", "exam", ["read-tool-output", "concept"], 1,
    """
    A teammate wants to keep the report in a file and runs:

    ```console
    $ uv run expenses report nosuch.csv > report.txt
    could not read nosuch.csv
    ```

    They expected `>` to send everything into `report.txt`. Why did the message still appear on the screen?
    """,
    [
        (
            "`>` only works when the command succeeds, so the shell printed the output on the screen instead",
            False,
            "`>` does not depend on success: the shell sets it up before the program starts. It redirected stdout, which was empty.",
        ),
        (
            "The shell prints a message of its own whenever a command exits with a non-zero code",
            False,
            "The shell prints nothing for a non-zero exit; it just records the code in `$?`. The text came from the program.",
        ),
        (
            "The program wrote it to stderr with `typer.echo(..., err=True)`, and `>` redirects only stdout",
            True,
            "Right: `>` moves stdout to the file; stderr still goes to the terminal, so the complaint reaches a human.",
        ),
        (
            "`report.txt` did not exist yet, so the text had nowhere to go except the screen",
            False,
            "`>` creates the file if it is missing. The file exists afterwards; it is just empty.",
        ),
    ],
    """
    `>` is short for `1>`: it redirects stream 1, stdout. The expense-tracker's `cli.py` catches the bad file and calls `typer.echo(f"could not read {path}", err=True)`, which writes to stream 2, stderr, and then `typer.Exit(1)`. stderr was not redirected, so it went to the terminal as usual. That is the point of the design from session 7: a redirected or piped report never contains the error text, and the person still sees what went wrong.
    """,
    "S7 slide 19; run on expense-tracker v0.4 (runs/r1.out)",
    "run",
)

# ===========================================================================
# Section 2: redirection
# ===========================================================================
mcq(
    "q03", "core", ["predict-output"], 2,
    """
    On the sample file (5 dining lines, 3 transport lines) you run:

    ```console
    $ grep dining expenses.csv > notes.txt
    $ grep transport expenses.csv > notes.txt
    ```

    What does `notes.txt` contain now?
    """,
    [
        (
            "Only the 3 transport lines",
            True,
            "Right: the second `>` emptied `notes.txt` and wrote the transport lines into it. The dining lines are gone.",
        ),
        (
            "The 5 dining lines followed by the 3 transport lines",
            False,
            "That is what `>>` would give on the second command. `>` replaces.",
        ),
        (
            "Only the 5 dining lines, because `>` refuses to replace a file",
            False,
            "bash replaces the file without asking. There is no protection against overwriting by default.",
        ),
        (
            "The 3 transport lines followed by the 5 dining lines",
            False,
            "Nothing keeps the old content, before or after. The file holds only the latest output.",
        ),
    ],
    """
    `>` creates the file or replaces its content; `>>` appends to the end. After the second command `notes.txt` holds the three transport lines only (checked by running it). Had the second command used `>>`, the file would have 8 lines: the 5 dining lines, then the 3 transport lines. The same mistake in real life is a monthly report written with `>` each time: every run destroys the previous one.
    """,
    "S10 slides 5, 9; run on the sample file (runs/r3.out)",
    "run",
)

mcq(
    "q04", "hard", ["predict-output", "judgement"], 2,
    """
    Yesterday you saved the full report with `uv run expenses report > report.txt`. Today you run this by mistake:

    ```console
    $ uv run expenses report nosuch.csv > report.txt
    could not read nosuch.csv
    $ echo $?
    1
    ```

    What is in `report.txt` now?
    """,
    [
        (
            "Yesterday's report, unchanged, because the program failed before it could write anything",
            False,
            "The program wrote nothing, but the shell had already emptied the file. A failure does not undo the redirection.",
        ),
        (
            "The line `could not read nosuch.csv`, which replaced yesterday's report",
            False,
            "That line went to stderr, which was not redirected, so it is on the screen, not in the file.",
        ),
        (
            "Yesterday's report, with the line `could not read nosuch.csv` added at the end",
            False,
            "That would need `>>` and a redirected stderr. Neither happened.",
        ),
        (
            "Nothing, because the shell emptied the file before the program even started",
            True,
            "Right: `>` truncates the file first, then the program runs. It failed and printed only to stderr, so the file stays empty.",
        ),
    ],
    """
    The shell prepares redirections before it starts the program: for `> report.txt` it opens the file and cuts it to zero length. Only then does `uv run expenses report nosuch.csv` run. It fails, writes its message to stderr (the screen) and exits 1, without writing a single line to stdout. Running it for real, `wc -l < report.txt` printed `0`. The habit that prevents it: write to a new file name, or think twice before `>` on a file you want to keep.
    """,
    "S10 slides 5, 9; run on expense-tracker v0.4 (runs/r1.out)",
    "run",
)

mcq(
    "q05", "exam", ["read-tool-output", "judgement"], 2,
    """
    A teammate adds `2> /dev/null` to a command in a script "to keep the output clean". You try it:

    ```console
    $ uv run expenses report nosuch.csv 2> /dev/null
    $ echo $?
    1
    ```

    What has the change really done?
    """,
    [
        (
            "It made the command succeed, because the error was thrown away before the shell saw it",
            False,
            "The shell does not read messages to decide success; it reads the exit code, which is still 1.",
        ),
        (
            "It hid the reason, but the exit code is still 1 for `&&`, `set -e` and CI",
            True,
            "Right: `/dev/null` swallows text, not exit codes. You have kept the failure and lost the explanation.",
        ),
        (
            "It threw away the report lines as well, because `/dev/null` swallows all output",
            False,
            "`2>` touches stream 2 only. With a correct file name the report would still print on the screen.",
        ),
        (
            "It saved the error into a file called `null` in a folder called `/dev`, for later reading",
            False,
            "`/dev/null` is a special file that discards whatever is written to it; nothing can be read back.",
        ),
    ],
    """
    `2> /dev/null` sends stderr to a special file that discards it. The run shows the exit code is still `1`: the failure is intact, only the message is gone. For the next command in a chain, for `set -e` and for CI nothing changed, but whoever reads the output now sees a failure with no reason. Session 7's rule was to "fail loudly, at the boundary"; silencing stderr undoes the loud part.
    """,
    "S7 slide 19; run on expense-tracker v0.4 (runs/r2.out)",
    "run",
)

mcq(
    "q11", "core", ["read-tool-output", "concept"], 2,
    """
    On the module's sample file:

    ```console
    $ wc -l expenses.csv
    19 expenses.csv
    $ wc -l < expenses.csv
    19
    ```

    Why does the second command print no file name?
    """,
    [
        (
            "`<` deletes the file name from wc's output once wc has finished counting",
            False,
            "Redirections do not edit a program's output. wc simply had no name to print.",
        ),
        (
            "`<` writes wc's result back into `expenses.csv`, so only the number is left on the screen",
            False,
            "That would be `>`, and it would destroy the file. `<` goes the other way: from the file into the program.",
        ),
        (
            "With `<` the shell feeds the file to wc's stdin, so wc never learns its name",
            True,
            "Right: the program reads stdin without knowing where the text came from. Same count, no name.",
        ),
        (
            "The second form skips the header line, which is where the file name is stored",
            False,
            "Both print 19, so nothing was skipped; the header is a line of data, not a name.",
        ),
    ],
    """
    `wc -l expenses.csv` opens the file itself and reports the count next to the name. With `wc -l < expenses.csv` the shell opens the file and connects it to wc's stdin; wc counts what arrives and has no name to report. This is the same mechanism as a pipe: in `cat expenses.csv | wc -l` wc also reads stdin and prints just `19`. Programs that read stdin are what make composition possible.
    """,
    "S10 slides 5, 9; run on the sample file (pipelines_run.log)",
    "run",
)

# ===========================================================================
# Section 3: the pipe
# ===========================================================================
mcq(
    "q06", "core", ["concept"], 3,
    """
    In `grep dining expenses.csv | wc -l`, what does the `|` do?
    """,
    [
        (
            "It sends grep's stdout to wc's stdin, so wc counts the lines that grep printed",
            True,
            "Right: the pipe connects the two programs. wc never opens `expenses.csv`; it only sees grep's output.",
        ),
        (
            "It runs grep on `expenses.csv` and then runs wc on `expenses.csv` as well",
            False,
            "wc has no file name; it reads stdin. If it counted the file it would count every line, header included (19 on the sample file), instead of just the dining lines.",
        ),
        (
            "It saves grep's output in a temporary file called `wc` and then prints that file",
            False,
            "A pipe writes no file at all; that would be `>`. `wc` is a program here, not a file name.",
        ),
        (
            "It sends grep's error messages to wc, so that problems are counted as well",
            False,
            "Only stdout goes through a pipe. Errors on stderr still go to the terminal.",
        ),
    ],
    """
    The pipe joins the stdout of the left command to the stdin of the right one: small programs, each doing one job, composed into an answer. grep picks the 5 lines that contain `dining`; wc counts the lines it receives and prints `5`. Nothing is written to disk and stderr is not part of it. This is the shape of the teacher's sample question 6.
    """,
    "S9 slide 6 ('It composes'); midterm sample Q6; S10 slide 4",
    "source",
)

mcq(
    "q07", "exam", ["read-tool-output"], 3,
    """
    ```console
    $ uv run expenses report nosuch.csv | wc -l
    could not read nosuch.csv
    0
    ```

    Why does `wc -l` print `0` although a line of text appeared on the screen?
    """,
    [
        (
            "`wc -l` only counts lines that end in a newline, and the message has none",
            False,
            "`typer.echo` ends the message with a newline. The message never reached wc in the first place.",
        ),
        (
            "The pipe broke when the program failed, so wc received an empty stream by mistake",
            False,
            "The pipe worked; there was simply nothing on stdout to carry. Nothing went wrong with the pipe itself.",
        ),
        (
            "wc started before the program had written anything, so it counted too early",
            False,
            "wc keeps reading until the left side closes its stdout. Timing does not change the count.",
        ),
        (
            "The message went to stderr, which skips the pipe; wc's stdin stayed empty",
            True,
            "Right: stderr skips the pipe. wc received nothing and counted 0 lines.",
        ),
    ],
    """
    A pipe carries stdout only. The expense-tracker writes its error to stderr (`typer.echo(..., err=True)`) and exits 1, so the message lands on the screen and wc gets an empty stdout: `0`. If you wanted the error inside the pipe, `2>&1` joins stderr to stdout first; running `uv run expenses report nosuch.csv 2>&1 | wc -l` printed `1`. Seeing an error and a count of 0 together is the signal that the first stage failed.
    """,
    "S7 slide 19; run on expense-tracker v0.4 (runs/r2.out, runs/r6.out)",
    "run",
)

# ===========================================================================
# Section 4: the text tools
# ===========================================================================
mcq(
    "q08", "exam", ["predict-output", "read-code"], 4,
    FILE_INTRO + "\n\nWhat does this command print?\n\n```bash\ngrep home expenses.csv | wc -l\n```",
    [
        (
            "`2`, the number of expenses in the home category",
            False,
            "grep does not know about columns. It matches `home` anywhere in the line.",
        ),
        (
            "`19`, the number of lines in the file",
            False,
            "wc counts what grep sends it, not the file. grep sends only matching lines.",
        ),
        (
            "`3`, the number of lines that contain `home`",
            True,
            "Right: Ikea and Leroy Merlin, plus `Sushi at home`, a dining expense whose merchant name contains the word.",
        ),
        (
            "The three lines that contain `home`",
            False,
            "Those lines go into the pipe, not to the screen. wc prints only the count.",
        ),
    ],
    """
    grep prints every line containing the text `home`, wherever it is: the two home expenses and `2025-07-06,Sushi at home,dining,24.90`. wc counts those lines: `3`. If the question is "how many home expenses?", the pipeline answers a different question. Matching the whole field fixes it: `grep ,home, expenses.csv | wc -l` prints `2` (both run). Same shape as sample Q6: it counts lines that contain the word, not expenses of that category.
    """,
    "midterm sample Q6 (variant); run on the sample file (pipelines_run.log)",
    "run",
)

mcq(
    "q09", "core", ["compare", "predict-output"], 4,
    """
    Two teammates count the dining expenses of the sample file in different ways:

    ```bash
    grep -c dining expenses.csv
    grep dining expenses.csv | wc -l
    ```

    What do the two commands print?
    """,
    [
        (
            "`5`, and then the five dining lines",
            False,
            "In the second command the lines go into the pipe; wc prints only the count.",
        ),
        (
            "`5` and `5`: both count the lines that contain `dining`",
            True,
            "Right: `grep -c` counts matching lines itself; `wc -l` counts the lines grep sent it. Same number.",
        ),
        (
            "`5` and `6`, because `wc -l` also counts the header line",
            False,
            "The header does not contain `dining`, so grep never sends it to wc.",
        ),
        (
            "The number of times `dining` appears, then the number of lines it appears on",
            False,
            "`grep -c` counts lines, not occurrences. A line with the word twice still counts once.",
        ),
    ],
    """
    Both count matching lines. `grep -c dining expenses.csv` does it inside grep; `grep dining expenses.csv | wc -l` has grep print the lines and wc count them. Running both on the sample file printed `5` twice. Neither counts occurrences of the word, and neither sees the header, because the header has no `dining` in it. Choose by habit; the pipe version is the one the sample paper uses.
    """,
    "midterm sample Q6 (variant); run on the sample file (pipelines_run.log)",
    "run",
)

mcq(
    "q10", "exam", ["read-tool-output"], 4,
    """
    The sample file has 18 expenses, 5 of them dining. You want the number of expenses that are not dining:

    ```console
    $ grep -v dining expenses.csv | wc -l
    14
    ```

    Why 14 and not 13?
    """,
    [
        (
            "The header line has no `dining` in it, so `grep -v` keeps it and `wc -l` counts it",
            True,
            "Right: `-v` keeps every line that does not match, and the header is one of them.",
        ),
        (
            "`grep -v` keeps one of the two identical Can Recasens lines, because it skips duplicates",
            False,
            "Both Can Recasens lines contain `dining`, so both are removed. grep looks at each line on its own.",
        ),
        (
            "`wc -l` always adds one extra line for the end of the file",
            False,
            "wc counts newline characters; there is no extra line. On the 5 dining lines it printed exactly `5`.",
        ),
        (
            "The `Sushi at home` line is kept, because its merchant name hides the word dining",
            False,
            "Its category field is `dining`, so the line contains the word and `-v` drops it.",
        ),
    ],
    """
    `grep -v dining` inverts the match: it prints every line that does not contain `dining`. That is 13 expenses plus the header `date,merchant,category,amount`, which matches nothing. wc counts all 14. Dropping the header first gives the intended number: `tail -n +2 expenses.csv | grep -v dining | wc -l` printed `13` when run. Any count over the whole file has to ask: is the header in there?
    """,
    "S10 slides 6–8; run on the sample file (pipelines_run.log, runs/r7.out)",
    "run",
)

mcq(
    "q12", "hard", ["read-tool-output", "judgement"], 4,
    """
    You added an expense, but `uv run expenses report` shows the same totals as before. You look for CSV files in the project:

    ```console
    $ uv run expenses add "Bar Ramon" dining 12.50 --date 2025-12-31
    added Bar Ramon (dining) 12.50 to data/expenses.csv
    $ find . -name "*.csv"
    ./expenses.csv
    ./data/expenses.csv
    ```

    What explains it?
    """,
    [
        (
            "`add` failed without a message, so the new expense was never written to any file",
            False,
            "The message says where it went and `find` shows `data/expenses.csv` exists. Nothing failed.",
        ),
        (
            "`find` lists the same file twice, once through `.` and once through `data`",
            False,
            "These are two different files: one in the project root, one inside `data/`.",
        ),
        (
            "`add` writes to `data/expenses.csv`, but `report` reads the root `expenses.csv` by default",
            True,
            "Right: that is what the README says. `uv run expenses report data/expenses.csv` reports on the new file.",
        ),
        (
            "`report` keeps old totals in `.venv`; delete `.venv` and run `uv sync` so it reads the file again",
            False,
            "The classic careless move. Nothing is cached; the report reads the file you name, every time.",
        ),
    ],
    """
    `find . -name "*.csv"` searches the whole tree under the current folder and prints every path whose name matches. Here it reveals two files, which is exactly what the README describes: `expenses.csv` at the root is sample data and is never modified; `add` writes to `data/expenses.csv`, which is not in version control. Running `uv run expenses report data/expenses.csv` showed the new expense. (The order of `find`'s lines can differ between machines.)
    """,
    "lab 09 exercise 4 (find); expense-tracker README; run on expense-tracker v0.4 (runs/f1.out)",
    "run",
)

# ===========================================================================
# Section 5: asking questions of the data
# ===========================================================================
mcq(
    "q13", "exam", ["read-tool-output"], 5,
    """
    You want the number of expenses per category in the sample file and run:

    ```console
    $ cut -d, -f3 expenses.csv | sort | uniq -c
          1 category
          5 dining
          1 education
          1 entertainment
          4 groceries
          1 health
          2 home
          3 transport
          1 utilities
    ```

    Which line is not an answer to your question, and what would fix it?
    """,
    [
        (
            "`1 utilities`: utilities is not one of the course's categories, so it should be removed",
            False,
            "utilities is a real category in the course's `expenses.csv`; Endesa is one.",
        ),
        (
            "`1 category`: it comes from the header line, so skip line 1 first, for example with `tail -n +2`",
            True,
            "Right: `cut` took the header's third field too. Starting at line 2 removes it.",
        ),
        (
            "`4 groceries`: uniq only counts neighbours, and the groceries lines are not next to each other",
            False,
            "They were sorted first, so all four groceries lines are neighbours by the time uniq sees them.",
        ),
        (
            "`3 transport`: `cut -d, -f3` took the merchant column, so these counts belong to merchants",
            False,
            "Field 3 of `date,merchant,category,amount` is the category. These are category names.",
        ),
    ],
    """
    The pipeline is right apart from one thing: the header `date,merchant,category,amount` is a line like any other, so `cut -d, -f3` prints `category` from it and `uniq -c` counts it once. Starting from line 2 gives the clean answer: `tail -n +2 expenses.csv | cut -d, -f3 | sort | uniq -c` lists the eight real categories (run in the module's pipeline "Expenses per category"). The sort is what makes the counts right, because uniq counts only neighbouring lines.
    """,
    "S10 slides 6–8; run on the sample file (pipelines_run.log)",
    "run",
)

mcq(
    "q14", "exam", ["read-tool-output"], 5,
    """
    The sample file contains amounts of 250.83 and 137.97. You want the three largest amounts:

    ```console
    $ cut -d, -f4 expenses.csv | sort -r | head -n 3
    amount
    91.60
    9.80
    ```

    What went wrong?
    """,
    [
        (
            "sort compared the lines as text, and the header word is still in the list",
            True,
            "Right: as text `9` beats `2` and `1`, and the letter `a` beats any digit. Two bugs: text sort and header.",
        ),
        (
            "`head -n 3` takes its lines from the bottom of the input, so it showed the smallest",
            False,
            "head takes the first lines. The order was wrong before head ever saw it.",
        ),
        (
            "`cut -d, -f4` took the merchant column, so these are not amounts at all",
            False,
            "Field 4 is the amount; `91.60` and `9.80` are amounts from the file.",
        ),
        (
            "`sort -r` removes repeated values, so the largest amounts were dropped",
            False,
            "sort never removes lines; removing repeats is uniq's job. Every amount is still there, in text order.",
        ),
    ],
    """
    Without `-n`, sort compares text one character at a time, so `91.60` and `9.80` beat `250.83` because `9` comes after `2`. The header word `amount` is still in the stream, and letters come after digits, so in reverse it comes first. Dropping the header and sorting numerically gives `250.83`, `137.97`, `91.60`: `tail -n +2 expenses.csv | cut -d, -f4 | sort -rn | head -n 3` (run). (The order shown is that of WSL's default settings; lines that differ only by punctuation, such as `91.60` and `9.80`, can swap places on a machine with other language settings.)
    """,
    "S10 slides 6–8; run on the sample file (pipelines_run.log)",
    "run",
)

mcq(
    "q15", "hard", ["read-tool-output", "judgement"], 5,
    """
    On the real `expenses.csv` of the expense-tracker:

    ```console
    $ wc -l expenses.csv
    421 expenses.csv
    $ uniq -d expenses.csv | wc -l
    5
    $ sort expenses.csv | uniq -d | wc -l
    6
    ```

    Session 8 says the file has six exact duplicate rows. Why does the first pipeline find only five?
    """,
    [
        (
            "One of the six is the header line, which sort moves to the end of the file",
            False,
            "The header appears once, so it can never be a repeated line. Sorting moves it but cannot make it a duplicate.",
        ),
        (
            "`uniq -d` without sort picks a random sample of the duplicates on each run",
            False,
            "uniq is deterministic: same input, same output. It misses one pair every time, for a reason.",
        ),
        (
            "uniq only compares neighbouring lines, and one duplicate pair is not adjacent",
            True,
            "Right: the two `2025-11-29,Condis,groceries,93.02` rows are lines 351 and 354, with other rows between them.",
        ),
        (
            "Six counts both copies of three rows, so five is the true number of extra rows",
            False,
            "`uniq -d` prints one line per duplicated row; six lines means six rows that appear twice, as session 8 says.",
        ),
    ],
    """
    uniq looks at neighbours only. Five of the real duplicate pairs sit on consecutive lines, so plain `uniq -d` sees them. The sixth pair, `2025-11-29,Condis,groceries,93.02`, sits at lines 351 and 354 with two other Condis rows between them (checked with `grep -n`). Sorting puts identical lines next to each other, so `sort | uniq -d` finds all six, matching session 8: 420 expenses, 414 after `remove_duplicates`. Hence the habit: `sort | uniq`.
    """,
    "S8 slides 11, 13 and 16; run on expense-tracker expenses.csv (runs/r5.out)",
    "run",
)

mcq(
    "q16", "hard", ["predict-output"], 5,
    """
    The real `expenses.csv` has 421 lines: a header and 420 expenses, six of which are exact copies of another row.

    ```console
    $ sort expenses.csv | uniq -d | wc -l
    6
    $ sort expenses.csv | uniq | wc -l
    ```

    What does the last command print?
    """,
    [
        (
            "`414`",
            False,
            "414 is the number of unique expenses, but the header is in the stream too and survives uniq.",
        ),
        (
            "`421`",
            False,
            "uniq does collapse the six duplicated rows once they are adjacent, so the count drops.",
        ),
        (
            "`408`",
            False,
            "uniq keeps one copy of each repeated line; it does not drop both copies (420 minus 12).",
        ),
        (
            "`415`",
            True,
            "Right: 414 unique expenses plus the header line.",
        ),
    ],
    """
    After sorting, each duplicated row sits next to its copy, and `uniq` keeps one of each: 421 lines minus 6 extra copies is 415. The 415 includes the header line `date,merchant,category,amount`, which is unique. Without the header the count is 414, the same number session 8 gets from `len(remove_duplicates(read_expenses("expenses.csv")))`. Both numbers were checked by running `sort expenses.csv | uniq | wc -l` and `tail -n +2 expenses.csv | sort | uniq | wc -l`.
    """,
    "S8 slide 16 (420 and 414); run on expense-tracker expenses.csv (runs/r5.out)",
    "run",
)

mcq(
    "q17", "exam", ["predict-output"], 5,
    FILE_INTRO
    + "\n\nWhat does this pipeline print?\n\n```bash\ngrep dining expenses.csv | cut -d, -f2 | sort | uniq\n```",
    [
        (
            "`Can Recasens`, `Sushi at home`, `Bar Ramon`, `Federal Cafe` (one per line)",
            False,
            "That is the file's order: what you get without the `sort` stage.",
        ),
        (
            "`Bar Ramon`, `Can Recasens`, `Federal Cafe`, `Sushi at home` (one per line)",
            True,
            "Right: the five dining merchants, sorted, with the repeated Can Recasens collapsed into one line.",
        ),
        (
            "`Bar Ramon`, `Can Recasens`, `Can Recasens`, `Federal Cafe`, `Sushi at home` (one per line)",
            False,
            "That is the output before `uniq`. uniq collapses the two neighbouring Can Recasens lines.",
        ),
        (
            "`1 Bar Ramon`, `2 Can Recasens`, `1 Federal Cafe`, `1 Sushi at home` (one per line)",
            False,
            "Counts appear only with `uniq -c`. Plain uniq prints each line once, without a number.",
        ),
    ],
    """
    Stage by stage: grep keeps the 5 dining lines; `cut -d, -f2` keeps the merchant field (`Can Recasens` twice, `Sushi at home`, `Bar Ramon`, `Federal Cafe`); sort puts them in text order; uniq collapses the two neighbouring `Can Recasens` into one. Result, as run: `Bar Ramon`, `Can Recasens`, `Federal Cafe`, `Sushi at home`. The pipeline answers "at which places did I eat out?", one name each.
    """,
    "S10 slides 6–8; run on the sample file (pipelines_run.log)",
    "run",
)

mcq(
    "q18", "hard", ["compare", "judgement"], 5,
    """
    Which pipeline correctly answers "how many expenses are there in each category?" for `expenses.csv` (header `date,merchant,category,amount`)?

    (`tail -n +2` prints a file from line 2 on, `uniq -c` puts a count in front of each group of equal neighbouring lines, and `uniq -d` prints only the lines that repeat.)
    """,
    [
        (
            "`cut -d, -f3 expenses.csv | sort | uniq -c`",
            False,
            "One stage short: the header's `category` is counted as a category with 1 expense. Skip line 1 first.",
        ),
        (
            "`tail -n +2 expenses.csv | cut -d, -f3 | sort | uniq -d`",
            False,
            "`uniq -d` prints each repeated category once, with no count, and leaves out categories that appear once (run: dining, groceries, home, transport).",
        ),
        (
            "`tail -n +2 expenses.csv | cut -d, -f3 | uniq -c`",
            False,
            "No sort: uniq counts runs of neighbouring lines, so dining appears four times with counts 2, 1, 1, 1 (run).",
        ),
        (
            "`tail -n +2 expenses.csv | cut -d, -f3 | sort | uniq -c`",
            True,
            "Right: skip the header, keep the category, sort so equal names are neighbours, count each group.",
        ),
    ],
    """
    Counting per category needs four moves: drop the header, keep the category field, bring equal values together, count them. Each wrong option drops or changes one move. Without `tail -n +2`, a line `1 category` appears. Without `sort`, dining shows up four times with counts 2, 1, 1, 1. With `uniq -d` you get the repeated names and no counts. All three were run on the sample file. Read each option stage by stage and ask what text reaches the next `|`.
    """,
    "S10 slides 6–8; run on the sample file (pipelines_run.log; pipes-bash-fix/runs/q18_options.out)",
    "run",
)

# ===========================================================================
# Section 6: exit codes and chaining
# ===========================================================================
mcq(
    "q19", "core", ["read-tool-output", "concept"], 6,
    """
    ```console
    $ grep clothing expenses.csv
    $ echo $?
    1
    ```

    What does the `1` tell you?
    """,
    [
        (
            "grep ran correctly and found no line containing `clothing`",
            True,
            "Right: grep exits 0 when it finds something, 1 when it finds nothing, 2 when something went wrong.",
        ),
        (
            "grep found exactly one line containing `clothing` and printed nothing else",
            False,
            "A match would be printed on the screen. `$?` is an exit code, not a count.",
        ),
        (
            "grep crashed while reading `expenses.csv`, so the file may be damaged",
            False,
            "A real problem gives exit code 2 and a message on stderr. Here there is no message at all.",
        ),
        (
            "`expenses.csv` does not exist in the current folder, so grep had nothing to read",
            False,
            "A missing file prints `grep: expenses.csv: No such file or directory` and exits 2.",
        ),
    ],
    """
    Session 5: "0 means success; anything else means failure", and `echo $?` shows the last command's exit code. grep uses three values: 0 found, 1 found nothing, 2 trouble (run: `grep dining nosuch.csv` printed `grep: nosuch.csv: No such file or directory` and `2`). "No match" is a normal answer for a human, but to the shell 1 is not 0, so `&&`, `set -e` and CI treat it as a failure. That matters in scripts.
    """,
    "S5 slide 9; run on the sample file (runs/r4.out)",
    "run",
)

mcq(
    "q20", "exam", ["read-code", "read-tool-output", "judgement"], 6,
    f"""
    A teammate writes this check script:

    ```bash
    #!/usr/bin/env bash
    uv run ruff check . ; uv run ruff format --check . ; uv run mypy src tests ; uv run pytest -q
    ```

    With an unused import in `report.py`, it prints (trimmed):

    ```console
    $ ./scripts/check-semicolons.sh
    F401 [*] `os` imported but unused
     --> src/expense_tracker/report.py:2:8
    ...
    Found 1 error.
    [*] 1 fixable with the `--fix` option.
    7 files already formatted
    Success: no issues found in 6 source files
    ........................                                                 [100%]
    24 passed in 0.04s
    $ echo $?
    0
    ```

    What is the problem with this script?
    """,
    [
        (
            "Nothing: every check ran, and the ruff error is on the screen for anyone who reads it",
            False,
            "CI and `&&` do not read the screen; they read the exit code, and it says success.",
        ),
        (
            "`;` runs every command regardless, so the script exits with pytest's 0",
            True,
            "Right: pytest passed, so the script exits 0. A check that prints an error and exits 0 lies.",
        ),
        (
            "ruff should be the last command, because a script's exit code comes from its first command",
            False,
            "It is the other way round: the exit code is the last command's. Moving ruff last only hides a different failure.",
        ),
        (
            "ruff's error is only a style warning, so it does not count as a failure",
            False,
            "ruff exits 1 whenever it reports a problem, F401 included: the `set -e` version of the same script stopped right after it with exit code 1. The 0 here is pytest's, because it ran last.",
        ),
    ],
    """
    With `;`, bash runs the next command whatever happened before. All four checks ran, and the script ended with pytest's exit code: 0. Anything that trusts the exit code (a `&&` after it, CI, your own habit of glancing at the last line) sees green while ruff found an error. Session 5: "A program that prints an error and exits 0 is a program that lies." The rubric's chain uses `&&`; a script can use `set -e` instead. Both stop at the first failure and exit non-zero.
    """,
    "S5 slide 9; partial rubric 'Check yourself'; run on a copy of expense-tracker v0.4 (runs/c1.out; pipes-bash-fix/runs/lint.out)",
    "run",
)

mcq(
    "q21", "core", ["predict-output"], 6,
    """
    What appears on the screen?

    ```bash
    uv run expenses report nosuch.csv && echo "report ok" || echo "report failed"
    ```
    """,
    [
        (
            "Only `could not read nosuch.csv`",
            False,
            "`||` runs its right side when what came before failed, so a second line follows.",
        ),
        (
            "`report ok`",
            False,
            "`&&` runs `echo \"report ok\"` only if the report exited 0. It exited 1.",
        ),
        (
            "`could not read nosuch.csv`, then `report ok`, then `report failed`",
            False,
            "`&&` and `||` are conditions, not separators. At most one of the two messages runs here.",
        ),
        (
            "`could not read nosuch.csv`, then `report failed`",
            True,
            "Right: the report fails (exit 1), `&&` skips `report ok`, and `||` runs `report failed`.",
        ),
    ],
    """
    `a && b` runs b only if a exited 0; `a || b` runs b only if what came before exited non-zero. The report prints its message on stderr and exits 1, so `echo "report ok"` is skipped and the `||` branch runs. Run for real, the output was exactly `could not read nosuch.csv` followed by `report failed`. With a file that exists, the same line prints the report and `report ok`.
    """,
    "S5 slide 9; run on expense-tracker v0.4 (runs/r2.out)",
    "run",
)

mcq(
    "q22", "hard", ["read-tool-output", "concept"], 6,
    """
    ```console
    $ grep clothing expenses.csv | wc -l
    0
    $ echo $?
    0
    $ set -o pipefail
    $ grep clothing expenses.csv | wc -l
    0
    $ echo $?
    1
    ```

    Which explanation fits both exit codes?
    """,
    [
        (
            "The first time grep found no clothing lines; the second time it found one and printed it",
            False,
            "Both runs print 0 lines. Same input, same grep result; only the shell setting changed.",
        ),
        (
            "`set -o pipefail` makes wc exit 1 whenever it has counted zero lines",
            False,
            "wc succeeds after counting zero lines. pipefail does not change any program, only how the shell scores the pipeline.",
        ),
        (
            "pipefail turns the `0` that wc printed into an exit code of 1",
            False,
            "That confuses output with exit code. The `0` on the screen is text; the exit code is separate.",
        ),
        (
            "Without pipefail wc's 0 decides; with it, grep's 1 fails the whole pipeline",
            True,
            "Right: grep found nothing (1), wc counted fine (0). pipefail reports the failure instead of hiding it.",
        ),
    ],
    """
    By default bash scores a pipeline by its last command. wc counted zero lines and exited 0, so the whole pipeline looked successful even though grep exited 1. `set -o pipefail` makes the pipeline fail when any stage fails, so the same command now exits 1. In a script with `set -e`, that difference decides whether the script stops: without pipefail it carries on, with pipefail it stops (both run). Whether you want that for a grep that may find nothing is a judgement call.
    """,
    "S10 slide 16; run on the sample file (runs/r4.out, runs/s2.out)",
    "run",
)

# ===========================================================================
# Section 7: bash scripts
# ===========================================================================
mcq(
    "q23", "core", ["concept", "compare"], 7,
    """
    In session 3 you ran `bash scripts/setup-check.sh`. The class script is run as `./scripts/check.sh`. Why does the second form need `chmod +x` and the first one does not?
    """,
    [
        (
            "`./` starts the script in the background, and background programs need extra permission",
            False,
            "`./` means \"the file in this folder\"; nothing runs in the background.",
        ),
        (
            "`bash` runs every script as the administrator, so file permissions do not apply to it",
            False,
            "bash runs as you, with your permissions. It needs to read the file, and you can.",
        ),
        (
            "With `bash file`, bash reads the file; `./file` asks the system to run it as a program",
            True,
            "Right: session 9, \"No x, no run\". Reading a file needs r; running it as a program needs x.",
        ),
        (
            "The `.sh` ending is understood by `bash` but not by `./`, so `./` needs the x bit to recognise it",
            False,
            "File endings mean nothing to the system here; the x bit and the shebang line decide.",
        ),
    ],
    """
    `bash scripts/setup-check.sh` starts the bash program and gives it the file as something to read; reading needs only the r bit. `./scripts/check.sh` asks the operating system to execute the file, which requires the x bit and then uses the shebang `#!/usr/bin/env bash` to choose the interpreter. Session 9: "A new file never gets execution permissions" and "chmod +x is a statement that a file is a program".
    """,
    "S3 slide 9; S9 slides 18–19 and 24",
    "source",
)

mcq(
    "q24", "exam", ["read-code", "read-tool-output"], 7,
    parts(
        "Your course folder is called `Moodle Files`. A teammate's script and its run:",
        fence("bash", COUNT_SH_UNQUOTED),
        """
        ```console
        $ ./count.sh "Moodle Files/expenses.csv"
        Dining expenses in Moodle Files/expenses.csv:
        grep: Moodle: No such file or directory
        grep: Files/expenses.csv: No such file or directory
        0
        ```
        """,
        "Which change fixes it?",
    ),
    [
        (
            "Write `\"$file\"` with double quotes on the grep line, so the path reaches grep as one word",
            True,
            "Right: unquoted, bash splits the value at the space and grep gets two names that do not exist.",
        ),
        (
            "Rename the folder to `Moodle_Files`, because bash cannot handle spaces in paths",
            False,
            "It works around this one folder and leaves the script broken for the next path with a space. bash handles spaces when the variable is quoted.",
        ),
        (
            "Run `chmod +x count.sh` again, because the script cannot read the file",
            False,
            "The script ran (it printed its first line). The x bit has nothing to do with how grep sees its arguments.",
        ),
        (
            "Add `set -u` at the top, so that the variable is properly set",
            False,
            "`file` is set; its value is right. `set -u` catches unset variables, not unquoted ones.",
        ),
    ],
    """
    `$file` holds `Moodle Files/expenses.csv`. Unquoted, bash splits it at the space, so grep receives two arguments, `Moodle` and `Files/expenses.csv`, and complains about both. The `echo` line works because its `$file` is inside double quotes. With `grep dining "$file"` the run printed `5`. Rule: always quote `"$var"`, because paths have spaces. Notice also that the broken script printed `0` and exited 0: the pipeline's exit code is wc's.
    """,
    "S10 slides 12, 14; run (runs/s1.out)",
    "run",
)

mcq(
    "q25", "beyond", ["read-code", "read-tool-output"], 7,
    """
    Bash treats `CATEGORY = dining` as the command `CATEGORY` with two arguments.

    ```bash
    #!/usr/bin/env bash
    CATEGORY = dining
    grep -c "$CATEGORY" expenses.csv
    ```

    ```console
    $ ./by-category.sh
    ./by-category.sh: line 2: CATEGORY: command not found
    19
    ```

    On the sample file (19 lines, 5 of them dining), why does it print 19 and not 5?
    """,
    [
        (
            "The variable was never set, so grep got an empty pattern, which matches every line",
            True,
            "Right: with spaces, bash ran a command called `CATEGORY` instead of assigning, so `$CATEGORY` stayed empty, and an empty pattern matches all 19 lines. `CATEGORY=dining` prints `5`.",
        ),
        (
            "grep counted every occurrence of the word dining in the whole file, not lines",
            False,
            "`grep -c` counts lines, and there are only 5 dining lines. 19 is the number of lines in the file.",
        ),
        (
            "`CATEGORY` is a reserved word in bash, so grep used the header as its pattern instead",
            False,
            "It is not reserved. bash treated it as the name of a program to run, which does not exist.",
        ),
        (
            "The error stopped the script at line 2, and 19 is the line number where bash gave up",
            False,
            "Without `set -e` the script carries on after an error. 19 is grep's output on line 3.",
        ),
    ],
    """
    In bash, `NAME=value` has no spaces. `CATEGORY = dining` is read as "run the program `CATEGORY` with arguments `=` and `dining`", hence `command not found`. The script does not stop (no `set -e`), and `$CATEGORY` is still unset, so `"$CATEGORY"` is an empty string. An empty pattern matches every line, so `grep -c` prints 19. The fixed line `CATEGORY=dining` printed `5` (run). A wrong number with exit code 0 is worse than a crash.
    """,
    "S10 slides 12, 14; run (runs/s1.out)",
    "run",
)

mcq(
    "q26", "hard", ["read-code", "read-tool-output"], 7,
    parts(
        fence("bash", MONTHLY_SH),
        """
        ```console
        $ ./monthly.sh expenses.csv
        Report for expenses.csv
        $ echo $?
        1
        ```
        """,
        "The sample file has no clothing expenses. Why does the script stop without printing the two totals?",
    ),
    [
        (
            "`set -u` stopped it, because the variable `clothing` was used before it had a value",
            False,
            "`clothing` is being assigned on that line, not read. `set -u` only fires when an unset variable is read.",
        ),
        (
            "`$( )` is not allowed in a script that uses `set -e`, so bash stopped at the first one",
            False,
            "The first `$( )` (dining) worked. Command substitution is fine with `set -e`.",
        ),
        (
            "grep crashed while reading the file the second time, and `set -e` stopped the script",
            False,
            "grep did not crash; a crash would print a message and exit 2. It just found nothing.",
        ),
        (
            "`grep -c clothing` found nothing and exited 1, and `set -e` stops at any non-zero exit",
            True,
            "Right: no match is exit code 1, and for `set -e` that is a failure. The script stops silently.",
        ),
    ],
    """
    `set -e` stops the script at the first command that exits non-zero. `grep -c clothing` prints `0` (captured into the variable) and exits 1, because "found nothing" is grep's exit code 1. The assignment takes that exit code, so the script ends there, before either `echo`, with no error message at all. Without `set -e` the same script printed `dining: 5` and `clothing: 0` (run). Keep `set -e` and mark this one grep as allowed to find nothing, for example with `|| true` after it.
    """,
    "S10 slides 6–8, 16; run (runs/s1.out, runs/s2.out)",
    "run",
)

mcq(
    "q27", "beyond", ["compare", "read-tool-output"], 7,
    """
    `by-category.sh` is:

    ```bash
    #!/usr/bin/env bash
    CATEGORY = dining
    grep -c "$CATEGORY" expenses.csv
    ```

    `by-category-u.sh` is the same script with `set -u` added as line 2. On the sample file (19 lines, 5 of them dining):

    ```console
    $ ./by-category.sh
    ./by-category.sh: line 2: CATEGORY: command not found
    19
    $ echo $?
    0
    $ ./by-category-u.sh
    ./by-category-u.sh: line 3: CATEGORY: command not found
    ./by-category-u.sh: line 4: CATEGORY: unbound variable
    $ echo $?
    1
    ```

    What did `set -u` change?
    """,
    [
        (
            "It fixed the spaces around `=`, so `CATEGORY` is now set correctly",
            False,
            "The same `command not found` appears in both runs; the assignment is still broken.",
        ),
        (
            "It sent the wrong count to stderr instead of stdout, so it no longer shows",
            False,
            "`set -u` does not move output. The count is gone because grep never ran.",
        ),
        (
            "Reading the unset variable became an error, so the script stops with exit 1",
            True,
            "Right: a loud failure (exit 1) instead of a silent wrong answer (19, exit 0).",
        ),
        (
            "Nothing that matters: both scripts failed, and the exit code is only for display",
            False,
            "The exit code is exactly what `&&`, `set -e` and CI read. Exit 0 with a wrong number would pass a check.",
        ),
    ],
    """
    Without `set -u`, an unset variable quietly becomes an empty string; here that turned `grep -c "$CATEGORY"` into "count every line" and the script exited 0 with a wrong answer. With `set -u`, reading `$CATEGORY` is an error: bash prints `CATEGORY: unbound variable`, stops, and exits 1. It does not fix the typo; it makes the typo impossible to miss. This is session 7's "fail loudly" applied to scripts.
    """,
    "S7 slides 17–19 (fail loudly); S10 slide 16; run (runs/s1.out; pipes-bash-fix/runs/scripts.out)",
    "run",
)

mcq(
    "q28", "beyond", ["read-code", "predict-output"], 7,
    """
    ```bash
    #!/usr/bin/env bash
    set -euo pipefail
    grep -c dining "$@"
    ```

    ```console
    $ ./count-all.sh expenses.csv "Moodle Files/expenses.csv"
    expenses.csv:5
    Moodle Files/expenses.csv:5
    ```

    A teammate replaces `"$@"` with `"$1"`. What does the same command print then?
    """,
    [
        (
            "The same two lines, because `\"$1\"` and `\"$@\"` both mean all the arguments",
            False,
            "`$1` is only the first argument; `$@` is all of them.",
        ),
        (
            "Two error messages, because the path `Moodle Files` is split into two words",
            False,
            "`\"$1\"` is quoted, and the first argument is `expenses.csv` anyway. Nothing is split.",
        ),
        (
            "`10`, the total number of dining lines over both files",
            False,
            "grep never adds counts across files; and with `$1` it sees only one file.",
        ),
        (
            "`5`: only the first argument reaches grep",
            True,
            "Right: grep gets one file, so it prints the count without a file name.",
        ),
    ],
    """
    `"$1"` is the first argument; `"$@"` stands for all of them, each kept as one word even if it contains a space. With two files grep prints one count per file, prefixed by its name. With `"$1"` grep sees only `expenses.csv` and prints a bare `5` (run). The second argument is ignored silently, which is why scripts that take several files use `"$@"`.
    """,
    "extension of S10 slide 12 (the slides use \"$1\" only, not \"$@\"); run (runs/s1.out)",
    "run",
)

# ===========================================================================
# Section 8: check.sh and CI
# ===========================================================================
mcq(
    "q29", "core", ["concept", "judgement"], 8,
    """
    The partial rubric's "Check yourself" gives one long command to run before `git tag -a v0.5`. Why run it on your own machine first?
    """,
    [
        (
            "Because the marker runs this command on your laptop instead of looking at CI",
            False,
            "The marker looks at the Actions tab and at your repository at the tag. Your laptop is never involved.",
        ),
        (
            "Because CI only runs on tagged commits, so this is the only check before the tag",
            False,
            "The check workflow runs on every push (`on: push`), tagged or not.",
        ),
        (
            "It runs the same checks as CI, so you catch a red check before you tag",
            True,
            "Right: CI must be green on the tagged commit; a red tag caps the Tests criterion at 1.",
        ),
        (
            "It fixes formatting and lint problems automatically, so the tagged commit is clean",
            False,
            "`ruff format --check` and `ruff check` only report; they change nothing. You fix and commit.",
        ),
    ],
    """
    The rubric: "CI must be green on the tagged commit, or tests is capped at 1", and "A fix pushed after the tag does not count". The command chains `ruff check`, `ruff format --check`, `mypy src tests` and `pytest`, the same commands as the last four steps of `check.yml` (lab 01: "If they pass here, they pass there"). Session 10 turned it into `scripts/check.sh`, written together in class: one command, four named checks, to run before tagging.
    """,
    "partial-rubric.txt; lab 01 §8; S9 slide 3; S10 slide 17",
    "source",
)

mcq(
    "q30", "exam", ["read-tool-output", "judgement"], 8,
    parts(
        "`scripts/check.sh`:",
        fence("bash", CHECK_SH),
        "You run it after adding a line to `report.py`:",
        fence("console", "$ ./scripts/check.sh\n==> ruff check\n" + RUFF_F401 + "\n$ echo $?\n1"),
        "Nothing appeared after ruff's report. What should you conclude?",
    ),
    [
        (
            "The other three checks passed without output, so only the unused import needs fixing",
            False,
            "They did not pass; they did not run. Each prints a line when it passes (`9 files already formatted`, `Success: ...`, a pytest summary).",
        ),
        (
            "The other three never ran: `set -e` stopped the script when ruff exited 1",
            True,
            "Right: the first non-zero exit ends the script, so you know nothing yet about formatting, types or tests. Fix the import, then run the whole script again.",
        ),
        (
            "The script is badly written: a check script should always run all four tools to the end",
            False,
            "Stopping at the first red check is the design, the same as the rubric's `&&` chain.",
        ),
        (
            "The `--fix` hint means the script will remove the import by itself on the next run",
            False,
            "The script runs `ruff check .` without `--fix`, so it only reports. Fixing is your job.",
        ),
    ],
    """
    `set -e` stops a script at the first command that exits non-zero. ruff found an unused import and exited 1, so the script ended there and returned 1; the format check, mypy and pytest were never started. That is the same behaviour as the rubric's `&&` chain and the same as CI, where a red step skips the rest. The right move: remove the import (or let `ruff check --fix` do it), then run `./scripts/check.sh` again until all four pass.
    """,
    "S10 slides 17–18; partial rubric; run on expense-tracker v0.5 (runs/check_lint.out)",
    "run",
)

mcq(
    "q31", "exam", ["read-tool-output", "judgement"], 8,
    """
    A teammate who works under `/mnt/c` on WSL committed `scripts/check.sh`. In a fresh clone in your Linux home:

    ```console
    $ ./scripts/check.sh
    bash: ./scripts/check.sh: Permission denied
    $ git ls-files -s scripts/check.sh
    100644 751c44e5d6d89ae197300a111cf218cf8338e17a 0	scripts/check.sh
    ```

    What is the right fix?
    """,
    [
        (
            "`chmod 777 scripts/check.sh`, so that everybody can run it, then carry on working",
            False,
            "Session 9: 777 \"makes the error go away and the problem worse\", and an uncommitted chmod helps only your clone.",
        ),
        (
            "Tell the group, and CI, to run it as `sudo ./scripts/check.sh` from now on",
            False,
            "sudo gives administrator rights; it does not make a file a program. It is never the fix for a missing x bit.",
        ),
        (
            "Delete the `#!/usr/bin/env bash` line, which is what the error is complaining about",
            False,
            "The error is about permissions, not the first line: `Permission denied` means the x bit is missing, and deleting the shebang does not add it.",
        ),
        (
            "`chmod +x scripts/check.sh` in your clone, then commit and push the mode change",
            True,
            "Right: the x bit is part of what git stores (100644 vs 100755), so once the change is committed every clone and CI get it.",
        ),
    ],
    """
    `100644` is git's record of a normal file without the x bit, so every clone gets the file with no x anywhere (`-rw-rw-r--` on session 9's Ubuntu slides) and `./scripts/check.sh` says `Permission denied`. Under `/mnt/c`, session 9 warns, "chmod silently does nothing", which is one way a script ends up committed without the x bit. In a Linux home folder, `chmod +x` changes the mode, `git diff` shows `old mode 100644` / `new mode 100755`, and after the commit `git ls-files -s` shows `100755` (run). Session 9: "In CI it needs the x bit too, and git remembers it."
    """,
    "S9 slides 18–21; run in a scratch git repo and a fresh clone of it (runs/perm2.out, runs/g1.out)",
    "run",
)

mcq(
    "q32", "beyond", ["read-diff"], 8,
    """
    A commit called `Make check.sh executable` contains only this (`100644` and `100755` are git's file modes: the permissions `rw-r--r--` and `rwxr-xr-x`):

    ```diff
    diff --git a/scripts/check.sh b/scripts/check.sh
    old mode 100644
    new mode 100755
    ```

    What does the commit change?
    """,
    [
        (
            "It changes only the permissions: the script is now executable in every clone",
            True,
            "Right: no `+` or `-` lines, so no text changed. 100755 is rwxr-xr-x.",
        ),
        (
            "Nothing at all: git ignores permissions, so this is an empty commit",
            False,
            "git stores the executable bit; this diff is git reporting exactly that change.",
        ),
        (
            "It replaces the file with a new version whose lines git chose not to display",
            False,
            "git always shows changed lines in a diff. There are none, so the text is unchanged.",
        ),
        (
            "It gives every user on the machine permission to edit and run the script",
            False,
            "755 is rwxr-xr-x: everyone may run it, but only the owner can write (edit) it. The change adds x, never w.",
        ),
    ],
    """
    git records two things per file: its content and whether it is executable (mode 100644 or 100755). This diff has no `+` or `-` lines, only a mode change, so the content is the same and the file is now a program for everyone who clones the repository, CI included. Running it for real, `git show --stat` listed `scripts/check.sh | 0` and `0 insertions(+), 0 deletions(-)`. Session 9: 755 is "a script or a folder".
    """,
    "S9 slides 20–21; run in a scratch git repo (runs/g1.out)",
    "run",
)

mcq(
    "q33", "exam", ["read-code", "read-tool-output"], 8,
    parts(
        "The steps of `.github/workflows/check.yml`:",
        fence("yaml", CHECK_YML_STEPS),
        "On GitHub the run is red, and the log of the Lint step ends with:",
        fence("text", "Found 1 error.\n[*] 1 fixable with the `--fix` option."),
        "Which steps ran on GitHub's machine?",
    ),
    [
        (
            "All seven ran, and only Lint is red; Formatting, Types and Tests are green",
            False,
            "After a failed step, the following steps do not run by default; GitHub marks them as skipped.",
        ),
        (
            "Only Lint ran, because each step runs on its own machine and stops on its own",
            False,
            "All steps of a job run one after another on the same machine; that is why Lint can use what `uv sync` installed.",
        ),
        (
            "Check out, Install uv, Install dependencies and Lint ran; the last three were skipped",
            True,
            "Right: like `&&`, the job stops at the first command that exits non-zero.",
        ),
        (
            "Every step except Lint ran, because GitHub skips a step that reports errors",
            False,
            "Lint did run: its log contains ruff's output. It is the steps after it that were skipped.",
        ),
    ],
    """
    Session 9: "CI is a terminal. The check workflow is a list of commands someone else's computer types for you." The steps run in order on one fresh Ubuntu machine. `uv run ruff check .` exited 1, the step turned red, and by default the remaining steps are skipped, so you do not know yet whether formatting, types and tests pass. Reproduce it locally with `./scripts/check.sh` (or the rubric's command), fix, push, and wait for green.
    """,
    "S9 slide 6; expense-tracker .github/workflows/check.yml; partial rubric 'If CI is red on the tag'; ruff output run (runs/c1.out)",
    "run",
)

mcq(
    "q34", "beyond", ["read-tool-output", "judgement"], 8,
    """
    For v0.5 you change `version = "0.1.0"` to `version = "0.5.0"` in `pyproject.toml`, run `./scripts/check.sh` (all green), commit `pyproject.toml` and push. CI fails at "Install dependencies from the lockfile":

    ```text
    error: The lockfile at `uv.lock` needs to be updated, but `--locked` was provided.

    hint: To update the lockfile, run `uv lock`.
    ```

    Back on your laptop:

    ```console
    $ git status --short
     M uv.lock
    ```

    Why did `check.sh` not catch this?
    """,
    [
        (
            "check.sh runs ruff before mypy, so the lockfile is checked too late to matter",
            False,
            "None of the four checks fails on a stale lockfile, whatever the order: `uv run` just rewrites `uv.lock` to match.",
        ),
        (
            "check.sh never runs `uv sync --locked`, and the updated `uv.lock` was not committed",
            True,
            "Right: locally `uv run` quietly updated `uv.lock`, and `git status` shows it modified. Commit it and CI's `--locked` check passes.",
        ),
        (
            "CI uses a newer Python than your laptop, and a new Python needs a new lockfile",
            False,
            "The message only says the lockfile needs updating, and `git status` shows your local `uv.lock` changed; nothing in it mentions a Python version.",
        ),
        (
            "The lockfile is corrupted; delete `uv.lock` and push the project without it",
            False,
            "CI runs `uv sync --locked`, which needs a lockfile. The fix is to commit the updated one.",
        ),
    ],
    """
    CI runs one step that `check.sh` does not: `uv sync --locked`, which refuses a lockfile that disagrees with `pyproject.toml` (sessions 4 and 5). Locally, `uv run` re-locked silently when the version changed: running it for real, `uv.lock` went from `version = "0.1.0"` to `"0.5.0"`, and `git status` listed it as modified. Committing only `pyproject.toml` left CI with the old lock. Fix: commit `uv.lock` too. A check script is only as good as the steps it shares with CI.
    """,
    "S4/S5 (uv sync --locked); lab 01 troubleshooting; run in a copy of the sandbox and a fresh clone of it (runs/l2.out, runs/l3.out, runs/l4.out)",
    "run",
)

# ===========================================================================
# Open questions
# ===========================================================================
openq(
    "q35", "exam", ["read-tool-output", "concept"], 2,
    """
    A teammate keeps the monthly report in a file:

    ```console
    $ uv run expenses report > report.txt
    $ echo $?
    0
    $ head -n 3 report.txt
    Expense report for expenses.csv
    ----------------------------------------
    groceries              6401.78
    $ uv run expenses report nosuch.csv > report.txt
    could not read nosuch.csv
    $ echo $?
    1
    $ wc -l < report.txt
    0
    ```
    """,
    [
        {
            "label": "1",
            "prompt": "The second command redirects its output to `report.txt`. Explain why `could not read nosuch.csv` appeared on the screen.",
            "marks": 2,
            "model": "The program writes the report to stdout but its error to stderr (`typer.echo(..., err=True)`). `>` redirects only stdout, so the message still went to the terminal.",
            "rubric": [
                "Says the message is written to stderr (or `err=True`), not stdout",
                "Says `>` redirects only stdout, so stderr still reaches the terminal",
            ],
            "weak": "\"Because the command failed\" explains nothing about where the text went. Saying \"the shell printed the error\" is wrong: the program wrote it. Full marks need both halves: which stream the message used, and which stream `>` moves.",
        },
        {
            "label": "2",
            "prompt": "Why is `report.txt` now empty, and what would have kept the first report?",
            "marks": 2,
            "model": "For `>` the shell empties the file before the program starts; the program then failed and wrote nothing to stdout, and the old content does not come back. Writing to a new file name (or appending with `>>`) would have kept the old report.",
            "rubric": [
                "Says `>` empties (truncates) the file before the command runs, whatever the command then does",
                "Names a way to keep it: a different file name, or `>>` to append",
            ],
            "weak": "Many answers say the error message overwrote the file: it did not, the message went to the screen and the file has 0 lines. Others say the program deleted the file. The point is the order: the shell prepares `>` first, so a failing command still costs you the file.",
        },
        {
            "label": "3",
            "prompt": "Why is it good that the program puts this message on stderr and exits with 1, instead of printing it to stdout and exiting 0?",
            "marks": 2,
            "model": "The data stays clean: a report saved with `>` or piped into another tool never contains the error text, yet the person still sees it. Exit code 1 tells the shell, scripts and CI that it failed; printing an error and exiting 0 is \"a program that lies\".",
            "rubric": [
                "stderr keeps the error out of files and pipes while still showing it to the user",
                "the non-zero exit code is what `&&`, `set -e` or CI read to know it failed",
            ],
            "weak": "\"Because errors go on stderr\" restates the rule without the reason. Answers that only mention the colour or visibility of errors miss the two consumers: other programs read stdout, and the shell and CI read the exit code.",
        },
    ],
    """
    The transcript shows both halves of session 7's "fail loudly, at the boundary": the message on stderr reaches the screen even though stdout was redirected, and the exit code is 1. It also shows the cost of `>`: the shell empties the target file before the command runs, so a failing command still wipes yesterday's report (`wc -l < report.txt` printed `0` when run). Strong answers name the stream, the operator and the order of events.
    """,
    "S5 slide 9; S7 slide 19; run on expense-tracker v0.4 (runs/r1.out)",
    "run",
)

openq(
    "q36", "exam", ["read-tool-output", "read-code"], 5,
    """
    A teammate wants the three largest amounts in the sample file, which contains 250.83 and 137.97:

    ```console
    $ cut -d, -f4 expenses.csv | sort -r | head -n 3
    amount
    91.60
    9.80
    ```
    """,
    [
        {
            "label": "1",
            "prompt": "Say in words what each of the three stages does.",
            "marks": 2,
            "model": "`cut` keeps the fourth comma-separated field of every line, the amount column with its header. `sort -r` puts those lines in reverse order. `head -n 3` keeps the first three lines it receives.",
            "rubric": [
                "`cut` takes the amount field (4th, comma-separated) from every line, header included",
                "`sort -r` reverses the order and `head -n 3` keeps the first three lines",
            ],
            "weak": "Answers that describe the whole pipeline in one phrase (\"it finds the biggest amounts\") describe the intent and skip the stages. Missing that `cut` also takes the header line loses the clue to part 2.",
        },
        {
            "label": "2",
            "prompt": "Give the two reasons the result is wrong.",
            "marks": 2,
            "model": "sort compares text character by character, so `9.80` and `91.60` beat `250.83` (9 after 2). And the header word `amount` is still in the data: as text, letters sort after digits, so it comes first in reverse.",
            "rubric": [
                "Text (character by character) order instead of numeric order",
                "The header line `amount` is still in the input and sorts to the top",
            ],
            "weak": "\"sort is broken\" or \"head took the wrong lines\" blame the wrong stage. Many students find only one of the two bugs: fixing the sort alone still leaves `amount` in the stream: `sort -rn` happens to push it to the bottom, but `cut -d, -f4 expenses.csv | sort -n | head -n 3` prints `amount`, `8.66`, `9.80`.",
        },
        {
            "label": "3",
            "prompt": "Describe in words how you would fix each problem.",
            "marks": 2,
            "model": "Drop the header first by starting at line 2 (`tail -n +2`), and sort as numbers in reverse (`sort -rn`). Then head prints 250.83, 137.97 and 91.60.",
            "rubric": [
                "Remove the header before sorting (start at line 2)",
                "Sort numerically, largest first",
            ],
            "weak": "Removing `amount` by hand from the output, or editing `expenses.csv` to delete the header, treats the symptom and damages the data (lab 09: never edit `expenses.csv` in place). Each fix should be tied to its cause.",
        },
    ],
    """
    Two independent bugs give one believable wrong answer. `sort` defaults to text order, and the header travels through every stage unless you drop it. Run for real, `tail -n +2 expenses.csv | cut -d, -f4 | sort -rn | head -n 3` printed `250.83`, `137.97`, `91.60`. The module's pipelines "Text order is not number order" and "The three largest amounts" show every intermediate output.
    """,
    "S10 slides 6–8; run on the sample file (pipelines_run.log)",
    "run",
)

openq(
    "q37", "hard", ["read-tool-output", "judgement"], 5,
    """
    A teammate writes in the README that the course's `expenses.csv` "has 5 exact duplicate rows", based on this run on the real file:

    ```console
    $ uniq -d expenses.csv | wc -l
    5
    ```

    Session 8 said six.
    """,
    [
        {
            "label": "1",
            "prompt": "What exactly does this pipeline count?",
            "marks": 1,
            "model": "The lines that are identical to the line just before them (one per repeated run), counted by `wc -l`.",
            "rubric": ["Counts only repeated lines that are next to each other (adjacent duplicates)"],
            "weak": "\"It counts the duplicates\" is exactly the belief that caused the bug. \"It counts repeated lines\" is half right. The mark needs what matters: uniq compares each line only with the one just before it, so only adjacent copies count.",
        },
        {
            "label": "2",
            "prompt": "Why does it miss one, and how would you change the pipeline?",
            "marks": 2,
            "model": "One duplicate pair is not adjacent: the two `2025-11-29,Condis,groceries,93.02` rows have other rows between them, so uniq never sees them side by side. Sort the file before `uniq -d` so identical rows become neighbours; then it finds all 6.",
            "rubric": [
                "A duplicate pair is separated by other lines, so uniq misses it",
                "Sort before uniq so identical lines become neighbours",
            ],
            "weak": "Saying uniq is \"unreliable\" or \"random\" is wrong: it is deterministic. Saying \"use sort\" without the reason (identical lines must be adjacent) gets half. Naming the Condis pair is not needed.",
        },
        {
            "label": "3",
            "prompt": "Another teammate runs `sort expenses.csv | uniq | wc -l`, gets 415, and writes \"415 unique expenses\". Correct the claim.",
            "marks": 2,
            "model": "The 415 includes the header line, which is unique. There are 414 unique expenses: 420 minus the 6 duplicates, the same 414 that session 8's `remove_duplicates` returns.",
            "rubric": [
                "The header line is counted in the 415",
                "414 unique expenses, consistent with 420 − 6 and `remove_duplicates`",
            ],
            "weak": "Answers that subtract 6 from 415 confuse the two pipelines. The check is to reconcile the number with what you know: 421 lines = 1 header + 420 expenses. Answers that just say the claim is wrong, without giving 414 and the reason, do not earn the mark.",
        },
    ],
    """
    Both numbers were produced on the real file: `uniq -d expenses.csv | wc -l` prints 5 and `sort expenses.csv | uniq -d | wc -l` prints 6, because the Condis pair at lines 351 and 354 is not adjacent. `sort expenses.csv | uniq | wc -l` prints 415 and `tail -n +2 expenses.csv | sort | uniq | wc -l` prints 414. The skill being tested is checking a pipeline's number against something you already know.
    """,
    "S8 slides 11, 13 and 16; run on expense-tracker expenses.csv (runs/r5.out)",
    "run",
)

openq(
    "q38", "hard", ["read-code", "read-tool-output", "judgement"], 7,
    parts(
        "A script to count dining expenses, run on the copy of the sample file in your course folder, `Moodle Files`:",
        fence("bash", COUNT_SH_UNQUOTED),
        """
        ```console
        $ ./count.sh "Moodle Files/expenses.csv"
        Dining expenses in Moodle Files/expenses.csv:
        grep: Moodle: No such file or directory
        grep: Files/expenses.csv: No such file or directory
        0
        $ echo $?
        0
        ```
        """,
    ),
    [
        {
            "label": "1",
            "prompt": "Explain the two `grep:` lines.",
            "marks": 2,
            "model": "`$file` is not quoted, so bash splits `Moodle Files/expenses.csv` at the space. grep receives two file names, `Moodle` and `Files/expenses.csv`, and neither exists.",
            "rubric": [
                "The unquoted variable is split at the space into two words",
                "grep looks for two files that do not exist",
            ],
            "weak": "\"The path is wrong\" or \"the file is missing\" miss why: the path is right, it is just delivered as two words. The `echo` line works because its `$file` is inside double quotes.",
        },
        {
            "label": "2",
            "prompt": "The script printed `0` and exited 0. Why did it exit 0, and why is that worse than a crash?",
            "marks": 2,
            "model": "A pipeline's exit code is its last command's: wc counted zero lines and exited 0, and nothing (no `set -e`, no `pipefail`) stopped the script. So it reports a wrong answer, \"0 dining expenses\", as success; `&&` or CI would trust it.",
            "rubric": [
                "Exit code comes from wc, the last command of the pipeline",
                "A wrong result with exit 0 is trusted by whoever runs it next (a lie, not a loud failure)",
            ],
            "weak": "Saying \"grep failed so the script should fail\" states a wish; the mark is for the rule. Name the rule (a pipeline's exit code is its last command's) and the consequence (a silent wrong answer).",
        },
        {
            "label": "3",
            "prompt": "Describe two changes, in words, and which problem each solves.",
            "marks": 2,
            "model": "Quote the variable (`\"$file\"`) so the path reaches grep as one word: this fixes the wrong count. Add `set -euo pipefail` at the top so grep's failure makes the pipeline and the script exit non-zero: this fixes the false success.",
            "rubric": [
                "Quote `\"$file\"`, which fixes the split path",
                "`set -e` with `pipefail` (or equivalent), which turns the failure into a non-zero exit",
            ],
            "weak": "Renaming the folder to remove the space works around this one case and leaves the script fragile. Adding only `set -e` is not enough: without `pipefail` the pipeline still ends with wc's 0.",
        },
    ],
    """
    Both problems were reproduced: the unquoted version printed two grep errors, `0`, and exited 0; with only `set -euo pipefail` added it still printed `0` but exited 2, a loud failure; with `"$file"` as well it printed `5`. The question combines three session 10 ideas: word splitting, a pipeline's exit code, and the safety line. It also echoes session 5: a program that prints an error and exits 0 is a program that lies.
    """,
    "S5 slide 9; S10 slides 12, 14, 16; run (runs/s1.out)",
    "run",
)

openq(
    "q39", "exam", ["read-code", "concept"], 8,
    parts(
        "The `scripts/check.sh` of v0.5, written together in session 10:",
        fence("bash", CHECK_SH),
    ),
    [
        {
            "label": "1",
            "prompt": "What does the first line do, and what else must be true before `./scripts/check.sh` runs on a teammate's clone and in CI?",
            "marks": 2,
            "model": "The shebang: run this file with bash. It also needs the x bit, committed so git records 100755, or a fresh clone and CI get `Permission denied`.",
            "rubric": [
                "Shebang: tells the system to run the file with bash",
                "Needs the x bit, and it must be committed (git records it) for clones and CI",
            ],
            "weak": "\"It is a comment\" is what bash sees, but not what the system uses it for. Saying only \"chmod +x\" misses that the change must be committed; your own laptop is not where CI runs.",
        },
        {
            "label": "2",
            "prompt": "In words, what does each of the four commands check, and what are the `echo` lines for?",
            "marks": 2,
            "model": "Lint (`ruff check`), formatting reported but not changed (`ruff format --check`), strict types in src and tests (`mypy`), and the test suite (`pytest`). The `echo \"==> ...\"` lines name each check before its output, so a red run shows which one failed.",
            "rubric": [
                "Lint and formatting check (formatting is checked, not rewritten)",
                "Type check of src and tests, and the test suite",
            ],
            "weak": "Listing tool names without what they check scores nothing. A common slip is saying `ruff format --check` fixes the formatting; it only reports. Another is saying mypy checks the code for errors, which is true of all four; the mark needs the word types.",
        },
        {
            "label": "3",
            "prompt": "What does `set -e` do here, and what would happen without it if ruff found an error?",
            "marks": 2,
            "model": "It stops at the first command that exits non-zero, and the script exits non-zero. Without it every line runs and pytest's exit code decides, so a lint error with passing tests ends in 0.",
            "rubric": [
                "Stops at the first failing command and exits non-zero",
                "Without it, the exit code is the last command's, so a failed check can end in 0",
            ],
            "weak": "\"It makes the script safer\" is too vague. The marker wants the mechanism, stop at the first non-zero exit, and the consequence of its absence: the last command's exit code decides, so a red check can end in 0.",
        },
        {
            "label": "4",
            "prompt": "Why run it before `git tag -a v0.5`?",
            "marks": 1,
            "model": "It runs CI's checks; the tag must sit on a green commit, or Tests is capped at 1.",
            "rubric": ["Same checks as CI, and CI must be green at the tag (Tests capped at 1 otherwise)"],
            "weak": "\"To check the code works\" misses the link to CI and the tag, which is the reason the rubric gives. A full answer says CI must be green on the tagged commit and that a fix pushed after the tag does not count.",
        },
    ],
    """
    The script is the rubric's "Check yourself" chain written one command per line, with `set -euo pipefail` playing the part of `&&`. Run at the v0.5 tag: clean, it printed ruff's `All checks passed!`, `9 files already formatted`, mypy's `Success: no issues found in 8 source files` and `44 passed`, and exited 0; with an unused import it stopped after ruff with exit code 1, and with a broken test after pytest, also 1. Without the x bit, `./scripts/check.sh` gave `Permission denied` (exit 126).
    """,
    "partial-rubric.txt; S10 slides 17–18; S9 slides 19–20; run at expense-tracker v0.5 (runs/check_clean.out, runs/check_lint.out, runs/check_red.out)",
    "run",
)

openq(
    "q40", "exam", ["read-code", "read-tool-output", "judgement"], 8,
    parts(
        "The steps of the course's `.github/workflows/check.yml`:",
        fence("yaml", CHECK_YML_STEPS),
        "The run on your v0.5 commit is red. The log of the Lint step:",
        fence("text", RUFF_F401),
    ),
    [
        {
            "label": "1",
            "prompt": "Session 9 says \"CI is a terminal\". Explain what that means, using this workflow.",
            "marks": 2,
            "model": "GitHub starts a fresh Ubuntu machine and types the steps' commands one after another, as you would: get the code, install uv and Python, `uv sync --locked`, then the same four checks as `check.sh`. Each command's exit code decides whether its step is green or red.",
            "rubric": [
                "The steps are commands typed in order on someone else's (fresh) machine",
                "Exit codes decide green or red; the last four match `check.sh` / the rubric command",
            ],
            "weak": "\"CI runs the tests online\" leaves out that it is the same commands, in order, judged by exit codes. Answers that do not connect the steps to what you type locally miss the point of the phrase.",
        },
        {
            "label": "2",
            "prompt": "Which steps ran, which did not, and why?",
            "marks": 2,
            "model": "Checkout, Install uv, Install dependencies and Lint ran. Lint exited 1 (an unused import), so the job stopped there and Formatting, Types and Tests were skipped, as with `&&` or `set -e`. Their result is unknown.",
            "rubric": [
                "Steps up to and including Lint ran; the three after it were skipped",
                "Because Lint exited non-zero, and a failed step stops the rest (like `&&`)",
            ],
            "weak": "Saying the later steps passed is the key error: they never ran, so their result is unknown. Saying only Lint ran forgets the three set-up steps before it, which Lint needed to have ruff installed at all.",
        },
        {
            "label": "3",
            "prompt": "A teammate suggests changing the Lint step to `uv run ruff check . || true` so the run goes green before the deadline. Do you accept? What do you do instead?",
            "marks": 2,
            "model": "No. `|| true` makes the step exit 0 whatever ruff finds, so the referee is switched off and the unused import stays. Instead run `./scripts/check.sh`, remove the import, push, wait for green, then move the `v0.5` tag.",
            "rubric": [
                "Rejects it: `|| true` turns every lint failure into exit 0, hiding the problem instead of fixing it",
                "Fix locally, push, wait for green CI on the new commit, then move the tag",
            ],
            "weak": "Accepting because \"it is only lint\" forgets that CI is the referee the rubric trusts: a step that cannot fail checks nothing. Rerunning the job unchanged, or adding `# noqa` without reading the error, are the same careless move. Moving the tag before the green tick repeats the problem.",
        },
    ],
    """
    The workflow is the course's real `check.yml`, and the Lint log is real ruff 0.16.9 output for an unused import. A failed step skips the later ones by default, so the run tells you about lint and nothing about types or tests. The partial rubric's "If CI is red on the tag" gives the recovery order: find out what failed, fix, commit and push, wait for CI, then move the tag. Run for real, `uv run ruff check . || true` printed ruff's error and then `echo $?` showed 0: a Lint step written that way can never turn red.
    """,
    "S9 slide 6; expense-tracker .github/workflows/check.yml; partial-rubric.txt; ruff output run (runs/c1.out; pipes-bash-fix/runs/lint.out)",
    "run",
)

openq(
    "q41", "beyond", ["read-code", "read-tool-output", "judgement"], 7,
    parts(
        "A script for a monthly summary, `totals.sh`:",
        fence("bash", TOTALS_SH),
        "On the sample file, which has no clothing expenses:",
        """
        ```console
        $ ./totals.sh expenses.csv
        Report for expenses.csv
        $ echo $?
        1
        ```
        """,
    ),
    [
        {
            "label": "1",
            "prompt": "Explain why the script stopped after its first line of output, without any error message.",
            "marks": 2,
            "model": "`grep clothing` finds nothing and exits 1. wc counts 0 and exits 0, but with `pipefail` the pipeline, and so the assignment, fails, and `set -e` stops the script before the `echo` lines. No match prints no message, so the stop is silent.",
            "rubric": [
                "grep exits 1 when nothing matches (no message, no crash)",
                "`pipefail` makes the pipeline fail despite wc's 0, and `set -e` stops before the `echo` lines",
            ],
            "weak": "\"wc failed\" is wrong: wc counted 0 lines and exited 0. Blaming `set -u` or the `$( )` misreads the script: the dining line worked. Answers that name `set -e` but not `pipefail` miss why a pipeline ending in a successful wc counts as a failure.",
        },
        {
            "label": "2",
            "prompt": "A teammate says \"`set -e` is broken, delete it\". Do you agree? Explain.",
            "marks": 2,
            "model": "No. `set -e` did its job: any non-zero exit counts as failure. Without it a missing file (grep exits 2) would give totals of 0 and exit 0. Better to say that \"no match\" is fine on this one line.",
            "rubric": [
                "Disagrees: `set -e` correctly treats non-zero as failure",
                "Without it, a real failure (for example a missing file) ends with wrong output and exit 0",
            ],
            "weak": "Agreeing because \"it works without it\" ignores the cases it protects against. A full answer names one real failure that would slip through, such as a missing file (grep exits 2) giving totals of 0 with exit 0. The grep messages on the screen do not help a script or CI, which read only the exit code.",
        },
        {
            "label": "3",
            "prompt": "Describe in words a fix that keeps `set -e`.",
            "marks": 1,
            "model": "Mark that one line as allowed to find nothing, for example `|| true` at the end of the clothing line, so a count of 0 is normal there while every other line still stops the script.",
            "rubric": ["Allows a failure on the clothing line only (e.g. `|| true`), keeping `set -e` for the rest"],
            "weak": "Turning off `set -e` for the whole script, or deleting the clothing line, avoids the question instead of handling it. The fix must be local: this one line may find nothing, and every other failure should still stop the script.",
        },
    ],
    """
    Run for real: with `set -euo pipefail` the script printed only `Report for expenses.csv` and exited 1. With `set -eu` and no `pipefail` it printed `dining: 5` and `clothing: 0` and exited 0. With `|| true` at the end of the clothing line it printed both totals and exited 0. Without `set -e`, a missing file printed two grep errors, `dining: 0` and `clothing: 0`, and exited 0. A `grep -c` version stops the same way; here the failure hides inside a pipeline whose last command succeeded, which is exactly what `pipefail` is for.
    """,
    "S5 slide 9; S10 slide 16; run (pipes-bash-fix/runs/totals.out, runs/scripts.out)",
    "run",
)

# ===========================================================================
# Sort questions
# ===========================================================================
sortq(
    "q42", "core", ["concept", "predict-output"], 2,
    """
    Where does each piece of text end up? (`uv run expenses report nosuch.csv` writes `could not read nosuch.csv` to stderr and exits 1; ruff writes its list of problems to stdout; uv writes its progress lines to stderr.)
    """,
    [
        ("screen", "The terminal"),
        ("file", "A file"),
        ("pipe", "The next command's stdin"),
        ("gone", "Discarded"),
    ],
    [
        (
            "The report lines of `uv run expenses report > report.txt`",
            "file",
            "`>` sends stdout, where the report lines are written, into the file.",
        ),
        (
            "The message from `uv run expenses report nosuch.csv > report.txt`",
            "screen",
            "The message is on stderr; `>` moves only stdout.",
        ),
        (
            "The message from `uv run expenses report nosuch.csv 2> errors.txt`",
            "file",
            "`2>` redirects stderr; `cat errors.txt` showed the message when run.",
        ),
        (
            "The message from `uv run expenses report nosuch.csv 2> /dev/null`",
            "gone",
            "`/dev/null` discards it. The exit code is still 1.",
        ),
        (
            "The lines `grep dining expenses.csv` prints in `grep dining expenses.csv | wc -l`",
            "pipe",
            "grep's stdout becomes wc's stdin; only the count reaches the screen.",
        ),
        (
            "The message from `uv run expenses report nosuch.csv | wc -l`",
            "screen",
            "stderr skips the pipe; wc printed `0` below the message.",
        ),
        (
            "The message from `uv run expenses report nosuch.csv 2>&1 | wc -l`",
            "pipe",
            "`2>&1` joins stderr to stdout before the pipe, so wc counted it and printed `1`.",
        ),
        (
            "Ruff's list of problems in `uv run ruff check . > /dev/null`",
            "gone",
            "ruff reports on stdout, so `> /dev/null` swallowed it; the run printed nothing but still exited 1.",
        ),
        (
            "uv's `Creating virtual environment at: .venv` line during `./scripts/check.sh > /dev/null` in a fresh clone",
            "screen",
            "uv writes progress to stderr, which `> /dev/null` does not touch; it showed on screen when run.",
        ),
    ],
    """
    Ask two questions for every piece of text: which stream did the program write it to, and what did the command line do with that stream? `>` and `> /dev/null` move stdout only; `2>` moves stderr; `|` carries stdout only; `2>&1` joins stderr to wherever stdout is going. Every item was run: in particular, ruff's findings vanished with `> /dev/null` (exit code still 1), while uv's progress lines still appeared.
    """,
    "S7 slide 19; S10 slides 4, 5, 9; run (runs/r1.out, runs/r2.out, runs/r6.out, runs/c1.out, runs/l2.out)",
    "run",
)

sortq(
    "q43", "exam", ["predict-output", "concept"], 6,
    """
    On the sample file (5 dining lines, no clothing), does the second command run? (`grep` exits 1 when it finds nothing; the ruff case has an unused import in `report.py`.)
    """,
    [("runs", "The second command runs"), ("skipped", "The second command does not run")],
    [
        (
            "`grep -c dining expenses.csv && echo found`",
            "runs",
            "grep found lines and exited 0, so `&&` continues.",
        ),
        (
            "`grep -c clothing expenses.csv && echo found`",
            "skipped",
            "grep found nothing and exited 1; `&&` stops.",
        ),
        (
            "`grep -c clothing expenses.csv || echo none`",
            "runs",
            "`||` runs its right side exactly when the left side failed.",
        ),
        (
            "`grep -c dining expenses.csv || echo none`",
            "skipped",
            "The left side succeeded, so there is nothing for `||` to do.",
        ),
        (
            "`uv run ruff check . ; uv run pytest` with ruff finding an error",
            "runs",
            "`;` runs the next command regardless of the exit code.",
        ),
        (
            "In a script with `set -e`: `uv run ruff check .` finds an error, and the next line is `uv run pytest`",
            "skipped",
            "`set -e` stops the script at the first non-zero exit.",
        ),
        (
            "In a script with `set -e` but no `pipefail`: `grep clothing expenses.csv | wc -l`, then the next line `echo done`",
            "runs",
            "The pipeline's exit code is wc's, 0, so `set -e` sees no failure; `done` was printed when run.",
        ),
        (
            "In a script with `set -eo pipefail`: `grep clothing expenses.csv | wc -l`, then the next line `echo done`",
            "skipped",
            "With pipefail grep's 1 makes the pipeline fail, and `set -e` stops before `done` (run: exit 1).",
        ),
    ],
    """
    `&&` continues only after exit 0, `||` only after a non-zero exit, `;` always. `set -e` behaves like an `&&` between lines, judging each pipeline by its exit code: the last command's unless `pipefail` is on. Each item was run in bash; the two pipeline items printed `0` and then `done`, and `0` with exit code 1, respectively.
    """,
    "S5 slide 9; partial rubric; S10 slide 16; run (runs/r4.out, runs/c1.out, runs/s2.out)",
    "run",
)

sortq(
    "q44", "core", ["concept"], 4,
    """
    Which tool does each job in a pipeline on `expenses.csv`?
    """,
    [
        ("grep", "`grep`"),
        ("cut", "`cut`"),
        ("sort", "`sort`"),
        ("uniq", "`uniq`"),
        ("wc", "`wc`"),
    ],
    [
        ("Keep only the lines that mention transport", "grep", "grep selects lines by their content."),
        ("Take the amount out of each line", "cut", "`cut -d, -f4` keeps one comma-separated field."),
        (
            "Put the categories in order so that equal names sit together",
            "sort",
            "Ordering lines is sort's only job; it is what makes uniq work.",
        ),
        (
            "Collapse repeated neighbouring lines into one, with how many there were",
            "uniq",
            "`uniq -c` does exactly this, and only for neighbours.",
        ),
        ("Say how many lines came out of the previous stage", "wc", "`wc -l` counts lines."),
        ("Drop every line that mentions dining", "grep", "`grep -v` keeps the lines that do not match."),
        ("Show only the lines that repeat", "uniq", "`uniq -d` prints one copy of each repeated line."),
        ("Order the amounts from largest to smallest as numbers", "sort", "`sort -rn`: numeric, reversed."),
        ("Keep just the merchant names", "cut", "`cut -d, -f2` keeps the second field."),
    ],
    """
    Each tool does one job on lines of text, and a pipeline is a sequence of those jobs: select lines (grep), select a column (cut), order (sort), collapse neighbours (uniq), count (wc). "Judgement, not memorised flags": you need to know the job of each tool so you can read a pipeline stage by stage; a flag in a question is there to be read, not recalled. All of these were used in the module's pipelines on the sample file.
    """,
    "S10 slides 6–8; run on the sample file (pipelines_run.log)",
    "run",
)

# ===========================================================================
# Added after review (q45-q51); every artefact run in work/pipes-bash-fix/
# ===========================================================================
mcq(
    "q45", "beyond", ["read-tool-output", "judgement"], 2,
    """
    A teammate wants the sample `expenses.csv` sorted and runs, on a copy:

    ```console
    $ sort expenses.csv > expenses.csv
    $ echo $?
    0
    $ wc -l < expenses.csv
    0
    ```

    Why is the file now empty?
    """,
    [
        (
            "The shell emptied the file for `>` before sort started, so sort read nothing",
            True,
            "Right: redirections are set up first. By the time sort opened the file, `>` had already cut it to zero length.",
        ),
        (
            "sort failed because the file was open twice, and a failed command leaves its output empty",
            False,
            "sort exited 0, as `echo $?` shows. Nothing failed; it sorted an empty file correctly.",
        ),
        (
            "sort removes duplicate lines, and every line counted as a duplicate of itself",
            False,
            "sort never removes lines; that is uniq's job. Sorting into a new file kept all 19 lines (run).",
        ),
        (
            "`wc -l <` cannot read a file that sort has just written, so it prints 0",
            False,
            "`<` feeds wc whatever is in the file, and the file really has 0 lines.",
        ),
    ],
    """
    For `sort expenses.csv > expenses.csv` the shell opens `expenses.csv` for writing and empties it before sort runs. sort then reads the now-empty file, sorts nothing and exits 0. Run on a copy, the file went from 19 lines to 0. The safe habit is lab 09's: never edit `expenses.csv` in place. Write to a new name (`sort expenses.csv > sorted.csv` kept all 19 lines, run) and check the result before replacing anything.
    """,
    "S10 slides 5, 9; labs/09-terminal.md exercise 2 ('Never edit expenses.csv in place'); run on a copy of the sample file (pipes-bash-fix/runs/inplace.out)",
    "run",
)

mcq(
    "q46", "core", ["predict-output"], 4,
    """
    Lab 09's stretch exercise runs this in a fresh clone of the expense-tracker (v0.4), where `src/expense_tracker/` holds `__init__.py`, `cli.py` and `report.py`:

    ```bash
    find src -name "*.py" -type f | wc -l
    ```

    What does it print?
    """,
    [
        (
            "`6`, because find also searches the `tests` folder next to `src`",
            False,
            "find searches only the folders you name, here `src`. `find src tests -name \"*.py\" | wc -l` gives 6 (run).",
        ),
        (
            "The three file paths that find printed, one per line, starting with `src/expense_tracker/__init__.py`",
            False,
            "The paths go into the pipe instead of to the screen; wc prints only the count.",
        ),
        (
            "`3`: one line per Python file under `src`, counted by wc",
            True,
            "Right: three paths in, one number out.",
        ),
        (
            "`3 src`, the count followed by the name of the folder searched",
            False,
            "wc reads stdin and never sees a name, so it prints only the number.",
        ),
    ],
    """
    `find src -name "*.py" -type f` prints one line per matching file under `src`: the paths of `__init__.py`, `cli.py` and `report.py`. The pipe hands those three lines to `wc -l`, which prints `3` (run on a fresh clone at v0.4). Searching `src tests` gives 6, the answer to the lab's first question. Same shape as sample Q6: wc counts what the previous stage printed, and it prints no name because it read stdin.
    """,
    "labs/09-terminal.md exercise 4; midterm sample Q6 (shape); run on a fresh clone of expense-tracker v0.4 (pipes-bash-fix/runs/find.out)",
    "run",
    origin="lab",
)

openq(
    "q47", "exam", ["read-diff", "compare", "judgement"], 8,
    parts(
        "Your group's first `scripts/check.sh` ran the four checks on four lines and ended with `echo \"Ready to tag\"`. A teammate changes it:",
        fence("diff", CHECK_DIFF),
        """
        Two candidate commit messages:

        - A: `Update check.sh`
        - B: `Stop check.sh at the first failing check`
        """,
    ),
    [
        {
            "label": "1",
            "prompt": "What does this change do? Say what the script did before when a check failed, and what it does now.",
            "marks": 2,
            "model": "Before, every line ran and the script exited with the `echo`'s code, so a failed check still printed Ready to tag and exited 0. Now the first failing check stops the script with a non-zero exit, and Ready to tag appears only when all four pass.",
            "rubric": [
                "Before: every line ran and the exit code was the `echo`'s, so a failed check still ended in 0 and Ready to tag",
                "After: stops at the first non-zero exit and exits non-zero; Ready to tag only when all four checks pass",
            ],
            "weak": "\"It makes the script safer\" or \"it adds error handling\" names no mechanism. Many answers describe only the new behaviour and miss what was wrong before: the old script ended with `echo`, so its exit code was 0 whatever ruff, mypy or pytest said. Saying the old script \"stopped at the error anyway\" is the misconception the change fixes.",
        },
        {
            "label": "2",
            "prompt": "Which message is better for someone reading the history six months later, and why?",
            "marks": 2,
            "model": "B. It says what behaviour changed, so a reader knows why the commit exists without opening the diff. A only names the file, which the diff already shows.",
            "rubric": [
                "Chooses B",
                "Reason: B states the behaviour that changed; A says nothing the list of changed files does not already say",
            ],
            "weak": "\"B is longer\" or \"B is more detailed\" gives no reason; length is beside the point. The mark is for saying what B tells a future reader that A does not: what the script now does differently. Choosing A because \"the diff explains it\" forgets that `git log --oneline` shows only the messages.",
        },
        {
            "label": "3",
            "prompt": "Describe in words one check you would run to show the change works.",
            "marks": 2,
            "model": "Make one check fail on purpose, say an unused import, run the script and confirm it stops there with no Ready to tag and a non-zero `echo $?`. Then undo it and confirm the clean run still ends with Ready to tag and 0.",
            "rubric": [
                "Breaks a check on purpose and expects the script to stop with a non-zero exit code (no Ready to tag)",
                "Also confirms the clean case still passes with exit 0",
            ],
            "weak": "\"Run it and see if it passes\" proves nothing: the old script also passed on clean code. The test that shows the change is the failing case, as in session 8's red step: make it fail first, then check the exit code as well as the screen. Testing only the failing case and never the clean one gets half.",
        },
    ],
    """
    The diff adds one line, so the question is what it changes in behaviour. Without `set -e` a script runs every line and exits with the last command's code. Run on a copy of the expense-tracker with a broken `largest_expense`, the old script printed `1 failed, 23 passed`, then `Ready to tag`, and exited 0; with the new line the same run stopped after pytest and exited 1. `-u` and `pipefail` change nothing in this script, which has no variables and no pipelines. Message B tells a future reader the behaviour that changed; A only names the file. The test is session 8's habit: see it fail first.
    """,
    "midterm sample Q8 (compare shape); partial rubric 'Check yourself'; S10 slide 16; run on a copy of expense-tracker v0.4 (pipes-bash-fix/runs/compare-U8.diff, nosete-test.out, sete-test.out)",
    "run",
)

mcq(
    "q48", "hard", ["read-code", "read-tool-output", "judgement"], 7,
    """
    Your group's first `scripts/check.sh`:

    ```bash
    #!/usr/bin/env bash
    uv run ruff check .
    uv run ruff format --check .
    uv run mypy src tests
    uv run pytest -q
    echo "Ready to tag"
    ```

    After a teammate changes `largest_expense`, you run it (trimmed):

    ```console
    $ ./scripts/check.sh
    All checks passed!
    7 files already formatted
    Success: no issues found in 6 source files
    ....................F...                                                 [100%]
    ...
    FAILED tests/test_report.py::test_largest_expense_tie_goes_to_the_first - Ass...
    1 failed, 23 passed in 0.05s
    Ready to tag
    $ echo $?
    0
    ```

    Why does the script exit 0 although a test failed?
    """,
    [
        (
            "pytest exits 0 when most tests pass; only a run where every test fails counts as a failure",
            False,
            "Run on its own here, `uv run pytest -q` exits 1: one failing test is enough. The 1 was there; the script threw it away.",
        ),
        (
            "Without `set -e` every line runs, and the script exits with its last command's code: the `echo`",
            True,
            "Right: the lines behave like commands joined by `;`. pytest exited 1, then `echo` ran and exited 0, and that is what the script reports.",
        ),
        (
            "`uv run` hides the exit code of the tool it starts and always hands 0 back to the script",
            False,
            "`uv run` passes the tool's exit code on: `uv run ruff check .` exits 1 when ruff finds a problem, which is what CI's Lint step relies on.",
        ),
        (
            "A script's exit code comes from its first command, and ruff reported that all checks passed",
            False,
            "It is the last command that counts. Had ruff failed instead, this script would still have exited 0, because `echo` ran last.",
        ),
    ],
    """
    A script without `set -e` runs every line, like commands joined by `;`, and exits with the code of the last command that ran. Here pytest exited 1 (checked by running `uv run pytest -q` on its own), then `echo "Ready to tag"` ran and exited 0, so the script exited 0 and printed a message that is false. Anything that trusts the exit code sees green. Session 5: "A program that prints an error and exits 0 is a program that lies." With `set -euo pipefail` on line 2, the same run stopped after pytest, printed no `Ready to tag` and exited 1 (run).
    """,
    "S5 slide 9; partial rubric 'Check yourself'; S10 slide 16; run on a copy of expense-tracker v0.4 with a broken largest_expense (pipes-bash-fix/runs/nosete-test.out, sete-test.out, lint.out)",
    "run",
)

mcq(
    "q49", "core", ["concept", "read-tool-output"], 1,
    """
    You meant to count the dining lines but pressed Enter too early. The prompt does not come back, so you type the file name as well:

    ```console
    $ grep dining
    expenses.csv
    ```

    Still nothing happens. What is going on?
    """,
    [
        (
            "grep is searching every file on the disk for `dining`, which takes a while; wait for it",
            False,
            "grep never goes looking for files on its own. With no file name it reads stdin, so waiting changes nothing.",
        ),
        (
            "grep is reading stdin, the keyboard, and searching what you type; Ctrl-C stops it",
            True,
            "Right: `expenses.csv` was read as a line of text to search, and it contains no `dining`. Ctrl-C (session 9) stops the program.",
        ),
        (
            "grep crashed because the file name was missing, and the terminal froze; open a new window",
            False,
            "Nothing crashed: grep is running and waiting for input. Ctrl-C stops it without losing the terminal.",
        ),
        (
            "grep is waiting for its file name and will open `expenses.csv` once you press Enter again",
            False,
            "What you type now is input, not an argument. grep treats `expenses.csv` as text to search, and it finds no `dining` in it.",
        ),
    ],
    """
    Programs that read text take it from a file name or, when given none, from stdin. Nothing was piped or redirected, so stdin is the keyboard: grep waits for lines and prints back any that contain `dining`. Typing `expenses.csv` gave it one line of text with no `dining` in it, so it printed nothing. Run for real in an interactive bash: typing `2025-07-10,Federal Cafe,dining,53.82` made grep print that line back, and Ctrl-C stopped it (`echo $?` then showed 130). Session 9: "Ctrl-C stops the program that is running." What you meant was `grep dining expenses.csv | wc -l`.
    """,
    "S9 slide 12 (Ctrl-C); S10 slides 5, 9; run in an interactive bash (pipes-bash-fix/runs/stdin_wait.out)",
    "run",
)

mcq(
    "q50", "exam", ["predict-output"], 2,
    """
    On the sample file (5 dining, 3 transport and 2 home expenses; one dining merchant is called `Sushi at home`):

    ```console
    $ grep -c dining expenses.csv > counts.txt
    $ grep -c transport expenses.csv >> counts.txt
    $ grep -c home expenses.csv > counts.txt
    $ cat counts.txt
    ```

    What does the last command print?
    """,
    [
        (
            "`3`",
            True,
            "Right: the third `>` emptied the file and grep wrote one number: the 3 lines that contain `home`, Sushi at home included.",
        ),
        (
            "`5`, `3` and `3`, one per line",
            False,
            "That needs `>>` on the third line too. `>` replaces the file every time, whatever wrote to it before.",
        ),
        (
            "`2`",
            False,
            "The file was replaced, but `grep -c home` counts lines that contain `home` anywhere: 3 lines for 2 home expenses.",
        ),
        (
            "`5`, `3` and `2`, one per line",
            False,
            "Two slips at once: the third `>` replaces the file instead of adding to it, and grep counts 3 lines for the 2 home expenses.",
        ),
    ],
    """
    `>` empties the file before the command runs; `>>` adds to the end. After the second command `counts.txt` held `5` and `3` (checked with `cat`). The third command uses `>` again, so the shell empties the file and grep writes a single number. That number is 3: grep counts lines that contain `home` anywhere, and `2025-07-06,Sushi at home,dining,24.90` is one of them. Run for real, `cat counts.txt` printed `3`. To collect several counts in one file, every command after the first needs `>>`.
    """,
    "S10 slides 5, 9; run on the sample file (pipes-bash-fix/runs/append.out)",
    "run",
)

mcq(
    "q51", "beyond", ["read-tool-output", "judgement"], 5,
    """
    You add two expenses, one with a comma in the merchant name, and look at the categories with a pipeline:

    ```console
    $ uv run expenses add "Bar Ramon" dining 9.80 --date 2025-12-30
    added Bar Ramon (dining) 9.80 to data/expenses.csv
    $ uv run expenses add "Can Recasens, Gracia" dining 33.02 --date 2025-12-31
    added Can Recasens, Gracia (dining) 33.02 to data/expenses.csv
    $ cat data/expenses.csv
    date,merchant,category,amount
    2025-12-30,Bar Ramon,dining,9.80
    2025-12-31,"Can Recasens, Gracia",dining,33.02
    $ tail -n +2 data/expenses.csv | cut -d, -f3
    dining
     Gracia"
    ```

    `uv run expenses report data/expenses.csv` shows both under dining, 42.82 in total. What explains the second line of cut's output?
    """,
    [
        (
            "`add` saved the row wrongly: the quotes are a bug, and the report total is wrong too",
            False,
            "The quotes are how CSV keeps a comma inside one field; Python's `csv` writer added them on purpose, and the report reads them back correctly.",
        ),
        (
            "`tail -n +2` broke the long line in two, and cut printed the end of the second half",
            False,
            "tail works on whole lines; it never splits one. The line reached cut intact, with one comma more than the others.",
        ),
        (
            "The quotes shift every row by one field, so the category is now field 4 in all rows",
            False,
            "Only the row with the comma has an extra field. Bar Ramon's row still gave `dining` from field 3.",
        ),
        (
            "cut splits at every comma, even inside quotes; the program's CSV reader does not",
            True,
            "Right: for cut the quoted name is two fields, so field 3 is ` Gracia\"`. `csv.reader` understands the quotes.",
        ),
    ],
    """
    `cut -d, -f3` knows nothing about CSV: it splits each line at every comma. `add` writes with Python's `csv` module, which puts quotes around a merchant name that contains a comma, so that row has one comma more than the others and its third field is ` Gracia"`. The program reads the file with `csv.reader`, which respects the quotes, so the report shows dining 42.82 for both (run). Text tools give quick answers on simple files like the course's `expenses.csv`; when a field can contain the separator, trust the tested code. Same habit as the merchant trap: check a pipeline's answer against something you know.
    """,
    "expense-tracker v0.4 cli.py (add uses csv.writer); S10 slides 6–8; run on a fresh clone of expense-tracker v0.4 (pipes-bash-fix/runs/comma.out)",
    "run",
)

# ---------------------------------------------------------------------------
# Added by the calibration pass: thin S10 topics (>>, <, 2>&1, shebang, set -u)
# ---------------------------------------------------------------------------
mcq(
    "q52", "core", ["predict-output"], 2,
    """
    In an empty folder:

    ```console
    $ echo start > log.txt
    $ echo checks passed >> log.txt
    $ echo checks passed >> log.txt
    $ cat log.txt
    ```

    What does the last command print?
    """,
    [
        (
            "`checks passed`, once, because the second `>>` replaces the first line",
            False,
            "`>>` never replaces anything. It adds the output to the end of the file, whatever is already there.",
        ),
        (
            "`start`, `checks passed` and `checks passed`, one per line",
            True,
            "Right: the first command creates the file with `start`, and each `>>` adds one line at the end. Three lines in all.",
        ),
        (
            "`start` and `checks passed`, because the same line is not written twice",
            False,
            "Nothing removes duplicates here. Dropping repeated lines is the job of `sort | uniq`, not of a redirection.",
        ),
        (
            "`checks passed` twice, because the first `>>` replaced `start`",
            False,
            "Replacing is what a single `>` does. `>>` keeps what is already in the file and appends.",
        ),
    ],
    """
    `>` replaces the content of a file, `>>` appends to it. The first line creates `log.txt` holding `start`. The next two each add `checks passed` at the end, so the file has three lines and `cat` prints them in that order. Had the second line used `>`, the file would have held only `checks passed` once, because `>` empties the file before the command runs. Run for real, `cat log.txt` printed the three lines.
    """,
    "S10 slides 5, 9; run on the sample file (calibration-fix/pb)",
    "run",
)

mcq(
    "q53", "exam", ["predict-output", "read-tool-output"], 2,
    """
    On the sample file:

    ```console
    $ head -3 expenses.csv > small.csv
    $ sort < small.csv > sorted.csv
    $ cat sorted.csv
    ```

    What does `cat sorted.csv` print?
    """,
    [
        (
            "The header, then the two expense rows, in date order",
            False,
            "`sort` knows nothing about headers. It orders all three lines as plain text, header included.",
        ),
        (
            "The three lines of `small.csv` unchanged, because `sort` only works on a file name",
            False,
            "`<` feeds the file to `sort` on stdin, and `sort` reads stdin when it has no file name. It sorts exactly as before.",
        ),
        (
            "Nothing: the `>` empties `small.csv` before `sort` can read it",
            False,
            "The output goes to a different file, `sorted.csv`. Reading and writing the same file in one command is the trap, not this one.",
        ),
        (
            "The two expense rows, then the header line, because lines starting with a digit sort first",
            True,
            "Right: `sort` compares whole lines, and a line starting with `2` comes before one starting with `d`. The header ends up last.",
        ),
    ],
    """
    `sort < small.csv` hands the file to `sort` on its standard input, so it behaves like `sort small.csv`, and `> sorted.csv` sends the result to a file instead of the screen: the command prints nothing. `sort` orders every line, and the header is just a line. Digits come before letters, so the two rows starting with `2025-` go first and `date,merchant,category,amount` goes last. That is why a pipeline that sorts a CSV usually drops the header first with `tail -n +2`. Run for real, the file held the two rows and then the header.
    """,
    "S10 slides 5, 9, 6–8; run on the sample file (calibration-fix/pb)",
    "run",
)

mcq(
    "q54", "beyond", ["predict-output", "read-tool-output"], 2,
    """
    On the sample file, `small.csv` holds the header and the first two expenses, and `nosuch.csv` does not exist. The shell applies redirections from left to right: each one points a stream at wherever its target points at that moment. So in `> all.txt 2>&1`, stdout goes to the file first, and `2>&1` then sends stderr to wherever stdout now goes.

    ```console
    $ cat small.csv nosuch.csv > all.txt 2>&1
    $ cat all.txt
    ```

    What appears on the screen when the first command runs, and what does `all.txt` hold?
    """,
    [
        (
            "Nothing on the screen; `all.txt` holds the three CSV lines, then `cat: nosuch.csv: No such file or directory`",
            True,
            "Right: both streams go to the file, in the order `cat` produced them. The error comes last because the second file is read last.",
        ),
        (
            "The error on the screen; `all.txt` holds the three CSV lines",
            False,
            "That is what `> all.txt` alone does, because only stdout is redirected. With `2>&1` after it, stderr follows stdout into the file.",
        ),
        (
            "The three CSV lines on the screen; `all.txt` holds the error message only",
            False,
            "It reverses the streams: the CSV lines are stdout and go to the file, and the error is stderr.",
        ),
        (
            "Nothing on the screen; `all.txt` holds only the CSV lines, because `2>&1` sends the error back to the screen",
            False,
            "`&1` means 'where stdout points now', and stdout already points at `all.txt`. It does not mean the screen.",
        ),
    ],
    """
    `cat` writes the three lines of `small.csv` (the header and two expenses) to stdout, and its complaint about the missing file to stderr. `> all.txt` points stdout at the file. `2>&1` then points stderr at wherever stdout points, which is now the file, so the screen stays empty and `all.txt` gets both. The exit code is still 1, because the second file failed. Run for real, `cat all.txt` showed the three CSV lines and then the `cat:` error. This is the usual way to keep a whole log of a command in one file.
    """,
    "extension of S10 slide 5 (2>&1 is not on the slides); run on the sample file (calibration-fix/pb)",
    "run",
)

mcq(
    "q55", "core", ["concept"], 7,
    """
    The first lines of the group's `scripts/check.sh`:

    ```bash
    #!/usr/bin/env bash
    uv run ruff check .
    ```

    A teammate runs `./scripts/check.sh`. What is the job of the first line?
    """,
    [
        (
            "It makes the file executable, so nobody needs to run `chmod +x`",
            False,
            "Permission is a property of the file, set with `chmod`. The first line is only text inside the file.",
        ),
        (
            "It makes the script stop at the first command that fails",
            False,
            "That is `set -e`, a line of its own. The first line says which program runs the file.",
        ),
        (
            "It loads the tools the script uses, so that `uv` and `ruff` are found",
            False,
            "Nothing is loaded. Commands are found through the `PATH`, as they are in any shell.",
        ),
        (
            "It tells the system to run the file with bash, whatever shell the caller is using",
            True,
            "Right: the two characters `#!` followed by a program name say 'start this program and give it the file'.",
        ),
    ],
    """
    A bash script starts with `#!/usr/bin/env bash`, the shebang. When you run `./scripts/check.sh`, the system reads that first line and starts `bash` with the file as its input, so the script runs the same from a zsh terminal, from CI or from another script. It does not grant the right to run the file: that is the `x` permission, which `chmod +x` adds and git records. It also does not stop the script on errors; that needs `set -e`.
    """,
    "S10 slides 12, 14; S9 permissions",
    "reasoning",
)

mcq(
    "q56", "exam", ["read-tool-output", "judgement"], 7,
    """
    `count.sh` counts the rows of the file you give it:

    ```bash
    #!/usr/bin/env bash
    set -u
    FILE=$1
    echo "Rows in $FILE: $(wc -l < "$FILE")"
    ```

    Run with a file name it prints `Rows in expenses.csv: 19`. Run with no argument:

    ```console
    $ ./count.sh
    ./count.sh: line 3: $1: unbound variable
    $ echo $?
    1
    ```

    Why did it stop there?
    """,
    [
        (
            "`set -u` stops bash when a script reads a variable that was never set, here `$1`; without it the script would go on with an empty `FILE`",
            True,
            "Right: no argument means `$1` was never set. Without `set -u` the script would run on and fail later, or print a wrong line.",
        ),
        (
            "`$1` cannot be used in a script that has `set -u`, so every script with it must avoid arguments",
            False,
            "`$1` works fine when an argument is given, as the first run shows. The error is about an unset value.",
        ),
        (
            "`set -u` checks that the file exists before the script runs, and `expenses.csv` was missing",
            False,
            "No file name was given at all, and `set -u` checks variables, not files.",
        ),
        (
            "`wc -l` failed on the missing file, and `set -u` turned its error into an unbound variable message",
            False,
            "`wc` never ran. The message names `$1` and line 3, the line before `wc`.",
        ),
    ],
    """
    `set -u` makes bash treat reading an unset variable as an error. With no argument, line 3 reads `$1`, which was never set, so the script stops with `unbound variable` and exit code 1, before `wc` is started. Without `set -u`, `FILE` would be empty, `wc` would be given nothing to read and the script would carry on: it printed `No such file or directory` and then a line saying `Rows in :` with no number. A script that fails at the first missing input is easier to trust than one that goes on with empty values. Run for real, both versions behaved as shown.
    """,
    "S10 slide 16; run in calibration-fix/pb",
    "run",
)

# ===========================================================================
# Added on Fri 16 Oct 2026, after session 10 (q57-q70): script arguments, conditions, loops,
# the ((counter++)) trap, check.sh at v0.5, working on a copy, and the lab's last exercises.
# Every artefact was run in scratchpad/work/s10/ (runs/*.out), shown in GNU format.
# ===========================================================================
TOP_SH = md(
    """
    #!/usr/bin/env bash
    set -euo pipefail
    if [ "$#" -lt 1 ]; then
      echo "usage: $0 FILE" >&2
      exit 2
    fi
    if [ ! -f "$1" ]; then
      echo "error: $1 is not a file" >&2
      exit 1
    fi
    tail -n +2 "$1" | cut -d, -f3 | sort | uniq -c | sort -rn | head -n 3
    """
)

TOP_RUNS = md(
    """
    $ ./top.sh expenses.csv
        119 groceries
         86 dining
         76 transport
    $ ./top.sh; echo $?
    usage: ./top.sh FILE
    2
    $ ./top.sh nofile; echo $?
    error: nofile is not a file
    1
    """
)

mcq(
    "q57", "exam", ["read-code", "predict-output"], 9,
    parts(
        "`top.sh` is saved in the folder with the course's `expenses.csv`:",
        fence("bash", TOP_SH),
        "You run it with no argument and then ask for the exit code. What do you see?",
    ),
    [
        (
            "`usage: ./top.sh FILE` on the screen, and `2` from `echo $?`",
            True,
            "Right: `$#` is 0, so the first test is true, the message goes out on stderr and the script leaves with `exit 2`. `$0` is the script's name as you typed it.",
        ),
        (
            "`usage: ./top.sh FILE` on the screen, and `0` from `echo $?`, because the `echo` succeeded",
            False,
            "`$?` is the exit code of the script, which ended with `exit 2`, not with the `echo` inside it.",
        ),
        (
            "`error: is not a file` on the screen, and `1` from `echo $?`",
            False,
            "The first test catches the missing argument and the script leaves before the second test is reached.",
        ),
        (
            "Nothing on the screen, and `1` from `echo $?`, because `set -u` stops the script at `\"$1\"`",
            False,
            "`set -u` fires only when `$1` is read. The argument count is tested first, and the script has already left by then.",
        ),
    ],
    """
    `"$#"` is the number of arguments: 0 here, so `-lt 1` is true and the usage branch runs. `echo ... >&2` writes the message to stderr, `exit 2` ends the script with code 2, and the `$?` you read afterwards is that 2. Run for real, `./top.sh` printed `usage: ./top.sh FILE` and `echo $?` printed `2`, while `./top.sh nofile` printed `error: nofile is not a file` and `1`. Two different mistakes, two different numbers (slide 15).
    """,
    "S10 slides 14–15; run (runs/s10_top.out)",
    "run",
)

mcq(
    "q58", "core", ["concept", "judgement"], 9,
    parts(
        "In `top.sh` the usage error leaves with `exit 2` and the missing-file error with `exit 1`:",
        fence("console", TOP_RUNS),
        "Which statement about the two numbers is right?",
    ),
    [
        (
            "Only `exit 1` is a failure; `exit 2` is a warning, so `&&` carries on after it",
            False,
            "`&&`, `set -e` and CI treat every non-zero number as a failure. The two errors differ only in which number they use.",
        ),
        (
            "The number is a count of the errors: 2 for two missing arguments, 1 for one missing file",
            False,
            "Exit codes are not counts. The script uses 2 for 'called wrongly' and 1 for 'could not do the job', which is a convention.",
        ),
        (
            "Any non-zero number is a failure; the script uses 2 for a wrong call and 1 for a job that failed, and CI reads the number",
            True,
            "Right: 0 means success, anything else is failure (slide 15). The number is what the next command, `set -e` or CI reads, never the message.",
        ),
        (
            "The numbers are only for people; CI ignores them and reads the messages on the screen",
            False,
            "Slide 15: CI reads one thing, the exit code. That is what turns a step red.",
        ),
    ],
    """
    Slide 15 puts it in one line: "0 means success. Anything else is failure." `top.sh` uses two different non-zero numbers so that a caller can tell a wrong call (2, usage) from a job that could not be done (1, the argument is not a file). Both stop a chain of `&&`, both stop a script with `set -e`, and both turn a CI step red. The messages go to stderr with `>&2`, so they are not mixed into the output.
    """,
    "S10 slides 14–15; labs/10-bash.md exercise 2; run (runs/s10_top.out)",
    "run",
)

mcq(
    "q59", "core", ["read-code", "predict-output"], 9,
    parts(
        "`top.sh` (above) tests `[ ! -f \"$1\" ]`. In the current folder `expenses.csv` is a file and `data` is a folder. What does `./top.sh data` do?",
    ),
    [
        (
            "It prints the three most common words in the folder's files, because `tail` reads whatever it is given",
            False,
            "The script never gets that far. `-f` is about the argument itself, not about what is inside it.",
        ),
        (
            "It prints `error: data is not a file` on stderr and exits with `1`: `-f` is true only for a regular file",
            True,
            "Right: `-f` is false for a folder, so `! -f` is true and the error branch runs. `-d` tests for a folder and `-e` for anything that exists (run: exit 1).",
        ),
        (
            "It prints `usage: ./top.sh FILE` and exits with `2`, because a folder is not a valid argument",
            False,
            "The usage test counts arguments, and `data` is one argument. The count is right, so that test passes.",
        ),
        (
            "`-f` accepts the folder, `tail` then fails and `set -e` stops the script with `1`",
            False,
            "`-f` does not accept a folder, so `tail` never runs. The script stops earlier, with its own message.",
        ),
    ],
    """
    `[ ... ]` is a test and its result is an exit code that `if` reads. `-f path` is true for a regular file, `-d path` for a folder and `-e path` for anything that exists; `!` turns the answer round. For `data`, `-f` is false, so `[ ! -f "data" ]` is true and the script prints its own error and leaves with 1. Run for real, `./top.sh data` printed `error: data is not a file` and the exit code was `1`. The spaces inside the brackets matter: `[` is a command and `]` its last argument.
    """,
    "S10 slide 14; labs/10-bash.md exercise 3; run (runs/s10_top.out)",
    "run",
)

mcq(
    "q60", "exam", ["read-code", "predict-output"], 9,
    """
    A folder holds `expenses.csv` (19 lines) and `refunds.csv` (3 lines), and nothing else with a `.csv` ending. The script `count-lines.sh` from slide 14:

    ```bash
    #!/usr/bin/env bash
    for file in *.csv; do
      echo "$file has $(wc -l < "$file") lines"
    done
    ```

    What does `./count-lines.sh` print?
    """,
    [
        (
            "`*.csv has 22 lines`, once, because the loop runs a single time",
            False,
            "The shell expands `*.csv` into the two file names before the loop starts, so the body runs once per file.",
        ),
        (
            "`expenses.csv has 19 expenses.csv lines`, then `refunds.csv has 3 refunds.csv lines`",
            False,
            "That is what you would get with `wc -l \"$file\"`, which prints the name too. With `<` the shell feeds the file to wc and wc has no name to print.",
        ),
        (
            "`expenses.csv has 18 lines`, then `refunds.csv has 2 lines`, because `wc -l` does not count a header",
            False,
            "`wc -l` counts every line, header included. The numbers are 19 and 3.",
        ),
        (
            "`expenses.csv has 19 lines`, then `refunds.csv has 3 lines`",
            True,
            "Right: one line per file, in alphabetical order. `$(...)` is replaced by the output of the command inside it, here just the number.",
        ),
    ],
    """
    `for file in *.csv; do ... done` runs the body once for each name the pattern expands to, with `file` set to that name. `$(wc -l < "$file")` is the output of the command inside it; because the file arrives on stdin through `<`, wc prints only the number (the same lesson as `wc -l < expenses.csv` in session 10's redirection slide). Run for real, the script printed `expenses.csv has 19 lines` and `refunds.csv has 3 lines`. Quote `"$file"`: a file name with a space would otherwise split into two words.
    """,
    "S10 slide 14; run (runs/sample_extra.out)",
    "run",
)

mcq(
    "q61", "core", ["read-code", "read-tool-output"], 9,
    """
    Lab 10b's `top.sh FILE [N]` prints the `N` categories with the most expenses, and `N` is optional. The key lines:

    ```bash
    file="$1"
    top="${2:-3}"
    ...
    tail -n +2 "$file" | cut -d, -f3 | sort | uniq -c | sort -rn | head -n "$top"
    ```

    ```console
    $ ./top.sh expenses.csv
        119 groceries
         86 dining
         76 transport
    $ ./top.sh expenses.csv 5
        119 groceries
         86 dining
         76 transport
         43 entertainment
         32 utilities
    ```

    What does `"${2:-3}"` mean?
    """,
    [
        (
            "The second argument if there is one, otherwise `3`",
            True,
            "Right: `${name:-default}` gives the default when the value is missing. Without a second argument `top` is `3`; with `5` it is `5`.",
        ),
        (
            "The second argument minus 3, which is why `5` prints five lines",
            False,
            "Nothing is subtracted. `5` prints five lines because `top` is `5` and `head -n 5` keeps five.",
        ),
        (
            "The second argument, and the script stops with exit code 3 if it is missing",
            False,
            "The `:-3` supplies a value and stops nothing. Without the second argument the script simply uses `3`.",
        ),
        (
            "The text `3` copied after the second argument, so `5` becomes `53`",
            False,
            "The default is used only when there is no value. With `5` given, `top` is `5`.",
        ),
    ],
    """
    `"${2:-3}"` is the second argument with `3` as a fallback. That is how one script serves both calls in the transcript: with no second argument it keeps the top three, with `5` the top five. The quotes around `"$top"` in the last stage follow the rule of the lesson: always quote. Both runs were checked, and the missing argument `./top.sh` alone still gave the usage message and exit code 2.
    """,
    "labs/10-bash.md exercise 6; run (runs/s10_top.out)",
    "run",
    origin="lab",
)

mcq(
    "q62", "hard", ["read-code", "judgement"], 9,
    """
    Slide 19 shows one trap of `set -e`. This script exits at the `((counter++))` line, silently, and never prints `reached`:

    ```bash
    #!/usr/bin/env bash
    set -e
    counter=0
    ((counter++))
    echo "reached"
    ```

    Why?
    """,
    [
        (
            "`counter` was never declared, and `set -e` stops a script that uses an undeclared variable",
            False,
            "`counter=0` sets it. Variables need no declaration, and catching unset variables is the job of `set -u`.",
        ),
        (
            "`++` is not valid in bash, so the shell reports a syntax error and leaves",
            False,
            "`((counter++))` is valid and it does add one to `counter`. The problem is its exit status, not its syntax.",
        ),
        (
            "`((counter++))` evaluates to the old value, `0`, which counts as false; `set -e` reads that as a failing command and stops",
            True,
            "Right: slide 19. `0` inside `(( ))` is false, so the command exits non-zero, even though `counter` did become 1.",
        ),
        (
            "`counter=0` already failed, because an assignment exits 1 when it stores a zero",
            False,
            "An assignment exits 0. The failing line is the arithmetic command that follows it.",
        ),
    ],
    """
    `((expression))` is a command whose exit status is 0 when the expression is non-zero and 1 when it is zero. `counter++` evaluates to the old value, so with `counter=0` the status is 1 (run: `status=1 counter=1`: the counter did increase). `set -e` treats the 1 as a failing command and stops the script. Use `counter=$((counter + 1))`, which is an expansion, not a command, and is safe (run: `status=0`). The stop itself is what slide 19 and lab 10b exercise 4 describe on Ubuntu's bash; macOS's old bash 3.2 does not stop there.
    """,
    "S10 slide 19; labs/10-bash.md exercise 4; exit statuses run in bash (runs/sample_extra.out)",
    "source",
)

sortq(
    "q63", "core", ["concept", "predict-output"], 7,
    """
    `set -euo pipefail` is three switches. Which letter turns each silent failure into a loud one?
    """,
    [
        ("e", "`-e`"),
        ("u", "`-u`"),
        ("pipefail", "`-o pipefail`"),
    ],
    [
        (
            "A script runs `false`, then `echo after`, and carries on",
            "e",
            "With `-e` the script printed `before`, stopped at `false` and exited 1; `after` never printed (run).",
        ),
        (
            "`echo \"hello $NAME\"` prints `hello` because `NAME` was never set",
            "u",
            "With `-u` the same line printed `./u.sh: line 3: NAME: unbound variable` and exited 1 (run).",
        ),
        (
            "`grep nothing /nonexistent | sort` is reported as success, because `sort` succeeded",
            "pipefail",
            "Without pipefail the pipeline's code is its last stage's: the script reported 0. With it, grep's 2 was reported (run).",
        ),
        (
            "`rm -rf \"$BUILD_DIR/\"` runs on `/` because `BUILD_DIR` is spelt wrong in the script",
            "u",
            "The misspelt name expands to nothing without `-u`. With it, the script stops with `unbound variable` before `rm` runs.",
        ),
        (
            "A failing `uv run ruff check .` must stop `check.sh` before the tests run",
            "e",
            "`-e` ends the script at the first non-zero exit (run: the lint run stopped after the ruff output, exit 1).",
        ),
        (
            "A pipeline's exit code is that of its last stage",
            "pipefail",
            "That is the default. `-o pipefail` changes it: the pipeline fails if any stage fails.",
        ),
    ],
    """
    Slide 16 pairs each letter with one silent failure. `-e`: the script carries on after a failing command. `-u`: a typo in a variable name expands to nothing. `-o pipefail`: a pipeline's code is its last stage's. All three were run: `e.sh` printed `before` and exited 1, `u.sh` printed `NAME: unbound variable`, and the pipeline of `p.sh` reported grep's 2 with pipefail and 0 without it.
    """,
    "S10 slide 16; labs/10-bash.md exercise 5; run (runs/scripts.out, runs/check_lint.out)",
    "run",
)

mcq(
    "q64", "exam", ["read-tool-output", "judgement"], 8,
    """
    You break two tests on purpose and run the v0.5 script (trimmed):

    ```console
    $ scripts/check.sh
    ==> ruff check
    All checks passed!
    ==> ruff format
    9 files already formatted
    ==> mypy
    Success: no issues found in 8 source files
    ==> pytest
    ...
    FAILED tests/test_report.py::test_totals_are_grouped_by_category_and_largest_first
    FAILED tests/test_report.py::test_category_filter[dining-expected0] - Asserti...
    ========================= 2 failed, 42 passed in 0.06s =========================
    $ echo $?
    1
    ```

    What can you conclude?
    """,
    [
        (
            "The failure is in mypy, because the line just before `==> pytest` is mypy's",
            False,
            "That line is `Success: no issues found`: mypy passed. A `==> name` line starts that check; the output under it belongs to it.",
        ),
        (
            "ruff, the format check and mypy passed, pytest failed, and the final `1` is what turns the GitHub step red",
            True,
            "Right: the script stopped at the first failing check, which was the last one. CI reads the exit code, 0 for green and anything else red.",
        ),
        (
            "The `1` counts the failed tests, so CI shows one red cross for each failure",
            False,
            "Two tests failed and the code is still 1. The exit code says only that something failed.",
        ),
        (
            "Nothing can be said about ruff and mypy, because the script stops printing at the first error",
            False,
            "Their own lines are on the screen before pytest started. A check that passed says so.",
        ),
    ],
    """
    The script prints a `==> name` line before each check and then that tool's own output, so you read it from the top. Three checks printed their success lines, and pytest printed two `FAILED` lines and `2 failed, 42 passed`. Because of `set -e`, the script stopped there and left with 1. Slide 18: "That 1 is the red cross on GitHub." Run for real on a copy of the v0.5 tag with two assertions broken, the exit code was 1.
    """,
    "S10 slide 18; run on expense-tracker v0.5 with two tests broken (runs/check_red2.out)",
    "run",
)

mcq(
    "q65", "hard", ["predict-output", "judgement"], 2,
    parts(
        FILE_INTRO,
        """
        Following slide 9, you build a clean copy of the file, but you type `>` on the second line where the recipe has `>>`:

        ```console
        $ head -n 1 expenses.csv > clean.csv
        $ tail -n +2 expenses.csv | sort -u > clean.csv
        $ wc -l < clean.csv
        ```

        What does the last command print, and what is wrong with `clean.csv`?
        """,
    ),
    [
        (
            "`17`: all is well, because `>` adds the lines after the header",
            False,
            "Adding after the header is what `>>` does. That recipe prints 17 (the header and 16 distinct expenses).",
        ),
        (
            "`1`: the sort failed, so only the header was written",
            False,
            "The sort worked. The second `>` then replaced the file with its output, header included in what was lost.",
        ),
        (
            "`16`: the header is gone, because the second `>` emptied the file",
            True,
            "Right: `>` overwrites without asking. The header written by line 1 was replaced, and `clean.csv` now starts with an expense.",
        ),
        (
            "`19`: `sort -u` kept every line of the original",
            False,
            "`sort -u` keeps one copy of each distinct line, so the two duplicate rows collapse: 18 expenses become 16.",
        ),
    ],
    """
    The recipe on slide 9 writes the header with `>` and the distinct rows with `>>`. The second command with `>` empties `clean.csv` before sort's output arrives, so only the 16 distinct rows remain and the header is lost (run: `16`; the correct recipe printed `17`). On the real file the recipe gives 415 lines (the header and 414 distinct expenses), and with `>` it gives 414 and no header. Slide 9: "One > where you meant >> is the shell's rm." Always work on a copy, never the original `expenses.csv`.
    """,
    "S10 slide 9; labs/10-wrangling.md exercise 6; run on the sample file and the real file (runs/sample_extra.out, runs/wrangling.out)",
    "run",
)

mcq(
    "q66", "exam", ["predict-output", "compare"], 5,
    parts(
        FILE_INTRO,
        "Which command prints `3`, the number of expenses made on 7 July?",
    ),
    [
        (
            "`grep 07 expenses.csv | wc -l`",
            False,
            "Every date in the file contains `-07-`, so grep keeps all 18 expenses and wc prints `18`.",
        ),
        (
            "`grep '^2025-07-0' expenses.csv | wc -l`",
            False,
            "This keeps the expenses of the first nine days of July and prints `13`.",
        ),
        (
            "`grep -c ',07,' expenses.csv`",
            False,
            "No field of the file is exactly `07`, so it prints `0`.",
        ),
        (
            "`grep '^2025-07-07' expenses.csv | wc -l`",
            True,
            "Right: `^` anchors the pattern to the start of the line, so only the lines that begin with that date match. Slide 8 uses `grep '^2025-09'` the same way (67 on the real file).",
        ),
    ],
    """
    grep matches anywhere in the line, so a short pattern like `07` matches far too much. Anchoring with `^` means "at the start of the line", and a long pattern that includes the day (`2025-07-07`) leaves only the three expenses of that date: Mercadona twice and Bar Ramon. All four commands were run on the sample file and printed `18`, `13`, `0` and `3`. Slide 8's `grep '^2025-09' expenses.csv | wc -l` counts September 2025 on the real file: 67.
    """,
    "S10 slide 8; labs/10-wrangling.md exercise 4; run on the sample file (runs/sample_extra.out)",
    "run",
)

mcq(
    "q67", "hard", ["read-tool-output", "judgement"], 5,
    """
    Lab 10, exercise 7: how much was spent on groceries? You ask the tracker, then the shell, on the real `expenses.csv`:

    ```console
    $ uv run expenses report --category groceries
    ...
    TOTAL                  6401.78
    $ grep ',groceries,' expenses.csv | cut -d, -f4 | paste -sd+ | bc
    6401.78
    ```

    The two answers agree. Session 8's six exact duplicate rows include three groceries rows (Condis 93.02, Mercadona 90.60 and Lidl 61.85). What does the agreement tell you?
    """,
    [
        (
            "Neither one removes the duplicate rows; putting `sort -u` before the `cut` would give `6156.31`",
            True,
            "Right: both counted all the rows. 6401.78 minus 93.02, 90.60 and 61.85 is 6156.31, the figure the shell gives once the duplicates are dropped (run).",
        ),
        (
            "Both remove the duplicates, so the three groceries rows are counted once each",
            False,
            "If they did, the total would be 6156.31. The `report` command and the pipeline both read every row.",
        ),
        (
            "The pipeline removes duplicates by itself, because `grep` prints each line only once",
            False,
            "grep prints a line as often as it appears. Removing repeats takes `sort -u` or `sort | uniq`.",
        ),
        (
            "The agreement proves that the file has no duplicate groceries rows",
            False,
            "It shows only that both methods read the same rows. The duplicates are there, and both include them.",
        ),
    ],
    """
    `paste -sd+` joins the column of amounts with plus signs and `bc` adds them. The tracker's `report` does not drop duplicates, and neither does the pipeline, so both give 6401.78. Dropping the three duplicate groceries rows takes 245.47 off the total: 6156.31, which the pipeline printed when `sort -u` was added before the `cut` (run). Agreement between two tools is only as good as what they have in common. Lab question 2 is exactly this: does the tracker count the duplicates, and does your pipeline?
    """,
    "labs/10-wrangling.md exercise 7; S8 slide 16 (six duplicates); run on the real expenses.csv at expense-tracker v0.5 (runs/wrangling.out)",
    "run",
    origin="lab",
)

mcq(
    "q68", "beyond", ["read-code", "predict-output"], 5,
    parts(
        FILE_INTRO,
        """
        The lab's stretch exercise asks you to read, not write, one `awk` line. `-F,` splits each line at commas, `NR>1` means "from line 2 on", `$3` is the third column and `$4` the fourth:
        """,
        fence(
            "bash",
            """awk -F, 'NR>1 {sum[$3]+=$4} END {for (c in sum) printf "%s %.2f\\n", c, sum[c]}' expenses.csv | sort -k2 -rn""",
        ),
        "What is the first line of the output?",
    ),
    [
        (
            "`dining 154.56`, the category with the most rows",
            False,
            "dining has the most rows (5) but not the biggest total. The line adds up amounts, not rows.",
        ),
        (
            "`home 342.43`, the category with the biggest total",
            True,
            "Right: home is 91.60 + 250.83. The awk line sums the amount of every row per category, and `sort -k2 -rn` puts the biggest total first.",
        ),
        (
            "`transport 99.12`, the first category in the file",
            False,
            "The output is sorted by the total in column 2, largest first, not by the order of the file.",
        ),
        (
            "`category 0.00`, because the header is read as a category",
            False,
            "`NR>1` skips line 1, so the header never reaches the sum.",
        ),
    ],
    """
    awk reads the file line by line. For every line after the first (`NR>1`) it adds the amount (`$4`) to a running total for the category (`$3`). At the end it prints one `category total` line each, and the pipe sorts them by the second column as numbers, largest first. On the sample file that gives `home 342.43`, then `dining 154.56`; run for real. The category with the most rows (dining) is not the one with the biggest total (home): rows and money are different questions. On the real file groceries leads on both.
    """,
    "labs/10-wrangling.md stretch; run on the sample file and the real file (runs/sample_extra.out, runs/wrangling.out)",
    "run",
    origin="lab",
)

mcq(
    "q69", "core", ["read-tool-output", "concept"], 5,
    """
    Slide 4, on the real `expenses.csv`:

    ```console
    $ wc -l expenses.csv
    421 expenses.csv
    $ tail -n +2 expenses.csv | cut -d, -f3 | sort | uniq | wc -l
    8
    ```

    What does the `8` count?
    """,
    [
        (
            "The categories that appear more than once; a category with a single expense would be left out",
            False,
            "That is what `uniq -d` does. Plain `uniq` keeps one line of every group, repeated or not.",
        ),
        (
            "The expenses in the first category after sorting",
            False,
            "wc counts the lines it receives, and `uniq` has already reduced the category names to one line each.",
        ),
        (
            "The number of different categories",
            True,
            "Right: `cut` keeps the category, `sort` brings equal names together, `uniq` leaves one line per name and `wc -l` counts them.",
        ),
        (
            "The lines of the file that are left after `uniq` removed the duplicate expenses",
            False,
            "`uniq` works on the category names that `cut` produced, not on whole expense rows. That would be 414 or 415.",
        ),
    ],
    """
    The pipeline never sees the other columns: `cut -d, -f3` turns every row into its category name, `sort` groups equal names, `uniq` collapses each group into one line and `wc -l` counts the groups. The answer is 8 different categories (groceries, dining, transport, entertainment, utilities, home, health and education). `tail -n +2` matters: without it the header word `category` is one more line and the pipeline prints 9 (run).
    """,
    "S10 slide 4; labs/10-wrangling.md exercise 3; run on the real expenses.csv (runs/wrangling.out, runs/sample_extra.out)",
    "run",
)

openq(
    "q70", "exam", ["read-code", "read-tool-output", "judgement"], 9,
    parts(
        "A teammate saves a pipeline as `top.sh`:",
        fence("bash", TOP_SH),
        "Three runs, in the folder with the course's `expenses.csv`:",
        fence("console", TOP_RUNS),
    ),
    [
        {
            "label": "1",
            "prompt": "Say in words what the last line of the script does, stage by stage, and what the three lines of output tell you.",
            "marks": 2,
            "model": "`tail -n +2` drops the header, `cut -d, -f3` keeps the category, `sort` puts equal names together, `uniq -c` counts each group, `sort -rn` puts the biggest count first and `head -n 3` keeps three. The output: groceries has the most expenses (119), then dining (86) and transport (76).",
            "rubric": [
                "The stages in order: drop the header, keep the category column, sort, count each group, rank by count, keep the top three",
                "Reads the output: the three categories with the most expenses, and how many each has",
            ],
            "weak": "\"It finds the top three\" says what it is for and skips the stages. Many answers forget that the header is removed first, or say `uniq -c` counts all the duplicates without noting that `sort` must come before it. The output lines are counts of expenses, not euros.",
        },
        {
            "label": "2",
            "prompt": "The two error calls print different messages and different exit codes. What does each test catch, and why does the script use 2 and 1?",
            "marks": 2,
            "model": "The first test catches a call with no argument: the script was used wrongly, so it prints a usage line and exits 2. The second catches an argument that is not a file: the job cannot be done, so it prints an error and exits 1. Both are failures to `&&`, `set -e` and CI, which read the number.",
            "rubric": [
                "Two different problems: no argument (usage) and an argument that is not a file",
                "Any non-zero code is a failure that the next command or CI reads; the number says which kind (2 wrong call, 1 failed job)",
            ],
            "weak": "Answers that say 2 means \"worse\" than 1, or that only 1 is a failure, miss the point: every non-zero number is a failure and the choice is a convention. \"So the user can read it\" ignores that the reader is the next program, not a person.",
        },
        {
            "label": "3",
            "prompt": "Why are both messages written with `>&2`, and what are the quotes in `\"$1\"` for?",
            "marks": 2,
            "model": "`>&2` sends the message to stderr, so `./top.sh nofile > out.txt` leaves `out.txt` empty and the message still reaches the person. The quotes keep a path with a space, such as `Moodle Files/expenses.csv`, as one argument.",
            "rubric": [
                "stderr keeps the message out of redirected output or a pipe, while the person still sees it",
                "Quotes keep a value that contains spaces as a single word",
            ],
            "weak": "\"To show errors in red\" is wrong: stderr has no colour. \"To print it faster\" is not a reason either. Answers about quotes that say they \"make it a string\" miss the spaces: without quotes the shell splits the path into two words.",
        },
    ],
    """
    This is slides 12, 14 and 15 in one script. A strong answer reads the pipeline stage by stage (the same skill as sample question 6), separates the two kinds of error by the problem they catch, and knows that the exit code is what the caller reads. Run for real: `./top.sh nofile > out.txt` printed the error on the screen and `out.txt` had 0 lines, and `./top.sh "Moodle Files/expenses.csv"` worked because the argument is quoted.
    """,
    "S10 slides 12, 14–15; run (runs/s10_top.out)",
    "run",
)

# ===========================================================================
# Sections
# ===========================================================================
SECTIONS = [
    {
        "id": f"{MID}-s1",
        "heading": "Three streams: stdin, stdout and stderr",
        "body_md": md(
            """
            Session 10 (Friday 16 October) had one goal: "Answer a question about real data with one pipeline. Then turn a pipeline into a script." Session 9 had given the two reasons the terminal survived: "It composes. Small programs, joined by pipes" and "It scripts". The session ran in four blocks: pipes and redirection, the wrangling lab on `expenses.csv`, bash scripts with `scripts/check.sh`, and questions about the partial submission. Every output shown in this module was produced by running the command.

            A program started by the shell gets three streams of text:

            | Stream | Number | Carries | By default |
            |---|---|---|---|
            | stdin | 0 | what the program reads | the keyboard |
            | stdout | 1 | the program's result | the terminal |
            | stderr | 2 | messages about problems | the terminal |

            stdout and stderr land in the same window, so they look like one thing. They are two separate channels, and the shell can send each one somewhere different.

            You have already written to stderr. In session 7 the imperative shell of the expense-tracker, `cli.py`, learned to "fail loudly, at the boundary". This is its `report` command at v0.4:

            ```python
                try:
                    expenses = read_expenses(path)
                except (OSError, ValueError):
                    typer.echo(f"could not read {path}", err=True)
                    raise typer.Exit(1) from None
                ...
                for line in format_report(path, category, minimum, totals, largest):
                    typer.echo(line)
            ```

            `err=True` sends the complaint to stderr and `typer.Exit(1)` sets the exit code; the report lines go to stdout. A v0.4 test checks both halves: `test_report_on_a_missing_file_exits_with_one_and_explains_on_stderr` asserts `result.exit_code == 1` and looks for the message in `result.stderr`.

            Why two output streams? stdout is data: the next program in a pipe, or a file, will consume it. If the complaint were mixed into it, a saved report would contain "could not read", and `wc -l` would count the complaint as a line of the report. Result on stdout, complaint on stderr: the data stays clean and the message still reaches a human.

            Programs that read text usually take it from a file name or, when given none, from stdin. That is what makes them easy to join together, which is the subject of the next two sections.
            """
        ),
        "key_points": [
            "Three streams: stdin (what comes in), stdout (the result), stderr (problems). stdout and stderr both show in the terminal by default.",
            "`typer.echo(..., err=True)` writes to stderr; plain `typer.echo(line)` writes to stdout.",
            "Result on stdout, complaint on stderr: the data stays clean and the message still reaches you.",
        ],
        "exam_note_md": "Expect a transcript where output was redirected or piped and a message still appears on the screen. The answer is always: which stream did the program write it to?",
        "source_ref": "S10 slides 2 and 5; S9 slides 6 and 24; S7 slide 19; S8 slide 21; expense-tracker v0.4 cli.py and tests/test_io.py",
        "check": [f"{MID}-q01", f"{MID}-q02", f"{MID}-q49"],
    },
    {
        "id": f"{MID}-s2",
        "heading": "Redirection: >, >>, <, 2>, 2>&1 and /dev/null",
        "body_md": md(
            """
            Redirection tells the shell where a stream should go before the program starts. The program does not choose: it writes to stdout or stderr as usual.

            | You type | stdout goes to | stderr goes to |
            |---|---|---|
            | `cmd > out.txt` | `out.txt`, replacing what was there | the terminal |
            | `cmd >> out.txt` | the end of `out.txt` | the terminal |
            | `cmd 2> err.txt` | the terminal | `err.txt` |
            | `cmd > all.txt 2>&1` | `all.txt` | wherever stdout goes: `all.txt` |
            | `cmd 2> /dev/null` | the terminal | discarded |

            `<` works the other way round: `wc -l < expenses.csv` makes the file the program's stdin. `wc -l expenses.csv` opens the file itself and prints the count and the name: `421 expenses.csv` on the course's file. With `<` wc only sees text arriving, so it prints just `421`.

            Here is the trap, run on the real project:

            ```console
            $ uv run expenses report > report.txt
            $ echo $?
            0
            $ head -n 3 report.txt
            Expense report for expenses.csv
            ----------------------------------------
            groceries              6401.78
            $ uv run expenses report nosuch.csv > report.txt
            could not read nosuch.csv
            $ echo $?
            1
            $ wc -l < report.txt
            0
            ```

            Two things happened. The message appeared on the screen although stdout went to the file: it was written to stderr. And the good report from the first command is gone. For `>` the shell opens the file and empties it before the program even starts; the program then failed and wrote nothing to stdout, so `report.txt` has zero lines. With `>>` the old report would have survived, and any new output would have been added at the end.

            `/dev/null` is a special file that swallows whatever is written to it. It hides the output and leaves the failure:

            ```console
            $ uv run expenses report nosuch.csv 2> /dev/null
            $ echo $?
            1
            ```

            Nothing on the screen, but the exit code is still 1, so `&&`, a script with `set -e` and CI still see a failure. You have only lost the reason.

            Tools differ in which stream they use for what. ruff, mypy and pytest print their findings on stdout, so `uv run ruff check . > /dev/null` shows nothing at all and still exits 1. uv prints its progress lines (`Creating virtual environment at: .venv`) on stderr, so they stay on the screen.

            **Never edit the original.** Slide 9 and lab 10 work on a copy (`cp ~/code/expense-tracker/expenses.csv ~/lab10/`), because `expenses.csv` is the fixture every session uses. Building a clean copy puts `>` and `>>` side by side, on the real file:

            ```console
            $ head -n 1 expenses.csv > clean.csv
            $ tail -n +2 expenses.csv | sort -u >> clean.csv
            $ wc -l clean.csv
            415 clean.csv
            ```

            `>` starts `clean.csv` with the header, and `>>` adds the 414 distinct expenses after it. The slide's warning is that one `>` where you meant `>>` is the shell's `rm`: with `>` on the second line the header is overwritten and `clean.csv` has 414 lines and no header.
            """
        ),
        "key_points": [
            "`>` replaces the file, and empties it before the command runs, even if the command then fails.",
            "`>>` appends; `<` feeds a file to the program's stdin.",
            "`2>` redirects stderr; `2>&1` sends stderr wherever stdout is going.",
            "`/dev/null` hides the message, never the exit code.",
            "Never edit the original: work on a copy; one `>` where you meant `>>` is the shell's `rm`.",
        ],
        "exam_note_md": "Typical judgement: a report overwritten by `>`, or a message that escaped the redirection. Name the stream and the operator.",
        "source_ref": "S10 slides 4, 5, 9; run on expense-tracker v0.4 (runs/r1.out, r2.out, c1.out, l2.out)",
        "check": [f"{MID}-q03", f"{MID}-q04", f"{MID}-q42"],
    },
    {
        "id": f"{MID}-s3",
        "heading": "The pipe: small programs, composed",
        "body_md": md(
            """
            The pipe `|` connects two programs: the stdout of the one on the left becomes the stdin of the one on the right. No file is written in between. This is the "composes" of session 9's slide: each program does one small job, and you build the answer by joining them, the same idea as one function, one job in session 6.

            The teacher's sample question 6 is a pipe:

            ```bash
            grep "food" expenses.csv | wc -l
            ```

            Read it left to right and ask, at each `|`, what text is flowing. `grep` prints every line of `expenses.csv` that contains `food`. Those lines do not reach the screen; they go down the pipe into `wc -l`, which counts the lines it receives and prints one number. So the command prints the number of lines that contain food: not the number of times the word appears, and not the lines themselves. (The real `expenses.csv` has no `food` category, so there the answer is `0`; the question is about what the command does.)

            Slide 4 shows the idea on the real file. `wc -l expenses.csv` prints `421 expenses.csv` (a header and 420 expenses), and one pipeline answers another question: `tail -n +2 expenses.csv | cut -d, -f3 | sort | uniq | wc -l` prints `8`, the number of different categories. Each program does one thing, and `|` sends what the left one prints into the right one. That is the Unix idea, fifty years old.

            On this module's sample file:

            ```console
            $ grep dining expenses.csv
            2025-07-03,Can Recasens,dining,33.02
            2025-07-03,Can Recasens,dining,33.02
            2025-07-06,Sushi at home,dining,24.90
            2025-07-07,Bar Ramon,dining,9.80
            2025-07-10,Federal Cafe,dining,53.82
            $ grep dining expenses.csv | wc -l
            5
            ```

            Only stdout travels through the pipe. stderr still goes straight to the terminal:

            ```console
            $ uv run expenses report nosuch.csv | wc -l
            could not read nosuch.csv
            0
            ```

            The message is on the screen because the program wrote it to stderr; wc received an empty stdout and counted 0 lines. If you really want errors in the pipe, `2>&1` joins them to stdout first: `uv run expenses report nosuch.csv 2>&1 | wc -l` prints `1`.

            A pipeline can have many stages. Each stage sees only the previous stage's output, never the original file, so a mistake early on (a header left in, an unsorted list) flows all the way to the end. The pipeline stepper in this module shows every intermediate output: predict each one before you reveal it.
            """
        ),
        "key_points": [
            "`a | b`: the stdout of a becomes the stdin of b.",
            "`grep x file | wc -l` counts lines that contain x, not occurrences of x.",
            "stderr skips the pipe and goes to the terminal; `2>&1` joins it in.",
            "Each stage sees only the previous stage's output.",
        ],
        "exam_note_md": "Sample Q6 is exactly this shape: say what the last program prints, given what the first one sends it.",
        "source_ref": "S10 slide 4; S9 slide 6; midterm sample Q6; run (pipelines_run.log, runs/r2.out, runs/r6.out, runs/wrangling.out)",
        "check": [f"{MID}-q06", f"{MID}-q07"],
    },
    {
        "id": f"{MID}-s4",
        "heading": "The text tools on expenses.csv",
        "body_md": md(
            """
            Every tool below reads lines of text (from a file name, or from stdin) and writes lines of text. The exam rule is "judgement, not memorised flags": a flag may appear in a command you are shown, and the question is what the command does. What you need is what each tool does to the lines.

            This module's sample file has the same header and columns as the real one, 18 expenses in the course's eight categories, and three traps built in. Its first lines:

            ```console
            $ head -n 3 expenses.csv
            date,merchant,category,amount
            2025-07-01,Cabify,transport,36.25
            2025-07-01,Lidl,groceries,56.77
            ```

            | Tool | What it does | On the sample file |
            |---|---|---|
            | `head -n 3`, `tail -n 3` | first 3 lines, last 3 lines | `tail -n +2` means from line 2 on: it drops the header |
            | `grep dining` | lines that contain `dining` anywhere | 5 lines |
            | `grep -c dining` | how many lines match | `5` |
            | `grep -v dining` | lines that do not match | 14 lines: 13 expenses and the header |
            | `wc -l` | counts lines | `19 expenses.csv` |
            | `cut -d, -f3` | the 3rd comma-separated field of each line | the category column, header word included |
            | `sort` | text order, character by character | `-n` numeric, `-r` reversed, `-rn` largest number first |
            | `uniq` | collapses identical neighbouring lines into one | `-c` adds counts, `-d` shows only repeated lines |
            | `sort -t, -k4 -rn` | sorts whole lines on column 4 (`-t,` is the separator), as numbers, largest first | the biggest expenses first |
            | `sort -u` | sorts and keeps one copy of each distinct line | the same as `sort \\| uniq` |
            | `grep '^2025-09'` | lines that start with the text (`^` is the start of the line) | the expenses of September 2025: 67 on the real file |
            | `find . -name "*.csv"` | files whose name matches, anywhere below `.` | `./expenses.csv` and, after `expenses add`, `./data/expenses.csv` |

            Three facts cause almost every wrong answer.

            **grep matches anywhere in the line.** It knows nothing about columns. `grep home` finds the two home expenses and also `2025-07-06,Sushi at home,dining,24.90`, so `grep home expenses.csv | wc -l` prints `3`. A pattern can also hit the header, or miss it: `grep -v dining` keeps the header because it contains no `dining`. Matching the whole field, commas included, avoids the merchant trap: `grep ,home, expenses.csv | wc -l` prints `2`.

            **sort is text order unless told otherwise.** As text, `137.97` comes before `14.20`, and `9.80` comes after `250.83`, because characters are compared one at a time and `9` sorts after `2`. Numbers need `-n`.

            **uniq only compares a line with the one just before it.** Two identical lines with something in between are not repeated as far as uniq can tell. That is why the habit is `sort` first, then `uniq`.
            """
        ),
        "key_points": [
            "grep finds lines that contain the text anywhere: merchant names and the header included.",
            "`grep -c x file` and `grep x file | wc -l` print the same number: matching lines.",
            "sort compares text; `-n` compares numbers.",
            "uniq collapses only neighbouring duplicates, so sort first.",
        ],
        "exam_note_md": "The traps are the point: a merchant called Sushi at home, a header line, amounts with different numbers of digits.",
        "source_ref": "S10 slides 6–8; lab 09 exercise 4; midterm sample Q6; run (pipelines_run.log)",
        "check": [f"{MID}-q08", f"{MID}-q10", f"{MID}-q44"],
    },
    {
        "id": f"{MID}-s5",
        "heading": "Asking questions of expenses.csv",
        "body_md": md(
            """
            Text wrangling means answering a question about the data by joining small tools. The same five questions come back again and again. Here they are on the sample file, each run for real.

            **How many dining expenses?** `grep -c ,dining, expenses.csv`, or `grep ,dining, expenses.csv | wc -l`: `5`.

            **How many expenses in each category?**

            ```console
            $ tail -n +2 expenses.csv | cut -d, -f3 | sort | uniq -c | sort -rn
                  5 dining
                  4 groceries
                  3 transport
                  2 home
                  1 utilities
                  1 health
                  1 entertainment
                  1 education
            ```

            Skip the header, keep the category column, sort so equal names sit together, count each group, then put the biggest count first.

            **What are the largest amounts?** `tail -n +2 expenses.csv | cut -d, -f4 | sort -rn | head -n 3` prints `250.83`, `137.97`, `91.60`.

            **Which rows are exact duplicates?** `sort expenses.csv | uniq -d` prints the two duplicated rows of the sample file. On the real file, `sort expenses.csv | uniq -d | wc -l` prints `6`: the "six exact duplicates" of session 8, which is why `remove_duplicates` takes 420 expenses down to 414.

            **How many lines are expenses?** `tail -n +2 expenses.csv | wc -l` prints `18`; `wc -l` alone counts the header too and says `19`.

            Each recipe has a broken twin that gives a believable wrong number.

            **Header left in.** A category called `category`, the word `amount` at the top of a reversed text sort, every whole-file line count one too high. Start at line 2.

            **uniq without sort.** On the real file:

            ```console
            $ uniq -d expenses.csv | wc -l
            5
            $ sort expenses.csv | uniq -d | wc -l
            6
            ```

            The two `2025-11-29,Condis,groceries,93.02` rows are lines 351 and 354, with other rows between them, so uniq never sees them side by side.

            **Text sort.** `cut -d, -f4 expenses.csv | sort -r | head -n 3` prints `amount`, `91.60`, `9.80`. Drop the header and use `sort -rn`.

            **Pattern too loose.** `grep home` also counts Sushi at home. Match `,home,`.

            **A comma inside a field.** One step beyond the sample file: `add` writes with Python's `csv` module, which puts quotes around a merchant name that contains a comma, as in `2025-12-31,"Can Recasens, Gracia",dining,33.02`. `cut -d,` splits at every comma, quotes or not, so that row's third field is ` Gracia"`; the program's `csv.reader` reads it correctly. Pipelines are quick answers on simple files; when a field can contain the separator, trust the tested code.

            Slides 7 and 8 run the recipes on the real file:

            ```console
            $ tail -n +2 expenses.csv | cut -d, -f3 | sort | uniq -c | sort -rn | head -n 3
                119 groceries
                 86 dining
                 76 transport
            $ grep -c ',dining,' expenses.csv
            86
            $ grep '^2025-09' expenses.csv | wc -l
            67
            $ tail -n +2 expenses.csv | sort | uniq -d
            2025-08-19,Bar Alegria,dining,52.71
            2025-11-07,Renfe,transport,52.24
            2025-11-10,Movistar,utilities,69.10
            2025-11-29,Condis,groceries,93.02
            2025-11-29,Mercadona,groceries,90.60
            2025-12-23,Lidl,groceries,61.85
            ```

            The `^` in `'^2025-09'` means "at the start of the line", so only dates in September 2025 match. The lab adds more recipes, all run on the real file: distinct merchants with `cut -d, -f2 | sort -u | wc -l` (33); the five biggest expenses with `sort -t, -k4 -rn | head -n 5` (all `home`, the first `2025-11-17,Ferreteria Mas,home,296.49`); the month with most expenses with `cut -c1-7 expenses.csv | sort | uniq -c | sort -rn | head -n 1` (`2025-11`, 85 rows); and the total spent on groceries, `grep ',groceries,' expenses.csv | cut -d, -f4 | paste -sd+ | bc`, which prints `6401.78`, the same as `uv run expenses report --category groceries`. Neither the report nor the pipeline removes duplicates: put `sort -u` before the `cut` and the shell gives `6156.31`.

            The lab's stretch is to read one `awk` line, not to write it: `awk -F, 'NR>1 {sum[$3]+=$4} END {for (c in sum) printf "%s %.2f\\n", c, sum[c]}' expenses.csv | sort -k2 -rn`. `-F,` splits at commas, `NR>1` skips the header, `$3` is the category and `$4` the amount, so it prints the total per category, biggest first. On the real file that is `groceries 6401.78`, the same category that has the most rows.

            When a pipeline gives you a number, check it against something you already know: the file has 18 expenses; session 8 says six duplicates. A number that disagrees is a bug to explain before you report anything.
            """
        ),
        "key_points": [
            "Per category: skip the header, cut the column, sort, `uniq -c`, `sort -rn`.",
            "Duplicates: `sort | uniq -d`; on the real file that is 6, matching session 8.",
            "The four classic bugs: header left in, uniq without sort, text sort, a pattern that matches too much.",
            "Check every number against something you know before you believe it.",
            "The real file (slides 4 to 9): 421 lines, 8 categories, groceries 119, dining 86, transport 76, six duplicate rows, 415 lines in `clean.csv`.",
        ],
        "exam_note_md": "Open questions of the explain-the-bug kind: a pipeline, its wrong output, and the right number. Name the cause and describe the fix in words.",
        "source_ref": "S8 slides 11, 13 and 16 (six duplicates, 420 and 414); expense-tracker expenses.csv and v0.4 cli.py (csv.writer); S10 slides 4 and 6–8; labs/10-wrangling.md; run (pipelines_run.log, runs/r5.out, runs/wrangling.out; pipes-bash-fix/runs/comma.out)",
        "check": [f"{MID}-q13", f"{MID}-q15", f"{MID}-q18"],
    },
    {
        "id": f"{MID}-s6",
        "heading": "Exit codes and chaining: $?, &&, || and ;",
        "body_md": md(
            """
            Session 5: "0 means success; anything else means failure." Every command leaves a number behind, and `echo $?` shows the last one. "Every tool downstream reads that number: the shell, `&&`, CI. A program that prints an error and exits 0 is a program that lies."

            grep uses three values, and the middle one surprises people:

            ```console
            $ grep clothing expenses.csv
            $ echo $?
            1
            $ grep dining nosuch.csv
            grep: nosuch.csv: No such file or directory
            $ echo $?
            2
            ```

            `0` means it found at least one line, `1` means it ran fine and found nothing, `2` means trouble such as a missing file. For the shell, 1 is still not 0, so a script treats "no match" as a failure. That matters in the next section.

            Three operators join commands on one line:

            - `a && b`: b runs only if a exited 0. Run the next check only if this one passed.
            - `a || b`: b runs only if a exited non-zero. Print a fallback message.
            - `a ; b`: b runs regardless.

            The line's exit code is that of the last command that ran.

            ```console
            $ uv run expenses report nosuch.csv && echo "report ok" || echo "report failed"
            could not read nosuch.csv
            report failed
            ```

            The partial rubric's "Check yourself" chains its four checks with `&&`, so the first failing check stops the line and the line exits non-zero. Written with `;`, every check runs whatever happens, and the exit code is the last command's: a lint error followed by passing tests exits 0, and anything that trusts the exit code sees green.

            A pipeline has one exit code too: by default, the last command's.

            ```console
            $ grep clothing expenses.csv | wc -l
            0
            $ echo $?
            0
            $ set -o pipefail
            $ grep clothing expenses.csv | wc -l
            0
            $ echo $?
            1
            ```

            wc happily counted zero lines and exited 0, hiding grep's 1. With `pipefail` the pipeline fails if any stage fails. Notice the two zeros in the first run: the `0` on the screen is wc's output, the `0` from `echo $?` is the exit code. They are different things.
            """
        ),
        "key_points": [
            "0 is success, anything else is failure; `echo $?` shows the last exit code.",
            "grep exits 1 when it finds nothing; the shell counts that as a failure, though nothing crashed.",
            "`&&` next only on success, `||` next only on failure, `;` next regardless.",
            "A pipeline's exit code is the last command's, unless `pipefail` is on.",
        ],
        "exam_note_md": "Expect to predict which commands in a chain ran and what `$?` is at the end, or to spot the `;` that allows a red check to pass.",
        "source_ref": "S5 slide 9; S10 slides 15–16; partial rubric 'Check yourself'; run (runs/r2.out, runs/r4.out, runs/c1.out)",
        "check": [f"{MID}-q19", f"{MID}-q20", f"{MID}-q43"],
    },
    {
        "id": f"{MID}-s7",
        "heading": "Bash scripts: shebang, variables, quoting and set -euo pipefail",
        "body_md": md(
            """
            Session 9: "It scripts. Whatever you typed once, you can save and run again." A bash script is a text file of commands, run from top to bottom: slide 12 calls it a pipeline saved for re-running.

            ```bash
            #!/usr/bin/env bash
            set -euo pipefail

            file="$1"
            echo "Dining expenses in $file:"
            grep dining "$file" | wc -l
            ```

            **The shebang.** The first line says which program runs the file: `env` finds `bash` for you. It matters when you run the file itself.

            **Running it.** `./count.sh expenses.csv` asks the system to run the file, which needs the x bit: `chmod +x count.sh` once, or you get `Permission denied` (session 9: "No x, no run"). The slide shows zsh's wording, `permission denied: ./hello.sh`; bash on Ubuntu says `bash: ./hello.sh: Permission denied`. Same cause, same fix: the x bit. `bash count.sh expenses.csv` runs the bash program and hands it the file to read, so no x bit is needed. That is how session 3 ran `bash scripts/setup-check.sh`.

            **Variables.** `file="$1"` stores the first argument; `"$@"` stands for all the arguments, each kept whole. There are no spaces around `=`: `CATEGORY = dining` makes bash look for a program called `CATEGORY` and print `CATEGORY: command not found`.

            **Quoting.** Always write `"$file"`, not `$file`. Without quotes, bash splits the value at spaces. Your own course folder, `Moodle Files`, shows why. Here is an earlier version of the script, with `grep dining $file` (no quotes) and no `set` line:

            ```console
            $ ./count.sh "Moodle Files/expenses.csv"
            Dining expenses in Moodle Files/expenses.csv:
            grep: Moodle: No such file or directory
            grep: Files/expenses.csv: No such file or directory
            0
            ```

            grep received two file names that do not exist. Worse, that version still printed 0 and exited 0, because nothing told it to stop.

            **The safety line.** Without a `set` line a script runs every line whatever happens, like commands joined by `;`, and exits with its last command's code: a final `echo` makes it exit 0 after a failed check. `set -e` stops the script at the first command that exits non-zero. `set -u` makes reading an unset variable an error instead of an empty string. `set -o pipefail` makes a pipeline fail when any stage fails. Together they turn silent wrong answers into loud failures: session 7's "fail loudly", for scripts. Slide 16 sets them side by side:

            | Letter | Without it | With it |
            |---|---|---|
            | `-e` | the script carries on after a failing command | it stops at the first failure |
            | `-u` | a `$NAME` typo expands to nothing | `Error: unbound variable` |
            | `-o pipefail` | the pipeline's code is its last stage's | it fails if any stage fails |

            ```console
            $ ./u.sh
            ./u.sh: line 3: NAME: unbound variable
            ```

            There is one catch. With `set -e`, a grep that finds nothing (exit 1) stops the script:

            ```console
            $ ./monthly.sh expenses.csv
            Report for expenses.csv
            $ echo $?
            1
            ```

            `monthly.sh` ran `clothing=$(grep -c clothing "$file")`. `$( )` runs the command inside it and stores what it prints, here `0`, in the variable; the line then has grep's exit code. The file has no clothing, so grep exited 1 and the script stopped without a word. If "no match" is a normal answer on that line, say so with `|| true` at the end of it: `true` is a command that does nothing and exits 0, so the line succeeds either way.
            """
        ),
        "key_points": [
            "`#!/usr/bin/env bash` picks the interpreter; `./script.sh` needs the x bit, `bash script.sh` does not.",
            "`NAME=value` with no spaces; `\"$1\"` is the first argument, `\"$@\"` all of them.",
            "Quote every `\"$var\"`: paths have spaces.",
            "`set -euo pipefail`: stop on a failure, on an unset variable, and on a failing pipeline stage.",
        ],
        "exam_note_md": "You will read a short script and its output and say why it misbehaved: a missing quote, a `;`, a missing `set -e`, or `set -e` meeting a grep that found nothing.",
        "source_ref": "S9 slides 6, 18–19 and 24; S3 slide 9; S10 slides; run (runs/s1.out, runs/s2.out; pipes-bash-fix/runs/perm.out, monthly.out, nosete-test.out)",
        "check": [f"{MID}-q23", f"{MID}-q24", f"{MID}-q26"],
    },
    {
        "id": f"{MID}-s9",
        "heading": "Scripts that take arguments: conditions, loops and exit codes",
        "body_md": md(
            """
            Slide 12: a script is saving a pipeline for re-running. `top.sh` takes the file as its first argument, `"$1"`, and runs the pipeline of slide 7 on it:

            ```console
            $ chmod +x top.sh
            $ ./top.sh expenses.csv
                119 groceries
                 86 dining
                 76 transport
            ```

            Three variables describe the call: `$1` is the first argument, `$#` is how many arguments there are, and `$0` is the script's own name as you typed it. A script should check its input before it trusts it, with `if` and a test in square brackets:

            ```bash
            if [ "$#" -lt 1 ]; then
              echo "usage: $0 FILE" >&2
              exit 2
            fi
            if [ ! -f "$1" ]; then
              echo "error: $1 is not a file" >&2
              exit 1
            fi
            ```

            `-lt` is "less than" for numbers. `-f` is true for a regular file, `-d` for a folder and `-e` for anything that exists; `!` turns the answer round. Spaces inside `[ ]` are required. `>&2` sends the message to stderr, so it is not mixed into the output, and `exit` sets the exit code (slide 15):

            ```console
            $ ./top.sh; echo $?
            usage: ./top.sh FILE
            2
            $ ./top.sh nofile; echo $?
            error: nofile is not a file
            1
            ```

            "0 means success. Anything else is failure." The script uses 2 for a call made wrongly and 1 for a job that failed, and CI reads only the number.

            A `for` loop repeats a command for each name a pattern expands to, and `$(...)` is replaced by the output of a command:

            ```bash
            for file in *.csv; do
              echo "$file has $(wc -l < "$file") lines"
            done
            ```

            Lab 10b adds `"${2:-3}"` (the second argument, or 3 when there is none), a `while` loop and `[ -d data ]` for a folder. The last trap of the session: under `set -e`, `((counter++))` evaluates to the old value, `0`, which `-e` reads as failure, and the script stops silently. Use `counter=$((counter + 1))`. Functions and `trap` were skipped on purpose and are not examined.
            """
        ),
        "key_points": [
            "`$1` is the first argument, `$#` the number of arguments, `$0` the script's name; quote `\"$1\"`.",
            "`if [ \"$#\" -lt 1 ]` and `[ ! -f \"$1\" ]` check the input; `-f` file, `-d` folder, `-e` exists.",
            "Errors go to `>&2`; exit 2 for a wrong call, exit 1 for a failed job. 0 is success, anything else is failure, and CI reads the number.",
            "`for file in *.csv; do ... done` and `$(...)` (the output of a command).",
            "Under `set -e`, `((counter++))` stops the script when the counter is 0. Use `counter=$((counter + 1))`.",
        ],
        "exam_note_md": "Expect a short script and several calls: say what is printed, to which stream, and what `echo $?` shows. Know why the two errors use different codes, and the one `set -e` trap.",
        "source_ref": "S10 slides 12–15 and 19; labs/10-bash.md exercises 2–4 and 6; run (runs/s10_top.out, runs/scripts.out, runs/sample_extra.out)",
        "check": [f"{MID}-q57", f"{MID}-q59", f"{MID}-q62"],
    },
    {
        "id": f"{MID}-s8",
        "heading": "scripts/check.sh for v0.5, and CI is a terminal",
        "body_md": md(
            f"""
            The partial submission is marked at the `v0.5` tag, due Sunday 18 October, and "CI must be green on the tagged commit, or tests is capped at 1". The rubric's "Check yourself" gives one command:

            ```bash
            {RUBRIC_LINE.replace(chr(10), chr(10) + "            ")}
            ```

            In session 10 the class wrote `scripts/check.sh` from it: the same four commands, one per line, each preceded by an `echo` that names it (slide 17).

            ```bash
            {CHECK_SH.replace(chr(10), chr(10) + "            ")}
            ```

            Lint, formatting (checked, not rewritten), types (strict, `src` and `tests`) and tests. `set -euo pipefail` gives the same stop-at-the-first-failure as the `&&` chain, and the `==>` lines show which check is running. Slide 18 shows a green run (trimmed, run at the v0.5 tag), ending with the exit code:

            ```console
            $ scripts/check.sh
            ==> ruff check
            All checks passed!
            ==> ruff format
            9 files already formatted
            ==> mypy
            Success: no issues found in 8 source files
            ==> pytest
            ...
            ============================== 44 passed in 0.05s ==============================
            $ echo $?
            0
            ```

            "Break a test and run it again: it stops at pytest, prints the failure, and exits 1. That 1 is the red cross on GitHub." With an unused import it stops earlier, at the first check:

            ```console
            $ ./scripts/check.sh
            ==> ruff check
            {RUFF_F401.replace(chr(10), chr(10) + "            ")}
            $ echo $?
            1
            ```

            The format check, mypy and pytest never ran. You know about the lint problem and nothing else yet.

            **CI is a terminal.** Session 9: "The check workflow is a list of commands someone else's computer types for you." The steps of `.github/workflows/check.yml`, mapped to your own terminal:

            | CI step | What you would type |
            |---|---|
            | Check out the code | `git clone` |
            | Install uv (and Python 3.13) | install uv, once |
            | Install dependencies from the lockfile | `uv sync --locked` |
            | Lint, Formatting, Types, Tests | the four commands of `check.sh` |

            Each `run:` line is typed on a fresh Ubuntu machine. A step that exits non-zero turns red, and by default the steps after it are skipped, just like `&&`. Slide 21 says `scripts/check.sh` is what CI runs and that exit code 0 is green. In the course repository the workflow lists the four checks as separate named steps (a commit that replaced them with one `scripts/check.sh` step was reverted, because a single step does not say which check failed), and `check.sh` stays for running the same checks before a push. Either way the rule is the same: CI reads the exit code. It is also the answer to the rubric's README criterion, which asks for "how to run the checks": one copy-pasteable line, `./scripts/check.sh`.

            Two things `check.sh` does not cover. It does not run `uv sync --locked`, and locally `uv run` quietly updates `uv.lock` when you change something the lockfile records, such as the version or a dependency, so commit `uv.lock` too. And it needs the x bit. On WSL under `/mnt/c`, chmod "silently does nothing" (session 9); in your Linux home, run `chmod +x scripts/check.sh` and commit. Git records the mode:

            ```diff
            diff --git a/scripts/check.sh b/scripts/check.sh
            old mode 100644
            new mode 100755
            ```
            """
        ),
        "key_points": [
            "`check.sh` is the rubric's four checks in one command, each named by an `echo \"==> ...\"`; exit code 0 is green, 1 is red. Run it before `git tag -a v0.5`.",
            "`set -e` or `&&`: stop at the first red check and exit non-zero.",
            "CI is a terminal: each step is a command; a non-zero exit turns it red and the rest are skipped.",
            "Commit the x bit (mode 100755) and `uv.lock`: `check.sh` checks neither.",
        ],
        "exam_note_md": "Expect `check.yml` or a CI log next to a script: say which steps ran, why the run is red, and what you do before moving the tag.",
        "source_ref": "S10 slides 17–18 and 21; expense-tracker v0.5 scripts/check.sh and .github/workflows/check.yml; partial-rubric.txt (Check yourself, CI gate, README criterion); S9 slides 3, 6 and 20; lab 01 §8; run (runs/check_clean.out, runs/check_lint.out, runs/check_red2.out, runs/g1.out, runs/l2.out; pipes-bash-fix/runs/lock.out)",
        "check": [f"{MID}-q30", f"{MID}-q31", f"{MID}-q33"],
    },
]

# ===========================================================================
# Terms, traps, flashcards
# ===========================================================================
TERMS = [
    ("stdin", "Standard input (stream 0): the text a program reads. The keyboard by default; `<` or a pipe can make it a file or another program's output.", 1),
    ("stdout", "Standard output (stream 1): where a program writes its result. The terminal by default; `>`, `>>` and `|` send it elsewhere.", 1),
    ("stderr", "Standard error (stream 2): where a program writes messages about problems, as `typer.echo(..., err=True)` does. It still reaches the terminal when stdout is redirected or piped.", 1),
    ("Redirection", "Telling the shell where a stream goes: `>` replace a file, `>>` append, `<` read from a file, `2>` send stderr, `2>&1` send stderr wherever stdout goes.", 2),
    ("/dev/null", "A special file that discards whatever is written to it. Hides output; never changes the exit code.", 2),
    ("Pipe", "`|`: connects the stdout of the command on its left to the stdin of the command on its right. Small programs, composed.", 3),
    ("Pipeline", "Commands joined by pipes. Each stage sees only the previous stage's output; the exit code is the last command's unless `pipefail` is on.", 3),
    ("grep", "Prints the lines that contain a pattern anywhere in the line; `-c` counts them, `-v` keeps the others. Exits 0 (found), 1 (nothing found) or 2 (trouble).", 4),
    ("cut", "`cut -d, -f3` prints one comma-separated field of every line: the category column of `expenses.csv`, header word included.", 4),
    ("sort", "Orders lines as text, character by character; `-n` compares numbers, `-r` reverses.", 4),
    ("uniq", "Collapses identical neighbouring lines into one; `-c` adds counts, `-d` prints only repeated lines. Neighbours only, hence `sort` first.", 4),
    ("Exit code", "The number a program leaves when it ends: 0 success, anything else failure. `echo $?` shows the last one; `&&`, `set -e` and CI read it.", 6),
    ("Chaining (&&, ||, ;)", "`a && b` runs b only if a succeeded, `a || b` only if a failed, `a ; b` always. The line's exit code is the last command's that ran.", 6),
    ("Shebang", "The first line of a script, `#!/usr/bin/env bash`: which program runs the file when you start it as `./script.sh`.", 7),
    ("Execute permission (x bit)", "Without it, `./script.sh` says `Permission denied`. `chmod +x` adds it, and git records it as mode 100755 when you commit.", 7),
    ("Quoting", "`\"$file\"` keeps a variable's value as one word even when it contains spaces; unquoted, bash splits it.", 7),
    ("set -euo pipefail", "The safety line of a script: stop at the first failing command (`-e`), treat unset variables as errors (`-u`), fail a pipeline if any stage fails (`pipefail`).", 7),
    ("scripts/check.sh", "v0.5's one-command check, written in session 10: under `set -euo pipefail`, an `echo \"==> name\"` and then `ruff check`, `ruff format --check`, `mypy src tests` and `pytest`. Exit code 0 is green, 1 is red. The same four commands CI runs; run it before tagging.", 8),
    ("CI is a terminal", "Session 9: the check workflow is a list of commands someone else's computer types for you. A non-zero exit turns a step red and skips the rest.", 8),
]

TRAPS = [
    "`grep dining expenses.csv | wc -l` counts how many times the word appears. It counts lines that contain it; `grep -c dining` prints the same number.",
    "grep looks in the category column. It looks anywhere in the line: `grep home` also finds `Sushi at home`, and patterns can match (or miss) the header. Match `,home,` when you mean the field.",
    "`uniq` removes all duplicate lines. It only compares a line with the one before it; on the real file `uniq -d` finds 5 of the 6 duplicates. Sort first.",
    "`sort` puts amounts in order. By default it compares text, so `9.80` comes after `250.83`. Use `sort -n` (or `-rn`), and drop the header.",
    "If the command fails, `> report.txt` leaves the old file alone. The shell empties the file before the command starts, so a failed run leaves it empty. `>>` appends instead.",
    "Redirecting with `>` captures error messages too. It captures stdout only; messages on stderr still reach the screen, which is why you see `could not read nosuch.csv`.",
    "`;` and `&&` are interchangeable in a check script. With `;` every check runs and the exit code is the last command's, so a lint error followed by passing tests exits 0.",
    "A pipeline fails when any of its commands fails. By default its exit code is the last command's (wc exits 0 after counting nothing); `set -o pipefail` changes that.",
    "grep exiting 1 means something broke. It means no line matched. Under `set -e` that still stops the script, without a message.",
    "A script stops at the first error by itself. Without `set -e` it runs every line and exits with the last command's code; a final `echo \"Ready to tag\"` makes it exit 0 after a failed check.",
    "An unset variable in a script is harmless. Without `set -u` it silently becomes empty: a misspelt `$OUPUT_DIR` turns `rm -r \"$OUPUT_DIR\"/` into `rm -r /`. Session 9's habit applies: never `rm -rf` with a variable you have not printed. With `set -u` the script stops at that line with `OUPUT_DIR: unbound variable` and exit code 1.",
    "`chmod +x` on your laptop is enough for CI. Commit it: git records the mode (100644 to 100755). Under `/mnt/c` chmod does nothing at all.",
]

FLASHCARDS = [
    ("What are stdin, stdout and stderr?", "Three streams every program gets: stdin is what it reads (keyboard by default), stdout its result, stderr its messages about problems. stdout and stderr both show in the terminal unless redirected.", "concept", 1),
    ("In the expense-tracker, which stream carries `could not read nosuch.csv`, and why that one?", "stderr, via `typer.echo(..., err=True)`. The report (stdout) stays clean for files and pipes, and the message still reaches the person.", "distinction", 1),
    ("`>` vs `>>`", "`>` replaces the file's content (creating it if needed); `>>` adds to the end.", "distinction", 2),
    ("`uv run expenses report nosuch.csv > report.txt` failed. What is in `report.txt`?", "Nothing. The shell empties the file before the program starts, and the program wrote only to stderr. Yesterday's report is gone.", "reading", 2),
    ("What does `> all.txt 2>&1` do?", "Sends stdout to `all.txt`, then sends stderr to the same place: both streams end up in the file.", "concept", 2),
    ("What does `2> /dev/null` change, and what does it not change?", "It discards the error messages. The exit code is unchanged, so `&&`, `set -e` and CI still see the failure; you only lose the reason.", "concept", 2),
    ("`wc -l expenses.csv` vs `wc -l < expenses.csv`", "On the sample file, `19 expenses.csv` vs `19`. With `<` the shell feeds the file to stdin, so wc never learns its name.", "distinction", 2),
    ("What does `|` connect?", "The stdout of the command on the left to the stdin of the command on the right. stderr is not carried.", "concept", 3),
    ("What does `grep \"food\" expenses.csv | wc -l` print? (sample Q6)", "The number of lines that contain `food`. Not the number of occurrences, not the lines themselves.", "reading", 3),
    ("`uv run expenses report nosuch.csv | wc -l` shows the error and `0`. Why?", "The error went to stderr, straight to the screen; stdout was empty, so wc counted 0 lines.", "reading", 3),
    ("Where does grep look for its pattern?", "Anywhere in the line: dates, merchant names (`Sushi at home` for `home`), the header. It knows nothing about columns.", "concept", 4),
    ("`grep -c x file` vs `grep x file | wc -l`", "Same number: the count of matching lines. One counts inside grep, the other has wc count grep's output.", "distinction", 4),
    ("Why does `grep -v dining expenses.csv | wc -l` give one more than the number of non-dining expenses?", "The header has no `dining` in it, so `-v` keeps it and wc counts it.", "reading", 4),
    ("What does `cut -d, -f3 expenses.csv` print?", "The third comma-separated field of every line: the category column, starting with the header word `category`.", "concept", 4),
    ("`sort` vs `sort -n` on amounts", "Text order compares characters (`137.97` before `14.20`, `9.80` after `250.83`); `-n` compares the numbers.", "distinction", 4),
    ("Why `sort | uniq` and not just `uniq`?", "uniq only collapses identical lines that are next to each other. Sorting brings identical lines together first.", "concept", 5),
    ("`uniq -c` vs `uniq -d`", "`-c` prints each line once with how many times it appeared in a row; `-d` prints only the lines that repeat (one copy each).", "distinction", 5),
    ("Real file: `uniq -d expenses.csv | wc -l` prints 5, `sort expenses.csv | uniq -d | wc -l` prints 6. Why?", "One duplicate pair (Condis, 93.02, lines 351 and 354) is not adjacent; only sorting brings it together. Six matches session 8.", "reading", 5),
    ("The pipeline for 'how many expenses per category?'", "`tail -n +2 expenses.csv | cut -d, -f3 | sort | uniq -c`: skip the header, keep the column, sort, count (add `sort -rn` to rank).", "concept", 5),
    ("grep's three exit codes", "0: found at least one line. 1: ran fine, found nothing. 2: trouble, such as a missing file.", "recall", 6),
    ("`&&` vs `||` vs `;`", "`&&`: next only if the previous exited 0. `||`: next only if it failed. `;`: next regardless.", "distinction", 6),
    ("What is a pipeline's exit code, and what does `pipefail` change?", "By default the last command's (wc's 0 hides grep's 1). With `set -o pipefail` the pipeline fails if any stage fails.", "concept", 6),
    ("What does `#!/usr/bin/env bash` do?", "It tells the system which program runs the file when you start it as `./script.sh`: bash, found by `env`.", "concept", 7),
    ("`bash script.sh` vs `./script.sh`", "The first runs bash, which reads the file (no x bit needed). The second runs the file itself: it needs `chmod +x`.", "distinction", 7),
    ("`CATEGORY = dining` gives `CATEGORY: command not found`. Why?", "With spaces, bash reads a command called `CATEGORY` with two arguments. An assignment is `CATEGORY=dining`, no spaces.", "reading", 7),
    ("Why always write `\"$file\"` with quotes?", "Unquoted, bash splits the value at spaces: `Moodle Files/expenses.csv` becomes two file names that do not exist.", "concept", 7),
    ("`set -e`, `set -u`, `set -o pipefail`", "-e: stop at the first failing command. -u: an unset variable is an error. pipefail: a pipeline fails if any stage fails.", "distinction", 7),
    ("Why can `set -e` stop a script that has no bug?", "A grep that finds nothing exits 1, and `set -e` treats any non-zero exit as failure. Allow it explicitly (`|| true`) where no match is normal.", "concept", 7),
    ("The four checks of v0.5's `check.sh` (the rubric's 'Check yourself')", "`uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src tests`, `uv run pytest`: one per line under `set -euo pipefail` in `check.sh`, or joined by `&&` in the rubric's one-liner.", "recall", 8),
    ("'CI is a terminal': what happens when a step exits non-zero?", "The step turns red and, by default, the later steps are skipped, like `&&`. The run is red; at the v0.5 tag that caps Tests at 1.", "concept", 8),
]

# ===========================================================================
# Pipelines (stage outputs: real runs on SAMPLE, GNU format)
# ===========================================================================
PIPELINES = [
    {
        "id": f"{MID}-pl01",
        "title": "Count one category",
        "goal_md": "How many dining expenses are there? The shape of sample question 6.",
        "stages": [
            {"cmd": "grep dining expenses.csv", "output": P_DINING, "explain_md": "grep prints every line that contains `dining` anywhere. Here all five are dining expenses; nothing else in the file contains the word."},
            {"cmd": "| wc -l", "output": "5", "explain_md": "wc receives those five lines on stdin and counts lines. It prints one number and no file name, because it never saw a file."},
        ],
        "takeaway_md": "`grep x file | wc -l` counts lines that contain x, not occurrences. `grep -c dining expenses.csv` prints the same `5` in one step.",
    },
    {
        "id": f"{MID}-pl02",
        "title": "The merchant trap",
        "goal_md": "How many home expenses are there? (The true answer is 2: Ikea and Leroy Merlin.)",
        "stages": [
            {"cmd": "grep home expenses.csv", "output": P_HOME, "explain_md": "grep has no idea of columns. `Sushi at home` is a dining expense whose merchant name contains `home`, so it matches too."},
            {"cmd": "| wc -l", "output": "3", "explain_md": "wc counts the three lines it was given. The number is right for the question grep answered, and wrong for the question you asked."},
        ],
        "takeaway_md": "Match the whole field: `grep ,home, expenses.csv | wc -l` prints `2`. On the real file both versions print 24, which is why this trap goes unnoticed until a merchant like this appears.",
    },
    {
        "id": f"{MID}-pl03",
        "title": "Inverting a match keeps the header",
        "goal_md": "How many expenses are not dining? (18 expenses, 5 dining: the answer is 13.)",
        "stages": [
            {"cmd": "grep -v dining expenses.csv", "output": P_NOT_DINING, "explain_md": "`-v` keeps every line that does not contain `dining`. The header contains no `dining`, so it is kept along with the 13 expenses."},
            {"cmd": "| wc -l", "output": "14", "explain_md": "wc counts all 14 lines, header included."},
        ],
        "takeaway_md": "Drop the header first: `tail -n +2 expenses.csv | grep -v dining | wc -l` prints `13`.",
    },
    {
        "id": f"{MID}-pl04",
        "title": "Expenses per category",
        "goal_md": "How many expenses are there in each category, most frequent first? Keep the top three.",
        "stages": [
            {"cmd": "tail -n +2 expenses.csv", "output": P_BODY, "explain_md": "`tail -n +2` prints from line 2 to the end: every expense, without the header."},
            {"cmd": "| cut -d, -f3", "output": P_CATS, "explain_md": "`cut` keeps the third comma-separated field: one category per expense, in file order."},
            {"cmd": "| sort", "output": P_CATS_SORTED, "explain_md": "sort puts equal names next to each other. Without this step uniq would count broken runs."},
            {"cmd": "| uniq -c", "output": P_CATS_COUNTED, "explain_md": "uniq collapses each run of identical lines into one and `-c` writes how many there were in front."},
            {"cmd": "| sort -rn", "output": P_CATS_RANKED, "explain_md": "`-rn` sorts on the number at the start of each line, largest first. Equal counts come out in an order you should not rely on."},
            {"cmd": "| head -n 3", "output": "      5 dining\n      4 groceries\n      3 transport", "explain_md": "`head -n 3` keeps the first three lines: the three categories with the most expenses."},
        ],
        "takeaway_md": "Skip the header, cut the column, sort, count, rank, keep three: slide 7 builds it one stage at a time. On the real file it prints `119 groceries`, `86 dining`, `76 transport`. Leave out `tail -n +2` and a line `      1 category` appears; leave out the first `sort` and dining is counted in four separate pieces.",
    },
    {
        "id": f"{MID}-pl05",
        "title": "Text order is not number order",
        "goal_md": "A first attempt at the three largest amounts. (The file contains 250.83 and 137.97.)",
        "stages": [
            {"cmd": "cut -d, -f4 expenses.csv", "output": P_AMOUNTS_WITH_HEADER, "explain_md": "The amount column, header word `amount` included, because `cut` treats the header like any other line."},
            {"cmd": "| sort -r", "output": P_AMOUNTS_TEXT_REV, "explain_md": "Without `-n`, sort compares characters: letters come after digits, and `9` after `2`, so `9.80` lands above `250.83`. Reversed, `amount` comes first and `250.83` lands in the middle."},
            {"cmd": "| head -n 3", "output": "amount\n91.60\n9.80", "explain_md": "head keeps the first three lines of a list that was already in the wrong order."},
        ],
        "takeaway_md": "Two bugs, one believable answer: the header is still in the data, and the sort is textual. The next pipeline fixes both.",
    },
    {
        "id": f"{MID}-pl06",
        "title": "The three largest amounts",
        "goal_md": "The three largest amounts, done right.",
        "stages": [
            {"cmd": "tail -n +2 expenses.csv", "output": P_BODY, "explain_md": "Drop the header first, so the word `amount` never reaches sort."},
            {"cmd": "| cut -d, -f4", "output": P_AMOUNTS, "explain_md": "Keep only the amount field."},
            {"cmd": "| sort -rn", "output": P_AMOUNTS_NUM_REV, "explain_md": "`-n` compares the values as numbers, `-r` puts the largest first."},
            {"cmd": "| head -n 3", "output": "250.83\n137.97\n91.60", "explain_md": "The first three lines are now the three largest amounts."},
        ],
        "takeaway_md": "Header out, numeric sort, then head. Compare with the previous pipeline: same tools, two changes, the right answer.",
    },
    {
        "id": f"{MID}-pl07",
        "title": "The largest expense, whole line",
        "goal_md": "Which expense is the largest? The shell's version of `largest_expense`.",
        "stages": [
            {"cmd": "tail -n +2 expenses.csv", "output": P_BODY, "explain_md": "All expenses, no header."},
            {"cmd": "| sort -t, -k4 -rn", "output": P_ROWS_BY_AMOUNT, "explain_md": "`-t,` tells sort the fields are separated by commas and `-k4` sorts on the fourth field, the amount, as a number, largest first. Whole lines move, so the merchant and date stay with their amount."},
            {"cmd": "| head -n 1", "output": "2025-07-14,Leroy Merlin,home,250.83", "explain_md": "The first line is the largest expense."},
        ],
        "takeaway_md": "On the real file the same pipeline prints `2025-11-17,Ferreteria Mas,home,296.49`, the expense `uv run expenses report` calls the largest single expense.",
    },
    {
        "id": f"{MID}-pl08",
        "title": "Find the duplicate rows",
        "goal_md": "Which rows appear more than once, and how many are there?",
        "stages": [
            {"cmd": "sort expenses.csv", "output": P_SORTED_FILE, "explain_md": "Sorting the whole lines puts identical rows next to each other. The header goes last, because letters sort after digits."},
            {"cmd": "| uniq -d", "output": P_DUPES, "explain_md": "`uniq -d` prints one copy of every line that is repeated on neighbouring lines."},
            {"cmd": "| wc -l", "output": "2", "explain_md": "Two rows of the sample file are exact duplicates."},
        ],
        "takeaway_md": "On the real file `sort expenses.csv | uniq -d | wc -l` prints `6`: session 8's six exact duplicates, the reason `remove_duplicates` takes 420 expenses to 414.",
    },
    {
        "id": f"{MID}-pl09",
        "title": "uniq without sort misses one",
        "goal_md": "The same question, without the sort.",
        "stages": [
            {"cmd": "uniq -d expenses.csv", "output": "2025-07-03,Can Recasens,dining,33.02", "explain_md": "uniq compares each line only with the one before it. The Can Recasens pair is adjacent; the Mercadona pair has Bar Ramon between them, so uniq never sees it."},
            {"cmd": "| wc -l", "output": "1", "explain_md": "One duplicate found out of two."},
        ],
        "takeaway_md": "On the real file the same mistake prints `5` instead of `6`: the two `2025-11-29,Condis,groceries,93.02` rows are lines 351 and 354. Sort first.",
    },
    {
        "id": f"{MID}-pl10",
        "title": "A merchant twice is not a duplicate",
        "goal_md": "Which merchants appear more than once?",
        "stages": [
            {"cmd": "tail -n +2 expenses.csv", "output": P_BODY, "explain_md": "All expenses, no header."},
            {"cmd": "| cut -d, -f2", "output": P_MERCHANTS, "explain_md": "Keep only the merchant field."},
            {"cmd": "| sort", "output": P_MERCHANTS_SORTED, "explain_md": "Equal merchant names are now neighbours."},
            {"cmd": "| uniq -d", "output": "Cabify\nCan Recasens\nMercadona", "explain_md": "Three merchants appear more than once."},
        ],
        "takeaway_md": "Three repeated merchants, but only two duplicate rows: the two Cabify trips (1 and 15 July, different amounts) are different expenses. Session 8's test said the same: `test_same_merchant_on_another_day_is_not_a_duplicate`.",
    },
]

TERMS.extend(
    [
        ("Positional arguments", "`$1` is the first argument of a script, `$#` how many there are and `$0` the script's own name as you typed it. Quote them: `\"$1\"`.", 9),
        ("Test `[ ... ]`", "The condition of an `if`: `[ \"$#\" -lt 1 ]` compares numbers, `[ -f \"$1\" ]` tests for a file, `-d` for a folder, `-e` for anything that exists, and `!` negates. Spaces inside the brackets are required.", 9),
        ("for loop", "`for file in *.csv; do ... done` runs the body once for each name the pattern expands to.", 9),
        ("Command substitution `$(...)`", "Replaced by the output of the command inside it: `\"$file has $(wc -l < \"$file\") lines\"`.", 9),
        ("`>&2`", "Sends a message to stderr instead of stdout, so it stays out of redirected output and pipes. Used for usage and error messages in a script.", 9),
        ("Arithmetic `$(( ))`", "`counter=$((counter + 1))` adds one and is safe under `set -e`. `((counter++))` evaluates to the old value, which is 0 the first time, and `-e` stops the script.", 9),
    ]
)

TRAPS.extend(
    [
        "`((counter++))` is a fine way to add one in a script with `set -e`. When the counter is 0 it evaluates to 0, `-e` reads that as failure and the script stops without a word. Use `counter=$((counter + 1))`.",
        "One `>` where you meant `>>` does little harm. `>` overwrites without asking: in the clean-copy recipe it deletes the header you have just written. Work on a copy and never edit the original `expenses.csv`.",
        "Every error in a script should `exit 1`. Any non-zero number is a failure for `&&`, `set -e` and CI, but the slides use 2 when the script is called wrongly (usage) and 1 when the job fails, and write both messages to stderr with `>&2`.",
        "If the shell total and the tracker's total agree, the file has no duplicates. Neither removes them: the groceries total is 6401.78 in both, and `sort -u` before the `cut` gives 6156.31.",
    ]
)

FLASHCARDS.extend(
    [
        ("What do `$#`, `$0` and `$1` hold in a script?", "`$#` is the number of arguments, `$0` the script's own name as you typed it, `$1` the first argument. Always quote it: `\"$1\"`.", "recall", 9),
        ("What do `-f`, `-d` and `-e` test inside `[ ... ]`?", "`-f`: is a regular file. `-d`: is a folder. `-e`: exists, either kind. `!` negates: `[ ! -f \"$1\" ]` is true when `$1` is not a file.", "recall", 9),
        ("Why does `top.sh` use `exit 2` for usage and `exit 1` for a missing file?", "Any non-zero code is a failure. By convention 2 means the script was called wrongly and 1 means the job could not be done. `&&`, `set -e` and CI read the number, not the message.", "concept", 9),
        ("What does `echo \"usage: $0 FILE\" >&2` do?", "It sends the message to stderr, so it is not mixed into the output: a redirected file or a pipe stays clean while the person still sees the error.", "concept", 9),
        ("What does `for file in *.csv; do echo \"$file has $(wc -l < \"$file\") lines\"; done` print?", "One line per CSV file in the folder: its name and its line count. `$(...)` is the output of a command, and `wc -l <` prints only the number.", "reading", 9),
        ("What does `top=\"${2:-3}\"` mean?", "`top` is the second argument if there is one, otherwise `3`.", "recall", 9),
        ("Why is `((counter++))` a trap under `set -e`?", "It evaluates to the old value, `0` the first time, which `-e` reads as failure, so the script stops silently. Use `counter=$((counter + 1))`.", "concept", 9),
        ("Which topics did session 10 skip and not examine?", "Functions and `trap` (clean up on exit). Look them up when you need them (slide 19).", "recall", 9),
        ("`>` where you meant `>>`: what is the damage?", "`>` overwrites without asking, so the earlier content is gone: slide 9 calls one `>` for `>>` the shell's `rm`. Work on a copy, never on the original `expenses.csv`.", "concept", 2),
        ("The clean-copy recipe for `expenses.csv`", "`head -n 1 expenses.csv > clean.csv`, then `tail -n +2 expenses.csv | sort -u >> clean.csv`: the header first with `>`, the distinct expenses added with `>>`. 415 lines on the real file.", "recall", 2),
        ("What does `sort -u` do?", "Sorts and keeps one copy of each distinct line: the same as `sort | uniq`.", "distinction", 5),
        ("What does `grep '^2025-09' expenses.csv | wc -l` count?", "The lines that start with `2025-09`, the expenses of September 2025 (67 on the real file). `^` anchors the pattern to the start of the line.", "reading", 5),
        ("The real `expenses.csv` in numbers", "421 lines (a header and 420 expenses), 8 categories, the biggest three groceries 119, dining 86 and transport 76, six exact duplicate rows, 415 lines in `clean.csv`.", "recall", 5),
        ("What does `scripts/check.sh` print and return when everything passes?", "A `==> name` line for each check (`ruff check`, `ruff format`, `mypy`, `pytest`) followed by that tool's output, then exit code 0. A failing check stops it there with exit code 1: the red cross on GitHub.", "concept", 8),
    ]
)

PIPELINES.extend(
    [
        {
            "id": f"{MID}-pl11",
            "title": "How many different categories?",
            "goal_md": "How many different categories does the file have? (Slide 4 asks it of the real file and gets 8.)",
            "stages": [
                {"cmd": "tail -n +2 expenses.csv", "output": P_BODY, "explain_md": "All expenses, without the header."},
                {"cmd": "| cut -d, -f3", "output": P_CATS, "explain_md": "One category name per expense, in file order."},
                {"cmd": "| sort", "output": P_CATS_SORTED, "explain_md": "Equal names are now neighbours."},
                {"cmd": "| uniq", "output": P_CATS_DISTINCT, "explain_md": "uniq leaves one line for each run of equal lines: one line per category."},
                {"cmd": "| wc -l", "output": "8", "explain_md": "wc counts those lines: eight different categories."},
            ],
            "takeaway_md": "Without `tail -n +2` the header word `category` is one more name and the count is 9. On the real file the same pipeline prints `8`.",
        },
        {
            "id": f"{MID}-pl12",
            "title": "Total spent on groceries",
            "goal_md": "How much was spent on groceries? Lab 10's exercise 7 asks the shell and then the tracker.",
            "stages": [
                {"cmd": "grep ',groceries,' expenses.csv", "output": P_GROCERIES, "explain_md": "The four groceries rows. The commas around the word keep a merchant such as `Sushi at home` out of other categories."},
                {"cmd": "| cut -d, -f4", "output": "56.77\n21.50\n21.50\n8.66", "explain_md": "Only the amount column."},
                {"cmd": "| paste -sd+", "output": "56.77+21.50+21.50+8.66", "explain_md": "`paste -sd+` joins all the lines into one, with a plus sign between them."},
                {"cmd": "| bc", "output": "108.43", "explain_md": "bc is a calculator: it reads the sum and prints the result."},
            ],
            "takeaway_md": "On the real file the same pipeline prints `6401.78`, exactly what `uv run expenses report --category groceries` shows. Both count the duplicate rows; `sort -u` before the `cut` would give `6156.31`.",
        },
    ]
)

# ===========================================================================
# Module
# ===========================================================================
MODULE: dict[str, Any] = {
    "id": MID,
    "order": 10,
    "module": "M3",
    "title": "Pipes, text wrangling and bash scripts",
    "sessions": [10],
    "predicted": False,
    "sources": [
        "slides-session-10 (slides 2–21)",
        "labs/10-wrangling.md",
        "labs/10-bash.md",
        "labs/10-check.sh (expense-tracker scripts/check.sh at v0.5)",
        "slides-session-9 (slides 3, 6, 18–21, 24)",
        "labs/09-terminal.md",
        "partial-rubric.txt",
        "moodle/midterm-sample-questions.md (Q6)",
        "slides-session-5 (exit codes)",
        "slides-session-7 (stderr, fail loudly)",
        "slides-session-8 (six duplicates)",
        "expense-tracker v0.4 and v0.5: expenses.csv, cli.py, scripts/check.sh, .github/workflows/check.yml",
    ],
    "summary_md": md(
        """
        Session 10 (Friday 16 October) had one goal: answer a question about real data with one pipeline, then turn a pipeline into a script. This module follows its slides and labs: pipes and redirection (`>`, `>>`, `|`, `2>`), the wrangling kit on `expenses.csv` (`head`, `tail`, `wc`, `cut`, `grep`, `sort`, `uniq`) and the traps that give wrong numbers, working on a copy, scripts with arguments, conditions and loops, exit codes, `set -euo pipefail`, and v0.5's `scripts/check.sh`, whose exit code is what turns a CI step green or red. It matters because the mid-term covers sessions 1–10 (Modules 1 to 3), sample question 6 is already a pipeline, and the partial submission's CI gate depends on a check script that does not lie. Every output in it was produced by running the command. Functions and `trap` were skipped in the session and are not examined.
        """
    ),
    "exam_focus_md": md(
        """
        - Sample Q6 shape: a pipeline on `expenses.csv` and "what does this print?". Lines, not occurrences; watch the header and merchant names that contain the word.
        - Predict the output of a 2–6 stage pipeline on a small file printed in the question, stage by stage (slide 7: header, column, sort, count, rank, top three).
        - Explain a wrong result: uniq without sort, a header that was counted, a text sort of amounts, a pattern that matches too much.
        - Where did the text go: `>` vs `>>`, `2>`, `/dev/null`, `>&2`, and why `could not read nosuch.csv` still appears on the screen (stderr, session 7). Never edit the original: `>` where you meant `>>` is the shell's `rm`.
        - Read a short script and its calls: `"$1"`, `$#`, `$0`, `[ ! -f "$1" ]`, `for file in *.csv`, `$(...)`, what is printed, to which stream, and what `echo $?` shows (2 for a wrong call, 1 for a failed job).
        - `set -euo pipefail`: which letter catches which silent failure, a grep that finds nothing under `set -e`, and the `((counter++))` trap (use `counter=$((counter + 1))`).
        - `check.sh` and CI: the `==>` lines, which step stopped the run, why exit code 1 is the red cross, why run the checks before tagging v0.5, the x bit and `uv.lock` that must be committed.
        """
    ),
    "sections": SECTIONS,
    "terms": [
        {"term": t, "definition_md": d, "section_ref": f"{MID}-s{s}"} for (t, d, s) in TERMS
    ],
    "traps": TRAPS,
    "flashcards": [
        {
            "id": f"{MID}-f{i:02d}",
            "front_md": front,
            "back_md": back,
            "kind": kind,
            "section_ref": f"{MID}-s{s}",
        }
        for i, (front, back, kind, s) in enumerate(FLASHCARDS, start=1)
    ],
    "questions": sorted(QUESTIONS, key=lambda q: q["id"]),
    "sample_files": {"expenses.csv": SAMPLE},
    "pipelines": PIPELINES,
}


def main() -> None:
    OUT.write_text(json.dumps(MODULE, ensure_ascii=False, indent=1) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
