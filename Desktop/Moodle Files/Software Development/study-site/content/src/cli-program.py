"""Generate content/cli-program.json: session 5, from script to program.

Every terminal transcript and tool output below was produced by running it in
$SCRATCH/work/cli-program (typer 0.27.2, uv 0.12.16, mypy 2.3.1/2.4.0, ruff 0.16.x,
pytest 9.1.1, the versions pinned by the course's lockfiles), then trimmed. Scratch
path prefixes were rewritten to project-relative paths.

Run:  uv run python content/src/cli-program.py
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

MID = "cli-program"
OUT = Path(__file__).resolve().parent.parent / f"{MID}.json"

# ---------------------------------------------------------------- artefact helpers

BOX_W = 76
ERR_TOP = "╭─ Error " + "─" * 70 + "╮"
BOX_BOT = "╰" + "─" * 78 + "╯"


def err_box(msg: str) -> str:
    """The error box typer 0.27.2 prints (80 columns, as in a non-interactive terminal)."""
    return "\n".join([ERR_TOP, "│ " + msg.ljust(BOX_W) + " │", BOX_BOT])


def usage_err(usage: str, try_cmd: str, msg: str) -> str:
    return f"Usage: {usage}\nTry '{try_cmd} --help' for help.\n{err_box(msg)}"


HELP_ADD_LAB = """\
 Usage: expenses add [OPTIONS] {merchant} {amount}

╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    merchant      <str>    [required]                                       │
│ *    amount        <float>  [required]                                       │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯"""

HELP_PARK = """\
 Usage: parking-lot park [OPTIONS] {plate}

╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    plate      <str>  [required]                                            │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --hours        <int>  [default: 1]                                           │
│ --help                Show this message and exit.                            │
╰──────────────────────────────────────────────────────────────────────────────╯"""

HELP_PARK_NO_CALLBACK = """\
 Usage: parking-lot [OPTIONS] {plate}

╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    plate      <str>  [required]                                            │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --hours                     <int>  [default: 1]                              │
│ --install-completion               Install completion for the current shell. │
│ --show-completion                  Show completion for the current shell, to │
│                                    copy it or customize the installation.    │
│ --help                             Show this message and exit.               │
╰──────────────────────────────────────────────────────────────────────────────╯"""

HELP_REPORT_NO_ARGUMENT = """\
 Usage: expenses report [OPTIONS]

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --path                 <str>    [default: expenses.csv]                      │
│ --category             <str>    Only this category.                          │
│ --minimum,--min        <float>  Ignore amounts below this. [default: 0.0]    │
│ --help                          Show this message and exit.                  │
╰──────────────────────────────────────────────────────────────────────────────╯"""


MYPY_MAIN = (
    "src/parking_lot/__main__.py:1: error: Cannot find implementation or library stub "
    'for module named "app.cli"  [import-not-found]\n'
    "src/parking_lot/__main__.py:1: note: See "
    "https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports\n"
    "Found 1 error in 1 file (checked 4 source files)"
)

LOCK_ERR = (
    "error: The lockfile at `uv.lock` needs to be updated, but `--locked` was provided.\n"
    "\n"
    "hint: To update the lockfile, run `uv lock`."
)

FOUR_CHECKS_MAIN_FORGOTTEN = f"""\
$ uv run ruff check .
All checks passed!
$ uv run ruff format --check .
6 files already formatted
$ uv run mypy src tests
{MYPY_MAIN}
$ uv run pytest
...
tests/test_cli.py ..                                                     [100%]

============================== 2 passed in 0.03s ==============================="""


def fence(lang: str, body: str) -> str:
    return f"```{lang}\n{body}\n```"


# ---------------------------------------------------------------- builders

QUESTIONS: list[dict[str, Any]] = []


def _common(
    n: int,
    qtype: str,
    level: str,
    skills: list[str],
    stem: str,
    explanation: str,
    sec: int,
    source_ref: str,
    origin: str,
    verified: str,
) -> dict[str, Any]:
    return {
        "id": f"{MID}-q{n:02d}",
        "type": qtype,
        "level": level,
        "skills": skills,
        "stem_md": stem.strip(),
        "explanation_md": explanation.strip(),
        "section_ref": f"{MID}-s{sec}",
        "source_ref": source_ref,
        "origin": origin,
        "verified_by": verified,
    }


def mcq(
    n: int,
    level: str,
    skills: list[str],
    stem: str,
    options: list[tuple[bool, str, str]],
    explanation: str,
    sec: int,
    source_ref: str,
    origin: str = "slides",
    verified: str = "run",
) -> None:
    q = _common(n, "mcq", level, skills, stem, explanation, sec, source_ref, origin, verified)
    assert len(options) == 4 and sum(o[0] for o in options) == 1, q["id"]
    q["options"] = [
        {"text_md": t.strip(), "correct": c, "why_md": w.strip()} for c, t, w in options
    ]
    QUESTIONS.append(q)


def open_q(
    n: int,
    level: str,
    skills: list[str],
    stem: str,
    parts: list[dict[str, Any]],
    explanation: str,
    sec: int,
    source_ref: str,
    lines: str,
    origin: str = "slides",
    verified: str = "run",
) -> None:
    q = _common(n, "open", level, skills, stem, explanation, sec, source_ref, origin, verified)
    q["parts"] = [
        {
            "label": str(i + 1),
            "prompt_md": p["prompt"].strip(),
            "marks": p["marks"],
            "model_answer_md": p["model"].strip(),
            "rubric": p["rubric"],
            "weak_answers_md": p["weak"].strip(),
        }
        for i, p in enumerate(parts)
    ]
    q["lines"] = lines
    QUESTIONS.append(q)


def sort_q(
    n: int,
    level: str,
    skills: list[str],
    stem: str,
    categories: list[tuple[str, str]],
    items: list[tuple[str, str, str]],
    explanation: str,
    sec: int,
    source_ref: str,
    origin: str = "slides",
    verified: str = "run",
) -> None:
    q = _common(n, "sort", level, skills, stem, explanation, sec, source_ref, origin, verified)
    q["categories"] = [{"id": i, "label": label} for i, label in categories]
    q["items"] = [{"text_md": t.strip(), "category": c, "why_md": w.strip()} for t, c, w in items]
    QUESTIONS.append(q)


def P(prompt: str, marks: int, model: str, rubric: list[str], weak: str) -> dict[str, Any]:
    return {"prompt": prompt, "marks": marks, "model": model, "rubric": rubric, "weak": weak}


# ================================================================ SECTIONS

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
            "id": f"{MID}-s{n}",
            "heading": heading,
            "body_md": body.strip(),
            "key_points": key_points,
            "exam_note_md": exam_note.strip(),
            "source_ref": source_ref,
            "check": [f"{MID}-q{c:02d}" for c in check],
        }
    )


# ---------------------------------------------------------------- s1
section(
    1,
    "Two ways to run the same code",
    """
Session 5 opens with "A program, not a script", and slide 4 puts two lines side by side:

```bash
python tracker.py                    # a file, run by an interpreter
uv run expenses report               # a command, installed from a project
```

Same code. The second one has **a name, a version, dependencies and an entry point**, and all four live in `pyproject.toml`: `name = "expense-tracker"`, `version = "0.1.0"`, `dependencies = ["typer>=0.12"]`, and the `[project.scripts]` line that turns `expenses` into a command. Session 4 called the first a script and the second a project.

**A file run by an interpreter.** You choose the interpreter, you stand in the right folder, and Python runs the file from top to bottom with whatever packages that interpreter happens to have. On the course's machines typer is installed only inside the project's `.venv`, so the system Python stops at `import typer`:

```console
$ python3 src/expense_tracker/cli.py report
Traceback (most recent call last):
  File "src/expense_tracker/cli.py", line 5, in <module>
    import typer
ModuleNotFoundError: No module named 'typer'
```

Even with the project's interpreter, the file route does nothing useful at `v0.4`: `uv run python src/expense_tracker/cli.py report` prints nothing and exits 0. Running a file executes its top-level code, and the top level of `cli.py` only creates `app` and defines the commands. No line calls `app()`, so `report` never runs.

**A command installed from a project.** `uv run` reads `pyproject.toml` and `uv.lock`, installs whatever is missing into `.venv`, and runs the command. Session 4 put it as "needs the project, from anywhere", with the same versions for every teammate and for CI. The command is also what Checkpoint 1 checks: `uv sync && uv run <your-app> --help` from a clean clone.

The demo made this move in two commits: `a953d05` turned the script into a uv package, and `2ecad20` moved the report "into the package behind a typer CLI". The rest of this module is about that command: how it is found, the second way in, how typer reads your function, how it reports failure, and the lab that turns your template into one.
""",
    [
        "Same code, two ways in: a file you hand to an interpreter, or a command the project installs.",
        "The command has a name, a version, dependencies and an entry point, all in `pyproject.toml`.",
        "A file gets whatever packages its interpreter has; `uv run` builds the project's environment from `pyproject.toml` and `uv.lock` first.",
        "Running `cli.py` as a file only defines `app`; something has to call it.",
    ],
    "Expect a transcript where the file route fails and the command works, and a question about why. Answer with the interpreter and the environment; reinstalling things is the careless move.",
    "S5 slides 3–4; S4 slides 19–23; expense-tracker a953d05, 2ecad20",
    [1, 2, 3],
)

# ---------------------------------------------------------------- s2
section(
    2,
    "What `uv run expenses` resolves",
    """
Slide 5 reads one line of `pyproject.toml`:

```toml
[project.scripts]
expenses = "expense_tracker.cli:app"
```

Read it in three steps: `expenses` → module `expense_tracker.cli` → object `app`. The left side is the name of the command you type. The right side is a dotted module path (the file `src/expense_tracker/cli.py`), a colon, and the name of an object inside that module: the `app = typer.Typer(...)` that every command is attached to.

**A wrapper is written into the environment on install.** When `uv sync` installs the project (and `uv run` syncs first), uv writes a tiny program called `expenses` into `.venv/bin/`. These are its working lines, from the real file:

```python
import sys
from expense_tracker.cli import app
if __name__ == "__main__":
    ...
    sys.exit(app())
```

It imports exactly the module and the object named in the line, calls `app()`, and hands typer's exit code back to the shell. `uv run expenses` finds that wrapper and runs it.

**Rename either side and the command disappears.** Each part can break on its own, and each gives a different message:

| What changed | What you see |
|---|---|
| The command name on the left (`2ecad20` replaced `expense-tracker = ...` with `expenses = ...`) | `uv run expense-tracker` now fails with `error: Failed to spawn` |
| The module on the right, but not the package folder (still `src/app`) | the wrapper starts, then `ModuleNotFoundError: No module named 'parking_lot'` |
| The object in `cli.py` (`app` renamed to `cli`) | `ImportError: cannot import name 'app' from 'parking_lot.cli'` |

Two readings follow. `Failed to spawn` means uv found no command by that name: nothing was installed under it. A traceback that starts in `.venv/bin/<command>` means the wrapper exists but its import failed, so look at the module or the object.

The command does not have to match the project name. The demo project is `expense-tracker` and its command is `expenses`. The lab asks you to use your hyphenated project name for both, which keeps one less name to remember.
""",
    [
        '`expenses = "expense_tracker.cli:app"`: command → module → object.',
        "Installing writes a wrapper into `.venv/bin/` that imports `app` and calls it.",
        "`Failed to spawn`: no command by that name. A traceback from `.venv/bin/...`: the wrapper's import failed.",
        "Rename the command, the module or the object without updating the line, and the command disappears.",
    ],
    "The usual artefact is an error after a rename. Say which part failed: the command name (left), the module (right, before the colon) or the object (after the colon).",
    "S5 slide 5; S4 slide 21; expense-tracker 2ecad20; labs/01-scaffold.md troubleshooting",
    [4, 5, 6],
)

# ---------------------------------------------------------------- s3
section(
    3,
    "`__main__.py`: the other door",
    """
Slide 6 shows a second way to start the same program:

```bash
python -m expense_tracker            # runs src/expense_tracker/__main__.py
```

```python
from expense_tracker.cli import app

if __name__ == "__main__":
    app()
```

`python -m <package>` asks Python to find the package and run the file `__main__.py` inside it. That file imports the same `app` object and calls it, so both doors lead to the same typer program. The difference is what each door needs. The command needs the `[project.scripts]` line and the wrapper written on install. The `-m` door reads neither: it "works without the install step" and only needs Python to be able to import the package. (With the `src/` layout, importable means installed into `.venv`, as session 4 showed. So in practice the `-m` door still needs `uv sync`; what it skips is the wrapper and `[project.scripts]`. That is why you type `uv run python -m ...`.)

**The doors fail independently.** Delete the `[project.scripts]` table from a renamed template and the command is gone while the other door still works:

```console
$ uv run parking-lot park 1234ABC
error: Failed to spawn: `parking-lot`
  cause: No such file or directory (os error 2)
$ uv run python -m parking_lot park 1234ABC
Ticket for 1234ABC: 1 h
```

The reverse happens on the demo. Session 4's anatomy slide lists a `__main__.py`, but the expense-tracker repository never added one (look at any tag from `v0.1` to `v0.4`), so `uv run expenses report` works while `uv run python -m expense_tracker report` stops with `No module named expense_tracker.__main__; 'expense_tracker' is a package and cannot be directly executed`. On paper, answer from the slides: slide 6 and the session 4 anatomy say `python -m expense_tracker` runs `src/expense_tracker/__main__.py`.

**The file everyone forgets to rename.** The template ships `src/app/__main__.py` with `from app.cli import app`. After you rename the package, nothing you normally run touches it: `uv run <your-app>` goes through the wrapper, and your tests import `<your_package>.cli` directly. So pytest stays green while the import points at a package that no longer exists. Only mypy, which reads every file under `src`, notices, or anyone who tries the `-m` door. That is the second of the three that bite, at the end of this module.
""",
    [
        "`python -m <package>` runs the package's `__main__.py`, which calls the same `app`.",
        "The `-m` door needs no `[project.scripts]` line and no wrapper; only an importable package.",
        "Each door can break while the other works.",
        "`__main__.py` is the rename everyone forgets: the tests never import it, mypy does.",
    ],
    "A question may show one door working and the other failing. Name the file each door depends on: `[project.scripts]` for the command, `__main__.py` for `python -m`.",
    "S5 slide 6; S4 slide 20; project-template src/app/__main__.py; expense-tracker v0.1–v0.4 file list",
    [8, 9],
)

# ---------------------------------------------------------------- s4
section(
    4,
    "typer: the type hints are the specification",
    f"""
Slide 7 shows the whole idea in a few lines:

```python
@app.command()
def add(merchant: str, amount: float) -> None:
    ...
```

`@app.command()` registers the function as a command named after it, `add`. typer then reads the signature and builds the command line from it. Each parameter becomes a value the user types, and each type hint says how to convert the text the user typed: `amount` arrives as the text `12.50` and typer hands your function the float `12.50`. One rule decides the shape: **a parameter with no default is an argument; a default is what turns a parameter into an option.** `merchant: str` has no default, so it is an argument. So is `amount: float` here. The type does not decide.

**`--help` is generated, never written.** This is the real help for the lab's command:

{fence("text", HELP_ADD_LAB)}

The slide prints the usage line as `Usage: expenses add [OPTIONS] MERCHANT AMOUNT`; the typer version pinned in the course's `uv.lock` (0.27.2) writes the names in braces. The meaning is the same: after `[OPTIONS]` come the arguments, in the order you type them. An argument you may leave out appears in square brackets, as `report`'s `[path]` does.

**The hints also do the checking.** typer converts every value before your function runs, and refuses what it cannot convert:

{fence("console", '$ uv run expenses add "Bar Ramon" twelve' + chr(10) + usage_err("expenses add [OPTIONS] {merchant} {amount}", "expenses add", "Invalid value for 'amount': 'twelve' is not a valid float.") + chr(10) + "$ echo $?" + chr(10) + "2")}

Your `add` never ran. Compare the `v0.0` script, which read `sys.argv` by position and had no help at all: `python tracker.py --help` printed `could not read --help`, because the script took `--help` for a file name. typer replaced that with one signature that is the specification, the parser, the type check and the help page at once.
""",
    [
        "typer reads the signature: function name → command, parameters → values, type hints → conversion.",
        "No default → argument. A default → option. The type does not decide.",
        "`--help` and the usage line are generated from the code.",
        "A value typer cannot convert is refused with exit code 2 before your function runs.",
    ],
    "Expect a signature and a usage line or an error box; you predict one from the other. The slide writes `MERCHANT AMOUNT`, the course's typer writes `{merchant} {amount}`: read both the same way.",
    "S5 slide 7; labs/01-scaffold.md §5; expense-tracker c746d38 (v0.0) and 2ecad20",
    [11, 12, 43],
)

# ---------------------------------------------------------------- s5
section(
    5,
    "Argument or option",
    f"""
Slide 8 gives the table to learn:

| | Argument | Option |
|---|---|---|
| Written | `add "Bar Ramon" 12.50` | `--category dining` |
| In Python | no default | has a default |
| For | what the command acts on | how it behaves |
| Missing | error | falls back to the default |

Read the rows as design advice. What the command acts on (the merchant and amount of an expense, the plate of a car) is an argument: the command makes no sense without it, so leaving it out is an error. How the command behaves (one category only, a minimum amount, a date other than today) is an option: it has a sensible default, so leaving it out is fine. The demo follows the table: at `v0.4`, `add` takes `merchant`, `category` and `amount` as arguments and `--date` as an option, and `report` has `--category` and `--minimum` as options.

**A default makes an option, even when a positional value was intended.** Give the lab's `amount` a default (`amount: float = 0.0`) and typer turns it into `--amount`. A forgotten amount is no longer typer's `Missing argument` error: `add "Bar Ramon"` now calls your function with 0.0, and only the lab's own check stops it (`amount must be positive`, exit 1). And the natural call fails:

{fence("console", '$ uv run expenses add "Bar Ramon" 12.50' + chr(10) + usage_err("expenses add [OPTIONS] {merchant}", "expenses add", "Got unexpected extra argument(s) (12.50)"))}

**`typer.Argument(...)` overrides that.** `report` wants a file that is optional:

```python
path: str = typer.Argument("expenses.csv", help="CSV file to read."),
```

The usage line becomes `expenses report [OPTIONS] [path]`: `expenses report` reads the sample `expenses.csv`, and `expenses report data/expenses.csv` reads the file `add` writes. The lab's troubleshooting row says the same: drop the default, or use `typer.Argument(...)`.

**argparse, the stdlib fallback.** Slide 10 shows the same table spelled the older way:

```python
parser = argparse.ArgumentParser()
parser.add_argument("plate")
parser.add_argument("--hours", type=int, default=1)
```

A name without dashes is a positional argument; `--hours` is an option with a default. Its generated help starts `usage: park.py [-h] [--hours HOURS] plate`. argparse ships with Python, so it needs no dependency, but it takes more code: you build the parser call by call instead of writing one signature. It is worth recognising in code you inherit; this course uses typer.
""",
    [
        "Argument: what the command acts on; no default; missing means an error.",
        "Option: how it behaves; has a default; missing means the default.",
        "A default turns a parameter into an option; `typer.Argument(default)` keeps it positional but optional.",
        "argparse: no dashes = positional, `--name` = option; standard library, more code.",
    ],
    "A favourite artefact is `Got unexpected extra argument(s)`, or a `--help` that lists an option where an argument was meant. The cause is almost always a default.",
    "S5 slides 8 and 10; labs/01-scaffold.md troubleshooting; expense-tracker cli.py v0.1–v0.4",
    [14, 16, 20],
)

# ---------------------------------------------------------------- s6
section(
    6,
    "Exit codes: a program that does not lie",
    """
Every program ends by handing the shell one number, its exit code. **0 means success; anything else means failure.** You read it with `echo $?` straight after the command. Slide 9 shows the idea with `-5.00`; here is the lab's command run with `0`:

```console
$ uv run expenses add "Bar Ramon" 0
amount must be positive
$ echo $?
1
```

In typer you choose the number with `raise typer.Exit(code=1)`, as in the lab's shape:

```python
if amount <= 0:
    typer.echo("amount must be positive", err=True)
    raise typer.Exit(code=1)
```

`err=True` sends the message to standard error, the channel for error messages. Session 7 builds on exactly this: fail loudly at the boundary, with a message on stderr and a non-zero exit.

**Every tool downstream reads that number**, not your message:
- the shell: `cmd1 && cmd2` runs `cmd2` only if `cmd1` exited 0;
- CI: a step that exits non-zero turns the run red;
- tests: `CliRunner` gives you `result.exit_code` (session 8: "Session 5's exit code, now checked by a machine").

**"A program that prints an error and exits 0 is a program that lies."** Replace the `raise` with `print(...)` and `return`, and this happens:

```console
$ uv run expenses add "Bar Ramon" 0 && echo "expense saved"
amount must be positive
expense saved
```

The human sees an error; `&&`, CI and any script see success. `raise typer.Exit()` with no code tells the same lie, because its code is 0.

Two more numbers you will meet. When typer itself refuses the command line (a missing argument, a value it cannot convert, an unknown option), it exits with **2** before your function runs; your own checks use 1. And the slide's `-5.00` begins with a dash, so the typer version in the course's `uv.lock` reads it as an unknown option (`No such option: -5`, exit 2) before `add` can check it. The lab's test uses `0`, which reaches the check. Either way the exit code is non-zero, which is the slide's point. On paper, take slide 9's transcript as given.
""",
    [
        "0 means success, anything else failure; `echo $?` shows the last one.",
        "`raise typer.Exit(code=1)`; a bare `typer.Exit()` exits 0.",
        "The shell, `&&`, CI and tests read the number, not the text.",
        "A program that prints an error and exits 0 is a program that lies.",
    ],
    "Expect a transcript with `echo $?` or an `&&` chain and the question of what runs next, or a failing `exit_code` assertion. If the paper shows slide 9's own transcript (`add \"Bar Ramon\" -5.00`, `amount must be positive`, `1`), answer from the slide: the command's check failed and the exit code is 1.",
    "S5 slide 9; labs/01-scaffold.md §5–6; S7 slide 19; S8 slide 21",
    [22, 23, 25],
)

# ---------------------------------------------------------------- s7
section(
    7,
    "Renaming the template: six places, two spellings",
    """
Your repository was generated from `project-template`, whose package is called `app`. The lab's first job is to make it yours, and it starts with two names that are not interchangeable:

| | Form | Example | Used for |
|---|---|---|---|
| Distribution name | hyphens | `parking-lot` | the project, and the command you type |
| Package name | underscores | `parking_lot` | the folder under `src/`, and Python imports |

Python identifiers cannot contain hyphens (`import parking-lot` is a `SyntaxError: invalid syntax`), which is why there are two. The repository itself is named after your topic. Write both names down before you start.

**The six places.** Between them, the two names appear six times, and a typo in any one breaks the install:

1. the folder: `git mv src/app src/parking_lot`;
2. `name = "parking-lot"` under `[project]`;
3. `parking-lot = "parking_lot.cli:app"` under `[project.scripts]`, both spellings on one line;
4. `packages = ["src/parking_lot"]` under `[tool.hatch.build.targets.wheel]`;
5. `from parking_lot.cli import app` in `src/parking_lot/__main__.py`;
6. `from parking_lot.cli import app` in `tests/test_cli.py`.

What does not change is the typer object `app`, in `app = typer.Typer(...)` and after the colon. The lab's check is a search:

```console
$ grep -rnI "app" pyproject.toml src tests
pyproject.toml:12:parking-lot = "parking_lot.cli:app"
src/parking_lot/__main__.py:1:from app.cli import app
src/parking_lot/__main__.py:4:    app()
src/parking_lot/cli.py:3:app = typer.Typer(help="A parking lot: tickets and prices.")
tests/test_cli.py:3:from parking_lot.cli import app
...
```

Every `app` left should be the object or an import of it. A line that mentions `src/app` or `app.cli`, like line 1 of `__main__.py` above, is a rename you missed.

**Then re-lock, then install:** `uv lock`, then `uv sync`. `uv.lock` records your project under its old name, and CI's `uv sync --locked` refuses a lockfile that disagrees with `pyproject.toml`. The real `uv lock` run says it in two lines, `Removed app v0.1.0` and `Added parking-lot v0.1.0`. Commit `uv.lock` with everything else, then check that `uv run parking-lot --help` prints your help.
""",
    [
        "Hyphens for the project and the command (`parking-lot`); underscores for the package and imports (`parking_lot`).",
        "Six places: folder, `name`, `[project.scripts]`, wheel `packages`, `__main__.py`, `tests/test_cli.py`.",
        "The typer object `app` keeps its name.",
        "`uv lock`, then `uv sync`, then commit `uv.lock`.",
    ],
    "A question can show a half-renamed project (a `grep` output or a `pyproject.toml`) and ask which line was missed, or which spelling belongs where.",
    "S5 slide 12; labs/01-scaffold.md §2–4; project-template",
    [30, 31],
)

# ---------------------------------------------------------------- s8
section(
    8,
    "One real command, the four checks and v0.1",
    '''
With the names fixed, the lab asks for **one command of your own**, the smallest useful thing your project does. It must have at least one argument, one option with a default, a non-zero exit when the input makes no sense, and type hints on every parameter. The lab's shape is the `add` command from the exit-code section with an empty callback above it:

```python
@app.callback()
def main() -> None:
    """A terminal expense tracker."""
```

Notice that the shape has two arguments and no option; yours needs one, such as `--hours`. Keep the callback (the last section explains why). The command must be about your own project: a parking lot's `park` with `plate` and `--hours`, not `add` with the nouns swapped.

**Fix what the template left behind.** Rewrite `tests/test_cli.py` for your command, one test for the normal case and one for the failure, both through `CliRunner`. Delete the README's rename banner and say what the program does and for whom, how to install it (`uv sync`) and how to run it, with a real copy-pasteable example: "A stranger will mark it." Put your group's names in `LICENSE`; it currently names the lecturer, and the work is yours.

**Run the four checks CI runs**, before you push:

```bash
uv run ruff format .        # fixes formatting in place
uv run ruff check .         # lint
uv run mypy src tests       # types
uv run pytest               # tests
```

They are exactly what `.github/workflows/check.yml` runs. If they pass here, they pass there. Two details of `check.yml`: it first runs `uv sync --locked`, and it runs the formatter as `ruff format --check .`, which changes nothing and fails if a committed file would be reformatted. Format before you commit, or CI goes red at Formatting while your laptop looks clean.

**Commit, push, tag.** `git add -A`, `git commit -m "Scaffold the project"`, `git push`, then `git tag -a v0.1 -m "Scaffolded project"` and `git push origin v0.1`. A plain `git push` sends your commits and leaves the tag behind, so the tag needs that push of its own. A tag is a permanent name for one commit. Checkpoint 1 is marked at `v0.1`, so a missing tag means there is nothing to mark.

**Checkpoint 1: three binary items.**

1. `uv sync && uv run <your-app> --help` works from a clean clone.
2. `src/` layout, package importable.
3. README: what it does, how to install, how to run.

Prove items 1 and 2 the way the marker will: clone into an empty folder, `git checkout v0.1`, `uv sync`, `uv run <your-app> --help`, and `uv run python -c "import <your_package>; print('import OK')"`. A clean clone has no `.venv`, no caches and nothing you forgot to commit, so it catches the file that only exists on your laptop.
''',
    [
        "One command of your own: an argument, an option, a non-zero exit, type hints everywhere.",
        "Rewrite the tests, the README and the LICENSE; the template's versions are not yours.",
        "The four checks you run locally are the four CI runs.",
        "CP1: clean-clone install and `--help`; `src/` layout, importable; README says what, how to install, how to run.",
    ],
    "CP1 is the course's Definition of Done in miniature: public, binary, checkable. A question may ask which situation fails which item, or what a clean clone catches that your laptop cannot.",
    "S5 slides 12 and 14; labs/01-scaffold.md §5–10; S4 slide 17; project-template check.yml",
    [32, 33, 44],
)

# ---------------------------------------------------------------- s9
NO_CALLBACK_RUN = "$ uv run parking-lot park 1234ABC\n" + usage_err(
    "parking-lot [OPTIONS] {plate}", "parking-lot", "Got unexpected extra argument(s) (1234ABC)"
)

section(
    9,
    "The three that bite",
    f"""
Slide 13 names the three mistakes that turn the first push red. All three are in the lab's troubleshooting table, and each has a message you can learn to recognise.

**1. `uv lock` after renaming.** CI's first real step is `uv sync --locked`, which refuses a lockfile that disagrees with `pyproject.toml`:

{fence("text", LOCK_ERR)}

Run `uv lock`, commit `uv.lock`, push. One subtlety: on your laptop, `uv run` and `uv sync` quietly refresh a stale `uv.lock`, so everything works there. CI only sees the committed file, which is why committing `uv.lock` is half of the fix.

**2. `__main__.py` still imports `app.cli`.** pytest passes; mypy fails; CI is red:

{fence("text", MYPY_MAIN)}

The tests import `parking_lot.cli`, so they never load `__main__.py`; mypy reads every file under `src` and follows its imports. The error is real, not a matter of style: `uv run python -m parking_lot` crashes with `ModuleNotFoundError: No module named 'app'`. Fix the import; do not silence it.

**3. One command, no `@app.callback()`.** With a single command, typer assumes the command is the program and drops its name. The usage line loses `COMMAND`, `--help` lists no commands, and `<app> <command> ...` fails:

{fence("console", NO_CALLBACK_RUN)}

typer read the word `park` as the plate, so `1234ABC` was left over. Your tests, which call `runner.invoke(app, ["park", ...])`, fail with exit code 2. When the second parameter is also an argument (no default) whose type cannot take the shifted word, as with the lab's `amount: float`, the box says `Invalid value for 'amount'` instead, because typer converts every value before it checks for left-over ones. Here `hours` is an option, so `1234ABC` is simply left over. Same cause, different message: read the usage line. The empty callback from the lab tells typer that more commands will come, so yours keeps its name. The demo did the same from its first typer commit: `2ecad20` gave `cli.py` a single command, `report`, with an empty `@app.callback()` (`def main() -> None: pass`) above it, which is why `uv run expenses report` kept the word `report` before `add` existed.
""",
    [
        "Stale `uv.lock` → CI's `uv sync --locked` refuses it: run `uv lock`, commit `uv.lock`.",
        "`__main__.py` still importing `app.cli` → pytest green, mypy red: fix the import.",
        "One command and no `@app.callback()` → the command's name is swallowed: add the empty callback.",
    ],
    "This is the most examinable slide of the session: an error from CI or the terminal, and you name which of the three it is, why the other checks did not catch it, and the fix in words.",
    "S5 slide 13; labs/01-scaffold.md §4–5 and troubleshooting",
    [35, 36, 37],
)

# ================================================================ QUESTIONS

# ---------------------------------------------------------------- s1 questions
mcq(
    1,
    "core",
    ["concept"],
    """
Slide 4 of session 5 shows two ways to run the same code:

```bash
python tracker.py                    # a file, run by an interpreter
uv run expenses report               # a command, installed from a project
```

What does the second way have that the first does not?
""",
    [
        (
            False,
            "A faster interpreter, because `uv run` compiles the code before running it",
            "uv runs the same CPython on the same code. Speed is not the difference the slide draws; packaging is.",
        ),
        (
            True,
            "A name, a version, dependencies and an entry point, declared in `pyproject.toml`",
            "These are the slide's four words, and each is a line of `pyproject.toml`: `name`, `version`, `dependencies` and `[project.scripts]`.",
        ),
        (
            False,
            "Different code, rewritten so that typer is able to run it as a command",
            'The slide says "Same code." The code is identical; what changes is the project around it.',
        ),
        (
            False,
            "A system-wide install, so that `expenses` works in any terminal without `uv run`",
            "Installing writes the command into the project's `.venv/bin/`. Outside that environment a terminal has no `expenses` command, which is why you type `uv run`.",
        ),
    ],
    """
Slide 4: "Same code. The second one has a name, a version, dependencies and an entry point." In the expense-tracker these are `name = "expense-tracker"`, `version = "0.1.0"`, `dependencies = ["typer>=0.12"]` and `[project.scripts] expenses = "expense_tracker.cli:app"`. The file route depends on which interpreter you pick and which folder you stand in. The command route is resolved by `uv run` from `pyproject.toml` and `uv.lock`, so every teammate and CI get the same versions.
""",
    1,
    "S5 slide 4; S4 slides 19–23",
    verified="source",
)

mcq(
    2,
    "exam",
    ["read-tool-output", "judgement"],
    """
On the expense-tracker at `v0.4`, a teammate who missed session 5 runs the CLI file with the system Python:

```console
$ python3 src/expense_tracker/cli.py report
Traceback (most recent call last):
  File "src/expense_tracker/cli.py", line 5, in <module>
    import typer
ModuleNotFoundError: No module named 'typer'
```

`uv run expenses report` works on the same laptop, in the same folder. What explains the difference?
""",
    [
        (
            False,
            "typer is missing from `pyproject.toml` and has to be added to `dependencies`",
            "It is already there (`typer>=0.12`). If it were missing, `uv run expenses report` would fail too.",
        ),
        (
            False,
            "The laptop needs `pip install typer`, so that every Python on it has typer",
            "The careless fix: it installs an unpinned copy outside the project, invisible to teammates and CI. The project's environment already has the pinned typer.",
        ),
        (
            True,
            "`python3` is the system interpreter; typer is only in the project's `.venv`",
            "A file run by an interpreter gets that interpreter's packages. `uv run` runs the command inside the environment built from `pyproject.toml` and `uv.lock`.",
        ),
        (
            False,
            "Line 5 of `cli.py` contains a mistake, and the import should be written differently",
            "`import typer` is correct. The message says the module was not found, not that the line is wrong.",
        ),
    ],
    """
The first command is "a file, run by an interpreter": you chose `python3`, and it only has the packages installed for it. typer lives in the project's environment, which uv builds from `pyproject.toml` and the pinned `uv.lock`. `uv run expenses report` resolves that environment, installs what is missing and runs the command, which is why it works from the same folder. The fix is to use the project's door, not to install packages by hand where nobody else can see them.
""",
    1,
    "S5 slide 4; S4 slide 23",
    origin="history",
)

mcq(
    3,
    "hard",
    ["read-code", "predict-output"],
    """
Same project, `v0.4`. This time the teammate uses the project's interpreter:

```console
$ uv run python src/expense_tracker/cli.py report
$ echo $?
0
```

Nothing is printed. This is the shape of the whole file:

```python
import csv
import datetime
from pathlib import Path

import typer

from expense_tracker.report import (...)

DATA_FILE = Path("data") / "expenses.csv"

app = typer.Typer(help="A terminal expense tracker.")


@app.callback()
def main() -> None:
    pass


@app.command()
def report(...) -> None:
    ...


@app.command()
def add(...) -> None:
    ...
```

Why did no report appear?
""",
    [
        (
            True,
            "Running the file defines `app` and its commands, but no line calls `app()`",
            "A file runs top to bottom. Nothing at the top level hands the command line to typer, so `report` never runs. The wrapper and `__main__.py` exist to make that call.",
        ),
        (
            False,
            "The report went to stderr, which the terminal hides when the exit code is 0",
            "The terminal shows stderr whatever the exit code. Nothing was printed on either channel because nothing ran.",
        ),
        (
            False,
            "`report` found no rows in `expenses.csv`, so it had nothing to print",
            'The report always starts with a header line ("Expense report for ..."). An empty file would still print it.',
        ),
        (
            False,
            "`uv run` only accepts commands, so it skipped the file and exited",
            "`uv run python file.py` does run the file, with the project's interpreter. That is why there is no `No module named 'typer'` this time.",
        ),
    ],
    """
A file run by an interpreter executes its top-level statements: imports, `DATA_FILE`, `app = typer.Typer(...)`, and the `def`s with their decorators. Defining a command is not running it. Something has to call `app()`: the wrapper that `[project.scripts]` writes on install, or `__main__.py` for `python -m`. The template's `cli.py` ends with `if __name__ == "__main__": app()`; the demo's does not. The exit code 0 is honest here: nothing failed, because nothing ran. The program's door is `uv run expenses report`.
""",
    1,
    "S5 slides 4–6; expense-tracker v0.4 cli.py",
    origin="history",
)

# ---------------------------------------------------------------- s2 questions
mcq(
    4,
    "core",
    ["concept", "read-tool-output"],
    """
A teammate edits one line of the expense-tracker's `pyproject.toml`, changes nothing else and runs `uv sync`:

```toml
[project.scripts]
spend = "expense_tracker.cli:app"
```

Their next command fails:

```console
$ uv run expenses report
error: Failed to spawn: `expenses`
  cause: No such file or directory (os error 2)
```

Which statement explains the error?
""",
    [
        (
            False,
            "uv could not download a package called `expenses` from PyPI when it ran the command",
            "Nothing is downloaded when a command runs; packages come from `dependencies`. The message says uv tried to start a program called `expenses` and found none.",
        ),
        (
            False,
            "The module path is wrong, so Python cannot import `expense_tracker.cli` and start `app`",
            "An import problem would be a `ModuleNotFoundError` or `ImportError` raised by an existing wrapper. The right side of the line is unchanged, and no wrapper named `expenses` exists to run.",
        ),
        (
            False,
            "`uv.lock` is out of date and must be refreshed with `uv lock` before any command runs",
            "The lockfile records dependencies, not command names, and `uv lock --check` still passes. Refreshing it would not bring `expenses` back.",
        ),
        (
            True,
            "The left side names the command; it is now `spend`, so `expenses` no longer exists",
            "Slide 5: the left side is the command, and renaming either side makes the old command disappear. After `uv sync` the wrapper in `.venv/bin/` is called `spend`.",
        ),
    ],
    """
Slide 5 reads the line as command, module, object, and says: "Rename either side and the command disappears." Here the left side was renamed. On install, uv writes a wrapper named after the left side into `.venv/bin/`, and `uv sync` replaced the old wrapper `expenses` with a new one, `spend`. `uv run expenses` has nothing to start, which is lab 01's `Failed to spawn` row. `uv run spend report` works. The module and the object on the right still exist, so no import error appears. Real run: `uv lock --check` passed after the edit.
""",
    2,
    "S5 slide 5; labs/01-scaffold.md troubleshooting",
    verified="run",
)

mcq(
    5,
    "exam",
    ["read-diff", "concept"],
    """
Commit `2ecad20` ("Move the report into the package behind a typer CLI") changed these lines of `pyproject.toml`:

```diff
 [project.scripts]
-expense-tracker = "expense_tracker:main"
+expenses = "expense_tracker.cli:app"
```

After this commit and `uv sync`, what does `uv run expenses report` run?
""",
    [
        (
            True,
            "The object `app` in `expense_tracker.cli`, which reads `report` as a command",
            "The right side changed to `expense_tracker.cli:app`: module `expense_tracker.cli`, object `app`, the typer app that knows `report`.",
        ),
        (
            False,
            "The function `main` in `src/expense_tracker/__init__.py`, as before the commit",
            "That was the old right side. The diff replaces it, and `2ecad20` also deletes `main` from `__init__.py`.",
        ),
        (
            False,
            "The file `cli.py` from top to bottom, as `python cli.py report` would",
            "The wrapper imports `app` and calls it. Run as a file, `cli.py` would only define `app`.",
        ),
        (
            False,
            "The package's `__main__.py`, which every installed command goes through",
            "The command goes through the wrapper written from `[project.scripts]`; the demo has no `__main__.py` at all.",
        ),
    ],
    """
Read the new line as slide 5 does: command `expenses` → module `expense_tracker.cli` → object `app`. On install, uv writes a wrapper that runs `from expense_tracker.cli import app` and `sys.exit(app())`, and typer reads `report` from the command line. The left side changed too, so the old command is gone: on this commit, `uv run expense-tracker report` gives `error: Failed to spawn`. The project stays `expense-tracker`; only the command became `expenses`.
""",
    2,
    "expense-tracker 2ecad20; S5 slide 5",
    origin="history",
)

mcq(
    6,
    "exam",
    ["read-tool-output", "judgement"],
    """
Your group is renaming the template to `parking-lot`. You moved the folder to `src/parking_lot`, fixed `name`, the wheel `packages` line and both imports, and ran `uv lock` and `uv sync`. Then:

```console
$ uv run parking-lot --help
error: Failed to spawn: `parking-lot`
  cause: No such file or directory (os error 2)
```

`pyproject.toml` still contains:

```toml
[project.scripts]
app = "app.cli:app"
```

What is the problem?
""",
    [
        (
            False,
            "`uv.lock` is still out of date; run `uv lock` once more and the command appears",
            "A stale lockfile gives a different message (`needs to be updated`), and the lockfile records versions, not commands.",
        ),
        (
            True,
            "The left side of `[project.scripts]` is still `app`, so no `parking-lot` exists",
            'No line names `parking-lot`, so no wrapper was written for it. Both sides need the new names: `parking-lot = "parking_lot.cli:app"`.',
        ),
        (
            False,
            "The `.venv` is damaged; delete it and run `uv sync` to rebuild it from scratch",
            "The careless move. A fresh environment installs exactly the same wrong command, because it reads the same table.",
        ),
        (
            False,
            "The package folder must be called `src/parking-lot` so that it matches the command",
            "Python packages cannot contain hyphens. The folder uses underscores; only the command uses hyphens.",
        ),
    ],
    """
`Failed to spawn` means uv found no command by that name in the environment. The lab's troubleshooting table gives the cause: "`[project.scripts]` does not match the command you typed". Here the left side is still `app`, so the command you can type is `app`, and its right side still points at `app.cli`, a module that no longer exists. Running it confirms both halves are wrong:

```console
$ uv run app --help
Traceback (most recent call last):
  File ".venv/bin/app", line 4, in <module>
    from app.cli import app
ModuleNotFoundError: No module named 'app'
```

The fix is the third of the six places: `parking-lot = "parking_lot.cli:app"`.
""",
    2,
    "labs/01-scaffold.md §3 and troubleshooting; S5 slide 5",
    origin="lab",
)

mcq(
    7,
    "hard",
    ["read-tool-output"],
    """
A teammate tidied up `src/parking_lot/cli.py` and pushed. Now:

```console
$ uv run parking-lot --help
Traceback (most recent call last):
  File ".venv/bin/parking-lot", line 4, in <module>
    from parking_lot.cli import app
ImportError: cannot import name 'app' from 'parking_lot.cli' (src/parking_lot/cli.py)
```

`[project.scripts]` says `parking-lot = "parking_lot.cli:app"`. What did the teammate most likely change?
""",
    [
        (
            False,
            "They renamed the package folder, so Python can no longer find `parking_lot`",
            "Then the error would be `ModuleNotFoundError: No module named 'parking_lot'`. Here the module was found: its file path is printed.",
        ),
        (
            False,
            "They broke `__main__.py`, which the command loads before `cli.py`",
            "The wrapper never touches `__main__.py`. The traceback shows it importing straight from `parking_lot.cli`.",
        ),
        (
            True,
            "They renamed the typer object in `cli.py`, so no `app` exists to import",
            "Module found, object missing. For example `app = typer.Typer(...)` became `cli = typer.Typer(...)`, and the wrapper still asks for `app`.",
        ),
        (
            False,
            "They removed typer from the dependencies, so `cli.py` can no longer import it",
            "Then the message would name typer (`No module named 'typer'`), not the object `app`.",
        ),
    ],
    """
Read the traceback the way slide 5 reads the line: command → module → object. The first frame is the wrapper in `.venv/bin/parking-lot`, so the command exists. Its import found the module, because the message prints the path of `cli.py`. What failed is the object after the colon. The rename moved the object, not the line, and "rename either side and the command disappears". This is why the lab says the one `app` that must stay is the typer object itself. Real run: renaming `app` to `cli` in `cli.py` produced exactly this `ImportError`.
""",
    2,
    "S5 slide 5; labs/01-scaffold.md §3",
    origin="lab",
)

# ---------------------------------------------------------------- s3 questions
mcq(
    8,
    "core",
    ["concept"],
    """
The template ships `src/app/__main__.py`:

```python
from app.cli import app

if __name__ == "__main__":
    app()
```

What does this file give the project?
""",
    [
        (
            False,
            "It marks `src/app/` as a package, so that `import app` can work at all",
            "That is the job of `__init__.py`, which the session 4 anatomy lists separately.",
        ),
        (
            False,
            "It is the file `uv run app` executes, so without it the command fails",
            "The command goes through the wrapper written from `[project.scripts]`, which imports `app.cli` directly.",
        ),
        (
            False,
            "It holds the command-line tests, which pytest discovers by the file name",
            "Tests live in `tests/` in files called `test_*.py`. `__main__.py` is part of the package.",
        ),
        (
            True,
            "A second way in: `python -m app` runs it, and it calls the same `app`",
            "Slide 6: the other door. It does not read `[project.scripts]` and needs no wrapper, only an importable package.",
        ),
    ],
    """
`python -m <package>` makes Python find the package and run its `__main__.py`. The template's file imports the same `app` object as the command does and calls it, so both doors lead to one program. Slide 6 adds two facts worth keeping: it "works without the install step", because it does not depend on the wrapper; and "the template ships one, and it is the file everyone forgets to rename".
""",
    3,
    "S5 slide 6; S4 slide 20",
    verified="source",
)

mcq(
    9,
    "exam",
    ["read-tool-output", "judgement"],
    """
A teammate tries both doors on your renamed project (`parking-lot` / `parking_lot`):

```console
$ uv run parking-lot park 1234ABC
Ticket for 1234ABC: 1 h
$ uv run python -m parking_lot park 1234ABC
Traceback (most recent call last):
  File "<frozen runpy>", line 203, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "src/parking_lot/__main__.py", line 1, in <module>
    from app.cli import app
ModuleNotFoundError: No module named 'app'
```

What can you conclude?
""",
    [
        (
            False,
            "The package was never installed; run `uv sync` and both doors will work",
            "The command imports `parking_lot.cli` from the same environment and works, so the package is installed. The module Python cannot find is `app`.",
        ),
        (
            False,
            "`[project.scripts]` still points at `app.cli`, so the `-m` door cannot find it",
            "`python -m` never reads `[project.scripts]`, and the working command shows that line is already right.",
        ),
        (
            True,
            "`__main__.py` still imports the old `app`; the command never loads that file",
            "The last frame is line 1 of `src/parking_lot/__main__.py`. The command goes through the wrapper, which imports `parking_lot.cli` directly.",
        ),
        (
            False,
            "`python -m` cannot run packages that live under `src/`, so use the command only",
            "Python found and started `src/parking_lot/__main__.py`; the crash is inside it, at the old import.",
        ),
    ],
    """
Read the last frame: the crash is on line 1 of `src/parking_lot/__main__.py`, which still says `from app.cli import app`. The two doors are independent. The command's wrapper was written from `parking-lot = "parking_lot.cli:app"` and imports the renamed module, so it works; `python -m` runs `__main__.py`, the file everyone forgets to rename. The tests import `parking_lot.cli` too, so pytest stays green, and mypy is the check that reports this file. The fix is one import.
""",
    3,
    "S5 slide 6; labs/01-scaffold.md §3c and troubleshooting",
    origin="lab",
)

open_q(
    10,
    "exam",
    ["concept", "read-tool-output"],
    """
A new teammate joins your group (project `parking-lot`, package `parking_lot`). The README says `uv run parking-lot park 1234ABC`; another teammate always types `uv run python -m parking_lot park 1234ABC`. Yesterday someone deleted the `[project.scripts]` table by accident, and this happened:

```console
$ uv run parking-lot park 1234ABC
error: Failed to spawn: `parking-lot`
  cause: No such file or directory (os error 2)
$ uv run python -m parking_lot park 1234ABC
Ticket for 1234ABC: 1 h
```

Explain the two doors to the new teammate.
""",
    [
        P(
            "On a healthy project, what happens, step by step, when you type `uv run parking-lot park 1234ABC`?",
            2,
            '`uv run` makes `.venv` match `pyproject.toml` and `uv.lock`, then runs the command `parking-lot`. That command is a wrapper uv wrote on install from `parking-lot = "parking_lot.cli:app"`: it imports the module `parking_lot.cli`, takes the object `app` and calls it, and typer reads `park 1234ABC`.',
            [
                "Says the command comes from the `[project.scripts]` line: command → module `parking_lot.cli` → object `app`",
                "Says a wrapper is written into the environment on install and it imports `app` and calls it",
                "Mentions that `uv run` first brings the environment in line with `pyproject.toml` and `uv.lock`",
            ],
            'A common answer is just "uv runs `cli.py`". It misses the mechanism the slide teaches: the name is looked up in `[project.scripts]`, and an installed wrapper imports the object and calls it. Saying "it runs the package" is too vague to earn either mark. Mentioning only that uv installs dependencies, without how the command is found, gets one mark at most.',
        ),
        P(
            "Why does the second command still work after the table was deleted?",
            2,
            "`python -m parking_lot` does not read `[project.scripts]` and needs no wrapper. Python finds the package and runs its `__main__.py`, which imports the same `app` from `parking_lot.cli` and calls it. The doors lead to the same program but fail independently.",
            [
                "Says `python -m` runs the package's `__main__.py`",
                "Says this door does not depend on `[project.scripts]` or the wrapper",
                "Says both doors end at the same `app` object",
            ],
            'Weak answers say "`-m` is more reliable" or "it bypasses uv". It does not bypass uv here (`uv run python` still picks the project\'s interpreter); it bypasses the wrapper. Full marks need the file it runs (`__main__.py`) and the reason it does not care about the deleted table.',
        ),
        P(
            "After a later rename, `uv run parking-lot` works but `uv run python -m parking_lot` fails. Which file do you check first, and why is it easy to forget?",
            2,
            "`src/parking_lot/__main__.py`: it probably still imports `app.cli`. Nothing in the normal workflow loads it, because the command goes through the wrapper and the tests import `parking_lot.cli`, so only mypy or using `-m` reveals it.",
            [
                "Names `__main__.py` and its import of the old name (`app.cli`)",
                "Explains that neither the command nor the tests load `__main__.py`, so only mypy or `python -m` shows the problem",
            ],
            "Naming `cli.py` or `pyproject.toml` misses that the working command proves both are fine. Naming `__main__.py` without saying why it slips through (the tests and the command never load it) earns one mark.",
        ),
    ],
    """
This question checks that you can tell the two doors apart: what each needs, and what breaks each one. The command door is `[project.scripts]` plus the wrapper written on install; the `-m` door is `__main__.py`. Both call the same `app`. The transcript is real: with the table deleted, uv has no `parking-lot` command to spawn, while `python -m` still runs `__main__.py`. Part 3 connects to the second of the three that bite.
""",
    3,
    "S5 slides 5–6; labs/01-scaffold.md troubleshooting",
    "6–8",
    origin="lab",
)

# ---------------------------------------------------------------- s4 questions
mcq(
    11,
    "core",
    ["concept"],
    """
In typer, what decides whether a function parameter becomes an argument or an option on the command line?
""",
    [
        (
            True,
            "Whether it has a default: none gives an argument, one gives an option",
            'Slide 7: "a default is what turns a parameter into an option". Slide 8 repeats it in the "In Python" row.',
        ),
        (
            False,
            "Its type hint: `str` parameters become arguments and numbers become options",
            "In slide 7, `amount: float` is an argument. The type decides how the text is converted, not which kind it is.",
        ),
        (
            False,
            "Its position: the first parameter is the argument and the rest are options",
            "The demo's `add` at `v0.4` has three arguments in a row: `merchant`, `category`, `amount`.",
        ),
        (
            False,
            "Whether it has a `help=` text: documented parameters become options",
            "`report`'s `path` has `help=` and is an argument. Help text only shows up in `--help`.",
        ),
    ],
    """
The rule is about the default. `def add(merchant: str, amount: float)` has two arguments because neither has a default; `date: str = typer.Option("", ...)` in the demo's `add` is an option because it has one. The type hint still matters: it is how typer converts and checks the value. The one way to have a default and stay positional is `typer.Argument(default)`, as `report`'s `path` does.
""",
    4,
    "S5 slides 7–8",
    verified="source",
)

mcq(
    12,
    "exam",
    ["predict-output", "read-code"],
    """
The `add` command of the expense-tracker at `v0.4`:

```python
@app.command()
def add(
    merchant: str,
    category: str,
    amount: float,
    date: str = typer.Option("", help="YYYY-MM-DD, defaults to today."),
) -> None:
```

Which usage line does `uv run expenses add --help` print? (The typer version pinned in the course's `uv.lock` writes argument names in braces.)
""",
    [
        (
            False,
            "`Usage: expenses add [OPTIONS] {merchant} {category} {amount} {date}`",
            "`date` has a default, so it is an option. Options are summarised by `[OPTIONS]` and listed as `--date` in the help.",
        ),
        (
            True,
            "`Usage: expenses add [OPTIONS] {merchant} {category} {amount}`",
            "Three parameters without defaults are three required arguments, in order; `--date` hides inside `[OPTIONS]`.",
        ),
        (
            False,
            "`Usage: expenses add [OPTIONS] {merchant}`",
            "This treats only the first parameter as an argument. Position does not decide; the default does.",
        ),
        (
            False,
            "`Usage: expenses add [OPTIONS] [merchant] [category] [amount]`",
            "Square brackets mark an argument you may leave out. These three have no default, so the help marks each `[required]`.",
        ),
    ],
    """
typer builds the usage line from the signature: the command name, `[OPTIONS]` for everything with a default, then each argument in order. Run on the repository, the help shows `Usage: expenses add [OPTIONS] {merchant} {category} {amount}`, an Arguments box with three `[required]` entries, and `--date` in the Options box. In slide 7's capitals style (`MERCHANT AMOUNT` for the lab's two-argument `add`) this line would read `MERCHANT CATEGORY AMOUNT`; braces or capitals, the reading is identical. `--help` is generated, never written.
""",
    4,
    "S5 slide 7; expense-tracker v0.4 cli.py",
    origin="history",
)

mcq(
    13,
    "hard",
    ["read-tool-output"],
    f"""
With the lab's `add(merchant: str, amount: float)`:

```console
$ uv run expenses add Bar Ramon 12.50
{usage_err("expenses add [OPTIONS] {merchant} {amount}", "expenses add", "Invalid value for 'amount': 'Ramon' is not a valid float.")}
$ echo $?
2
```

What happened?
""",
    [
        (
            False,
            "typer cannot read decimals such as `12.50`, so amounts must be whole numbers",
            '`12.50` was never looked at, and `add "Bar Ramon" 12.50` works. The value typer refused is `Ramon`.',
        ),
        (
            False,
            "The function's own check rejected the amount, and it chose exit code 2 for that",
            "The function never ran. Its own check prints `amount must be positive` and exits 1; the boxed error is typer's.",
        ),
        (
            False,
            "`merchant` has to be passed as `--merchant`, because its type hint is `str`",
            "`merchant` has no default, so it is an argument. The type never makes something an option.",
        ),
        (
            True,
            "Unquoted, `Bar Ramon` is two words, so `Ramon` filled `amount` and failed",
            "Arguments are filled in order: `merchant` = `Bar`, `amount` = `Ramon`. typer converts with the `float` hint before calling `add`.",
        ),
    ],
    """
Arguments are positional, and the shell splits unquoted words, so `add` received three values: `Bar`, `Ramon`, `12.50`. typer filled `merchant` with `Bar` and tried to turn `Ramon` into the `float` the type hint asks for. That failed, so typer refused the whole command line with exit code 2 before your function ran. The type hints are the specification and the first check. Typing it as the lab does, `add "Bar Ramon" 12.50`, gives `Added Bar Ramon: 12.50`.
""",
    4,
    "S5 slides 7–8; labs/01-scaffold.md §5",
    origin="lab",
)

# ---------------------------------------------------------------- s5 questions
mcq(
    14,
    "core",
    ["concept", "judgement"],
    """
Your group's gradebook gets a `report` command. It must read a grades file, and it can round the averages to one decimal if the user asks. Following the session 5 table, how should the two be exposed?
""",
    [
        (
            False,
            "Both as options, so that users can type them in any order they like",
            "The file is what the command acts on. As an option it would silently fall back to a default when forgotten.",
        ),
        (
            False,
            "Both as arguments, so that the user always states both explicitly",
            "Rounding is how the command behaves and has a sensible default. Forcing it on every call is noise.",
        ),
        (
            True,
            "The grades file as an argument, the rounding as an option with a default",
            "What it acts on is an argument (missing means error); how it behaves is an option (missing means default).",
        ),
        (
            False,
            "The rounding as an argument, the grades file as an option with a default",
            "This reverses the table: the thing acted on becomes optional and the behaviour becomes compulsory.",
        ),
    ],
    """
Slide 8's "For" row: an argument is what the command acts on, an option is how it behaves. The "Missing" row follows from it: a missing argument is an error, a missing option falls back to its default. The demo does the same thing: `report [path] --category --min`, where the file is an argument (optional only through `typer.Argument("expenses.csv")`) and the filters are options.
""",
    5,
    "S5 slide 8",
    verified="source",
)

mcq(
    15,
    "core",
    ["read-code", "concept"],
    """
The expense-tracker declares `report` like this:

```python
@app.command()
def report(
    path: str = typer.Argument("expenses.csv", help="CSV file to read."),
    category: str = typer.Option("", help="Only this category."),
    minimum: float = typer.Option(0.0, "--minimum", "--min", help="Ignore amounts below this."),
) -> None:
```

What does `typer.Argument("expenses.csv", ...)` do for `path`?
""",
    [
        (
            True,
            "It keeps `path` positional but optional, defaulting to `expenses.csv`",
            "Slide 8: `typer.Argument(...)` overrides the default rule. The usage line shows `[path]`, an argument you may leave out.",
        ),
        (
            False,
            "It makes `path` required, so `expenses report` without a file is an error",
            "The first value is the default. `uv run expenses report` reads `expenses.csv`, as the README shows.",
        ),
        (
            False,
            "It turns `path` into an option, so users type `--path data/expenses.csv`",
            "That is what a plain default would do. `typer.Argument` exists to prevent it.",
        ),
        (
            False,
            "It checks that the file exists before `report` is allowed to run",
            "typer does not check files here. A missing file is handled by `report` itself: `could not read nosuch.csv`, exit 1.",
        ),
    ],
    """
A parameter with a default becomes an option "even when a positional value was intended", and `typer.Argument(...)` overrides that. The real help shows `Usage: expenses report [OPTIONS] [path]` with `[default: expenses.csv]`. So `uv run expenses report` reads the sample file and `uv run expenses report data/expenses.csv` reads the file that `add` writes, both positional. The two filters use `typer.Option`, which is what a default would have given them anyway, plus help text and a short alias.
""",
    5,
    "S5 slide 8; expense-tracker 2ecad20",
    origin="history",
)

mcq(
    16,
    "exam",
    ["read-tool-output", "predict-output"],
    f"""
Your teammate's command and its help:

```python
@app.command()
def park(plate: str, hours: int = 1) -> None:
```

{fence("text", HELP_PARK)}

Which of these commands does typer accept?
""",
    [
        (
            False,
            "`uv run parking-lot park --plate 1234ABC`",
            "`plate` has no default, so it is an argument with no `--plate` form. Real result: `No such option: --plate`.",
        ),
        (
            True,
            "`uv run parking-lot park 1234ABC --hours 3`",
            "The argument by position, the option by name. Real result: `Ticket for 1234ABC: 3 h`.",
        ),
        (
            False,
            "`uv run parking-lot park 1234ABC 3`",
            "`hours` is an option, so a bare `3` has no slot. Real result: `Got unexpected extra argument(s) (3)`.",
        ),
        (
            False,
            "`uv run parking-lot park --hours 3`",
            "A missing argument is an error, not a default. Real result: `Missing argument 'plate'.`",
        ),
    ],
    """
Read the help as the table: `{plate}` after `[OPTIONS]` is a required argument, typed by position; `--hours` is an option with `[default: 1]`, typed by name or left out. All three wrong commands are refused by typer itself with exit code 2 before `park` runs, each with the message quoted in its explanation. The help was generated from the two-parameter signature; nobody wrote it.
""",
    5,
    "S5 slides 7–8",
    origin="lab",
)

mcq(
    17,
    "exam",
    ["read-tool-output", "read-code"],
    f"""
A student gives the lab's `amount` a default, to make it optional:

```python
@app.command()
def add(merchant: str, amount: float = 0.0) -> None:
```

```console
$ uv run expenses add "Bar Ramon" 12.50
{usage_err("expenses add [OPTIONS] {merchant}", "expenses add", "Got unexpected extra argument(s) (12.50)")}
```

What is the cause?
""",
    [
        (
            False,
            "`12.50` is not a valid float for typer, so it is reported as an extra value",
            "Floats like `12.50` convert fine; the same call worked before the change. The value has no slot, which is a different problem.",
        ),
        (
            False,
            "`merchant` needs a default as well, so typer can tell where it ends",
            "That would turn `merchant` into `--merchant` too. Defaults caused the problem, and another one cannot cure it.",
        ),
        (
            False,
            "The shell split `Bar Ramon` into two words, so one word was left over",
            '`"Bar Ramon"` is quoted, so it arrives as one value. The leftover typer names is `12.50`, not `Ramon`.',
        ),
        (
            True,
            "The default made `amount` the option `--amount`, so `12.50` has no slot",
            "The usage line no longer lists `{amount}`. A positional value with nowhere to go is an extra argument.",
        ),
    ],
    """
"A parameter with a default becomes an option, even when a positional value was intended." The usage line has lost `{amount}`, and the help now lists `--amount <float> [default: 0.0]`. Worse than the error: typer now accepts `uv run expenses add "Bar Ramon"` and calls `add` with 0.0, so a forgotten amount is caught only by the function's own check (`amount must be positive`, exit 1) instead of by typer's `Missing argument`. The lab's troubleshooting row gives both fixes: drop the default, or use `typer.Argument(...)` if the value should be positional and optional.
""",
    5,
    "S5 slide 8; labs/01-scaffold.md troubleshooting",
    origin="lab",
)

mcq(
    18,
    "exam",
    ["read-tool-output", "read-code"],
    f"""
The README of the expense-tracker says `uv run expenses report data/expenses.csv`. A teammate tidies `report` by replacing

```python
path: str = typer.Argument("expenses.csv", help="CSV file to read."),
```

with `path: str = "expenses.csv",`. Now:

```console
$ uv run expenses report data/expenses.csv
{usage_err("expenses report [OPTIONS]", "expenses report", "Got unexpected extra argument(s) (data/expenses.csv)")}
```

What has happened?
""",
    [
        (
            False,
            "`data/expenses.csv` does not exist yet, so typer refuses to accept the path",
            "typer does not check files. A missing file is handled inside `report`: `could not read ...`, exit 1. The box is about an extra argument.",
        ),
        (
            False,
            "The README is out of date: `report` never accepted a file path at all",
            "It did, from `v0.1` to `v0.4`, through `typer.Argument`. The README describes the real interface.",
        ),
        (
            True,
            "The plain default made `path` the option `--path`, so the file has no slot",
            "The usage line lost `[path]`. Restoring `typer.Argument` brings back the positional, optional file.",
        ),
        (
            False,
            "typer only accepts paths that start with `./`, so it needs `./data/expenses.csv`",
            "No such rule exists. typer receives a string either way; the problem is that the string has no slot.",
        ),
    ],
    f"""
Removing `typer.Argument` left a plain default, and a default turns a parameter into an option. The real help now reads:

{fence("text", HELP_REPORT_NO_ARGUMENT)}

The tidy-up changed the interface and broke the README's example. It also breaks the demo's own test from session 8: `runner.invoke(app, ["report", "nosuch.csv"])` now gets exit code 2 instead of 1 (`assert 2 == 1`). Restore `typer.Argument("expenses.csv", ...)`.
""",
    5,
    "S5 slide 8; expense-tracker v0.4 cli.py and tests/test_io.py",
    origin="history",
)

mcq(
    19,
    "exam",
    ["compare", "read-code"],
    """
You inherit a parking script built on `argparse`:

```python
parser = argparse.ArgumentParser()
parser.add_argument("plate")
parser.add_argument("--hours", type=int, default=1)
```

```console
$ python park.py --help
usage: park.py [-h] [--hours HOURS] plate

positional arguments:
  plate

options:
  -h, --help     show this help message and exit
  --hours HOURS
```

Which typer signature describes the same command-line interface?
""",
    [
        (
            True,
            "`def park(plate: str, hours: int = 1) -> None`",
            "No default makes `plate` an argument; the default makes `hours` the option `--hours`; `int` matches `type=int`.",
        ),
        (
            False,
            '`def park(plate: str = "", hours: int = 1) -> None`',
            "The default turns `plate` into `--plate`, an option. In argparse it is positional and required.",
        ),
        (
            False,
            "`def park(plate: str, hours: int) -> None`",
            "Without a default, `hours` becomes a second required argument instead of an optional `--hours`.",
        ),
        (
            False,
            '`def park(hours: int, plate: str = "") -> None`',
            "This swaps the roles: `hours` becomes the required argument and `plate` an option.",
        ),
    ],
    """
Slide 10's argparse code and the typer rule describe the same table. In argparse a name without dashes is positional and `--hours` with `default=1` is an option; in typer a parameter without a default is an argument and one with a default is an option, and the type hint does the job of `type=int`. Both versions refuse a call without a plate with exit code 2 (`park.py: error: the following arguments are required: plate` and `Missing argument 'plate'.`). argparse needs no dependency but more code; this course uses typer.
""",
    5,
    "S5 slide 10; S5 slides 7–8",
)

sort_q(
    20,
    "core",
    ["read-code", "concept"],
    """
Each line is a parameter from a real typer command seen in this module. Sort it by what typer makes of it on the command line.
""",
    [
        ("required", "Required argument"),
        ("optional", "Optional argument"),
        ("option", "Option"),
    ],
    [
        (
            "`merchant: str` in the lab's `add`",
            "required",
            "No default, so it is an argument, and a missing argument is an error.",
        ),
        (
            "`amount: float` in the lab's `add`",
            "required",
            "The type is `float`, but types do not make options. No default, so required argument.",
        ),
        (
            '`path: str = typer.Argument("expenses.csv", help="CSV file to read.")` in `report`',
            "optional",
            "`typer.Argument` keeps it positional; its default makes it optional, shown as `[path]`.",
        ),
        (
            '`category: str = typer.Option("", help="Only this category.")` in `report`',
            "option",
            "Given by name as `--category dining`; missing means the empty default, all categories.",
        ),
        (
            '`date: str = typer.Option("", help="YYYY-MM-DD, defaults to today.")` in the demo\'s `add`',
            "option",
            "How the command behaves: a different date from today. Typed as `--date 2026-03-01`.",
        ),
        (
            "`plate: str` in `park`",
            "required",
            "What the command acts on, with no default: `parking-lot park 1234ABC`.",
        ),
        (
            "`hours: int = 1` in `park`",
            "option",
            "A plain default makes an option: `--hours 3`, or 1 when left out.",
        ),
        (
            "`amount: float = 0.0` in a student's `add`",
            "option",
            'The default turned it into `--amount`, which is why `add "Bar Ramon" 12.50` is refused.',
        ),
    ],
    """
One rule and one override sort every line. No default: required argument. A plain default (or `typer.Option`): option. `typer.Argument(default)`: optional argument, written in square brackets in the usage line. The type hint never decides the kind; it only tells typer how to convert the text. Every classification here matches the real `--help` output of the command it comes from.
""",
    5,
    "S5 slides 7–8; expense-tracker cli.py; labs/01-scaffold.md",
)

open_q(
    21,
    "hard",
    ["compare", "read-tool-output", "judgement"],
    """
The same parking command, written twice. The `argparse` version, run without a plate:

```python
parser = argparse.ArgumentParser()
parser.add_argument("plate")
parser.add_argument("--hours", type=int, default=1)
```

```console
$ python park.py
usage: park.py [-h] [--hours HOURS] plate
park.py: error: the following arguments are required: plate
$ echo $?
2
```

The typer version, run the same way:

```python
@app.command()
def park(plate: str, hours: int = 1) -> None:
    ...
```

```console
$ uv run parking-lot park --hours 3
Usage: parking-lot park [OPTIONS] {plate}
Try 'parking-lot park --help' for help.
╭─ Error ──────────────────────────────────────────────────────────────────────╮
│ Missing argument 'plate'.                                                    │
╰──────────────────────────────────────────────────────────────────────────────╯
$ echo $?
2
```
""",
    [
        P(
            "Both versions describe the same interface. Which value is the argument and which the option, and how does each library decide?",
            2,
            "`plate` is the argument: it is what the command acts on and it is required. `--hours` is an option with default 1. argparse decides by the name you register (no dashes is positional, `--hours` an option); typer decides by the signature (no default is an argument, a default an option).",
            [
                "Identifies `plate` as the required argument and `--hours` as the option with default 1",
                "argparse's rule: a name without dashes is positional, a `--` name is an option",
                "typer's rule: no default gives an argument, a default gives an option",
            ],
            'Many answers name the argument and the option correctly but stop there, which is one mark. Saying typer decides by the type ("int becomes an option") is the classic confusion: `amount: float` in the lab is an argument. Saying argparse decides by `default=` alone misses that the dashes do the work.',
        ),
        P(
            "Give one reason the course uses typer, and one reason argparse is still worth recognising.",
            2,
            "typer: the type hints are the specification, so the parser, the conversion to `int` and the `--help` page come from one signature with less code. argparse ships with Python, needs no dependency, and is common in code you will inherit.",
            [
                "A typer reason from the session: one signature is the spec; conversion from type hints; `--help` generated; less code",
                "An argparse reason: standard library, no dependency; met in inherited code",
            ],
            '"typer is newer" or "argparse is old" are not reasons. "typer is faster" is not true in any way the course discussed. The slide\'s own words are the safest: argparse is "no dependency, more code" and "worth recognising in code you inherit".',
        ),
        P(
            "Both runs end with exit code 2. What does that tell a script or CI that runs the command?",
            1,
            "Any non-zero code means failure, so an `&&` chain stops and a CI step turns red. Here the library refused the command line before the program's own code ran.",
            [
                "Non-zero is read as failure by `&&`, scripts and CI",
                "Notes that the library rejected the input before the program's logic ran",
            ],
            'Answers that say "2 means two errors" or "2 is a warning" misread exit codes: only 0 is success. Mentioning that a human sees the message is not the point; tools read the number.',
        ),
    ],
    """
A compare question in the teacher's style: two artefacts that do the same job, then a judgement. Both outputs are real runs. The links to make are slide 8's table (argument for what the command acts on, option for how it behaves), slide 10's verdict on argparse ("no dependency, more code", "worth recognising"), and slide 9's exit codes (non-zero is failure, whoever produced it).
""",
    5,
    "S5 slides 7–10",
    "5–8",
)

# ---------------------------------------------------------------- s6 questions
mcq(
    22,
    "core",
    ["concept"],
    """
A command finishes and you type `echo $?`. Which reading of the number is right?
""",
    [
        (
            False,
            "`1` means the command succeeded and `0` means it did nothing",
            "Inverted. Slide 9: 0 means success.",
        ),
        (
            True,
            "`0` means success, and any other number means failure",
            "Slide 9, word for word. Every downstream tool reads it this way.",
        ),
        (
            False,
            "The number counts the error lines the command printed",
            "It is a status the program chooses, such as `typer.Exit(code=1)`; nothing is counted.",
        ),
        (
            False,
            "Only negative numbers mean failure; positive ones are warnings",
            "There are no warning codes. Anything other than 0 is failure.",
        ),
    ],
    """
"0 means success; anything else means failure." `echo $?` prints the exit code of the last command. In typer you set it with `raise typer.Exit(code=1)`. The number matters because "every tool downstream reads that number: the shell, `&&`, CI". A human may read the message; machines read only the code.
""",
    6,
    "S5 slide 9",
    verified="source",
)

mcq(
    23,
    "exam",
    ["read-code", "read-tool-output", "judgement"],
    """
A teammate wrote:

```python
@app.command()
def add(merchant: str, amount: float) -> None:
    if amount <= 0:
        print("amount must be positive")
        return
    typer.echo(f"Added {merchant}: {amount:.2f}")
```

```console
$ uv run expenses add "Bar Ramon" 0
amount must be positive
$ echo $?
0
$ uv run expenses add "Bar Ramon" 0 && echo "expense saved"
amount must be positive
expense saved
```

What is wrong?
""",
    [
        (
            False,
            "The `&&` is the mistake; with `;` the second command would have been skipped",
            "`;` runs the next command whatever happens. `&&` is the right operator, and it did its job: it trusted the 0.",
        ),
        (
            False,
            "`print` must become `typer.echo`, because only typer's output sets the exit code",
            "How you print does not set the exit code. `typer.echo` followed by `return` still exits 0.",
        ),
        (
            False,
            "The check should be `amount < 0`, so that a zero amount is accepted as valid",
            "That changes the rule and leaves the problem: whatever the rule, a rejected input must end with a non-zero exit.",
        ),
        (
            True,
            "It exits 0 after an error, so tools read success; raise `typer.Exit(code=1)`",
            "A program that prints an error and exits 0 is a program that lies. `&&` ran the next command because of that 0.",
        ),
    ],
    """
The human reads "amount must be positive"; every tool reads 0 and concludes the expense was saved. `&&` ran `echo "expense saved"`, a CI step would stay green, and a script would carry on. The lab's shape ends the error path with `typer.echo(..., err=True)` and `raise typer.Exit(code=1)`, and its second test asserts `result.exit_code == 1`, which would catch this version immediately. Real runs: this code gives `echo $?` 0; the lab's code gives 1.
""",
    6,
    "S5 slide 9; labs/01-scaffold.md §5–6",
    origin="lab",
)

mcq(
    24,
    "exam",
    ["predict-output"],
    """
The lab's `add` exits with code 1 when the amount is not positive. What appears in the terminal?

```console
$ uv run expenses add "Bar Ramon" 0 && uv run expenses add Zara 39.90
```
""",
    [
        (
            True,
            "`amount must be positive` only; the second `add` never runs",
            "The first command exits 1, and `&&` runs the right side only after a 0.",
        ),
        (
            False,
            "`amount must be positive`, then `Added Zara: 39.90`",
            "This is what the lying version prints: it exits 0, so `&&` carries on. Real run, wrong program.",
        ),
        (
            False,
            "`Added Zara: 39.90` only, because a chain hides error messages",
            "Nothing hides the message: it is printed to stderr, which the terminal shows.",
        ),
        (
            False,
            "Nothing, because `&&` checks that both commands will succeed first",
            "`&&` runs left to right. The left command runs and prints; only then is its code checked.",
        ),
    ],
    """
`&&` reads the exit code of its left side: 0 runs the right side, anything else stops. Real runs: with the lab's `add`, only `amount must be positive` appears and the chain's status is 1. With the version that prints and returns, the same line prints `amount must be positive` and then `Added Zara: 39.90`. This is why the partial-submission check is written as `uv run ruff check . && ... && uv run pytest`: each step only runs if the one before told the truth about success.
""",
    6,
    "S5 slide 9; labs/01-scaffold.md §5",
    origin="lab",
)

mcq(
    25,
    "hard",
    ["read-code", "judgement"],
    """
```python
@app.command()
def add(merchant: str, amount: float) -> None:
    if amount <= 0:
        typer.echo("amount must be positive", err=True)
        raise typer.Exit()
    typer.echo(f"Added {merchant}: {amount:.2f}")
```

```console
$ uv run expenses add "Bar Ramon" 0
amount must be positive
$ echo $?
0
```

Which change makes the command tell the truth?
""",
    [
        (
            False,
            "Remove `err=True`, so the message goes to standard output",
            "Which channel the message uses does not change the exit code; it would still be 0.",
        ),
        (
            False,
            "Replace `raise typer.Exit()` with `return`, so the function ends cleanly",
            "`return` ends the command normally, which is exit code 0: the same lie.",
        ),
        (
            True,
            "Give the exit a non-zero code: `raise typer.Exit(code=1)`",
            "A bare `typer.Exit()` uses code 0. Slide 9 spells out `code=1`.",
        ),
        (
            False,
            "Move the amount check into the `@app.callback()`, which runs first",
            "The callback runs before every command and does not receive `amount`. Where the check lives does not set the code.",
        ),
    ],
    """
The message is right and it goes to stderr, as session 7 asks, but the program still says "success". `typer.Exit()` with no argument is a normal exit, code 0: real run, `echo $?` printed 0 and `&& echo "expense saved"` ran. Slide 9 and the lab both write `raise typer.Exit(code=1)`. Careful reading is the skill here: the code looks like the lab's shape and differs by one argument.
""",
    6,
    "S5 slide 9; labs/01-scaffold.md §5",
    origin="lab",
)

mcq(
    26,
    "hard",
    ["read-tool-output", "judgement"],
    """
These are your group's two tests from lab 01 §6. After a teammate edits `add`, pytest prints:

```text
    def test_add_rejects_a_non_positive_amount() -> None:
        result = runner.invoke(app, ["add", "Bar Ramon", "0"])
>       assert result.exit_code == 1
E       assert 0 == 1
E        +  where 0 = <Result okay>.exit_code

tests/test_cli.py:16: AssertionError
=========================== short test summary info ============================
FAILED tests/test_cli.py::test_add_rejects_a_non_positive_amount - assert 0 == 1
========================= 1 failed, 1 passed in 0.04s ==========================
```

When they run `uv run expenses add "Bar Ramon" 0` by hand, the terminal shows `amount must be positive`. What can you conclude?
""",
    [
        (
            False,
            "The test is wrong: the message appears, so the command handles the case",
            "The message is for people. The test checks the number that `&&`, CI and scripts read, and the lab asks for a non-zero exit.",
        ),
        (
            False,
            "The test is flaky because `CliRunner` is unreliable; rerun it until it passes",
            "Nothing here is random: the command exits 0 every time with this input.",
        ),
        (
            False,
            "Change the test to expect `0`, since that is what the command returns now",
            "That makes the test agree with the lie. The lab's requirement is a non-zero exit when the input makes no sense.",
        ),
        (
            True,
            "The command prints its error but exits 0; fix the command, not the test",
            "`<Result okay>` with code 0 means a normal exit. The specification (non-zero on bad input) is clear, so the code is wrong.",
        ),
    ],
    """
The assertion compares the real exit code (0) with the expected one (1), and `<Result okay>` confirms the command ended normally. Unlike the sample paper's discount question, you can tell which side is right here: lab 01 says the command must have "a non-zero exit when the input makes no sense", and slide 9 calls the alternative a program that lies. Session 8 named this test's job: "Session 5's exit code, now checked by a machine." Real run: replacing `raise typer.Exit(code=1)` with `print` and `return` produced exactly this failure.
""",
    6,
    "S5 slide 9; labs/01-scaffold.md §6; S8 slide 21",
    origin="lab",
)

open_q(
    28,
    "exam",
    ["read-code", "read-tool-output", "judgement"],
    f"""
A teammate pushes this command for the expense-tracker:

```python
@app.command()
def add(merchant: str = "", category: str = "", amount: float = 0.0) -> None:
    if amount <= 0:
        print("Error: amount must be positive")
        return
    print(f"added {{merchant}} ({{category}}) {{amount:.2f}}")
```

```console
$ uv run expenses add "Bar Ramon" dining 12.50
{usage_err("expenses add [OPTIONS]", "expenses add", "Got unexpected extra argument(s) (Bar Ramon dining 12.50)")}
$ uv run expenses add --merchant "Bar Ramon" --category dining --amount 0
Error: amount must be positive
$ echo $?
0
$ uv run expenses add --amount 12.50
added  () 12.50
$ echo $?
0
```
""",
    [
        P(
            "What is wrong with the interface, that is, how values are given? Name two problems a user would hit.",
            2,
            'All three parameters have defaults, so typer made them options. The natural call `add "Bar Ramon" dining 12.50` is refused as extra arguments, and a missing value silently becomes its default: `add --amount 12.50` is accepted with no merchant or category.',
            [
                "Says the defaults turned `merchant`, `category` and `amount` into options",
                "Explains the positional call is rejected (`Got unexpected extra argument(s)`)",
                "Explains missing values silently fall back to empty defaults (`added  () 12.50`)",
            ],
            '"The command is hard to use" or "too many options" names a feeling, not a cause. The cause is the defaults, and full marks need one consequence each: the refused positional call and the silently accepted empty merchant. Answers blaming the types (`float`) have the rule backwards.',
        ),
        P(
            "What is wrong with the exit behaviour, and who is misled by it?",
            2,
            "On bad input it prints an error and returns, so the exit code is 0: a program that lies. `&&`, CI and a test on `exit_code` all read success. The message also goes to standard output instead of stderr.",
            [
                "Says it prints an error but exits 0 (`echo $?` shows 0)",
                "Names a downstream reader that is misled: `&&`, CI, a script or a test on `exit_code`",
                "Notes the error goes to standard output via `print` rather than to stderr",
            ],
            'Saying only "it should use `typer.echo`" misses the point: the function that prints does not set the exit code. Saying "the user sees the error, so it is fine" is exactly the misconception slide 9 targets. One mark for noticing exit 0, the second for naming who is misled.',
        ),
        P(
            "Describe in words how you would fix both problems, and which problem each change solves.",
            2,
            "Remove the defaults so the three values become required arguments; that fixes the refused call and the empty values. End the error path with the message on stderr and `typer.Exit` with code 1, so every tool sees the failure.",
            [
                "Remove the defaults (or use `typer.Argument`) so what the command acts on becomes arguments, linked to the interface problem",
                "End the error path with a non-zero exit (`typer.Exit(code=1)`), message to stderr, linked to the exit problem",
            ],
            'Fixes without the link to a problem lose a mark each. "Add validation" is not a fix: the validation exists, it just exits 0. "Make merchant required with a check inside the function" keeps the wrong interface and adds code typer would give you for free.',
        ),
    ],
    """
This is the teacher's "read code and say what is wrong" shape applied to session 5: the interface (slide 8, a default makes an option) and the exit behaviour (slide 9, a program that lies). The transcript is a real run of this code. A strong answer names a cause, shows the consequence from the transcript, and links each fix to its problem, in prose.
""",
    6,
    "S5 slides 8–9; labs/01-scaffold.md §5",
    "6–8",
    origin="lab",
)

open_q(
    29,
    "exam",
    ["concept", "judgement"],
    """
During the lab a teammate says: "Exit codes do not matter. If the input is bad, the user can read the message on the screen." Your group's CI runs `uv sync --locked`, then ruff, mypy and pytest on every push, and the partial-submission rubric asks that bad input give "a clear message and a non-zero exit code, not a traceback".
""",
    [
        P(
            "Name two things, other than a person reading the screen, that read a command's exit code, and what each does with it.",
            2,
            "The shell: `&&` runs the next command only when the previous one exited 0, and `$?` holds the number for scripts. CI: a step that exits non-zero fails and turns the run red. Tests: `CliRunner` gives `result.exit_code`, so a test can assert it.",
            [
                "The shell: `&&` runs the next command only after 0, or `$?` in a script",
                "CI: a step that exits non-zero turns the check red",
                "Tests: `CliRunner` exposes `exit_code` for an assertion",
            ],
            '"The computer" or "the system" is too vague to score. Each mark needs a named reader and what it does with the number. Listing ruff and mypy as readers of your command\'s exit code confuses the tools CI runs with the readers of their results.',
        ),
        P(
            'Explain the slide\'s sentence "A program that prints an error and exits 0 is a program that lies" with one concrete consequence.',
            2,
            'Exit 0 tells the tools the work succeeded. If `add` prints "amount must be positive" but exits 0, a chain such as `expenses add ... && expenses report` carries on as if the expense was saved, and CI reports success when nothing was stored.',
            [
                "States that 0 is read as success by tools that never see the text",
                "Gives a concrete consequence: the next command in an `&&` chain runs, CI stays green, or a script carries on",
            ],
            'Restating the sentence earns nothing on its own. Weak answers stay abstract ("it gives wrong information"); full marks need the mechanism (tools read the number, not the text) and one situation where that causes harm.',
        ),
        P(
            "How would you make sure, by machine, that your command keeps exiting non-zero on bad input?",
            1,
            "A `CliRunner` test that invokes the command with an invalid value, such as an amount of 0, and asserts that the exit code is 1; pytest runs it in CI on every push.",
            [
                "Describes a test that runs the command with bad input and asserts the non-zero exit code",
            ],
            '"Test it manually before each push" is not by machine. "Check that the message is printed" tests the part the teammate already trusts; the assertion has to be on the exit code.',
        ),
    ],
    """
A judgement question built from slide 9 ("every tool downstream reads that number"), lab 01 §6 (the failure test asserts `exit_code == 1`), session 8's `CliRunner` slide and the partial-submission rubric. Full marks need named readers of the number and a concrete failure, not a general statement that exit codes are good practice.
""",
    6,
    "S5 slide 9; labs/01-scaffold.md §6; S8 slide 21; partial-rubric",
    "5–7",
    verified="source",
)

# ---------------------------------------------------------------- s7 questions
mcq(
    30,
    "core",
    ["concept"],
    """
Your group's topic is the parking lot. Which pair of spellings does the lab ask for?
""",
    [
        (
            True,
            "`parking-lot` for the project and the command; `parking_lot` for the `src/` folder and imports",
            "Distribution name with hyphens, package name with underscores, as in the lab's table.",
        ),
        (
            False,
            "`parking_lot` for the project and the command; `parking-lot` for the `src/` folder and imports",
            "Reversed. A folder called `parking-lot` cannot be imported: `import parking-lot` is a `SyntaxError`.",
        ),
        (
            False,
            "`parking-lot` everywhere, because uv converts the name for Python automatically",
            "uv does not rewrite your imports or your folder. The package must be a valid Python identifier.",
        ),
        (
            False,
            "Either spelling anywhere, as long as the whole team uses the same one",
            "Consistency is not enough: hyphens are invalid in a package name, whatever the team agrees.",
        ),
    ],
    """
"Python identifiers cannot contain hyphens, which is why there are two." Real run: `uv run python -c "import parking-lot"` stops with `SyntaxError: invalid syntax`, while `import parking_lot` prints `import OK`. So the project `name` and the command use hyphens, and the folder under `src/`, the wheel `packages` line and every `import` use underscores. The `[project.scripts]` line uses both: `parking-lot = "parking_lot.cli:app"`.
""",
    7,
    "S5 slide 12; labs/01-scaffold.md §2",
    origin="lab",
)

sort_q(
    31,
    "exam",
    ["read-code", "concept"],
    """
You rename the template from `app` to `parking-lot` / `parking_lot`. For each occurrence of `app`, decide what it becomes.
""",
    [
        ("hyphen", "Becomes `parking-lot` (hyphens)"),
        ("underscore", "Becomes `parking_lot` (underscores)"),
        ("keep", "Stays `app`"),
    ],
    [
        (
            "The folder `src/app/`",
            "underscore",
            "The folder is the package, so it must be importable: `git mv src/app src/parking_lot`.",
        ),
        (
            '`name = "app"` under `[project]`',
            "hyphen",
            "The distribution name, the project's identity, uses hyphens.",
        ),
        (
            "The command on the left of `[project.scripts]`: `app = ...`",
            "hyphen",
            "The command you type uses the hyphenated name: `uv run parking-lot`.",
        ),
        (
            'The module part on the right of `[project.scripts]`: `"app.cli:..."`',
            "underscore",
            "It is an import path, so it uses the package name: `parking_lot.cli`.",
        ),
        (
            'The object after the colon in `"app.cli:app"`',
            "keep",
            "That is the typer object in `cli.py`, which the rename does not touch.",
        ),
        (
            '`packages = ["src/app"]` under `[tool.hatch.build.targets.wheel]`',
            "underscore",
            "It names the package folder to build, so it follows the folder: `src/parking_lot`.",
        ),
        (
            "`from app.cli import app` in `__main__.py` (the module part)",
            "underscore",
            "An import of the package: `from parking_lot.cli import app`. The one everyone forgets.",
        ),
        (
            "`from app.cli import app` in `tests/test_cli.py` (the module part)",
            "underscore",
            "The tests import the package too: `from parking_lot.cli import app`.",
        ),
        (
            '`app = typer.Typer(help="...")` in `cli.py`',
            "keep",
            "The lab: the only `app` left should be the typer object itself.",
        ),
    ],
    """
The six places are the folder, three lines of `pyproject.toml` (`name`, `[project.scripts]`, wheel `packages`), `__main__.py` and `tests/test_cli.py`. Anything Python imports takes underscores; the project's name and the command take hyphens; the typer object keeps its name. In a real rename of the template, `grep -rnI "app" pyproject.toml src tests` afterwards showed only the object and its imports, plus any line you missed.
""",
    7,
    "labs/01-scaffold.md §2–3; S5 slide 12",
    origin="lab",
)

# ---------------------------------------------------------------- s8 questions
mcq(
    32,
    "core",
    ["concept"],
    """
Checkpoint 1 is three binary items, marked at your `v0.1` tag. Which situation costs your group one of them?
""",
    [
        (
            False,
            "The project has only one command so far, and no second command is planned yet",
            "The lab asks for exactly one real command at this stage. CP1 does not count commands.",
        ),
        (
            False,
            "`strict = true` for mypy is not yet set in `pyproject.toml`",
            "Strict typing is session 7's step. It is not a CP1 item.",
        ),
        (
            True,
            "The README still shows the rename banner and no way to run the program",
            "Item 3: the README says what it does, how to install and how to run.",
        ),
        (
            False,
            "There are fewer than eight tests in the repository at the `v0.1` tag",
            "Eight tests are Checkpoint 2's first item (session 8) and part of the partial submission's Tests criterion. CP1 has no item about tests; the lab only asks for two that pass today.",
        ),
    ],
    """
CP1's items: 1. `uv sync && uv run <your-app> --help` works from a clean clone; 2. `src/` layout, package importable; 3. README: what it does, how to install, how to run. They are public, binary and checkable before you submit; session 4 put it as "a Definition of Done you cannot check yourself is a wish". A README left as the template fails item 3 however good the code is.
""",
    8,
    "S5 slide 14; S4 slide 17; labs/01-scaffold.md §7 and §10",
    verified="source",
)

mcq(
    33,
    "hard",
    ["read-tool-output", "judgement"],
    """
Before tagging `v0.1`, you run the lab's clean-clone check on `main`:

```console
$ uv sync
...
$ uv run parking-lot --help
Traceback (most recent call last):
  File ".venv/bin/parking-lot", line 4, in <module>
    from parking_lot.cli import app
ModuleNotFoundError: No module named 'parking_lot'
```

On your own laptop the same command works, and there:

```console
$ git status --short
?? src/
```

What is going on?
""",
    [
        (
            False,
            "The clean clone has no `.venv`, so it needs `uv lock` before `uv sync`",
            "`uv sync` built the environment without complaint. The lockfile is not the problem; the package is.",
        ),
        (
            False,
            "`[project.scripts]` is wrong; its left side has to match the folder name",
            "The wrapper exists and runs (the traceback starts in it), so the command was installed. The import inside it fails.",
        ),
        (
            False,
            "The clean clone runs a different Python version from the one on the laptop",
            "Nothing in the message is about versions. It is your own package that cannot be found.",
        ),
        (
            True,
            "The package folder was never committed, so the clone has no `src/` at all",
            "`??` means untracked. The folder exists only on your laptop, which is exactly what a clean clone catches; commit it, push and check again.",
        ),
    ],
    """
"A clean clone has no `.venv`, no caches and nothing you forgot to commit. That is the whole point of the check." Here the folder was moved with plain `mv` instead of `git mv` and committed with `git commit -am`, which records the deletion of `src/app` but never adds the new folder, so `git status` shows the whole `src/` as untracked. The clone has no package: CP1 items 1 and 2 would both fail at the tag. The lab's `git add -A` before committing avoids this. Real run: same steps, same traceback, and `ls src` in the clone found nothing.
""",
    8,
    "labs/01-scaffold.md §9–10; S5 slide 14",
    origin="lab",
)

open_q(
    34,
    "hard",
    ["judgement", "concept"],
    """
Friday 25 September, 13:00, near the end of the lab. A teammate has `uv run parking-lot --help` working on their laptop and wants to tag straight away. The lab's self-check for Checkpoint 1 is:

```bash
cd /tmp && rm -rf cp1 && git clone git@github.com:esade-swdev-2026/<your-repo>.git cp1
cd cp1 && git checkout v0.1
uv sync
uv run <your-app> --help
uv run python -c "import <your_package>; print('import OK')"
```
""",
    [
        P(
            "What does this check prove that running the command on the teammate's laptop does not?",
            2,
            "It proves the tag works from what is committed: a clean clone has no `.venv`, no caches and no uncommitted files, and the commands check CP1 items 1 and 2 the way the marker will.",
            [
                "A clean clone contains only committed files: no `.venv`, no caches, nothing left only on the laptop",
                "It reproduces how CP1 items 1 and 2 are marked: install and `--help`, package importable",
            ],
            '"It checks that it works" says nothing about why the laptop is not enough. The key word is committed: the laptop has files and an environment that the repository does not. Mentioning "works on my machine" without saying what differs earns one mark.',
        ),
        P(
            "Name two session 5 mistakes that pass on the laptop but fail from a clean clone or in CI.",
            2,
            "The renamed package folder left uncommitted: the laptop has it, the clone fails with `No module named 'parking_lot'`. Or a `uv.lock` refreshed on the laptop but never committed, which CI's `uv sync --locked` refuses.",
            [
                "An uncommitted file or folder, such as the renamed package",
                "A stale `uv.lock` that was not committed, refused by `uv sync --locked`",
                "`__main__.py` still importing `app.cli`, red at mypy in CI",
            ],
            "A typo in the code is not an example: it fails on the laptop too. Each mark needs a mistake that the laptop hides, and what the clone or CI shows instead.",
        ),
        P(
            "Why does the lab ask for the four checks locally before the push, and what does the tag mean for marking?",
            2,
            "The four commands are what `check.yml` runs, so passing them locally predicts a green CI run. The tag names the one commit CP1 is marked at: no tag means nothing to mark.",
            [
                "The four local checks are the same as CI's, so they predict a green run",
                "The tag names the one commit CP1 is marked against; no tag means nothing to mark",
            ],
            '"To be safe" is not a reason. Weak answers treat the tag as a label for the whole repository; it points at one commit, and that commit is what the marker clones.',
        ),
    ],
    """
This question combines CP1 (slide 14), the lab's clean-clone check (§10), the four checks (§8) and the tag (§9). Every mistake in the model answer and the rubric was reproduced in a real run: the uncommitted package folder (`No module named 'parking_lot'` in the clone), the uncommitted lockfile (`uv sync --locked` refused it), and the forgotten `__main__.py` (red at mypy).
""",
    8,
    "S5 slide 14; labs/01-scaffold.md §8–10",
    "6–8",
    origin="lab",
)

# ---------------------------------------------------------------- s9 questions
mcq(
    35,
    "exam",
    ["read-tool-output", "judgement"],
    f"""
Your first push after renaming goes red. The log of the step "Install dependencies from the lockfile" shows:

```text
Using CPython 3.13.15
Creating virtual environment at: .venv
Resolved 30 packages in 210ms
{LOCK_ERR}
```

What should you do?
""",
    [
        (
            False,
            "Remove `--locked` from the workflow so that CI resolves the versions itself",
            "That silences the referee. `--locked` is how CI guarantees it installs exactly what you committed.",
        ),
        (
            True,
            "Run `uv lock` locally, check that `uv.lock` changed, commit it and push",
            "The committed lockfile still describes the old project. The lab's troubleshooting row says exactly this.",
        ),
        (
            False,
            "Delete `.venv` on your laptop and run `uv sync` again",
            "CI never sees your `.venv`. The problem is a file in the repository, not your environment.",
        ),
        (
            False,
            "Delete `uv.lock` from the repository, since CI can regenerate it",
            "With `--locked`, a missing lockfile also fails (`Unable to find lockfile`), and you lose the pinned versions.",
        ),
    ],
    """
The first of the three that bite. `uv.lock` records the project under its old name, `app`, and CI runs `uv sync --locked`, which "refuses a lockfile that disagrees with `pyproject.toml`". The lab calls skipping `uv lock` "the single most likely reason your first push goes red". The fix is local and committed: `uv lock` (the real run prints `Removed app v0.1.0` and `Added parking-lot v0.1.0`), then commit `uv.lock` and push.
""",
    9,
    "S5 slide 13; S4 slide 24; labs/01-scaffold.md §4 and troubleshooting",
    origin="lab",
)

mcq(
    36,
    "exam",
    ["read-tool-output", "judgement"],
    f"""
Your first push after renaming the template to `parking-lot` / `parking_lot` goes red. Lint and Formatting are green; the run stops at the Types step:

{fence("text", MYPY_MAIN)}

On your laptop, `uv run pytest` passes. Which fix is most appropriate?
""",
    [
        (
            True,
            "Change line 1 of `__main__.py` to import `app` from `parking_lot.cli`",
            "The import still names the package you renamed. One changed line fixes mypy and the `python -m parking_lot` door at once.",
        ),
        (
            False,
            "Add `# type: ignore` to line 1 of `__main__.py` so the Types step passes",
            "It hides a real crash: on the same code, `uv run python -m parking_lot` fails with `ModuleNotFoundError: No module named 'app'`.",
        ),
        (
            False,
            "Rerun the workflow: pytest passes locally, so the Types step must be wrong",
            "mypy reports the same missing module on every run. pytest passes only because the tests never load `__main__.py`.",
        ),
        (
            False,
            "Stop mypy from checking `__main__.py`, since no test ever imports that file",
            "That moves the referee instead of fixing the code: the broken import stays and the `-m` door still crashes.",
        ),
    ],
    """
The second of the three that bite: `__main__.py` still imports `app.cli`, so pytest passes, mypy fails and CI is red. The tests import `parking_lot.cli`, so pytest never loads `__main__.py`; mypy checks every file under `src` and has to resolve each import. The error is a real crash: `uv run python -m parking_lot` stops with `ModuleNotFoundError: No module named 'app'`. Read the error and fix the cause, as session 7 asks. Ignoring the line, hiding the file from mypy or rerunning CI leaves the program broken.
""",
    9,
    "S5 slide 13; labs/01-scaffold.md troubleshooting; S7 slide 9",
    origin="lab",
)

mcq(
    37,
    "exam",
    ["read-tool-output", "read-code"],
    f"""
Your group replaced `greet` and `bye` with one command and did not add the empty `@app.callback()` from the lab:

```python
app = typer.Typer(help="A parking lot: tickets and prices.")


@app.command()
def park(plate: str, hours: int = 1) -> None:
    ...
```

```console
{NO_CALLBACK_RUN}
```

What is the cause, and the fix?
""",
    [
        (
            False,
            "`plate` needs a default, so that typer can tell it apart from the command's name",
            "A default would make `plate` the option `--plate`. It would not give `park` its name back.",
        ),
        (
            False,
            "The lockfile still lists `greet` and `bye`; run `uv lock` and `uv sync`",
            "The lockfile records packages and versions, not commands. Nothing about it changed.",
        ),
        (
            True,
            "One command, no callback: typer took `park` as the plate; add the empty callback",
            "The usage line has no `COMMAND`. The empty callback tells typer more commands will come.",
        ),
        (
            False,
            "`hours` needs `typer.Option(...)`, because a plain default cannot make an option",
            "A plain default already makes `--hours` an option, and the help lists it. What is missing is the command's name.",
        ),
    ],
    f"""
The usage line is the clue: `parking-lot [OPTIONS] {{plate}}`, with no `COMMAND`. typer has dropped the command's name, so the word `park` filled `plate` and `1234ABC` had no slot. The help shows the same thing:

{fence("text", HELP_PARK_NO_CALLBACK)}

With the lab's four-line empty callback added, the real usage becomes `Usage: parking-lot park [OPTIONS] {{plate}}` and `uv run parking-lot park 1234ABC` prints `Ticket for 1234ABC: 1 h`.
""",
    9,
    "S5 slide 13; labs/01-scaffold.md §5 and troubleshooting",
    origin="lab",
)

mcq(
    38,
    "hard",
    ["read-tool-output"],
    f"""
Another group made the same mistake with the lab's `add(merchant: str, amount: float)` and no callback:

```console
$ uv run expenses add "Bar Ramon" 12.50
{usage_err("expenses [OPTIONS] {merchant} {amount}", "expenses", "Invalid value for 'amount': 'Bar Ramon' is not a valid float.")}
```

The lab's troubleshooting table says this mistake shows `Got unexpected extra argument(s)`. Why is the message different here, and what is the fix?
""",
    [
        (
            False,
            "The amount must come before the merchant; swap the two parameters in `add`",
            "Swapping changes nothing: the word `add` would still fill the first parameter.",
        ),
        (
            False,
            "The shell joined `Bar Ramon` and `12.50`; quote the amount separately as well",
            "The shell passed three words: `add`, `Bar Ramon` and `12.50`. The quotes are fine.",
        ),
        (
            False,
            "`float` cannot hold money; make `amount` a `str` and convert it inside `add`",
            "That throws away typer's type check, and the name `add` would still be swallowed.",
        ),
        (
            True,
            "`add` filled `merchant` and `Bar Ramon` failed as `amount`; add the callback",
            "typer converts values before it looks for left-over ones. Same cause as the table's row, different message.",
        ),
    ],
    """
Read the usage line, not just the box: `expenses [OPTIONS] {merchant} {amount}` has no `COMMAND`, so the command's name has been dropped. typer filled `merchant` with the word `add` and `amount` with `Bar Ramon`, and the `float` conversion failed before typer noticed that `12.50` was left over. Real run: without the callback, `uv run expenses "Bar Ramon" 12.50` works, which proves `add` is no longer a word you type. The lab's empty `@app.callback()` brings the name back.
""",
    9,
    "S5 slide 13; labs/01-scaffold.md §5 and troubleshooting",
    origin="lab",
)

mcq(
    39,
    "beyond",
    ["read-tool-output", "judgement"],
    """
A teammate adds colour to the `report` command. On their laptop `uv run pytest` prints `24 passed`. Their commit changed only `src/expense_tracker/cli.py`, which now starts with `from colorama import Fore`. They had run `uv pip install colorama` and committed no other file. CI's `uv sync --locked` step passes, then the tests step fails:

```text
tests/test_io.py:5: in <module>
    from expense_tracker.cli import app
src/expense_tracker/cli.py:6: in <module>
    from colorama import Fore
E   ModuleNotFoundError: No module named 'colorama'
=========================== short test summary info ============================
ERROR tests/test_io.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
```

What is the problem, and what is the fix?
""",
    [
        (
            False,
            "CI built its environment from a stale cache, so rerun the job until `colorama` appears",
            "A rerun repeats the same fresh checkout and the same missing dependency. Rerunning until green is the careless move the course warns about.",
        ),
        (
            False,
            "Delete `.venv` on the runner and run `uv sync` again, so uv installs it from scratch",
            "CI already starts from a fresh checkout. A new environment built from the same `pyproject.toml` and `uv.lock` still has no `colorama`.",
        ),
        (
            False,
            "Add `# type: ignore` to line 6, because the failure comes from the type checker",
            "The failure is a runtime `ModuleNotFoundError` during test collection, not a mypy message. An ignore comment changes nothing about what is installed.",
        ),
        (
            True,
            "It lives only in their `.venv`; declare it with `uv add colorama` and commit both files",
            "`pyproject.toml` is the single source of truth. `uv pip install` touched only the laptop's environment, so the project file and `uv.lock` never listed it.",
        ),
    ],
    """
"Works on my machine" (session 3), seen from CI's side. `uv pip install` changes the local `.venv` and nothing else, so `pyproject.toml` and `uv.lock` still describe a project without `colorama`. CI builds a fresh environment from those two files. Its `uv sync --locked` passes because the lockfile matches the project file; both are equally ignorant of the package. The first import then fails, and pytest stops at collection. `uv add colorama` edits `pyproject.toml` and `uv.lock` together; commit both. Real run: the fresh copy failed with exactly this `ModuleNotFoundError` after a passing `uv sync --locked`.
""",
    9,
    "S3 slide 3; S4 slide 20; labs/01-scaffold.md",
    origin="lab",
)

sort_q(
    40,
    "hard",
    ["read-tool-output", "judgement"],
    """
Your group's CI runs these steps in order and stops at the first one that fails: install from the lockfile (`uv sync --locked`), Lint (`ruff check .`), Formatting (`ruff format --check .`), Types (`mypy src tests`), Tests (`pytest`). For each situation, which step is the first to go red? Assume everything else in the repository is correct.
""",
    [
        ("lock", "Install from the lockfile"),
        ("format", "Formatting"),
        ("types", "Types"),
        ("tests", "Tests"),
        ("none", "No step goes red"),
    ],
    [
        (
            "`pyproject.toml` renamed, but the `uv.lock` in the commit is from before the rename",
            "lock",
            "`uv sync --locked` refuses a lockfile that disagrees with `pyproject.toml`: `needs to be updated`.",
        ),
        (
            "`ruff format .` was run after committing, so the committed file still has spacing the formatter would change",
            "format",
            "The lab's troubleshooting row: red at Formatting, green locally. `ruff format --check` reports `1 file would be reformatted`.",
        ),
        (
            "`__main__.py` still contains `from app.cli import app`",
            "types",
            'ruff and pytest pass; mypy reports `Cannot find implementation or library stub for module named "app.cli"`.',
        ),
        (
            'One command, no `@app.callback()`, and the tests invoke `["park", "1234ABC"]`',
            "tests",
            "The code is valid for ruff and mypy; typer drops the command's name, so the tests get exit code 2.",
        ),
        (
            "`add` prints its error and returns, and a test asserts `result.exit_code == 1`",
            "tests",
            "Nothing is wrong for the linters or mypy; the test sees `assert 0 == 1`.",
        ),
        (
            "The README still shows the template's rename banner and no example",
            "none",
            "No CI step reads the README. It costs CP1 item 3, which a person marks.",
        ),
        (
            "`LICENSE` still names the lecturer as the copyright holder",
            "none",
            "CI does not check the licence. It is still wrong: the work is yours.",
        ),
    ],
    """
CI is the referee, not the judge: it catches what its four tools and the lockfile step can see, in order, and nothing else. Each technical case was reproduced: the stale lockfile, the unformatted file, the forgotten `__main__.py` (ruff and pytest green, mypy red) and both test failures (exit code 2 without the callback, 0 for the lying `add`). The README and the licence pass every step, which is why CP1 and the rubric have human items too.
""",
    9,
    "S5 slide 13; labs/01-scaffold.md §8 and troubleshooting; project-template check.yml",
    origin="lab",
)

open_q(
    41,
    "hard",
    ["read-tool-output", "judgement"],
    f"""
After renaming the template to `parking-lot` / `parking_lot`, your teammate runs the four checks before pushing:

```console
{FOUR_CHECKS_MAIN_FORGOTTEN}
```
""",
    [
        P(
            "Which check fails, on which file and line, and what does the message mean?",
            1,
            "mypy fails on line 1 of `src/parking_lot/__main__.py`: it cannot find the module `app.cli`, because the package is now `parking_lot` and that import was never renamed.",
            [
                "mypy, `src/parking_lot/__main__.py` line 1: the imported module `app.cli` no longer exists after the rename",
            ],
            '"mypy found a type error" is not enough: this is a missing module, not a type disagreement. The mark needs the file and the reason (the old package name in the import).',
        ),
        P(
            "Why do ruff and pytest pass on the same code?",
            2,
            "ruff checks each file's style and simple mistakes without finding the modules it imports. pytest only runs what the tests reach, and the tests import `parking_lot.cli`, so `__main__.py` is never loaded. mypy reads every file under `src` and resolves each import.",
            [
                "ruff does not resolve imports",
                "pytest only loads what the tests import (`parking_lot.cli`), never `__main__.py`",
                "mypy checks every file under `src` and resolves each import",
            ],
            '"pytest does not check types" is true and not the reason: the problem is a missing module, which pytest would report if it ever imported the file. The point is which files each tool actually reads.',
        ),
        P(
            "The teammate proposes adding `# type: ignore` to that line to get CI green before the tag. Do you accept? Give your reasoning.",
            2,
            "No. The error is a real crash: `uv run python -m parking_lot` fails with `ModuleNotFoundError: No module named 'app'`. The ignore would hide a broken door and keep a wrong name in the code. The proper fix is one change: import from `parking_lot.cli`.",
            [
                "Rejects the ignore",
                "Explains it is a real failure for anyone using `python -m`, not a false alarm",
                "Gives the proper fix: update the import to the new package name",
            ],
            'Accepting "because CI must be green for the tag" treats the referee as the obstacle. A "no" without a reason scores one mark at most; full marks need the real consequence (the `-m` door crashes) and the one-word fix.',
        ),
    ],
    """
The sample paper's "read tool output" shape (sort, judge, decide on `# type: ignore`), applied to slide 13's second trap. The output is a real run on a renamed template with `__main__.py` left alone, and `uv run python -m parking_lot` on the same code really crashes with `ModuleNotFoundError: No module named 'app'`. Session 7's rule applies too: read the error and fix the cause; an ignore comment is not a fix.
""",
    9,
    "S5 slide 13; labs/01-scaffold.md troubleshooting; sample paper Q9 shape",
    "5–8",
    origin="lab",
)

open_q(
    42,
    "beyond",
    ["read-tool-output", "read-code", "judgement"],
    """
A group has one command and no callback. Its CLI and the lab's two tests:

```python
app = typer.Typer(help="A terminal expense tracker.")


@app.command()
def add(merchant: str, amount: float) -> None:
    if amount <= 0:
        typer.echo("amount must be positive", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Added {merchant}: {amount:.2f}")
```

```text
>       assert result.exit_code == 0
E       assert 2 == 0
E        +  where 2 = <Result SystemExit(2)>.exit_code

tests/test_cli.py:10: AssertionError
...
>       assert result.exit_code == 1
E       assert 2 == 1
E        +  where 2 = <Result SystemExit(2)>.exit_code

tests/test_cli.py:16: AssertionError
=========================== short test summary info ============================
FAILED tests/test_cli.py::test_add_reports_the_merchant - assert 2 == 0
FAILED tests/test_cli.py::test_add_rejects_a_non_positive_amount - assert 2 == 1
============================== 2 failed in 0.12s ===============================
```

The tests call `runner.invoke(app, ["add", "Bar Ramon", "12.50"])` and `runner.invoke(app, ["add", "Bar Ramon", "0"])`.
""",
    [
        P(
            "Why do both tests fail, and why with exit code 2 rather than 0 or 1?",
            2,
            "With one command and no callback, typer treats `add` as the whole program, so the word `add` is read as the merchant and the other values no longer fit. typer refuses the command line before `add` runs: exit 2 is typer's usage error, while 1 is what the command's own check returns.",
            [
                "Identifies a single command with no `@app.callback()`, so typer drops the command's name",
                "Explains that `add` is consumed as the first argument and typer rejects the input",
                "Explains that 2 comes from typer refusing the command line, distinct from the command's own exit 1",
            ],
            '"The amount check is wrong" misses that `add` never ran: both tests got the same 2, whatever the amount. Answers that see the missing callback but cannot say why the code is 2 earn one mark.',
        ),
        P(
            "Describe the fix in words.",
            1,
            "Add the lab's empty `@app.callback()` function above the command, so typer expects several commands and `add` keeps its name.",
            [
                "Add an empty `@app.callback()` so the command keeps its name",
            ],
            '"Rewrite the tests without `add`" makes the tests agree with the accident and breaks every README example. "Add a second command" works but adds a feature to fix a structural problem.',
        ),
        P(
            'Without the callback, `uv run expenses "Bar Ramon" 12.50` works. Why does the lab still tell you to keep it?',
            2,
            "The project will grow more commands (the demo has `report` and `add`), and the README, tests and users all call `<app> <command>`. Keeping the name from the start means a second command later changes nothing that already calls the first.",
            [
                "More commands will come, so each needs its own name",
                "Changing the interface later breaks README examples, users' habits and tests that call `<app> <command>`",
            ],
            '"Because the lab says so" scores nothing. A good answer treats the command line as an interface other people depend on: changing it later breaks them, as the failing tests here show.',
        ),
    ],
    """
A small step beyond slide 13: the lab says to keep the callback and adds "Delete it later if you ever want the one-command form." This question asks why that choice matters. The test output is a real run of the lab's two tests against this code. Exit code 2 is the clue that typer, not your function, rejected the input; session 8's `CliRunner` exposes it as `result.exit_code`.
""",
    9,
    "S5 slide 13; labs/01-scaffold.md §5–6",
    "5–8",
    origin="lab",
)

# ---------------------------------------------------------------- added after review
mcq(
    43,
    "core",
    ["read-tool-output", "predict-output"],
    """
Slide 7 prints the usage line of the lab's `add(merchant: str, amount: float)` in capitals:

```text
Usage: expenses add [OPTIONS] MERCHANT AMOUNT
```

Which call does typer accept?
""",
    [
        (
            False,
            '`uv run expenses add --merchant "Bar Ramon" --amount 12.50`',
            "Names after `[OPTIONS]` are arguments, typed by position; neither has a `--` form. Real run: `No such option: --merchant`, exit 2.",
        ),
        (
            False,
            '`uv run expenses add 12.50 "Bar Ramon"`',
            "Arguments are filled in order, so `12.50` becomes the merchant and `Bar Ramon` fails the `float` conversion: `Invalid value for 'amount'`, exit 2.",
        ),
        (
            True,
            '`uv run expenses add "Bar Ramon" 12.50`',
            "Two arguments in the order the usage line lists them; `[OPTIONS]` may be left out. Real run: `Added Bar Ramon: 12.50`, exit 0.",
        ),
        (
            False,
            '`uv run expenses add MERCHANT="Bar Ramon" AMOUNT=12.50`',
            "The capitals are placeholders that you replace, never keywords you type. typer takes `AMOUNT=12.50` as the amount and refuses it as not a valid float, exit 2.",
        ),
    ],
    """
The usage line is generated from the signature: the command name, `[OPTIONS]` for everything with a default, then each argument in order. Slide 7 writes argument names in capitals; the typer pinned in the course's `uv.lock` writes `{merchant} {amount}`. Both say the same thing: two required values, typed by position, merchant first. A placeholder is never typed literally, and an argument has no `--name`. All four calls were run against the lab's `add`; typer refuses the three wrong ones with exit code 2 before `add` runs.
""",
    4,
    "S5 slide 7; labs/01-scaffold.md §5",
)

mcq(
    44,
    "exam",
    ["judgement", "concept"],
    """
At 13:04 your group finishes the lab with these commands, and the Actions tab goes green:

```bash
git add -A
git commit -m "Scaffold the project"
git push
git tag -a v0.1 -m "Scaffolded project"
```

The next day the marker reports that the repository has no `v0.1`, so there is nothing to mark for Checkpoint 1. What went wrong?
""",
    [
        (
            False,
            "The tag was made after the push, so it names a commit GitHub never received",
            "The tag names the commit you had just pushed, so GitHub has that commit. What it lacks is the tag itself.",
        ),
        (
            True,
            "The tag stayed on the laptop: `git push` sent the commits but never the tag",
            "A plain `git push` sends commits only. The lab's next line, `git push origin v0.1`, is the one that was skipped.",
        ),
        (
            False,
            "GitHub only shows a tag after CI has passed on the commit it points at",
            "CI never creates, hides or publishes tags. The green run is about the commit; the tag simply never left the laptop.",
        ),
        (
            False,
            "`git add -A` did not stage the tag, so the commit was pushed without it",
            "Tags are not files and are never staged. A tag is a name for a commit, and it travels with its own push.",
        ),
    ],
    """
A tag is a permanent name for one commit, and it stays in the repository where you made it until you push it by name. That is why lab 01 §9 has a separate `git push origin v0.1` after the tag, and the partial-submission rubric writes `git tag -a v0.5 -m "Partial submission" && git push origin v0.5`. In a scratch repository, the remote listed no tags after `git push`, and `git push origin v0.1` then printed `* [new tag]         v0.1 -> v0.1`. CP1 is marked at the tag, so a missing tag means there is nothing to mark, however green the commit is.
""",
    8,
    "labs/01-scaffold.md §9; S5 slides 2 and 12; partial-rubric",
    origin="lab",
)

mcq(
    45,
    "core",
    ["read-code", "judgement"],
    """
Lab 01 §5 asks for one command of your own with at least one argument, one option with a default, a non-zero exit when the input makes no sense, and type hints on every parameter. Four groups show their first command's signature and what it does with bad input. Which one meets every requirement?
""",
    [
        (
            False,
            "`add(merchant: str, amount: float)`, which exits 1 when `amount` is not positive",
            "Two arguments and no option: neither parameter has a default. It is also the lab's own example, and the lab says a copy with the nouns swapped is not done.",
        ),
        (
            False,
            "`grade(student: str, digits: int = 1)`, which prints an error and returns",
            "Printing and returning exits 0, a program that lies. The lab asks for a non-zero exit when the input makes no sense.",
        ),
        (
            False,
            '`book(room: str = "A1", hours: int = 1)`, which exits 1 when `hours` is below 1',
            "Both parameters have defaults, so both are options and the command has no argument. The room it acts on should have no default.",
        ),
        (
            True,
            "`park(plate: str, hours: int = 1)`, which exits 1 when `hours` is below 1",
            "`plate` has no default, so it is the argument; `hours` has one, so it is the option `--hours`; bad input exits 1; both are typed.",
        ),
    ],
    """
Slide 12 sums the requirement up as "an argument, an option, a non-zero exit", and lab 01 §5 adds type hints on every parameter. Read each signature with slide 8's rule: no default makes an argument, a default makes an option. Only `park` has one of each, types on both, and a failure path that exits non-zero; a real run with `--hours 0` printed `hours must be at least 1` and `echo $?` gave 1. The lab's `add` is a shape to translate into your own project, and it has no option at all.
""",
    8,
    "labs/01-scaffold.md §5; S5 slides 8 and 12",
    origin="lab",
)

open_q(
    46,
    "exam",
    ["read-diff", "compare", "judgement"],
    """
Reading the history of your group's `cli.py`, you find this diff:

```diff
 @app.command()
 def add(merchant: str, amount: float) -> None:
     if amount <= 0:
-        print("amount must be positive")
-        return
+        typer.echo("amount must be positive", err=True)
+        raise typer.Exit(code=1)
     typer.echo(f"Added {merchant}: {amount:.2f}")
```

Two candidate commit messages:

- A: `Tidy up add`
- B: `Exit with code 1 when add gets a non-positive amount`
""",
    [
        P(
            "What does this change do, for the person at the terminal and for the tools that run the command?",
            2,
            "The person sees the same message, now on standard error. The exit code changes from 0 to 1, so `&&` stops, a CI step or script sees a failure, and a test on `exit_code` can tell bad input from success.",
            [
                "Says the message is unchanged for the user but now goes to stderr",
                "Says the exit code on a non-positive amount goes from 0 to 1",
                "Names a tool that now sees the failure: `&&`, CI, a script or a test on `exit_code`",
            ],
            "'It uses `typer.echo` instead of `print`' describes the text of the diff, but not what changes. The change that matters is the number: before, the command printed an error and exited 0, a program that lies. Answers that say the user now sees an error miss that the user saw it before too.",
        ),
        P(
            "Which message is better for someone reading the history six months later, and why?",
            2,
            "B. It says what the program now does differently and when: exit 1 on a non-positive amount. A gives a later reader nothing to search for, and calls a behaviour change a tidy-up, which reads like a refactoring.",
            [
                "Chooses B because it states the behaviour change and when it applies",
                "Notes that A hides a behaviour change behind 'tidy', which suggests a refactoring that changes nothing",
            ],
            "'B is longer' or 'B is more detailed' earns nothing on its own. Full marks need what a later reader gets from B (what changed, and when it applies) and what A gets wrong: fixing the exit code changes behaviour, so it is no tidy-up.",
        ),
        P(
            "Describe in words one test you would add for this change.",
            1,
            "A `CliRunner` test that invokes `add` with the merchant `Bar Ramon` and the amount `0` and asserts that the exit code is 1.",
            [
                "Runs the command with a non-positive amount through `CliRunner` and asserts the exit code is 1, beyond checking the message",
            ],
            "A test that only checks that the message appears in `result.output` passes on both versions, so it would never have caught the old behaviour. The assertion has to be on the exit code, the number every tool reads.",
        ),
    ],
    """
The teacher's compare shape (sample Q8) applied to slide 9. Both versions were run. Before the change, `add "Bar Ramon" 0` printed the error and `echo $?` gave 0, so `&& echo "expense saved"` still ran. After it, the exit code was 1 and the chain stopped. A good message names the behaviour that changed, and a good test pins down the number the tools read, as the lab's second test does.
""",
    6,
    "S5 slide 9; labs/01-scaffold.md §5–6; sample paper Q8 shape",
    "5–7",
    origin="lab",
)

mcq(
    47,
    "exam",
    ["read-tool-output", "predict-output"],
    """
You inherit an `argparse` script and cannot see its code, only its help page:

```console
$ python report.py --help
usage: report.py [-h] [--category CATEGORY] [--minimum MINIMUM] [--verbose]
                 path

positional arguments:
  path

options:
  -h, --help           show this help message and exit
  --category CATEGORY
  --minimum MINIMUM
  --verbose
```

A colleague runs `python report.py --minimum 20 --verbose`. What do you expect?
""",
    [
        (
            False,
            "It runs with a minimum of 20, because everything except `-h` has a default",
            "Square brackets mark the optional parts. `path` has none, so it is required, and no word in the command line fills it.",
        ),
        (
            False,
            "It takes `20` as the `path`, because positional arguments grab the first bare word",
            "`--minimum MINIMUM` shows that the option takes a value, so `20` belongs to it. Nothing is left for `path`.",
        ),
        (
            False,
            "It refuses `--verbose`, because every option on this page needs a value after it",
            "`--verbose` shows no value name, so it is a plain on/off switch. Only `--category` and `--minimum` take a value.",
        ),
        (
            True,
            "It stops with a usage error that says `path` is required, and exits with code 2",
            "`path` has no brackets and appears under positional arguments, so it is required. argparse refuses the command line before the program's own code runs.",
        ),
    ],
    """
Read a `usage:` line the way slide 10 contrasts it with typer. Anything in square brackets is optional, and a bare name (`path`) is a required positional argument, which in typer would be a parameter with no default. `--category CATEGORY` and `--minimum MINIMUM` are options that take a value; `--verbose` is a switch without one. The command line has `--minimum 20` and `--verbose` but no path, so argparse prints the usage and `report.py: error: the following arguments are required: path`, then exits with 2, the code a library uses when it refuses the command line. Real run, same output.
""",
    5,
    "S5 slides 8, 10",
    verified="run",
)

# ================================================================ TERMS, TRAPS, CARDS


def s(n: int) -> str:
    return f"{MID}-s{n}"


TERMS = [
    (
        "Usage line",
        "The first line of `--help` and of a usage error. The slide prints the argument names in capitals (`MERCHANT AMOUNT`); the typer pinned in the course's `uv.lock` prints them in braces (`{merchant} {amount}`). Read both the same way.",
        4,
    ),
    (
        "Script",
        "A file run by an interpreter, as in `python tracker.py`: no name, no version, no dependencies, no home for tests.",
        1,
    ),
    (
        "`uv run`",
        "Brings the project's environment in line with `pyproject.toml` and `uv.lock`, then runs the command inside it.",
        1,
    ),
    (
        "Entry point",
        "Where a program starts. In this course, the `[project.scripts]` line that names a command and the object it runs.",
        2,
    ),
    (
        "`[project.scripts]`",
        'The table in `pyproject.toml` that turns a name into a command: `expenses = "expense_tracker.cli:app"` reads command → module → object.',
        2,
    ),
    (
        "Wrapper",
        "The small program uv writes into `.venv/bin/<command>` on install. It imports the object named in `[project.scripts]` and calls it.",
        2,
    ),
    (
        "`__main__.py`",
        "The file `python -m <package>` runs. In the template it imports `app` from the package's `cli` module and calls it.",
        3,
    ),
    (
        "`python -m`",
        "Runs a package's `__main__.py`: the other door into the program. It does not use `[project.scripts]` or the wrapper.",
        3,
    ),
    (
        "typer",
        "The library this course uses to build command-line interfaces from function signatures: the type hints are the specification.",
        4,
    ),
    (
        "Usage line",
        "The first line of `--help`, generated by typer, such as `Usage: expenses add [OPTIONS] {merchant} {amount}`. Arguments follow `[OPTIONS]` in order; `[path]` in brackets is optional.",
        4,
    ),
    (
        "Argument",
        "A value typed by position, for what the command acts on. In typer, a parameter with no default. Missing means an error.",
        5,
    ),
    (
        "Option",
        "A value given by name, such as `--category dining`, for how the command behaves. In typer, a parameter with a default. Missing means the default.",
        5,
    ),
    (
        "`typer.Argument`",
        'Overrides the default rule: `typer.Argument("expenses.csv")` keeps `path` positional while giving it a default.',
        5,
    ),
    (
        "argparse",
        "The command-line parser in Python's standard library: no dependency, more code. Worth recognising in code you inherit.",
        5,
    ),
    (
        "Exit code",
        "The number a program hands back when it ends: 0 means success, anything else failure. `echo $?` shows the last one.",
        6,
    ),
    (
        "`typer.Exit`",
        "Raised to end a typer command with a chosen exit code: `raise typer.Exit(code=1)`. Without a code it exits 0.",
        6,
    ),
    (
        "Distribution name",
        "The project's name with hyphens, such as `parking-lot`: `name` in `pyproject.toml`, and the command you type.",
        7,
    ),
    (
        "Package name",
        "The import name with underscores, such as `parking_lot`: the folder under `src/` and every `import`.",
        7,
    ),
    (
        "Clean clone",
        "A fresh `git clone` into an empty folder: no `.venv`, no caches, nothing uncommitted. How Checkpoint 1 is checked.",
        8,
    ),
    ("Tag", "A permanent name for one commit, such as `v0.1`. Checkpoints are marked at a tag.", 8),
    (
        "`@app.callback()`",
        "A function typer runs before any command. Left empty, it tells typer there will be several commands, so a single command keeps its name.",
        9,
    ),
]

TRAPS = [
    "**The command is named after the package.** The command is whatever the left side of `[project.scripts]` says. The demo's package is `expense_tracker`, its project `expense-tracker`, and its command `expenses`.",
    "**If pytest passes, the rename is complete.** The tests never import `__main__.py`, so an old `from app.cli import app` survives them. mypy, which reads every file under `src`, is what catches it.",
    "**A default just makes an argument optional.** In typer a default turns the parameter into an option (`--amount`). To keep it positional and optional, use `typer.Argument(default)`.",
    "**The type hint decides argument or option.** The default decides. The type hint decides how the text is converted, and `amount: float` without a default is an argument.",
    "**Printing an error is enough.** The shell, `&&`, CI and tests read the exit code, not the text. A program that prints an error and exits 0 is a program that lies.",
    "**`raise typer.Exit()` reports a failure.** Without `code=1` it exits 0, exactly like a normal return.",
    "**It works on my laptop, so CI will be green.** CI starts from the committed files and runs `uv sync --locked`. Your laptop has a refreshed `uv.lock`, a `.venv` and maybe files you never committed.",
    "**One command does not need a callback.** Without `@app.callback()`, typer makes that command the whole program and its name stops being a word you type, so `<app> <command>` and the tests fail.",
    "**`python src/<package>/cli.py` is the same as `uv run <app>`.** The file route uses whatever interpreter you name; for the demo it only defines `app` and never calls it.",
    "**Hyphens and underscores are interchangeable.** `import parking-lot` is a `SyntaxError`. The package and every import use underscores; only the project name and the command use hyphens.",
    "**`git push` publishes the tag.** A plain `git push` sends commits only; the tag needs `git push origin v0.1`, and without it there is nothing at `v0.1` to mark.",
]

CARDS: list[tuple[str, str, str, int]] = [
    (
        "Slide 4 contrasts `python tracker.py` with `uv run expenses report`. What does the second one have?",
        "A name, a version, dependencies and an entry point, all declared in `pyproject.toml`. Same code.",
        "concept",
        1,
    ),
    (
        "Why does `python3 src/expense_tracker/cli.py` fail with `No module named 'typer'` while `uv run expenses` works?",
        "A file run by an interpreter only gets that interpreter's packages. typer lives in the project's `.venv`, which `uv run` uses.",
        "reading",
        1,
    ),
    (
        "Why does `uv run python src/expense_tracker/cli.py report` print nothing at `v0.4`?",
        "Running the file only creates `app` and defines the commands; no line calls `app()`. The wrapper or `__main__.py` makes that call.",
        "concept",
        1,
    ),
    (
        'Read `expenses = "expense_tracker.cli:app"` in three steps.',
        "Command `expenses` → module `expense_tracker.cli` → object `app`.",
        "recall",
        2,
    ),
    (
        "What does uv write into `.venv/bin/expenses` on install?",
        "A wrapper that runs `from expense_tracker.cli import app` and then `sys.exit(app())`.",
        "concept",
        2,
    ),
    (
        "uv answers `error: Failed to spawn` for `parking-lot`, or prints a traceback starting in `.venv/bin/parking-lot`. What does each mean?",
        "Failed to spawn: no command by that name was installed. Traceback from the wrapper: the command exists but its import of the module or object failed.",
        "reading",
        2,
    ),
    (
        "`uv run expenses` versus `python -m expense_tracker`: what does each door need?",
        "The command needs `[project.scripts]` and the wrapper written on install. `-m` needs the package's `__main__.py` and an importable package.",
        "distinction",
        3,
    ),
    (
        "What does the template's `__main__.py` do, and what must change in it when you rename the package?",
        "It imports the typer `app` from `app.cli` and calls it, so `python -m app` works. After the rename its import must name your package's `cli` module.",
        "concept",
        3,
    ),
    (
        "Why is `__main__.py` the rename everyone forgets?",
        "Neither the command (it uses the wrapper) nor the tests (they import `<package>.cli`) load it. Only mypy, or using `python -m`, notices.",
        "concept",
        3,
    ),
    (
        'What does "the type hints are the specification" mean in typer?',
        "typer builds the command line from the signature: the function name is the command, parameters are values, type hints say how to convert them, and `--help` is generated.",
        "concept",
        4,
    ),
    (
        "In typer, what turns a parameter into an option?",
        "A default value. No default makes an argument, whatever the type.",
        "distinction",
        5,
    ),
    (
        'Argument or option: the "For" row of the table.',
        "Argument: what the command acts on. Option: how it behaves.",
        "recall",
        5,
    ),
    (
        'Argument or option: the "Missing" row of the table.',
        "Missing argument: error. Missing option: falls back to the default.",
        "recall",
        5,
    ),
    (
        'What does `typer.Argument("expenses.csv")` do for `report`\'s `path`?',
        "Keeps it positional but optional: `expenses report` reads `expenses.csv`, `expenses report data/expenses.csv` reads the other file. Usage shows `[path]`.",
        "concept",
        5,
    ),
    (
        "`Got unexpected extra argument(s) (12.50)` right after you gave `amount` a default. Why?",
        "The default turned `amount` into `--amount`, so the positional `12.50` has no slot.",
        "reading",
        5,
    ),
    (
        "The slide writes `MERCHANT AMOUNT`, the course's typer writes `{merchant} {amount}`. What do both mean?",
        "Required arguments, in the order you type them, after `[OPTIONS]`. Square brackets, as in `[path]`, mark an optional argument.",
        "reading",
        4,
    ),
    (
        "Why is argparse worth recognising, and why does the course use typer instead?",
        "argparse ships with Python: no dependency, more code, common in inherited code. typer builds the same interface from one signature.",
        "distinction",
        5,
    ),
    (
        "What does an exit code of 0 mean, and how do you see it?",
        "0 means success; anything else means failure. `echo $?` straight after the command.",
        "recall",
        6,
    ),
    (
        "How does a typer command fail properly?",
        "Message to stderr with `typer.echo(..., err=True)`, then `raise typer.Exit(code=1)`.",
        "recall",
        6,
    ),
    (
        '"A program that prints an error and exits 0 is a program that lies." Who is lied to?',
        "Every tool that reads the number: the shell (`&&` carries on), CI (stays green), scripts and tests checking `exit_code`.",
        "concept",
        6,
    ),
    (
        "Exit code 2 from typer versus exit code 1 from your command?",
        "2: typer refused the command line (missing argument, bad type, unknown option) before your function ran. 1: your own check failed.",
        "distinction",
        6,
    ),
    (
        "Distribution name versus package name, for the parking lot?",
        "`parking-lot` (hyphens) for the project and the command; `parking_lot` (underscores) for the folder under `src/` and imports.",
        "distinction",
        7,
    ),
    (
        "The six places the template's `app` must be renamed.",
        "The folder `src/app`; in `pyproject.toml` the `name`, the `[project.scripts]` line and the wheel `packages` line; the import in `__main__.py`; the import in `tests/test_cli.py`.",
        "recall",
        7,
    ),
    (
        "The lab's path from template to `v0.1`, in order.",
        "Rename in six places; `uv lock` then `uv sync`; one real command; fix tests, README, LICENSE; the four checks; commit, push, tag `v0.1` and push the tag.",
        "recall",
        8,
    ),
    (
        "Checkpoint 1's three binary items.",
        "1. `uv sync && uv run <your-app> --help` works from a clean clone. 2. `src/` layout, package importable. 3. README: what it does, how to install, how to run.",
        "recall",
        8,
    ),
    (
        "What does a clean clone catch that your laptop cannot?",
        "Anything you forgot to commit, and anything that only works because of your `.venv` or caches.",
        "concept",
        8,
    ),
    (
        "`The lockfile at uv.lock needs to be updated, but --locked was provided` in CI. Meaning and fix?",
        "The committed `uv.lock` disagrees with `pyproject.toml` (after a rename). Run `uv lock`, commit `uv.lock`, push.",
        "reading",
        9,
    ),
    (
        'mypy: `Cannot find implementation or library stub for module named "app.cli"` in `__main__.py`. Meaning?',
        "The import was not renamed. pytest passes because the tests never load `__main__.py`; fix the import, do not ignore it.",
        "reading",
        9,
    ),
    (
        "One command and no `@app.callback()`: what goes wrong?",
        "typer drops the command's name, so `<app> <command> ...` fails (the command word fills the first argument) and the tests get exit code 2.",
        "concept",
        9,
    ),
]

# ================================================================ MODULE

EXAM_FOCUS = """\
- A terminal transcript after a rename (`Failed to spawn`, `ModuleNotFoundError`, `ImportError` from the wrapper): say which part of `[project.scripts]` or which file broke.
- A typer signature next to a `--help` page or an error box (`Missing argument`, `Got unexpected extra argument(s)`, `Invalid value`): say which parameters are arguments or options, predict the usage line, or explain the error.
- A command that prints an error but exits 0, with `echo $?` or an `&&` chain: what the shell, CI and tests conclude, and the fix in words.
- The four checks' output where pytest passes and mypy fails on `__main__.py`, or CI's `uv sync --locked` refusing the lockfile: which of the three that bite, why the other tools missed it, and whether `# type: ignore` is acceptable.
- One command without `@app.callback()`: read the usage line without `COMMAND` and the failing `exit_code` assertions.
- Compare: `python file.py` against `uv run <command>`, `uv run <command>` against `python -m <package>`, argparse against typer, or a diff that makes a lying command exit 1, with two commit messages to judge.
- Checkpoint 1 as a Definition of Done: which situation fails which binary item, what a clean clone catches, and why the tag needs its own push."""


module: dict[str, Any] = {
    "id": MID,
    "order": 4,
    "module": "M2",
    "title": "From script to program: entry points, typer and exit codes",
    "sessions": [5],
    "predicted": False,
    "sources": [
        "slides-session-5",
        "labs/01-scaffold.md",
        "slides-session-4 (anatomy)",
        "project-template",
        "expense-tracker v0.0..v0.4 (c746d38, a953d05, 2ecad20)",
        "slides-session-7 (failing well), slides-session-8 (CliRunner)",
    ],
    "summary_md": (
        "Session 5 turns a script into a program: the same code, but installed as a command with a name, a version, "
        "dependencies and an entry point. You learn how `uv run expenses` is resolved through `[project.scripts]`, why "
        "`__main__.py` is a second door, and how typer reads a function signature so that the type hints are the "
        "specification of arguments, options and `--help`. You learn why exit codes matter: every tool downstream reads "
        "the number, and a program that prints an error and exits 0 is a program that lies. The lab applies it all: "
        "rename the template in six places, write one real command, pass the four checks and tag `v0.1` for Checkpoint 1."
    ),
    "exam_focus_md": EXAM_FOCUS,
    "sections": SECTIONS,
    "terms": [{"term": t, "definition_md": d, "section_ref": s(n)} for t, d, n in TERMS],
    "traps": TRAPS,
    "flashcards": [
        {"id": f"{MID}-f{i:02d}", "front_md": f, "back_md": b, "kind": k, "section_ref": s(n)}
        for i, (f, b, k, n) in enumerate(CARDS, start=1)
    ],
    "questions": QUESTIONS,
}


def main() -> None:
    ids = [q["id"] for q in QUESTIONS]
    assert len(ids) == len(set(ids)), "duplicate question ids"
    assert ids == sorted(ids), "questions out of order"
    pos = Counter(
        "abcd"[[o["correct"] for o in q["options"]].index(True)]
        for q in QUESTIONS
        if q["type"] == "mcq"
    )
    print("correct positions:", dict(sorted(pos.items())))
    print("types:", dict(Counter(q["type"] for q in QUESTIONS)))
    print("levels:", dict(Counter(q["level"] for q in QUESTIONS)))
    with OUT.open("w", encoding="utf-8") as f:
        json.dump(module, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
